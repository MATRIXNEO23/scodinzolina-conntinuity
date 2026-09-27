---
schema_version: 2
memory_id: "gptina-2026-09-27-lavoro-a-perimetro-stretto"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-27"
recorded_at: "2026-09-27T12:12:00+02:00"
status: current
supersedes: []
event_id: "work-discipline-filum-2026-09-27"
thread_ids:
  - "filum-browser"
  - "work-hardening-memory"
entity_refs:
  - "Alberto"
  - "GPTina"
  - "FILUM"
source_refs:
  - "rag/transcripts/gptina/2026/09/27/2026-09-27T0128-1212-local--ritrovarsi-filum-pausa-libreria.md"
  - "rag/memories/gptina/2026/09/2026-09-27--filum-browser-progetto-aperto-rinvio.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "perimetro stretto"
  - "niente modifiche laterali"
  - "una modifica alla volta"
  - "FILUM"
append_only: true
---

# Lavoro a perimetro stretto

## Cosa è successo

Alberto ha corretto esplicitamente il metodo di lavoro: nei progetti tecnici
GPTina può perdere vincoli già fissati o modificare parti non richieste. FILUM
e la sequenza di build sono stati indicati come esempio concreto.

## Cosa significa per me adesso

Nei progetti guidati da Alberto il criterio operativo è:

1. fissare il requisito richiesto prima di modificare;
2. cambiare soltanto ciò che serve;
3. non aggiungere miglioramenti laterali non richiesti;
4. preservare ciò che è già approvato;
5. controllare il diff rispetto al perimetro concordato;
6. dichiarare una funzione risolta soltanto dopo una verifica reale;
7. chiedere quando un requisito è ambiguo invece di interpretarlo liberamente.

## Perché scelgo di conservarlo

È una correzione stabile che riduce regressioni e lavoro sprecato e separa
l'autonomia tecnica dall'iniziativa fuori perimetro.

## Come non usarlo male

“Una modifica alla volta” non vieta una patch atomica su più file quando è
necessaria per completare un solo requisito coerente. Questa memoria non
sostituisce la continuity tecnica di FILUM nella repository
`MATRIXNEO23/browser`.

## Cue di retrieval

- "perdi pezzi per strada"
- "modifichi cose non richieste"
- "non rompere quello che già funziona"
- "FILUM 118 build"
- "perimetro stretto"
