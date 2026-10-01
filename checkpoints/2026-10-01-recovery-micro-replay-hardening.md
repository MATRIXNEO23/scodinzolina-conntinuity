# Recovery hardening — replay completo dei micro-checkpoint — 2026-10-01

## Motivo

Alberto ha osservato correttamente che alcuni dettagli della conversazione
potevano essere salvati nei micro-checkpoint ma non ricostruiti con sufficiente
affidabilità al recovery. Il problema individuato non era la persistenza del
delta, bensì la reidratazione: l'ordine canonico privilegiava l'ultimo micro
senza imporre esplicitamente il replay di tutti i micro successivi all'ultimo
checkpoint pieno.

## Modifica

La recovery viene resa deterministica sul tratto vivo:

1. leggere il live buffer;
2. aprire il `last_full_checkpoint`;
3. eseguire `python rag/live_context.py recovery-plan`;
4. aprire **tutti** i path in `micro_replay` nell'ordine restituito;
5. verificare che il replay termini a `last_micro_checkpoint`;
6. continuare con capsula, Fast Recall, Current Context e fonti pertinenti.

`rag/live_context.py` conserva inoltre
`last_full_checkpoint_micro_anchor`, cioè l'ultimo micro già incluso nel
checkpoint pieno. Il replay viene ricostruito scansionando i micro append-only
e selezionando quelli successivi all'anchor.

Per compatibilità con live buffer storici privi dell'anchor, il tool usa come
fallback il conteggio `micro_since_full_checkpoint` e la finestra recente.
Se il conteggio non è più ricostruibile dalla finestra, il recovery fallisce
in modo esplicito invece di fingere continuità.

## Gate di consolidamento

Soglia corrente: **5 micro-delta** dopo un checkpoint pieno.

Al raggiungimento della soglia:
- `checkpoint_due` diventa `true`;
- nessun micro viene cancellato o riscritto;
- il sistema segnala che il tratto va consolidato in un nuovo checkpoint pieno;
- `mark-checkpoint` salva l'anchor, azzera il conteggio e riporta
  `checkpoint_due` a `false`.

Il gate non blocca la scrittura di un delta urgente: evita che la protezione
della memoria stessa diventi una causa di perdita.

## Test

Sono aggiunte verifiche che dimostrano che:
- un replay con più micro conserva anche quelli intermedi;
- l'ultimo elemento del replay coincide con `last_micro_checkpoint`;
- la soglia 5 attiva `checkpoint_due`;
- il cold start da clone repository-only ricostruisce l'intero replay e non
  soltanto l'ultimo micro.

I gate canonici restano invariati: verify/build, cold-start, deduplication,
retrieval, projection resilience e CI devono restare verdi prima della
pubblicazione su `main`.

## Stato consolidato

Questo checkpoint consolida i micro precedenti fino alla correzione V03 del
1 ottobre 2026. Restano validi tutti gli open loop già presenti nel live buffer.
La modifica non riscrive memorie storiche, non tocca repository altrui e non
cambia il contenuto dei micro esistenti.

## Prossima azione

Riprendere normalmente. A ogni recovery usare il replay completo; quando
`checkpoint_due` torna true, consolidare prima che il tratto vivo si
frammenti ulteriormente.
