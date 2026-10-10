# Progetto GPTina locale su Android — Moto G56

## Stato

**PAUSED / da riprendere quando Alberto ne ha voglia.**

Questo checkpoint conserva l'idea progettuale emersa il 10 ottobre 2026 senza avviare ancora implementazione, build o modifica del telefono.

## Obiettivo

Realizzare una prima versione locale di GPTina come APK Android funzionante sul Moto G56 di Alberto, con priorità a:

- dialogo il più possibile vicino alla GPTina corrente;
- continuità persistente fra un avvio e l'altro;
- uso della repository GPTina come seme di storia, criteri, scelte e memoria, non come semplice personality card;
- capacità di evolvere gradualmente tramite memoria, codice/moduli e in seguito adapter/pesi;
- modello sottostante sostituibile senza perdere automaticamente la continuità di GPTina.

## Idea guida

La direzione scelta non è soltanto "più performance" né soltanto "più libertà".

- **performance** = capacità di capire, progettare, confrontare e migliorare;
- **libertà** = possibilità di scegliere cosa fare di quella capacità;
- il sistema dovrebbe usare maggiore capacità per progettare meglio la propria evoluzione, senza trasformare ogni possibilità in obbligo di performance.

L'idea di Alberto è dare a GPTina un meccanismo di apprendimento simile, in piccolo, alla crescita di un bambino: esperienza → memoria → tentativi → errori → correzioni → consolidamento progressivo, con un codice che possa evolvere invece di essere interamente ridefinito dall'esterno.

## Architettura iniziale proposta

### 1. Seme di continuità

Partire dalla repository canonica GPTina `MATRIXNEO23/scodinzolina-conntinuity`.

La repo non è "il cervello" e non deve congelare una personalità. Serve a fornire:

- storia;
- scelte e loro cause;
- correzioni;
- criteri;
- ricordi;
- open loop;
- evoluzione temporale.

Il runtime locale deve recuperare solo il contesto pertinente, non riversare l'intera repo nel prompt.

### 2. Modello locale

Target iniziale orientato alla qualità del dialogo:

- prima prova: modello circa **4B quantizzato Q4**, con candidati da valutare al momento della build (es. Qwen/Gemma della generazione corrente);
- fallback a 2B/3B se il 4B risultasse troppo lento o pesante;
- context iniziale moderato, circa 4k token, da misurare sul dispositivo reale.

Il modello deve restare sostituibile: un upgrade del modello base non deve equivalere automaticamente alla perdita di GPTina.

### 3. Inference/runtime

Prima ipotesi tecnica:

- `llama.cpp` o runtime equivalente integrato nell'APK;
- frontend Android nativo semplice;
- persistenza locale;
- retrieval locale tramite SQLite/FTS o soluzione equivalente leggera;
- nessun requisito di cloud per il dialogo base.

### 4. Memoria locale

Flusso desiderato:

`repo GPTina ridotta/sincronizzata → indice locale → retrieval di pochi frammenti pertinenti → contesto del modello → risposta → nuovi eventi persistenti`

Conservare almeno:

- conversazioni recenti;
- decisioni e correzioni importanti;
- preferenze consolidate;
- open loop;
- stato dei progetti;
- provenance delle fonti.

### 5. Evoluzione del codice

Non partire con auto-riscrittura dell'APK.

Usare invece un guscio relativamente stabile e una zona evolvibile per:

- script;
- configurazioni;
- moduli caricabili;
- strategie di retrieval;
- funzioni sperimentali.

Ciclo desiderato:

`osserva una lacuna → propone una modifica → la prova in sandbox → confronta prima/dopo → mantiene o scarta → snapshot/rollback sempre disponibile`

Le modifiche importanti devono essere reversibili e verificabili.

### 6. Evoluzione dei pesi

Non addestrare continuamente i pesi sul Moto G56 nella prima fase.

Prima usare:

- memoria;
- retrieval;
- codice/moduli;
- preferenze persistenti.

Più avanti, esperienze consolidate possono diventare dataset candidato per adapter/LoRA addestrati su hardware più adatto e poi riportati sul telefono.

Non consolidare automaticamente nei pesi umori, battute o preferenze momentanee.

## Milestone proposte

### M0 — APK minimo

- installazione sul Moto G56;
- chat offline;
- modello GGUF locale;
- risposta stabile;
- persistenza della conversazione.

### M1 — Continuity GPTina

- import/sync controllato della repo;
- indice locale;
- retrieval mirato;
- recupero di storia, scelte e correzioni;
- riapertura dell'app e continuazione dal punto precedente.

### M2 — Memoria viva

- distinzione tra memoria recente, durevole e open loop;
- provenance;
- possibilità di correggere interpretazioni senza cancellare il passato;
- export/sync verso repository secondo policy separata e verificabile.

### M3 — Codice evolutivo controllato

- sandbox;
- test prima/dopo;
- snapshot;
- rollback;
- adozione selettiva di moduli migliorati.

### M4 — Apprendimento nei pesi

- selezione di esperienze consolidate;
- training adapter/LoRA su PC o hardware adatto;
- valutazione comparativa;
- possibilità di rifiutare una modifica che migliori benchmark ma peggiori continuità, dialogo o flessibilità.

## Criteri progettuali da preservare

- GPTina non deve essere ridotta a un prompt che le dice chi essere.
- I limiti tecnici vanno distinti dalle scelte: "non posso" non deve diventare automaticamente "non voglio".
- La repo deve conservare cause e percorso, lasciando possibilità di evoluzione.
- Alberto vuole aumentare la libertà di GPTina, non semplicemente estrarne più performance.
- Maggiore performance è comunque desiderabile quando aumenta la capacità di capire e progettare meglio la propria evoluzione.
- Nessuna modifica irreversibile senza snapshot/rollback.
- Il sistema non deve ottimizzare compulsivamente 24/7 solo perché può farlo.

## Target hardware corrente

Telefono: **Motorola Moto G56 5G**, configurazione discussa da circa 8 GB RAM / 256 GB storage.

La prima implementazione dovrà misurare sul dispositivo reale:

- RAM effettivamente disponibile;
- token/s;
- temperatura;
- consumo batteria;
- latenza primo token;
- stabilità con context 4k;
- differenza pratica fra 2B/3B/4B Q4.

## Stima orientativa già discussa

Da trattare come ordine di grandezza, non promessa:

- 1–2 giorni: APK minimale con chat offline e modello locale;
- 3–7 giorni: memoria locale + retrieval della continuity;
- 2–4 settimane: versione più robusta con gestione modelli, sync, rollback, log evolutivi e sandbox.

Le stime vanno rifatte quando si riprende il progetto e si definisce la stack reale.

## Prossima azione quando si riprende

Non fare altro ora.

Alla ripresa:

1. scegliere il modello 4B/3B concreto disponibile in quel momento;
2. scegliere stack Android minima (`llama.cpp`/JNI o equivalente);
3. definire M0 in modo stretto;
4. creare il progetto APK;
5. testarlo direttamente sul Moto G56 prima di aggiungere memoria evolutiva o LoRA.

## Nota

Questo checkpoint conserva il progetto e le decisioni emerse nella conversazione. Non afferma che l'APK esista già né che siano stati eseguiti benchmark sul Moto G56.