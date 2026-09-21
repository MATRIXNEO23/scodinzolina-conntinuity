---
schema_version: 2
memory_id: "gptina-2026-09-21-verifier-v2-compatibilita-legacy-da-replicare"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21"
recorded_at: "2026-09-21"
status: current
supersedes: []
event_id: "event-2026-09-21-verifier-v2-compatibilita-legacy"
thread_ids:
  - "continuity-architecture"
  - "memory-reliability"
  - "tessa-shared-correspondence"
  - "romanziere-bootstrap"
entity_refs:
  - "Alberto"
  - "GPTina"
  - "Tessa"
  - "Ettore"
source_refs:
  - "rag/live/LEGACY_V1_COMPATIBILITY_AUDIT.md"
  - "rag/live_context.py"
  - "rag/live/MICRO_CHECKPOINT_SCHEMA.md"
  - "rag/test_live_context.py"
  - "checkpoints/2026-09-21-live-verifier-v2-compatibility-completed.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "verifier"
  - "micro-checkpoint"
  - "schema v2"
  - "compatibilita legacy"
  - "Tessa"
  - "Ettore"
  - "continuity architecture"
append_only: true
---

# Verifier v2 + compatibilità legacy: correzione da preservare e replicare

Il 21 settembre 2026 GPTina ha corretto il proprio sistema di micro-checkpoint dopo aver scoperto che il verifier applicava troppo rigidamente lo schema corrente ai record storici v1.

## Stato corretto GPTina

- I vecchi micro-checkpoint v1 restano append-only e non vengono riscritti.
- Tutti i 50 v1 esistenti sono stati letti e auditati.
- Il verifier normalizza in memoria soltanto i campi realmente assenti nelle forme storiche osservate.
- I riferimenti v1 non vuoti possono restare validi come testimonianza storica anche se il target è stato rinominato/spostato.
- I nuovi micro-checkpoint sono schema v2.
- Il writer `save-delta` genera v2.
- Il verifier v2 resta rigoroso e rifiuta i record incompleti.
- I test coprono compatibilità v1 e severità v2.
- La CI deve essere verde prima di dichiarare la memoria sana.

## Audit reale v1

L'audit completo è in:

`rag/live/LEGACY_V1_COMPATIBILITY_AUDIT.md`

Nucleo v1 verificato presente in tutti i 50 record storici:

- `schema_version`
- `owner`
- `kind`
- `event_at`
- `recorded_at`
- `change_type`
- `summary`
- `next_action`

Normalizzazione legacy consentita solo per campi effettivamente mancanti:

- `micro_id`
- `changed`
- `thread_ids`
- `source_refs`
- `memory_refs`
- `media_refs`
- `importance`
- `preflight`

## Regola da trasferire a Tessa ed Ettore

Quando Tessa o Ettore presentano la stessa famiglia di problemi, non copiare alla cieca il profilo GPTina. Bisogna:

1. fare preflight;
2. leggere tutti i loro micro-checkpoint storici;
3. inventariare schema, campi mancanti, tipi, change_type e riferimenti realmente usati;
4. definire la compatibilità legacy sui dati osservati;
5. non riscrivere i record append-only;
6. introdurre un nuovo schema corrente rigoroso;
7. allineare writer, verifier, test e CI;
8. documentare come salvare spesso e come recuperare il presente;
9. dichiarare il sistema sano soltanto dopo verifica completa dell'archivio e CI PASS.

Alberto ha chiesto esplicitamente che questa correzione venga preservata per poter istruire Tessa appena il suo sistema sarà nuovamente disponibile e per portare Ettore alla stessa qualità infrastrutturale.
