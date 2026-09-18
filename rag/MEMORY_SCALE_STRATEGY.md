# GPTina — Memory Scale Strategy

## Premessa

La continuity va progettata per **anni di crescita**, non per il volume attuale.

La fonte canonica deve poter crescere fino a migliaia o decine di migliaia di ricordi, immagini, checkpoint e transcript senza richiedere riscritture distruttive.

## Principio

**Scala la proiezione, non la memoria.**

Le fonti originali restano append-only e leggibili.
Ciò che cambia con la crescita sono:
- partizionamento;
- indici;
- candidate selection;
- cache/proiezioni;
- strategie di retrieval.

## Livelli logici

### HOT — presente
Piccolo e sempre rapido:
- checkpoint più recente;
- `CURRENT_CONTEXT.md`;
- `GPTINA_FAST_RECALL.md`;
- memorie recenti ad alta importanza;
- stato esterno live recuperato dalla fonte.

### WARM — memoria strutturata
- memorie GPTina;
- chronology;
- visual records;
- checkpoint recenti;
- transcript recenti.

Qui il retrieval deve usare metadata prima di aprire il testo completo.

### COLD — archivio profondo
- raw session;
- transcript storici;
- snapshot;
- revisioni Git;
- media storici;
- fonti superate/invalidated.

Non devono partecipare a ogni query.

## Partizionamento senza migrazioni distruttive

I file storici esistenti restano dove sono.

Per nuovi volumi è consentito partizionare:
- memorie: `rag/memories/gptina/YYYY/MM/`
- metadata immagini: `rag/media-links/YYYY/MM/`
- transcript: già naturalmente partizionabili per anno/mese/giorno
- checkpoint: `checkpoints/YYYY/MM/` quando il numero in root diventa scomodo

Il retrieval deve essere ricorsivo e non dipendere dal fatto che i file siano piatti o partizionati.

## ID stabili

I path possono cambiare organizzazione in futuro; gli ID no.

Ogni nuova memoria deve avere `memory_id`.
Quando utile aggiungere:
- `event_id` — raggruppa memoria, immagini e fonti dello stesso episodio;
- `thread_ids` — fili persistenti come posticino, vita-a-tre, visual-identity;
- `entity_refs` — Alberto, GPTina, Tessa o altri referenti narrativi/progettuali.

Gli ID sono riferimenti logici; non sostituiscono le fonti.

## Immagini a scala

Una singola Visual Chronology manuale non deve diventare il database di migliaia di immagini.

Per ogni nuova immagine significativa, oltre al file media, creare un record metadata in:
`rag/media-links/YYYY/MM/`

Il record conserva:
- image path / blob identity;
- event_at / recorded_at;
- context/source refs;
- memory refs;
- event_id/thread_ids;
- visual status;
- cue.

`GPTINA_VISUAL_CHRONOLOGY.md` diventa quindi una **proiezione umana rigenerabile**, non il solo luogo dove esiste il legame.

## Indici incrementali

A corpus grande non rileggere tutto a ogni query.

Regole:
1. se `git_head` e manifest SHA non sono cambiati rispetto all'indice, considerarlo fresco senza ricalcolare fingerprint di tutte le fonti;
2. se HEAD cambia, verificare una volta le sorgenti e aggiornare/rebuildare la proiezione;
3. SQLite FTS5 aggiorna ora solo documenti i cui source SHA sono cambiati;
4. gli indici derivati possono essere eliminati e ricostruiti.

## Evoluzione del backend

### Fase A — compatibility/debug
JSONL + BM25 Python resta disponibile come fallback.

### Fase B — attiva
**SQLite FTS5 incrementale** è il backend predefinito.

Contiene:
- chunk text;
- source path;
- source SHA;
- status;
- event/date hints;
- kind/priority metadata.

Aggiorna solo sorgenti nuove/cambiate/rimosse confrontando gli SHA; il secondo sync senza modifiche deve essere no-op.

Git resta la source of truth.

### Fase C — gap semantico misurato
Se il gold set fallisce ripetutamente su parafrasi senza overlap lessicale:
- aggiungere embeddings come secondo canale;
- mantenere lexical retrieval;
- fondere i ranking;
- verificare sempre la fonte testuale finale.

### Fase D — relazioni multi-hop reali
Aggiungere una proiezione graph/temporal soltanto se diventano frequenti domande che richiedono catene di relazioni tra molti eventi/entità.

Il graph non diventa mai la fonte canonica.

## Compaction sicura

Mai compattare cancellando.

Sono ammesse **proiezioni sintetiche**:
- daily/monthly digest;
- thread summaries;
- entity timelines;
- visual digests.

Devono essere marcate come derived e contenere riferimenti alle fonti.
Servono per localizzare i record, non per sostituirli.

## Metriche di scala

Non migrare backend soltanto perché esiste un numero arbitrario di file.

Misurare almeno:
- tempo build indice;
- tempo query;
- dimensione indice;
- recall@k del gold set;
- numero di query che richiedono fallback manuale;
- percentuale di risultati provenienti da versioni errate/superate;
- numero di sorgenti aperte per arrivare alla risposta verificata.

La migrazione avviene quando una metrica reale peggiora in modo persistente.

## Failure containment

Con migliaia di record, una memoria corrotta non deve invalidare tutto:
- schema verify per i nuovi record;
- status invalidated/superseded;
- CI regression;
- commit atomici multi-file;
- nessun force push;
- indici disposable;
- ownership GPTina/Tessa verificata automaticamente.

## Obiettivo

Fra anni la domanda deve restare semplice:

> “Ricordi quella volta che...?”

e il sistema deve poter restringere rapidamente:
**tempo → thread/evento → fonti candidate → memoria corrente → prova**, senza leggere l'intera vita ogni volta.
