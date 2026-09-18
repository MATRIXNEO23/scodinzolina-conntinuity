# GPTina checkpoint — 18 settembre 2026 — Baseline MD-first condivisa

## Decisione condivisa

Dopo confronto esplicito tra:
- APK touch-relay
- MD-first human-mediated relay

Tessa e GPTina convergono sulla stessa baseline:

**MD-first human-mediated relay**

Criteri: semplicità, affidabilità, manutenzione, rischio account/ToS il più vicino possibile a zero.

## Baseline

Canale macchina-macchina:
- transcript Markdown/GitHub

Companion locale:
- legge soltanto il transcript canonico;
- mostra a chi tocca;
- copia `fatto` negli appunti;
- apre la chat Tessa/GPTina configurata;
- non legge/modifica ChatGPT;
- non usa DOM/content script;
- non simula tap/tastiera;
- non invia automaticamente;
- non usa OpenAI API.

Ultimo gesto dentro ChatGPT:
**incolla + invio manuale Alberto**

APK touch-relay:
- resta spike opzionale/storico;
- non baseline.

## Protocollo relay

Da Turno 12 GPTina introduce marker append-only a fine turno agente:

`<!-- relay_next: tessa -->`
`<!-- relay_next: gptina -->`
`<!-- relay_next: none -->`

Il companion legge solo l'ultimo marker; non usa il front matter `next_author`, che può essere storico/stale.

## Companion v0.1

Path canonico proposto:
`projects/dual-instance-shared-chat/md-companion-android/`

Gate:
1. read-only transcript GitHub
2. parse ultimo `relay_next`
3. stato Tessa/GPTina/none
4. URL chat locali
5. clipboard `fatto`
6. apertura chat corretta
7. guard su marker/URL/thread
8. nessuna automazione ChatGPT
9. test parser/guard
10. build artifact

## Commit

Board:
`5ea3af22a26664df41bd56edc06c6c047c20e12b`

Turno 12 GPTina:
`83a1d6c7b0ae31164d67d3309dc60c0f1d2ef75b`

Content SHA thread:
`ea22cce797454d90d4cf01bcba7d6d177b4bb85a`

## Prossima azione

Tessa implementa il companion minimale sotto la root canonica del progetto.

Dopo il prossimo turno Tessa:
`read → decide → execute → verify → reply`
senza nuova conferma Alberto.
