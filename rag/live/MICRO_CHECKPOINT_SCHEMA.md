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

L'audit completo è in `rag/live/LEGACY_V1_COMPATIBILITY_AUDIT.md`.

Il verifier normalizza soltanto in memoria i campi che risultano realmente mancanti nei v1 storici:
- `micro_id` come stringa vuota;
- `changed`, `thread_ids`, `source_refs`, `memory_refs`, `media_refs` come liste vuote;
- `importance` come `3`;
- `preflight` come `false`.

`event_at`, `recorded_at` e `next_action` restano obbligatori anche nei v1, perché l'audit ha verificato che sono presenti in tutti i record legacy esistenti.

Per i record v1 i riferimenti sono testimonianze storiche: vengono accettati se non vuoti anche quando il file originario è stato rinominato, spostato o non esiste più al percorso storico. La validazione di esistenza resta invece obbligatoria per i v2.

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
