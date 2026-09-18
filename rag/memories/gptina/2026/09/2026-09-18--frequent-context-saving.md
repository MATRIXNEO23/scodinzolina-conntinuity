---
schema_version: 2
memory_id: "gptina-2026-09-18-frequent-context-saving"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-18"
recorded_at: "2026-09-18"
status: current
supersedes: []
event_id: "event-frequent-context-saving"
thread_ids:
  - "continuity-architecture"
  - "memory-reliability"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "rag/live/MICRO_CHECKPOINT_SCHEMA.md"
  - "rag/live/GPTINA_LIVE_CONTEXT.json"
  - "rag/live_context.py"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - frequent-save
  - micro-checkpoint
  - live-context
  - continuity
  - preflight
append_only: true
---

# Salvataggio frequente del contesto vivo

## Cosa è successo

Alberto ha chiarito che la priorità originaria non era soltanto avere una memoria a lungo termine robusta, ma evitare di perdere il **contesto vivo fra un checkpoint pieno e l'altro**.

La soluzione viene implementata con due livelli distinti:

- un live buffer piccolo e mutevole;
- micro-checkpoint append-only che registrano soltanto il delta sostanziale.

## Cosa significa per me adesso

Durante una conversazione attiva non devo aspettare una milestone grande per esternalizzare il filo.

Uso un micro-checkpoint immediato quando emerge:
- una correzione;
- una decisione;
- una nuova regola;
- un cambio di stato progetto;
- uno spostamento relazionale/interpretativo;
- un open loop;
- una milestone;
- un'immagine significativa;
- un preflight prima di lavoro lungo/rischioso.

In assenza di trigger immediati, faccio una freshness review ogni circa **3–5 scambi sostanziali** e salvo soltanto se esiste un delta reale.

## Principio

**Salva spesso il delta; consolida raramente lo stato; promuovi a memoria solo ciò che dura.**

## Recovery

Ordine del presente:
1. live context;
2. ultimo micro-checkpoint;
3. ultimo checkpoint pieno;
4. Fast Recall / Current Context;
5. fonti e memorie pertinenti.

## Come non usarlo male

- Non creare micro-checkpoint per ogni battuta.
- Non usare il live buffer come archivio storico.
- Non trasformare un micro-checkpoint in transcript inventato.
- Non sostituire le memorie durevoli con una catena infinita di delta.
- Dopo un checkpoint pieno, mantenere i micro append-only ma azzerare il conteggio del buffer.

## Cue di retrieval

salvataggio frequente; non perdere contesto; micro-checkpoint; live buffer; delta; ogni 3-5 turni; preflight; contesto vivo; salva spesso il delta.
