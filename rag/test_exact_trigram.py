#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import gptina_memory as gm

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    gold = json.loads((ROOT / "rag/eval/GPTINA_MEMORY_GOLD.json").read_text(encoding="utf-8"))
    exact_cases = [case for case in gold if case.get("mode", "search") == "exact"]
    if not gm.exact_trigram_is_fresh():
        raise AssertionError("exact trigram index is not fresh after build")
    for case in exact_cases:
        scan = gm.exact_matches(case["query"], limit=20, backend="scan")
        trigram = gm.exact_matches(case["query"], limit=20, backend="trigram")
        scan_sources = {hit["source"] for hit in scan}
        trigram_sources = {hit["source"] for hit in trigram}
        expected = set(case.get("expected_any", []))
        if expected and not (trigram_sources & expected):
            raise AssertionError(f"{case['id']}: trigram missed expected source")
        if not trigram_sources.issubset(scan_sources):
            raise AssertionError(f"{case['id']}: trigram returned an unverified source")
    print(f"OK: optional exact trigram parity passed for {len(exact_cases)} cases.")


if __name__ == "__main__":
    main()
