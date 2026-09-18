#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(
    os.environ.get("GPTINA_REPO_ROOT", str(Path(__file__).resolve().parents[1]))
).resolve()
RAG = ROOT / "rag"
LIVE = RAG / "live"
MICRO = LIVE / "micro-checkpoints"
LIVE_CONTEXT = LIVE / "GPTINA_LIVE_CONTEXT.json"

ALLOWED_CHANGE_TYPES = {
    "correction", "decision", "rule", "project_state", "relational_shift",
    "open_loop", "preflight", "milestone", "visual_context",
}
ALLOWED_EXTERNAL_PREFIXES = ("conversation://", "github://", "external://")
MICRO_REQUIRED = {
    "schema_version", "micro_id", "owner", "kind", "event_at", "recorded_at",
    "change_type", "summary", "changed", "thread_ids", "source_refs",
    "memory_refs", "media_refs", "importance", "next_action", "preflight",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_slug(text: str) -> str:
    text = text.casefold().strip()
    text = re.sub(r"[^0-9a-zà-öø-ÿ_-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:64] or "delta").strip("-")


def load_live() -> dict:
    if not LIVE_CONTEXT.is_file():
        return {
            "schema_version": 1,
            "owner": "gptina",
            "kind": "gptina_live_context",
            "updated_at": now_iso(),
            "latest_summary": "",
            "next_action": "",
            "last_micro_checkpoint": None,
            "last_full_checkpoint": None,
            "active_threads": [],
            "open_loops": [],
            "recent_micro_checkpoints": [],
            "micro_since_full_checkpoint": 0,
            "review_policy": {
                "substantive_turn_interval": 4,
                "immediate_triggers": sorted(ALLOWED_CHANGE_TYPES - {"preflight"}),
                "preflight_before_long_or_risky_work": True,
            },
            "note": (
                "Projection only. Append-only truth lives in "
                "micro-checkpoints/checkpoints/memories/sources."
            ),
        }
    try:
        return json.loads(LIVE_CONTEXT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid live context JSON: {exc}")


def ref_exists(ref: str) -> bool:
    if ref.startswith(ALLOWED_EXTERNAL_PREFIXES):
        return True
    return (ROOT / ref).exists()


def validate_micro(record: dict, path: Path | None = None) -> list[str]:
    errors: list[str] = []
    missing = sorted(MICRO_REQUIRED - set(record))
    if missing:
        errors.append(f"missing keys: {missing}")
    if record.get("owner") != "gptina":
        errors.append("owner must be gptina")
    if record.get("kind") != "gptina_micro_checkpoint":
        errors.append("kind must be gptina_micro_checkpoint")
    if record.get("change_type") not in ALLOWED_CHANGE_TYPES:
        errors.append(f"invalid change_type={record.get('change_type')}")
    importance = record.get("importance")
    if not isinstance(importance, int) or not 1 <= importance <= 5:
        errors.append("importance must be integer 1..5")
    if not str(record.get("summary") or "").strip():
        errors.append("summary is empty")
    if not isinstance(record.get("changed"), list):
        errors.append("changed must be a list")
    for key in ("thread_ids", "source_refs", "memory_refs", "media_refs"):
        if not isinstance(record.get(key), list):
            errors.append(f"{key} must be a list")
    for key in ("source_refs", "memory_refs", "media_refs"):
        for ref in record.get(key, []):
            if not ref_exists(str(ref)):
                errors.append(f"{key} missing ref: {ref}")
    if path and not path.as_posix().endswith(".json"):
        errors.append("micro-checkpoint path must end in .json")
    return errors


def save_delta(args: argparse.Namespace) -> Path:
    if args.change_type not in ALLOWED_CHANGE_TYPES:
        fail(f"Unsupported change type: {args.change_type}")

    recorded_at = now_iso()
    event_at = args.event_at or recorded_at
    dt = datetime.fromisoformat(recorded_at)
    stamp = dt.strftime("%Y-%m-%dT%H%M%S%z")
    slug = safe_slug(args.summary)
    token = uuid.uuid4().hex[:8]
    target = (
        MICRO / f"{dt:%Y}" / f"{dt:%m}" / f"{dt:%d}"
        / f"{stamp}--{slug}--{token}.json"
    )

    sources = args.source or ["conversation://current"]
    record = {
        "schema_version": 1,
        "micro_id": f"gptina-micro-{stamp}-{token}",
        "owner": "gptina",
        "kind": "gptina_micro_checkpoint",
        "event_at": event_at,
        "recorded_at": recorded_at,
        "change_type": args.change_type,
        "summary": args.summary.strip(),
        "changed": args.changed or [],
        "thread_ids": args.thread or [],
        "source_refs": sources,
        "memory_refs": args.memory or [],
        "media_refs": args.media or [],
        "importance": args.importance,
        "next_action": (args.next_action or "").strip(),
        "preflight": bool(args.preflight or args.change_type == "preflight"),
    }

    errors = validate_micro(record, target)
    if errors:
        fail("Invalid micro-checkpoint:\n- " + "\n- ".join(errors))

    atomic_write(target, json.dumps(record, ensure_ascii=False, indent=2) + "\n")

    live = load_live()
    recent = list(live.get("recent_micro_checkpoints") or [])
    recent.append(rel(target))
    recent = recent[-12:]

    threads = list(live.get("active_threads") or [])
    for thread in record["thread_ids"]:
        if thread not in threads:
            threads.append(thread)

    loops = list(live.get("open_loops") or [])
    for resolved in args.resolve or []:
        loops = [item for item in loops if item != resolved]
    if record["next_action"] and record["next_action"] not in loops:
        loops.append(record["next_action"])

    live.update(
        {
            "schema_version": 1,
            "owner": "gptina",
            "kind": "gptina_live_context",
            "updated_at": recorded_at,
            "latest_summary": record["summary"],
            "next_action": record["next_action"],
            "last_micro_checkpoint": rel(target),
            "active_threads": threads,
            "open_loops": loops,
            "recent_micro_checkpoints": recent,
            "micro_since_full_checkpoint": int(
                live.get("micro_since_full_checkpoint") or 0
            ) + 1,
        }
    )
    live.setdefault(
        "review_policy",
        {
            "substantive_turn_interval": 4,
            "immediate_triggers": sorted(ALLOWED_CHANGE_TYPES - {"preflight"}),
            "preflight_before_long_or_risky_work": True,
        },
    )
    live.setdefault(
        "note",
        "Projection only. Append-only truth lives in "
        "micro-checkpoints/checkpoints/memories/sources.",
    )
    atomic_write(LIVE_CONTEXT, json.dumps(live, ensure_ascii=False, indent=2) + "\n")
    return target


def mark_checkpoint(path_text: str) -> None:
    path = (ROOT / path_text).resolve()
    checkpoints = (ROOT / "checkpoints").resolve()
    if checkpoints not in path.parents or not path.is_file():
        fail(f"Checkpoint must exist under checkpoints/: {path_text}")
    live = load_live()
    live["updated_at"] = now_iso()
    live["last_full_checkpoint"] = rel(path)
    live["micro_since_full_checkpoint"] = 0
    atomic_write(LIVE_CONTEXT, json.dumps(live, ensure_ascii=False, indent=2) + "\n")


def verify_live_context() -> None:
    if not LIVE_CONTEXT.is_file():
        fail("Missing rag/live/GPTINA_LIVE_CONTEXT.json")
    live = load_live()

    for key in (
        "schema_version", "owner", "kind", "updated_at", "latest_summary",
        "next_action", "last_micro_checkpoint", "last_full_checkpoint",
        "active_threads", "open_loops", "recent_micro_checkpoints",
        "micro_since_full_checkpoint", "review_policy",
    ):
        if key not in live:
            fail(f"Live context missing key: {key}")

    if live.get("owner") != "gptina":
        fail("Live context owner must be gptina")
    if live.get("kind") != "gptina_live_context":
        fail("Live context kind must be gptina_live_context")

    recent = list(live.get("recent_micro_checkpoints") or [])
    if len(recent) > 12:
        fail("Live context recent_micro_checkpoints must contain at most 12 items")
    if len(recent) != len(set(recent)):
        fail("Live context recent_micro_checkpoints contains duplicates")

    last_micro = live.get("last_micro_checkpoint")
    if last_micro:
        if not recent or recent[-1] != last_micro:
            fail("last_micro_checkpoint must be the newest recent_micro_checkpoints item")
        if not (ROOT / last_micro).is_file():
            fail(f"last_micro_checkpoint missing: {last_micro}")

    last_full = live.get("last_full_checkpoint")
    if last_full and not (ROOT / last_full).is_file():
        fail(f"last_full_checkpoint missing: {last_full}")

    count = 0
    for path in sorted(MICRO.rglob("*.json")) if MICRO.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"Invalid micro-checkpoint JSON {rel(path)}: {exc}")
        errors = validate_micro(record, path)
        if errors:
            fail(f"Invalid {rel(path)}:\n- " + "\n- ".join(errors))
        count += 1

    for path_text in recent:
        if not (ROOT / path_text).is_file():
            fail(f"Recent micro-checkpoint missing: {path_text}")

    policy = live.get("review_policy") or {}
    interval = policy.get("substantive_turn_interval")
    if not isinstance(interval, int) or not 3 <= interval <= 5:
        fail("review_policy.substantive_turn_interval must be between 3 and 5")

    print(
        "OK: live context verified "
        f"(micro-checkpoints={count}, recent={len(recent)}, "
        f"since_full={live.get('micro_since_full_checkpoint')})."
    )


def print_status() -> None:
    print(json.dumps(load_live(), ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="GPTina frequent live-context saver")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("save-delta", help="Append a micro-checkpoint and refresh live context")
    sp.add_argument("--summary", required=True)
    sp.add_argument("--change-type", choices=sorted(ALLOWED_CHANGE_TYPES), required=True)
    sp.add_argument("--event-at")
    sp.add_argument("--changed", action="append", default=[])
    sp.add_argument("--thread", action="append", default=[])
    sp.add_argument("--source", action="append", default=[])
    sp.add_argument("--memory", action="append", default=[])
    sp.add_argument("--media", action="append", default=[])
    sp.add_argument("--importance", type=int, choices=range(1, 6), default=3)
    sp.add_argument("--next", dest="next_action", default="")
    sp.add_argument("--resolve", action="append", default=[])
    sp.add_argument("--preflight", action="store_true")

    mp = sub.add_parser("mark-checkpoint", help="Point live context to a full checkpoint")
    mp.add_argument("path")

    sub.add_parser("status", help="Show current live context")
    sub.add_parser("verify", help="Verify live buffer and all micro-checkpoints")

    args = ap.parse_args()
    if args.cmd == "save-delta":
        target = save_delta(args)
        print(f"Created {rel(target)}")
    elif args.cmd == "mark-checkpoint":
        mark_checkpoint(args.path)
        print(f"Marked full checkpoint: {args.path}")
    elif args.cmd == "status":
        print_status()
    elif args.cmd == "verify":
        verify_live_context()


if __name__ == "__main__":
    main()
