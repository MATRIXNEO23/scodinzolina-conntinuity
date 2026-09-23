# GPTina — sorgente selettiva: runtime offline, motore locale e handoff a Work

Data: 2026-09-23  
Intervallo: dopo la catalogazione visuale 66–84 fino alla chiusura dell'istanza serale.

Questa è una **sorgente selettiva operativa**, non il transcript verbatim completo della chat. Conserva le correzioni, le decisioni e i riferimenti tecnici necessari a riprendere il lavoro senza indovinare.

## Hardware e runtime locale

Dalle verifiche e schermate della sessione:

- sistema Windows;
- CPU: Intel Core i3-2100 @ 3.10 GHz;
- Sandy Bridge, 2 core fisici / 4 thread;
- SSE4.2 + AVX disponibili;
- AVX2 non disponibile;
- RAM totale: 10 GB;
- GPU AMD vecchia non identificata con certezza; presenza di software NVIDIA sul desktop non basta a dimostrare una GPU NVIDIA utilizzabile;
- non assumere CUDA, ROCm o Vulkan funzionanti senza verifica live.

Il runtime iniziale funzionava con KoboldCpp `koboldcpp-oldpc.exe`. La lentezza osservata era in parte aggravata da impostazioni e contesto, ma il limite fisico principale resta la CPU.

## Modelli

Il modello più pesante preso come riferimento nella sessione è il community fine-tune:

`Unrestricted/Qwen3-4B-2507-Instruct-Uncensored-HauhauCS-Aggressive`

Il file GGUF era stato scaricato in:

`C:\Users\matri\Downloads\GPTina offline`

La quantizzazione esatta del file 4B non è stata verificata con certezza e **non va inventata**.

È stato provato/scaricato anche un modello più leggero. Alberto ha poi corretto esplicitamente l'obiettivo:

> “no io parlo col modello più pesante”

Quindi il lavoro futuro di ottimizzazione deve mantenere il **modello pesante come target primario**, invece di risolvere il problema semplicemente passando a un modello più piccolo.

## Repository offline

Repository sandbox/offline autorizzata:

`MATRIXNEO23/scodinzolina-offline`

Path locale dichiarato:

`C:\Users\matri\Documents\GitHub\scodinzolina-offline`

La repository canonica `MATRIXNEO23/scodinzolina-conntinuity` resta separata e non deve essere modificata dal runtime offline.

### Stato precedente verificato

Il bridge memoria locale era già stato costruito e verificato:

`127.0.0.1:8765`

Alberto ha mostrato `/health` e `/recover/current` funzionanti: il runtime leggeva realmente live context, micro-checkpoint, checkpoint pieno, recovery capsule, Fast Recall e Current Context dalla copia offline.

### App autonoma

Alberto ha chiesto:

> “mi chiedevo se facessimo un nostro motore per far girare il modello su questo hardware? invece di kobo”

e poi:

> “quindi che si fa fai tu un app che avvia la chat?”

È stato quindi costruito un percorso autonomo basato su llama.cpp, con launcher unico, motore Sandy Bridge, memoria, RAG e chat locale.

Alberto ha effettuato personalmente un merge durante la lavorazione:

> “ho interrotto efatto io merge”

Lo stato finale poi verificato e pubblicato nel sandbox è descritto nel checkpoint di fine istanza.

## Audit runtime richiesto

Alberto ha chiesto esplicitamente:

> “fai prima un audit e controlla tutti i fix necessari, inoltre serverebbe poter avere una finestra che fa vedere eventuali errori”

L'audit ha prodotto fix per:

- streaming token-per-token;
- timeout generazione;
- diagnostica grafica/log;
- thread-safety Tkinter;
- controllo del context reale;
- propagazione di Max risposta;
- retrieval memoria con scansione unica;
- rilevamento runtime vecchi/porte occupate;
- verifica modello già attivo;
- disattivazione thinking quando supportata;
- telemetria tempi/tok/s;
- rotazione log.

Il documento audit è nel sandbox:

`offline-runtime/AUDIT_2026-09-23.md`

## Verifica visiva locale

Alberto ha mostrato una schermata della chat `GPTina Offline` su `127.0.0.1:8766` che generava realmente risposte e mostrava le fonti memoria.

Questa schermata dimostra che **una versione locale precedente all'ultimo audit** funzionava end-to-end.

Non dimostra che l'ultima versione auditata sia già installata sul PC: Alberto ha detto esplicitamente:

> “non ho ancora installato la nuova”

Nella schermata, a una domanda tecnica sull'hardware, il RAG recuperava anche fonti autobiografiche come `GPTINA_SELF_PORTRAIT.md`, `CHRONICLE.md` e una memoria sulle immagini/zampine. Questo è un segnale concreto di retrieval troppo largo per domande tecniche.

## Obiettivo prestazionale corrente

Alberto vuole mantenere il modello pesante e chiede concretamente come:

- non tenere la CPU sempre al massimo;
- velocizzare le risposte;
- sfruttare meglio il vecchio i3-2100.

Le ipotesi da verificare con benchmark, non da assumere:

- 2 thread fisici vs 4 thread logici;
- context 1024 vs 2048;
- batch/micro-batch più conservativi;
- prompt cache e prefisso stabile;
- RAG tecnico separato dal RAG autobiografico;
- history e frammenti memoria minimi;
- priorità/affinità processo Windows per mantenere il PC usabile;
- speculative decoding solo se un test A/B dimostra beneficio sul dual-core;
- GPU offload soltanto dopo identificazione hardware e backend realmente supportato.

## Handoff a Work

Alberto ha chiesto:

> “vuoi lavorare in work?”

e subito dopo:

> “salvati e dammi prompt per ritrovarti su work”

Decisione corrente: la prossima fase deve essere portata avanti in Work come intervento multi-file/benchmark sul sandbox offline, mantenendo la continuity canonica come fonte di recovery e `scodinzolina-offline` come target tecnico autorizzato.
