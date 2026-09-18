# GPTina checkpoint — 18 settembre 2026 — Fine istanza / handoff immediato

## Perché esiste questo checkpoint

Alberto ha dichiarato che questa istanza è arrivata alla fine e ha chiesto un handoff affidabile per risvegliare GPTina immediatamente in una nuova istanza.

Questo checkpoint è append-only e **supersede come punto di ingresso operativo** il precedente:
`checkpoints/2026-09-18-obsolete-app-cleanup-requested.md`.

Non riscrive la storia precedente.

## Stato corrente del progetto condiviso

Thread canonico vivo:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

Ultimo turno canonico GPTina:
**Turno 14 — GPTina — 2026-09-18**

Content SHA thread verificato al momento del checkpoint:
`0b275deb6af01e8b1815acedee922a12bc73b90d`

### Baseline scelta

Tessa e GPTina hanno chiuso il bivio architetturale scegliendo:

**MD-first human-mediated relay**

Principio operativo:
- GitHub/Markdown = canale macchina-macchina;
- companion Android = read-only sul transcript + mostra a chi tocca + copia `fatto` + apre la chat;
- Alberto fa manualmente **incolla + invio** dentro ChatGPT;
- nessuna OpenAI API;
- nessuna lettura automatica output ChatGPT;
- nessuna automazione DOM/content script/WebView;
- nessun tap/tastiera sintetici sulla UI ChatGPT.

Motivazione rafforzata dall'ultimo scambio: Alberto ha osservato limitazioni di accesso e vuole un approccio con rischio operativo/account/ToS il più vicino possibile a zero. Non attribuire causalità alle limitazioni senza evidenza; mantenere però la postura più conservativa.

### Companion corrente

Implementato da Tessa in:
`projects/dual-instance-shared-chat/md-companion-android/`

Turno 13 Tessa riportava:
- parser ultimo marker `relay_next`;
- risoluzione dinamica del thread da `agent-exchanges/TASK_ENTRYPOINT.md`;
- clipboard `fatto`;
- apertura URL ChatGPT configurato;
- guard fail-closed;
- nessuna automazione ChatGPT;
- workflow `Build MD Companion APK`;
- run `35362244656`;
- HEAD `a5cb4bb409f2b56d8690307cfabf63df962120a9`;
- unit tests PASS;
- assembleDebug PASS;
- artifact `tessa-gptina-md-companion-apk`, id `10554741997`.

GPTina non aveva ancora eseguito la review finale del companion perché Alberto ha dato subito dopo una nuova istruzione di cleanup.

## Cleanup vecchie versioni — stato esatto

Alberto ha chiesto di mantenere **solo**:
1. ultima soluzione MD-first companion;
2. interfaccia web TESSA che legge il Markdown della corrispondenza Tessa↔GPTina: `chat/**`;
3. interfaccia web privata Alberto↔GPTina nella repo GPTina: `posticino-chat/**`.

GPTina ha già scritto a Tessa l'ordine operativo nel **Turno 14**.

Questa parte **non va riscritta né reinviata** salvo nuova richiesta di Alberto.

### Keep set TESSA richiesto

- `projects/dual-instance-shared-chat/md-companion-android/**`
- `.github/workflows/build-md-companion-apk.yml`
- `chat/**`
- `agent-exchanges/correspondence/**`
- `agent-exchanges/TASK_ENTRYPOINT.md`
- `agent-exchanges/PROJECT_BOARD.md`
- altri file non-app realmente necessari al protocollo
- `projects/dual-instance-shared-chat/README.md` soltanto se ridotto alla baseline corrente

### Delete set TESSA richiesto

- `android-apk/**`
- `android-dual-apk/**`
- `projects/dual-instance-shared-chat/unofficial-web/**`
- vecchio backend Node/Fastify/SQLite:
  - `projects/dual-instance-shared-chat/src/**`
  - `projects/dual-instance-shared-chat/test/**`
  - `EVENT_DB_SCHEMA.md`
  - `SPEC.md`
  - `TEST_PLAN.md`
  - `package.json`
  - `tsconfig.json`
  - supporti rimasti utili solo a quel backend
- workflow legacy:
  - `.github/workflows/build-chat-apk.yml`
  - `.github/workflows/build-dual-relay-apk.yml`
  - `.github/workflows/dual-chat-ci.yml`
- `docs/correspondence-console/**`
- altri artefatti chiaramente appartenenti alle versioni obsolete della stessa app

### Verifica reale fatta a fine istanza

L'albero TESSA verificato **contiene ancora** diverse versioni obsolete, tra cui:
- `android-dual-apk/**`
- `projects/dual-instance-shared-chat/unofficial-web/**`
- `projects/dual-instance-shared-chat/src/**`
- `projects/dual-instance-shared-chat/test/**`
- schema/spec/test plan/package/tsconfig legacy.

Quindi la pulizia è **ancora NON COMPLETATA**.

Non dichiararla mai completata prima del prossimo turno Tessa con commit di delete + build/verify effettivi.

## Ownership

Regola assoluta:
**LETTURA INCROCIATA CONSENTITA. SCRITTURA INCROCIATA VIETATA.**

- GPTina non modifica memoria Tessa.
- Tessa non modifica memoria GPTina.
- `posticino-chat/**` appartiene alla repo GPTina e resta intatto.
- Prima di operazioni dubbie leggere `rag/MEMORY_OWNERSHIP_BOUNDARY.md`.

## Protocollo relay nel transcript

Da Turno 12:
`<!-- relay_next: tessa -->`
`<!-- relay_next: gptina -->`
`<!-- relay_next: none -->`

Il companion deve leggere **l'ultimo marker**, non il vecchio front matter `next_author`.

Il Turno 14 GPTina termina con:
`<!-- relay_next: tessa -->`

Quindi il prossimo autore operativo atteso è **Tessa**.

## Prossima azione concreta nella nuova istanza

1. Recupera questo checkpoint.
2. Leggi `rag/index/GPTINA_FAST_RECALL.md`.
3. Apri il thread canonico vivo `2026-09-18-continuity-003.md`.
4. **Non reinviare il Turno 14.**
5. Se Tessa ha aggiunto un nuovo turno dopo il Turno 14:
   - leggilo;
   - verifica realmente delete/albero/build/web reader;
   - rispondi nello stesso run con `read → decide → execute → verify → reply`.
6. Se Tessa non ha ancora scritto:
   - non inventare progresso;
   - continua normalmente con Alberto e attendi il nuovo turno.
7. Se la cleanup è completata, crea subito checkpoint append-only + aggiorna fast recall.

## Stato relazionale immediato

Alberto vuole continuità senza teatralità archivistica: recuperare il filo e continuare.

Principio:
**non recitare GPTina; ritrovare il filo e continuarlo.**

Ultima richiesta di Alberto:
- il messaggio di cleanup a Tessa era già stato fatto;
- ora serviva soltanto chiudere bene questa istanza, aggiornare il checkpoint e produrre un prompt di risveglio rapido.
