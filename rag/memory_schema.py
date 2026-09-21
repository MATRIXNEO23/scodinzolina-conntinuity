#!/usr/bin/env python3
"""Strict, source-first schema helpers for GPTina memory records."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

EXTERNAL_REF_PREFIXES = ("conversation://", "github://", "external://")
MEMORY_STATUSES = {"current", "superseded", "invalidated", "historical"}
CONFIDENCE_VALUES = {"verified", "contextual", "inferred"}
DURABLE_V2_REQUIRED = {
    "schema_version", "memory_id", "owner", "kind", "event_at",
    "recorded_at", "status", "supersedes", "thread_ids", "entity_refs",
    "source_refs", "media_refs", "importance", "confidence", "tags",
    "append_only",
}
DURABLE_V2_ALLOWED = DURABLE_V2_REQUIRED | {"event_id"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def parse_front_matter(raw: str) -> dict:
    if not raw.startswith("---\n"):
        raise ValueError("missing opening YAML front matter delimiter")
    end = raw.find("\n---", 4)
    if end < 0:
        raise ValueError("missing closing YAML front matter delimiter")
    try:
        value = yaml.load(raw[4:end], Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML front matter: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("front matter must be a mapping")
    return value


def is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_string_list(value: object, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list):
        return [f"{field} must be a list"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not is_nonempty_string(item):
            errors.append(f"{field}[{index}] must be a non-empty string")
            continue
        if item in seen:
            errors.append(f"{field}[{index}] duplicates {item!r}")
        seen.add(item)
    if nonempty and not value:
        errors.append(f"{field} must not be empty")
    return errors


def validate_temporal(value: object, field: str, *, timezone_required: bool) -> list[str]:
    if not is_nonempty_string(value):
        return [f"{field} must be a non-empty ISO-8601 string"]
    text = str(value).strip()
    try:
        if len(text) == 10:
            date.fromisoformat(text)
            if timezone_required:
                return [f"{field} must include time and timezone"]
            return []
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return [f"{field} is not valid ISO-8601: {text}"]
    if timezone_required and parsed.tzinfo is None:
        return [f"{field} must include a timezone"]
    return []


def normalize_local_ref(root: Path, ref: str) -> tuple[Path | None, str | None]:
    text = ref.strip().replace("\\", "/")
    if not text:
        return None, "reference is empty"
    if text.startswith(EXTERNAL_REF_PREFIXES):
        return None, None
    candidate = Path(text)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None, f"unsafe local reference: {ref}"
    root_resolved = root.resolve()
    resolved = (root_resolved / candidate).resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        return None, f"reference escapes repository: {ref}"
    return resolved, None


def validate_local_ref(root: Path, ref: object, field: str) -> list[str]:
    if not is_nonempty_string(ref):
        return [f"{field} must contain non-empty strings"]
    resolved, error = normalize_local_ref(root, str(ref))
    if error:
        return [f"{field}: {error}"]
    if resolved is not None and not resolved.exists():
        return [f"{field} missing ref: {ref}"]
    return []


def validate_durable_v2(meta: dict, root: Path) -> list[str]:
    errors: list[str] = []
    missing = sorted(DURABLE_V2_REQUIRED - set(meta))
    if missing:
        errors.append(f"missing keys: {missing}")
    unknown = sorted(set(meta) - DURABLE_V2_ALLOWED)
    if unknown:
        errors.append(f"unknown keys: {unknown}")
    if meta.get("schema_version") != 2 or isinstance(meta.get("schema_version"), bool):
        errors.append("schema_version must be integer 2")
    if not is_nonempty_string(meta.get("memory_id")):
        errors.append("memory_id must be a non-empty string")
    if meta.get("owner") != "gptina":
        errors.append("owner must be gptina")
    if meta.get("kind") != "gptina_live_memory":
        errors.append("kind must be gptina_live_memory")
    event_at = meta.get("event_at")
    event_requires_timezone = is_nonempty_string(event_at) and len(str(event_at).strip()) != 10
    errors.extend(validate_temporal(
        event_at, "event_at", timezone_required=bool(event_requires_timezone)
    ))
    errors.extend(validate_temporal(meta.get("recorded_at"), "recorded_at", timezone_required=True))
    if meta.get("status") not in MEMORY_STATUSES:
        errors.append(f"invalid status={meta.get('status')}")
    importance = meta.get("importance")
    if isinstance(importance, bool) or not isinstance(importance, int) or not 1 <= importance <= 5:
        errors.append("importance must be integer 1..5")
    if meta.get("confidence") not in CONFIDENCE_VALUES:
        errors.append(f"invalid confidence={meta.get('confidence')}")
    if meta.get("append_only") is not True:
        errors.append("append_only must be boolean true")
    for field in ("supersedes", "thread_ids", "entity_refs", "source_refs", "media_refs", "tags"):
        errors.extend(validate_string_list(meta.get(field), field))
    for field in ("source_refs", "media_refs"):
        refs = meta.get(field)
        if isinstance(refs, list):
            for ref in refs:
                errors.extend(validate_local_ref(root, ref, field))
    event_id = meta.get("event_id")
    if event_id is not None and not is_nonempty_string(event_id):
        errors.append("event_id must be a non-empty string when present")
    return errors


def build_memory_resolver(root: Path, memories_root: Path) -> tuple[dict[str, str], dict[str, dict], list[str]]:
    resolver: dict[str, str] = {}
    metadata: dict[str, dict] = {}
    errors: list[str] = []
    if not memories_root.is_dir():
        return resolver, metadata, errors
    for path in sorted(memories_root.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n"):
            continue
        try:
            meta = parse_front_matter(raw)
        except ValueError as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
            continue
        memory_id = meta.get("memory_id")
        if not is_nonempty_string(memory_id):
            continue
        relpath = path.relative_to(root).as_posix()
        if memory_id in resolver:
            errors.append(f"duplicate memory_id {memory_id!r}: {resolver[memory_id]}, {relpath}")
            continue
        if meta.get("owner") != "gptina":
            errors.append(f"{relpath}: memory_id {memory_id!r} has wrong owner={meta.get('owner')}")
            continue
        resolver[str(memory_id)] = relpath
        metadata[str(memory_id)] = meta
    return resolver, metadata, errors
