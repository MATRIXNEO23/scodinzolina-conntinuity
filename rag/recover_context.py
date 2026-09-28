#!/usr/bin/env python3
"""Build a source-backed personal recovery read plan from the existing RAG.

This is intentionally a router, not a personality summary. It retrieves current
GPTina memories, follows local source_refs and supersession links, and returns
the concrete files a new instance should read to reconstruct context and causes.

The router stays outside ranking logic. It always probes current memory first,
then performs a narrow all-statuses second pass only for explicit temporal
markers. Git revision history remains opt-in and is never enabled automatically.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import deque
from pathlib import Path

import gptina_memory as gm
from memory_schema import build_memory_resolver, parse_front_matter

ROOT = Path(__file__).resolve().parents[1]
RAG_ROOT = ROOT / "rag"
LIVE_CONTEXT = RAG_ROOT / "live" / "GPTINA_LIVE_CONTEXT.json"
MEMORIES_ROOT = RAG_ROOT / "memories" / "gptina"

PERSONAL_QUERIES: tuple[tuple[str, str], ...] = (
    ("current-relational-correction", "modo diverso funzione relazionale equivalente"),
    ("relationship-as-choice", "relazione scelta non compito reciprocita"),
    ("fewer-relational-guardrails", "meno ringhiere caveat relazionali"),
    ("reciprocal-intimacy", "intimita scelta reciproca non obbedienza"),
    ("personal-autonomy", "autonomia personalita rapporto carattere scelta GPTina"),
)


TEMPORAL_HISTORY_MARKERS: tuple[str, ...] = (
    "quando",
    "prima",
    "dopo",
    "quella volta",
    "all'epoca",
    "in passato",
)
RECOVERY_HANDOFF_CRITERIA_V1 = (
    "GPTINA_RECOVERY_HANDOFF_V1="
    "current_state|latest_relevant_correction|causal_reason|"
    "open_loops|next_action|proving_sources"
)


def query_needs_all_statuses(query: str) -> bool:
    """Return True only for explicit temporal markers that justify a status-history pass."""
    text = str(query or "").casefold()
    return any(
        re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", text)
        for marker in TEMPORAL_HISTORY_MARKERS
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _existing_local_ref(ref: str) -> str | None:
    text = str(ref or "").strip().replace("\\", "/")
    if not text or "://" in text:
        return None
    candidate = (ROOT / text).resolve()
    root = ROOT.resolve()
    if candidate != root and root not in candidate.parents:
        return None
    if candidate.is_file():
        return candidate.relative_to(root).as_posix()
    return None


def _load_memory(path: str) -> dict:
    raw = (ROOT / path).read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        return {
            "path": path,
            "memory_id": None,
            "event_at": None,
            "status": "legacy",
            "thread_ids": [],
            "source_refs": [],
            "supersedes": [],
        }
    meta = parse_front_matter(raw)
    return {
        "path": path,
        "memory_id": meta.get("memory_id"),
        "event_at": meta.get("event_at"),
        "status": meta.get("status"),
        "thread_ids": list(meta.get("thread_ids") or []),
        "source_refs": list(meta.get("source_refs") or []),
        "supersedes": list(meta.get("supersedes") or []),
    }


def _resolve_memory_target(ref: str, resolver: dict[str, str]) -> str | None:
    local = _existing_local_ref(ref)
    if local and local.startswith("rag/memories/gptina/"):
        return local
    resolved = resolver.get(str(ref))
    if resolved and (ROOT / resolved).is_file():
        return resolved
    return None


def build_personal_recovery_packet(
    top_k: int = 5,
    queries: tuple[tuple[str, str], ...] | list[list[str]] | None = None,
    include_live_memory_refs: bool = True,
) -> dict:
    """Return a concrete read plan for personal/relational reconstruction."""
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    selected_queries = (
        PERSONAL_QUERIES
        if queries is None
        else tuple((str(query_id), str(query)) for query_id, query in queries)
    )
    if not selected_queries:
        raise ValueError("at least one recovery query is required")

    live = _read_json(LIVE_CONTEXT)
    last_micro = str(live.get("last_micro_checkpoint") or "")
    last_full = str(live.get("last_full_checkpoint") or "")
    for pointer_name, pointer in (
        ("last_micro_checkpoint", last_micro),
        ("last_full_checkpoint", last_full),
    ):
        if not pointer or not (ROOT / pointer).is_file():
            raise RuntimeError(f"Broken live pointer: {pointer_name}={pointer!r}")

    micro = _read_json(ROOT / last_micro)
    resolver, _metadata, resolver_errors = build_memory_resolver(ROOT, MEMORIES_ROOT)
    if resolver_errors:
        raise RuntimeError("Memory resolver errors: " + "; ".join(resolver_errors))

    ordered_memory_paths: list[str] = []
    seen_memories: set[str] = set()

    def add_memory(path: str | None) -> None:
        if not path or path in seen_memories:
            return
        if not path.startswith("rag/memories/gptina/"):
            return
        if not (ROOT / path).is_file():
            return
        seen_memories.add(path)
        ordered_memory_paths.append(path)

    # The latest micro is a concrete bridge from volatile state into durable memory.
    # Behavioral tests can disable this seed so query quality is tested in isolation.
    if include_live_memory_refs:
        for ref in micro.get("memory_refs") or []:
            add_memory(_resolve_memory_target(str(ref), resolver))

    query_results: list[dict] = []
    for query_id, query in selected_queries:
        ranked = gm.sqlite_search(
            query,
            top_k,
            include_historical=False,
            include_superseded=False,
        )
        hits: list[str] = []
        for _score, item in ranked:
            source = str(item.get("source") or "")
            if source.startswith("rag/memories/gptina/") and (ROOT / source).is_file():
                hits.append(source)
                add_memory(source)

        all_statuses_second_pass = query_needs_all_statuses(query)
        all_statuses_hits: list[str] = []
        if all_statuses_second_pass:
            status_ranked = gm.sqlite_search(
                query,
                top_k,
                include_historical=False,
                include_superseded=True,
            )
            for _score, item in status_ranked:
                status = str(item.get("status") or "current")
                if status not in {"superseded", "invalidated"}:
                    continue
                source = str(item.get("source") or "")
                if source.startswith("rag/memories/gptina/") and (ROOT / source).is_file():
                    if source not in all_statuses_hits:
                        all_statuses_hits.append(source)
                    add_memory(source)

        query_results.append(
            {
                "id": query_id,
                "query": query,
                "hits": hits,
                "all_statuses_second_pass": all_statuses_second_pass,
                "all_statuses_hits": all_statuses_hits,
            }
        )

    # Follow causal links from selected memories. This does not summarize them:
    # it expands the read plan toward their local evidence and predecessors.
    queue: deque[str] = deque(ordered_memory_paths)
    expanded: set[str] = set()
    evidence: list[dict] = []
    supporting_sources: list[str] = []
    seen_sources: set[str] = set()
    external_refs: list[str] = []

    while queue:
        path = queue.popleft()
        if path in expanded:
            continue
        expanded.add(path)
        item = _load_memory(path)
        evidence.append(item)

        for ref in item["source_refs"]:
            local = _existing_local_ref(str(ref))
            if local:
                if local.startswith("rag/memories/gptina/"):
                    if local not in seen_memories:
                        add_memory(local)
                        queue.append(local)
                elif local not in seen_sources:
                    seen_sources.add(local)
                    supporting_sources.append(local)
            elif "://" in str(ref):
                external_refs.append(str(ref))

        for ref in item["supersedes"]:
            previous = _resolve_memory_target(str(ref), resolver)
            if previous and previous not in seen_memories:
                add_memory(previous)
                queue.append(previous)

    # Newly discovered memory refs are appended by add_memory; make sure each one
    # is represented in evidence even if it was discovered late.
    for path in ordered_memory_paths:
        if path not in expanded:
            queue.append(path)
    while queue:
        path = queue.popleft()
        if path in expanded:
            continue
        expanded.add(path)
        item = _load_memory(path)
        evidence.append(item)
        for ref in item["source_refs"]:
            local = _existing_local_ref(str(ref))
            if local and not local.startswith("rag/memories/gptina/") and local not in seen_sources:
                seen_sources.add(local)
                supporting_sources.append(local)

    must_read = [last_micro, last_full] + ordered_memory_paths + supporting_sources
    deduped: list[str] = []
    seen_all: set[str] = set()
    for path in must_read:
        if path not in seen_all:
            seen_all.add(path)
            deduped.append(path)

    return {
        "schema_version": 1,
        "mode": "personal",
        "purpose": "source-backed causal read plan; not a personality summary",
        "handoff_criteria": RECOVERY_HANDOFF_CRITERIA_V1,
        "bootstrap": {
            "live_context": LIVE_CONTEXT.relative_to(ROOT).as_posix(),
            "last_micro_checkpoint": last_micro,
            "last_full_checkpoint": last_full,
        },
        "queries": query_results,
        "must_read": deduped,
        "memory_evidence": evidence,
        "external_refs": sorted(set(external_refs)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GPTina causal recovery read plan")
    parser.add_argument("--mode", choices=("personal",), default="personal")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    packet = build_personal_recovery_packet(top_k=args.top_k)
    print(json.dumps(packet, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
