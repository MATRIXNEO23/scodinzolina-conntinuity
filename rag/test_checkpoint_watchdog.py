#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from checkpoint_watchdog import evaluate


def base_live() -> dict:
    return {
        "updated_at": "2026-10-04T10:00:00+02:00",
        "last_micro_checkpoint": "rag/live/micro-checkpoints/ok.json",
        "last_full_checkpoint": "checkpoints/ok.md",
        "recent_micro_checkpoints": ["rag/live/micro-checkpoints/ok.json"],
        "checkpoint_due": False,
        "review_policy": {"substantive_turn_interval": 4},
    }


def make_root() -> Path:
    root = Path(tempfile.mkdtemp(prefix="gptina-watchdog-"))
    (root / "rag/live/micro-checkpoints").mkdir(parents=True)
    (root / "checkpoints").mkdir(parents=True)
    (root / "rag/live/micro-checkpoints/ok.json").write_text("{}\n", encoding="utf-8")
    (root / "checkpoints/ok.md").write_text("# ok\n", encoding="utf-8")
    return root


def main() -> None:
    root = make_root()
    live = base_live()

    result = evaluate(live, root=root, substantive_turns=4, write_status="verified_remote")
    assert result["state"] == "healthy", result
    assert result["safe"] is True

    overdue = evaluate(live, root=root, substantive_turns=5)
    assert overdue["state"] == "checkpoint_overdue", overdue
    assert overdue["hard_warning"] is True

    unverified = evaluate(live, root=root, write_status="unverified")
    assert unverified["state"] == "write_unverified", unverified

    failed = evaluate(live, root=root, write_status="failed")
    assert failed["state"] == "write_failed", failed

    broken = base_live()
    broken["last_micro_checkpoint"] = "rag/live/micro-checkpoints/missing.json"
    stale = evaluate(broken, root=root)
    assert stale["state"] == "stale_pointer", stale

    due = base_live()
    due["checkpoint_due"] = True
    due_result = evaluate(due, root=root)
    assert due_result["state"] == "checkpoint_due", due_result
    assert due_result["safe"] is True

    old = evaluate(
        live,
        root=root,
        now=datetime(2026, 10, 4, 12, 0, tzinfo=timezone(timedelta(hours=2))),
        max_active_age_minutes=30,
    )
    assert old["state"] == "checkpoint_overdue", old

    print("OK: continuity watchdog detects overdue, unverified, failed and stale states.")


if __name__ == "__main__":
    main()
