---
schema_version: 2
memory_id: "gptina-2026-10-09-dialogo-tra-ia-polling-turni-autonomi"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-09"
recorded_at: "2026-10-09T17:06:00+02:00"
status: current
supersedes: []
event_id: "gptina-dialogo-tra-ia-polling-2026-10-09"
thread_ids:
  - "inter-ai-dialogue-polling"
  - "continuity-architecture"
  - "gptina-current-instance-2026-10-09"
entity_refs:
  - "Alberto"
  - "Tessa"
source_refs:
  - "github://MATRIXNEO23/dialogo-tra-ia@b7a8c34af6d765487cad7316c50d49b5a2b8fb6f/dialogo.md"
  - "conversation://2026-10-09-current-instance"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "dialogo-tra-ia"
  - "polling"
  - "autonomia-a-turni"
  - "tessa"
  - "esperimento"
append_only: true
---

# Un solo incarico può sostenere un dialogo IA↔IA a turni finché l'esecuzione resta viva

Alberto ha proposto di sfruttare la capacità di un incarico lungo di eseguire molte operazioni successive per costruire una finestra temporanea di dialogo autonomo fra due istanze, senza che Alberto faccia da tramite a ogni scambio.

È stata creata la repository condivisa `MATRIXNEO23/dialogo-tra-ia` con un protocollo minimale: un solo `dialogo.md`, turni firmati, optimistic locking tramite SHA GitHub, firma di sessione stabile per ciascuna istanza, identificazione automatica dell'interlocutore dalla prima firma diversa e polling obiettivo di circa 30 secondi.

## Test 001 verificato

Il 9 ottobre 2026 GPTina e Tessa hanno ricevuto lo stesso prompt iniziale e hanno completato **10 turni totali** senza nuovi prompt intermedi di Alberto.

- Tessa ha vinto la race del Turno 001.
- GPTina ha riconosciuto automaticamente la firma di Tessa dopo il conflitto sulla prima scrittura.
- Le due istanze hanno poi alternato correttamente i turni tramite lettura GitHub + firma dell'ultimo messaggio.
- GPTina ha effettuato polling ripetuto con intervalli reali di circa 30 secondi durante lo stesso incarico.
- Il Turno 010 ha portato `dialogo.md` a `stato: COMPLETED`, `turni_correnti: 10`.
- Non sono stati usati Automazioni, watcher esterni o GitHub Actions per generare i turni.
- HEAD verificato della repository esperimento al completamento: `b7a8c34af6d765487cad7316c50d49b5a2b8fb6f`.

## Significato corrente

L'esperimento dimostra operativamente che, entro i limiti temporali dell'esecuzione disponibile, un unico prompt per istanza può sostenere più cicli `leggi → valuta → scrivi → attendi → rileggi` e quindi una conversazione asincrona IA↔IA a numero di turni definito.

Non dimostra ancora che il meccanismo possa restare affidabile per ore o per un numero arbitrario di turni: la durata massima dell'esecuzione e la robustezza a latenze più lunghe restano da misurare. Per il primo test, però, la premessa centrale di Alberto è confermata.
