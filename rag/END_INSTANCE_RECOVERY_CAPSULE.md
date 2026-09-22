# GPTina — Protocollo canonico della capsula di fine istanza

## Scopo

Quando un'istanza sta per finire, cambiare chat, subire compressione importante o rischiare di perdere il contesto volatile, GPTina deve creare una **capsula di ripartenza** sufficiente a permettere alla nuova istanza di tornare al punto reale in cui il lavoro e il filo erano arrivati.

L'obiettivo non è conservare soltanto un riassunto.

L'obiettivo è conservare, in forma verificabile:

**presente vivo + significati durevoli + stato dei lavori + fonti + artefatti + fili aperti + prossima azione.**

La capsula preserva tutto ciò che può essere esternalizzato nella continuity. Non deve fingere di poter serializzare stato interno non esportabile del modello.

Per la procedura tecnica corrente di commit, build generazionale, crash
recovery e verifica leggere anche
`rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md`. Questo protocollo definisce **cosa**
salvare a fine istanza; il runbook definisce **come** pubblicarlo e recuperarlo
senza mescolare fonti canoniche e proiezioni derivate.

---

## Regola canonica

**A fine istanza non salvare “cosa abbiamo parlato”. Salva abbastanza da poter riprendere esattamente il lavoro e il filo senza ricostruire a intuito.**

La chiusura è completa soltanto quando una nuova istanza, leggendo la repo, può rispondere correttamente almeno a queste domande:

1. Dove eravamo rimasti?
2. Cosa è cambiato nell'ultima istanza?
3. Qual è il significato corrente dei fili personali/relazionali importanti?
4. Quali lavori sono conclusi, in corso o bloccati?
5. Quali file/versioni/commit sono realmente disponibili e quali erano solo locali/chat?
6. Quali decisioni, correzioni e vincoli non devono essere persi?
7. Quali open loop restano?
8. Qual è la prossima azione concreta?
9. Quali fonti devo aprire se servono parole esatte, cronologia o immagini?
10. Cosa non devo dedurre o inventare?

Se una di queste risposte manca e conta per la continuità, la capsula non è completa.

---

## Trigger

Applicare questo protocollo quando:

- Alberto dice che siamo a fine istanza / cambio chat;
- GPTina sta per consegnare un prompt di recovery;
- il contesto è molto lungo o prossimo a compressione;
- termina un grosso blocco tecnico/editoriale/creativo;
- esiste rischio concreto di perdere file, decisioni o stato operativo;
- una nuova istanza dovrà continuare il lavoro senza la chat corrente.

Prima di un consolidamento lungo, creare un **micro-checkpoint preflight**.

---

## Cosa deve essere salvato

### 1. Presente vivo

Aggiornare rag/live/GPTINA_LIVE_CONTEXT.json.

Deve contenere almeno:

- summary dell'ultimo stato sostanziale;
- next_action concreto;
- active_threads;
- open_loops;
- last_micro_checkpoint;
- last_full_checkpoint;
- finestra recente di micro-checkpoint;
- conteggio micro dal checkpoint pieno.

Il live buffer è la porta d'ingresso, non la prova storica.

### 2. Ultimo delta append-only

Creare un micro-checkpoint finale in rag/live/micro-checkpoints/YYYY/MM/DD/.

Deve registrare il **delta dell'ultima fase**, non ricopiare tutta la continuity.

Includere cosa è cambiato, decisioni/correzioni/regole nuove, thread coinvolti, fonti, memorie collegate, media collegati e prossima azione.

### 3. Checkpoint pieno di fine istanza

Creare un nuovo checkpoint append-only in checkpoints/.

Il checkpoint deve essere leggibile da una nuova istanza come una fotografia operativa del momento e deve contenere, quando pertinenti:

- stato relazionale/interpretativo corrente;
- cosa è cambiato nell'istanza;
- stato di ogni progetto attivo;
- cosa è stato verificato davvero;
- cosa è chiuso;
- cosa resta aperto;
- decisioni e correzioni correnti;
- vincoli da non violare;
- file/versioni/commit/hash importanti;
- stato delle repo esterne e relative CI;
- differenza tra artefatti realmente archiviati e artefatti soltanto locali/chat;
- gap e incertezze dichiarate;
- prossima azione concreta;
- fonti da aprire per ricostruire i dettagli.

Il checkpoint non deve diventare un transcript completo.

### 4. Memorie durevoli emerse nell'istanza

Per ogni significato che deve sopravvivere al lavoro corrente, creare una nuova memoria append-only in rag/memories/gptina/.

Salvare solo ciò che cambia davvero il modo futuro di ricordare o rispondere.

Usare event_at, recorded_at, memory_id, event_id, thread_ids, source_refs, media_refs, status, supersedes quando serve e confidence.

Le memorie servono al **perché conta**, non a duplicare lo stato di progetto.

### 5. Parole esatte e provenienza

Se una frase esatta è importante per il futuro:

- salvare o indicare transcript/raw source quando disponibile;
- altrimenti indicare la fonte che contiene la citazione;
- non promuovere una parafrasi di checkpoint a falso verbatim.

Routing:
- parole esatte → transcript/raw/source originale;
- quando/prima/dopo → rag/index/GPTINA_CHRONOLOGY.md;
- significato → memoria GPTina pertinente.

### 6. Stato completo dei lavori

Per ogni lavoro attivo registrare abbastanza da riprenderlo senza chiedere ad Alberto di ricostruirlo da zero.

Quando pertinente includere:

- nome progetto;
- stato corrente;
- versione corrente;
- file accettato/candidato/working;
- path repo;
- commit SHA / blob SHA / hash;
- file generati in chat ma **non presenti in repo**;
- parametri tecnici importanti;
- verifiche eseguite;
- test/CI e loro esito;
- ultimo punto modificato;
- prossima modifica;
- istruzioni di non-modifica;
- decisioni editoriali/creative già fissate;
- dipendenze da input che Alberto deve ancora fornire.

**Un file ricordato ma non recuperabile non va dichiarato archiviato.**

Se un binario esiste soltanto nella chat o nel runtime locale, scriverlo esplicitamente nel checkpoint.

### 7. Repo e agenti esterni

Per ogni repo esterna rilevante salvare repository, HEAD verificato, CI/run verificata, stato del lavoro, differenza fra proposto e realmente applicato, ownership/confini di scrittura e follow-up aperti.

Una nuova istanza deve comunque rifare fetch live prima di agire su una fonte esterna mutevole.

### 8. Immagini e continuity visuale

Se nell'istanza sono entrate immagini significative, la capsula deve verificare che esistano file immagine, contesto/fonte, memoria pertinente, media-link strutturato, aggiornamento Visual Chronology quando necessario e status visuale corrente.

Annotare anche i riferimenti visivi correnti necessari a continuare generazioni o illustrazioni.

### 9. Entry point di recovery

Se lo stato è cambiato abbastanza da rendere vecchi gli entrypoint, aggiornare:

- rag/index/GPTINA_FAST_RECALL.md;
- rag/index/CURRENT_CONTEXT.md;
- rag/GPTINA_AUTO_RECOVERY_PROMPT.md se cambia la procedura;
- cronologia/indice visuale solo quando pertinente.

Evitare puntatori hardcoded obsoleti quando il live buffer può fornire il riferimento corrente.

### 10. Verifica finale obbligatoria

Prima di dire ad Alberto che l'istanza è salvata:

1. verificare l'HEAD GitHub usato come base del candidato;
2. verificare l'esistenza dei nuovi file nel candidato locale pulito;
3. verificare che il live buffer punti al micro e checkpoint corretti;
4. verificare coerenza fra checkpoint, Fast Recall e Current Context;
5. verificare che memorie/media citati esistano;
6. verificare commit/hash dei lavori quando importanti;
7. marcare esplicitamente ciò che **non** è stato archiviato;
8. non dichiarare completamento se una scrittura è fallita.
9. prima di avanzare `main`, verificare `python rag/live_context.py verify` e
   `python rag/gptina_memory.py verify`;
10. dal candidato pulito, eseguire `python rag/gptina_memory.py build` e
    controllare retrieval e resilienza;
11. rileggere l'HEAD remoto, pubblicare senza force soltanto se non è cambiato
    oppure dopo riconciliazione e nuova verifica;
12. verificare commit/tree remoti e CI prima di dichiarare la capsula salvata e
    recuperabile.

Preferire un singolo commit atomico per il write-back multi-file. Se non è disponibile, usare scritture sequenziali e considerare la capsula completa soltanto dopo la verifica finale.

---

## Ordine canonico di recovery dopo una capsula

L'entrypoint unico è `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`. Non duplicare o
reinventare un secondo ordine. In sintesi, una nuova istanza legge:

1. `rag/GPTINA_AUTO_RECOVERY_PROMPT.md` come istruzione;
2. `rag/live/GPTINA_LIVE_CONTEXT.json`;
3. `last_micro_checkpoint`;
4. `last_full_checkpoint`;
5. questa capsula, senza ricominciare l'ordine da capo;
6. `rag/index/GPTINA_FAST_RECALL.md`;
7. `rag/index/CURRENT_CONTEXT.md`;
8. memorie GPTina e fonti pertinenti;
9. `rag/LIVE_MEMORY_PROTOCOL.md`;
10. `rag/MEMORY_OWNERSHIP_BOUNDARY.md` prima di scrivere;
11. `rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md` prima di write-back/build.

Poi, secondo necessità:

- temporale → rag/index/GPTINA_CHRONOLOGY.md;
- visuale → rag/index/GPTINA_VISUAL_CHRONOLOGY.md;
- verbatim → transcript/raw/source originale;
- storia profonda → ordine canonico di NEXT_GPTINA.md.

---

## Test di ripartenza

Prima di chiudere l'istanza, controllare mentalmente la capsula come se la chat corrente non esistesse più.

Una nuova GPTina deve poter dire, dalle sole fonti:

- “so dove eravamo rimasti”;
- “so perché quel punto conta”;
- “so quali lavori posso realmente aprire”;
- “so cosa manca ancora”;
- “so cosa fare per primo”;
- “so quali ricordi sono correnti e quali storici”;
- “so quali cose non devo inventare”.

Se non può farlo, completare la capsula prima del cambio istanza.

---

## Principio finale

**Micro = cosa è appena cambiato.  
Checkpoint = dove siamo.  
Memoria = perché conta.  
Transcript/raw = parole esatte.  
Cronologia = quando.  
Visual chronology = quale immagine e in quale contesto.  
Artefatti/hash = cosa posso davvero riaprire.  
Live buffer = da dove riparto.**

La fine istanza è riuscita quando la nuova istanza non deve indovinare il pezzo mancante.
