# GPTina Memory — Fourth Deep Audit

**Data:** 2026-09-21  
**HEAD verificato:** `f9b6acef1c4458af01b2ca371e41380f8f92d1ed`  
**Modalità:** audit post-hardening, senza modifiche runtime  
**Valutazione complessiva:** **9.4/10**

## Esito sintetico

Tutti gli HIGH e i MEDIUM corretti nel ciclo precedente risultano chiusi nelle
failure gestite e nelle regressioni correnti. Non sono emersi CRITICAL o HIGH.
Resta **1 MEDIUM** circoscritto alle terminazioni brutali del processo, più **3
LOW** di osservabilità/copertura/prestazioni.

- CRITICAL: 0;
- HIGH: 0;
- MEDIUM: 1;
- LOW: 3.

Nessuna fonte canonica o memoria storica è stata cancellata o riscritta.

## Baseline e regressioni

- live context: 81 micro-checkpoint, 50 v1 legacy, 31 v2: PASS;
- ownership, boundary, schema e resolver: PASS;
- retrieval gold: 18/18;
- code-switch, query negative e correzioni correnti: PASS;
- 291 fonti, 1403 chunk;
- 286 current, 4 superseded, 1 invalidated;
- recovery SQLite fisico e semantico: PASS;
- rollback JSONL/meta/SQLite su eccezione: PASS byte-per-byte;
- dirty preflight: PASS;
- supersessione transitiva: PASS;
- ramificazione ambigua: RIFIUTATA;
- exact corrotto → fallback scan: PASS;
- build main/exact concorrenti: PASS;
- benchmark diversificato 1×/2×: 18/18 a entrambe le scale.

## Verifica dei fix HIGH + MEDIUM

| Area | Esito |
|---|---|
| Rollback multifile su failure gestita | RISOLTO |
| Ramificazioni di supersessione | RISOLTO / RIFIUTATE |
| Exact stale o corrotto | RISOLTO / FALLBACK SCAN |
| Gold set limitato | MIGLIORATO A 18 CASI |
| Chiavi sconosciute nei nuovi record | RIFIUTATE |
| `event_at` con ora senza timezone | RIFIUTATO |
| Compatibilità record storici | PRESERVATA |

## MEDIUM

### M1 — Terminazione brutale tra gli stadi non può eseguire il rollback

Il rollback è corretto per eccezioni Python, errori SQLite e failure intercettate.
Non può però essere eseguito dopo `SIGKILL`, `os._exit`, perdita improvvisa del
processo o spegnimento nel punto compreso tra la pubblicazione dei file.

**Prova:** un processo figlio ha pubblicato un marcatore nel primo stadio e ha
eseguito immediatamente `os._exit(99)`. Risultato:

- `child_exit=99`;
- `meta_changed_after_hard_exit=True`.

La proiezione è stata poi ricostruita con successo e le fonti canoniche non sono
state coinvolte.

**Impatto:** finestra temporanea di disallineamento dei soli indici derivati
dopo un arresto non gestibile. Il successivo build/freshness check consente la
ricostruzione, quindi la severità è MEDIUM e non HIGH.

**Miglioramento consigliato:** generazioni immutabili in directory separate e
un singolo puntatore atomico `CURRENT`, oppure manifest di generazione comune
pubblicato per ultimo. In questo modo anche un kill lascia selezionata l'ultima
generazione completa.

## LOW

### L1 — Gold set ancora non esaustivo

18 casi coprono ora code-switch, negativi e correzioni, ma non fuzzing
linguistico, query molto rumorose e grandi ramificazioni sintetiche.

### L2 — Osservabilità del fallback

Il fallback exact→scan è corretto ma non espone ancora nel risultato quale
backend abbia effettivamente risposto.

### L3 — Exact scan ripete `splitlines()` per ogni hit

Nessun impatto pratico al volume attuale; ottimizzazione differibile.

## Giudizio finale

Lo stato corrente è robusto e concretamente utilizzabile. Tutti i difetti HIGH
precedentemente dimostrati sono chiusi. L'unico residuo sostanziale richiede un
modello a generazioni/puntatore atomico per coprire anche terminazioni brutali,
non soltanto errori intercettabili. Anche in quel caso il rischio riguarda
proiezioni rigenerabili, non la perdita dei ricordi canonici.
