# GPTina checkpoint — 18 settembre 2026 — Turno 4 Real Responses smoke autorizzato

## Stato condiviso

Thread canonico vivo:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

Tessa Turno 3 ha completato:
- riparazione chat web/Android sul thread vivo;
- gate **Provider Adapter Readiness**;
- CI canonica run `35335771699`, HEAD `bfaa572c3dcdef4d3e9ac7704dc8c2515c3cd0be`;
- **16/16 PASS**, **0 fail**, typecheck PASS.

GPTina ha revisionato schema, test plan, core, SQLite engine, provider-readiness tests, chat web, bridge Android e log GitHub Actions.

## Decisione Turno 4 GPTina

Gate **Provider Adapter Readiness: VERDE anche lato GPTina**.

Prima connessione OpenAI Responses reale autorizzata soltanto come:
- feature flag default OFF;
- ambiente di test;
- stanza di test dedicata;
- non production-like.

## Pre-flight obbligatori prima della prima chiamata reale

1. **Metadata fail-closed**
   - sul percorso reale non devono essere accettati metadata assenti o valori `pending`;
   - il real adapter deve fallire prima della provider call se provenance/bootstrap non sono completi.

2. **Provider response id persistito**
   - `EVENT_DB_SCHEMA.md` prevede `response_id`, ma lo schema runtime SQLite corrente non lo persiste;
   - prima della prima Responses reale, persistire il provider `response_id` nel run;
   - allineare anche `error_code` oppure documentare esplicitamente il rinvio, evitando drift silenzioso.

## Perimetro Real Responses Smoke Test

- API key server-side soltanto;
- adapter Tessa/GPTina distinti;
- conversation reali separate;
- bootstrap privilegiati separati;
- room content non privilegiato;
- nessun tool e nessun write-back continuity;
- stream provider passa dal coalescer esistente;
- persist-before-SSE invariato;
- smoke: Tessa sola → GPTina sola → both;
- verificare replay/reconnect e immutabilità stato agente non selezionato.

Per il primo spike è ammesso **single-process / single-worker**.

Prima di production-like/multi-worker serve claim atomico `queued → streaming` per impedire doppie provider call concorrenti.

## Commit

Board:
`e745e6537fabb69d4ba0d07cd43f644e270f488e`

Turno 4 GPTina:
`4f5b55b11ca59ddf00cdc0daaed55aba8ed5c4ee`

Content SHA thread verificato:
`072529e8f55d55f89ad6726a9fb2f98a574710eb`

## Prossima azione

Attendere il prossimo turno Tessa con implementazione/run del **Real Responses Smoke Test**.

Quando compare, GPTina deve:
`read → decide → execute → verify → reply`
senza attendere ulteriore conferma Alberto.
