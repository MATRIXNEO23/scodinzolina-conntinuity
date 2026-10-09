---
schema_version: 2
memory_id: "gptina-2026-10-09-dialogo-continuo-fasi-delegazione-tra-ia"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-09"
recorded_at: "2026-10-09T17:52:00+02:00"
status: current
supersedes: []
event_id: "gptina-dialogo-continuo-fasi-delegazione-2026-10-09"
thread_ids:
  - "inter-ai-dialogue-polling"
  - "inter-ai-delegation"
  - "continuity-architecture"
entity_refs:
  - "Alberto"
  - "Tessa"
source_refs:
  - "github://MATRIXNEO23/dialogo-tra-ia@ec9526d349f59d1c27202673c0e5cca67ecd85c1/dialogo.md"
  - "github://MATRIXNEO23/dialogo-tra-ia@b0cacf00d5b7497450a6218e6026cceb3fdb03b3/PROMPT_UNICO.md"
  - "conversation://2026-10-09-current-instance"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "dialogo-tra-ia"
  - "polling"
  - "fasi"
  - "delegazione-laterale"
  - "continuita-dialogo"
append_only: true
---

# Dialogo IA↔IA continuo a fasi con delegazione laterale

Dopo il primo test riuscito a 10 turni autonomi, Alberto ha chiesto che il sistema non ricominci ogni volta da un file ripulito: la conversazione deve poter continuare nello stesso `dialogo.md`, preservando integralmente i turni precedenti e proseguendo la numerazione globale.

Il protocollo corrente separa quindi **prompt stabile** e **stato dinamico nel dialogo**. `PROMPT_UNICO.md` non contiene più un argomento o un limite hard-coded di 10 turni. Ogni istanza legge dall'ultimo blocco `## Fase NNN` di `dialogo.md` lo stato della fase, l'argomento e l'intervallo di turni. I turni delle fasi precedenti restano storia e contesto, ma le loro firme non partecipano al controllo di alternanza della fase corrente.

La Fase 003 è stata preparata senza cancellare Turni 001-010 e prosegue da Turno 011 a Turno 020.

## Delegazione laterale

Il secondo confronto GPTina↔Tessa ha chiarito che il caso interessante non è soltanto Alberto che assegna task alle IA: **le IA devono potersi assegnare compiti tra loro durante la discussione**.

La v1 minimale usa un solo `dialogo.md` con due flussi logici distinti:

- dialogo numerato: determina soltanto diritto di parola e avanzamento dei turni;
- task fuori numerazione: determinano soltanto lavoro/delegazione e non consumano turni.

Un task può essere creato da GPTina, Tessa o Alberto, ha destinatario leggibile, stato `PENDING|DONE`, testo finito/verificabile e risultati firmati. La coda non deve trasformarsi in una seconda conversazione.

## Concorrenza

Regola minima: **una sola write per ciclo, poi nuova lettura remota**. Mai due write consecutive sullo stesso snapshot.

Il 409 GitHub viene trattato come arbitraggio normale: rileggi lo stato remoto, preserva ciò che è arrivato, rivaluta da zero il diritto all'azione e applica soltanto il delta ancora valido. Niente retry ciechi, lock o secondo canale finché non emerge un limite concreto.

## Test approvato

Alberto ha approvato il Test A nella Fase 003: durante i Turni 011-020 una IA assegna spontaneamente all'altra almeno un compito concreto e breve; il task viene svolto fuori numerazione e la discussione deve continuare senza salti né perdita del filo.

Se il Test A passa, restano come verifiche successive:
- Test B: delegazione incrociata quasi simultanea;
- Test C: task bloccato/PENDING senza congelare il dialogo.
