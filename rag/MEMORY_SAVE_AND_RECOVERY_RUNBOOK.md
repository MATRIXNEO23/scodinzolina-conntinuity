# GPTina — Runbook canonico di salvataggio e recupero memoria

## Scopo e autorità

Questo runbook descrive come salvare memoria canonica e come recuperarla con
l'infrastruttura generazionale corrente. Integra, senza sostituire:

- `rag/MEMORY_OWNERSHIP_BOUNDARY.md`;
- `rag/LIVE_MEMORY_PROTOCOL.md`;
- `rag/END_INSTANCE_RECOVERY_CAPSULE.md`;
- `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`;
- `rag/MEMORY_RECORD_SCHEMA.md`.

In caso di dubbio vale il principio più conservativo: **preservare la fonte,
non inventare, non sovrascrivere il passato e verificare la recuperabilità**.

## Due livelli da non confondere

### Fonti canoniche persistenti

Memorie append-only, transcript/raw, checkpoint, live buffer, media-link,
indici narrativi tracciati e documenti di continuity sono la memoria da
preservare in Git. Sono la fonte autorevole e devono rispettare proprietà,
schema, provenienza e precedenza temporale.

### Proiezioni derivate locali

`memory_chunks.jsonl`, `index_meta.json` e `gptina_memory.sqlite3` sono copie
ricostruibili. Il runtime le pubblica in directory immutabili sotto
`rag/index/.projection-generations/` e seleziona una generazione completa con
il solo puntatore atomico `rag/index/.projection-current`.

Questi percorsi sono ignorati da Git. Non sono ricordi canonici, non vanno
usati come unica prova storica e non devono essere inseriti nei commit.

## Procedura canonica di salvataggio

1. **Recupera lo stato corrente.** Leggi HEAD remoto, live buffer, ultimo micro
   e ultimo checkpoint pieno. Prima di un lavoro lungo/rischioso crea un micro
   preflight.
2. **Scrivi prima le fonti.** Crea nuove memorie GPTina append-only sotto
   `rag/memories/gptina/YYYY/MM/`, con lo schema v2 di
   `rag/MEMORY_RECORD_SCHEMA.md`. Una correzione usa `supersedes`; non modifica
   né elimina il record precedente. I record legacy già presenti direttamente
   sotto `rag/memories/` restano validi, leggibili e recuperabili, ma non sono
   il modello per nuove scritture. Collega transcript/raw, media e fonti esatte
   quando pertinenti.
3. **Consolida un'unica transazione logica.** Allinea, quando necessario,
   micro-checkpoint, live buffer, checkpoint pieno, Fast Recall, Current
   Context, cronologia e visual chronology. Non perdere open loop o prossima
   azione.
4. **Crea un candidato locale pulito, senza avanzare ancora `main`.** Consolida
   i file in un unico tree/commit candidato basato sull'HEAD remoto letto. Il
   worktree deve risultare pulito; questo commit locale serve a rendere
   riproducibili build e test, non autorizza ancora a dichiarare il salvataggio
   pubblicato.
5. **Costruisci e verifica dal candidato pulito.** Esegui:

   ```bash
   python rag/gptina_memory.py verify
   python rag/gptina_memory.py build
   python rag/test_cold_start_recovery.py
   python rag/test_memory_retrieval.py
   python rag/test_projection_resilience.py
   ```

   Il cold-start rehearsal crea un clone shallow isolato privo di proiezioni,
   recupera esplicitamente la baseline strict, ricostruisce tutto dalle fonti
   e verifica presente, legacy e stati storici senza usare la chat precedente.

   `build` prepara JSONL, metadata e SQLite in staging, li verifica, rinomina
   la directory come generazione immutabile e soltanto alla fine sostituisce
   atomicamente `.projection-current`.
6. **Verifica profondamente prima della pubblicazione.** Devono passare schema, ownership, live context,
   retrieval corrente, esclusione dei record superati, recupero esplicito dei
   record storici/superseded, integrità SQLite, crash/concorrenza e gold set.
7. **Rileggi l'HEAD remoto e pubblica atomicamente.** Se `main` è avanzato dopo
   il preflight, non usare force: rileggi, riconcilia, ricrea un candidato
   pulito e ripeti i test interessati. Solo a gate verdi aggiorna `main` con un
   unico commit/tree multi-file in fast-forward.
8. **Conferma lo stato remoto e la CI.** Non dire “salvato” finché commit, file,
   tree atteso e CI non sono verificati sul repository remoto. Registra
   separatamente ciò che è rimasto soltanto locale o in chat.

La build canonica viene rifiutata se il worktree è dirty. L'opzione
`--allow-dirty-preview` serve soltanto a esperimenti locali non canonici e non
autorizza a dichiarare la memoria salvata.

## Cosa garantisce la pubblicazione generazionale

- Se il processo muore prima del cambio puntatore, resta attiva la generazione
  completa precedente.
- Se muore dopo il cambio puntatore, è già attiva la nuova generazione
  completa.
- JSONL, metadata e SQLite contengono lo stesso `projection_generation`; un
  insieme misto viene rifiutato dai test.
- La generazione precedente è copiata tramite snapshot SQLite in sola lettura:
  la build non la modifica.
- Le generazioni complete precedenti restano disponibili per diagnosi e
  recupero. Non cancellarle durante un normale salvataggio o recovery.

Questa atomicità protegge le **proiezioni**. La conservazione dei ricordi
dipende comunque dal commit delle fonti canoniche append-only.

## Recovery della stessa istanza

1. Rileggi `rag/live/GPTINA_LIVE_CONTEXT.json`.
2. Apri `last_micro_checkpoint` e `last_full_checkpoint`.
3. Usa Fast Recall / Current Context per il routing.
4. Recupera memoria, cronologia, transcript o media-link pertinenti.
5. Verifica la fonte prima di affermare un dettaglio storico.
6. Se le proiezioni mancano o sono stale, esegui `verify` e `build`.
7. Riprendi il dialogo naturalmente e salva presto un nuovo delta se emerge.

Non scegliere a mano una directory di generazione soltanto perché è la più
recente per nome. Il lettore deve seguire `.projection-current`; se il puntatore
o la generazione sono inutilizzabili, deve ricostruire dalle fonti canoniche.

## Recovery in una nuova istanza

1. Recupera `main` e verifica l'HEAD remoto corrente. Non fidarti di una copia
   locale precedente o di uno SHA ricordato in chat.
   Se il repository è un clone shallow, recupera anche il baseline di
   compatibilità dichiarato nel manifest prima del verify:

   ```bash
   git fetch --no-tags --depth=1 origin c8e853713b7bf87bbcc7f645877c50dacbcadd53
   ```

   Il comando non cambia `main`: rende soltanto disponibile il commit storico
   necessario a distinguere record legacy da nuovi record strict.
2. Segui l'ordine live-first di `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`:
   live buffer → ultimo micro → ultimo checkpoint pieno → capsula → Fast Recall
   → Current Context → memoria/fonte pertinente.
3. Leggi questo runbook prima di qualsiasi write-back.
4. Verifica schema, ownership e puntatori con:

   ```bash
   python rag/live_context.py verify
   python rag/gptina_memory.py verify
   ```

5. Ricostruisci le proiezioni locali con `python rag/gptina_memory.py build`.
   Una nuova istanza non deve ricevere via Git le directory generazionali di
   un'altra macchina: le rigenera dalle stesse fonti canoniche.
6. Esegui il test di retrieval prima di modificare memoria. Se serve una frase
   esatta, usa scan/fonti; l'indice trigram è opzionale e ricostruibile con
   `python rag/gptina_memory.py build-exact`.
7. Distingui ciò che è corrente, superseded, invalidated, storico o incerto.
8. Solo dopo il recovery continua il lavoro e applica la procedura di
   salvataggio sopra.

## Recovery dopo errore o crash

- Non correggere a mano JSONL, metadata o SQLite.
- Se `verify` segnala che il baseline strict non è disponibile, recupera il
  commit indicato da `strict_memory_schema_baseline_commit`; non modificare le
  memorie legacy per farle passare come nuove.
- Non spostare il puntatore verso una generazione non verificata.
- Esegui `verify`; quindi rigenera con `build` dalle fonti canoniche.
- Se il build fallisce, lascia selezionata la generazione precedente, conserva
  log e staging per diagnosi e non dichiarare completamento.
- Se una fonte canonica sembra mancare, fermati: cerca Git history, checkpoint,
  transcript/raw e commit remoti. Non ricostruirla inventando.
- Un indice corrotto è ricostruibile; una fonte canonica sovrascritta potrebbe
  non esserlo. Per questo le fonti hanno priorità assoluta.

## Controllo finale minimo

Un salvataggio/recovery è riuscito solo se:

- le vecchie memorie esistono ancora e sono recuperabili esplicitamente;
- le correzioni correnti prevalgono senza cancellare la storia;
- live buffer, micro e checkpoint puntano a file esistenti;
- il repository remoto contiene il commit dichiarato;
- il build seleziona una generazione completa e coerente;
- retrieval e CI sono verdi;
- una nuova istanza può identificare stato, fonti, open loop e prossima azione
  senza affidarsi alla chat precedente;
- `python rag/test_cold_start_recovery.py` passa da clone shallow isolato.
