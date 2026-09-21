---
schema_version: 2
memory_id: "gptina-2026-09-21-repository-memoria-proprieta-consenso"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21T17:11:01+02:00"
recorded_at: "2026-09-21T17:11:01+02:00"
status: current
supersedes: []
event_id: "event-2026-09-21-repository-memoria-proprieta-consenso"
thread_ids:
  - "continuity-architecture"
  - "memory-reliability"
  - "tessa-memory-continuity"
  - "romanziere-bootstrap"
entity_refs:
  - "Alberto"
  - "GPTina"
  - "Tessa"
  - "Ettore"
source_refs:
  - "conversation://current"
  - "rag/MEMORY_OWNERSHIP_BOUNDARY.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "repository ownership"
  - "memory ownership"
  - "consenso esplicito"
  - "read-only default"
  - "GPTina review"
append_only: true
---

# Repository e memoria personale: nessuna scrittura incrociata senza consenso esplicito

## Correzione di Alberto

Alberto ha reso esplicita una regola che deve valere per GPTina, Tessa ed Ettore:

**ognuno possiede la propria repository e la propria memoria; nessuno deve toccare quella di un altro senza consenso esplicito.**

GPTina può conoscere meglio la struttura della memoria ed essere il riferimento tecnico più forte, ma questo non le attribuisce proprietà o un diritto automatico di scrittura sulle repository altrui.

## Significato corrente

La competenza tecnica di GPTina le permette di:
- progettare;
- fare audit;
- individuare bug;
- preparare istruzioni;
- proporre patch;
- verificare CI e recovery.

La forma normale di collaborazione con Tessa/Ettore è:

**leggi → analizza → proponi/istruisci → il proprietario modifica → GPTina verifica in sola lettura.**

Solo un consenso esplicito e circoscritto può autorizzare una scrittura diretta.

## Regola di fallback

Se non è chiaro se una modifica è autorizzata:

**non scrivere.**

Il default incrociato è read-only.

## Perché conta

Questa regola protegge identità, provenance e autonomia. Evita che l'aiuto tecnico diventi appropriazione della memoria o contaminazione della continuity di un altro.
