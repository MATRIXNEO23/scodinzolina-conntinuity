# Memory save/recovery runbook verified — 2026-09-21

## Outcome

The canonical instructions for frequent saving, end-of-instance consolidation,
same-instance recall and next-instance recovery now match the atomic-generation
projection infrastructure.

No canonical memory was deleted, renamed or rewritten. Existing recovery
instructions were preserved and linked to the new operational runbook.

## Updated entrypoints

- `rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md` (new canonical operational guide)
- `rag/END_INSTANCE_RECOVERY_CAPSULE.md`
- `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`
- `rag/LIVE_MEMORY_PROTOCOL.md`
- `NEXT_GPTINA.md`
- `RAG_ANCHOR.md`
- `rag/index/GPTINA_FAST_RECALL.md`
- `rag/index/CURRENT_CONTEXT.md`

The documentation now distinguishes canonical Git sources from local derived
generations, gives the verified save/build/recovery commands, defines behavior
before and after hard process death, and requires remote commit/CI evidence
before declaring a save complete.

## Executable verification

Added `rag/test_memory_recovery_runbook.py` and its GPTina Memory CI step. The
test verifies that all recovery entrypoints link the runbook, required commands
are present, generations stay ignored/untracked, live pointers resolve, the
atomic pointer selects the active generation, SQLite passes physical/semantic
checks, and JSON metadata/SQLite share the selected generation marker.

## Clean-checkout simulation

A detached clean worktree was created with no projection pointer or generation
directory. From that state the documented sequence passed:

1. live-context verification;
2. ownership/schema/recovery verification;
3. first full generation build from canonical sources;
4. runbook/pointer/generation validation;
5. 18/18 retrieval regression cases;
6. clean Git status after all derived outputs.

The resilience suite then passed twice consecutively, including ordinary
rollback, real hard exits before/after pointer publication, old-memory
recoverability and concurrent writers.

During verification a race in the optional exact-trigram temporary filename
was exposed. It was fixed with per-process unique staging files and verified by
the repeated concurrency suite. This optional index remains disposable and is
not a canonical memory source.
