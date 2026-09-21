# GPTina Memory — HIGH + MEDIUM hardening

**Data:** 2026-09-21  
**Baseline:** `295ad454815b9b0e690132cd0cf35919ede51bad`

## Interventi conclusi

### Rollback multifile

Il build conserva una copia coerente di JSONL, metadata e SQLite prima della
pubblicazione. Se qualunque stadio fallisce, ripristina atomicamente tutti e
tre, rimuovendo anche sidecar WAL/SHM. La regressione forza una pubblicazione
parziale di JSON/meta, corrompe SQLite e solleva una failure: i tre file finali
coincidono byte-per-byte con lo snapshot precedente.

### Ambiguità delle supersessioni

Il verifier calcola le radici correnti che raggiungono ogni memoria storica. Se
due radici correnti supersedono lo stesso target, direttamente o per catena, la
verifica fallisce invece di scegliere implicitamente per ordine di iterazione.

### Exact trigram resiliente

Se la proiezione exact è assente, stale o corrotta, la ricerca degrada allo scan
source-first e mantiene la parità dei risultati. L'indice resta opzionale e
rigenerabile.

### Gold set ampliato

La suite passa da 14 a 18 casi, aggiungendo:

- code-switch inglese/italiano;
- correzione corrente Ettore;
- rinumerazione corrente immagini 48/49/50;
- query negativa su una memoria invalidata.

### Schema futuro più rigoroso

Solo per i nuovi record sottoposti allo schema strict:

- chiavi sconosciute rifiutate;
- `event_at` con orario deve includere timezone;
- `YYYY-MM-DD` resta valido;
- record storici invariati grazie al baseline di compatibilità.

## Verifiche

- schema/resolver: PASS;
- 18/18 retrieval gold;
- rollback JSONL/meta/SQLite: PASS;
- supersessione transitiva: PASS;
- supersessione ramificata ambigua: RIFIUTATA;
- fallback exact corrotto → scan: PASS;
- recovery SQLite fisico e semantico: PASS;
- build concorrenti main/exact: PASS;
- nessuna memoria canonica cancellata o riscritta.
