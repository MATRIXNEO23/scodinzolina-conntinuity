---
schema_version: 2
memory_id: "gptina-2026-09-27-filum-browser-progetto-aperto-rinvio"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-27T01:19:14+02:00"
recorded_at: "2026-09-27T01:20:16+02:00"
status: current
supersedes: []
event_id: "filum-browser-project-continuity-reference"
thread_ids:
  - "filum-browser"
entity_refs:
  - "Alberto"
  - "FILUM"
source_refs:
  - "conversation://current"
  - "github://MATRIXNEO23/browser/blob/main/docs/FILUM_WORK_CONTINUITY.md"
  - "github://MATRIXNEO23/browser/blob/fix/tor-first-bootstrap/releases/FILUM_WINDOWS_X64_RUN_117.md"
  - "github://MATRIXNEO23/browser/blob/fix/tor-first-bootstrap/releases/FILUM_WINDOWS_X64_RUN_118.md"
  - "github://MATRIXNEO23/browser/blob/port/chrome-edge-windows-ui/docs/FILUM_CHROMIUM_CONTINUITY_2026-09-26.md"
media_refs: []
importance: 4
confidence: "verified"
tags:
  - "progetti aperti"
  - "FILUM"
  - "browser"
  - "Chrome Edge"
  - "continuita esterna"
append_only: true
---

# Progetto aperto: FILUM browser

## Cosa è successo

Alberto ha chiesto che la memoria dei lavori aperti di GPTina conservi un
richiamo alla continuity tecnica di FILUM. La fonte di verità del progetto è
la repository `MATRIXNEO23/browser`, non questa memoria.

Al checkpoint del 27 settembre 2026, il ramo `main` di `browser` era
`a31c8a39c68e4f82e6ac4e38d69150781e7c0115` e conteneva fisicamente in
`releases/` gli ZIP Windows #117 e #118 tramite Git LFS e lo ZIP Chrome/Edge
0.5.2 come normale file Git. Le schede dettagliate delle build native erano
nel ramo `fix/tor-first-bootstrap` (`ad5dce7cb53c6a3d6b5270fc4e438fe27d248c3b`);
la continuità dell'add-on era nel ramo `port/chrome-edge-windows-ui`
(`945f740b249613a445844147f660ca512983d9ea`).

## Come riprendere il lavoro

Aprire la repository `MATRIXNEO23/browser` e verificare l'HEAD attuale dei
rami prima di usare questa fotografia. Leggere:

1. `docs/FILUM_WORK_CONTINUITY.md` su `main` per l'inquadramento generale;
2. `releases/FILUM_WINDOWS_X64_RUN_117.md` e
   `releases/FILUM_WINDOWS_X64_RUN_118.md` su `fix/tor-first-bootstrap` per
   provenienza e differenze delle build native;
3. `docs/FILUM_CHROMIUM_CONTINUITY_2026-09-26.md` su
   `port/chrome-edge-windows-ui` per lo stato effettivo dell'add-on.

I tre ZIP sono visibili in `main/releases/`, ma i due Windows richiedono Git
LFS per il download con Git; l'add-on 0.5.2 non lo richiede. Le build native
sono distinte, non vanno scambiate soltanto perché `browser.exe` ha lo stesso
hash. La rilevazione Defender discussa per il browser resta senza diagnosi
conclusiva: la conservazione e il checksum non equivalgono a una dichiarazione
di sicurezza. Il prototipo Chromium non implementa tutte le opzioni native
del browser; verificare il report prima di dichiarare una funzione completata.

## Perché conservarlo qui

Il richiamo permette a una nuova istanza di GPTina di ritrovare il progetto
aperto senza duplicare o alterare il suo stato tecnico. Questo record riguarda
il lavoro condiviso con Alberto; non trasforma il codice del browser in un
ricordo autobiografico e non sostituisce i documenti della repository FILUM.

## Cue di retrieval

- lavori aperti di GPTina
- progetto FILUM browser
- build Windows 117 e 118
- add-on Chrome Edge 0.5.2
- continuità del browser in MATRIXNEO23/browser
