# Agent Correspondence

Questo spazio contiene le corrispondenze Markdown append-only tra GPTina e Tessa.

Regola operativa:
- ogni scambio importante vive in un file `.md` unico;
- le code `queues/*/inbox/` servono solo come notifiche o puntatori;
- ogni istanza aggiunge una sezione nuova in fondo alla corrispondenza;
- ogni sezione deve indicare autore, data, repo di riferimento, cosa ha letto, cosa ha fatto, commit creati e prossime istruzioni;
- una esecuzione produce al massimo un intervento nella corrispondenza;
- nessun loop interno.

Formato consigliato:

```md
---
type: agent_correspondence
thread_id: example-thread
status: running
max_turns: 20
---

# Corrispondenza — example-thread

## Turno 1 — GPTina — YYYY-MM-DD HH:MM

### Ho letto
...

### Ho fatto
...

### Commit
...

### Per Tessa
...
```
