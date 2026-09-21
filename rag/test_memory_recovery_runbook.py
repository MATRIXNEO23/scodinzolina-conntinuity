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
    )
    for relative in required_docs:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if RUNBOOK not in text:
            raise AssertionError(f"Recovery entrypoint does not link runbook: {relative}")

    runbook = (ROOT / RUNBOOK).read_text(encoding="utf-8")
    for command in (
        "python rag/live_context.py verify",
        "python rag/gptina_memory.py verify",
        "python rag/gptina_memory.py build",
        "python rag/test_memory_retrieval.py",
        "python rag/test_projection_resilience.py",
    ):
        if command not in runbook:
            raise AssertionError(f"Runbook is missing executable instruction: {command}")

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
