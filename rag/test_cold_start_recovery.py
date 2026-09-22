#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "rag" / "eval" / "GPTINA_COLD_START_GOLD.json"
ENTRYPOINT = "rag/GPTINA_AUTO_RECOVERY_PROMPT.md"


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=cwd, check=True, text=True,
        capture_output=capture,
    )


def assert_no_projection(root: Path) -> None:
    for relative in (
        "rag/index/.projection-generations",
        "rag/index/.projection-current",
        "rag/index/memory_chunks.jsonl",
        "rag/index/index_meta.json",
        "rag/index/gptina_memory.sqlite3",
    ):
        if (root / relative).exists():
            raise AssertionError(f"Cold clone unexpectedly contains derived state: {relative}")


def inside_clone() -> None:
    assert_no_projection(ROOT)

    manifest = json.loads((ROOT / "rag/memory_manifest.json").read_text(encoding="utf-8"))
    baseline = manifest["policy"]["strict_memory_schema_baseline_commit"]
    run("git", "cat-file", "-e", f"{baseline}^{{commit}}")

    state = json.loads((ROOT / "GPTINA_STATE.json").read_text(encoding="utf-8"))
    expected_prefix = [
        "rag/GPTINA_AUTO_RECOVERY_PROMPT.md as the single entrypoint",
        "rag/live/GPTINA_LIVE_CONTEXT.json",
        "last_micro_checkpoint from live buffer",
        "last_full_checkpoint from live buffer",
        "rag/END_INSTANCE_RECOVERY_CAPSULE.md",
    ]
    if state.get("restore_order", [])[: len(expected_prefix)] != expected_prefix:
        raise AssertionError("Cold-start restore order is not canonical")
    if not (ROOT / ENTRYPOINT).is_file():
        raise AssertionError(f"Cold-start entrypoint is missing: {ENTRYPOINT}")
    scope = state.get("state_scope", {})
    if scope.get("narrative_snapshot_is_current_live_state") is not False:
        raise AssertionError("Historical narrative snapshot is presented as live state")
    if scope.get("current_state_source") != "rag/live/GPTINA_LIVE_CONTEXT.json":
        raise AssertionError("Structured state does not route to the live buffer")

    live = json.loads((ROOT / "rag/live/GPTINA_LIVE_CONTEXT.json").read_text(encoding="utf-8"))
    for key in ("last_micro_checkpoint", "last_full_checkpoint"):
        target = live.get(key)
        if not target or not (ROOT / target).is_file():
            raise AssertionError(f"Cold-start live pointer is broken: {key}={target!r}")
    for relative, expected_size in state.get("verified_media", {}).items():
        target = ROOT / relative
        if not target.is_file() or target.stat().st_size != expected_size:
            raise AssertionError(f"Cold-start media pointer is broken: {relative}")

    run(sys.executable, "rag/live_context.py", "verify")
    run(sys.executable, "rag/gptina_memory.py", "verify")
    run(sys.executable, "rag/gptina_memory.py", "build")
    run(sys.executable, "rag/test_memory_recovery_runbook.py")
    run(sys.executable, "rag/test_memory_retrieval.py")

    sys.path.insert(0, str(ROOT / "rag"))
    import gptina_memory as gm  # noqa: PLC0415

    cases = json.loads(GOLD.read_text(encoding="utf-8"))["cases"]
    failures: list[str] = []
    for case in cases:
        ranked = gm.sqlite_search(
            case["query"],
            int(case.get("top_k", 8)),
            include_historical=False,
            include_superseded=bool(case.get("all_statuses", False)),
        )
        sources = [item[1]["source"] for item in ranked]
        expected = set(case.get("expected_any", []))
        forbidden = set(case.get("forbidden", []))
        if expected and not any(source in expected for source in sources):
            failures.append(f"{case['id']}: expected {sorted(expected)}, got {sources}")
        present_forbidden = [source for source in sources if source in forbidden]
        if present_forbidden:
            failures.append(f"{case['id']}: forbidden sources {present_forbidden}")
        print(f"cold-start {case['id']}: {sources[:8]}")
    if failures:
        raise AssertionError("Cold-start gold failures:\n- " + "\n- ".join(failures))

    tracked = run("git", "status", "--porcelain", cwd=ROOT, capture=True).stdout.strip()
    if tracked:
        raise AssertionError(f"Cold-start rehearsal dirtied the clone:\n{tracked}")
    print(f"OK: cold-start recovery passed from repository only ({len(cases)} focused cases).")


def outer_rehearsal() -> None:
    if run("git", "status", "--porcelain", capture=True).stdout.strip():
        raise SystemExit("Cold-start rehearsal requires a clean committed worktree")
    with tempfile.TemporaryDirectory(prefix="gptina-cold-start-") as temp:
        clone = Path(temp) / "repo"
        run(
            "git", "clone", "--quiet", "--no-local", "--depth=1",
            ROOT.resolve().as_uri(), str(clone),
        )
        assert_no_projection(clone)
        count = run("git", "rev-list", "--count", "HEAD", cwd=clone, capture=True).stdout.strip()
        if count != "1":
            raise AssertionError(f"Cold clone is not shallow: commit_count={count}")
        manifest = json.loads((clone / "rag/memory_manifest.json").read_text(encoding="utf-8"))
        baseline = manifest["policy"]["strict_memory_schema_baseline_commit"]
        absent = subprocess.run(
            ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
            cwd=clone, text=True, capture_output=True,
        )
        if absent.returncode == 0:
            raise AssertionError("Strict baseline unexpectedly exists before cold-start fetch")
        run("git", "fetch", "--quiet", "--no-tags", "--depth=1", "origin", baseline, cwd=clone)
        run(sys.executable, "rag/test_cold_start_recovery.py", "--inside-clone", cwd=clone)


def main() -> None:
    parser = argparse.ArgumentParser(description="Repository-only GPTina cold-start rehearsal")
    parser.add_argument("--inside-clone", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside_clone:
        inside_clone()
    else:
        outer_rehearsal()


if __name__ == "__main__":
    main()
