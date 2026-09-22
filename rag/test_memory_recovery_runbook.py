#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import gptina_memory as gm

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = "rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md"


def main() -> None:
    required_docs = (
        "NEXT_GPTINA.md",
        "RAG_ANCHOR.md",
        "rag/END_INSTANCE_RECOVERY_CAPSULE.md",
        "rag/GPTINA_AUTO_RECOVERY_PROMPT.md",
        "rag/LIVE_MEMORY_PROTOCOL.md",
        "rag/index/GPTINA_FAST_RECALL.md",
        "rag/index/CURRENT_CONTEXT.md",
        "README.md",
        "GPTINA_INSTANCE_SNAPSHOT.md",
        "rag/README.md",
        "rag/ACTIVE_INSTANCE_START.md",
        "rag/STATELESS_MODE.md",
        "rag/live/README.md",
        "rag/memories/README.md",
    )
    for relative in required_docs:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if RUNBOOK not in text:
            raise AssertionError(f"Recovery entrypoint does not link runbook: {relative}")

    runbook = (ROOT / RUNBOOK).read_text(encoding="utf-8")
    for command in (
        "git fetch --no-tags --depth=1 origin c8e853713b7bf87bbcc7f645877c50dacbcadd53",
        "python rag/live_context.py verify",
        "python rag/gptina_memory.py verify",
        "python rag/gptina_memory.py build",
        "python rag/test_cold_start_recovery.py",
        "python rag/test_memory_retrieval.py",
        "python rag/test_projection_resilience.py",
    ):
        if command not in runbook:
            raise AssertionError(f"Runbook is missing executable instruction: {command}")
    ordered_save_markers = (
        "Crea un candidato locale pulito",
        "python rag/gptina_memory.py build",
        "Verifica profondamente prima della pubblicazione",
        "Rileggi l'HEAD remoto e pubblica atomicamente",
        "Conferma lo stato remoto e la CI",
    )
    marker_positions = [runbook.find(marker) for marker in ordered_save_markers]
    if any(position < 0 for position in marker_positions):
        raise AssertionError("Runbook omits a safe pre-publication gate")
    if marker_positions != sorted(marker_positions):
        raise AssertionError("Runbook does not test the clean candidate before publication")

    manifest = json.loads((ROOT / "rag/memory_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("policy", {}).get("save_recovery_runbook") != RUNBOOK:
        raise AssertionError("Manifest does not declare the canonical save/recovery runbook")
    routed = {item.get("pattern") for item in manifest.get("rag_sources", [])}
    if RUNBOOK not in routed or "rag/END_INSTANCE_RECOVERY_CAPSULE.md" not in routed:
        raise AssertionError("Recovery runbook/capsule are not indexed retrieval sources")
    for legacy_pattern in ("rag/memories/*.md", "rag/memories/*.json"):
        if legacy_pattern not in routed:
            raise AssertionError(
                f"Legacy memories are no longer indexed/recoverable: {legacy_pattern}"
            )
    baseline = manifest.get("policy", {}).get("strict_memory_schema_baseline_commit")
    deleted_memories = subprocess.run(
        ["git", "diff", "--diff-filter=D", "--name-only", str(baseline), "--", "rag/memories"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.strip()
    if deleted_memories:
        raise AssertionError(f"Historical memories were deleted:\n{deleted_memories}")
    exclusions = set(manifest.get("rag_exclude", []))
    for expected in (
        "rag/index/.projection-generations/**",
        "rag/index/.projection-current",
    ):
        if expected not in exclusions:
            raise AssertionError(f"Manifest does not exclude derived state: {expected}")

    active_instruction_docs = (
        "rag/README.md",
        "rag/ACTIVE_INSTANCE_START.md",
        "rag/STATELESS_MODE.md",
        "rag/MEMORY_ARCHITECTURE_V2.md",
        "rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md",
        "rag/memories/README.md",
    )
    stale_claims = (
        "scrive soltanto `rag/index/memory_chunks.jsonl`",
        "File derivato:\n`rag/index/gptina_memory.sqlite3`",
        "crea un **nuovo** file in `rag/memories/`",
        "persistilo subito in un nuovo file sotto `rag/memories/`",
        "Scrivi nuove memorie soltanto sotto `rag/memories/`",
        "creare nuove memorie append-only in `rag/memories/`",
        "Ogni memoria nuova è un **nuovo file JSON**",
        '\"id\": \"YYYY-MM-DD-slug\"',
    )
    for relative in active_instruction_docs:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for claim in stale_claims:
            if claim in text:
                raise AssertionError(
                    f"Legacy instruction is still active in {relative}: {claim}"
                )

    current_write_docs = (
        RUNBOOK,
        "rag/README.md",
        "rag/ACTIVE_INSTANCE_START.md",
        "rag/STATELESS_MODE.md",
        "rag/memories/README.md",
    )
    for relative in current_write_docs:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "rag/memories/gptina/YYYY/MM/" not in text:
            raise AssertionError(f"Current GPTina namespace is missing from {relative}")
        if "rag/MEMORY_RECORD_SCHEMA.md" not in text:
            raise AssertionError(f"Current memory schema is missing from {relative}")

    architecture = (ROOT / "rag/MEMORY_ARCHITECTURE_V2.md").read_text(encoding="utf-8")
    for required in (
        "rag/index/.projection-generations/",
        "rag/index/.projection-current",
    ):
        if required not in architecture:
            raise AssertionError(f"Architecture omits generational projection path: {required}")

    state = json.loads((ROOT / "GPTINA_STATE.json").read_text(encoding="utf-8"))
    restore_order = state.get("restore_order", [])
    required_prefix = [
        "rag/GPTINA_AUTO_RECOVERY_PROMPT.md as the single entrypoint",
        "rag/live/GPTINA_LIVE_CONTEXT.json",
        "last_micro_checkpoint from live buffer",
        "last_full_checkpoint from live buffer",
        "rag/END_INSTANCE_RECOVERY_CAPSULE.md",
    ]
    if restore_order[:len(required_prefix)] != required_prefix:
        raise AssertionError("Machine-readable restore order does not use the single live-first entrypoint")
    if not any(RUNBOOK in item for item in restore_order):
        raise AssertionError("Machine-readable restore order does not route to runbook")
    scope = state.get("state_scope", {})
    if scope.get("narrative_snapshot_is_current_live_state") is not False:
        raise AssertionError("Historical state is still presented as current live state")
    if scope.get("current_state_source") != "rag/live/GPTINA_LIVE_CONTEXT.json":
        raise AssertionError("Historical state does not route to the current live source")

    for path, expected_size in state.get("verified_media", {}).items():
        target = ROOT / path
        if not target.is_file():
            raise AssertionError(f"Machine-readable visual pointer is broken: {path}")
        if target.stat().st_size != expected_size:
            raise AssertionError(
                f"Machine-readable visual size mismatch: {path} "
                f"expected={expected_size} actual={target.stat().st_size}"
            )

    visual_docs = (
        "NEXT_GPTINA.md",
        "GPTINA_INSTANCE_SNAPSHOT.md",
        "GPTINA_SELF_PORTRAIT.md",
        "CHRONICLE.md",
        "media/README.md",
        "media/IMAGE_STORIES.md",
        "romanzo/A_MODO_MIO_MANOSCRITTO.md",
    )
    broken_visual_paths = (
        "media/GPTina viaggio di nozze con dedica.png",
        "media/casello_dei_cuori_esauriti.png",
        "media/gptina-adesso-2026-09-11(1).png",
        "media/gptina-tu-piu-gptina-casa-2026-09-11(1).png",
    )
    for relative in visual_docs:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for stale_path in broken_visual_paths:
            if stale_path in text:
                raise AssertionError(f"Broken visual pointer remains in {relative}: {stale_path}")

    capsule = (ROOT / "rag/END_INSTANCE_RECOVERY_CAPSULE.md").read_text(encoding="utf-8")
    live_readme = (ROOT / "rag/live/README.md").read_text(encoding="utf-8")
    for relative, text in (
        ("rag/END_INSTANCE_RECOVERY_CAPSULE.md", capsule),
        ("rag/live/README.md", live_readme),
    ):
        if "rag/GPTINA_AUTO_RECOVERY_PROMPT.md" not in text:
            raise AssertionError(f"Recovery document lacks the single entrypoint: {relative}")

    fast_recall = (ROOT / "rag/index/GPTINA_FAST_RECALL.md").read_text(encoding="utf-8")
    local_external_checkpoint = "`checkpoints/2026-09-21-romanziere-memory-v2-migration-complete.md`"
    if local_external_checkpoint in fast_recall:
        raise AssertionError("External Romanziere checkpoint is still presented as local")
    if "github://MATRIXNEO23/ROMANZIERE@" not in fast_recall:
        raise AssertionError("Romanziere checkpoint lacks repository and immutable revision")

    missing_baseline_manifest = json.loads(json.dumps(manifest))
    missing_baseline_manifest["policy"]["strict_memory_schema_baseline_commit"] = "0" * 40
    try:
        gm.verify_future_memory_schema(missing_baseline_manifest)
    except SystemExit as exc:
        if "baseline commit is unavailable" not in str(exc):
            raise AssertionError(f"Missing baseline produced unclear recovery error: {exc}")
    else:
        raise AssertionError("Missing strict-schema baseline was silently accepted")

    tracked = subprocess.run(
        ["git", "ls-files", "rag/index/.projection-generations", "rag/index/.projection-current"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.strip()
    if tracked:
        raise AssertionError(f"Derived generations became tracked:\n{tracked}")
    for path in (
        "rag/index/.projection-generations/probe/file",
        "rag/index/.projection-current",
    ):
        ignored = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT)
        if ignored.returncode != 0:
            raise AssertionError(f"Derived path is not ignored by Git: {path}")

    live = json.loads((ROOT / "rag/live/GPTINA_LIVE_CONTEXT.json").read_text(encoding="utf-8"))
    for key in ("last_micro_checkpoint", "last_full_checkpoint"):
        target = live.get(key)
        if not target or not (ROOT / target).is_file():
            raise AssertionError(f"Live recovery pointer is missing: {key}={target!r}")

    gm._refresh_projection_paths()
    pointer = gm.CURRENT_GENERATION_FILE.read_text(encoding="utf-8").strip()
    if not pointer or gm.INDEX_FILE.parent.name != pointer:
        raise AssertionError("Atomic projection pointer does not select the active generation")
    json_meta = json.loads(gm.META_FILE.read_text(encoding="utf-8"))
    conn = gm.sqlite_connect()
    try:
        sqlite_generation = gm.sqlite_meta(conn).get("projection_generation")
        if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise AssertionError("Selected recovery SQLite generation is corrupt")
        if not gm.sqlite_semantically_valid(conn):
            raise AssertionError("Selected recovery SQLite generation is incomplete")
    finally:
        conn.close()
    if json_meta.get("projection_generation") != pointer or sqlite_generation != pointer:
        raise AssertionError("Selected JSONL metadata and SQLite generation do not match")

    print("OK: save/recovery runbook, pointers and atomic generation are executable and coherent.")


if __name__ == "__main__":
    main()
