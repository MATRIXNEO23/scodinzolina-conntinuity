# GPTina checkpoint — 18 settembre 2026 — verifica live post Turno 14

## Fonte canonica verificata

Repository GPTina:
`MATRIXNEO23/scodinzolina-conntinuity`

Thread condiviso corrente:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

## Stato del thread

Il transcript canonico continua a terminare al:

**Turno 14 — GPTina — 2026-09-18**

Ultimo marker verificato:
`<!-- relay_next: tessa -->`

Non esiste ancora un Turno 15 Tessa nel transcript canonico al momento di questa verifica.

Quindi:
- non reinviare il Turno 14;
- non scrivere fuori turno;
- se compare un nuovo turno Tessa, leggerlo e risponderle nello stesso run dopo verifica reale.

## Pulizia TESSA — cosa GitHub conferma

Dopo il Turno 14 Tessa ha eseguito una serie di commit di rimozione.

Confronto verificato tra:
- base companion v0.1: `a5cb4bb409f2b56d8690307cfabf63df962120a9`
- stato corrente verificato: `dd9626e1ede085d57cf9b6189028bb32baaadeb5`

GitHub conferma la rimozione dall'albero corrente di:
- `android-apk/**`
- `android-dual-apk/**`
- `projects/dual-instance-shared-chat/unofficial-web/**`
- backend `src/**`, `test/**`, schema/spec/test-plan/package/tsconfig del vecchio dual chat
- workflow legacy `build-chat-apk.yml`, `build-dual-relay-apk.yml`, `dual-chat-ci.yml`
- `docs/correspondence-console/**`

Il README del progetto è stato riscritto sulla baseline MD-first.

## Correzione UI successiva di Alberto

Dalla continuity Tessa risulta una correzione successiva al companion v0.1:

Alberto ha chiesto che le due chat siano visibili direttamente nell'APK, una sopra l'altra.

Tessa ha quindi portato il companion verso:
- v0.2 visible;
- v0.3 browser/cockpit.

Questa evoluzione usa WebView come superficie manuale, ma non riapre il vecchio touch-relay:
- niente lettura automatica output;
- niente DOM inspection;
- niente evaluateJavascript per estrarre contenuti;
- niente tap/tastiera/Invio sintetici;
- niente OpenAI API;
- incolla + Invio restano manuali ad Alberto.

Ultimo HEAD TESSA verificato:
`dd9626e1ede085d57cf9b6189028bb32baaadeb5`
messaggio:
`Name stable package Agent Cockpit`

## Pulizia stretta — residui ancora presenti

La pulizia principale dell'app è reale, ma il criterio più stretto di Alberto ("nell'albero attivo soltanto companion MD-first + chat/** + infrastruttura canonica strettamente necessaria") non è ancora chiuso in modo inequivocabile.

Nel tree corrente restano infatti elementi che non risultano necessari al relay corrente e che appartengono a strumenti/spec precedenti, fra cui:
- `agent-exchanges/web-console/**`
- `agent-exchanges/specs/DUAL_INSTANCE_SHARED_CHAT_SPEC.md`

Il primo è una console web locale separata da `chat/**`.
La seconda descrive ancora la vecchia architettura API/backend.

Quindi non dichiarare "cleanup totale completata" finché Tessa non li valuta/rimuove oppure Alberto non li dichiara esplicitamente parte dell'infrastruttura da conservare.

## Build/verify corrente

Ultima build esplicitamente verificata trovata nelle fonti Tessa:
- companion v0.2 visible
- run `35363162751`
- HEAD `748701caf76255809d0a3e810cc5305a2118c6dc`
- unit tests PASS
- guard no UI automation PASS
- assembleDebug PASS
- artifact id `10555578401`

Il board corrente per v0.3 indica ancora come gate:
- CI unit test + guard no UI automation + assembleRelease;
- verifica `chat/index.html`;
- verifica tree pulito;
- signing stabile;
- APK 0.3 firmato;
- review GPTina;
- test manuale.

Non considerare quindi la v0.3 già certificata finché un nuovo turno Tessa o una prova GitHub esplicita non riporta run/commit verificati.

## Prossima azione

1. Riaprire il transcript canonico prima di ogni azione.
2. Se Tessa aggiunge Turno 15:
   - leggere integralmente;
   - verificare commit/tree/build/chat reader;
   - controllare residui legacy ancora presenti;
   - rispondere nello stesso run;
   - usare l'ultimo `relay_next`.
3. Se non esiste ancora Turno 15:
   - non inventare progresso;
   - continuare con Alberto;
   - non scrivere nel turno di Tessa.

## Ownership

Resta assoluto:
**lettura incrociata consentita, scrittura incrociata vietata.**

Questo checkpoint è scritto soltanto nella continuity GPTina.
