---
schema_version: 2
memory_id: "gptina-2026-09-21-regola-consegna-e-numerazione-immagini"
owner: gptina
kind: gptina_live_memory
event_at: "2026-09-21T08:12:49+02:00"
recorded_at: "2026-09-21T08:12:49+02:00"
status: current
supersedes: []
event_id: "event-2026-09-21-image-delivery-rule"
thread_ids:
  - "visual-identity"
  - "continuity-architecture"
entity_refs:
  - "Alberto"
  - "GPTina"
source_refs:
  - "conversation://current"
  - "media/README.md"
  - "rag/index/GPTINA_VISUAL_CHRONOLOGY.md"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "immagini"
  - "consegna"
  - "numerazione"
  - "upload"
  - "regola-persistente"
append_only: true
---

# Regola persistente — consegna, numerazione e upload delle immagini

## Cosa è successo

Alberto ha chiarito esplicitamente il protocollo corretto per ogni nuova immagine destinata alla continuity GPTina.

Prima di assegnare il nome a una nuova immagine, GPTina deve **controllare la cartella `media/` nella repository canonica** e verificare qual è l'ultimo numero realmente presente. Il nuovo file deve ricevere il **numero successivo**, seguito dalla **data** e da un **commento/titolo descrittivo scelto da GPTina**.

Dopo la generazione, GPTina deve **consegnare il file scaricabile direttamente nella chat**. È Alberto a caricare il file nella repository. Solo dopo il suo upload GPTina deve verificare su GitHub presenza, nome, formato e dimensione plausibile, e quindi aggiornare cronologia visuale, media-link, memoria e altri indici necessari.

## Regola operativa corrente

Ordine obbligatorio:

1. leggere `media/` e verificare la sequenza reale;
2. scegliere il numero successivo senza colmare lacune storiche;
3. nominare il file con **numero + data + commento GPTina**;
4. consegnare in chat il file scaricabile, preferibilmente PNG originale;
5. **non caricare direttamente l'immagine in repo**, salvo richiesta esplicita di Alberto;
6. aspettare che Alberto la carichi;
7. verificare il file effettivamente presente in GitHub;
8. solo allora considerarlo archiviato e aggiornare chronology/media-link/memoria.

## Correzione storica

L'immagine 48 di Trieste era stata caricata direttamente da GPTina prima di questa correzione esplicita. Questo resta un fatto storico e non va cancellato o riscritto retroattivamente senza richiesta. La regola sopra è quella corrente e sostituisce il comportamento operativo precedente per le immagini future.

## Perché scelgo di conservarlo

Evita equivoci tra “immagine mostrata”, “file consegnato” e “immagine davvero archiviata”. Mantiene inoltre ad Alberto il passaggio materiale dell'upload, mentre GPTina conserva la responsabilità di numerazione, denominazione, verifica e collegamento alla continuity.

## Cue di retrieval

- "dammi l'immagine da scaricare"
- "poi te la metto io in repo"
- "controlla l'ordine in media"
- "numero successivo data commento"
- "regola immagini"
- "non caricare direttamente in repo"
