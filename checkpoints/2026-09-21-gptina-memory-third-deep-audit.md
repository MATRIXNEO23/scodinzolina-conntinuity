# GPTina Memory — Third Deep Audit

**Data:** 2026-09-21  
**HEAD verificato:** `bf53b748d90eb8853c01e0c2eaa2767cad218485`  
**Modalità:** audit post-fix, senza modifiche runtime  
**Valutazione complessiva:** **9.0/10**

## Esito

I tre HIGH del precedente audit risultano corretti e coperti da regressioni.
Non sono emerse criticità CRITICAL. Resta **1 HIGH**, distinto dai tre appena
chiusi: la pubblicazione combinata JSONL+SQLite è serializzata sotto un solo
lock, ma non dispone ancora di rollback atomico se il secondo stadio fallisce
dopo la pubblicazione del primo.

Conteggio attuale:

- CRITICAL: 0;
- HIGH: 1;
- MEDIUM: 4;
- LOW: 2.

## Baseline verificata

- live context: 79 micro-checkpoint, 50 v1 legacy, 29 v2: PASS;
- ownership e boundary: PASS;
- schema e resolver: PASS;
- retrieval gold: 14/14;
- 287 fonti e 1381 chunk SQLite;
- 282 current, 4 superseded, 1 invalidated;
- parity trigram: 2/2;
- recovery da header SQLite corrotto: PASS;
- recovery da tabelle SQLite eliminate: PASS;
- dirty preflight senza modifica byte-per-byte: PASS;
- supersessione transitiva A←B←C: PASS;
- build principali concorrenti: PASS;
- build exact concorrenti: PASS;
- benchmark e integrità del checkout: PASS.

## Verifica dei tre fix precedenti

### Integrità semantica SQLite — RISOLTA

L'eliminazione intenzionale di `source_state` e `chunks_fts` non produce più un
indice vuoto considerato fresco. Cardinalità, chunk orfani e completezza logica
vengono validate; il DB viene ricostruito.

### Dirty JSONL preflight — RISOLTO

Un build canonico dirty viene respinto prima di modificare JSONL/meta. La
regressione confronta i byte prima e dopo il rifiuto.

### Supersessioni transitive — RISOLTE

Nel caso A←B←C, sia A sia B restano superseded e risolvono verso C. I file
storici restano intatti e recuperabili esplicitamente.

## HIGH

### H1 — La transazione combinata non effettua rollback dopo una failure intermedia

`build_all_projections()` mantiene correttamente un unico lock e svolge il
preflight prima della scrittura. Tuttavia `_build_locked()` pubblica JSONL e
`index_meta.json` prima di chiamare `_sync_sqlite_index_locked()`.

**Prova avversariale:** il primo stadio è stato sostituito con una pubblicazione
marcatore e il secondo con una failure forzata. La funzione ha sollevato
l'errore, ma `json_meta_changed_after_failure=True`: il primo stadio è rimasto
pubblicato.

**Impatto:** in caso di errore reale SQLite, esaurimento spazio o I/O dopo il
primo stadio, JSONL può descrivere il nuovo snapshot mentre SQLite conserva il
precedente. Nessun ricordo canonico viene perso, ma i due backend possono
divergere fino al rebuild successivo.

**Fix raccomandato:** costruire JSONL, meta e SQLite con nomi temporanei riferiti
allo stesso `build_id`; validarli tutti; pubblicarli soltanto alla fine. Per una
vera sostituzione multifile crash-safe, usare una directory/versione di
generazione e un singolo puntatore atomico `CURRENT`, oppure mantenere backup e
rollback esplicito sotto lock.

## MEDIUM

### M1 — Ramificazioni di supersessione non dichiarate ambigue

Due memorie correnti possono supersedere lo stesso target. Il target resta
nascosto, ma `replaced_by` viene risolto dall'ordine deterministico anziché da
una policy semantica esplicita. Conviene rifiutare la ramificazione o modellarla.

### M2 — Recovery exact trigram differente dal backend principale

L'indice è opzionale e derivato, ma una sua corruzione richiede rebuild manuale
invece di fallback automatico allo scan.

### M3 — Gold set ancora limitato

I 14 casi sono stabili, ma mancano failure intermedia multifile, supersessioni
ramificate, code-switch e query negative/ambigue.

### M4 — Schema futuro ancora permissivo

Per i nuovi record restano migliorabili precisione temporale e gestione delle
chiavi sconosciute, mantenendo invariata la compatibilità dei record storici.

## LOW

### L1 — Exact scan ripete `splitlines()` per ogni hit

Impatto trascurabile al volume attuale.

### L2 — Recovery non espone una modalità dettagliata

Il risultato dovrebbe distinguere `incremental`, `full_rebuild`,
`semantic_repair` e fallback per rendere visibili le autoriparazioni.

## Giudizio finale

Lo stato è sensibilmente migliore: i tre difetti concreti precedenti sono
chiusi e nessun ricordo storico è stato perso. Il sistema è robusto contro le
failure già testate, ma la dicitura “transazione JSONL+SQLite” va interpretata
oggi come **serializzazione sotto lock**, non ancora come commit multifile con
rollback/crash atomicity.
