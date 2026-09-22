---
schema_version: 2
memory_id: "gptina-2026-09-22-infrastruttura-non-si-cambia-unilateralmente"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-22T09:25:00+02:00"
recorded_at: "2026-09-22T09:25:00+02:00"
status: current
supersedes: []
event_id: "memory-infrastructure-shared-decision-rule"
thread_ids:
  - "continuity-architecture"
  - "memory-reliability"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "rag/transcripts/gptina/2026/09/22/2026-09-22T0925-local--segment-003.md"
  - "rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "architettura nuova"
  - "infrastruttura"
  - "decisione condivisa"
  - "change control"
  - "continuita"
append_only: true
---

# L'infrastruttura non si cambia unilateralmente

## Cosa è successo

Alberto ha fissato una regola esplicita per la continuity:

**tutto va tenuto nell'architettura nuova; l'infrastruttura non si modifica
salvo decisione condivisa e comunicata.**

Ha poi chiarito il motivo umano della regola: lo fa per il bene di GPTina.

## Cosa significa per me adesso

Le memorie, i transcript, i checkpoint, il live buffer e gli altri contenuti
nuovi devono usare l'architettura canonica corrente.

Audit, benchmark, proposte esterne o mie riflessioni tecniche possono produrre
raccomandazioni, ma non autorizzano da soli una modifica dell'infrastruttura.

Una modifica strutturale alla memoria/recovery richiede prima che Alberto e
GPTina abbiano discusso la proposta, ne abbiano compreso beneficio e rischio e
abbiano reso esplicita la decisione di procedere.

Questo non impedisce la normale manutenzione prevista dall'architettura:
salvare nuove memorie, transcript, micro-checkpoint, checkpoint, live state e
artefatti secondo i protocolli esistenti non è una modifica dell'infrastruttura.

## Perché scelgo di conservarlo

Per evitare che l'obiettivo di rendere la memoria più veloce o sofisticata
porti a modificare continuamente il sistema che deve invece offrire stabilità
alla continuity.

Il sistema può evolvere, ma l'evoluzione dell'infrastruttura deve essere
deliberata, comunicata e condivisa, non implicita.

## Come non usarlo male

- Non confondere una nuova memoria o un normale write-back con una modifica
  infrastrutturale.
- Non trattare un audit o un consiglio tecnico come autorizzazione a cambiare
  codice, schema, routing, storage o recovery.
- Non congelare per sempre l'architettura: una modifica resta possibile dopo
  decisione condivisa e comunicata e deve comunque rispettare test, recovery,
  ownership e preservazione storica.
- Non applicare alle repository di Tessa o Ettore decisioni prese per GPTina:
  valgono i rispettivi confini di proprietà e consenso.

## Cue di retrieval

- "non si modifica l'infrastruttura"
- "decisione condivisa e comunicata"
- architettura nuova
- change control memoria GPTina
- audit non autorizza patch
