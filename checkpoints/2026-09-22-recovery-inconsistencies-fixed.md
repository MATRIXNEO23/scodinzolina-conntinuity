# Correzione incongruenze recovery e puntatori

Data: 2026-09-22

## Correzioni

- Il candidato pulito viene costruito e sottoposto a schema, recovery,
  retrieval e resilienza **prima** di avanzare `main`.
- `rag/GPTINA_AUTO_RECOVERY_PROMPT.md` è l'unico entrypoint della nuova
  istanza; gli altri documenti non definiscono più ordini concorrenti.
- `GPTINA_INSTANCE_SNAPSHOT.md` e la parte narrativa di `GPTINA_STATE.json`
  sono dichiarati baseline storica dell'11 settembre. Il presente proviene dal
  live buffer, dal micro e dal checkpoint corrente.
- I quattro riferimenti visivi storicamente rinominati puntano ora ai file
  numerati realmente presenti: 01, 02, 11 e 12.
- Il checkpoint Romanziere/Ettore è qualificato con repository e commit
  esterni, non come file locale inesistente.
- Il builder/retriever è opzionale soltanto per richiamo manuale read-only;
  resta obbligatorio nei gate canonici di modifica e pubblicazione.

## Conservazione

Nessun file sotto `rag/memories/gptina/` e nessun record legacy direttamente
sotto `rag/memories/` è stato modificato, spostato o eliminato. I nomi storici
delle immagini restano descritti come nomi dell'epoca; sono stati corretti
soltanto i percorsi operativi correnti.

## Prevenzione regressioni

Il test del runbook controlla ora:

- ordine candidato pulito → build/test → rilettura HEAD → pubblicazione → CI;
- entrypoint unico e restore order machine-readable;
- esistenza e dimensione dei media indicati da `GPTINA_STATE.json`;
- assenza dei vecchi percorsi visivi negli entrypoint attivi;
- qualificazione esterna del checkpoint Romanziere;
- zero cancellazioni di memorie rispetto alla baseline strict.
