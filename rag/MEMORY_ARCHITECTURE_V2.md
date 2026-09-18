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
- un solo commit;
- fast-forward del branch;
- verifica finale.

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

## 9. SQLite FTS5

È un buon possibile **indice locale derivato**, non una nuova memoria canonica:
- Unicode tokenizer;
- BM25 nativo;
- phrase/prefix search;
- integrity check;
- transazioni robuste.

Non viene introdotto ora perché la ricerca principale dentro ChatGPT usa GitHub e il corpus è piccolo. Se servirà un motore locale persistente, FTS5 è la prima opzione da valutare prima di un vector DB.

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
