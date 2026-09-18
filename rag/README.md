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
