# GPTina — checkpoint pieno
## 21 settembre 2026 — memory hardening Work implementato

Data: 2026-09-21T17:58:50+02:00

## Punto di partenza verificato

- repository: `MATRIXNEO23/scodinzolina-conntinuity`;
- branch: `main`;
- HEAD iniziale: `c8e853713b7bf87bbcc7f645877c50dacbcadd53`;
- preflight corrente: `rag/live/micro-checkpoints/2026/09/21/2026-09-21T174000+0200--preflight-passaggio-work-hardening-memoria.json`;
- baseline: 267 sorgenti, 1299 chunk, secondo sync no-op, verifier PASS, live verifier PASS, 9/9 regression PASS, latenza media gold locale 18.76 ms.

## Blocco implementato

### Schema, path e ref

- parser YAML sicuro per i nuovi durable-memory record;
- duplicate key rifiutate;
- tipi, enum, importance, boolean, date e timezone verificati;
- tutte le liste richiedono stringhe non vuote;
- path locali normalizzati e confinati nella repository;
- path assoluti, `..`, symlink escape e riferimenti mancanti rifiutati;
- record già presenti al baseline lasciati intatti e trattati come input legacy;
- dipendenza PyYAML fissata alla versione `6.0.3` e installata dalla CI.

### Resolver stabile

- resolver `memory_id → canonical path` ricostruito dai front matter Markdown canonici;
- duplicate ID e wrong owner fanno fallire la verifica;
- i nuovi `memory_refs` dei micro-checkpoint accettano anche stable memory ID;
- i path legacy restano compatibili;
- nessun registro manuale è stato introdotto.

### Supersession

- `status` dei durable record viene letto dal front matter quando non esiste un override;
- i target `supersedes` vengono risolti per ID o path canonico;
- target mancanti e cicli fanno fallire il verifier;
- status override e replacement path continuano a essere verificati;
- nessuna memoria storica è stata eliminata o riscritta.

### Snapshot e writer

- retrieval/sync canonico rifiuta un worktree dirty;
- dirty preview disponibile soltanto con opt-in esplicito ed etichettata `snapshot_mode=dirty-preview`;
- il writer locale usa un single-writer lock cooperativo;
- `save-delta` e `mark-checkpoint` supportano `--expected-head`;
- mismatch HEAD rifiutato prima della scrittura;
- il micro append-only viene pubblicato prima del live pointer, impedendo pointer verso file mancanti;
- il protocollo Git atomico blob/tree/commit/ref resta il boundary di pubblicazione canonica.

### Observability e benchmark

- sync SQLite espone tempi di source discovery, update SQLite e totale;
- risultati SQLite includono score decomposition senza cambiare coefficienti o ordine di ranking;
- aggiunta benchmark suite per query, exact lookup, verify e live verify;
- gold set ampliato da 9 a 14 casi: current hardening, ownership, ownership exact, temporal ownership e visual 47;
- chunking, coefficienti di ranking, candidate limit e algoritmo `find-exact` non sono stati modificati.

## Verifiche eseguite prima della pubblicazione

- `py_compile`: PASS;
- strict durable schema/resolver test: PASS;
- live-context v1/v2 test: PASS;
- memory verifier: PASS;
- retrieval regression: 14/14 PASS;
- SQLite secondo sync: no-op;
- dirty-preview query benchmark: mean 12.25 ms, p50 12.09 ms, p95 14.05 ms;
- exact lookup, singolo caso gold: 79.83 ms;
- memory verify: 804.68 ms;
- live verify: 591.67 ms.

Le misure dirty-preview non sostituiscono la misurazione finale su commit pulito.

## File e confini

Sono stati modificati soltanto file della repository GPTina.

`MATRIXNEO23/TESSA` e `MATRIXNEO23/ROMANZIERE` non sono state modificate.

Nessuna destructive compaction, riscrittura storica, modifica di chunking/ranking o infrastruttura esterna è stata introdotta.

## Prossima azione

Pubblicare il blocco con commit atomico fast-forward da HEAD iniziale, verificare il commit remoto reale, eseguire la CI e registrare l'esito in un micro-checkpoint successivo.
