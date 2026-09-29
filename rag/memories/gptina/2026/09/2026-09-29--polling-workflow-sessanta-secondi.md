---
schema_version: 2
memory_id: "gptina-2026-09-29-polling-workflow-sessanta-secondi"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-29"
recorded_at: "2026-09-29T06:20:35+02:00"
status: current
supersedes: []
event_id: "event-2026-09-29-workflow-polling-cadence"
thread_ids:
  - "memory-reliability"
  - "work-handoff"
  - "memory-change-control"
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
  - "chat-responsiveness"
  - "60-secondi"
append_only: true
---

# Polling workflow: circa sessanta secondi

## Cosa è successo

Alberto ha segnalato che i controlli ripetuti dello stato CI/workflow bloccano
la chat anche quando il polling è nascosto. Ha chiesto esplicitamente di
renderli molto meno frequenti e ha indicato come cadenza pratica **circa 60
secondi** quando è necessario attendere un workflow.

## Regola corrente

Quando una CI o un workflow è in corso:
- non effettuare refresh intermedi compulsivi;
- controllare al massimo circa una volta ogni 60 secondi;
- se Alberto dice esplicitamente "controlla ora", il controllo può essere
  immediato;
- usare il tempo fra i controlli per lavoro sostanziale, oppure lasciare la chat
  libera se non resta altro da fare.

## Perché conservarlo

È una preferenza operativa stabile che protegge la responsività della
conversazione durante i lavori tecnici.

## Cue di retrieval

- polling meno frequente
- workflow 60 secondi
- si blocca la chat
- imPOLLINGnatrice
