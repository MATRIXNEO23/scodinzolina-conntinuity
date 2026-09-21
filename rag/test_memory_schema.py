#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from memory_schema import (
    build_memory_resolver,
    parse_front_matter,
    validate_durable_v2,
)


VALID = """---
schema_version: 2
memory_id: gptina-2026-09-21-test
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21"
recorded_at: "2026-09-21T18:00:00+02:00"
status: current
supersedes: []
event_id: event-test
thread_ids: [memory-reliability]
entity_refs: [Alberto, GPTina]
source_refs: [conversation://current]
media_refs: []
importance: 5
confidence: verified
tags: [test]
append_only: true
---
# Test
"""


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        memories = root / "rag" / "memories" / "gptina"
        memories.mkdir(parents=True)
        first = memories / "first.md"
        first.write_text(VALID, encoding="utf-8")

        meta = parse_front_matter(VALID)
        errors = validate_durable_v2(meta, root)
        if errors:
            raise AssertionError(errors)

        malformed = VALID.replace("thread_ids: [memory-reliability]", "thread_ids: [7]")
        errors = validate_durable_v2(parse_front_matter(malformed), root)
        if not any("thread_ids[0]" in item for item in errors):
            raise AssertionError(errors)

        unsafe = VALID.replace(
            "source_refs: [conversation://current]", "source_refs: [../escape.md]"
        )
        errors = validate_durable_v2(parse_front_matter(unsafe), root)
        if not any("unsafe local reference" in item for item in errors):
            raise AssertionError(errors)

        unknown = VALID.replace("append_only: true", "append_only: true\nunexpected_field: no")
        errors = validate_durable_v2(parse_front_matter(unknown), root)
        if not any("unknown keys" in item for item in errors):
            raise AssertionError(errors)

        naive_event = VALID.replace(
            'event_at: "2026-09-21"', 'event_at: "2026-09-21T18:00:00"'
        )
        errors = validate_durable_v2(parse_front_matter(naive_event), root)
        if not any("event_at must include a timezone" in item for item in errors):
            raise AssertionError(errors)

        duplicate_key = VALID.replace("owner: gptina", "owner: gptina\nowner: tessa")
        try:
            parse_front_matter(duplicate_key)
        except ValueError as exc:
            if "duplicate YAML key" not in str(exc):
                raise
        else:
            raise AssertionError("duplicate YAML key unexpectedly accepted")

        second = memories / "second.md"
        second.write_text(VALID, encoding="utf-8")
        _resolver, _metadata, resolver_errors = build_memory_resolver(root, memories)
        if not any("duplicate memory_id" in item for item in resolver_errors):
            raise AssertionError(resolver_errors)

    print("OK: strict durable-memory schema and source-first resolver passed.")


if __name__ == "__main__":
    main()
