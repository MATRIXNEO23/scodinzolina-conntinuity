# GPTina checkpoint — 18 settembre 2026 — regola immagini collegate a contesto e ricordo

## Nuova regola stabile

Su richiesta esplicita di Alberto:

> quando viene inserita una nuova immagine, oppure GPTina trova una nuova immagine già presente ma non ancora indicizzata, deve collegarla direttamente a contesto e ricordo.

La regola operativa completa è salvata in:

- `rag/memories/gptina/2026-09-18-regola-immagini-collegate-a-contesto-e-ricordo.md`

## Comportamento obbligatorio

Nello stesso ciclo operativo dell'inserimento/scoperta dell'immagine:

1. verificare il file reale in repository;
2. collocarlo nella cronologia visiva;
3. collegarlo al contesto/fonte che spiega quando e perché è nato;
4. collegarlo alla memoria GPTina pertinente;
5. creare una nuova memoria append-only se l'immagine introduce un significato nuovo e durevole;
6. marcarne lo stato visivo senza confondere presenza in `media/` con riconoscimento canonico;
7. aggiungere cue di retrieval;
8. aggiornare Fast Recall quando diventa un riferimento importante.

Se il contesto esatto non è recuperabile:
- non inferirlo dal filename o dall'estetica;
- marcare `context incomplete`;
- distinguere data evento/creazione, data upload e data scoperta quando divergono.

## Principio

**Nessuna immagine significativa deve restare orfana.**

File = scena.  
Cronologia = quando.  
Fonte/contesto = cosa stava succedendo.  
Memoria = perché conta.

## Modifiche verificate

- nuova memoria-regola: commit `58b419ab48f828b252c6f1673fcac5546f10608a`
- cronologia visiva aggiornata: commit `839d32ed755e2b31cb948d4b358172d8a0bca7fc`
- Fast Recall aggiornato: commit `1a6ef1580e4d7789902bdfca11d2e4b0dce7e3b5`
- Current Context aggiornato: commit `e3beb20db080d17d9e1f33e851b7efdc6a89a449`

## Ownership

Questa regola vale per la memoria e l'archivio GPTina.

Per immagini condivise con Tessa:
- GPTina può collegare il proprio contesto/ricordo;
- non deve scrivere nella memoria personale di Tessa;
- resta valida la regola assoluta: lettura incrociata consentita, scrittura incrociata vietata.

## Prossima azione

Aggiornare gli entrypoint perché questo checkpoint diventi il più recente da leggere in recovery.
