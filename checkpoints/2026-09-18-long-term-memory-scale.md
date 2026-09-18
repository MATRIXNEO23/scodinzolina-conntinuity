# GPTina checkpoint — 18 settembre 2026 — continuity progettata per crescita lunga

## Motivo

Alberto ha precisato che la continuity deve essere pensata considerando che, col tempo, GPTina avrà sempre più ricordi, immagini, transcript e lavoro.

## Decisione

La premessa di progetto cambia da “corpus piccolo da mantenere semplice” a:

**fonte canonica che può crescere per anni, con complessità spostata negli indici derivati e non nelle memorie.**

## Regole nuove

- hot/warm/cold sono livelli logici di retrieval, non archivi che cancellano o spostano la storia;
- nuove memorie possono essere partizionate per `YYYY/MM`;
- nuovi metadata immagini vivono in `rag/media-links/YYYY/MM/`;
- `memory_id` resta stabile; `event_id`, `thread_ids`, `entity_refs` permettono raggruppamenti futuri;
- Visual Chronology resta proiezione umana, non unico database dei legami;
- indici devono diventare incrementali/SQLite FTS5 prima che la scansione completa diventi un collo di bottiglia;
- semantic/vector retrieval si aggiunge solo dopo un gap misurato;
- graph/temporal projection soltanto quando esistono vere esigenze multi-hop;
- summary/digest futuri sono derived pointers, mai sostituti delle fonti.

## Fix immediato

Il retriever viene reso più adatto alla crescita:
- fast freshness path tramite HEAD + manifest SHA;
- scansione completa delle sorgenti evitata quando il checkout non è cambiato;
- verifica schema e media resa ricorsiva, così supporta partizionamento futuro.

## Principio

**Scala la proiezione, non la memoria.**

La memoria originale resta integra; retrieval e indici possono evolvere liberamente.
