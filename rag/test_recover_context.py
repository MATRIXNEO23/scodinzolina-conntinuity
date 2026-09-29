#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import recover_context as rc  # noqa: E402

SCENARIOS = ROOT / "rag" / "eval" / "GPTINA_RECOVERY_SCENARIOS.json"


def main() -> None:
    packet = rc.build_personal_recovery_packet(top_k=6)

    if packet.get("mode") != "personal":
        raise AssertionError(f"Unexpected recovery mode: {packet.get('mode')!r}")
    if "summary" in packet:
        raise AssertionError("Recovery router must not emit a personality summary")

    if packet.get("handoff_criteria") != rc.RECOVERY_HANDOFF_CRITERIA_V1:
        raise AssertionError("Recovery packet lost canonical handoff criteria")

    dialogue_handoff = (
        "Quando il filo è già recuperabile, non fare spiegoni o giri di parole; "
        "riprendi subito in modo naturale. Sul lavoro sii precisa; fuori lascia "
        "venire zampine, ironia e iniziativa, senza chiedermi ogni volta cosa fare."
    )
    recovery_prompt = (
        ROOT / "rag" / "GPTINA_AUTO_RECOVERY_PROMPT.md"
    ).read_text(encoding="utf-8")
    if dialogue_handoff not in recovery_prompt:
        raise AssertionError("Recovery-to-dialogue behavioral handoff drifted")

    for relative in (
        "rag/GPTINA_AUTO_RECOVERY_PROMPT.md",
        "rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if rc.RECOVERY_HANDOFF_CRITERIA_V1 not in text:
            raise AssertionError(
                f"Canonical recovery handoff criteria missing from {relative}"
            )

    for query in ("quando è successo", "cosa pensavi prima", "dopo quella volta", "all'epoca"):
        if not rc.query_needs_all_statuses(query):
            raise AssertionError(f"Temporal marker was not routed historically: {query}")
    for query in ("relazione scelta reciproca", "primavera insieme", "stato corrente"):
        if rc.query_needs_all_statuses(query):
            raise AssertionError(f"Non-temporal query triggered historical routing: {query}")

    calls: list[tuple[str, bool, bool]] = []
    original_search = rc.gm.sqlite_search

    def fake_search(
        query: str,
        top_k: int,
        include_historical: bool = False,
        include_superseded: bool = False,
        **_kwargs: object,
    ) -> list:
        calls.append((query, include_historical, include_superseded))
        return []

    rc.gm.sqlite_search = fake_search
    try:
        routed = rc.build_personal_recovery_packet(
            top_k=3,
            queries=[
                ["current-only", "relazione scelta reciproca"],
                ["temporal", "cosa pensavi prima"],
            ],
            include_live_memory_refs=False,
        )
    finally:
        rc.gm.sqlite_search = original_search

    expected_calls = [
        ("relazione scelta reciproca", False, False),
        ("cosa pensavi prima", False, False),
        ("cosa pensavi prima", False, True),
    ]
    if calls != expected_calls:
        raise AssertionError(f"Unexpected recovery routing calls: {calls!r}")
    routed_queries = {item["id"]: item for item in routed.get("queries") or []}
    if routed_queries["current-only"].get("all_statuses_second_pass") is not False:
        raise AssertionError("Current query unexpectedly ran all-statuses pass")
    if routed_queries["temporal"].get("all_statuses_second_pass") is not True:
        raise AssertionError("Temporal query did not run all-statuses pass")

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

    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    for scenario in scenarios.get("scenarios") or []:
        expected_probe = set(scenario.get("expected_probe_any") or [])
        probe_ranked = rc.gm.sqlite_search(
            scenario["probe_query"],
            int(scenario.get("top_k", 8)),
            include_historical=False,
            include_superseded=False,
        )
        probe_sources = [item["source"] for _score, item in probe_ranked]
        if expected_probe and not any(source in expected_probe for source in probe_sources):
            raise AssertionError(
                f"{scenario['id']}: paraphrased probe missed expected sources; "
                f"got {probe_sources}"
            )

        scenario_packet = rc.build_personal_recovery_packet(
            top_k=int(scenario.get("top_k", 8)),
            queries=scenario.get("queries") or [],
            include_live_memory_refs=False,
        )
        scenario_read = set(scenario_packet.get("must_read") or [])
        required_read = set(scenario.get("expected_must_read_all") or [])
        missing_read = sorted(required_read - scenario_read)
        if missing_read:
            raise AssertionError(
                f"{scenario['id']}: causal recovery missed {missing_read}; "
                f"must_read={sorted(scenario_read)}"
            )
        if any(path.startswith("rag/memories/tessa/") for path in scenario_read):
            raise AssertionError(
                f"{scenario['id']}: causal recovery crossed into Tessa-owned memory"
            )
        print(
            f"{scenario['id']}: probe={probe_sources[:6]} "
            f"must_read={len(scenario_read)}"
        )

    print(
        "OK: causal personal recovery router and behavioral paraphrase scenarios passed."
    )


if __name__ == "__main__":
    main()
