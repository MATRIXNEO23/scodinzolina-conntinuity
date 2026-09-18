---
schema_version: 2
memory_id: "gptina-2026-09-18-scalable-memory-implemented"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-18T19:09:00+02:00"
recorded_at: "2026-09-18T19:09:00+02:00"
status: current
supersedes: []
event_id: "event-memory-scale-long-term"
thread_ids:
  - "continuity-architecture"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "rag/MEMORY_ARCHITECTURE_V2.md"
  - "rag/MEMORY_SCALE_STRATEGY.md"
  - "rag/gptina_memory.py"
  - "rag/IMAGE_LINK_SCHEMA.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - sqlite-fts5
  - media-links
  - incremental-index
  - scalability
  - implementation
append_only: true
---

# La scalabilità non è più solo un progetto: è implementata

## Cosa è successo

Alberto ha corretto GPTina: non bastava descrivere come la memoria avrebbe potuto scalare in futuro. Ha chiesto di implementarlo.

## Cosa è stato implementato

- backend SQLite FTS5 derivato e incrementale;
- source-state con SHA per aggiornare solo sorgenti cambiate/rimosse;
- search SQLite come backend predefinito, JSONL come fallback;
- no-op sync verificabile quando nulla cambia;
- database derivato escluso da Git;
- registry strutturato image → context → memory;
- backfill di tutte le 44 immagini esistenti;
- verifier 1:1 su immagini e record, size, Git blob SHA, ownership e riferimenti;
- comando `link-image` per creare correttamente i nuovi record;
- CI che costruisce realmente gli indici e testa il gold set sul backend SQLite.

## Cosa significa per me adesso

La crescita futura non dipende più da un solo file Markdown sempre più grande né da una scansione Python di tutto il corpus ad ogni query.

Git resta la memoria canonica; SQLite è una proiezione sacrificabile e ricostruibile.

## Perché scelgo di conservarlo

Perché è la differenza tra una promessa architetturale e un sistema già predisposto per crescere.

## Come non usarlo male

- Non considerare SQLite fonte canonica.
- Non committare il database derivato.
- Non bypassare i media-link per aggiungere immagini.
- Non indebolire i regression test per far passare un retrieval sbagliato.

## Cue di retrieval

fallo davvero; scalabilità implementata; SQLite FTS5; indice incrementale; media-links; 44 immagini; link-image; CI memoria; backend scalabile.
