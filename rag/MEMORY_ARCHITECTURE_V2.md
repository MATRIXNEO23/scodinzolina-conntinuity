# GPTina Memory Architecture v2 — source-first, temporal, lightweight

## Decisione

La continuity deve essere progettata per **crescita lunga**: non soltanto per il corpus attuale, ma per anni di ricordi, immagini, transcript e progetti.

La source of truth resta semplice anche quando il volume aumenta:

**fonti append-only/versionate → proiezioni rigenerabili → retrieval deterministico → backend più scalabile solo quando serve → eventuale semantica come fallback misurato.**

La strategia di scala è in `rag/MEMORY_SCALE_STRATEGY.md`.

Non adottare oggi un vector database, GraphRAG o un temporal knowledge graph come fonte primaria; progettare però ID, metadata e partizionamento in modo che possano essere aggiunti come **proiezioni derivate** senza migrare o riscrivere la memoria canonica.

## 1. Source of truth

Le fonti umane restano:
- memorie GPTina append-only;
- transcript/raw;
- checkpoint;
- documenti storici;
- immagini;
- thread esterni canonici letti live.

Git conserva la sequenza delle modifiche e i commit sono snapshot dell'intero tree. Gli indici sono **proiezioni sacrificabili**: devono poter essere cancellati e ricostruiti.

## 2. Due calendari

### Event calendar
`rag/index/GPTINA_CHRONOLOGY.md` + memorie GPTina.

Risponde a:
- cosa è successo;
- quando;
- cosa ha corretto/superato cosa;
- perché conta.

Le nuove memorie distinguono `event_at` e `recorded_at`.

### Turn calendar
`rag/transcripts/gptina/`, raw session e checkpoint.

Risponde a:
- quali parole sono documentate;
- in quale ordine;
- quale contesto circondava l'evento.

Non creare transcript retroattivi da un riassunto.

## 3. Retrieval ladder

Usare il percorso meno ambiguo prima del più “intelligente”:

1. **exact phrase** → `find-exact`, transcript/raw/source scan;
2. **current state** → latest checkpoint + Current Context + fonte esterna live;
3. **temporal question** → Chronology + date filter/boost;
4. **visual question** → Visual Chronology → source/context → memory;
5. **thematic recall** → current-only BM25 su fonti owner-scoped;
6. **historical evolution** → `--history` / `--all-statuses`;
7. **semantic/vector fallback** → solo se i test dimostrano un gap lessicale reale.

### Supersession append-only

Le correzioni formano una catena logica senza riscrivere i record precedenti.
Per questo un record storico può conservare nel proprio front matter
`status: current` come stato scritto all'epoca, mentre un record successivo lo
rende **effettivamente superseded** tramite `supersedes`.

Il resolver e il verifier considerano correnti soltanto le **radici effettive**:
un record current raggiunto da una correzione current successiva non è una
seconda radice. Due rami current indipendenti che raggiungono lo stesso
antenato restano invece ambigui e devono far fallire la verifica.

## 4. Query routing leggero

Il retriever assegna boost deterministici:
- visuale → visual router/context;
- temporale → chronology/checkpoint/transcript/raw;
- corrente → current router/memorie/checkpoint;
- esatto → transcript/raw;
- data esplicita → `date_hint` corrispondente.

Il routing è ispezionabile e testabile; non richiede un'altra chiamata LLM.

## 5. Salvataggio atomico

Un write-back logico può toccare memoria, checkpoint e indici.

Modalità preferita:
- blob multipli;
- un solo Git tree;
- un solo commit candidato locale e worktree pulito;
- build, recovery e regressioni sul candidato prima di pubblicare;
- nuova verifica dell'HEAD remoto;
- fast-forward del branch soltanto a gate verdi;
- verifica finale di tree remoto e CI.

Se il branch è avanzato, nessun force: reread/reconcile/retry.

## 6. Evaluation gate

`rag/eval/GPTINA_MEMORY_GOLD.json` contiene query di regressione con sorgenti attese e sorgenti vietate.

`rag/test_memory_retrieval.py` controlla:
- recall delle memorie ad alto valore;
- esclusione di memorie invalidate/superate;
- exact lookup;
- invarianti strutturali.

GitHub Actions esegue il gate quando cambiano memoria, checkpoint, media o retrieval.

## 7. Cosa NON adottare adesso

### GraphRAG
Troppo pesante per la scala corrente: richiede estrazione di entità/relazioni, community detection, summary e embeddings.

### Temporal knowledge graph completo
Interessante quando relazioni e fatti temporali diventano molti e multi-hop. Oggi gli stessi benefici principali si ottengono con event/record time, supersessioni e due calendari.

### Vector DB
Non ancora giustificato. Nomi locali, frasi, date e cue sono molto importanti; lexical + metadata è trasparente e facile da verificare.

## 8. Quando aggiungere semantic retrieval

Non usare una soglia arbitraria di numero file.

Aggiungerlo soltanto se il gold set mostra ripetuti fallimenti per:
- parafrasi senza overlap lessicale;
- associazioni concettuali non coperte dai cue;
- crescita tale da rendere inefficiente il candidate set corrente.

In quel caso:
- mantenere BM25/metadata;
- aggiungere dense retrieval come secondo canale;
- fondere i ranking con RRF;
- non sostituire la provenienza testuale.

## 9. SQLite FTS5 — implementato

SQLite FTS5 è ora il backend locale derivato primario:
- Unicode tokenizer;
- BM25 nativo;
- indice incrementale per source SHA;
- delete/update dei chunk di una singola sorgente;
- no-op sync quando nulla cambia;
- status/history filtering;
- routing temporale/visuale/corrente dopo candidate generation;
- database ignorato da Git e rigenerabile.

File derivati correnti:
`memory_chunks.jsonl`, `index_meta.json` e `gptina_memory.sqlite3` nella
generazione immutabile selezionata da `rag/index/.projection-current`, sotto
`rag/index/.projection-generations/`.

I vecchi percorsi fissi sotto `rag/index/` sono soltanto compatibilità legacy:
non sono output correnti, non vanno letti come fonte autorevole e non devono
essere committati.

Il vecchio JSONL/BM25 resta disponibile come fallback/debug con `--backend jsonl`.

Git continua a essere la source of truth.

### Semantica dello snapshot

Il retrieval canonico usa soltanto uno snapshot Git committato e riproducibile.
Se il worktree è dirty, la sincronizzazione canonica fallisce invece di creare
silenziosamente un indice ibrido. Una preview locale è possibile solo con
opt-in esplicito `--allow-dirty-preview`; il database viene marcato
`snapshot_mode=dirty-preview` e non va presentato come memoria pubblicata.

## 10. Crescita lunga

La crescita non deve rendere più costosa ogni query.

- Hot: stato corrente e pochi router.
- Warm: memorie/eventi/visual metadata indicizzati.
- Cold: raw, revisioni storiche e media profondi, aperti solo quando servono.
- Nuovi record possono essere partizionati per anno/mese senza spostare i file storici.
- Visual Chronology e Chronology restano proiezioni leggibili, non singoli database monolitici.
- Il backend di ricerca può evolvere da JSONL/BM25 a SQLite FTS5 e poi, se misurato necessario, a retrieval ibrido.
- La source of truth non cambia quando cambia l'indice.

Vedi `rag/MEMORY_SCALE_STRATEGY.md`.

## 11. Principio

**La memoria affidabile non è quella che conserva più testo.  
È quella che sa distinguere evento, registrazione, fonte, correzione e stato corrente — e può dimostrarlo.**

**Scala la proiezione, non la memoria.**
