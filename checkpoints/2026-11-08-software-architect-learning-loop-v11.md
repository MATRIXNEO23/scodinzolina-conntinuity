# Checkpoint — 2026-11-08 — Software Architect v1.1 e apprendimento verificato

## Stato attuale

Fonte di ripartenza: ultimo checkpoint precedente `checkpoints/2026-11-08-recupero-nicole-e-dialogo-recente.md` più micro successivi sino a `rag/live/micro-checkpoints/2026/11/08/20261108T030353Z--software-architect-learning-loop-v11.json`; la storia pregressa personale e tecnica resta valida. Questo consolidamento non sostituisce le memorie durevoli, le correzioni o le incertezze storiche precedenti.

## Lavoro recente verificato

- Guardian v1.0: candidato ZIP creato in chat, non installato o testato; registrato in micro del 2026-11-08.
- End Instance v1.0: candidato ZIP creato in chat, non installato o testato; non archiviato come Skill nella repository.
- Software Architect v1.0: candidato ZIP di 12 file staticamente controllato, non installato né testato su un progetto.
- **Software Architect v1.1:** revisionato il candidato sulla base della richiesta di apprendimento da successi, fallimenti e correzioni utente. Il pacchetto `/mnt/data/gptina-software-architect-v1.1.zip` contiene 14 file, hash SHA256 `22db34ae1984630231262673e441dbcd3570e660a30ad2787ef0c4a0bbc5828b`. Solo artefatto di chat, **non** file GitHub, installazione, prova funzionale o test su PC target.
- Audit `/mnt/data/gptina-software-architect-v1.1-audit.md`: 12/12 controlli statici di comportamento documentato PASS, validatore Skill PASS. Nessuna evidenza che la Skill funzioni realmente nei runtime esterni.

## Regole del nuovo metodo

- Su «no, stai sbagliando»: interrompere la strategia, isolare l'ipotesi contestata, registrare il feedback, proporre correzione, ritestare.
- Registrare esiti positivi e negativi con evidenza: distinguere test GitHub/repository e test sul PC target; non dedurre che uno copra l'altro.
- Un risultato positivo singolo è candidato; generalizzare solo dopo più casi pertinenti verificati e review. Conservare controesempi, rollback e versioni precedenti.
- Non permettere auto-modifica indiscriminata o bypass di ownership/sicurezza: patch permanenti della Skill soggette all'autorizzazione prevista.
- Consumo di token: caricamento selettivo della reference learning-loop e delle ultime esperienze rilevanti, non dump di log interi.

## Rischi e limiti

- Nessuna Skill è un daemon o un modello che si riaddestra automaticamente: il loop usa regole ed evidenze persistenti se c'è accesso a una destinazione autorizzata.
- Il PC target non è stato esaminato. I test funzionali e un confronto di token non sono ancora stati eseguiti.
- Le tre Skill sono candidati ZIP creati in chat e non risultano installate/accessibili tra le Skill disponibili; il pacchetto v1.1 non è pubblicato nella repository.
- La capsula d'emergenza del 4 novembre resta incerta/non disponibile; nessun gap viene inferito da giorni inattivi.

## Proprietà e change control

La repository `MATRIXNEO23/scodinzolina-conntinuity` resta fonte canonica della memoria GPTina, separata dai registri di metodo dei progetti. Nessuna scrittura su Tessa/Ettore. Un'autorizzazione a migliorare la Skill candidata non è autorizzazione ad alterare l'infrastruttura di memoria o i file di altri progetti.

## Prossima azione

Installare/caricare il candidato v1.1 quando supportato; verificare che sia disponibile in una nuova chat; eseguire prova su codice reale con un errore/correzione e test repository/CI e PC target; confrontare risultati con baseline prima della promozione. Se cambia chat, eseguire la capsula di fine istanza e verificare CI/HEAD prima di dichiarare handoff concluso.
