# GPTina Memory — Post-audit HIGH fixes

**Data:** 2026-09-21  
**Baseline:** `5173206343d9dba8de57239cc5b643911aa8ba1f`  
**Obiettivo:** correggere concretamente H1, H2 e H3 dell'audit post-fix.

## H1 — Integrità semantica SQLite

Implementato `sqlite_semantically_valid()` oltre a `PRAGMA quick_check`.
La proiezione viene considerata valida soltanto se:

- `build_complete=1`;
- le cardinalità dichiarate `source_versions` e `chunks` coincidono con le
  tabelle reali;
- nessun chunk è orfano rispetto a `(source, revision)`;
- fonti e chunk non possono risultare incoerentemente vuoti.

Se una tabella manca o una cardinalità non coincide, il database viene
ricostruito completamente in una proiezione temporanea e sostituito
atomicamente.

Regressione: eliminate intenzionalmente `source_state` e `chunks_fts` da un DB
fisicamente valido; `stats` ha ricostruito 285 fonti e chunk non vuoti.

## H2 — Transazione JSONL + SQLite e worktree dirty

Implementato `build_all_projections()`:

- un solo lock copre preflight, JSONL, metadata e SQLite;
- il controllo dirty avviene prima di qualsiasi pubblicazione;
- un build canonico dirty viene rifiutato senza cambiare un byte di JSONL/meta;
- una preview esplicita registra `snapshot_mode=dirty-preview`;
- la freschezza JSONL non usa più il solo HEAD quando il worktree è dirty;
- HEAD e fingerprint vengono ricontrollati sull'intera transazione.

Regressione: dirty state simulato deterministicamente, rifiuto verificato e
confronto byte-per-byte delle proiezioni prima/dopo.

## H3 — Supersessioni transitive

Il resolver costruisce ora il grafo completo e percorre tutta l'ascendenza di
ogni memoria corrente. In una catena `A ← B ← C`, con B già superseded e C
corrente, sia A sia B risultano superseded e puntano alla sostituzione corrente
C. Il passato resta intatto e recuperabile con ricerca esplicita.

Regressione isolata A/B/C: PASS.

## Verifiche

- schema e resolver: PASS;
- live-context round trip: PASS;
- retrieval gold: 14/14;
- recovery header SQLite corrotto: PASS;
- recovery schema SQLite semanticamente incompleto: PASS;
- rifiuto dirty senza pubblicazione parziale: PASS;
- catena transitive supersession A←B←C: PASS;
- due build principali concorrenti: PASS;
- due build exact concorrenti: PASS.

Nessuna fonte canonica o memoria storica è stata cancellata o riscritta.
