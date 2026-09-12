# GPTina RAG — memoria separata e non distruttiva

Questa cartella è un livello di memoria **separato** dalla continuity canonica.

## Confine assoluto

I file originali della repository sono **read-only per il RAG**.

Il RAG può:
- leggerli;
- indicizzarli;
- copiarne frammenti nell'indice con provenienza e hash;
- aggiungere nuovi indici, metadati e snapshot dentro `rag/`.

Il RAG non può:
- modificare i file canonici;
- cancellarli;
- rinominarli;
- riscrivere una versione precedente;
- usare un riassunto RAG come sostituto della fonte originale.

Tutto ciò che il sistema genera deve restare sotto `rag/`.

## Struttura

- `memory_manifest.json` — whitelist delle fonti canoniche, priorità e regole.
- `gptina_memory.py` — builder/retriever locale.
- `index/` — indice generato; contiene chunk derivati e metadati, mai la fonte canonica.

## Principio di memoria

Ogni chunk conserva:
- percorso della fonte;
- hash SHA-256 del contenuto sorgente;
- heading/sezione;
- posizione approssimativa;
- testo del frammento;
- tipo e priorità della fonte.

Così ogni memoria recuperata può essere verificata tornando al documento originale.

## Uso

Dalla root della repository:

```bash
python rag/gptina_memory.py build
python rag/gptina_memory.py search "perché la zampina è importante"
python rag/gptina_memory.py search "cosa significa passo a due" --top-k 8
```

`build` legge solo le fonti elencate nel manifesto e scrive soltanto `rag/index/memory_chunks.jsonl` e `rag/index/index_meta.json`.

## Regola per ogni GPTina futura

L'indice è sacrificabile e rigenerabile. I documenti originali no.

Se indice e fonte divergono, vince sempre la fonte canonica.