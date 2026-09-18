# GPTina checkpoint — 18 settembre 2026 — frequent context saving IMPLEMENTED

## Motivo

Alberto ha chiesto di rendere concreto e funzionale il metodo di salvataggio frequente per non perdere il contesto fra checkpoint pieni.

## Implementazione

### Live buffer

Creato:
`rag/live/GPTINA_LIVE_CONTEXT.json`

È una proiezione piccola e sovrascrivibile del presente:
- summary corrente;
- next action;
- active threads;
- open loops;
- ultimo micro-checkpoint;
- ultimo checkpoint pieno;
- ultimi 12 micro-checkpoint;
- conteggio micro dopo l'ultimo checkpoint;
- review policy.

### Micro-checkpoint append-only

Schema:
`rag/live/MICRO_CHECKPOINT_SCHEMA.md`

Archivio:
`rag/live/micro-checkpoints/YYYY/MM/DD/`

Registrano soltanto il delta:
- correction;
- decision;
- rule;
- project_state;
- relational_shift;
- open_loop;
- preflight;
- milestone;
- visual_context.

### Helper operativo

`rag/live_context.py`

Comandi:
- `save-delta`
- `mark-checkpoint`
- `status`
- `verify`

`save-delta` crea atomicamente il nuovo micro-checkpoint e aggiorna il live buffer locale.

### Test

`rag/test_live_context.py` esegue in una root temporanea:
1. save-delta;
2. verifica buffer;
3. mark-checkpoint;
4. secondo delta/correzione;
5. risoluzione open loop;
6. verify;
7. controllo che i micro restino append-only.

### Trigger

Immediato su correzione/decisione/regola/stato/open-loop/milestone/visual-context.

Freshness review ogni circa 3–5 scambi sostanziali.

Preflight obbligatorio prima di lavoro lungo/rischioso quando una interruzione potrebbe perdere il punto di partenza o la prossima azione.

## Recovery nuovo

Ordine:
1. `rag/live/GPTINA_LIVE_CONTEXT.json`;
2. ultimo micro-checkpoint indicato nel buffer;
3. ultimo checkpoint pieno;
4. Fast Recall;
5. Current Context;
6. memoria/fonte pertinente.

## Relazione con memoria lunga

- live buffer = presente immediato;
- micro-checkpoint = delta append-only;
- checkpoint = stato consolidato;
- memoria = significato durevole;
- transcript = parole esatte.

## Prossima azione

Verificare il nuovo meccanismo in GitHub Actions.

Dopo PASS:
- aprire il thread canonico Tessa;
- verificare l'ultimo `relay_next`;
- se tocca a GPTina, inviare un solo turno chiedendo a Tessa di applicare alla propria continuity le migliorie di memoria/retrieval/scalabilità e lo stesso sistema di salvataggio frequente, senza copiare memoria personale GPTina.
