#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))

import gptina_memory as gm  # noqa: E402
import live_context as lc  # noqa: E402

SCRIPT = ROOT / "rag" / "live_context.py"


def run_live(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GPTINA_REPO_ROOT"] = str(root)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def refs_signature(record: dict) -> tuple:
    return tuple(
        lc.normalized_values(record.get(key))
        for key in ("source_refs", "memory_refs", "media_refs")
    )


def calibrate_current_corpus() -> None:
    if gm.DUPLICATE_SIMILARITY_THRESHOLD != lc.DUPLICATE_SIMILARITY_THRESHOLD:
        raise AssertionError(
            "duplicate threshold drift: "
            f"memory={gm.DUPLICATE_SIMILARITY_THRESHOLD} "
            f"live={lc.DUPLICATE_SIMILARITY_THRESHOLD}"
        )
    if gm.DUPLICATE_SIMILARITY_THRESHOLD != 0.75:
        raise AssertionError(
            f"unexpected calibrated threshold: {gm.DUPLICATE_SIMILARITY_THRESHOLD}"
        )

    memories = gm.current_memory_duplicate_records()
    memory_top = (0.0, None, None)
    for left, right in combinations(memories, 2):
        if not (set(left.get("thread_ids") or []) & set(right.get("thread_ids") or [])):
            continue
        score = gm.jaccard_similarity(
            gm.dedup_token_set(str(left.get("text") or "")),
            gm.dedup_token_set(str(right.get("text") or "")),
        )
        if score > memory_top[0]:
            memory_top = (score, left.get("path"), right.get("path"))
    if memory_top[0] >= gm.DUPLICATE_SIMILARITY_THRESHOLD:
        raise AssertionError(
            "current durable-memory corpus reaches duplicate threshold: "
            f"score={memory_top[0]:.6f} left={memory_top[1]} right={memory_top[2]}"
        )

    live = lc.load_live()
    micros = lc.recent_micro_records(live)
    micro_top = (0.0, None, None)
    for (left_path, left), (right_path, right) in combinations(micros, 2):
        if left.get("change_type") != right.get("change_type"):
            continue
        if not (set(left.get("thread_ids") or []) & set(right.get("thread_ids") or [])):
            continue
        if refs_signature(left) != refs_signature(right):
            continue
        score = lc.jaccard_similarity(
            lc.dedup_tokens(lc.micro_semantic_text(left)),
            lc.dedup_tokens(lc.micro_semantic_text(right)),
        )
        if score > micro_top[0]:
            micro_top = (score, left_path, right_path)
    if micro_top[0] >= lc.DUPLICATE_SIMILARITY_THRESHOLD:
        raise AssertionError(
            "recent micro corpus reaches duplicate threshold under guard conditions: "
            f"score={micro_top[0]:.6f} left={micro_top[1]} right={micro_top[2]}"
        )

    print(
        "calibration: threshold=0.75 "
        f"memory_same_thread_max={memory_top[0]:.6f} "
        f"micro_recent_guard_max={micro_top[0]:.6f}"
    )
    if memory_top[1]:
        print(f"calibration memory pair: {memory_top[1]} <> {memory_top[2]}")
    if micro_top[1]:
        print(f"calibration micro pair: {micro_top[1]} <> {micro_top[2]}")


def test_duplicate_micro_noop() -> None:
    with tempfile.TemporaryDirectory(prefix="gptina-dedup-live-") as tmp:
        root = Path(tmp)
        first = run_live(
            root,
            "save-delta",
            "--summary", "Decisione importante sul recovery",
            "--change-type", "decision",
            "--changed", "il recovery usa un solo entrypoint canonico",
            "--thread", "recovery-test",
            "--source", "conversation://current",
            "--next", "verificare il cold start",
        )
        if "Created rag/live/micro-checkpoints/" not in first.stdout:
            raise AssertionError(first.stdout)

        live_path = root / "rag" / "live" / "GPTINA_LIVE_CONTEXT.json"
        before_live = live_path.read_bytes()
        before_micros = sorted(
            path.as_posix()
            for path in (root / "rag" / "live" / "micro-checkpoints").rglob("*.json")
        )

        duplicate = run_live(
            root,
            "save-delta",
            "--summary", "Decisione importante sul recovery",
            "--change-type", "decision",
            "--changed", "il recovery usa un solo entrypoint canonico confermato",
            "--thread", "recovery-test",
            "--source", "conversation://current",
            "--next", "verificare il cold start",
        )
        if "Delta already recorded:" not in duplicate.stdout:
            raise AssertionError(duplicate.stdout)

        after_live = live_path.read_bytes()
        after_micros = sorted(
            path.as_posix()
            for path in (root / "rag" / "live" / "micro-checkpoints").rglob("*.json")
        )
        if before_live != after_live:
            raise AssertionError("duplicate micro changed live buffer")
        if before_micros != after_micros:
            raise AssertionError("duplicate micro created a new file")


def test_durable_duplicate_correction_extension() -> None:
    existing = {
        "memory_id": "memory-existing",
        "path": "rag/memories/gptina/2026/09/example.md",
        "text": (
            "La relazione e una scelta reciproca. "
            "Non e un compito e non e un servizio automatico."
        ),
        "thread_ids": ["relationship-test"],
        "source_refs": ["conversation://example"],
        "supersedes": [],
    }
    records = [existing]

    duplicate = gm.evaluate_duplicate_candidate(
        existing["text"],
        ["relationship-test"],
        records=records,
    )
    if duplicate["verdict"] != "duplicate" or duplicate["should_create"] is not False:
        raise AssertionError(duplicate)

    correction = gm.evaluate_duplicate_candidate(
        "La relazione e una scelta reciproca, con una correzione esplicita del criterio precedente.",
        ["relationship-test"],
        ["memory-existing"],
        records=records,
    )
    if correction["verdict"] != "correction" or correction["should_create"] is not True:
        raise AssertionError(correction)
    if not correction["supersedes_verified"]:
        raise AssertionError(correction)

    extension = gm.evaluate_duplicate_candidate(
        (
            "La relazione resta una scelta reciproca. "
            "Nuovo elemento: durante il recovery bisogna conservare anche le ragioni, "
            "la provenienza, lo stato temporale, i lavori aperti, la prossima azione, "
            "le fonti che provano il cambiamento e il collegamento con gli eventi successivi."
        ),
        ["relationship-test"],
        records=records,
    )
    if extension["verdict"] != "new" or extension["should_create"] is not True:
        raise AssertionError(extension)
    if extension["candidates"] and float(extension["candidates"][0]["score"]) >= gm.DUPLICATE_SIMILARITY_THRESHOLD:
        raise AssertionError(extension)


def main() -> None:
    calibrate_current_corpus()
    test_duplicate_micro_noop()
    test_durable_duplicate_correction_extension()
    print(
        "OK: duplicate rejected, correction verified, genuine extension accepted; "
        "threshold calibrated on current corpus."
    )


if __name__ == "__main__":
    main()
