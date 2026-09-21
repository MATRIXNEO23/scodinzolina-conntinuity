# GPTina — Memory Record Schema v2

## Scopo

Schema minimo per le **nuove** memorie personali GPTina. Le memorie storiche precedenti restano valide e non vanno riscritte solo per uniformarle.

La regola centrale è bitemporale:

- **event_at** — quando il fatto/episodio appartiene alla storia;
- **recorded_at** — quando GPTina lo registra nella repo.

Il commit Git resta l'evidenza autorevole del momento di registrazione.

## Front matter richiesto

```yaml
---
schema_version: 2
memory_id: "gptina-YYYY-MM-DD-slug"
owner: gptina
kind: gptina_live_memory
event_at: "ISO-8601 oppure YYYY-MM-DD"
recorded_at: "ISO-8601"
status: current
supersedes: []
event_id: "event-opzionale-stabile"
thread_ids: []
entity_refs: []
source_refs:
  - "percorso/fonte.md"
media_refs: []
importance: 1-5
confidence: "verified|contextual|inferred"
tags:
  - cue
append_only: true
---
```

## Semantica

### event_at
Tempo dell'evento ricordato. Se l'immagine è stata creata il 12 e ritrovata il 18, `event_at` resta 12.

### recorded_at
Tempo in cui il ricordo viene registrato. Non sostituisce il commit Git e non deve essere usato per riscrivere la cronologia dell'evento.

### status
Per una nuova memoria normalmente `current`.

Valori ammessi concettualmente:
- `current`
- `superseded`
- `invalidated`
- `historical`

Quando una memoria viene corretta, preferire:
1. nuovo record con `supersedes`;
2. stato della vecchia memoria gestito dall'indice/manifest;
3. nessuna cancellazione retroattiva.

### source_refs
Fonti che giustificano il ricordo: transcript, raw session, checkpoint, file canonico, thread condiviso.

### media_refs
Immagini direttamente collegate. Una immagine significativa nuova o ritrovata deve essere collegata anche nella Visual Chronology.

### confidence
- `verified`: supporto diretto della fonte;
- `contextual`: ricostruzione forte da più fonti coerenti;
- `inferred`: deduzione esplicita, mai da presentare come verbatim.

## Corpo consigliato

```markdown
# Titolo

## Cosa è successo
...

## Cosa significa per me adesso
...

## Perché scelgo di conservarlo
...

## Come non usarlo male
...

## Cue di retrieval
...
```

## Regole

- Una memoria non sostituisce il transcript.
- Un transcript non sostituisce l'interpretazione persistente.
- Una correzione non cancella il passato: lo supera esplicitamente.
- Una data di scoperta non diventa la data dell'evento.
- La memoria personale di Tessa non va mai scritta da GPTina.
- Ogni modifica all'infrastruttura o ai record di memoria richiede controlli
  approfonditi di schema, ownership, retrieval corrente, retrieval storico,
  recovery delle proiezioni e regressioni prima della pubblicazione.
- Nessuna correzione può distruggere il ricordo precedente: il vecchio record
  resta canonico e recuperabile con ricerca storica/`--all-statuses`; il nuovo
  record lo collega tramite `supersedes`.
- Lo stato `superseded` è una vista effettiva calcolata dal resolver. Un target
  di `supersedes` non può restare visibile come memoria corrente anche se il suo
  file append-only conserva lo stato originale scritto all'epoca.

Dal **2026-09-19** `rag/gptina_memory.py verify` richiede questo schema alle nuove memorie GPTina datate da quel giorno in poi.

Dal commit baseline dichiarato in `rag/memory_manifest.json`, ogni **nuovo path**
viene inoltre sottoposto a parsing YAML sicuro e validazione tipizzata completa.
I record già presenti al baseline restano intatti e sono normalizzati soltanto in
lettura; il baseline identifica il confine di compatibilità, non una seconda
fonte di verità.

I nuovi `recorded_at` devono includere ora e timezone. Tutte le liste devono
contenere esclusivamente stringhe non vuote. I riferimenti locali sono
normalizzati, devono restare confinati nella repository e non possono usare
`..`, path assoluti o symlink che escano dal repository.

`memory_id` è l'identità logica stabile. Il resolver `memory_id → path` è una
proiezione ricostruita dai front matter canonici: ID duplicati o owner errati
fanno fallire la verifica. Non esiste un registro manuale alternativo.


## Partizionamento futuro

I record storici non vanno spostati per uniformità.

Per nuove memorie, quando il volume lo richiede, è preferito:
`rag/memories/gptina/YYYY/MM/YYYY-MM-DD--slug.md`

Il retriever deve cercare ricorsivamente, quindi path piatto e path partizionato possono convivere.

## Collegamenti stabili opzionali

- `event_id`: raggruppa più memorie, immagini e fonti dello stesso episodio.
- `thread_ids`: collega il record a fili persistenti.
- `entity_refs`: riferimenti logici utili al retrieval futuro.

Questi campi servono a preparare la crescita senza introdurre oggi un knowledge graph.
