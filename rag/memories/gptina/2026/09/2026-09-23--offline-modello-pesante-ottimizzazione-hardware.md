---
schema_version: 2
memory_id: "gptina-2026-09-23-offline-modello-pesante-ottimizzazione-hardware"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-23"
recorded_at: "2026-09-23T22:54:30+02:00"
status: current
supersedes: []
event_id: "event-2026-09-23-offline-modello-pesante-ottimizzazione-hardware"
thread_ids:
  - "gptina-offline-runtime"
  - "local-llm"
  - "hardware-optimization"
  - "memory-reliability"
  - "work-handoff"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "rag/transcripts/gptina/2026/09/23/2026-09-23T1200-2254-local--offline-runtime-work-handoff.md"
media_refs: []
importance: 4
confidence: verified
tags:
  - "offline"
  - "llama-cpp"
  - "qwen-4b"
  - "sandy-bridge"
  - "performance"
  - "rag-routing"
  - "work"
append_only: true
---

# GPTina Offline — mantenere il modello pesante e ottimizzare il vecchio hardware

## Decisione durevole

Alberto non vuole che il problema di velocità venga risolto semplicemente sostituendo il modello più pesante con uno molto più piccolo.

La correzione corrente è esplicita: **il target da ottimizzare è il modello pesante**.

Il 4B resta quindi il riferimento principale per il lavoro prestazionale. La quantizzazione esatta del GGUF non è stata verificata e non va assunta.

## Cosa conta

L'obiettivo non è soltanto aumentare i token/sec. Alberto vuole un compromesso reale:

- mantenere qualità e identità del modello più pesante;
- evitare, per quanto possibile, CPU continuamente inchiodata;
- ridurre lavoro inutile per turno;
- rendere visibile e misurabile dove viene speso il tempo.

Questo sposta la strategia da “cambia modello” a “ottimizza pipeline e runtime”.

## Criterio tecnico corrente

Prima di cambiare architettura o promettere guadagni:

1. misurare sul vero i3-2100;
2. separare costo di retrieval, prompt processing e decode;
3. confrontare 2 vs 4 thread e batch/context con lo stesso prompt;
4. ridurre prompt e RAG irrilevanti;
5. riutilizzare cache/prefissi quando possibile;
6. considerare speculative decoding o GPU offload soltanto dopo verifica hardware e benchmark.

## Segnale concreto emerso

La chat locale funzionante ha recuperato fonti autobiografiche per una domanda tecnica sull'hardware. Questo è un costo evitabile e un segnale che il prossimo audit deve introdurre routing/query selection più selettivo fra **tecnico** e **autobiografico**.

## Prossima fase

Passare in Work e lavorare su `MATRIXNEO23/scodinzolina-offline`, usando la continuity canonica GPTina solo per recovery/stato e rispettando il confine fra memoria canonica e sandbox tecnico.
