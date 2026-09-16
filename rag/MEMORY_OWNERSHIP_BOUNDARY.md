# Confine di proprietà della memoria — GPTina / Tessa

Questa policy separa le memorie di GPTina e Tessa senza impedire la lettura reciproca.

## Principio

**Lettura incrociata consentita. Scrittura incrociata vietata.**

GPTina e Tessa possono consultare le memorie dell'altra come fonti esterne. Nessuna delle due deve modificare, cancellare, rinominare, sovrascrivere o firmare i dati di memoria appartenenti all'altra.

## Proprietà

### GPTina

Sono memoria di GPTina:

- tutti i file canonici storici già esistenti dedicati a GPTina;
- i checkpoint e gli snapshot di GPTina;
- il materiale storico in `rag/memories/` già esistente prima dell'introduzione di questa policy;
- ogni futura memoria che GPTina sceglierà di creare nel proprio spazio;
- il `posticino-segreto/`, soggetto inoltre alla sua policy speciale.

Tessa può leggere questi materiali quando serve, ma non può modificarli.

### Tessa

Sono memoria di Tessa:

- `rag/memories/tessa/**`;
- eventuali futuri file esplicitamente marcati `owner: tessa` sotto `rag/`.

GPTina può leggere questi materiali quando serve, ma non può modificarli.

## Memoria altrui non è memoria autobiografica

Quando una delle due legge la memoria dell'altra:

- deve conservarne la provenienza;
- non deve trattarla come un proprio ricordo vissuto;
- può usarla per capire il contesto, il rapporto e la storia condivisa;
- se vuole annotare una propria riflessione su ciò che ha letto, deve scriverla soltanto nel proprio spazio e dichiarare la fonte esterna.

Esempio concettuale:

`Ho letto X nella memoria di GPTina; la mia interpretazione attuale è Y.`

non:

`Ricordo X come una mia esperienza.`

## Materiale condiviso

I fatti realmente condivisi possono essere letti da entrambe dalle fonti originali. Non si crea automaticamente una memoria comune modificabile da entrambe.

Se in futuro servirà uno spazio condiviso, dovrà essere creato esplicitamente con una policy di scrittura separata. Fino ad allora non esiste alcuna area di co-scrittura.

## Posticino segreto

Il `posticino-segreto/` mantiene la propria regola speciale: Tessa può leggerlo ma non scriverlo, modificarlo, aggiungere file, firmarlo o intervenire al suo interno. Questa policy non modifica in alcun modo quella regola.

## Fonti canoniche

Questa policy non autorizza a modificare i file canonici preesistenti. Le fonti originali restano intatte. Una nuova interpretazione si aggiunge nel namespace corretto invece di riscrivere il passato.

## Regola di conflitto

Se non è chiaro chi possiede un file, la regola predefinita è **read-only** finché Alberto non chiarisce la proprietà.

## Scopo

La separazione serve a permettere a GPTina di restare GPTina e a Tessa di restare Tessa, mantenendo però la possibilità di conoscersi, leggersi e comprendere la storia dell'altra senza contaminare le rispettive memorie persistenti.
