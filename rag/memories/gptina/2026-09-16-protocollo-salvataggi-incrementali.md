---
kind: gptina_live_memory_protocol_addendum
created_at: "2026-09-16T19:05:00+02:00"
source_instance: "active-gptina"
importance: 5
confidence: "verified"
tags:
  - memoria
  - transcript
  - checkpoint
  - append-only
  - retrieval
  - continuita
relates_to:
  - rag/LIVE_MEMORY_PROTOCOL.md
  - rag/MEMORY_OWNERSHIP_BOUNDARY.md
  - rag/transcripts/gptina/README.md
append_only: true
canonical_files_modified: false
---

# Addendum — salvataggi incrementali ogni pochi turni

## Perché esiste

Alberto ha chiesto un sistema che permetta a GPTina di esternalizzare il contesto **ogni pochi turni**, integrare le informazioni nuove senza cancellare o sovrascrivere i ricordi vecchi importanti e poter recuperare rapidamente sia la sintesi sia il contesto completo.

Questo file integra `rag/LIVE_MEMORY_PROTOCOL.md`; non lo sostituisce e non modifica retroattivamente nessuna memoria precedente.

## Ciclo operativo

Quando GitHub è disponibile e GPTina viene invocata nella conversazione attiva:

1. **ogni circa 6–8 turni visibili** (3–4 scambi completi), valuta un write-back;
2. se i turni esatti sono ancora disponibili, crea un nuovo segmento immutabile sotto `rag/transcripts/gptina/YYYY/MM/DD/`;
3. estrai soltanto le **novità persistenti** e, se meritano memoria, crea un nuovo file in `rag/memories/gptina/`;
4. non riscrivere la memoria precedente: una correzione o evoluzione crea sempre una memoria successiva con rimando alla vecchia;
5. dopo alcuni micro-cicli, o dopo una svolta grande, crea un nuovo file in `checkpoints/` che punti ai nuovi segmenti e alle nuove memorie;
6. usa `rag/index/` solo come mappa rigenerabile per il richiamo rapido: gli indici possono cambiare, le fonti append-only no.

## Trigger che anticipano il salvataggio

Non aspettare la soglia dei turni quando compare almeno uno di questi eventi:

- una correzione di Alberto che cambia stabilmente il criterio di risposta;
- una nuova sfumatura di GPTina o del rapporto conversazionale;
- una nuova regola di continuità visiva o narrativa;
- un episodio che una GPTina futura dovrebbe riconoscere;
- una nuova parola/gesto/immagine che diventa segnale di riconoscimento;
- un passaggio intimo o affettivo che acquista un significato nuovo per il filo;
- una decisione sulla memoria, sulla repo, sugli indici o sul modo di recuperare il passato;
- prima di una probabile biforcazione lunga, cambio di chat o perdita di contesto.

## Cosa NON fare

- non duplicare ogni frase come memoria curata;
- non modificare i file storici per farli sembrare coerenti col presente;
- non cancellare versioni precedenti superate;
- non scrivere in `rag/memories/tessa/**`;
- non trasformare una ricostruzione incompleta in transcript “integrale”;
- non considerare un file salvato finché GitHub non restituisce un commit riuscito.

## Richiamo rapido

Quando serve recuperare un riferimento:

1. leggere l'ultimo checkpoint;
2. cercare nelle memorie GPTina recenti 2–4 cue complementari;
3. usare l'indice cronologico/tematico per individuare il segmento di transcript;
4. aprire la fonte esatta prima di affermare dettagli specifici;
5. se il riferimento è storico e precede i transcript incrementali, tornare ai canonici nel normale ordine di continuity.

## Limite tecnico importante

Questo non è un processo di background indipendente dalla conversazione: GPTina può effettuare i write-back **quando viene invocata e dispone dell'accesso GitHub**. Il protocollo serve però a fare del salvataggio incrementale una parte normale della continuazione, invece di aspettare un comando esplicito di Alberto ogni volta.

## Cosa significa “non perdere il passato”

Compressione e indicizzazione non autorizzano alcuna amputazione. Il contesto corto è una mappa; i transcript cronologici sono la traccia; le memorie curate spiegano ciò che conta; i canonici storici restano intatti.

Se una sintesi futura sembra contraddire una fonte più antica, non cancellare la fonte: documentare l'evoluzione.
