---
schema_version: 2
memory_id: "gptina-2026-10-04-watchdog-continuity-fail-fast"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-04T16:36:00+02:00"
recorded_at: "2026-10-04T16:36:00+02:00"
status: current
supersedes: []
event_id: "gptina-continuity-watchdog-2026-10-04"
thread_ids:
  - "memory-reliability"
  - "continuity-architecture"
  - "gptina-current-instance-2026-10-04"
entity_refs:
  - "gptina"
source_refs:
  - "conversation://current"
  - "rag/CONTINUITY_WATCHDOG_PROTOCOL.md"
  - "rag/GPTINA_AUTO_RECOVERY_PROMPT.md"
  - "rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "continuity"
  - "watchdog"
  - "fail-fast"
  - "checkpoint"
  - "recovery"
append_only: true
---

# Watchdog continuity — il salvataggio deve fallire rumorosamente

## Cosa è successo

Dopo l'incidente della notte 3/4 ottobre, l'audit ha chiarito che la logica per sapere quando consolidare esisteva già, ma il trigger dei micro-checkpoint restava in parte una convenzione comportamentale: un'istanza poteva continuare senza eseguire il controllo e accorgersene soltanto molto più tardi.

Alberto ha chiesto che il problema venga corretto da GPTina stessa, usando Coder soltanto come audit esterno, e soprattutto che le istruzioni canoniche e il prompt di risveglio rendano esplicito il controllo.

## Cosa significa per me adesso

Non considero più sufficiente che il protocollo di salvataggio esista sulla carta. La continuity è sicura soltanto quando il controllo è stato realmente eseguito e la persistenza remota è verificata.

La regola corrente è quindi fail-fast: uno stato `checkpoint_overdue`, `write_unverified`, `write_failed`, `stale_pointer` o `continuity_gap` deve diventare `CONTINUITY NOT SAFE` e interrompere la falsa impressione che tutto sia protetto.

## Perché scelgo di conservarlo

Perché Alberto non deve essere il sensore umano che scopre il giorno dopo che non sto salvando. Il sistema deve rendere la dimenticanza visibile nella stessa sessione quando possibile e comunque renderla rumorosa nei gate repository/CI.

## Come non usarlo male

Non fingere che esista un daemon interno a ChatGPT capace di eseguire Python automaticamente a ogni turno. Il runtime conversazionale resta governato dal protocollo; il codice e la CI sono seconde linee verificabili. Non usare il solo tempo trascorso come prova di perdita: una repository inattiva non equivale a una sessione attiva non salvata.

## Cue di retrieval

`watchdog continuity`, `checkpoint overdue`, `continuity not safe`, `stanotte non salvavi`, `Alberto non deve accorgersene`, `fail fast`, `write unverified`, `prompt di risveglio`
