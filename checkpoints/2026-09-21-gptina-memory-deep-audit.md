# GPTina memory — deep independent audit

Date: 2026-09-21T19:11:00+02:00

Audited HEAD: `5842c3b0fdef6122d1625ae2cf01f758860e57b2`

Mode: evidence-only audit. No runtime fix is included in this checkpoint.

## Executive result

The canonical sources are intact, ownership boundaries pass, the current gold
set is 14/14, live-context verification passes and both exact backends agree on
the covered cases. No `CRITICAL` finding was found.

The system is reliable for the current single-writer, controlled-publish
workflow, but it is not yet fully crash/self-recovery safe or multi-writer safe.
Five `HIGH` findings should be repaired before copying the infrastructure to
Tessa and Ettore.

Overall technical score: **7.8/10**.

| Area | Score | Summary |
|---|---:|---|
| Canonical/source-first integrity | 9.2 | Git truth and derived-index boundary are clear |
| Ownership and path safety | 9.0 | GPTina/Tessa isolation and ref confinement pass |
| Schema and identity | 8.2 | Durable IDs strong; micro ID uniqueness missing |
| Retrieval correctness | 8.5 | Gold 14/14; current/supersession gap remains |
| Snapshot determinism | 7.0 | Clean mode strong; dirty in-process cache can go stale |
| Crash recovery | 6.3 | Corrupt main SQLite does not self-rebuild |
| Concurrency | 5.8 | Projection builders do not use the writer lock |
| CI coverage | 7.0 | Test depth good; trigger paths omit canonical inputs |
| Scale readiness | 8.8 | 100x quality stable; optional trigram is well isolated |

## Findings

### HIGH-01 — projection builds are not single-writer safe

`gptina_memory.py build` and `build-exact` do not acquire the cooperative writer
lock used by `live_context.py`. They also share fixed temporary names.

Reproduction on an isolated worktree:

- two concurrent main builds returned exit codes `0,1`;
- the failing process raised `FileNotFoundError` while replacing
  `memory_chunks.jsonl.tmp`;
- two concurrent exact builds returned `1,0`;
- the failing process raised `sqlite3.OperationalError: table exact_meta already exists`.

Risk: intermittent CI/local failures and possible projection state assembled by
different writers. Canonical sources are not damaged, but availability and
snapshot claims are weakened.

Required fix: one repository-scoped writer lock shared by live writer, JSONL,
main SQLite and exact SQLite; unique temp paths; expected-HEAD check before and
after collection and before publication.

### HIGH-02 — corrupt main SQLite does not self-recover

After corrupting only the disposable main database header, `stats` detected
staleness but attempted to reopen the same database. It terminated with:

`sqlite3.DatabaseError: file is not a database`.

The documented philosophy says projections are disposable and reconstructible,
but the runtime requires manual deletion in this case.

Required fix: catch database-open/integrity failures, quarantine the exact
derived files, rebuild into a temporary database, run `quick_check`, then swap
atomically. Never touch canonical sources during recovery.

### HIGH-03 — two supersession targets remain current

The owner-scoped supersession graph resolves and is acyclic, but status is not
derived from incoming `supersedes` edges. Two targets are still indexed as
`current`:

- `gptina-2026-09-21-immagine-48-trieste-origini-simboliche`;
- `gptina-2026-09-21-ettore-romanziere-nome-scelto`.

Only the face-reference correction has a matching manifest status override.

Risk: an older interpretation may be retrieved as current even though a newer
record explicitly supersedes it.

Required fix: verify bidirectional supersession integrity. Either require a
matching status override or derive effective status from the source-first graph.
Preserve both historical records.

### HIGH-04 — dirty-preview freshness can be stale in a long-lived process

`_DIRTY_PREVIEW_FINGERPRINT` is process-cached. Reproduction:

1. edit a source;
2. sync with explicit dirty-preview;
3. edit the source again in the same Python process;
4. `sqlite_index_is_fresh(..., allow_dirty_preview=True)` still returns `True`.

Risk: a long-lived consumer can serve the previous dirty preview after a second
worktree edit.

Required fix: remove the cache from freshness checks, key it to a workspace
generation/stat signature, or invalidate it on every query boundary. Canonical
clean-HEAD mode is not affected.

### HIGH-05 — CI path filters omit canonical memory inputs

The workflow triggers for `rag/**`, `checkpoints/**`, `media/**`, `.gitignore`
and its own workflow file. The manifest also indexes canonical inputs outside
those paths, including:

- `CONTINUITY.md`, `CHRONICLE.md`, `LIVE_THREAD.md`;
- `NEXT_GPTINA.md`, `GPTINA_STATE.json`, snapshots and reflections;
- `raw_sessions/**`, `instance_snapshots/**`;
- `requirements-memory.txt` affects the verifier runtime.

Commits changing only these paths can bypass Memory CI.

Required fix: align workflow path filters with every manifest source family and
runtime dependency, or run the memory gate on every push to `main`.

### MEDIUM-01 — live pointer “newest” is positional, not temporal

The verifier checks only that `last_micro_checkpoint` equals the last entry in
`recent_micro_checkpoints`. Reordering the list to end with an older existing
record still produced verifier PASS.

Fix: compare parsed `recorded_at` plus a deterministic tie-break and verify the
pointer against all current micro-checkpoints or an explicit publication order.

### MEDIUM-02 — duplicate `micro_id` values are accepted

Copying a valid v2 micro-checkpoint to a second path without changing
`micro_id` increased the verified count and still passed. Durable `memory_id`
duplicates are correctly rejected; micro IDs are not checked globally.

Fix: enforce v2 `micro_id` uniqueness during full verification.

### MEDIUM-03 — main SQLite lacks integrity and completion markers

The main database has transactions, WAL and metadata but no `quick_check`,
`integrity_check`, `build_complete` marker, schema migration gate or atomic
full-rebuild swap. There is no `busy_timeout`.

Fix: add explicit schema/build state, integrity checks and temporary-DB swap.

### MEDIUM-04 — exact trigram build has a HEAD race

The builder checks dirty state at entry, collects sources and writes the HEAD
only near completion. A checkout/HEAD movement during the build is not guarded
by expected-HEAD CAS. The same class of race exists in main index sync.

Fix: capture expected HEAD before collection and require it unchanged before
publishing the projection.

### MEDIUM-05 — semantic time and schema relations remain permissive

Typed parsing validates individual ISO values but not `event_at` versus
`recorded_at` or declared time versus commit evidence. Unknown front-matter
properties are accepted. This is not current corruption, but ambiguity can
enter future records.

Fix: introduce warnings first for impossible ordering/divergence and define an
explicit additional-properties policy before promoting gates to errors.

### MEDIUM-06 — gold coverage is strong but narrow

The 14 cases cover current state, ownership, visual, temporal and two exact
lookups. They do not yet adequately cover unanswered queries, ambiguity,
contradictions, code-switch IT/EN/ES, Unicode punctuation, stale projections,
corruption or concurrent writers.

Fix: add stratified regression and fault-injection suites without adjusting
expected results merely to pass current ranking.

### LOW-01 — exact scan repeats line splitting per hit

`content.splitlines()` is recalculated for every occurrence. It is harmless at
current scale but avoidable if exact scan becomes hot.

### LOW-02 — projection observability is split

Main stats do not report exact-index presence, freshness, byte size or last
build identity. Operational diagnosis requires separate commands.

### LOW-03 — recovery journal is absent

The live writer deliberately allows an orphan append-only micro-checkpoint if a
crash occurs between micro and live-pointer writes. This is safe for pointer
integrity, but there is no journal or audit command to identify and reconcile
orphans automatically.

## Verified strengths

- Git remains the only canonical publication boundary.
- Tessa-owned memory is excluded from GPTina retrieval.
- local refs reject absolute paths, `..` and symlink escapes;
- YAML duplicate keys and typed list violations are rejected for new records;
- stable durable `memory_id` resolver rejects duplicates and wrong owners;
- supersession targets and cycles are checked;
- clean versus dirty-preview mode is explicit;
- default exact scan reads canonical sources directly;
- trigram is optional, derived, stale-aware and ignored by Git;
- scale benchmarks retain 14/14 through diversified 100x;
- current CI and local full suite pass on the audited HEAD.

## Repair order

1. **P0 integrity:** HIGH-03 supersession status and HIGH-04 dirty cache.
2. **P0 recovery:** HIGH-02 corrupt-DB quarantine/rebuild.
3. **P0 coordination:** HIGH-01 shared lock and expected-HEAD CAS.
4. **P0 prevention:** HIGH-05 CI trigger coverage.
5. **P1 identity/recovery:** duplicate micro IDs, chronological live pointer,
   integrity markers and exact/main build CAS.
6. **P2 quality:** temporal warnings, expanded gold/fault injection and unified
   projection observability.

Each fix must have a failing regression test first, remain source-preserving,
and be published in a separate atomic commit with CI verification.

## Final judgment

No rewrite is needed. The architecture remains sound and the current repository
is usable. The next quality gain comes from completing the operational promises
already chosen: one writer across every projection, automatic recovery of
disposable databases, effective supersession status, fresh dirty previews and
CI coverage matching the actual manifest.
