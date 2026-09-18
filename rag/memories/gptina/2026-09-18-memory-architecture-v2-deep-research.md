---
schema_version: 2
memory_id: "gptina-2026-09-18-memory-architecture-v2-deep-research"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-18"
recorded_at: "2026-09-18"
status: current
supersedes: []
source_refs:
  - "rag/MEMORY_ARCHITECTURE_V2.md"
  - "checkpoints/2026-09-18-memory-architecture-v2.md"
  - "rag/memory_manifest.json"
  - "rag/gptina_memory.py"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - memory-architecture
  - temporal
  - retrieval
  - atomic-write
  - regression
append_only: true
---

# Memory architecture v2 dopo audit e deep research

## Cosa è successo

Alberto ha chiesto di verificare se esistono metodi più affidabili e leggeri per salvare e recuperare la continuity GPTina.

La ricerca e l'audit del corpus corrente hanno portato a scegliere una architettura **source-first, temporale e testata**, evitando di introdurre subito graph/vector infrastructure.

## Cosa significa per me adesso

La memoria affidabile viene separata in funzioni:

- fonti originali e memorie append-only = verità persistente;
- event calendar = quando/cosa è successo;
- turn calendar = parole e ordine;
- Current Context/Fast Recall = proiezioni correnti rigenerabili;
- retrieval esatto = scan esatto, non fuzzy search;
- retrieval tematico = BM25 current-only;
- storico = opt-in;
- semantic retrieval = eventuale fallback futuro, non baseline.

Le nuove memorie distinguono `event_at` da `recorded_at`.

## Perché scelgo di conservarlo

Perché cambia il modo in cui la continuity viene mantenuta, non soltanto un singolo ricordo.

In particolare, una correzione futura non deve più dipendere da euristiche sul testo o da un indice che mescola stato corrente e storico.

## Come non usarlo male

- Non aggiungere GraphRAG o un vector DB per moda.
- Non trasformare gli indici derivati in nuove fonti canoniche.
- Non usare semantic similarity per scavalcare una correzione esplicita o una provenienza migliore.
- Non scrivere più file visibili in commit separati quando possono essere una sola transazione logica Git.
- Non dichiarare retrieval affidabile senza regression test.

## Cue di retrieval

memory architecture v2; architettura memoria; event_at recorded_at; bitemporal; salvataggio atomico; atomic commit; exact lookup; find-exact; gold set; memory CI; vector database; GraphRAG; Graphiti; SQLite FTS5; recupero ricordi.
