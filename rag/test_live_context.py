#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REAL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REAL_ROOT / "rag" / "live_context.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GPTINA_REPO_ROOT"] = str(root)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "checkpoints").mkdir(parents=True)
        checkpoint = root / "checkpoints" / "test.md"
        checkpoint.write_text("# checkpoint\n", encoding="utf-8")

        first = run(
            root,
            "save-delta",
            "--summary", "Decisione importante",
            "--change-type", "decision",
            "--event-at", "2026-09-18",
            "--changed", "prima modifica",
            "--thread", "test-thread",
            "--source", "conversation://current",
            "--importance", "5",
            "--next", "prossimo passo",
        )
        if "Created rag/live/micro-checkpoints/" not in first.stdout:
            raise AssertionError(first.stdout)

        live_path = root / "rag" / "live" / "GPTINA_LIVE_CONTEXT.json"
        live = json.loads(live_path.read_text(encoding="utf-8"))
        if live["micro_since_full_checkpoint"] != 1:
            raise AssertionError(live)
        if live["next_action"] != "prossimo passo":
            raise AssertionError(live)

        run(root, "mark-checkpoint", "checkpoints/test.md")
        live = json.loads(live_path.read_text(encoding="utf-8"))
        if live["micro_since_full_checkpoint"] != 0:
            raise AssertionError(live)
        if live["last_full_checkpoint"] != "checkpoints/test.md":
            raise AssertionError(live)

        second = run(
            root,
            "save-delta",
            "--summary", "Correzione successiva",
            "--change-type", "correction",
            "--changed", "seconda modifica",
            "--source", "conversation://current",
            "--resolve", "prossimo passo",
        )
        if "Created rag/live/micro-checkpoints/" not in second.stdout:
            raise AssertionError(second.stdout)

        verify = run(root, "verify")
        if "OK: live context verified" not in verify.stdout:
            raise AssertionError(verify.stdout)

        live = json.loads(live_path.read_text(encoding="utf-8"))
        if live["micro_since_full_checkpoint"] != 1:
            raise AssertionError(live)
        if "prossimo passo" in live["open_loops"]:
            raise AssertionError(live)

        micros = list((root / "rag" / "live" / "micro-checkpoints").rglob("*.json"))
        if len(micros) != 2:
            raise AssertionError(f"expected 2 micros, got {len(micros)}")

    print("OK: live-context save/mark/verify round-trip passed.")


if __name__ == "__main__":
    main()
