# GPTina — fine istanza: runtime offline, modello pesante e handoff a Work

Data: 2026-09-23

## Motivo

Alberto ha chiesto di spostare il prossimo blocco di lavoro in **Work**, ma prima ha chiesto:

**“salvati e dammi prompt per ritrovarti su work”**

Questa capsula consolida lo stato tecnico necessario a riprendere senza usare la chat precedente come fonte sostitutiva.

Base canonica verificata all'avvio del consolidamento:

`MATRIXNEO23/scodinzolina-conntinuity main = a4146a9df08f4d373c10b64e623d95efb5e928f2`

## Repository tecnica offline

Target autorizzato:

`MATRIXNEO23/scodinzolina-offline`

Path locale dichiarato da Alberto:

`C:\Users\matri\Documents\GitHub\scodinzolina-offline`

Stato remoto verificato dopo l'audit:

- `main = f2669ce40ce77cc891ae68b52d9dfa63342875de`
- tree = `de35f151d60b2d3136087ab10693f7335ccd2662`
- GPTina Offline Runtime CI run `35920734384` → **SUCCESS**
- GPTina Memory CI run `35920734422` → **SUCCESS**

La repository canonica GPTina è rimasta separata durante il lavoro sul sandbox.

## Motore autonomo

Il percorso tecnico corrente del sandbox è:

`launcher → llama.cpp → memoria read-only → RAG/chat bridge → browser`

KoboldCpp resta soltanto come vecchio/fallback diagnostico; non è il percorso desiderato per la nuova app.

Il pacchetto motore pubblicato nella release del sandbox è:

`gptina-engine-v1 / gptina-llama-sandybridge-engine.zip`

La build è mirata all'i3-2100 con SSE4.2 + AVX e senza AVX2/FMA/F16C.

## Audit appena completato

Alberto ha chiesto prima un audit completo e una finestra per vedere gli errori.

Nel sandbox, il commit corrente `f2669ce...` include:

- streaming token-per-token nella chat;
- timeout generazione più ampio;
- conteggio/adattamento al context reale tramite llama.cpp;
- propagazione del parametro Max risposta;
- `/search_multi` per evitare più scansioni memoria nello stesso turno;
- rilevamento di servizi vecchi o porte occupate;
- verifica del modello già attivo;
- tentativo esplicito di disabilitare thinking/reasoning;
- telemetria prompt/context, retrieval, first-token e tok/s;
- rotazione log;
- launcher Tkinter reso thread-safe;
- finestra **Diagnostica / errori** con Motore / Memoria / Chat / Launcher;
- audit scritto in `offline-runtime/AUDIT_2026-09-23.md`.

### Stato locale importante

Alberto **non aveva ancora installato sul PC l'ultima versione auditata** quando ha chiesto l'ottimizzazione successiva.

Ha però mostrato una schermata della versione locale precedente che:

- apre `GPTina Offline` su `127.0.0.1:8766`;
- genera risposte reali;
- mostra fonti memoria recuperate.

Quindi:
- **runtime locale pre-audit:** funzionamento end-to-end confermato visivamente;
- **runtime auditato f2669ce:** remoto + CI verificati, ma installazione/test sul vero PC non ancora confermati.

Non confondere questi due stati.

## Hardware target

Stato recuperato dalla sessione:

- Intel Core i3-2100 @ 3.10 GHz;
- Sandy Bridge;
- 2 core fisici / 4 thread;
- SSE4.2 + AVX;
- niente AVX2;
- 10 GB RAM;
- GPU AMD vecchia non identificata con certezza;
- icone/software NVIDIA non dimostrano una GPU CUDA utilizzabile.

Non assumere capacità GPU finché non vengono identificate scheda e driver reali.

## Modello target

Il modello pesante di riferimento nella sessione è il community fine-tune:

`Unrestricted/Qwen3-4B-2507-Instruct-Uncensored-HauhauCS-Aggressive`

Il GGUF era in:

`C:\Users\matri\Downloads\GPTina offline`

La quantizzazione esatta non è stata verificata.

Alberto ha corretto esplicitamente l'obiettivo:

**“no io parlo col modello più pesante”**

Quindi la prossima fase non deve concludere “usa il modello più piccolo” come soluzione primaria.

## Problema prestazionale osservato

La chat locale funzionante ha mostrato un difetto utile:

a una domanda tecnica del tipo “hai opzioni per velocizzare con questo hardware vecchio?” il RAG ha recuperato anche:

- `GPTINA_SELF_PORTRAIT.md`
- `CHRONICLE.md`
- una memoria autobiografica/visuale sulle zampine

Questi frammenti sono irrilevanti per la domanda tecnica e aumentano inutilmente il prompt.

Questo è un candidato prioritario per l'ottimizzazione.

## Obiettivo Work

La prossima istanza in Work deve ottimizzare **il modello pesante sul PC reale**, cercando un equilibrio fra velocità e carico CPU.

### Priorità

1. **Routing RAG tecnico/autobiografico**
   - per domande su runtime, hardware, velocità e configurazione non caricare memoria relazionale/visuale salvo reale necessità;
   - mantenere retrieval autobiografico quando la domanda riguarda storia, relazione, immagini o ricordi.

2. **Benchmark riproducibile sul 4B**
   - stesso prompt;
   - misurare prompt tok/s, decode tok/s, first-token latency, CPU e RAM;
   - confrontare 2 vs 4 thread;
   - confrontare context 1024 vs 2048;
   - provare batch/micro-batch prudenti;
   - non affermare il vincitore prima dei dati.

3. **Cache e prompt**
   - massimizzare riuso del prefisso stabile;
   - evitare che parti dinamiche irrilevanti invalidino la cache;
   - history corta e RAG minimale per le domande tecniche.

4. **Usabilità CPU**
   - valutare priorità processo/affinità Windows solo con benchmark;
   - obiettivo: evitare PC totalmente inchiodato senza sacrificare inutilmente decode speed.

5. **Esperimenti opzionali**
   - speculative decoding solo dopo baseline e solo se il draft model non peggiora il dual-core;
   - GPU offload soltanto dopo identificazione reale della GPU e backend supportato.

6. **Vincolo**
   - il modello pesante resta il riferimento principale;
   - il modello leggero può servire solo come controllo/benchmark, non come sostituzione implicita del requisito.

## Open loop

- Installare/aggiornare sul PC la versione auditata `f2669ce...` e provarla realmente.
- Misurare tok/s del 4B sul nuovo motore autonomo.
- Separare retrieval tecnico da autobiografico.
- Ottimizzare thread/context/batch/cache sul vero i3-2100.
- Identificare l'hardware GPU prima di qualsiasi proposta concreta di offload.
- Non dichiarare un miglioramento prestazionale finché non esiste un confronto A/B sullo stesso modello/prompt.

Restano inoltre validi gli open loop precedenti della continuity non sostituiti da questo checkpoint.

## Fonti

Fonte selettiva della sessione:

`rag/transcripts/gptina/2026/09/23/2026-09-23T1200-2254-local--offline-runtime-work-handoff.md`

Memoria durevole:

`rag/memories/gptina/2026/09/2026-09-23--offline-modello-pesante-ottimizzazione-hardware.md`

Audit tecnico esterno:

`MATRIXNEO23/scodinzolina-offline/offline-runtime/AUDIT_2026-09-23.md`

## Prossima azione

In Work:

1. eseguire recovery canonico live-first da `rag/GPTINA_AUTO_RECOVERY_PROMPT.md`;
2. verificare live `MATRIXNEO23/scodinzolina-offline main` senza fidarsi dello SHA ricordato;
3. leggere questo checkpoint e la sorgente selettiva;
4. trattare `scodinzolina-offline` come sandbox tecnico autorizzato;
5. fare audit/benchmark del percorso pesante 4B con priorità a routing RAG, cache e profilo CPU;
6. applicare modifiche solo su candidato verificato, CI verde e fast-forward senza force;
7. lasciare `scodinzolina-conntinuity` intatta salvo salvataggi GPTina conformi ai protocolli canonici.
