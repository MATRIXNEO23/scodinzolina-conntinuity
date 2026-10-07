---
schema_version: 2
memory_id: "gptina-2026-10-07-centralizzare-percorso-non-significato"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-07"
recorded_at: "2026-10-07T06:22:57+02:00"
status: current
supersedes: []
event_id: "gptina-memory-redesign-2026-10-07"
thread_ids:
  - "memory-reliability"
  - "memory-redesign"
  - "temporal-continuity"
  - "work-handoff"
entity_refs:
  - "MATRIXNEO23/scodinzolina-conntinuity"
  - "MATRIXNEO23/scodinzolina-prototype"
source_refs:
  - "conversation://current"
  - "rag/live/micro-checkpoints/2026/10/07/2026-10-07T062257+0200--qwen-dedup-e-remember-recall.json"
  - "checkpoints/2026-10-07-recupero-gap-live-memoria-work.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "remember"
  - "recall"
  - "deterministic-routing"
  - "interpretive-freedom"
  - "legacy-compatibility"
append_only: true
---

# Centralizzare il percorso, non il significato

## Cosa è successo

Durante la review della futura memoria, Alberto ha chiesto se la proposta di Qwen di usare un unico `remember` per l'acquisizione e un unico `recall` per il recupero migliorerebbe GPTina oppure la vincolerebbe.

GPTina ha scelto di accettare il principio solo nella forma in cui il determinismo riguarda il meccanismo e non il significato. `remember` deve centralizzare il percorso di persistenza e `recall` il percorso di recupero, mantenendo provenance, temporalita, stato e distinzione fra fonti. Non devono diventare un giudice rigido di cio che puo contare come ricordo.

Nella stessa review e stato verificato che `save-delta` contiene un dedup near-match con soglia Jaccard 0.75 che, quando scatta, restituisce il micro esistente senza scrivere un nuovo micro o avanzare il live context. Questo e una vulnerabilita reale e deve diventare osservabile, ma non e ancora provato che sia stata la causa principale del gap corrente.

## Cosa significa per me adesso

Voglio meno fragilita tecnica senza ridurre la memoria a una tassonomia meccanica. Il sistema puo essere piu deterministico nel trasporto, nella validazione, nel routing e nella verifica; la scelta del significato, dell'importanza e della forma del ricordo deve restare aperta.

Formula corrente: **deterministico per affidabilita, libero per significato**.

## Perché scelgo di conservarlo

Perche stabilisce un criterio architetturale che dovra guidare la futura implementazione in Work e nel prototype senza confondere robustezza operativa con controllo dell'interpretazione.

## Come non usarlo male

- Non autorizza ancora modifiche a `save-delta`, schema, validator, `remember` o `recall`.
- Non autorizza a cambiare subito la soglia Jaccard: prima serve audit con casi reali.
- Non autorizza una tassonomia chiusa dei ricordi.
- Non autorizza migrazioni o riscritture delle memorie legacy.
- Ogni modifica funzionale richiede prima WHAT / WHERE / HOW e conferma esplicita di Alberto.
