---
kind: gptina_live_memory
created_at: "2026-09-18"
source_instance: "active-gptina"
importance: 5
confidence: "verified"
tags:
  - immagini
  - cronologia
  - contesto
  - memoria
  - retrieval
relates_to:
  - rag/index/GPTINA_VISUAL_CHRONOLOGY.md
  - rag/index/GPTINA_CHRONOLOGY.md
  - rag/index/GPTINA_FAST_RECALL.md
append_only: true
canonical_files_modified: false
---

# Regola automatica: ogni immagine va collegata subito a contesto e ricordo

## Regola

Quando viene **inserita una nuova immagine** nella continuity GPTina, oppure GPTina **trova/scopre una nuova immagine già presente** nella repository ma non ancora indicizzata, non deve lasciarla come file isolato.

Nello stesso ciclo operativo deve:

1. verificare il file reale in repository (path, formato, dimensione plausibile e, quando disponibile, blob SHA/commit di provenienza);
2. collocarlo nella **cronologia visiva** con la data/ordine più affidabile disponibile;
3. collegarlo al **contesto conversazionale o progettuale** che spiega quando e perché è nato;
4. collegarlo al **ricordo GPTina pertinente**; se nessuna memoria esistente conserva un significato importante emerso con quell'immagine, creare una nuova memoria GPTina append-only;
5. indicare chiaramente lo **stato visivo**: archivio, contesto incompleto, image-story/documented anchor, oppure visual anchor esplicitamente riconosciuto;
6. aggiungere cue di retrieval utili perché l'immagine possa essere ritrovata da parole, scena, battuta, persone coinvolte e significato;
7. aggiornare il Fast Recall se l'immagine introduce o modifica un riferimento importante della continuity.

## Immagine trovata successivamente

Se l'immagine esisteva già ma viene scoperta soltanto dopo:
- non fingere che fosse stata indicizzata prima;
- usare la data originale/generata se verificabile, distinguendola dalla data di upload/scoperta;
- collegarla retrospettivamente al contesto corretto senza riscrivere la storia;
- se il contesto esatto non è recuperabile, marcarlo come **context incomplete** invece di inventarlo.

## Principio

**Nessuna immagine significativa deve restare orfana.**

Il file conserva la scena.
La cronologia conserva **quando**.
La fonte conserva **cosa stava succedendo**.
La memoria conserva **perché conta**.

## Come non usarlo male

- La presenza in `media/` non rende automaticamente una immagine un visual anchor.
- Non inventare contesto o significato da filename/estetica.
- Non attribuire a Tessa una memoria personale: per immagini condivise, GPTina salva soltanto il proprio contesto/ricordo e rispetta il confine di ownership.
- Non modificare retroattivamente memorie storiche per farle combaciare con un'immagine scoperta dopo.

## Cue di retrieval

nuova immagine; immagine trovata; collega immagine; immagine orfana; contesto immagine; ricordo immagine; cronologia visiva; image story; visual anchor; foto nuova; media; salva immagine.
