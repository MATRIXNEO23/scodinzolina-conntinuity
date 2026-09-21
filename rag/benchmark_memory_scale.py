#!/usr/bin/env python3
"""Disposable scale benchmark for GPTina memory.

The canonical corpus is read-only. Synthetic replicas and every SQLite file are
created under a temporary directory and removed when the process exits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import gptina_memory as gm  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, int((len(ordered) - 1) * fraction))
    return ordered[index]


def timing_summary(values: list[float]) -> dict[str, float | int]:
    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 3) if values else 0.0,
        "p50": round(percentile(values, 0.50), 3),
        "p95": round(percentile(values, 0.95), 3),
    }


def diversified_content(content: str, blocked_terms: set[str], replica: int) -> str:
    """Preserve document shape while removing every gold-query token."""

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.casefold() not in blocked_terms:
            return token
        marker = f"z{replica:x}q"
        return (marker * ((len(token) // len(marker)) + 1))[: len(token)]

    return gm.TOKEN_RE.sub(replace, content)


def scaled_versions(
    originals: list[gm.SourceVersion],
    scale: int,
    corpus_mode: str,
    blocked_terms: set[str],
) -> list[gm.SourceVersion]:
    replicas: list[gm.SourceVersion] = []
    for replica in range(scale):
        prefix = f"synthetic/replica-{replica:03d}"
        for source in originals:
            replicas.append(
                gm.SourceVersion(
                    path=f"{prefix}/{source.path}",
                    kind=source.kind,
                    priority=source.priority,
                    revision=source.revision,
                    content=(
                        source.content
                        if corpus_mode == "replicated" or replica == 0
                        else diversified_content(source.content, blocked_terms, replica)
                    ),
                    historical=source.historical,
                    status=source.status,
                    replaced_by=source.replaced_by,
                )
            )
    return replicas


def canonical_source(path: str) -> str:
    parts = path.split("/", 2)
    if len(parts) == 3 and parts[0] == "synthetic" and parts[1].startswith("replica-"):
        return parts[2]
    return path


def configure_temporary_projection(temp_root: Path, fingerprint: str, scale: int) -> None:
    temp_rag = temp_root / "rag"
    temp_index = temp_rag / "index"
    temp_index.mkdir(parents=True)
    manifest = temp_rag / "memory_manifest.json"
    manifest.write_bytes((ROOT / "rag" / "memory_manifest.json").read_bytes())

    gm.ROOT = temp_root
    gm.RAG_ROOT = temp_rag
    gm.INDEX_DIR = temp_index
    gm.GENERATION_ROOT = temp_index / ".projection-generations"
    gm.CURRENT_GENERATION_FILE = temp_index / ".projection-current"
    gm.LEGACY_INDEX_FILE = temp_index / "memory_chunks.jsonl"
    gm.LEGACY_META_FILE = temp_index / "index_meta.json"
    gm.LEGACY_SQLITE_FILE = temp_index / "gptina_memory.sqlite3"
    gm._refresh_projection_paths()
    gm.MANIFEST_FILE = manifest
    gm._DIRTY_PREVIEW_FINGERPRINT = None
    gm.git_worktree_dirty = lambda: False
    gm.git_head = lambda: f"synthetic-scale-{scale}"
    gm.current_source_fingerprint = lambda _manifest: fingerprint


def exact_trigram_experiment(
    versions: list[gm.SourceVersion],
    gold: list[dict],
    temp_root: Path,
    repetitions: int,
) -> dict:
    exact_cases = [case for case in gold if case.get("mode", "search") == "exact"]
    database = temp_root / "exact_trigram.sqlite3"
    conn = sqlite3.connect(database)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    started = time.perf_counter()
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE exact_fts USING fts5("
            "source UNINDEXED, text, tokenize='trigram case_sensitive 0')"
        )
        with conn:
            conn.executemany(
                "INSERT INTO exact_fts(source, text) VALUES (?, ?)",
                ((source.path, source.content) for source in versions),
            )
        build_ms = (time.perf_counter() - started) * 1000.0
        query_ms: list[float] = []
        passed = 0
        failed_case_ids: list[str] = []
        for case in exact_cases:
            expected = set(case.get("expected_any", []))
            sources: list[str] = []
            phrase = '"' + str(case["query"]).replace('"', '""') + '"'
            for _ in range(repetitions):
                started = time.perf_counter()
                rows = conn.execute(
                    "SELECT source, text FROM exact_fts WHERE text MATCH ? LIMIT 20",
                    (phrase,),
                ).fetchall()
                needle = str(case["query"]).casefold()
                sources = [source for source, text in rows if needle in text.casefold()]
                query_ms.append((time.perf_counter() - started) * 1000.0)
            normalized = [canonical_source(source) for source in sources]
            if not expected or any(source in expected for source in normalized):
                passed += 1
            else:
                failed_case_ids.append(str(case["id"]))
    finally:
        conn.close()
    database_bytes = sum(
        path.stat().st_size
        for path in temp_root.glob("exact_trigram.sqlite3*")
        if path.is_file()
    )
    return {
        "backend": "sqlite-fts5-trigram-experimental",
        "build_ms": round(build_ms, 3),
        "database_bytes": database_bytes,
        "query_ms": timing_summary(query_ms),
        "gold_pass": passed,
        "gold_total": len(exact_cases),
        "failed_case_ids": failed_case_ids,
    }


def run_scale(
    originals: list[gm.SourceVersion],
    gold: list[dict],
    chunking: dict,
    scale: int,
    repetitions: int,
    corpus_mode: str,
    exact_index_experiment: bool,
) -> dict:
    blocked_terms = {
        token
        for case in gold
        for token in gm.tokenize(str(case["query"]))
    }
    versions = scaled_versions(originals, scale, corpus_mode, blocked_terms)
    source_bytes = sum(len(source.content.encode("utf-8")) for source in versions)

    started = time.perf_counter()
    hashes = [gm.sha256_text(source.content) for source in versions]
    hashing_ms = (time.perf_counter() - started) * 1000.0
    fingerprint = hashlib.sha256("\n".join(hashes).encode("ascii")).hexdigest()

    started = time.perf_counter()
    expected_chunks = sum(
        len(
            gm.chunk_text(
                source.content,
                int(chunking.get("max_chars", 1400)),
                int(chunking.get("overlap_chars", 220)),
                int(chunking.get("min_chars", 120)),
            )
        )
        for source in versions
    )
    chunking_ms = (time.perf_counter() - started) * 1000.0

    with tempfile.TemporaryDirectory(prefix=f"gptina-scale-{scale}x-") as tmp:
        temp_root = Path(tmp)
        configure_temporary_projection(temp_root, fingerprint, scale)
        gm.collect_versions = lambda _include_history: versions

        first_sync = gm.sync_sqlite_index(False)
        no_op_sync = gm.sync_sqlite_index(False)
        if first_sync["chunks"] != expected_chunks:
            raise AssertionError(
                f"scale {scale}: expected {expected_chunks} chunks, "
                f"built {first_sync['chunks']}"
            )
        if no_op_sync["changed_sources"] or no_op_sync["removed_sources"]:
            raise AssertionError(f"scale {scale}: second sync was not a no-op")

        query_ms: list[float] = []
        exact_ms: list[float] = []
        quality_passes = 0
        quality_cases = 0
        failed_case_ids: list[str] = []
        for case in gold:
            expected = set(case.get("expected_any", []))
            forbidden = set(case.get("forbidden", []))
            sources: list[str] = []
            if case.get("mode", "search") == "exact":
                for _ in range(repetitions):
                    started = time.perf_counter()
                    needle = case["query"].casefold()
                    sources = [
                        source.path
                        for source in versions
                        if needle in source.content.casefold()
                    ][:20]
                    exact_ms.append((time.perf_counter() - started) * 1000.0)
            else:
                for _ in range(repetitions):
                    started = time.perf_counter()
                    ranked = gm.sqlite_search(case["query"], int(case.get("top_k", 6)))
                    query_ms.append((time.perf_counter() - started) * 1000.0)
                    sources = [item[1]["source"] for item in ranked]

            normalized = [canonical_source(source) for source in sources]
            quality_cases += 1
            hit_expected = not expected or any(source in expected for source in normalized)
            hit_forbidden = any(source in forbidden for source in normalized)
            quality_passes += int(hit_expected and not hit_forbidden)
            if not hit_expected or hit_forbidden:
                failed_case_ids.append(str(case["id"]))

        db_bytes = sum(
            path.stat().st_size
            for path in gm.SQLITE_FILE.parent.glob(gm.SQLITE_FILE.name + "*")
            if path.is_file()
        )
        report = {
            "scale": scale,
            "corpus_mode": corpus_mode,
            "sources": len(versions),
            "source_bytes": source_bytes,
            "chunks": first_sync["chunks"],
            "database_bytes": db_bytes,
            "hashing_ms": round(hashing_ms, 3),
            "chunking_ms": round(chunking_ms, 3),
            "initial_sync": first_sync,
            "no_op_sync": no_op_sync,
            "query_ms": timing_summary(query_ms),
            "exact_scan_ms": timing_summary(exact_ms),
            "normalized_gold_pass": quality_passes,
            "normalized_gold_total": quality_cases,
            "failed_case_ids": failed_case_ids,
        }
        if exact_index_experiment:
            report["exact_trigram_experiment"] = exact_trigram_experiment(
                versions, gold, temp_root, repetitions
            )
        return report


def parse_scales(raw: str) -> list[int]:
    values = sorted({int(item.strip()) for item in raw.split(",") if item.strip()})
    if not values or any(value < 1 for value in values):
        raise argparse.ArgumentTypeError("scales must be positive comma-separated integers")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scales", type=parse_scales, default=[1, 10])
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument(
        "--corpus-mode",
        choices=("replicated", "diversified"),
        default="replicated",
        help="replicated stresses duplicates; diversified masks gold-query tokens in added records",
    )
    parser.add_argument(
        "--exact-index-experiment",
        action="store_true",
        help="also build a disposable FTS5 trigram index for exact substring lookup",
    )
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")

    canonical_head = gm.git_head()
    originals = gm.collect_versions(False)
    chunking = gm.load_manifest().get("chunking", {})
    gold = json.loads((ROOT / "rag/eval/GPTINA_MEMORY_GOLD.json").read_text(encoding="utf-8"))
    report = {
        "benchmark": "gptina-memory-disposable-scale-v2",
        "canonical_head": canonical_head,
        "canonical_sources_modified": False,
        "corpus_mode": args.corpus_mode,
        "scales": [
            run_scale(
                originals,
                gold,
                chunking,
                scale,
                args.repetitions,
                args.corpus_mode,
                args.exact_index_experiment,
            )
            for scale in args.scales
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
