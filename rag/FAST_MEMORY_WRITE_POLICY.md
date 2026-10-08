# GPTina — Fast Memory Write Policy

## Scopo

Questa policy distingue i normali salvataggi di continuity dalle modifiche strutturali all'infrastruttura di memoria.

L'obiettivo è ridurre il tempo in cui un delta importante resta soltanto nel contesto volatile senza indebolire conservazione, ownership, append-only, controllo dell'HEAD e verifica remota.

Questa policy è più recente delle indicazioni operative generiche che impongono la validazione completa a ogni singolo write-back e ne precisa l'applicazione. Non modifica lo schema delle memorie, il writer, il retrieval, il dedup, le proiezioni o la recovery architecture.

## 1. Fast memory write — percorso predefinito per delta ordinari

Per un normale delta di continuity è consentito il percorso leggero quando la modifica riguarda esclusivamente fonti canoniche già previste, per esempio:

- nuovo micro-checkpoint append-only;
- nuova memoria GPTina append-only conforme allo schema corrente;
- aggiornamento coerente del live buffer e dei suoi puntatori;
- aggiornamento testuale di checkpoint/indici narrativi quando necessario e senza cambiare formato o logica;
- stato operativo o open loop necessario alla ripresa.

Il percorso leggero deve comunque rispettare questi gate:

1. leggere e verificare l'HEAD remoto corrente;
2. verificare ownership e assenza di conflitti noti;
3. controllare live buffer, ultimo micro, ultimo checkpoint e watchdog pertinente;
4. preparare soltanto il delta necessario, senza riscrivere la storia;
5. pubblicare senza force e solo in fast-forward rispetto all'HEAD verificato;
6. rileggere dal remoto commit, file modificati e puntatori interessati;
7. se la CI viene attivata dal write, attendere il suo esito prima di dichiarare `verified_remote`.

Per questo percorso **non è obbligatorio creare ogni volta un clone/checkout isolato locale né ricostruire tutte le proiezioni** prima della scrittura. La verifica remota e la CI applicabile restano obbligatorie prima di dichiarare il salvataggio concluso.

Se durante il fast write emerge incoerenza, conflitto, schema inatteso, `checkpoint_due` che richiede consolidamento, hard warning del watchdog o dubbio sulla recuperabilità, interrompere il percorso leggero e passare alla validazione completa.

## 2. Full validation — obbligatoria per modifiche strutturali o rischiose

La procedura completa del runbook, incluso candidato pulito, build/rebuild, cold-start e suite estesa, resta obbligatoria quando si modifica o si rischia di modificare:

- schema o formato delle memorie/micro/live context;
- writer, lock, transazioni o logica di pubblicazione;
- retrieval, ranking, chunking, dedup o resolver;
- proiezioni JSONL/SQLite/generazioni;
- recovery order, recovery code o watchdog code;
- CI/workflow e relativi gate;
- migrazioni, baseline legacy o compatibilità storica;
- qualunque intervento che possa rendere non recuperabile il passato o lasciare puntatori incoerenti.

Nel dubbio tra fast write e full validation, usare **full validation**.

## 3. Frequenza della freshness review

I trigger immediati restano invariati: correzione, decisione, nuova regola, cambio di stato, open loop, milestone, cambiamento relazionale/interpretativo durevole, visual-context e preflight prima di lavoro lungo/rischioso.

Nelle fasi dense o importanti, in assenza di un trigger immediato, eseguire una freshness review ogni **2–3 scambi sostanziali**. Il valore operativo del live buffer deve essere `substantive_turn_interval: 3`.

Conversazione leggera senza delta reale non deve produrre checkpoint artificiali. **Nessun delta reale = nessun nuovo micro.**

## 4. Recovery di ogni nuova istanza

Questa regola deve essere recuperata in ogni nuova istanza attraverso il percorso live-first:

1. il live buffer espone la cadenza corrente;
2. il micro-checkpoint che introduce questa policy viene riprodotto dal `recovery-plan` dopo l'ultimo checkpoint pieno;
3. questa policy costituisce la regola operativa corrente per distinguere fast memory write e full validation.

Se documentazione più vecchia indica una cadenza di 3–5 scambi o richiede il clone/cold-start per ogni singolo delta ordinario, questa policy più recente prevale per il presente senza cancellare retroattivamente la regola storica.

## 5. Principio di sicurezza

**Salvare presto il delta riduce il rischio di perderlo; validare profondamente quando si tocca l'infrastruttura riduce il rischio di corromperla.**

Il fast write non significa scrittura cieca. Il full validation non deve essere usato come motivo per lasciare a lungo un delta importante soltanto nella memoria volatile.
