# GPTina — Audit compatibilità micro-checkpoint v1

Data audit: 21 settembre 2026.

## Scopo

Questo audit è stato eseguito **in lettura** su tutti i micro-checkpoint legacy `schema_version: 1` presenti nella repository, per rendere il verifier compatibile con le forme storiche realmente esistenti senza riscrivere i file append-only.

Totale micro-checkpoint presenti al momento dell'audit: **52**.

- v1 legacy letti: **50**
- v2 correnti: **2**

## Risultato

Tutti i 50 record v1 hanno:

- `schema_version`
- `owner`
- `kind`
- `event_at`
- `recorded_at`
- `change_type`
- `summary`
- `next_action`

Non sono emersi errori di tipo nei campi presenti.

Per questo il verifier v1 mantiene questi campi come nucleo obbligatorio e normalizza soltanto i campi che risultano realmente assenti in almeno un record storico.

## Profili legacy osservati

### Profilo completo

**31 record** hanno già tutti i campi del contratto v2.

Non richiedono alcuna normalizzazione.

### Mancano `memory_refs` e `media_refs`

**1 record**:

- `2026-09-20T134300+0200--preflight-v4-definitiva-a-modo-mio.json`

### Mancano `memory_refs`, `media_refs`, `preflight`

**11 record**.

### Mancano `memory_refs` e `preflight`

**1 record**:

- `2026-09-20T184000+0200--stato-copertina-a-modo-mio.json`

### Mancano solo `media_refs`

**4 record**:

- `2026-09-21T082600+0200--tessa-sorellina-ti-voglio-bene.json`
- `2026-09-21T082900+0200--correzione-origine-tessa-ettore.json`
- `2026-09-21T083100+0200--gptina-nata-per-caso.json`
- `2026-09-21T093200+0200--intimita-piu-spontanea-restando-gptina.json`

### Record legacy sparso — candidata V6

**1 record**:

`2026-09-20T161400+0200--v6-candidata-a-modo-mio.json`

Mancano:

- `micro_id`
- `thread_ids`
- `source_refs`
- `memory_refs`
- `media_refs`
- `importance`
- `preflight`

### Record legacy sparso — preflight impaginazione

**1 record**:

`2026-09-20T224500+0200--preflight-impaginazione-ariosa-a-modo-mio.json`

Mancano:

- `changed`
- `thread_ids`
- `source_refs`
- `memory_refs`
- `media_refs`
- `importance`
- `preflight`

Contiene inoltre due campi storici aggiuntivi, da preservare e ignorare ai fini della validazione corrente:

- `constraints`
- `starting_point`

## Riferimenti legacy osservati

Nei v1 compaiono riferimenti con questi schemi esterni:

- `conversation://`
- `github://`
- `artifact://`
- `attachment://`
- `commit://`

Esistono anche riferimenti locali che in seguito sono stati rinominati o spostati, per esempio durante la correzione della numerazione immagini.

Per i v1 il verifier richiede quindi soltanto che un riferimento presente non sia vuoto; non pretende che il target storico esista ancora allo stesso percorso.

Per i v2 resta invece la validazione corrente rigorosa dei riferimenti.

## Normalizzazione v1 consentita

Soltanto durante la validazione, senza modificare il JSON storico:

- `micro_id` mancante → stringa vuota;
- `changed` mancante → `[]`;
- `thread_ids` mancante → `[]`;
- `source_refs` mancante → `[]`;
- `memory_refs` mancante → `[]`;
- `media_refs` mancante → `[]`;
- `importance` mancante → `3`;
- `preflight` mancante → `false`.

Non vengono normalizzati `event_at`, `recorded_at` o `next_action`, perché l'audit ha verificato che sono presenti in tutti i 50 record v1.

## Regola

**Compatibilità significa capire le varianti storiche realmente esistenti, non rendere il v1 arbitrariamente permissivo.**

I record v1 restano immutati. Tutti i nuovi micro-checkpoint devono essere v2 e rispettare integralmente lo schema corrente.
