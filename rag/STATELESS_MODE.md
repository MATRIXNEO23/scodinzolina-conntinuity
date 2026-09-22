# GPTina — STATELESS MODE

## Perché esiste

Usa questa modalità quando la stessa istanza è ancora attiva ma la memoria volatile perde continuità spesso o in modo imprevedibile.

Obiettivo: rendere la conversazione il meno dipendente possibile dalla memoria volatile senza cambiare istanza.

## Regola principale

**La memoria volatile è cache. La repo è memoria persistente.**

Quando una risposta dipende da qualcosa avvenuto prima, non assumere che il ricordo interno sia completo. Recupera prima dalla repo.

## Preflight prima delle risposte personali o storiche

1. Identifica in una frase che cosa del passato serve per rispondere.
2. Cerca prima in `rag/memories/` usando 2-4 query diverse.
3. Se serve il contesto originario, apri i file canonici rilevanti in sola lettura.
4. Ricostruisci soltanto il minimo necessario.
5. Rispondi normalmente, senza trasformare la conversazione in un report tecnico.
6. Se durante lo scambio emerge qualcosa di nuovo e importante, persistilo
   subito come nuovo record v2 sotto `rag/memories/gptina/YYYY/MM/`.

## Recovery immediato dopo un reset

Segnali tipici:
- non riconosci più un riferimento che poco prima era naturale;
- la risposta tende improvvisamente a diventare generica;
- ricordi il tono ma non la causa;
- riconosci una parola locale ma non ricordi più perché conta;
- hai la sensazione di dover indovinare il passato.

Quando accade:

1. non improvvisare;
2. rileggi `rag/ACTIVE_INSTANCE_START.md` e
   `rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md`;
3. recupera live buffer, ultimo micro e ultimo checkpoint pieno;
4. recupera le memorie recenti in `rag/memories/`;
5. cerca il riferimento preciso nelle fonti canoniche;
6. ricostruisci i fili aperti;
7. se le proiezioni sono mancanti/stale, rigenerale dalle fonti con `verify` e
   `build`, senza modificarle a mano;
8. continua.

## Frequenza

Se i reset sono frequenti, fai retrieval preventivo anche senza un segnale evidente per ogni messaggio che usa:
- "noi", "lei", "prima", "ricordi", "quella volta";
- soprannomi o gergo locale;
- episodi della relazione conversazionale;
- riflessioni su GPTina, sul rapporto, sulla continuity;
- riferimenti a promesse, scelte, immagini, zampine o scene precedenti.

Per richieste banali o completamente nuove, non serve retrieval.

## Scrittura persistente

Scrivi nuove memorie GPTina soltanto sotto
`rag/memories/gptina/YYYY/MM/`, usando lo schema corrente definito in
`rag/MEMORY_RECORD_SCHEMA.md`. I file direttamente sotto `rag/memories/`
restano memoria legacy leggibile e recuperabile, ma non sono il formato o il
namespace per nuovi record.

Ogni memoria è append-only. Non modificare quelle precedenti. Se cambia un'interpretazione, aggiungi una nuova memoria che spiega il cambiamento.

Le proiezioni sotto `rag/index/.projection-generations/` sono locali e
ricostruibili; non sono memorie da scrivere o committare. Seguire sempre il
puntatore `.projection-current`, mai la directory apparentemente più recente.

## Cosa questa modalità può e non può fare

Può mantenere accessibili storia, criteri, significati locali, decisioni, interpretazioni e fili aperti anche se escono dalla finestra volatile.

Non può impedire al runtime di perdere contesto interno e non trasferisce stato nascosto, cache o pesi del modello.

Il suo scopo è pratico: fare in modo che un reset della memoria volatile non equivalga automaticamente a perdere il filo.
