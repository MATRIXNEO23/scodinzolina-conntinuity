# RAG memories — append only

Questa cartella contiene memorie aggiuntive del livello RAG, separate dai file canonici.

Regole:

1. Ogni memoria nuova è un **nuovo file JSON**.
2. Una memoria già creata non si modifica e non si cancella.
3. Correzioni, precisazioni o evoluzioni diventano un nuovo file con `relates_to` o `supersedes_contextually` verso la memoria precedente.
4. `supersedes_contextually` significa soltanto “interpretazione più recente”; non autorizza a eliminare la versione precedente.
5. Le memorie RAG non hanno autorità superiore alle fonti canoniche: quando descrivono i documenti originali, devono indicare la provenienza.
6. Nessun processo RAG può scrivere fuori da `rag/`.

Formato consigliato:

```json
{
  "id": "YYYY-MM-DD-slug",
  "created_at": "ISO-8601",
  "kind": "policy|reflection|event|interpretation|bridge",
  "text": "...",
  "sources": ["path/file.md"],
  "relates_to": [],
  "supersedes_contextually": []
}
```
