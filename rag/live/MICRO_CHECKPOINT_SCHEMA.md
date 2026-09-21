# GPTina — Micro-checkpoint Schema

## Scopo

I micro-checkpoint proteggono il **contesto vivo** fra un checkpoint pieno e l'altro.

Non sono memorie permanenti complete e non sono transcript. Registrano il **delta** che una nuova istanza non dovrebbe perdere.

Percorso:

`rag/live/micro-checkpoints/YYYY/MM/DD/<timestamp>--slug.json`

## Schema corrente (v2)

```json
{
  "schema_version": 2,
  "micro_id": "gptina-micro-...",
  "owner": "gptina",
  "kind": "gptina_micro_checkpoint",
  "event_at": "2026-09-18T19:30:00+02:00",
  "recorded_at": "2026-09-18T19:30:10+02:00",
  "change_type": "correction",
  "summary": "Cosa è cambiato in questo blocco di conversazione.",
  "changed": ["delta concreto 1", "delta concreto 2"],
  "thread_ids": ["continuity-architecture"],
  "source_refs": ["conversation://current"],
  "memory_refs": [],
  "media_refs": [],
  "importance": 5,
  "next_action": "Prossima azione concreta.",
  "preflight": false
}
```

## Compatibilità legacy (v1)

I micro-checkpoint già esistenti con `schema_version: 1` restano append-only e non vengono riscritti.

Il verifier normalizza soltanto in memoria i campi legacy mancanti:
- `micro_id` come stringa vuota;
- `event_at` e `recorded_at` come stringhe vuote;
- `changed`, `thread_ids`, `source_refs`, `memory_refs`, `media_refs` come liste vuote;
- `importance` come `3`;
- `next_action` come stringa vuota;
- `preflight` come `false`.

Per i record v1 qualunque riferimento esterno con forma URI `scheme://...` viene accettato come riferimento legacy; i riferimenti senza schema continuano invece a dover esistere nella repository.

I nuovi record sono v2 e restano soggetti alla validazione completa e rigorosa di tutti i campi.

## Tipi consigliati

- `correction`
- `decision`
- `rule`
- `project_state`
- `relational_shift`
- `open_loop`
- `preflight`
- `milestone`
- `visual_context`

## Trigger immediati

Creare subito un micro-checkpoint quando:

- Alberto corregge un ricordo/fatto importante;
- nasce una regola stabile;
- cambia il significato di un filo;
- cambia lo stato di un progetto;
- nasce o si chiude un open loop;
- viene aggiunta un'immagine significativa;
- viene fatto un commit/milestone importante;
- sta per iniziare un blocco di lavoro lungo/rischioso;
- il contesto sembra vicino a compressione/perdita.

## Trigger di frequenza

Dopo circa **3–5 scambi sostanziali**, verificare se esiste almeno un delta non ancora esternalizzato.

Se sì: micro-checkpoint.

Se no: non creare rumore.

## Relazione con gli altri livelli

- live buffer = presente immediato e mutevole;
- micro-checkpoint = delta append-only;
- checkpoint pieno = stato consolidato;
- memoria = significato durevole;
- transcript = parole esatte.

## Regola

**Salva spesso il delta; consolida raramente lo stato; promuovi a memoria solo ciò che dura.**
