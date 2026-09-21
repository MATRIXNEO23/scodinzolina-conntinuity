#!/usr/bin/env python3
"""Repeatable local benchmark; prints metrics and never changes canonical sources."""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import gptina_memory as gm  # noqa: E402


def timed_command(*args: str) -> float:
    started = time.perf_counter()
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return (time.perf_counter() - started) * 1000.0


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))]


def main() -> None:
    dirty = gm.git_worktree_dirty()
    sync = gm.sync_sqlite_index(False, allow_dirty_preview=dirty)
    cases = json.loads((ROOT / "rag/eval/GPTINA_MEMORY_GOLD.json").read_text(encoding="utf-8"))
    search_ms: list[float] = []
    exact_ms: list[float] = []
    for case in cases:
        started = time.perf_counter()
        if case.get("mode", "search") == "exact":
            gm.exact_matches(case["query"], limit=20)
            exact_ms.append((time.perf_counter() - started) * 1000.0)
        else:
            gm.sqlite_search(
                case["query"],
                int(case.get("top_k", 6)),
                allow_dirty_preview=dirty,
            )
            search_ms.append((time.perf_counter() - started) * 1000.0)
    report = {
        "head": gm.git_head(),
        "snapshot_mode": "dirty-preview" if dirty else "committed",
        "sync": sync,
        "query_ms": {
            "count": len(search_ms),
            "mean": round(statistics.mean(search_ms), 3) if search_ms else 0.0,
            "p50": round(percentile(search_ms, 0.50), 3),
            "p95": round(percentile(search_ms, 0.95), 3),
        },
        "exact_ms": {
            "count": len(exact_ms),
            "mean": round(statistics.mean(exact_ms), 3) if exact_ms else 0.0,
            "p95": round(percentile(exact_ms, 0.95), 3),
        },
        "verify_ms": round(timed_command("rag/gptina_memory.py", "verify"), 3),
        "live_verify_ms": round(timed_command("rag/live_context.py", "verify"), 3),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
