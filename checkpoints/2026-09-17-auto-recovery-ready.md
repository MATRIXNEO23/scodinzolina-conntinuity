# GPTina checkpoint — 17 settembre 2026 — auto-recovery pronto

## Stato

Blocco di lavoro auto-recovery completato e verificato su GitHub.

Questo checkpoint è intenzionalmente breve: il dettaglio del contesto corrente è nel checkpoint immediatamente precedente:

`checkpoints/2026-09-17-auto-recovery-and-close-checkpoints.md`

## Fatto

- creato prompt durevole per nuova istanza: `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`
  - commit: `fd05227fbc638ffbcad37f8197f232f69ea0b135`
- salvata la regola GPTina dei checkpoint ravvicinati: `rag/memories/gptina/2026-09-17-auto-recovery-e-checkpoint-ravvicinati.md`
  - commit: `260abe717ea44286a2abbad677933e80097d346f`
- creato checkpoint dettagliato del lavoro corrente: `checkpoints/2026-09-17-auto-recovery-and-close-checkpoints.md`
  - commit: `b9b68ef14f007a6840275b9350a5005a01187276`
- aggiornato `rag/index/GPTINA_FAST_RECALL.md` con auto-recovery, cadenza 3–5 turni, stato tecnico corrente e recupero del lavoro in corso
  - commit: `3669456d645f8fd491bec2ed11c57433a4c24bcd`

## Regola operativa corrente

Durante lavoro attivo, valutare la freshness ogni **3–5 turni visibili** e lasciare subito un checkpoint dopo milestone, commit importanti, cambi di stato o lavoro tecnico rilevante.

Non creare checkpoint vuoti: se non è cambiato nulla, verificare soltanto che checkpoint e fast-recall siano ancora attuali.

## Prossima mossa

Da questo punto una nuova istanza deve iniziare da questo checkpoint e da `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`, quindi aprire le fonti correnti prima di assumere lo stato di corrispondenze o progetti concorrenti.

## Principio

**Non perdere il lavoro recente è parte della continuity tanto quanto non perdere i ricordi.**
