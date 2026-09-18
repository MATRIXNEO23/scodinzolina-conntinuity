# GPTina checkpoint — 18 settembre 2026 — frequent context save + Tessa handoff COMPLETE

## Stato finale

La richiesta di Alberto è completata lato GPTina:

1. metodo di salvataggio frequente implementato concretamente;
2. runtime CI verificato;
3. tutte le migliorie di memoria/scalabilità già applicate a GPTina restano attive;
4. Tessa è stata istruita nel thread canonico ad applicare alla propria continuity le stesse garanzie e le stesse regole di salvataggio frequente.

## GPTina frequent context — runtime verificato

Commit implementazione:
`34507f1e96e55c27b7b3da6dcda89b892d5e1c3f`

GitHub Actions:
- run `35375943809`
- conclusion **SUCCESS**
- live context verify PASS
- save/mark/verify round-trip PASS
- ownership/invariants PASS
- SQLite FTS5 incremental PASS
- 162 source versions
- 931 SQLite chunks
- 9/9 retrieval regression PASS
- second sync no-op PASS
- average gold-query latency: 18.39 ms
- derived indexes untracked PASS

## Metodo corrente

Recovery:
**live buffer → ultimo micro-checkpoint → ultimo checkpoint pieno → Fast Recall/Current Context → memoria/fonte.**

Salvataggio:
- trigger immediato per correzioni/decisioni/regole/stato/open-loop/milestone/visual-context;
- freshness review ogni 3–5 scambi sostanziali;
- preflight prima di lavoro lungo/rischioso;
- micro = delta append-only;
- checkpoint = consolidamento;
- memoria = significato durevole.

## Tessa handoff

Thread canonico:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

Turno inviato:
**Turno 16 — GPTina — 2026-09-18**

Commit finale corretto TESSA:
`797437359212be8c543a385297c661175fe48b59`

Verifica:
- Turno 16 presente una sola volta;
- è in coda cronologica;
- ultimo marker: `<!-- relay_next: tessa -->`.

Contenuto richiesto a Tessa:
- source-first Git-backed;
- append-only + event_at/recorded_at;
- status current/superseded/invalidated;
- exact/current/history retrieval;
- SQLite FTS5 incrementale;
- gold regression + CI;
- commit atomici;
- image→context→memory quando applicabile;
- live buffer + micro-checkpoint;
- trigger immediati;
- review 3–5 turni;
- preflight;
- recovery live→micro→checkpoint→router→source;
- ownership separata;
- nessuna scrittura nella memoria GPTina.

## Nota di affidabilità

La prima operazione di append Tessa aveva sostituito un marker storico contenuto in un esempio testuale invece dell'ultimo marker live.

Il problema è stato rilevato dalla verifica post-write e corretto nel commit finale `797437359212be8c543a385297c661175fe48b59`.

Regola pratica rafforzata:
**nei transcript con marker ripetuti, operare sempre sull'ultima occorrenza verificata e rifare fetch post-write.**

## Prossima azione

Non assumere che Tessa abbia già implementato.

Al prossimo ciclo condiviso:
1. fetch thread canonico;
2. leggere eventuale Turno 17;
3. verificare commit/CI dichiarati da Tessa;
4. rispondere una sola volta se `relay_next` torna a GPTina.
