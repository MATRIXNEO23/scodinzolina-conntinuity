#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_CONTEXT = ROOT / "rag" / "live" / "GPTINA_LIVE_CONTEXT.json"

SAFE_STATES = {"healthy", "checkpoint_due"}
HARD_STATES = {
    "checkpoint_overdue",
    "write_unverified",
    "write_failed",
    "stale_pointer",
    "continuity_gap",
}


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def evaluate(
    live: dict,
    *,
    root: Path = ROOT,
    substantive_turns: int | None = None,
    write_status: str | None = None,
    now: datetime | None = None,
    max_active_age_minutes: int | None = None,
) -> dict:
    reasons: list[str] = []
    state = "healthy"

    last_micro = live.get("last_micro_checkpoint")
    last_full = live.get("last_full_checkpoint")

    if last_micro and not (root / str(last_micro)).is_file():
        state = "stale_pointer"
        reasons.append(f"last_micro_checkpoint missing: {last_micro}")

    if last_full and not (root / str(last_full)).is_file():
        state = "stale_pointer"
        reasons.append(f"last_full_checkpoint missing: {last_full}")

    recent = list(live.get("recent_micro_checkpoints") or [])
    if last_micro and recent and recent[-1] != last_micro:
        state = "stale_pointer"
        reasons.append("last_micro_checkpoint is not newest recent micro")

    interval = int((live.get("review_policy") or {}).get("substantive_turn_interval") or 4)
    if substantive_turns is not None and substantive_turns > interval:
        state = "checkpoint_overdue"
        reasons.append(
            f"substantive turns since last review={substantive_turns} exceeds interval={interval}"
        )

    if write_status:
        normalized = write_status.strip().casefold()
        if normalized in {"failed", "write_failed"}:
            state = "write_failed"
            reasons.append("last persistence attempt failed")
        elif normalized not in {"verified", "verified_remote", "ok"}:
            state = "write_unverified"
            reasons.append(f"last persistence status is not remotely verified: {write_status}")

    if max_active_age_minutes is not None:
        updated_at = _parse_time(str(live.get("updated_at") or ""))
        if updated_at is None:
            state = "continuity_gap"
            reasons.append("live updated_at is missing or invalid")
        else:
            current = now or datetime.now().astimezone()
            age_minutes = (current - updated_at).total_seconds() / 60.0
            if age_minutes > max_active_age_minutes:
                state = "checkpoint_overdue"
                reasons.append(
                    f"active-session live age={age_minutes:.1f}m exceeds {max_active_age_minutes}m"
                )

    if state == "healthy" and bool(live.get("checkpoint_due")):
        state = "checkpoint_due"
        reasons.append("full checkpoint consolidation is due")

    return {
        "state": state,
        "safe": state in SAFE_STATES,
        "hard_warning": state in HARD_STATES,
        "last_micro_checkpoint": last_micro,
        "last_full_checkpoint": last_full,
        "updated_at": live.get("updated_at"),
        "checkpoint_due": bool(live.get("checkpoint_due")),
        "substantive_turn_interval": interval,
        "reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="GPTina continuity watchdog")
    parser.add_argument("--substantive-turns", type=int)
    parser.add_argument(
        "--write-status",
        help="verified_remote, unverified, failed, or equivalent runtime status",
    )
    parser.add_argument(
        "--max-active-age-minutes",
        type=int,
        help="Use only for an explicitly active session; never as an idle-repository CI timeout",
    )
    parser.add_argument(
        "--fail-on-due",
        action="store_true",
        help="Also return non-zero when a full checkpoint consolidation is due",
    )
    args = parser.parse_args()

    if not LIVE_CONTEXT.is_file():
        raise SystemExit("CONTINUITY NOT SAFE: missing live context")

    try:
        live = json.loads(LIVE_CONTEXT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"CONTINUITY NOT SAFE: invalid live context: {exc}")

    result = evaluate(
        live,
        substantive_turns=args.substantive_turns,
        write_status=args.write_status,
        max_active_age_minutes=args.max_active_age_minutes,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["hard_warning"] or (args.fail_on_due and result["state"] == "checkpoint_due"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
