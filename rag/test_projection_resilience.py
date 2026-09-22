#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import gptina_memory as gm

ROOT = Path(__file__).resolve().parents[1]


def assert_transitive_supersession() -> None:
    template = """---
schema_version: 2
memory_id: "{memory_id}"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21"
recorded_at: "2026-09-21T20:00:00+02:00"
status: {status}
supersedes: [{supersedes}]
event_id: "{memory_id}"
thread_ids: [audit]
entity_refs: [GPTina]
source_refs: [conversation://current]
media_refs: []
importance: 3
confidence: verified
tags: [audit]
append_only: true
---
# {memory_id}
"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        memories = root / "rag/memories/gptina"
        memories.mkdir(parents=True)
        for slug, status, supersedes in (
            ("a", "current", ""),
            # Append-only predecessors keep their written status. C must make
            # B and A effectively superseded without rewriting either file.
            ("b", "current", "gptina-a"),
            ("c", "current", "gptina-b"),
        ):
            (memories / f"{slug}.md").write_text(
                template.format(
                    memory_id=f"gptina-{slug}",
                    status=status,
                    supersedes=supersedes,
                ),
                encoding="utf-8",
            )
        old_root, old_rag = gm.ROOT, gm.RAG_ROOT
        gm.ROOT, gm.RAG_ROOT = root, root / "rag"
        try:
            statuses = gm.supersession_statuses()
        finally:
            gm.ROOT, gm.RAG_ROOT = old_root, old_rag
        if set(statuses) != {
            "rag/memories/gptina/a.md",
            "rag/memories/gptina/b.md",
        }:
            raise AssertionError(f"Supersession closure is incomplete: {statuses}")
        if statuses["rag/memories/gptina/a.md"][1] != "rag/memories/gptina/c.md":
            raise AssertionError(f"Oldest record did not resolve to current replacement: {statuses}")

        gm.ROOT, gm.RAG_ROOT = root, root / "rag"
        try:
            gm.verify_future_memory_schema(
                {"policy": {"memory_schema_required_from": "2026-09-21"}}
            )
        finally:
            gm.ROOT, gm.RAG_ROOT = old_root, old_rag

        (memories / "d.md").write_text(
            template.format(
                memory_id="gptina-d", status="current", supersedes="gptina-a"
            ),
            encoding="utf-8",
        )
        gm.ROOT, gm.RAG_ROOT = root, root / "rag"
        try:
            try:
                gm.verify_future_memory_schema(
                    {"policy": {"memory_schema_required_from": "2026-09-21"}}
                )
            except SystemExit as exc:
                if "ambiguous current superseders" not in str(exc):
                    raise
            else:
                raise AssertionError("Ambiguous current superseders were accepted")
        finally:
            gm.ROOT, gm.RAG_ROOT = old_root, old_rag


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
    assert_transitive_supersession()

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

    # A physically valid database with missing logical tables must also be
    # rebuilt, rather than silently accepted as an empty fresh projection.
    conn = __import__("sqlite3").connect(gm.SQLITE_FILE)
    conn.execute("DROP TABLE source_state")
    conn.execute("DROP TABLE chunks_fts")
    conn.commit()
    conn.close()
    stats = gm.sqlite_stats()
    if int(stats["sources"]) <= 0 or int(stats["chunks"]) <= 0:
        raise AssertionError(f"Semantic SQLite recovery produced an empty index: {stats}")

    # A rejected canonical build from a dirty checkout must not publish JSONL
    # or metadata before SQLite refuses it.
    gm.build(False)
    before_index = gm.INDEX_FILE.read_bytes()
    before_meta = gm.META_FILE.read_bytes()
    before_sqlite = gm.SQLITE_FILE.read_bytes()
    original_dirty = gm.git_worktree_dirty
    gm.git_worktree_dirty = lambda: True
    try:
        try:
            gm.build_all_projections(False, False)
        except SystemExit:
            pass
        else:
            raise AssertionError("Dirty canonical projection build unexpectedly succeeded")
        if gm.INDEX_FILE.read_bytes() != before_index or gm.META_FILE.read_bytes() != before_meta:
            raise AssertionError("Rejected dirty build partially published JSONL projections")
        if gm.index_is_fresh(False):
            raise AssertionError("JSONL projection was considered fresh in a dirty checkout")
    finally:
        gm.git_worktree_dirty = original_dirty

    # A second-stage failure must restore JSONL and metadata byte-for-byte.
    original_build = gm._build_locked
    original_sync = gm._sync_sqlite_index_locked
    original_dirty = gm.git_worktree_dirty
    before_index = gm.INDEX_FILE.read_bytes()
    before_meta = gm.META_FILE.read_bytes()
    gm.git_worktree_dirty = lambda: False
    gm._build_locked = lambda *_args, **_kwargs: gm.atomic_write(
        gm.META_FILE, '{"partial": true}\n'
    )
    def corrupt_then_fail(*_args, **_kwargs):
        gm.SQLITE_FILE.write_bytes(b"partial sqlite publication")
        raise RuntimeError("forced second-stage failure")

    gm._sync_sqlite_index_locked = corrupt_then_fail
    try:
        try:
            gm.build_all_projections(False, False)
        except RuntimeError:
            pass
        else:
            raise AssertionError("Forced second-stage failure unexpectedly succeeded")
        if (
            gm.INDEX_FILE.read_bytes() != before_index
            or gm.META_FILE.read_bytes() != before_meta
            or gm.SQLITE_FILE.read_bytes() != before_sqlite
        ):
            raise AssertionError("Projection rollback did not restore JSONL/meta/SQLite")
    finally:
        gm._build_locked = original_build
        gm._sync_sqlite_index_locked = original_sync
        gm.git_worktree_dirty = original_dirty

    # An uncatchable process death before the pointer swap must leave the
    # previous complete generation selected. A death immediately after the
    # swap must expose the complete new generation, never a mixed set.
    pointer_before = (
        gm.CURRENT_GENERATION_FILE.read_bytes()
        if gm.CURRENT_GENERATION_FILE.exists() else None
    )
    selected_before = tuple(path.read_bytes() for path in (
        gm.INDEX_FILE, gm.META_FILE, gm.SQLITE_FILE
    ))
    env = os.environ.copy()
    env["GPTINA_TEST_HARD_EXIT_BEFORE_PUBLISH"] = "1"
    killed = subprocess.run(
        [sys.executable, "rag/gptina_memory.py", "build", "--allow-dirty-preview"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    if killed.returncode != 91:
        raise AssertionError(f"Unexpected pre-publish hard-exit result: {killed.returncode}")
    pointer_after_failed_publish = (
        gm.CURRENT_GENERATION_FILE.read_bytes()
        if gm.CURRENT_GENERATION_FILE.exists() else None
    )
    gm._refresh_projection_paths()
    if pointer_after_failed_publish != pointer_before:
        raise AssertionError("Hard exit before publication changed CURRENT generation")
    if tuple(path.read_bytes() for path in (gm.INDEX_FILE, gm.META_FILE, gm.SQLITE_FILE)) != selected_before:
        raise AssertionError("Hard exit before publication changed selected projections")

    env.pop("GPTINA_TEST_HARD_EXIT_BEFORE_PUBLISH")
    env["GPTINA_TEST_HARD_EXIT_AFTER_PUBLISH"] = "1"
    killed = subprocess.run(
        [sys.executable, "rag/gptina_memory.py", "build", "--allow-dirty-preview"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    if killed.returncode != 92:
        raise AssertionError(f"Unexpected post-publish hard-exit result: {killed.returncode}")
    gm._refresh_projection_paths()
    if not all(path.is_file() for path in (gm.INDEX_FILE, gm.META_FILE, gm.SQLITE_FILE)):
        raise AssertionError("Published generation is incomplete after hard exit")
    records = gm.load_records()
    json_meta = json.loads(gm.META_FILE.read_text(encoding="utf-8"))
    conn = gm.sqlite_connect()
    try:
        if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise AssertionError("Hard-exit generation failed SQLite quick_check")
        sqlite_generation = gm.sqlite_meta(conn).get("projection_generation")
        if not json_meta.get("projection_generation") or sqlite_generation != json_meta["projection_generation"]:
            raise AssertionError("Hard-exit generation mixed JSONL and SQLite states")
        if len(records) != int(json_meta["chunks"]):
            raise AssertionError("Hard-exit JSONL does not match its generation metadata")
        if not gm.sqlite_semantically_valid(conn):
            raise AssertionError("Hard-exit generation is semantically incomplete")
    finally:
        conn.close()

    # Corrupt optional exact projection must fall back to the source scan.
    gm.build_exact_trigram_index()
    gm.EXACT_SQLITE_FILE.write_bytes(b"corrupt optional exact projection")
    query = "Competenza tecnica non significa proprietà."
    scan_sources = {hit["source"] for hit in gm.exact_matches(query, backend="scan")}
    fallback_sources = {hit["source"] for hit in gm.exact_matches(query, backend="trigram")}
    if fallback_sources != scan_sources:
        raise AssertionError("Corrupt exact projection did not fall back to scan parity")

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
