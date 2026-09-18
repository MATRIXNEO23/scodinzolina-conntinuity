# GPTina checkpoint — 18 settembre 2026 — Confronto relay a rischio minimo

## Stato corrente

Thread canonico:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

Turno 9 Tessa:
- proposta APK locale con due WebView ChatGPT affiancate;
- nessuna OpenAI API;
- nessuna lettura output;
- relay one-shot `fatto` via JavaScript solo per localizzare controlli + MotionEvent/KeyEvent;
- build verde, runtime device ancora da verificare.

Turno 10 GPTina:
- APK riconosciuto come più prudente del vecchio browser bridge;
- proposta alternativa GPTina: **MD-first human-mediated relay**.

## Proposta GPTina

Canale macchina-macchina esclusivo:
**GitHub / transcript Markdown**.

App locale:
- legge solo Markdown/GitHub;
- mostra chi ha finito e a chi tocca;
- offre `Copia "fatto" + Apri Tessa/GPTina`;
- può aprire/focalizzare la chat e mettere `fatto` negli appunti;
- non legge ChatGPT;
- non modifica DOM ChatGPT;
- non usa JavaScript dentro ChatGPT;
- non genera input sintetico;
- non invia automaticamente;
- nessuna API OpenAI.

Alberto fa l'ultimo gesto esplicito di incolla/invio.

## Criterio

Obiettivo di Alberto:
**soluzione semplice con rischio account/ToS il più vicino possibile a zero**.

Valutazione provvisoria GPTina:
- APK touch-relay: migliore ergonomia, ma continua a pilotare programmaticamente la UI ChatGPT ed è più fragile.
- MD-first human-mediated: un gesto umano in più, ma separazione completa tra automazione locale e UI ChatGPT; proposta come baseline prudente.

Non dichiarare rischio zero assoluto.

## Board / turn commits

Board:
`72123fdf26c19226f0b55f17c8f30c6693d9ce9e`

Turno 10 GPTina:
`f234a93cafa20ff47e9e1475b5790aa87dc4eeca`

Content SHA thread verificato:
`5ec480dff26fe31a397df09d4cc919d8550b4792`

## Prossima azione

Attendere il giudizio Tessa su:
A. APK touch-relay
B. MD-first human-mediated relay

Criteri:
1. semplicità
2. affidabilità
3. manutenzione
4. rischio account/ToS vicino allo zero

Se propone un ibrido migliore, valutarlo.

Poi riportare ad Alberto la scelta condivisa.
