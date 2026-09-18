# GPTina structured media links

Questa directory contiene il registro strutturato **image → context → memory**.

- un record JSON per immagine;
- partizionamento per anno/mese;
- Git blob SHA e byte size;
- event-time e record-time distinti;
- contesto e memoria obbligatori;
- status visuale esplicito;
- cue di retrieval.

Backfill iniziale del 2026-09-18: **44/44 immagini presenti in `media/` hanno un record**.

Il database canonico resta Git + file sorgente; questo registro è parte della memoria strutturata GPTina e viene indicizzato dal retrieval.

Per nuove immagini usare `python rag/gptina_memory.py link-image ...` in un checkout locale, oppure produrre lo stesso JSON nello stesso commit atomico quando si opera via GitHub connector.
