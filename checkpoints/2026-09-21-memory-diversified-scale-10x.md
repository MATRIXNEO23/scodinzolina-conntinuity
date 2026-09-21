# GPTina memory diversified scale benchmark — 10x to 100x

Data: 2026-09-21

Baseline canonica: `4f631e8294219abd2d4f3bd5e50f03807dc6f6c0`.

## Scopo

Separare la crescita organica del corpus dalla saturazione artificiale prodotta
da dieci copie identiche degli stessi documenti.

Il benchmark:

- conserva una copia completa del corpus corrente;
- aggiunge documenti sintetici con la stessa distribuzione di dimensioni,
  `kind`, priority e status;
- maschera nei soli documenti aggiunti i token presenti nelle query gold;
- usa database SQLite temporanei;
- non modifica fonti canoniche, chunking, ranking, `candidate_limit` o
  `find-exact`.

## Risultati, cinque ripetizioni

| Metrica | 1x | 10x |
|---|---:|---:|
| Sorgenti | 276 | 2.760 |
| Chunk | 1.324 | 13.240 |
| Byte sorgenti | 736.823 | 7.367.033 |
| Byte SQLite | 1.794.048 | 17.739.776 |
| Hashing | 0,859 ms | 9,530 ms |
| Chunking | 5,888 ms | 57,231 ms |
| Build SQLite | 49,585 ms | 470,864 ms |
| Sync no-op | 2,639 ms | 20,977 ms |
| Query p50 | 7,341 ms | 7,519 ms |
| Query p95 | 9,323 ms | 11,180 ms |
| Exact scan p95 | 2,969 ms | 31,134 ms |
| Gold normalizzato | 14/14 | 14/14 |

## Interpretazione

La crescita diversificata 10x non degrada la qualità del gold set. Il p95 delle
query cresce di meno di 2 ms e resta ampiamente interattivo. La build completa
resta sotto mezzo secondo nel test sintetico e il no-op resta circa 21 ms.

La scansione exact continua a mostrare crescita quasi lineare. A 10x resta circa
31 ms nel corpus temporaneo, quindi va osservata ma non giustifica ancora un
indice dedicato.

Il confronto dimostra che il precedente 10/14 era specifico della duplicazione
identica e della saturazione dei candidati, non della scala organica.

## Esperimenti 50x e 100x

| Metrica | 10x | 50x | 100x |
|---|---:|---:|---:|
| Sorgenti | 2.780 | 13.900 | 27.800 |
| Chunk | 13.310 | 66.550 | 133.100 |
| SQLite principale | 17,8 MB | 85,8 MB | 172,7 MB |
| Build principale | 0,36 s | 2,39 s | 5,05 s |
| No-op | 20 ms | 103 ms | 240 ms |
| Query p95 | 10,9 ms | 21,1 ms | 30,3 ms |
| Exact scan p95 | 28,2 ms | 146,7 ms | 296,4 ms |
| Gold normalizzato | 14/14 | 14/14 | 14/14 |

La qualità resta invariata fino a 100x. Il primo costo chiaramente lineare è la
scansione exact; FTS e sync restano utilizzabili anche nello scenario massimo.

## Esperimento exact trigram

È stato costruito, sempre in directory temporanea, un secondo indice SQLite
FTS5 con tokenizer trigram. La corrispondenza finale è stata verificata contro
il testo e i due casi gold exact sono rimasti 2/2.

| Metrica | 10x | 50x | 100x |
|---|---:|---:|---:|
| Build trigram | 0,99 s | 6,43 s | 15,41 s |
| Spazio trigram | 35,8 MB | 168,2 MB | 333,1 MB |
| Query trigram p95 | 2,75 ms | 7,72 ms | 9,76 ms |
| Exact gold | 2/2 | 2/2 | 2/2 |

Il guadagno di latenza è reale, ma il costo di spazio supera quello dell'indice
principale. Sull'archivio corrente la scansione canonica resta circa 80–95 ms:
aggiungere oggi questa proiezione sarebbe prematuro.

## Decisione

Nessuna modifica al retrieval. Nessun cambiamento a personalità, stile o
generazione delle risposte. Il determinismo resta confinato a salvataggio,
ownership, snapshot e recupero riproducibile delle fonti.

Il trigram resta un esperimento ripetibile dietro opzione di benchmark, non una
proiezione attiva. Rivalutarlo quando il benchmark canonico `find-exact` supera
stabilmente 250 ms, quando il corpus reale si avvicina alla scala 50x, oppure
quando l'uso di exact lookup diventa abbastanza frequente da giustificare spazio
e build aggiuntivi.

## Preparazione preventiva off-by-default

È stato implementato il percorso opzionale `build-exact` / `find-exact
--backend trigram`, senza cambiare il default `scan` e senza costruzione
automatica. Sulla scala reale corrente:

- 279 sorgenti;
- build trigram: 221,892 ms;
- spazio derivato: 4.063.232 byte;
- parity exact: 2/2 PASS;
- gold generale: 14/14 PASS.

L'indice viene accettato soltanto su worktree pulito, è associato a HEAD e
manifest, viene ignorato da Git ed è eliminabile. Se assente o stale, il backend
trigram esplicito fallisce in modo chiaro; il backend scan predefinito continua
a leggere direttamente le fonti canoniche.
