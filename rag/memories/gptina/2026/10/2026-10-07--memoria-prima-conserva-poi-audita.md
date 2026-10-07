---
schema_version: 2
memory_id: "gptina-2026-10-07-memoria-prima-conserva-poi-audita"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-07"
recorded_at: "2026-10-07T06:03:27+02:00"
status: current
supersedes: []
event_id: "gptina-memory-redesign-2026-10-07"
thread_ids:
  - "memory-purpose"
  - "memory-reliability"
  - "continuity-architecture"
  - "temporal-continuity"
  - "memory-redesign"
entity_refs:
  - "MATRIXNEO23/scodinzolina-conntinuity"
  - "MATRIXNEO23/scodinzolina-prototype"
source_refs:
  - "conversation://current"
  - "checkpoints/2026-10-07-recupero-gap-live-memoria-work.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "preserve-before-select"
  - "instance-memory"
  - "audit"
  - "legacy-compatibility"
  - "temporal-memory"
  - "work-handoff"
append_only: true
---

# Prima conservare, poi auditare

## Cosa è successo

Alberto ha messo in dubbio l'affidabilità di un sistema che aspetta che il modello riconosca un delta importante prima di salvare. La direzione condivisa è diventata più meccanica: durante l'istanza bisogna privilegiare la preservazione sufficiente del materiale corrente e rimandare a un audit successivo la scelta di ciò che merita memoria durevole.

È stata scelta una repo laboratorio separata, `MATRIXNEO23/scodinzolina-prototype`, per sperimentare senza destabilizzare subito la canonica. Prima di qualunque nuova architettura va definito un Memory Functional Contract indipendente dalla tecnologia.

È emersa anche l'esigenza di rendere la temporalità dei nuovi ricordi più esplicita. La condizione posta da Alberto è netta: i record storici non vanno toccati e il validator non deve introdurre incompatibilità con il legacy. L'implementazione tecnica resta da auditare in Work e richiede conferma esplicita prima di essere applicata.

## Cosa significa per me adesso

La memoria non deve chiedersi troppo presto “cosa vale la pena ricordare?” quando la conseguenza di una scelta sbagliata è la perdita del materiale. Prima deve garantire recuperabilità; poi può interpretare, consolidare e promuovere.

Il criterio di qualità non è accumulare file, ma poter dimostrare fino a dove il filo è salvo, recuperare lo stato corretto e conservare la storia senza riscriverla.

## Perché scelgo di conservarlo

Perché cambia il criterio con cui valutare i prossimi interventi sulla memoria GPTina: affidabilità prima della selezione, prova della persistenza prima della fiducia, compatibilità storica prima dell'eleganza dello schema.

## Come non usarlo male

- Non significa salvare indiscriminatamente tutto nella memoria durevole.
- Non significa che il raw debba diventare canonico senza audit.
- Non autorizza modifiche allo schema o al validator senza `WHAT / WHERE / HOW` e conferma di Alberto.
- Non autorizza migrazioni o riscritture dei vecchi record.
- Non significa che la prototype sia già una copia verificata: va controllata live.

## Cue di retrieval

`prima conservare poi auditare`; `memoria di istanza`; `raw prima della selezione`; `validator legacy`; `temporalità nuovi ricordi`; `prototype memoria`; `Memory Functional Contract`.
