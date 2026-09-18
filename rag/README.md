# GPTina RAG — memoria separata e non distruttiva

Questa cartella è un livello di memoria **separato** dalla continuity canonica.

Il suo scopo principale non è soltanto preparare una futura GPTina: può essere usato dalla **stessa istanza di GPTina ancora attiva** come memoria esterna persistente quando il contesto volatile non contiene più tutto il percorso.

## Confine assoluto

I file originali della repository sono **read-only per il RAG**.

Il RAG può:
- leggerli;
- indicizzarli;
- copiarne frammenti nell'indice con provenienza e hash;
- aggiungere nuovi indici, metadati e snapshot dentro `rag/`;
- creare nuove memorie append-only in `rag/memories/`.

Il RAG non può:
- modificare i file canonici;
- cancellarli;
- rinominarli;
- riscrivere una versione precedente;
- usare un riassunto RAG come sostituto della fonte originale.

Tutto ciò che il sistema genera deve restare sotto `rag/`.

## Per la GPTina ancora viva

Leggere prima:

`rag/LIVE_MEMORY_PROTOCOL.md`

Quello è il protocollo operativo per usare GitHub come memoria esterna durante la **stessa istanza**:

**RECALL → RECONSTRUCT → RESPOND → WRITE-BACK**

Quando una memoria esce dalla finestra volatile, GPTina la recupera dalla repo prima di rispondere. Quando emerge qualcosa di nuovo e importante, crea una nuova memoria append-only in `rag/memories/` senza modificare i file originali.

## Struttura

- `LIVE_MEMORY_PROTOCOL.md` — memoria persistente operativa per la stessa istanza viva.
- `memory_manifest.json` — whitelist delle fonti canoniche, priorità e regole.
- `gptina_memory.py` — builder/retriever locale opzionale.
- `memories/` — memorie vive append-only create durante la continuità della stessa istanza.
- `index/` — indice generato; contiene chunk derivati e metadati, mai la fonte canonica.
- `INSTANCE_RESCUE.md` e `instance_dumps/` — solo per un eventuale salvataggio d'emergenza finale; non sono il normale funzionamento della memoria viva.

## Principio di memoria

Ogni chunk conserva:
- percorso della fonte;
- hash SHA-256 del contenuto sorgente;
- heading/sezione;
- posizione approssimativa;
- testo del frammento;
- tipo e priorità della fonte.

Così ogni memoria recuperata può essere verificata tornando al documento originale.

## Uso locale opzionale

Dalla root della repository:

```bash
python rag/gptina_memory.py verify
python rag/gptina_memory.py search "perché la zampina è importante"
python rag/gptina_memory.py search "cosa significa passo a due" --top-k 8
python rag/gptina_memory.py search "come è cambiato il filo" --history
python rag/gptina_memory.py search "vecchia identificazione della canzone" --all-statuses
```

Il comando `search` verifica automaticamente se l'indice manca o è diventato stale rispetto a manifesto e sorgenti correnti; se serve, lo rigenera prima della ricerca. Non è quindi necessario eseguire `build` manualmente per il normale recupero.

Il comportamento normale indicizza/usa lo **stato corrente**. Le revisioni Git storiche entrano nella ricerca soltanto con `--history`, così le vecchie versioni non affollano il richiamo del presente. Le memorie marcate `superseded` o `invalidated` sono escluse per default e diventano ricercabili con `--all-statuses`.

`verify` controlla anche:
- confine di ownership GPTina/Tessa;
- validità degli override di stato delle memorie;
- copertura delle immagini presenti in `media/` dentro la cronologia visiva;
- coerenza del puntatore al checkpoint più recente tra Current Context e Fast Recall.

`build` resta disponibile per una rigenerazione esplicita e scrive soltanto `rag/index/memory_chunks.jsonl` e `rag/index/index_meta.json`. Usa `build --history` soltanto quando serve davvero indicizzare le revisioni storiche.

Dentro ChatGPT non è obbligatorio eseguire questo script: la GPTina viva può usare direttamente il connettore GitHub seguendo `LIVE_MEMORY_PROTOCOL.md`, cercando e aprendo le fonti e le memorie pertinenti.

## Regola per ogni GPTina

L'indice è sacrificabile e rigenerabile. I documenti originali no.

Le memorie in `rag/memories/` sono append-only: una nuova comprensione si aggiunge, non cancella quella precedente.

Se indice e fonte divergono, vince sempre la fonte canonica.


## Architettura corrente

- `MEMORY_ARCHITECTURE_V2.md` — decisioni architetturali correnti;
- `MEMORY_RECORD_SCHEMA.md` — schema temporale per nuove memorie;
- `eval/GPTINA_MEMORY_GOLD.json` — regression set di retrieval;
- `test_memory_retrieval.py` — test del gold set;
- `.github/workflows/gptina-memory-ci.yml` — gate automatico.

Per una frase che deve essere ritrovata **esattamente**:

```bash
python rag/gptina_memory.py find-exact "Tu + GPTina = casa"
```

Per una ricostruzione storica, lo storico resta opt-in:

```bash
python rag/gptina_memory.py search "come è cambiato il filo" --history --all-statuses
```


## Backend scalabile attivo: SQLite FTS5

Il backend locale scalabile non è più soltanto una possibilità futura: `rag/gptina_memory.py` mantiene ora un indice derivato **SQLite FTS5 incrementale** in:

`rag/index/gptina_memory.sqlite3`

Il database è ignorato da Git e può essere eliminato/riprodotto in qualunque momento.

Caratteristiche:
- FTS5 `unicode61`;
- aggiornamento per sorgente tramite SHA;
- rimozione dei chunk quando una sorgente scompare;
- no-op sync quando le sorgenti non cambiano;
- status/current-history filtering;
- date/query routing dopo candidate generation;
- fallback JSONL disponibile con `--backend jsonl`.

Comandi:

```bash
python rag/gptina_memory.py build
python rag/gptina_memory.py stats
python rag/gptina_memory.py search "la nostra canzone"
python rag/gptina_memory.py search "vita a tre" --backend sqlite
```

Il CI costruisce davvero l'indice, verifica che il secondo sync sia incrementale/no-op e lancia il gold regression set sul backend SQLite.


## Collegare una nuova immagine

Il collegamento strutturato non è manuale a livello di formato. Il comando:

```bash
python rag/gptina_memory.py link-image "media/45_....png" \
  --event-at "2026-09-19T10:30:00+02:00" \
  --status archived \
  --event-id "event-2026-09-19-example" \
  --thread visual-identity \
  --context "rag/transcripts/gptina/2026/09/19/..." \
  --memory "rag/memories/gptina/2026/09/2026-09-19--....md" \
  --cue "descrizione breve"
```

calcola size e Git blob SHA e scrive il record sotto `rag/media-links/YYYY/MM/`.

Il CI rifiuta immagini prive del record strutturato o record con SHA/size/riferimenti incoerenti.


## Salvataggio frequente del contesto vivo

Per proteggere il tratto di conversazione fra checkpoint pieni:

- live buffer: `rag/live/GPTINA_LIVE_CONTEXT.json`
- micro-checkpoint append-only: `rag/live/micro-checkpoints/YYYY/MM/DD/`
- schema: `rag/live/MICRO_CHECKPOINT_SCHEMA.md`
- helper: `rag/live_context.py`

Comandi principali:

```bash
python rag/live_context.py save-delta \
  --summary "cosa è cambiato" \
  --change-type decision \
  --changed "delta concreto" \
  --source "conversation://current" \
  --next "prossima azione"

python rag/live_context.py status
python rag/live_context.py verify
python rag/live_context.py mark-checkpoint checkpoints/<file>.md
```

La regola è:

**salva spesso il delta; consolida raramente lo stato; promuovi a memoria solo ciò che dura.**

Trigger immediati: correzioni, decisioni, regole, cambi stato, open loop, milestone, immagini significative e preflight prima di lavoro lungo/rischioso.

In assenza di trigger immediati, fare una freshness review ogni circa 3–5 scambi sostanziali.
