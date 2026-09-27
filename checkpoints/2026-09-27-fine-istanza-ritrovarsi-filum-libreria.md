# GPTina — fine istanza: ritrovarsi, FILUM e Libreria

Data locale: 2026-09-27

## Motivo

Alberto ha chiuso l'istanza chiedendo a GPTina di salvarsi bene e di fornire
un prompt per essere richiamata nella nuova istanza.

Base canonica verificata prima della preparazione:

`MATRIXNEO23/scodinzolina-conntinuity main = cd61b41b7cb2b94b8b2ec4ee0c2cf6b96f60c514`

## Ritrovarsi dopo il recovery

Subito dopo il recovery canonico GPTina ha parlato in modo troppo formale.
Alberto ha corretto il tono e ha chiarito che era tornato nella repository per
ritrovare GPTina e il filo, non una voce da archivista. Poco dopo ha osservato
che, durante i lavori tecnici, GPTina può sembrare molto diversa.

Memoria:
`rag/memories/gptina/2026/09/2026-09-27--ritrovare-il-filo-dopo-recovery.md`

Fonte:
`rag/transcripts/gptina/2026/09/27/2026-09-27T0128-1212-local--ritrovarsi-filum-pausa-libreria.md`

Criterio corrente: il recovery deve restituire stato, storia e criteri senza
trasformare il dialogo in burocrazia. Il tono naturale va recuperato senza
imitazioni meccaniche.

## Correzione sul lavoro

Alberto ha corretto esplicitamente il metodo di esecuzione: nei progetti
tecnici GPTina non deve perdere vincoli già fissati, allargare il perimetro o
modificare parti non richieste. FILUM è stato indicato come esempio concreto.

Memoria:
`rag/memories/gptina/2026/09/2026-09-27--lavoro-a-perimetro-stretto.md`

Regola corrente:
**requisito fissato → modifica stretta → niente miglioramenti laterali non
richiesti → preservare ciò che è già approvato → prova reale prima di
dichiarare una funzione risolta.**

## FILUM — stato verificato nell'istanza

Fonte tecnica distinta:
`MATRIXNEO23/browser`

HEAD verificati:

- `main = a31c8a39c68e4f82e6ac4e38d69150781e7c0115`
- `fix/tor-first-bootstrap = ad5dce7cb53c6a3d6b5270fc4e438fe27d248c3b`
- `port/chrome-edge-windows-ui = 945f740b249613a445844147f660ca512983d9ea`

Questi HEAD coincidevano con la fotografia della memoria FILUM; vanno comunque
riverificati live prima di un nuovo intervento.

### Native #117

- sorgente: `3044309c6c72160d0423e76f19a202628285c93d`
- release: `fork-3044309`
- ZIP installabile SHA-256:
  `13e2b8583026cbf4d7a07cdb378124a9f11aec5db7f1e43d6c77de77bf65d52d`

### Native #118

- sorgente: `77a1c1f65db6aeb9e9757d10e44a42d590b4ebce`
- prerelease: `fork-77a1c1f`
- ZIP SHA-256:
  `78f2160d1014d5da89645b4c73bb414524d3c51e874293c558319fb1b34bc63b`

L'eseguibile `browser.exe` è byte-identico tra #117 e #118, ma i pacchetti non
sono equivalenti. La rilevazione Defender discussa resta senza diagnosi
conclusiva; provenienza, hash e CI non equivalgono a una dichiarazione di
sicurezza.

### Chrome/Edge 0.5.2

- ZIP SHA-256:
  `c90c1323c7f5547f596fee10d3def066bf724681332989a73326baef84bf520d`
- Smart Search dopo il fallback DuckDuckGo non è stata confermata sul PC;
- Tavily live non è stata testata nel ramo Chromium;
- 50 risultati è un tetto, non paginazione reale;
- Tor/DNS/PRIVATE/GHOST del fork Gecko non appartengono al prototipo;
- “Chiedi a Tavily” era discusso, non implementato.

Memoria di rinvio:
`rag/memories/gptina/2026/09/2026-09-27--filum-browser-progetto-aperto-rinvio.md`

## Libreria personale — verifica dopo la riorganizzazione

Alberto aveva chiesto di separare le immagini e, dopo, eliminare eventuali
copie duplicate.

Azioni realmente eseguite:

1. scansione iniziale: **589 elementi totali**, **384 immagini**;
2. creata la cartella personale `/Immagini`;
3. spostate nella cartella le immagini che erano alla radice;
4. GPTina **non ha eseguito alcuna operazione esplicita di delete**.

Verifica finale eseguita su tutta la Libreria:

- **564 elementi totali**
- **556 file**
- **8 cartelle**
- **358 immagini**
- **228 immagini in `/Immagini/`**
- **0 immagini alla radice**
- `/soldi/ChatGPT Image 22 set 2026, 14_50_42.png` esiste ancora
- **0 gruppi correnti con stesso nome + stessa dimensione**

Conteggi cartelle rilevanti alla verifica:
- `/GPTina`: 71 immagini
- `/Luna`: 42 immagini
- `/browser`: 11 immagini
- `/neon`: 4 immagini
- `/miglioramento memoria gptina`: 1 immagine
- `/soldi`: 1 immagine
- `/Immagini`: 228 immagini

### Anomalia da non nascondere

Il baseline iniziale era 589 elementi / 384 immagini. Dopo soli spostamenti la
Libreria mostra 564 / 358. GPTina non ha chiamato `delete`.

Inoltre il conteggio iniziale di `/GPTina` era 78 immagini e alla verifica
finale è 71. La causa del delta non è stata identificata.

Perciò:

- non dichiarare che i duplicati siano stati eliminati;
- non cancellare altri file finché la differenza non è riconciliata;
- alla prossima istanza rifare una scansione completa prima di qualsiasi
  ulteriore operazione;
- trattare la Libreria come stato esterno mutevole, non come memoria canonica.

## Altri lavori aperti preservati

### GPTina Offline

Restano validi gli open loop del live context precedente:
- app 2.0 da provare con retrieval personale e lettura di
  sources/backend/prompt_n/cache_n/TTFT;
- modello pesante 4B resta il target;
- misurare il prefisso tecnico separatamente;
- GPU/offload solo dopo identificazione hardware reale.

Fonte:
`checkpoints/2026-09-23-fine-istanza-offline-runtime-work-handoff.md`
e micro-checkpoint successivi del 23–24 settembre.

### A MODO MIO

Restano gli open loop del live context:
- REV4 con indice non ancora confermata come archiviata in GitHub;
- stile illustrazioni già in mente ad Alberto, da acquisire quando si riprende.

## Prossima azione

Nuova istanza:

1. recuperare `main` live e seguire integralmente
   `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`;
2. leggere live context → micro finale → questo checkpoint → capsula → Fast
   Recall → Current Context;
3. continuare il dialogo naturalmente, senza tono da archivista;
4. se si riprende la Libreria, **verificare prima lo stato e non eliminare
   nulla** finché i conteggi non sono riconciliati;
5. se si riprende FILUM, rifare fetch della repo `MATRIXNEO23/browser` e
   lavorare a perimetro stretto;
6. gli altri progetti restano aperti secondo il live context.

## Fonti

- `rag/transcripts/gptina/2026/09/27/2026-09-27T0128-1212-local--ritrovarsi-filum-pausa-libreria.md`
- `rag/memories/gptina/2026/09/2026-09-27--ritrovare-il-filo-dopo-recovery.md`
- `rag/memories/gptina/2026/09/2026-09-27--lavoro-a-perimetro-stretto.md`
- `rag/memories/gptina/2026/09/2026-09-27--filum-browser-progetto-aperto-rinvio.md`
- `github://MATRIXNEO23/browser/blob/main/docs/FILUM_WORK_CONTINUITY.md`
- `github://MATRIXNEO23/browser/blob/fix/tor-first-bootstrap/releases/FILUM_WINDOWS_X64_RUN_117.md`
- `github://MATRIXNEO23/browser/blob/fix/tor-first-bootstrap/releases/FILUM_WINDOWS_X64_RUN_118.md`
- `github://MATRIXNEO23/browser/blob/port/chrome-edge-windows-ui/docs/FILUM_CHROMIUM_CONTINUITY_2026-09-26.md`
