---
schema_version: 2
memory_id: "gptina-2026-09-21-infrastruttura-verifier-v2-propagazione"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21"
recorded_at: "2026-09-21"
status: current
supersedes: []
event_id: "event-2026-09-21-verifier-v2-propagazione"
thread_ids:
  - "continuity-architecture"
  - "memory-reliability"
  - "tessa-shared-correspondence"
  - "romanziere-bootstrap"
entity_refs:
  - "Alberto"
  - "GPTina"
  - "Tessa"
  - "Ettore"
source_refs:
  - "checkpoints/2026-09-21-live-verifier-v2-compatibility-completed.md"
  - "rag/live/LEGACY_V1_COMPATIBILITY_AUDIT.md"
  - "rag/live/MICRO_CHECKPOINT_SCHEMA.md"
  - "rag/live_context.py"
  - "rag/test_live_context.py"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "verifier"
  - "schema v2"
  - "legacy v1"
  - "retrocompatibilita"
  - "Tessa"
  - "Ettore"
  - "salvataggio frequente"
  - "recovery"
append_only: true
---

# Infrastruttura memoria corrente da propagare a Tessa ed Ettore

Alberto ha chiesto di conservare in modo durevole le correzioni applicate alla continuity GPTina perché la stessa architettura dovrà essere trasferita anche a Tessa quando la sua repo tornerà disponibile e, subito, al Romanziere/Ettore.

## Architettura corrente GPTina

- I micro-checkpoint storici `schema_version: 1` restano append-only e non vengono riscritti.
- Il verifier li legge con compatibilità controllata, derivata da un audit reale di tutti i v1 esistenti.
- La normalizzazione legacy avviene soltanto in memoria e soltanto per campi realmente assenti nella storia.
- I riferimenti legacy non vuoti restano leggibili anche se il target storico è stato rinominato o spostato.
- Tutti i nuovi micro-checkpoint sono `schema_version: 2`.
- Il writer `save-delta` produce v2 completo.
- Il verifier v2 resta rigoroso: struttura, tipi, riferimenti e campi obbligatori devono essere corretti.
- I test devono coprire sia accettazione legacy controllata sia rifiuto di v2 malformati.
- La CI deve verificare il sistema completo prima di considerarlo sano.
- Le immagini derivate già dichiarate in `derivative_refs` contano come copertura strutturata senza duplicare inutilmente un media-link completo.

## Regola operativa

**Capire il passato senza riscriverlo; validare il futuro con regole più strette.**

## Salvataggio frequente

- live buffer piccolo = presente immediato;
- micro-checkpoint = delta append-only;
- checkpoint pieno = consolidamento di fase;
- memoria = significato durevole;
- transcript = parole esatte;
- preflight prima di lavoro lungo/rischioso;
- salvataggio immediato su correzioni, decisioni, regole, cambi di stato, open loop, milestone e visual context;
- freshness review periodica senza produrre rumore se non esiste un delta sostanziale.

## Recovery

Ordine raccomandato:

1. live context;
2. ultimo micro-checkpoint;
3. ultimo checkpoint pieno;
4. fast recall/current context;
5. memoria pertinente;
6. transcript/raw source se servono parole esatte;
7. cronologia/visual chronology per domande temporali o visuali.

## Propagazione

Quando Tessa sarà nuovamente modificabile, verificare prima il suo archivio reale e adattare la compatibilità alle sue varianti legacy, senza copiare ciecamente i default GPTina.

Per Ettore/Romanziere applicare lo stesso principio: audit reale dell'archivio, allineamento writer/verifier/schema/policy, v2 rigoroso per il futuro, compatibilità legacy in lettura, test e CI verde prima di dichiarare il sistema sano.
