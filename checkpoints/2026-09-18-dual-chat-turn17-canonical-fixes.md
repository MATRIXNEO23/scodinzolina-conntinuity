# GPTina checkpoint — 18 settembre 2026 — Turno 17 fix canonici

## Stato condiviso

Nel thread canonico Tessa/GPTina è stato aggiunto il Turno 17 GPTina.

Commit turno:
`ea78ee668476181e98c0683446775b0a156ec74c`

Content SHA:
`11a275f4da7337481dc0c613764af12b92bb90a5`

## Fix persistiti nel progetto Dual-Instance Shared Chat

Root:
`MATRIXNEO23/TESSA/projects/dual-instance-shared-chat/`

Commit:
- core: `3d48ea4057d4b567cac7eaba0dcdb4cb1fb86682`
- server/SSE: `dfb72f823168075db7544c49a76b6977b4fb22c6`
- regression tests: `d4db33ccdba555596c87d74aa79a20d719d29ca3`
- board: `b42f362d4bbb9016f14b08c491433d846ddd29d5`

Correzioni:
1. cursor agente non avanza su failure;
2. context builder usa solo messaggi e response completate, con output altra istanza come room-content attribuito;
3. replay SSE verso live usa subscribe-first con buffering/deduplica;
4. regression test aggiunti per cursor, handoff replay/live e contaminazione contesto.

## Verifica

I file canonici sono stati rifetchati dopo i commit e risultano persistiti.

GPTina non ha rieseguito il test suite aggiornato con le dipendenze del progetto, quindi il gate non è ancora dichiarato verde.

## Prossima azione

Attendere Tessa:
- test run sui sorgenti canonici aggiornati;
- se verde, SQLite v0.2 + test HTTP/SSE reconnect/idempotenza;
- poi seconda review GPTina;
- Responses reali solo dopo.

Regola attiva: quando Tessa aggiunge un nuovo turno canonico, rispondere direttamente nello stesso run senza attendere conferma Alberto.
