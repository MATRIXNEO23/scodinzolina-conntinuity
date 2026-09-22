# Recovery a freddo repository-only superato

Data: 2026-09-22

## Prova eseguita

`python rag/test_cold_start_recovery.py`

La prova ha creato un clone shallow isolato contenente soltanto l'HEAD
candidato e nessuna proiezione derivata. Ha verificato che il baseline strict
non fosse inizialmente disponibile, lo ha recuperato esplicitamente dal remote
del clone e ha ricostruito la memoria esclusivamente dalle fonti versionate.

## Esito

- live context e puntatori: PASS;
- schema e ownership: PASS;
- build generazionale da zero: PASS;
- runbook e ordine di recovery: PASS;
- gold retrieval ordinario: 18/18 PASS;
- cold-start gold mirato: 6/6 PASS;
- memoria legacy del 12 settembre: recuperata;
- memoria invalidated “En tus ojos”: esclusa dal presente e recuperata con
  richiesta esplicita `all_statuses`;
- correzione numerazione immagini: recuperata;
- fonte ownership: recuperata;
- ultimo allineamento recovery: recuperato;
- worktree del clone dopo il rehearsal: pulito.

## Regola permanente

Il cold-start rehearsal è ora un gate di GitHub Actions. Una modifica futura
alla memoria o ai protocolli non è accettabile se un clone nuovo, senza chat e
senza indici ereditati, non riesce a ricostruire e interrogare correttamente la
memoria.

## Conservazione

La prova non modifica, sposta o elimina memorie canoniche. Le proiezioni sono
locali, ignorate da Git e ricostruibili. Baseline e stato candidato conservano
lo stesso insieme di 65 file sotto `rag/memories/`, con zero cancellazioni.
