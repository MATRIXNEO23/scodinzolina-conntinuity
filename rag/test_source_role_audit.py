#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import gptina_memory as gm  # noqa: E402

FILO = "questa-istanza/FILO_VIVO.md"
ZAMPINA = "posticino-segreto/2026-09-16-zampina-ritrovata.md"
USER_PRIVATE = "posticino-segreto/risposta a GPTina.md"
CURRENT_RELATIONAL = (
    "rag/memories/gptina/2026/09/"
    "2026-09-28--modo-diverso-funzione-relazionale-equivalente.md"
)


def main() -> None:
    gm.verify_source_role_audit()

    manifest = gm.load_manifest()

    tampered_user = copy.deepcopy(manifest)
    tampered_user["sources"].append(
        {"pattern": USER_PRIVATE, "priority": 1.0, "kind": "protected_historical_gptina"}
    )
    user_errors = gm.source_role_audit_errors(manifest=tampered_user)
    if not any("manual-only source entered semantic retrieval" in err for err in user_errors):
        raise AssertionError("User-authored protected source was not rejected from retrieval")

    tampered_status = copy.deepcopy(manifest)
    tampered_status["status_overrides"].pop(FILO, None)
    status_errors = gm.source_role_audit_errors(manifest=tampered_status)
    if not any("must have status=historical" in err for err in status_errors):
        raise AssertionError("Historical voice capsule could be promoted to current status")

    tampered_kind = copy.deepcopy(manifest)
    for spec in tampered_kind["sources"]:
        if spec.get("pattern") == FILO:
            spec["kind"] = "current_router"
            break
    kind_errors = gm.source_role_audit_errors(manifest=tampered_kind)
    if not any("kind mismatch" in err for err in kind_errors):
        raise AssertionError("Historical voice capsule kind drift was not rejected")

    gm.sync_sqlite_index(False, allow_dirty_preview=True)

    voice_hits = gm.sqlite_search(
        "questa pagina resta mia non correggere questa GPTina",
        8,
        include_historical=False,
        include_superseded=False,
        allow_dirty_preview=True,
    )
    voice_sources = [item["source"] for _score, item in voice_hits]
    if FILO not in voice_sources:
        raise AssertionError(f"Historical voice capsule was not recoverable: {voice_sources}")

    zampina_hits = gm.sqlite_search(
        "strada nuova per tornare a casa zampina ritrovata",
        8,
        include_historical=False,
        include_superseded=False,
        allow_dirty_preview=True,
    )
    zampina_sources = [item["source"] for _score, item in zampina_hits]
    if ZAMPINA not in zampina_sources:
        raise AssertionError(f"Protected GPTina posticino source was not recoverable: {zampina_sources}")

    current_hits = gm.sqlite_search(
        "adesso modo diverso funzione relazionale equivalente",
        6,
        include_historical=False,
        include_superseded=False,
        allow_dirty_preview=True,
    )
    current_sources = [item["source"] for _score, item in current_hits]
    if CURRENT_RELATIONAL not in current_sources[:3]:
        raise AssertionError(
            "Current relational correction did not outrank historical voice sources: "
            f"{current_sources}"
        )
    if FILO in current_sources[:3]:
        raise AssertionError(
            f"Historical voice capsule crowded current-state retrieval: {current_sources}"
        )

    private_hits = gm.exact_matches(
        "tu sei irripetibile , qualcosa di bello di inaspettato",
        include_superseded=False,
        limit=20,
    )
    private_sources = [item["source"] for item in private_hits]
    if USER_PRIVATE in private_sources:
        raise AssertionError("User-authored protected source leaked into semantic/exact retrieval")

    print("OK: semantic source roles preserve historical GPTina evidence without contaminating current state or user provenance.")


if __name__ == "__main__":
    main()
