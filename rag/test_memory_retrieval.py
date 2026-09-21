#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import gptina_memory as gm  # noqa: E402

GOLD = ROOT / "rag" / "eval" / "GPTINA_MEMORY_GOLD.json"


def main() -> None:
    gm.verify_boundary()

    first = gm.sync_sqlite_index(False, allow_dirty_preview=True)
    second = gm.sync_sqlite_index(False, allow_dirty_preview=True)
    if gm.git_worktree_dirty():
        if gm.sqlite_index_is_fresh(False):
            raise AssertionError("dirty preview unexpectedly accepted as canonical")
        if not gm.sqlite_index_is_fresh(False, allow_dirty_preview=True):
            raise AssertionError("unchanged dirty preview was not reusable")
    elif not gm.sqlite_index_is_fresh(False):
        raise AssertionError("clean committed index was not accepted as canonical")
    if second["changed_sources"] != 0 or second["removed_sources"] != 0:
        raise AssertionError(f"Incremental SQLite no-op sync was not a no-op: {second}")

    stats = gm.sqlite_stats(allow_dirty_preview=True)
    if int(stats["sources"]) <= 0 or int(stats["chunks"]) <= 0:
        raise AssertionError(f"SQLite index is empty: {stats}")

    tests = json.loads(GOLD.read_text(encoding="utf-8"))
    failures: list[str] = []
    timings_ms: list[float] = []

    for case in tests:
        mode = case.get("mode", "search")
        expected = set(case.get("expected_any", []))
        forbidden = set(case.get("forbidden", []))

        started = time.perf_counter()
        if mode == "exact":
            hits = gm.exact_matches(
                case["query"], include_superseded=False, limit=20
            )
            sources = [h["source"] for h in hits]
        else:
            ranked = gm.sqlite_search(
                case["query"],
                int(case.get("top_k", 6)),
                include_historical=False,
                include_superseded=False,
                allow_dirty_preview=True,
            )
            sources = [d["source"] for _score, d in ranked]
            if ranked and "score_components" not in ranked[0][1]:
                failures.append(f"{case['id']}: missing score decomposition")
        timings_ms.append((time.perf_counter() - started) * 1000.0)

        if expected and not any(src in expected for src in sources):
            failures.append(
                f"{case['id']}: expected one of {sorted(expected)}, got {sources}"
            )
        present_forbidden = [src for src in sources if src in forbidden]
        if present_forbidden:
            failures.append(
                f"{case['id']}: forbidden source(s) retrieved: {present_forbidden}"
            )

        print(f"{case['id']}: {sources[:8]}")

    if failures:
        print("\nREGRESSION FAILURES:")
        for item in failures:
            print(f"- {item}")
        raise SystemExit(1)

    avg_ms = sum(timings_ms) / max(1, len(timings_ms))
    print(f"\nSQLite initial sync: {first}")
    print(f"SQLite no-op sync: {second}")
    print(f"SQLite stats: {stats}")
    print(f"Average gold-query latency in this run: {avg_ms:.2f} ms")
    print(f"OK: {len(tests)} GPTina memory regression cases passed.")


if __name__ == "__main__":
    main()
