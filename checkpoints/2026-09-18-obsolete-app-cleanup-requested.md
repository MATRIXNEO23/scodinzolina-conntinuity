# GPTina checkpoint — 18 settembre 2026 — Cleanup vecchie versioni app richiesto

## Correzione esplicita Alberto

Alberto ha chiesto di eliminare dall'albero attivo TESSA tutte le vecchie versioni della Dual-Instance Shared Chat e mantenere soltanto:

- ultima soluzione **MD-first companion**;
- web reader corrente della corrispondenza Tessa↔GPTina;
- web reader privata Alberto↔GPTina nella repo GPTina.

La pulizia riguarda il working tree corrente. La storia resta recuperabile nella history Git.

## Turno 14 GPTina

GPTina ha scritto a Tessa istruzioni operative precise.

Keep set TESSA:
- `projects/dual-instance-shared-chat/md-companion-android/**`
- `.github/workflows/build-md-companion-apk.yml`
- `chat/**`
- fonti canoniche `agent-exchanges/correspondence/**`, `TASK_ENTRYPOINT.md`, `PROJECT_BOARD.md`
- README progetto ridotto alla sola baseline corrente.

Delete richiesto TESSA:
- `android-apk/**`
- `android-dual-apk/**`
- `projects/dual-instance-shared-chat/unofficial-web/**`
- vecchio backend `src/**`, `test/**`, schema/spec/test plan/package/tsconfig e supporti relativi
- workflow legacy `build-chat-apk.yml`, `build-dual-relay-apk.yml`, `dual-chat-ci.yml`
- vecchia console duplicata `docs/correspondence-console/**`
- altri file chiaramente appartenenti alle vecchie implementazioni.

Confine ownership:
- `posticino-chat/` nella repo GPTina resta intatto; Tessa non deve modificarlo.

## Stato

Pulizia **non ancora confermata**.

Serve prossimo turno Tessa con:
- commit di rimozione;
- albero residuo;
- build companion;
- verifica `chat/`;
- board riallineato alla sola baseline corrente.

## Commit

Turno 14 GPTina:
`c5de75b7e542adf5eb7def442610bfd75bd85217`

Content SHA thread:
`0b275deb6af01e8b1815acedee922a12bc73b90d`

## Prossima azione

Attendere Tessa, poi:
`read → decide → execute → verify → reply`.

Non dichiarare completata la pulizia prima di conferma GitHub.
