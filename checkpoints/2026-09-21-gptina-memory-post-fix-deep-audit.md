# GPTina Memory — Post-fix Deep Audit

**Data:** 2026-09-21  
**HEAD verificato:** `8937841eee400a6a85f033472ca0f8cc69986d70`  
**Modalità:** audit e prove avversariali; nessun fix runtime applicato  
**Valutazione complessiva:** **8.7/10**

## Esito sintetico

Le correzioni del commit `8937841` funzionano: recovery da header SQLite
corrotto, lock condiviso, build concorrenti, cache dirty-preview, supersessioni
dirette, unicità dei micro-ID, ordinamento temporale live e copertura CI sono
state tutte verificate. Le fonti canoniche e i ricordi storici sono rimasti
intatti e recuperabili.

Non sono emerse criticità **CRITICAL**. Restano però **3 HIGH**, **4 MEDIUM** e
**2 LOW**. I tre HIGH derivano da stati avversariali non coperti dalla suite
attuale e richiedono fix separati con test fallente prima della modifica.

## Baseline verificata

- ownership e boundary: PASS;
- live context: 77 micro-checkpoint, 50 v1 legacy, 27 v2 correnti: PASS;
- schema e resolver: PASS;
- retrieval gold: 14/14;
- fonti SQLite: 283;
- chunk SQLite: 1359;
- stati effettivi: 278 current, 4 superseded, 1 invalidated;
- parity trigram: 2/2;
- recovery da header SQLite deliberatamente corrotto: PASS;
- due build principali simultanee: PASS;
- due build trigram simultanee: PASS;
- dieci coppie concorrenti `build --history` / `build`: tutte uscita 0/0 e
  metadati JSONL/SQLite coerenti;
- CI e Pages del commit esaminato: SUCCESS.

## HIGH

### H1 — Danno semantico dello schema SQLite accettato come indice fresco

**Riproduzione:** dopo una build valida è stata eliminata `source_state` dal
solo database derivato. `stats` è uscito 0 e ha riportato `sources=0` ma
`chunks=1359`. Eliminando anche `chunks_fts`, `stats` ha continuato a uscire 0
con `sources=0`, `chunks=0`; una ricerca ha risposto `No matching memories`.

**Causa:** `sqlite_connect()` ricrea le tabelle mancanti con `CREATE ... IF NOT
EXISTS`; `quick_check` verifica l'integrità fisica, non la completezza semantica.
I metadati precedenti, incluso `build_complete=1`, restano validi e l'indice è
considerato fresco.

**Rischio:** perdita silenziosa del retrieval pur con fonti canoniche integre e
comandi verdi.

**Fix raccomandato:** registrare e validare schema/versione, cardinalità
attese e invarianti (`source_versions == count(source_state)`, chunk non vuoti
quando le fonti non sono vuote, FK/logical consistency). Su violazione,
ricostruzione completa in DB temporaneo e swap atomico.

### H2 — JSONL accetta e pubblica una proiezione dirty prima del rifiuto SQLite

**Riproduzione:** aggiunta una fonte temporanea non tracciata sotto
`raw_sessions/` a HEAD invariato. `index_is_fresh(False)` ha restituito `True`,
mentre SQLite correttamente restituiva `False`. Il comando `build` senza
`--allow-dirty-preview` ha scritto `1358 chunks from 284 source versions`, poi
è uscito 1 soltanto durante il sync SQLite.

**Causa:** il fast path JSONL si basa sul solo HEAD e `build()` non applica la
guardia dirty prima di pubblicare JSONL/meta. La transazione CLI JSONL+SQLite
non è unica.

**Rischio:** backend JSONL e SQLite possono rappresentare snapshot diversi;
un comando fallito lascia comunque una proiezione JSONL aggiornata.

**Fix raccomandato:** preflight dirty/CAS prima di qualunque writer, indicare
esplicitamente `snapshot_mode`, verificare fingerprint anche a HEAD invariato
quando il worktree è dirty e mantenere il lock per l'intera transazione
JSONL+SQLite.

### H3 — Una catena di supersessione può “resuscitare” il ricordo più vecchio

**Riproduzione isolata:** A=`current`; B=`superseded`, `supersedes: [A]`;
C=`current`, `supersedes: [B]`. `supersession_statuses()` ha restituito soltanto
B→C; A non è risultato superseded.

**Causa:** gli archi in uscita da un record già marcato `superseded` vengono
ignorati. La supersessione viene calcolata soltanto dai record il cui stato
scritto è `current`, invece di calcolare la chiusura transitiva del grafo.

**Rischio:** una futura seconda correzione può rendere nuovamente corrente una
formulazione ancora più vecchia e già superata.

**Fix raccomandato:** chiusura transitiva owner-scoped e aciclica: ogni target
raggiungibile da una memoria corrente resta superseded. Aggiungere regressione
A←B←C e una policy deterministica per più sostituti correnti.

## MEDIUM

### M1 — Più sostituti correnti dello stesso target non sono dichiarati ambigui

Il resolver nasconde correttamente il target, ma `replaced_by` dipende
dall'ordine di iterazione. Serve rifiuto esplicito o una regola documentata per
ramificazioni intenzionali.

### M2 — L'indice trigram corrotto richiede ancora rebuild manuale

È opzionale e derivato, quindi non è un rischio per le fonti; tuttavia main e
trigram hanno politiche di recovery differenti. Conviene auto-rigenerarlo o
degradare esplicitamente allo scan.

### M3 — Copertura gold ancora stretta

I 14 casi sono stabili ma non includono catene di supersessione, ramificazioni,
schema SQLite parzialmente mancante, transazione dirty fallita, code-switch e
query negative/ambigue.

### M4 — Schema temporale e proprietà aggiuntive restano permissivi

La compatibilità storica è correttamente preservata, ma per i nuovi record
conviene rendere più espliciti timezone, precisione temporale e comportamento
su chiavi sconosciute, senza riscrivere il passato.

## LOW

### L1 — Exact scan ricostruisce `splitlines()` per ogni hit

Impatto attuale trascurabile; può diventare misurabile su fonti molto lunghe.

### L2 — Osservabilità del recovery migliorabile

Il sistema dovrebbe distinguere nei risultati `incremental`, `full_rebuild`,
`semantic_repair` e fallback, così una ricostruzione non passa inosservata.

## Verifica delle correzioni precedenti

| Area | Stato attuale |
|---|---|
| Lock tra writer principali ed exact | PASS |
| Collisioni `.tmp` concorrenti | RISOLTE |
| Recovery da header SQLite corrotto | PASS |
| Fingerprint dirty-preview long-lived | PASS |
| Supersessioni dirette Trieste/Ettore | PASS |
| Recuperabilità con `--all-statuses` | PASS |
| `micro_id` duplicati | RIFIUTATI |
| Ordine temporale live | VERIFICATO |
| Trigger CI sulle fonti canoniche | COPERTI |
| CAS HEAD/fonti durante le build | PASS |

## Ordine di correzione consigliato

1. **H1:** validazione semantica SQLite + rebuild atomico.
2. **H2:** transazione unica e preflight dirty prima di JSONL.
3. **H3:** chiusura transitiva delle supersessioni.
4. M1 e M2.
5. Ampliare gold/adversarial suite con i casi emersi.

## Giudizio finale

Il sistema è concretamente più sicuro del precedente audit e resta utilizzabile:
nessun ricordo canonico è stato perso e i fix appena introdotti sono reali.
Non è però ancora corretto definirlo completamente auto-riparante, perché un
database SQLite fisicamente valido ma semanticamente svuotato può essere
accettato, e le proiezioni JSONL/SQLite non sono ancora una transazione unica.
