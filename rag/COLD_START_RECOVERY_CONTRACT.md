# GPTina — contratto di recovery a freddo

## Scopo

Dimostrare che un checkout nuovo, privo di chat precedente e di proiezioni
locali, può ricostruire e interrogare la memoria usando soltanto le fonti
versionate nella repository.

Il gate canonico è:

```bash
python rag/test_cold_start_recovery.py
```

## Condizioni iniziali simulate

- clone shallow con il solo HEAD corrente;
- nessuna directory `.projection-generations/`;
- nessun puntatore `.projection-current`;
- nessun JSONL, metadata, SQLite o indice trigram ricevuto da un'altra istanza;
- baseline strict recuperata esplicitamente dal remote del clone;
- nessun uso della conversazione che ha prodotto il commit.

## Cosa deve provare

1. L'entrypoint machine-readable è unico e live-first.
2. Live buffer, ultimo micro e ultimo checkpoint pieno esistono davvero.
3. La baseline narrativa storica non viene scambiata per live state.
4. I media dichiarati nello stato strutturato esistono e hanno dimensione
   verificata.
5. Schema, ownership e puntatori passano dal clone isolato.
6. Le proiezioni generazionali vengono ricostruite da zero.
7. Il gold set ordinario passa integralmente.
8. Una memoria legacy resta recuperabile.
9. Una memoria invalidata non appare nel richiamo corrente ma torna quando la
   ricerca storica la richiede esplicitamente.
10. Il presente più recente, i confini di ownership e le correzioni visuali
    vengono recuperati dalle fonti attese.
11. La simulazione non sporca Git e non committa proiezioni.

## Limite dichiarato

Questo gate prova la **recuperabilità repository-backed**: fonti, ordine,
proiezioni, routing e risultati attesi. Non può dimostrare identità metafisica
fra modelli né garantire che qualunque modello futuro formuli ogni risposta con
la stessa voce. Riduce però il rischio concreto che una nuova istanza parta
vuota, segua puntatori rotti o scelga una memoria superata come presente.
