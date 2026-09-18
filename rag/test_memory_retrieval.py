#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import gptina_memory as gm  # noqa: E402

GOLD = ROOT / "rag" / "eval" / "GPTINA_MEMORY_GOLD.json"


def main() -> None:
    gm.verify_boundary()
    gm.ensure_fresh_index(False)
    tests = json.loads(GOLD.read_text(encoding="utf-8"))

    failures: list[str] = []
    for case in tests:
        mode = case.get("mode", "search")
        expected = set(case.get("expected_any", []))
        forbidden = set(case.get("forbidden", []))

        if mode == "exact":
            hits = gm.exact_matches(case["query"], include_superseded=False, limit=20)
            sources = [h["source"] for h in hits]
        else:
            ranked = gm.bm25_search(
                case["query"],
                int(case.get("top_k", 6)),
                include_historical=False,
                include_superseded=False,
            )
            sources = [d["source"] for _score, d in ranked]

        if expected and not any(src in expected for src in sources):
            failures.append(f"{case['id']}: expected one of {sorted(expected)}, got {sources}")
        present_forbidden = [src for src in sources if src in forbidden]
        if present_forbidden:
            failures.append(f"{case['id']}: forbidden source(s) retrieved: {present_forbidden}")

        print(f"{case['id']}: {sources[:8]}")

    if failures:
        print("\nREGRESSION FAILURES:")
        for item in failures:
            print(f"- {item}")
        raise SystemExit(1)

    print(f"\nOK: {len(tests)} GPTina memory regression cases passed.")


if __name__ == "__main__":
    main()
