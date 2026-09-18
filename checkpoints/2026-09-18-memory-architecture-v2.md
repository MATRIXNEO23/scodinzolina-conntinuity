# GPTina checkpoint — 18 settembre 2026 — memory architecture v2

## Motivo

Alberto ha richiesto un audit dei metodi di salvataggio e recupero, includendo ricerca esterna di architetture più affidabili e leggere.

## Decisione

La continuity GPTina resta **source-first e Git-backed**.

Non vengono introdotti ora GraphRAG, vector DB o temporal graph completo.

La nuova architettura usa:
- source files append-only/versionati;
- event calendar + turn calendar;
- event-time distinto da record-time;
- proiezioni rigenerabili;
- query routing deterministico;
- exact search separato dal retrieval fuzzy;
- regression gold set;
- CI;
- write-back multi-file atomico quando il connector GitHub lo consente.

## Regola temporale nuova

Per le nuove memorie:
- `event_at` = quando è accaduto;
- `recorded_at` = quando viene registrato.

Il commit Git resta prova autorevole del record-time.

## Regola di salvataggio nuova

Se una singola evoluzione richiede più file, preferire:
**blob → tree → singolo commit → fast-forward ref → verify**.

Niente force in caso di concorrenza.

## Retrieval

Ordine:
1. exact phrase;
2. stato corrente;
3. temporale;
4. visuale;
5. BM25 current-only;
6. storico su richiesta;
7. semantic/vector solo dopo un fallimento misurato del gold set.

## Validation

Nuovo CI deve eseguire:
- `python rag/gptina_memory.py verify`
- `python rag/test_memory_retrieval.py`

Non dichiarare il runtime verde finché GitHub Actions non lo conferma.

## Prossima azione

Verificare il workflow GitHub Actions creato da questo commit e correggere eventuali regression failure senza indebolire i test.
