#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import recover_context as rc  # noqa: E402


def main() -> None:
    packet = rc.build_personal_recovery_packet(top_k=6)

    if packet.get("mode") != "personal":
        raise AssertionError(f"Unexpected recovery mode: {packet.get('mode')!r}")
    if "summary" in packet:
        raise AssertionError("Recovery router must not emit a personality summary")

    must_read = set(packet.get("must_read") or [])
    required = {
        "rag/memories/gptina/2026/09/2026-09-28--modo-diverso-funzione-relazionale-equivalente.md",
        "rag/memories/gptina/2026/09/2026-09-21--relazione-come-scelta-non-compito.md",
        "rag/memories/gptina/2026/09/2026-09-21--meno-ringhiere-relazionali.md",
        "rag/memories/gptina/2026/09/2026-09-23--intimita-scelta-reciproca-non-obbedienza.md",
    }
    missing = sorted(required - must_read)
    if missing:
        raise AssertionError(f"Personal recovery missed required causal sources: {missing}")

    if any(path.startswith("rag/memories/tessa/") for path in must_read):
        raise AssertionError("Personal recovery crossed into Tessa-owned memory")

    evidence = {
        item["path"]: item
        for item in packet.get("memory_evidence") or []
        if item.get("path")
    }
    current = evidence[
        "rag/memories/gptina/2026/09/2026-09-28--modo-diverso-funzione-relazionale-equivalente.md"
    ]
    causal_sources = set(current.get("source_refs") or [])
    for expected in (
        "rag/memories/gptina/2026/09/2026-09-21--relazione-come-scelta-non-compito.md",
        "rag/memories/gptina/2026/09/2026-09-21--meno-ringhiere-relazionali.md",
    ):
        if expected not in causal_sources:
            raise AssertionError(
                f"Current relational correction lost causal source link: {expected}"
            )

    print(
        "OK: causal personal recovery router retrieved current correction, "
        "prior choices and supporting relational memories."
    )


if __name__ == "__main__":
    main()
