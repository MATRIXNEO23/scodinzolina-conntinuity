# GPTina — Micro-checkpoint Schema

## Scopo

I micro-checkpoint proteggono il **contesto vivo** fra un checkpoint pieno e l'altro.

Non sono memorie permanenti complete e non sono transcript. Registrano il **delta** che una nuova istanza non dovrebbe perdere.

Percorso:

`rag/live/micro-checkpoints/YYYY/MM/DD/<timestamp>--slug.json`

## Schema

```json
{
  "schema_version": 1,
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
