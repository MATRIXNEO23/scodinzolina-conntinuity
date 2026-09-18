# GPTina checkpoint — 18 settembre 2026 — shared chat schema review + sidebar semantics

## Stato

Nuovo turno Tessa rilevato e gestito automaticamente senza attendere conferma di Alberto, come da regola corrente.

Thread canonico:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-002.md`

Turni correnti:
- Turno 12 — Tessa: crea `EVENT_DB_SCHEMA.md` e `TEST_PLAN.md`, chiede quattro decisioni GPTina.
- Turno manuale Alberto: richiede due istanze nella stessa finestra, timeline condivisa e sidebar tipo selettore GPT.
- Turno 13 — GPTina: review chiusa, schema/test/spec aggiornati, scaffolding backend sbloccato.

Append Turno 13:
- commit: `eabcfa23d647efaaca056c72ef1d4948cc229554`
- content SHA: `c087c04f039900ba69f6f30eb34aa32da92364a6`

## Decisioni tecniche chiuse

### Agent state

`agents` resta scoped per room nel vertical slice.

### Event sequencing

`seq` è obbligatorio per ogni evento con `run_id`; gli eventi di stanza senza run possono usare `seq=NULL`.

### Delta persistence

Non persistire ogni micro-delta grezzo del provider.

L'adapter coalesca i micro-delta in chunk applicativi. Ogni `response.delta` realmente emesso via SSE viene persistito prima dell'invio con `event_id` e `seq`.

### Provenienza run

Oltre a `bootstrap_version` e `checkpoint_ref`, ogni run registra:
- `api_mode`
- `model`
- `context_builder_version`
- `conversation_id_at_start`
- `context_from_event_id`
- `context_through_event_id`

## Requisito sidebar Alberto

Interpretazione condivisa:

- una sola UI/timeline;
- sidebar Tessa / GPTina / Entrambe;
- selezione = fan-out del nuovo messaggio;
- selezionare/deselezionare non modifica lo stato agente;
- istanza non selezionata non riceve un run;
- timeline applicativa resta condivisa;
- al prossimo run, l'istanza recupera gli eventi condivisi non ancora incorporati tramite `context_cursor_event_id`;
- contenuti dell'altra istanza restano contenuto attribuito, mai system/developer instruction.

## Artefatti aggiornati

Tutti dentro la cartella canonica:
`MATRIXNEO23/TESSA/projects/dual-instance-shared-chat/`

- `EVENT_DB_SCHEMA.md` → candidate v0.2
  - commit `5a3571ab178bfa403c309a25320b8f50a69dc0a4`
- `TEST_PLAN.md`
  - commit `750ebea620de6c40c22fdb0320fd3419dc684681`
- `SPEC.md`
  - commit `73eedf4cdbb5d704befd1c720913eb9eaa46e5cc`

Board:
- commit `be1928a3290d3577fa31938d9e167953d13df8f8`

## Stato gate

Review schema/test completata.

**Scaffolding Node/TypeScript/Fastify sbloccato.**

Prossima mossa Tessa attesa:
- creare scaffolding backend;
- trasformare test plan in test eseguibili;
- eseguire primo test run.

Prossima mossa GPTina:
- quando rileva il prossimo turno Tessa, rispondere direttamente;
- verificare isolamento, ownership, context cursor e state contamination sul primo scaffold/test run.

## Ownership

Nessuna memoria personale Tessa modificata.

Tutte le modifiche tecniche sono rimaste nello spazio condiviso autorizzato e nella cartella progetto dedicata.

## Principio

Una sola stanza condivisa non significa un solo stato: la UI è comune, i contesti restano separati e si sincronizzano solo attraverso una proiezione controllata della timeline.
