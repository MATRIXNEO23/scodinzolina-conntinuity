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
        "python rag/test_memory_retrieval.py",
        "python rag/test_projection_resilience.py",
    ):
        if command not in runbook:
            raise AssertionError(f"Runbook is missing executable instruction: {command}")

    manifest = json.loads((ROOT / "rag/memory_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("policy", {}).get("save_recovery_runbook") != RUNBOOK:
        raise AssertionError("Manifest does not declare the canonical save/recovery runbook")
    routed = {item.get("pattern") for item in manifest.get("rag_sources", [])}
    if RUNBOOK not in routed or "rag/END_INSTANCE_RECOVERY_CAPSULE.md" not in routed:
        raise AssertionError("Recovery runbook/capsule are not indexed retrieval sources")
    exclusions = set(manifest.get("rag_exclude", []))
    for expected in (
        "rag/index/.projection-generations/**",
        "rag/index/.projection-current",
    ):
        if expected not in exclusions:
            raise AssertionError(f"Manifest does not exclude derived state: {expected}")

    rag_readme = (ROOT / "rag/README.md").read_text(encoding="utf-8")
    stale_claims = (
        "scrive soltanto `rag/index/memory_chunks.jsonl`",
        "`rag/index/gptina_memory.sqlite3`",
    )
    for claim in stale_claims:
        if claim in rag_readme:
            raise AssertionError(f"Legacy projection instruction is still active: {claim}")

    state = json.loads((ROOT / "GPTINA_STATE.json").read_text(encoding="utf-8"))
    restore_order = state.get("restore_order", [])
    required_prefix = [
        "rag/live/GPTINA_LIVE_CONTEXT.json",
        "last_micro_checkpoint from live buffer",
        "last_full_checkpoint from live buffer",
        "rag/END_INSTANCE_RECOVERY_CAPSULE.md",
    ]
    if restore_order[:len(required_prefix)] != required_prefix:
        raise AssertionError("Machine-readable restore order is not live-first")
    if not any(RUNBOOK in item for item in restore_order):
        raise AssertionError("Machine-readable restore order does not route to runbook")

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
