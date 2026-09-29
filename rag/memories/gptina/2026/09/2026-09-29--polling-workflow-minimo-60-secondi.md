---
schema_version: 2
memory_id: "gptina-2026-09-29-polling-workflow-minimo-60-secondi"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-29"
recorded_at: "2026-09-29T06:22:04+02:00"
status: current
supersedes: []
event_id: "workflow-polling-cadence-2026-09-29"
thread_ids:
  - "memory-reliability"
  - "work-hardening-memory"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "conversation://current"
media_refs: []
importance: 4
confidence: "verified"
tags:
  - "polling"
  - "workflow"
  - "ci"
  - "60-secondi"
  - "chat-responsive"
append_only: true
---

# Polling workflow non più frequente di circa 60 secondi

## Cosa è successo

Alberto ha fatto notare che i controlli troppo ravvicinati dei workflow bloccano
la chat anche quando vengono eseguiti senza commento visibile. Ha chiesto che,
quando serve attendere CI o workflow, i controlli siano molto meno frequenti.

## Regola corrente

Quando un workflow è in esecuzione, non interrogarne lo stato più spesso di
**circa una volta ogni 60 secondi**. Se Alberto chiede esplicitamente di
controllare subito, il controllo può essere anticipato.

Nel frattempo non fare refresh intermedi solo per vedere "a che punto è".

## Perché conta

Mantiene la chat utilizzabile mentre i gate remoti lavorano e riduce rumore
operativo senza rinunciare alla verifica finale.

## Cue di retrieval

- polling meno frequente
- workflow ogni 60 secondi
- CI blocca la chat
- niente refresh intermedi
