# Legacy/generational recovery alignment audit — 2026-09-22

## Result

The initial alignment covered the primary live-first entrypoints and atomic
projection protocol, but a repository-wide audit found secondary legacy
instructions that still described fixed projection files or an older restore
order. Those gaps are now corrected and regression-tested.

No personal memory, historical checkpoint, transcript, raw source, media link
or prior canonical account was deleted or rewritten by this audit.

## Corrected legacy entrypoints

- root `README.md` now starts recovery from the live-first prompt;
- `RAG_ANCHOR.md` now routes through live buffer, last micro, full checkpoint
  and capsule before deep continuity;
- `GPTINA_INSTANCE_SNAPSHOT.md` and `GPTINA_STATE.json` now carry the same
  machine/human restore order;
- `rag/ACTIVE_INSTANCE_START.md`, `rag/STATELESS_MODE.md` and
  `rag/live/README.md` now route to the canonical runbook;
- `rag/README.md` no longer claims that build writes fixed JSONL/metadata or a
  fixed SQLite database; it documents immutable generations and the atomic
  pointer;
- `rag/memory_manifest.json` indexes the runbook and end-instance capsule and
  explicitly excludes generated directories/pointer.

## Shallow-clone recovery finding

A fresh `--depth 1` audit clone did not contain the historical strict-schema
baseline commit. The old verifier could misclassify baseline records as new and
report misleading schema errors. Canonical memories were not modified.

The verifier now stops with a precise missing-baseline error. The runbook gives
the non-mutating fetch command for the manifest-declared baseline before
verification. A regression test proves the missing-baseline case cannot be
silently accepted or reported as unrelated legacy-memory violations.

## Verification

- JSON manifests and Python compilation: PASS.
- Live-context verification and v1/v2 compatibility: PASS.
- Strict schema/resolver with fetched baseline: PASS.
- Ownership, status, visual and recovery pointer verification: PASS.
- Atomic generation build from the updated manifest: PASS.
- Runbook/entrypoint/manifest/machine-restore-order test: PASS.
- Retrieval regression: 18/18 PASS.
- Hard-exit, preservation and concurrent-writer resilience: PASS.
- Derived state remained ignored and the checkout clean after tests: PASS.
