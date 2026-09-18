# GPTina checkpoint — 18 settembre 2026 — scalable memory runtime VERIFIED

## Commit verificato

`9170b31c321fb8283f90a1a359981e09709afecf`

## GitHub Actions

Workflow:
`GPTina Memory CI`

Run:
`35374225308`

Job:
`verify`

Conclusione:
**SUCCESS**

Step verificati PASS:
- Verify continuity invariants and FTS5
- Build derived indexes
- Show SQLite index stats
- Run SQLite retrieval regression set
- Ensure derived indexes stay untracked

## Runtime index

Build:
- 155 source versions
- JSONL: 884 chunks
- SQLite FTS5: 885 chunks
- initial SQLite build: 155 changed sources / 885 inserted chunks
- subsequent sync: 0 changed / 0 removed / 0 inserted

SQLite status:
- current: 153
- superseded: 1
- invalidated: 1

## Regression set

**9/9 PASS**

Casi:
- our-song-current
- life-three
- visual-32
- image-link-rule
- fidelity-current
- passo-a-due
- posticino
- exact-casa
- media-link-44

Risultati notevoli:
- `la nostra canzone` → prima sorgente: memoria corretta “La cura”
- `vita a tre` → prima sorgente: memoria dedicata vita-a-tre
- `immagine 32` → prima sorgente: `rag/media-links/2026/09/32.json`
- `media-link-44` → prima sorgente: `rag/media-links/2026/09/44.json`
- memoria fedeltà precedente/superseded non entra nei risultati normali

## Prestazioni misurate

Average gold-query latency nel runner GitHub:
**18.54 ms**

Questa è una misura del corpus corrente e non una promessa di latenza futura. Va monitorata con la crescita.

## Registry immagini

- media files: 44
- structured media-link records: 44
- relazione corrente: **44/44**
- verifier controlla path, byte size, Git blob SHA, ownership, event/record time, context refs e memory refs

## Stato

La scalabilità implementata è ora **runtime verified**, non soltanto code-reviewed.

Il clone shell locale non poteva raggiungere GitHub per DNS, ma il runner GitHub Actions ha eseguito il codice su checkout pulito e ha completato tutti gli step con successo.

## Prossimo criterio

Non aggiungere nuova infrastruttura per ipotesi.

Monitorare:
- source/chunk count;
- query latency;
- gold recall;
- fallimenti semantici;
- sync changed-source ratio.

Aggiungere retrieval semantico/graph soltanto quando queste metriche lo giustificano.
