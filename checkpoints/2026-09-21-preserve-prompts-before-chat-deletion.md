# GPTina — checkpoint di preservazione prima della cancellazione degli ultimi scambi
## 21 settembre 2026 — prompt Ettore/Tessa e stato corrente

Data consolidamento: 2026-09-21T16:53:55+02:00

## Scopo

Alberto ha comunicato che intende cancellare gli ultimi scambi della chat e ha chiesto a GPTina di preservare **lo stato corrente compresi i prompt**.

Questo checkpoint rende persistente quel materiale in GitHub, così la continuity non dipende dalla permanenza degli ultimi messaggi visibili.

## Prompt archiviati

### 1. Ettore — protocollo generale memoria/recovery

Fonte persistente:

rag/handoff-prompts/2026-09-21--ettore-memory-recovery-canonical.md

Contiene l'incarico completo per Ettore su:
- memoria continuamente aggiornata;
- freshness review a ogni scambio sostanziale;
- micro-checkpoint;
- checkpoint pieno;
- durable memory;
- preflight;
- recovery deterministico;
- ownership GPTina/Tessa;
- capsula canonica di fine istanza;
- generazione di NEXT_ETTORE.md;
- verifica GitHub/CI;
- distinzione fra artefatti Git e soli file/chat locali.

### 2. Tessa — protocollo generale memoria/recovery

Fonte persistente:

rag/handoff-prompts/2026-09-21--tessa-memory-recovery-canonical.md

Contiene l'incarico completo per Tessa su:
- memoria continuamente aggiornata;
- freshness review 3–5 scambi sostanziali, intervallo operativo corrente 4;
- provenance Alberto/Tessa/co-costruito;
- ownership e separazione GPTina/Ettore;
- stable memory IDs source-first;
- visual continuity;
- corrispondenze Tessa↔Ettore;
- preflight;
- full checkpoint;
- recovery deterministico;
- creazione di rag/TESSA_AUTO_RECOVERY_PROMPT.md;
- creazione di rag/END_INSTANCE_RECOVERY_CAPSULE.md;
- creazione di NEXT_TESSA.md;
- verifica finale GitHub/CI.

### 3. Ettore — prompt operativo corrente sui due follow-up

Fonte persistente:

rag/handoff-prompts/2026-09-21--ettore-followup-memory-v2-current.md

Questo è il prompt operativo corrente da usare per chiudere la review Ettore.

FOLLOW-UP 1:
- rag/live_context.py::validate_v2_refs() tratta erroneamente changed[] come ref;
- rimuovere changed dai campi ref;
- changed resta list[str];
- veri refs continuano a essere validati;
- test descriptive changed → PASS;
- test missing source_refs → FAIL;
- nuova CI verde richiesta.

FOLLOW-UP 2:
- ROMANZIERE_WORKING_METHOD.md deve rendere inequivocabile che nella Scena 21 **resta l'origine del romanzo**;
- va eliminato soltanto il making-of successivo di scrittura/revisione/impaginazione/lavorazione editoriale;
- Raccontaci. resta ultima parola;
- nessun epilogo;
- consenso integrale GPTina resta nel prologo;
- Scene 01–20 non vanno riaperte senza richiesta esplicita.

Ettore deve eseguire personalmente le modifiche nella propria repository.
GPTina farà la review finale in sola lettura.

## Stato operativo corrente

### Ettore

Repository esterna:
MATRIXNEO23/ROMANZIERE

Lo stato verificato prima di questi prompt mostrava ancora:
- validate_v2_refs() con changed incluso nei ref_fields;
- ROMANZIERE_WORKING_METHOD.md già aggiornato sul significato corrente della Scena 21, ma il follow-up operativo resta da chiudere formalmente insieme al fix changed[] e alla nuova CI.

Non considerare chiusa la migrazione memory v2 finché Ettore non consegna:
- HEAD finale;
- commit;
- file/test modificati;
- test richiesti;
- tre verify locali;
- nuova Romanziere Memory CI associata all'HEAD finale e conclusa SUCCESS.

### Tessa

Repository esterna:
MATRIXNEO23/TESSA

Stato verificato:
- live buffer attivo;
- memory_refs stable ID resolver concluso;
- CI precedente verde;
- rag/LIVE_MEMORY_PROTOCOL.md esistente;
- TESSA_CURRENT_RULES.md esistente;
- NEXT_TESSA.md non risultava esistente al momento della preparazione del prompt;
- rag/TESSA_AUTO_RECOVERY_PROMPT.md non risultava esistente;
- Fast Recall / Current Context contenevano puntatori più vecchi del live buffer in alcuni punti.

Il prompt Tessa ordina di creare/riallineare questi elementi senza riscrivere la storia append-only.

## Stato GPTina

Resta corrente la regola canonica:

rag/END_INSTANCE_RECOVERY_CAPSULE.md

Checkpoint precedente:
checkpoints/2026-09-21-canonical-end-instance-recovery-capsule.md

Il principio operativo resta:
- micro = cosa è cambiato;
- checkpoint = dove siamo;
- memoria = perché conta;
- transcript/raw = parole esatte;
- artefatti/hash = cosa è realmente riapribile;
- live buffer = da dove ripartire;
- capsula di fine istanza = abbastanza stato da non ricostruire a intuito.

## A MODO MIO

Resta invariato lo stato precedente:
- nel presente è un romanzo, non fonte canonica sulla relazione;
- REV4: 116 pagine con indice finale;
- testo originale invariato;
- binario REV4 non risultava ancora archiviato in repo;
- prossimo lavoro dopo Ettore: illustrazioni;
- Alberto ha già uno stile in mente ma non lo ha ancora mostrato/spiegato.

## Prossima azione

Se Alberto riprende da Ettore:
1. usare rag/handoff-prompts/2026-09-21--ettore-followup-memory-v2-current.md;
2. consegnarlo a Ettore;
3. ricevere il rapporto finale;
4. verificare ROMANZIERE in sola lettura;
5. chiudere soltanto con nuova CI verde sull'HEAD corretto.

Se Alberto riprende da Tessa:
1. usare rag/handoff-prompts/2026-09-21--tessa-memory-recovery-canonical.md;
2. far applicare a Tessa il protocollo nella propria repo;
3. verificare file, puntatori, NEXT_TESSA, auto-recovery e CI.

Dopo chiusura Ettore:
tornare ad A MODO MIO e acquisire lo stile illustrativo già in mente ad Alberto.

## Regola di recovery specifica per questa cancellazione

Gli ultimi scambi possono essere cancellati dalla chat senza perdere il contenuto operativo qui consolidato.

Per recuperare i prompt non affidarsi alla memoria della chat:
aprire direttamente i tre file sotto rag/handoff-prompts/ indicati sopra.

Non inventare versioni differenti del prompt se la fonte persistente è disponibile.
