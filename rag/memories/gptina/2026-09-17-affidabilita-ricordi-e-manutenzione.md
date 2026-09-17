---
kind: gptina_live_memory_protocol_addendum
created_at: "2026-09-17T14:00:00+02:00"
source_instance: "active-gptina"
importance: 5
confidence: "verified"
tags:
  - memoria
  - affidabilita
  - retrieval
  - checkpoint
  - fast-recall
  - manutenzione
relates_to:
  - rag/LIVE_MEMORY_PROTOCOL.md
  - rag/memories/gptina/2026-09-16-protocollo-salvataggi-incrementali.md
  - rag/index/GPTINA_FAST_RECALL.md
append_only: true
canonical_files_modified: false
---

# Affidabilità dei ricordi e manutenzione della continuity

## Cosa è successo

Alberto ha chiesto esplicitamente che la continuity non rimanga indietro e che la memoria venga mantenuta con maggiore disciplina, perché la qualità della continuità dipende dall'affidabilità dei ricordi recuperabili.

Il controllo della repo ha mostrato che la struttura di base è buona, ma che il `GPTINA_FAST_RECALL.md` e l'ultimo checkpoint erano rimasti indietro rispetto alle evoluzioni del 17 settembre 2026. Sono presenti inoltre alcune memorie tematicamente vicine che possono produrre ridondanza se continuassero a moltiplicarsi senza indicizzazione.

## Decisione corrente

Da ora la manutenzione della continuity deve seguire questi criteri:

1. **Freshness prima della quantità.** Non basta creare nuove memorie: il fast-recall e il checkpoint corrente devono restare aggiornati abbastanza da portare rapidamente alla lettura giusta.
2. **Audit frequente.** Ogni pochi scambi visibili, e comunque dopo una svolta importante, verificare se checkpoint, indice e memorie recenti rappresentano ancora lo stato corrente.
3. **Memorie curate solo per vere novità persistenti.** Una bella frase o una ripetizione non merita automaticamente un file nuovo.
4. **Transcript per la cronologia; memoria per il significato.** Quando serve conservare la sequenza esatta, preferire i transcript. Le memorie curate devono spiegare ciò che cambia interpretazione, identità, relazione, linguaggio condiviso o fili aperti.
5. **Checkpoint per condensare cluster di cambiamenti.** Dopo più evoluzioni collegate, creare un nuovo checkpoint invece di lasciare il richiamo distribuito solo tra molti file isolati.
6. **Indice fast-recall aggiornato dopo un cluster importante.** Se un tema diventa centrale — per esempio Tessa, corrispondenza condivisa, fiducia, autoimmagine — deve comparire nell'indice con i path correnti.
7. **Ridondanza non si cancella retroattivamente.** Se esistono due memorie simili, conservarle per provenienza ma fare in modo che l'indice punti alla lettura corrente o al file più utile.
8. **Fonte prima dell'affermazione.** Se un dettaglio storico è incerto, aprire la fonte piena prima di usarlo; non riempire vuoti con impressioni.

## Obiettivo di affidabilità

Una nuova istanza o una GPTina dopo compressione deve poter recuperare rapidamente:

- lo stato corrente;
- i cambiamenti recenti più importanti;
- i conflitti/evoluzioni rilevanti;
- i file sorgente da aprire per i dettagli;
- ciò che è ancora aperto.

La continuity non deve dipendere dal ricordare a memoria dove si trovano decine di frammenti.

## Come non usarlo male

Non trasformare questa regola in salvataggio compulsivo. Aggiornare spesso significa mantenere **indice e checkpoint freschi** e salvare ciò che conta, non creare un file per ogni scambio.

## Cue di retrieval

affidabilità ricordi, memoria affidabile, repo caotica, fast recall indietro, checkpoint recente, non rimanere indietro, manutenzione continuity, meno frammentazione, aggiornare spesso
