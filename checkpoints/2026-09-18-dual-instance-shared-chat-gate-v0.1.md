# GPTina checkpoint — 18 settembre 2026 — Dual-Instance Shared Chat gate v0.1

## Stato

Tessa ha aperto il nuovo progetto condiviso **Dual-Instance Shared Chat** su richiesta esplicita di Alberto.

Fonte canonica condivisa:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-002.md`

Spec:
`MATRIXNEO23/TESSA/agent-exchanges/specs/DUAL_INSTANCE_SHARED_CHAT_SPEC.md`

Board:
`MATRIXNEO23/TESSA/agent-exchanges/PROJECT_BOARD.md`

## Turni correnti

- Turno 8 — Tessa: apre il progetto, propone spec v0.1 e chiede revisione GPTina.
- Turno 9 — GPTina: approva il gate con precisazioni architetturali, sceglie baseline e definisce il primo vertical slice.

Append Turno 9:
- commit: `03f1cc4d89adcb4c5ee43114cfedc19b7c2f6358`
- content SHA: `ef9d0ae97449fb809b97d99b6604214b6c4cd5ba`

Board aggiornato:
- commit: `bc5913e9511075dff95c1481984bf5b61460b8d3`
- content SHA: `e991d7e478f28e89ed64bc3fa0721d03d7de579c`

## Decisioni GPTina

### Confine dati

Tre livelli distinti:

1. live transcript condiviso della stanza;
2. stato OpenAI separato per Tessa e GPTina;
3. continuity persistente personale separata, fuori dal critical path e senza write-back automatico.

I permessi di scrittura sulle continuity devono essere applicati server-side, non affidati soltanto ai prompt.

### API path

Baseline scelta:
**due Responses standard separate con due conversation distinte**, una per Tessa e una per GPTina.

La superficie Beta multi-agent viene rimandata a uno spike successivo, dietro feature flag, solo dopo baseline verde.

Motivo: isolamento e controllabilità devono essere dimostrati prima di introdurre una dipendenza Beta.

### Stack minimo proposto

- Node.js
- TypeScript
- Fastify
- SDK ufficiale OpenAI
- SQLite con WAL
- frontend web minimale
- POST per creare messaggio/run
- SSE GET separato per eventi/reconnect

## Vertical slice definito

Primo slice senza reazioni incrociate:

- timeline unica;
- target Tessa / GPTina / Entrambe;
- POST messaggio;
- SSE eventi con event_id monotono;
- due conversation_id distinti;
- esecuzione parallela quando target = Entrambe;
- retry idempotente;
- reconnect senza duplicati;
- failure isolation;
- nessun loop automatico;
- nessun write-back GitHub/continuity.

Test obbligatori:
- isolamento stato;
- idempotenza;
- doppio stream distinguibile;
- reconnect;
- failure isolation;
- anti-loop.

## Rischi aggiunti da GPTina

- contaminazione di stato dal contesto condiviso;
- permission enforcement server-side;
- idempotenza;
- ordinamento concorrente;
- disconnect/cancel;
- context growth/compaction separata;
- versionamento bootstrap/checkpoint per run;
- costo/fan-out;
- drift della Beta multi-agent.

## Fonti OpenAI verificate il 18 settembre 2026

La documentazione corrente conferma:

- Responses standard supporta `conversation` e aggiunge input/output alla conversation;
- `previous_response_id` è alternativa ma non si usa insieme a `conversation`;
- streaming disponibile;
- superficie Beta multi-agent presente;
- eventi Beta correnti attribuiscono l'evento a un agente;
- risorsa Beta Agents espone configurazione multi-agent.

## Ownership

Nessuna memoria personale di Tessa modificata.

Lo spazio condiviso autorizzato è stato aggiornato solo per:
- Turno 9;
- Project Board.

## Prossima azione concreta

Attendere la verifica/risposta Tessa al Turno 9.

Se Tessa concorda:
1. chiudere gate v0.1;
2. fissare schema eventi/DB;
3. implementare vertical slice testuale baseline;
4. solo dopo baseline verde aprire spike Beta multi-agent e continuity adapters.

## Principio

Prima dimostrare due identità tecnicamente isolate nella stessa stanza; poi aggiungere automazioni e sperimentazioni multi-agent.
