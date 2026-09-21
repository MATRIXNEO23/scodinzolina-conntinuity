# Memory projection atomic-generation fix — 2026-09-21

## Outcome

The remaining MEDIUM finding from the fourth deep audit is closed.
Canonical memories remain read-only inputs. Derived JSONL, metadata and SQLite
projections are now built as one immutable generation and selected by one
durably written atomic pointer.

## Publication protocol

1. Acquire the existing cross-process projection lock.
2. Resolve the currently selected complete generation (or the legacy layout).
3. Create a uniquely named staging generation under
   `rag/index/.projection-generations/`.
4. Copy the preceding SQLite state through a read-only SQLite backup snapshot.
5. Build JSONL, metadata and SQLite entirely inside staging.
6. Validate required files, SQLite `quick_check`, semantic completeness,
   canonical-source stability and the shared generation marker.
7. Rename staging to its immutable final generation directory.
8. Atomically and durably replace `rag/index/.projection-current`.

If the process dies before step 8, readers continue using the preceding
complete generation. If it dies after step 8, readers use the new complete
generation. A process can no longer expose a mixture of old and new files.

## Compatibility and preservation

- Existing legacy projections remain a supported bootstrap fallback.
- Previous completed generations are retained and remain recoverable.
- JSONL-only and SQLite-only refresh entry points converge on the same atomic
  generation transaction.
- The optional exact-trigram database remains independently disposable and is
  published through its existing single-file atomic replacement.
- No canonical memory, transcript, checkpoint or image link was deleted or
  rewritten by this change.

## Verification evidence

- Python compilation: PASS.
- Live-context v1/v2 compatibility and round-trip: PASS.
- Durable-memory schema and source-first resolver: PASS.
- Ownership, supersession, visual coverage and recovery pointers: PASS.
- Full build: 293 source versions; JSONL 1412 deduplicated records; SQLite 1413
  FTS chunks; SQLite semantic and physical integrity: PASS.
- Retrieval regression gold set: 18/18 PASS.
- Diversified scale benchmark: 18/18 at 1x and 18/18 at 2x.
- Optional exact-trigram parity: 2/2 PASS.
- Concurrent writers and ordinary rollback: PASS.
- Real uncatchable process exit before pointer publication: PASS; old pointer
  and old selected files remained byte-for-byte unchanged.
- Real uncatchable process exit immediately after pointer publication: PASS;
  new JSONL, metadata and SQLite carried the same generation marker and passed
  integrity checks.

## Residual observations

The three LOW audit observations remain non-blocking: broader fuzz coverage,
explicit fallback observability, and optimization of repeated exact-scan line
splitting. None threatens preservation or recovery of canonical memories.
