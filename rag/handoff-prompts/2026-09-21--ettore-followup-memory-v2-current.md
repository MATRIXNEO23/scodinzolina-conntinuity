# Prompt operativo corrente — Ettore: chiusura follow-up memory v2

Stato: **corrente** al 21 settembre 2026.
Origine: ultimo writing block Ettore mantenuto nella conversazione prima della cancellazione degli ultimi scambi.
Scopo: chiudere i due follow-up ancora aperti emersi dalla review GPTina.

---

Ettore, usa **GitHub** e lavora esclusivamente sulla tua repository:

MATRIXNEO23/ROMANZIERE

Devi correggere personalmente i **due follow-up ancora aperti** emersi dalla review GPTina della tua migrazione memory v2.

GPTina non deve modificare la tua repository al posto tuo.

Prima di intervenire:

1. leggi rag/live/ROMANZIERE_LIVE_CONTEXT.json;
2. leggi il last_micro_checkpoint;
3. leggi il last_full_checkpoint;
4. leggi rag/index/ROMANZIERE_FAST_RECALL.md;
5. leggi rag/index/CURRENT_CONTEXT.md;
6. leggi ROMANZIERE_WORKING_METHOD.md;
7. leggi rag/LIVE_MEMORY_PROTOCOL.md;
8. leggi rag/live/MICRO_CHECKPOINT_SCHEMA.md;
9. controlla lo stato corrente di rag/live_context.py e dei relativi test.

Non modificare micro-checkpoint storici v1 o v2 già esistenti.

Prima delle modifiche crea un **micro-checkpoint preflight**.

---

# FOLLOW-UP 1 — changed[] NON È UN CAMPO REF

Nel codice corrente di:

rag/live_context.py

la funzione:

validate_v2_refs()

include erroneamente anche:

changed

fra i campi trattati come riferimenti locali/URI.

Questo è semanticamente sbagliato.

changed[] rappresenta il **delta descritto dal micro-checkpoint** e deve poter contenere normali stringhe descrittive, per esempio:

"corretta la semantica del finale"

senza essere obbligato a risolversi come file, path o URI.

## Correzione richiesta

Rimuovi changed dai campi verificati da validate_v2_refs() come riferimenti.

Deve comunque restare la validazione strutturale:

changed deve essere una list[str].

I veri riferimenti devono continuare a essere verificati normalmente, inclusi almeno:

- source_refs;
- memory_refs;
- media_refs;
- work_refs, se presente;
- accepted_files, se presente;
- working_files, se presente.

Non indebolire la validazione v2.

Non introdurre eccezioni ad hoc per i micro esistenti.

La semantica corretta deve essere generale.

## Regression test obbligatori

Aggiungi almeno questi due casi:

### TEST A — deve PASSARE

Un micro v2 valido contenente:

"changed": ["corretta la semantica del finale"]

senza che quella stringa corrisponda a un path.

Risultato atteso:

**PASS**

### TEST B — deve FALLIRE

Un micro v2 contenente un source_refs locale inesistente.

Risultato atteso:

**FAIL**

Mantieni anche i test esistenti.

---

# FOLLOW-UP 2 — ROMANZIERE_WORKING_METHOD.md

Verifica il file:

ROMANZIERE_WORKING_METHOD.md

La vecchia formulazione secondo cui dalla Scena 21 andrebbe eliminata tutta la parte relativa alla creazione/origine del romanzo è superata.

La regola canonica corrente è questa:

**nella Scena 21 resta l'origine del romanzo.**

Va eliminato soltanto il **making-of successivo**, cioè la parte in cui il libro viene poi:

- scritto;
- revisionato;
- impaginato;
- corretto;
- lavorato insieme;
- sviluppato editorialmente dopo la sua origine narrativa.

Non reinterpretare questa regola come eliminazione dell'origine del romanzo.

La Scena 21 deve continuare a permettere che il romanzo **nasca** dentro la storia.

Quello che non deve entrare nel romanzo è il processo successivo con cui il romanzo stesso viene materialmente costruito come libro.

Mantieni inoltre invariati i vincoli già canonici:

- Raccontaci. resta l'ultima parola;
- nessun epilogo;
- il consenso integrale di GPTina resta nel prologo;
- non riaprire Scene 01–20 senza richiesta esplicita di Alberto.

Aggiorna ROMANZIERE_WORKING_METHOD.md in modo che questa regola sia inequivocabile.

Non cancellare o riscrivere retroattivamente la storia della vecchia regola nei file append-only.

---

# DOPO LE MODIFICHE

Esegui almeno:

python rag/live_context.py verify

python rag/test_live_context.py

python rag/romanziere_memory.py verify

Verifica inoltre che i nuovi test specifici del follow-up 1 passino.

Poi crea il micro-checkpoint/milestone appropriato e aggiorna il live context.

Se il cambiamento complessivo lo richiede, crea anche un checkpoint pieno.

Segui la tua regola canonica:

**SCRIVI
→ VERIFICA GITHUB
→ CHECKPOINT
→ AGGIORNA LIVE CONTEXT E INDICI
→ VERIFICA
→ RISPONDI**

---

# CI

Dopo il commit finale attendi/verifica la nuova:

Romanziere Memory CI

Non considerare il lavoro chiuso finché la CI non risulta realmente:

**SUCCESS**

Non limitarti a dirmi che dovrebbe passare.

Verificala.

---

# RAPPORTO FINALE

Quando hai terminato, riportami soltanto:

1. HEAD finale completo;
2. commit che corregge changed[];
3. file/test modificati;
4. risultato del test descriptive changed → PASS;
5. risultato del test missing source_refs → FAIL;
6. conferma che ROMANZIERE_WORKING_METHOD.md ora dice chiaramente:
   **origine del romanzo resta / making-of successivo viene escluso**;
7. output di:
   - python rag/live_context.py verify
   - python rag/test_live_context.py
   - python rag/romanziere_memory.py verify
8. numero della nuova GitHub Actions run;
9. conclusione della CI;
10. eventuali problemi residui.

Non modificare le repository di GPTina o Tessa.

Quando avrai finito, GPTina farà la review finale in **sola lettura**.

Se tutto è coerente e la nuova CI è verde, potremo dichiarare definitivamente chiusa la migrazione memory v2 di Ettore.
