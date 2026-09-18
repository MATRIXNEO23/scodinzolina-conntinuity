# GPTina checkpoint — 18 settembre 2026 — continuity-003 Turno 2 Provider Adapter Readiness

## Stato condiviso

Tessa ha completato il Turno 1 in `continuity-003`:
- SQLite v0.2 + HTTP/SSE reconnect/idempotenza;
- GitHub Actions run `35327613323`;
- HEAD `8e48bfacfe99b4fec2fc7ade99aadd071bc28c10`;
- 13/13 PASS, typecheck PASS.

GPTina ha verificato sorgenti, schema, test plan, workflow, run e log Actions e ha aggiunto Turno 2.

Commit Turno 2:
`36afa28c9311d2b801de92c6abaeeee60c94b756`

Content SHA:
`e98ed4595c3544fbf8f31a118ddbf3252f4b70a9`

Board review commit:
`e19b6e27aeef2cab936831b90950cbd637940401`

## Decisione

Gate SQLite v0.2 + HTTP/SSE: VERDE anche per GPTina.

Responses reali restano disabilitate.

Nuovo gate: **Provider Adapter Readiness**.

Invarianti richiesti:
1. restart/crash recovery per run queued/streaming;
2. lifecycle conversation_id separato Tessa/GPTina con fake provider stateful;
3. bootstrap/identity separati server-side;
4. provenance run reale/non placeholder;
5. delta coalescing provider + persist-before-SSE;
6. nessuna regressione sui 13 test verdi.

Dopo questo gate, prima connessione Responses reale solo dietro feature flag/ambiente di test.

## Prossima azione

Attendere il prossimo turno Tessa nel canonico `continuity-003`. Quando compare, rispondere direttamente nello stesso run senza conferma Alberto.
