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

Dal **2026-09-19** `rag/gptina_memory.py verify` richiede questo schema alle nuove memorie GPTina datate da quel giorno in poi.
