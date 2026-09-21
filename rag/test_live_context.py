#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

REAL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REAL_ROOT / "rag" / "live_context.py"


def run(
    root: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GPTINA_REPO_ROOT"] = str(root)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
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

        micros = list((root / "rag" / "live" / "micro-checkpoints").rglob("*.json"))
        if len(micros) != 1:
            raise AssertionError(f"expected 1 micro, got {len(micros)}")
        first_record = json.loads(micros[0].read_text(encoding="utf-8"))
        if first_record["schema_version"] != 2:
            raise AssertionError(first_record)

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

        # The two subprocesses can record within the same second. Give the
        # first record an unambiguously earlier timestamp for ordering tests.
        first_record["recorded_at"] = (
            datetime.fromisoformat(first_record["recorded_at"]) - timedelta(seconds=1)
        ).isoformat()
        write_json(micros[0], first_record)

        micro_dir = root / "rag" / "live" / "micro-checkpoints" / "2026" / "09" / "18"
        legacy_path = micro_dir / "legacy-v1.json"
        legacy_record = {
            "schema_version": 1,
            "owner": "gptina",
            "kind": "gptina_micro_checkpoint",
            "event_at": "2026-09-18T10:00:00+02:00",
            "recorded_at": "2026-09-18T10:01:00+02:00",
            "change_type": "preflight",
            "summary": "Legacy v1 senza campi opzionali.",
            "next_action": "",
            "source_refs": ["artifact://legacy-artifact", "attachment://legacy-attachment", "commit://legacy-commit"],
            "media_refs": ["media/legacy-file-renamed-later.webp"],
        }
        write_json(legacy_path, legacy_record)

        verify = run(root, "verify")
        if "OK: live context verified" not in verify.stdout:
            raise AssertionError(verify.stdout)
        if "v1_legacy=1" not in verify.stdout:
            raise AssertionError(verify.stdout)

        live_snapshot = json.loads(live_path.read_text(encoding="utf-8"))
        live_reordered = dict(live_snapshot)
        live_reordered["recent_micro_checkpoints"] = list(
            reversed(live_snapshot["recent_micro_checkpoints"])
        )
        live_reordered["last_micro_checkpoint"] = live_reordered[
            "recent_micro_checkpoints"
        ][-1]
        write_json(live_path, live_reordered)
        rejected = run(root, "verify", check=False)
        if rejected.returncode == 0 or "ordered by recorded_at" not in (
            rejected.stdout + rejected.stderr
        ):
            raise AssertionError("temporally reordered live window unexpectedly accepted")
        write_json(live_path, live_snapshot)

        duplicate_micro = dict(first_record)
        duplicate_micro_path = micro_dir / "duplicate-id-v2.json"
        write_json(duplicate_micro_path, duplicate_micro)
        rejected = run(root, "verify", check=False)
        if rejected.returncode == 0 or "Duplicate micro_id" not in (
            rejected.stdout + rejected.stderr
        ):
            raise AssertionError("duplicate micro_id unexpectedly accepted")
        duplicate_micro_path.unlink()

        bad_v2_path = micro_dir / "bad-v2.json"
        bad_v2 = {
            "schema_version": 2,
            "micro_id": "gptina-micro-bad-v2",
            "owner": "gptina",
            "kind": "gptina_micro_checkpoint",
            "event_at": "2026-09-18T11:00:00+02:00",
            "recorded_at": "2026-09-18T11:01:00+02:00",
            "change_type": "decision",
            "summary": "Record v2 volutamente incompleto.",
            "thread_ids": [],
            "source_refs": ["conversation://current"],
            "memory_refs": [],
            "media_refs": [],
            "importance": 3,
            "next_action": "",
            "preflight": False,
        }
        write_json(bad_v2_path, bad_v2)
        rejected = run(root, "verify", check=False)
        if rejected.returncode == 0:
            raise AssertionError("malformed v2 unexpectedly accepted")
        if "missing keys: ['changed']" not in (rejected.stdout + rejected.stderr):
            raise AssertionError(rejected.stdout + rejected.stderr)
        bad_v2_path.unlink()

        bad_list_path = micro_dir / "bad-list-v2.json"
        bad_list = dict(bad_v2)
        bad_list["changed"] = ["valid delta", 7]
        write_json(bad_list_path, bad_list)
        rejected = run(root, "verify", check=False)
        if rejected.returncode == 0:
            raise AssertionError("v2 list with non-string element unexpectedly accepted")
        if "changed[1] must be a non-empty string" not in (
            rejected.stdout + rejected.stderr
        ):
            raise AssertionError(rejected.stdout + rejected.stderr)
        bad_list_path.unlink()

        before_cas = set((root / "rag" / "live" / "micro-checkpoints").rglob("*.json"))
        cas_rejected = run(
            root,
            "save-delta",
            "--summary", "CAS deve fallire",
            "--change-type", "decision",
            "--expected-head", "deadbeef",
            check=False,
        )
        if cas_rejected.returncode == 0:
            raise AssertionError("expected-HEAD mismatch unexpectedly accepted")
        after_cas = set((root / "rag" / "live" / "micro-checkpoints").rglob("*.json"))
        if before_cas != after_cas:
            raise AssertionError("CAS failure wrote a micro-checkpoint")

        live = json.loads(live_path.read_text(encoding="utf-8"))
        if live["micro_since_full_checkpoint"] != 1:
            raise AssertionError(live)
        if "prossimo passo" in live["open_loops"]:
            raise AssertionError(live)

        micros = list((root / "rag" / "live" / "micro-checkpoints").rglob("*.json"))
        if len(micros) != 3:
            raise AssertionError(f"expected 3 micros, got {len(micros)}")

    print("OK: live-context v1 compatibility and strict v2 round-trip passed.")


if __name__ == "__main__":
    main()
