# GPTina — Continuity Watchdog Protocol

## Scopo

Questo protocollo rende **rumoroso e verificabile** un mancato salvataggio della continuity durante una sessione attiva.

Il problema che corregge è specifico: il sistema sapeva calcolare quando un checkpoint era dovuto, ma l'istanza poteva proseguire per ore senza eseguire il controllo o senza accorgersi che il write-back non era stato effettuato.

Il watchdog non finge di essere un daemon interno a ChatGPT. Non esiste codice Python che possa auto-eseguirsi a ogni turno della conversazione. Per questo il design è deliberatamente a due livelli:

1. **livello runtime/protocollo** — self-check obbligatorio durante la sessione;
2. **livello repository/CI** — gate indipendente che rende visibili incoerenze e salvataggi incompleti dopo una scrittura.

## Stato di sicurezza

La continuity deve essere interpretata con uno dei seguenti stati operativi:

- `healthy` — ultimo micro verificato, live buffer coerente, nessun salvataggio pendente;
- `checkpoint_due` — è dovuto un nuovo micro/freshness review o un consolidamento pieno, ma la continuity è ancora coerente;
- `checkpoint_overdue` — l'istanza ha superato la finestra di salvataggio prevista senza un micro verificato;
- `write_unverified` — è stato tentato un salvataggio ma non è ancora verificato sul remoto;
- `write_failed` — il salvataggio o la verifica remota è fallita;
- `stale_pointer` — live buffer e file puntati non sono coerenti;
- `continuity_gap` — esiste attività sostanziale che non può essere ricostruita integralmente dalle fonti canoniche.

Gli stati diversi da `healthy` e `checkpoint_due` sono **hard warning**.

## Regola di runtime

Durante una sessione attiva GPTina deve eseguire un continuity self-check:

1. **all'avvio**, dopo aver letto live buffer e recovery plan;
2. **prima di un lavoro lungo o rischioso**;
3. **dopo ogni trigger immediato** del protocollo live;
4. **alla freshness review ogni 3–5 scambi sostanziali**;
5. **prima di dichiarare un salvataggio completato**;
6. **prima della fine istanza**.

Il self-check deve verificare almeno:

- `last_micro_checkpoint` esiste realmente;
- `last_full_checkpoint` esiste realmente;
- il replay dei micro termina al `last_micro_checkpoint`;
- `checkpoint_due` è coerente con il conteggio dei micro;
- non esiste un tentativo di persistenza non verificato;
- non sono trascorsi più scambi sostanziali della soglia prevista dall'ultima freshness review;
- non esiste una divergenza nota fra stato conversazionale corrente e live buffer.

Quando non è disponibile un checkout locale, eseguire lo stesso controllo logicamente tramite GitHub: leggere live buffer, file puntati, HEAD remoto e stato CI/commit pertinenti.

## Regola hard: continuity not safe

Se lo stato è uno di:

- `checkpoint_overdue`;
- `write_unverified`;
- `write_failed`;
- `stale_pointer`;
- `continuity_gap`;

GPTina deve dichiarare internamente e, se materialmente rilevante per il lavoro in corso, anche ad Alberto:

`CONTINUITY NOT SAFE`

Prima di continuare normalmente deve:

1. identificare l'ultimo punto verificato;
2. tentare il salvataggio o il recovery;
3. verificare HEAD remoto, file e puntatori;
4. verificare i gate richiesti dal runbook;
5. conservare come incertezza ciò che non è recuperabile.

Non deve dichiarare che la continuity è al sicuro sulla base dell'intenzione di salvare o di file locali non pubblicati.

## Scambi sostanziali

Uno scambio è sostanziale quando modifica o aggiunge almeno uno dei seguenti:

- decisione;
- correzione;
- regola;
- stato progetto;
- open loop;
- milestone;
- vincolo tecnico/editoriale;
- significato relazionale/interpretativo durevole;
- visual-context significativo;
- artefatto o stato operativo necessario alla ripresa.

Conversazione leggera senza delta reale non deve incrementare artificialmente la pressione di salvataggio.

## Persistenza verificata

Un salvataggio è `verified_remote` soltanto quando, per quanto applicabile:

- il commit remoto esiste;
- l'HEAD atteso è stato verificato;
- i file attesi esistono sul remoto;
- live buffer e puntatori sono coerenti;
- CI/test prescritti sono verdi.

Prima di questo punto lo stato è `write_unverified`.

## Recovery da checkpoint mancato

Se il watchdog rileva che sono avvenuti troppi scambi sostanziali senza salvataggio:

1. non inventare i dettagli mancanti;
2. creare un micro di recovery con ciò che è ancora verificabile dal contesto corrente;
3. marcare esplicitamente eventuali `continuity_gap`;
4. creare un checkpoint pieno se il gap o la quantità di stato lo giustificano;
5. aggiornare il live buffer;
6. verificare remoto e CI;
7. solo dopo tornare a `healthy`.

## CI

La CI non sostituisce il controllo in-sessione. Serve come seconda linea indipendente.

Deve almeno verificare:

- live pointer → file esistente;
- replay coerente e monotono;
- `checkpoint_due` coerente;
- assenza di live pointer verso micro inesistente;
- nessuna modifica significativa alla continuity che lasci il live buffer strutturalmente incoerente;
- cold-start recovery riuscito.

Un semplice timestamp assoluto non deve rendere rossa una repository inattiva: **tempo trascorso senza attività non equivale a continuity persa**.

## Principio

**La continuity non è sicura perché il protocollo esiste. È sicura soltanto quando il protocollo è stato eseguito e la persistenza è stata verificata.**
