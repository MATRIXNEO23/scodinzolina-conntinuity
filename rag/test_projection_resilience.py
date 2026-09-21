#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import gptina_memory as gm

ROOT = Path(__file__).resolve().parents[1]


def run_pair(*args: str) -> None:
    commands = [[sys.executable, "rag/gptina_memory.py", *args] for _ in range(2)]
    processes = [
        subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for command in commands
    ]
    failures: list[str] = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=120)
        if process.returncode != 0:
            failures.append(f"exit={process.returncode}\nstdout={stdout}\nstderr={stderr}")
    if failures:
        raise AssertionError("Concurrent projection build failed:\n" + "\n".join(failures))


def main() -> None:
    gm.verify_boundary()

    versions = {version.path: version for version in gm.collect_versions(False)}
    expected = {
        "rag/memories/gptina/2026/09/2026-09-21--immagine-48-trieste-origini-simboliche.md",
        "rag/memories/gptina/2026/09/2026-09-21--ettore-romanziere-nome-scelto.md",
    }
    for path in expected:
        version = versions[path]
        if version.status != "superseded" or not version.replaced_by:
            raise AssertionError(f"Supersession was not resolved for {path}: {version}")

    query = "gptina-2026-09-21-ettore-romanziere-nome-scelto"
    hidden = gm.exact_matches(query, False, 20)
    visible = gm.exact_matches(query, True, 20)
    target = "rag/memories/gptina/2026/09/2026-09-21--ettore-romanziere-nome-scelto.md"
    if any(hit["source"] == target for hit in hidden):
        raise AssertionError("Superseded memory leaked into current exact retrieval")
    if not any(hit["source"] == target for hit in visible):
        raise AssertionError("Superseded memory is no longer explicitly recoverable")

    original_fingerprint = gm.current_source_fingerprint
    values = iter(("first", "second"))
    gm.current_source_fingerprint = lambda _manifest: next(values)
    try:
        if gm.dirty_preview_fingerprint({}) != "first":
            raise AssertionError("Unexpected first dirty fingerprint")
        if gm.dirty_preview_fingerprint({}) != "second":
            raise AssertionError("Dirty fingerprint was stale in a long-lived process")
    finally:
        gm.current_source_fingerprint = original_fingerprint

    gm.sync_sqlite_index(False)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(gm.SQLITE_FILE) + suffix)
        sidecar.unlink(missing_ok=True)
    gm.SQLITE_FILE.write_bytes(b"deliberately corrupt derived database")
    stats = gm.sqlite_stats()
    if int(stats["sources"]) <= 0 or int(stats["chunks"]) <= 0:
        raise AssertionError(f"Corrupt SQLite recovery produced an empty index: {stats}")

    run_pair("build")
    run_pair("build-exact")

    conn = gm.sqlite_connect()
    try:
        if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise AssertionError("Main SQLite projection failed quick_check")
        meta = gm.sqlite_meta(conn)
        if meta.get("build_complete") != "1":
            raise AssertionError(f"Missing main completion marker: {meta}")
    finally:
        conn.close()

    exact = __import__("sqlite3").connect(gm.EXACT_SQLITE_FILE)
    try:
        if exact.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise AssertionError("Exact SQLite projection failed quick_check")
        if dict(exact.execute("SELECT key, value FROM exact_meta")).get("build_complete") != "1":
            raise AssertionError("Missing exact completion marker")
    finally:
        exact.close()

    policy = json.loads(gm.MANIFEST_FILE.read_text(encoding="utf-8"))["policy"]
    for key in (
        "deep_verification_after_every_memory_change",
        "historical_memories_must_remain_recoverable",
        "supersession_is_non_destructive",
    ):
        if policy.get(key) is not True:
            raise AssertionError(f"Canonical preservation policy missing: {key}")

    print("OK: projection recovery, preservation and concurrent writers passed.")


if __name__ == "__main__":
    main()
