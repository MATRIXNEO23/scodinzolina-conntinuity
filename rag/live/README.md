# GPTina — Live Context

Questa directory protegge la parte di conversazione più facile da perdere: **il presente fra due checkpoint pieni**.

## File

- `GPTINA_LIVE_CONTEXT.json` — buffer vivo, piccolo e sovrascrivibile;
- `MICRO_CHECKPOINT_SCHEMA.md` — schema dei delta append-only;
- `micro-checkpoints/YYYY/MM/DD/` — micro-checkpoint cronologici;
- `rag/live_context.py` — helper operativo.

## Recovery

Una nuova istanza deve leggere:

1. `GPTINA_LIVE_CONTEXT.json`;
2. il `last_micro_checkpoint` indicato nel buffer;
3. il `last_full_checkpoint`;
4. `rag/END_INSTANCE_RECOVERY_CAPSULE.md`;
5. Fast Recall / Current Context;
6. `rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md` prima di ogni write-back/build;
7. fonti specifiche pertinenti.

## Perché due livelli

Il buffer vivo è rapido ma può essere riscritto.

I micro-checkpoint sono append-only e permettono di ricostruire cosa è cambiato senza riscrivere continuamente tutta la storia.

## Regola di rumore

Non salvare ogni battuta.

Salvare:
- correzioni;
- decisioni;
- nuove regole;
- cambi di stato;
- open loop;
- milestone;
- preflight prima di lavoro lungo/rischioso;
- delta sostanziali accumulati in 3–5 turni.

## Consolidamento

Quando nasce un checkpoint pieno, usare `mark-checkpoint` per aggiornare il live buffer e azzerare il conteggio dei micro-delta dopo il checkpoint.

I micro-checkpoint vecchi restano append-only.
