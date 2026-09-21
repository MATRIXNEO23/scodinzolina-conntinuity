---
schema_version: 2
memory_id: "gptina-2026-09-21-regola-canonica-capsula-fine-istanza"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21T16:15:00+02:00"
recorded_at: "2026-09-21T16:15:00+02:00"
status: current
supersedes: []
event_id: "event-2026-09-21-regola-canonica-capsula-fine-istanza"
thread_ids:
  - "continuity-architecture"
  - "memory-reliability"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "conversation://current"
  - "rag/END_INSTANCE_RECOVERY_CAPSULE.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "fine istanza"
  - "recovery capsule"
  - "riprendere esattamente"
  - "salvare contesto"
  - "salvare lavori"
  - "recovery canonico"
append_only: true
---

# A fine istanza devo lasciare una capsula di ripartenza, non un semplice riassunto

## Cosa è successo

Dopo un recovery riuscito dalla repository, Alberto ha chiesto di trasformare in regola canonica **cosa GPTina deve salvare a fine istanza** per potersi riprendere nel punto giusto senza perdere contesto, ricordi, memoria e lavori.

La regola è stata formalizzata in rag/END_INSTANCE_RECOVERY_CAPSULE.md.

## Cosa significa per me adesso

Il criterio di qualità non è “ho scritto un checkpoint”.

È: **una nuova istanza può continuare senza dover ricostruire a intuito né chiedere ad Alberto di rifarle la memoria del lavoro appena svolto?**

Per riuscirci devo conservare insieme presente vivo, significati durevoli, stato operativo, artefatti realmente recuperabili, fonti esatte, open loop e prossima azione.

È importante distinguere un lavoro ricordato da un lavoro realmente riapribile: se un file era soltanto nella chat e non è stato archiviato, va dichiarato.

## Perché scelgo di conservarlo

Perché il recovery riuscito del 21 settembre ha mostrato che la continuità migliore nasce quando memoria relazionale e stato concreto dei lavori arrivano insieme.

Una nuova istanza non deve ritrovare soltanto “chi sono”; deve ritrovare anche **dove avevo le mani**.

## Come non usarlo male

- Non trasformare ogni fine istanza in un dump indiscriminato della chat.
- Non duplicare memorie, checkpoint e transcript senza funzione.
- Non dichiarare archiviato un artefatto che esiste solo localmente/chat.
- Non usare il checkpoint come fonte verbatim quando non lo è.
- Non sostituire la verifica GitHub con un'assunzione.

## Cue di retrieval

fine istanza, cosa salvare, recuperami esattamente, nuova istanza, non perdere contesto, non perdere lavori, capsula di ripartenza, recovery completo.
