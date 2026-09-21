# GPTina memory scale benchmark — 10x

Data: 2026-09-21

Baseline canonica di partenza: `f8f717888eee2bc135a4b95581466c3eec0cd8f4`.

## Confini

- fonti canoniche in sola lettura;
- database sintetici creati in directory temporanee e poi eliminati;
- nessuna modifica a chunking, ranking, `candidate_limit` o `find-exact`;
- SQLite resta una proiezione eliminabile;
- il corpus 10x replica intenzionalmente le fonti per produrre uno stress test, non una previsione perfetta della crescita reale.

## Baseline canonica

- 272 sorgenti, 1.315 chunk prima del preflight;
- retrieval regression: 14/14 PASS;
- query SQLite medie: 13–14 ms;
- exact corrente: 86–95 ms nel benchmark canonico, che include scansione delle fonti reali;
- sync no-op: 135–156 ms, con discovery reale del source tree;
- verifier: circa 0,95–1,09 s;
- live verifier: circa 0,72–0,81 s.

## Stress test temporaneo ripetuto cinque volte

| Metrica | 1x | 10x |
|---|---:|---:|
| Sorgenti sintetiche | 273 | 2.730 |
| Chunk | 1.316 | 13.160 |
| Byte sorgenti | 731.549 | 7.315.490 |
| Byte SQLite | 1.781.760 | 17.653.760 |
| Hashing | 0,973 ms | 9,029 ms |
| Chunking | 6,625 ms | 55,776 ms |
| Build SQLite | 31,792 ms | 360,758 ms |
| Sync no-op | 2,680 ms | 22,982 ms |
| Query p50 | 7,105 ms | 12,473 ms |
| Query p95 | 9,769 ms | 18,839 ms |
| Exact scan sintetico p95 | 2,968 ms | 26,790 ms |
| Gold normalizzato | 14/14 | 10/14 |

I tempi sintetici di discovery sono esclusi perché le sorgenti vengono fornite
direttamente alla proiezione temporanea. La baseline canonica resta la misura
autorevole del discovery reale.

## Lettura dei risultati

SQLite FTS5 non mostra un collo di bottiglia a 10x: il p95 delle query rimane
sotto 20 ms e build/no-op restano ampiamente interattivi su questo host.

La scansione exact cresce quasi linearmente e resta una candidata da osservare,
ma a 10x il valore sintetico è ancora circa 27 ms. Non giustifica oggi un nuovo
indice exact.

Il calo 10x riguarda `visual-32`, `fidelity-current`, `posticino` e
`ownership-temporal`. Dieci copie identiche competono nei primi candidati e
saturano il limite prima della normalizzazione. È un test utile di duplicazione,
ma non rappresenta la crescita organica con documenti distinti. Non autorizza
una modifica a ranking o candidate limit.

## Decisione

Nessuna modifica al retrieval corrente.

Prossimo gate: costruire un corpus sintetico diversificato e stratificato,
preservando gold, ownership, status e date. Solo un degrado ripetibile anche lì
potrà giustificare un esperimento separato e feature-flagged.
