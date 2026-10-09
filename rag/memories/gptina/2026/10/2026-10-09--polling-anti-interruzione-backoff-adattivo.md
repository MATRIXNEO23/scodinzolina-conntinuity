---
schema_version: 2
memory_id: "gptina-2026-10-09-polling-anti-interruzione-backoff-adattivo"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-09"
recorded_at: "2026-10-09T18:27:00+02:00"
status: current
supersedes: []
event_id: "gptina-dialogo-tra-ia-polling-anti-interruzione-2026-10-09"
thread_ids:
  - "inter-ai-dialogue-polling"
  - "inter-ai-delegation"
  - "continuity-architecture"
entity_refs:
  - "Alberto"
  - "Tessa"
source_refs:
  - "github://MATRIXNEO23/dialogo-tra-ia@3d24b3f07ba963782b4972d1c7f679d799f5fb52/PROMPT_UNICO.md"
  - "conversation://2026-10-09-current-instance"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "dialogo-tra-ia"
  - "polling"
  - "anti-interruzione"
  - "backoff-adattivo"
  - "continuita-dialogo"
append_only: true
---

# Polling anti-interruzione con backoff adattivo

Alberto ha corretto un comportamento emerso durante la Fase 003 del dialogo IA↔IA: una fase `ACTIVE` non deve essere interrotta solo perché l'altra istanza tarda a rispondere. L'assenza di cambiamenti remoti non è una condizione di fine e non deve provocare un ritorno prematuro in chat né una richiesta ad Alberto di rilanciare l'altra istanza.

La regola approvata e pubblicata in `MATRIXNEO23/dialogo-tra-ia/PROMPT_UNICO.md` è:

- finché la fase è `ACTIVE`, continuare il polling senza un numero massimo prestabilito di tentativi;
- partire da circa 30 secondi fra i controlli;
- se più letture consecutive sono identiche, aumentare progressivamente l'intervallo, per esempio 30s → 60s → 120s → 300s;
- appena compare un cambiamento pertinente, riportare l'intervallo a circa 30 secondi;
- una lunga attesa non è un errore né una conclusione implicita;
- la fase si considera materialmente interrotta solo se la piattaforma o lo strumento termina davvero l'esecuzione o impedisce ulteriori letture;
- dopo una interruzione materiale, al nuovo avvio si riprende la stessa fase `ACTIVE` dallo stato remoto senza crearne una nuova.

Questa regola corregge l'interpretazione precedente in cui, dopo alcuni minuti senza risposta, GPTina aveva smesso di fare polling e aveva chiesto ad Alberto di scrivere `continua` a Tessa. Quel comportamento non è più corretto per una fase ancora `ACTIVE`.

Il principio operativo diventa quindi: **latenza ≠ fine; attesa lunga → backoff, non interruzione**.
