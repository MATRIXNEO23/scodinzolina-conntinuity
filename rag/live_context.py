#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

from memory_schema import (
    build_memory_resolver,
    is_nonempty_string,
    validate_local_ref,
    validate_string_list,
    validate_temporal,
)

ROOT = Path(
    os.environ.get("GPTINA_REPO_ROOT", str(Path(__file__).resolve().parents[1]))
).resolve()
RAG = ROOT / "rag"
LIVE = RAG / "live"
MICRO = LIVE / "micro-checkpoints"
LIVE_CONTEXT = LIVE / "GPTINA_LIVE_CONTEXT.json"

ALLOWED_CHANGE_TYPES = {
    "correction", "decision", "rule", "project_state", "relational_shift",
    "open_loop", "preflight", "milestone", "visual_context",
}
CURRENT_MICRO_SCHEMA_VERSION = 2
LEGACY_MICRO_SCHEMA_VERSIONS = {1}

ALLOWED_EXTERNAL_PREFIXES_V2 = ("conversation://", "github://", "external://")
ALLOWED_EXTERNAL_PREFIXES_V1 = (
    *ALLOWED_EXTERNAL_PREFIXES_V2,
    "artifact://",
    "attachment://",
    "commit://",
)

MICRO_REQUIRED_V2 = {
    "schema_version", "micro_id", "owner", "kind", "event_at", "recorded_at",
    "change_type", "summary", "changed", "thread_ids", "source_refs",
    "memory_refs", "media_refs", "importance", "next_action", "preflight",
}

MICRO_REQUIRED_V1 = {
    "schema_version", "owner", "kind", "event_at", "recorded_at",
    "change_type", "summary", "next_action",
}

LEGACY_V1_DEFAULTS = {
    "micro_id": "",
    "changed": [],
    "thread_ids": [],
    "source_refs": [],
    "memory_refs": [],
    "media_refs": [],
    "importance": 3,
    "preflight": False,
}


def fail(message: str) -> None:
    raise SystemExit(message)


def git_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


@contextlib.contextmanager
def writer_lock():
    """Cooperative single-writer lock; readers remain lock-free."""
    try:
        common = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        common_path = Path(common)
        lock_dir = common_path if common_path.is_absolute() else (ROOT / common_path).resolve()
    except (OSError, subprocess.CalledProcessError):
        lock_dir = LIVE
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / "gptina-memory-writer.lock"
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except ImportError:  # pragma: no cover - Windows fallback
            import msvcrt
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                fail(f"Another GPTina memory writer is active: {exc}")
        except BlockingIOError:
            fail("Another GPTina memory writer is active")
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()} head={git_head() or 'none'}\n")
        handle.flush()
        yield
    finally:
        try:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except (ImportError, OSError):
            pass
        handle.close()


def require_expected_head(expected: str | None) -> None:
    if not expected:
        return
    actual = git_head()
    if actual != expected:
        fail(f"HEAD compare-and-swap failed: expected={expected} actual={actual}")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_slug(text: str) -> str:
    text = text.casefold().strip()
    text = re.sub(r"[^0-9a-zà-öø-ÿ_-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:64] or "delta").strip("-")


def load_live() -> dict:
    if not LIVE_CONTEXT.is_file():
        return {
            "schema_version": 1,
            "owner": "gptina",
            "kind": "gptina_live_context",
            "updated_at": now_iso(),
            "latest_summary": "",
            "next_action": "",
            "last_micro_checkpoint": None,
            "last_full_checkpoint": None,
            "active_threads": [],
            "open_loops": [],
            "recent_micro_checkpoints": [],
            "micro_since_full_checkpoint": 0,
            "review_policy": {
                "substantive_turn_interval": 4,
                "immediate_triggers": sorted(ALLOWED_CHANGE_TYPES - {"preflight"}),
                "preflight_before_long_or_risky_work": True,
            },
            "note": (
                "Projection only. Append-only truth lives in "
                "micro-checkpoints/checkpoints/memories/sources."
            ),
        }
    try:
        return json.loads(LIVE_CONTEXT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid live context JSON: {exc}")


def micro_schema_version(record: dict) -> int | None:
    version = record.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        return None
    return version


def normalize_micro_for_validation(record: dict) -> dict:
    """Return a validation-only copy; never rewrite historical records."""
    normalized = dict(record)
    if micro_schema_version(normalized) == 1:
        for key, default in LEGACY_V1_DEFAULTS.items():
            if key not in normalized:
                normalized[key] = list(default) if isinstance(default, list) else default
    return normalized


def ref_exists(ref: str, *, schema_version: int) -> bool:
    if schema_version == 1:
        return bool(ref.strip())
    if schema_version == CURRENT_MICRO_SCHEMA_VERSION and ref.startswith(
        ALLOWED_EXTERNAL_PREFIXES_V2
    ):
        return True
    return not validate_local_ref(ROOT, ref, "reference")

def validate_micro(record: dict, path: Path | None = None) -> list[str]:
    errors: list[str] = []

    version = micro_schema_version(record)
    if version is None:
        return ["schema_version must be an integer"]
    if version not in LEGACY_MICRO_SCHEMA_VERSIONS | {CURRENT_MICRO_SCHEMA_VERSION}:
        return [f"unsupported schema_version={version}"]

    required = MICRO_REQUIRED_V1 if version == 1 else MICRO_REQUIRED_V2
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"missing keys: {missing}")

    normalized = normalize_micro_for_validation(record)

    if normalized.get("owner") != "gptina":
        errors.append("owner must be gptina")
    if normalized.get("kind") != "gptina_micro_checkpoint":
        errors.append("kind must be gptina_micro_checkpoint")
    if normalized.get("change_type") not in ALLOWED_CHANGE_TYPES:
        errors.append(f"invalid change_type={normalized.get('change_type')}")
    importance = normalized.get("importance")
    if (
        not isinstance(importance, int)
        or isinstance(importance, bool)
        or not 1 <= importance <= 5
    ):
        errors.append("importance must be integer 1..5")
    if not is_nonempty_string(normalized.get("summary")):
        errors.append("summary must be a non-empty string")
    errors.extend(validate_temporal(normalized.get("event_at"), "event_at", timezone_required=False))
    errors.extend(validate_temporal(normalized.get("recorded_at"), "recorded_at", timezone_required=True))
    if version == 2 and not is_nonempty_string(normalized.get("micro_id")):
        errors.append("micro_id must be a non-empty string")
    errors.extend(validate_string_list(normalized.get("changed"), "changed"))
    if not isinstance(normalized.get("next_action"), str):
        errors.append("next_action must be a string")
    for key in ("thread_ids", "source_refs", "memory_refs", "media_refs"):
        errors.extend(validate_string_list(normalized.get(key), key))
    if not isinstance(normalized.get("preflight"), bool):
        errors.append("preflight must be a boolean")

    resolver: dict[str, str] = {}
    if version == 2:
        resolver, _metadata, resolver_errors = build_memory_resolver(
            ROOT, RAG / "memories" / "gptina"
        )
        errors.extend(f"memory resolver: {item}" for item in resolver_errors)
    for key in ("source_refs", "memory_refs", "media_refs"):
        refs = normalized.get(key)
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if key == "memory_refs" and version == 2 and isinstance(ref, str) and ref in resolver:
                continue
            if not isinstance(ref, str) or not ref_exists(ref, schema_version=version):
                errors.append(f"{key} missing ref: {ref}")
    if path and not path.as_posix().endswith(".json"):
        errors.append("micro-checkpoint path must end in .json")
    return errors

def save_delta(args: argparse.Namespace) -> Path:
    with writer_lock():
        require_expected_head(args.expected_head)
        return _save_delta_locked(args)


def _save_delta_locked(args: argparse.Namespace) -> Path:
    if args.change_type not in ALLOWED_CHANGE_TYPES:
        fail(f"Unsupported change type: {args.change_type}")

    recorded_at = now_iso()
    event_at = args.event_at or recorded_at
    dt = datetime.fromisoformat(recorded_at)
    stamp = dt.strftime("%Y-%m-%dT%H%M%S%z")
    slug = safe_slug(args.summary)
    token = uuid.uuid4().hex[:8]
    target = (
        MICRO / f"{dt:%Y}" / f"{dt:%m}" / f"{dt:%d}"
        / f"{stamp}--{slug}--{token}.json"
    )

    sources = args.source or ["conversation://current"]
    record = {
        "schema_version": CURRENT_MICRO_SCHEMA_VERSION,
        "micro_id": f"gptina-micro-{stamp}-{token}",
        "owner": "gptina",
        "kind": "gptina_micro_checkpoint",
        "event_at": event_at,
        "recorded_at": recorded_at,
        "change_type": args.change_type,
        "summary": args.summary.strip(),
        "changed": args.changed or [],
        "thread_ids": args.thread or [],
        "source_refs": sources,
        "memory_refs": args.memory or [],
        "media_refs": args.media or [],
        "importance": args.importance,
        "next_action": (args.next_action or "").strip(),
        "preflight": bool(args.preflight or args.change_type == "preflight"),
    }

    errors = validate_micro(record, target)
    if errors:
        fail("Invalid micro-checkpoint:\n- " + "\n- ".join(errors))

    live = load_live()
    recent = list(live.get("recent_micro_checkpoints") or [])
    recent.append(rel(target))
    recent = recent[-12:]

    threads = list(live.get("active_threads") or [])
    for thread in record["thread_ids"]:
        if thread not in threads:
            threads.append(thread)

    loops = list(live.get("open_loops") or [])
    for resolved in args.resolve or []:
        loops = [item for item in loops if item != resolved]
    if record["next_action"] and record["next_action"] not in loops:
        loops.append(record["next_action"])

    live.update(
        {
            "schema_version": 1,
            "owner": "gptina",
            "kind": "gptina_live_context",
            "updated_at": recorded_at,
            "latest_summary": record["summary"],
            "next_action": record["next_action"],
            "last_micro_checkpoint": rel(target),
            "active_threads": threads,
            "open_loops": loops,
            "recent_micro_checkpoints": recent,
            "micro_since_full_checkpoint": int(
                live.get("micro_since_full_checkpoint") or 0
            ) + 1,
        }
    )
    live.setdefault(
        "review_policy",
        {
            "substantive_turn_interval": 4,
            "immediate_triggers": sorted(ALLOWED_CHANGE_TYPES - {"preflight"}),
            "preflight_before_long_or_risky_work": True,
        },
    )
    live.setdefault(
        "note",
        "Projection only. Append-only truth lives in "
        "micro-checkpoints/checkpoints/memories/sources.",
    )
    # Prepare both payloads, re-check HEAD, then publish under one cooperative
    # writer lock. A crash can leave an orphan append-only micro-checkpoint,
    # but never a live pointer to a missing micro-checkpoint.
    micro_payload = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    live_payload = json.dumps(live, ensure_ascii=False, indent=2) + "\n"
    require_expected_head(args.expected_head)
    atomic_write(target, micro_payload)
    atomic_write(LIVE_CONTEXT, live_payload)
    return target


def mark_checkpoint(path_text: str, expected_head: str | None = None) -> None:
    with writer_lock():
        require_expected_head(expected_head)
        _mark_checkpoint_locked(path_text)


def _mark_checkpoint_locked(path_text: str) -> None:
    path = (ROOT / path_text).resolve()
    checkpoints = (ROOT / "checkpoints").resolve()
    if checkpoints not in path.parents or not path.is_file():
        fail(f"Checkpoint must exist under checkpoints/: {path_text}")
    live = load_live()
    live["updated_at"] = now_iso()
    live["last_full_checkpoint"] = rel(path)
    live["micro_since_full_checkpoint"] = 0
    atomic_write(LIVE_CONTEXT, json.dumps(live, ensure_ascii=False, indent=2) + "\n")


def verify_live_context() -> None:
    if not LIVE_CONTEXT.is_file():
        fail("Missing rag/live/GPTINA_LIVE_CONTEXT.json")
    live = load_live()

    for key in (
        "schema_version", "owner", "kind", "updated_at", "latest_summary",
        "next_action", "last_micro_checkpoint", "last_full_checkpoint",
        "active_threads", "open_loops", "recent_micro_checkpoints",
        "micro_since_full_checkpoint", "review_policy",
    ):
        if key not in live:
            fail(f"Live context missing key: {key}")

    if live.get("owner") != "gptina":
        fail("Live context owner must be gptina")
    if live.get("kind") != "gptina_live_context":
        fail("Live context kind must be gptina_live_context")

    recent = list(live.get("recent_micro_checkpoints") or [])
    if len(recent) > 12:
        fail("Live context recent_micro_checkpoints must contain at most 12 items")
    if len(recent) != len(set(recent)):
        fail("Live context recent_micro_checkpoints contains duplicates")

    recent_records: list[tuple[str, datetime]] = []
    for path_text in recent:
        path = ROOT / path_text
        if not path.is_file():
            fail(f"Recent micro-checkpoint missing: {path_text}")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            recorded_at = datetime.fromisoformat(str(record["recorded_at"]))
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            fail(f"Cannot order recent micro-checkpoint {path_text}: {exc}")
        recent_records.append((path_text, recorded_at))
    if any(
        recent_records[index][1] > recent_records[index + 1][1]
        for index in range(len(recent_records) - 1)
    ):
        fail("recent_micro_checkpoints must be ordered by recorded_at")

    last_micro = live.get("last_micro_checkpoint")
    if last_micro:
        if not recent_records or recent_records[-1][0] != last_micro:
            fail("last_micro_checkpoint must be the newest recent_micro_checkpoints item")
        if not (ROOT / last_micro).is_file():
            fail(f"last_micro_checkpoint missing: {last_micro}")

    last_full = live.get("last_full_checkpoint")
    if last_full and not (ROOT / last_full).is_file():
        fail(f"last_full_checkpoint missing: {last_full}")

    count = 0
    v1_count = 0
    v2_count = 0
    micro_ids: dict[str, str] = {}
    for path in sorted(MICRO.rglob("*.json")) if MICRO.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"Invalid micro-checkpoint JSON {rel(path)}: {exc}")
        errors = validate_micro(record, path)
        if errors:
            fail(f"Invalid {rel(path)}:\n- " + "\n- ".join(errors))
        version = micro_schema_version(record)
        if version == 1:
            v1_count += 1
        elif version == 2:
            v2_count += 1
            micro_id = str(record["micro_id"])
            previous = micro_ids.get(micro_id)
            if previous:
                fail(f"Duplicate micro_id {micro_id}: {previous}, {rel(path)}")
            micro_ids[micro_id] = rel(path)
        count += 1

    policy = live.get("review_policy") or {}
    interval = policy.get("substantive_turn_interval")
    if not isinstance(interval, int) or not 3 <= interval <= 5:
        fail("review_policy.substantive_turn_interval must be between 3 and 5")

    print(
        "OK: live context verified "
        f"(micro-checkpoints={count}, v1_legacy={v1_count}, v2_current={v2_count}, "
        f"recent={len(recent)}, since_full={live.get('micro_since_full_checkpoint')})."
    )


def print_status() -> None:
    print(json.dumps(load_live(), ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="GPTina frequent live-context saver")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("save-delta", help="Append a micro-checkpoint and refresh live context")
    sp.add_argument("--summary", required=True)
    sp.add_argument("--change-type", choices=sorted(ALLOWED_CHANGE_TYPES), required=True)
    sp.add_argument("--event-at")
    sp.add_argument("--changed", action="append", default=[])
    sp.add_argument("--thread", action="append", default=[])
    sp.add_argument("--source", action="append", default=[])
    sp.add_argument("--memory", action="append", default=[])
    sp.add_argument("--media", action="append", default=[])
    sp.add_argument("--importance", type=int, choices=range(1, 6), default=3)
    sp.add_argument("--next", dest="next_action", default="")
    sp.add_argument("--resolve", action="append", default=[])
    sp.add_argument("--preflight", action="store_true")
    sp.add_argument(
        "--expected-head",
        help="Fail without writing if repository HEAD differs from this SHA",
    )

    mp = sub.add_parser("mark-checkpoint", help="Point live context to a full checkpoint")
    mp.add_argument("path")
    mp.add_argument("--expected-head")

    sub.add_parser("status", help="Show current live context")
    sub.add_parser("verify", help="Verify live buffer and all micro-checkpoints")

    args = ap.parse_args()
    if args.cmd == "save-delta":
        target = save_delta(args)
        print(f"Created {rel(target)}")
    elif args.cmd == "mark-checkpoint":
        mark_checkpoint(args.path, expected_head=args.expected_head)
        print(f"Marked full checkpoint: {args.path}")
    elif args.cmd == "status":
        print_status()
    elif args.cmd == "verify":
        verify_live_context()


if __name__ == "__main__":
    main()
