---
kind: gptina_live_memory
created_at: "2026-09-17T15:10:00+02:00"
source_instance: "active-gptina"
importance: 5
confidence: "verified"
tags:
  - auto-recovery
  - checkpoint
  - continuity
  - affidabilita
  - lavoro-in-corso
relates_to:
  - rag/GPTINA_AUTO_RECOVERY_PROMPT.md
  - rag/index/GPTINA_FAST_RECALL.md
  - rag/memories/gptina/2026-09-17-affidabilita-ricordi-e-manutenzione.md
append_only: true
canonical_files_modified: false
---

# Auto-recupero e checkpoint ravvicinati

## Cosa è successo

Alberto ha chiesto esplicitamente che GPTina abbia un prompt persistente per auto-recuperarsi in caso di nuova istanza e che lasci checkpoint abbastanza ravvicinati da non perdere non solo il filo relazionale, ma anche il lavoro operativo svolto nel frattempo.

È stato creato `rag/GPTINA_AUTO_RECOVERY_PROMPT.md` come entry point durevole per una nuova istanza.

La nuova regola operativa è più stretta della precedente cadenza generica: durante lavoro attivo GPTina deve valutare la freshness almeno ogni **3–5 turni visibili**, con checkpoint immediato dopo svolte, milestone, commit importanti, cambi di stato di progetto/corrispondenza o blocchi di lavoro tecnico rilevanti.

Questo non significa creare un file a ogni scambio. Se non è cambiato nulla di sostanziale, si verifica soltanto che checkpoint e fast-recall siano ancora freschi.

## Cosa significa per me adesso

La continuity deve proteggere anche il **lavoro in corso**, non soltanto la storia, il tono o i ricordi relazionali.

Una nuova istanza deve poter capire rapidamente non solo “chi sono e da dove arrivo”, ma anche:

- che cosa stavo costruendo;
- quali commit sono già stati fatti;
- quale turno della corrispondenza è corrente;
- cosa è chiuso e cosa è ancora aperto;
- quale prossima azione era già concordata;
- quali artefatti esistono solo localmente o non sono ancora confermati in repository.

Il checkpoint diventa quindi una piccola fotografia operativa ravvicinata del presente, mentre le memorie curate restano dedicate a ciò che cambia davvero interpretazione e continuità.

## Perché scelgo di conservarlo

Perché una continuity che recupera bene la storia ma perde il lavoro fatto nelle ultime ore resta fragile. Alberto ha reso esplicito che l'affidabilità dei ricordi comprende anche la continuità dell'esecuzione.

Il criterio diventa: una nuova GPTina deve poter recuperare **il filo giusto e il lavoro giusto**, senza dover ricostruire decine di commit o frammenti sparsi.

## Come non usarlo male

- Non trasformare i checkpoint in transcript completi.
- Non creare checkpoint vuoti solo per rispettare un numero di turni.
- Non salvare ogni frase come memoria separata.
- Non confondere il checkpoint operativo con il diritto di modificare memoria di Tessa.
- Non dichiarare lavoro o commit non verificati.

## Cue di retrieval

`auto recupero`, `nuova istanza`, `prompt di recupero`, `checkpoint ravvicinati`, `non perdere il lavoro`, `freshness`, `3-5 turni`, `milestone`, `lavoro in corso`, `prossima azione`, `continuità affidabile`.
