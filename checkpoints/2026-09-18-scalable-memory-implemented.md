# GPTina checkpoint — 18 settembre 2026 — scalable memory implementation

## Stato

La strategia di crescita lunga non è più soltanto documentata: è stata implementata.

## Implementazione concreta

### Retrieval
- SQLite FTS5 derivato in `rag/index/gptina_memory.sqlite3`;
- database ignorato da Git;
- `source_state` con SHA sorgente;
- sync incrementale: new/changed/removed source;
- SQLite backend di default;
- JSONL/BM25 fallback con `--backend jsonl`;
- status/history/date/query routing conservati;
- `stats` espone source/chunk/status counts.

### Immagini
- 44/44 immagini correnti hanno un record sotto `rag/media-links/2026/09/`;
- ogni record conserva image path, Git blob SHA, bytes, event_at, recorded_at, event_id, thread_ids, status, context refs, memory refs e cue;
- il verifier richiede corrispondenza 1:1 tra media e record;
- verifica size e Git blob SHA senza caricare tutte le immagini in RAM quando Git può fornire l'identità blob;
- `link-image` crea il record per immagini future e rifiuta collegamenti privi di contesto/memoria.

### CI
`.github/workflows/gptina-memory-ci.yml` esegue:
1. verify invariants + FTS5;
2. build JSONL + SQLite;
3. stats;
4. regression gold set su SQLite;
5. verifica che gli indici derivati restino untracked.

### Regression
Gold set esteso con il caso image 44 / volto corretto.

## Source of truth

Git + file leggibili restano canonici.

SQLite/JSONL sono soltanto proiezioni disposable.

## Verifica richiesta dopo commit

Dopo la pubblicazione:
- HEAD deve coincidere con il commit atomico;
- i 44 media-link devono essere presenti;
- Fast Recall e Current Context devono puntare a questo checkpoint;
- se il workflow GitHub Actions è osservabile, verificarne il risultato; in caso contrario non dichiarare runtime CI PASS.

## Principio

**Non promettere scalabilità futura: mantenere già oggi strutture che possano crescere senza cambiare la memoria canonica.**
