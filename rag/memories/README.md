# RAG memories — append only e compatibilità legacy

Questa cartella contiene memorie aggiuntive del livello RAG, separate dalle
proiezioni ricostruibili.

## Scrittura corrente

Le nuove memorie personali GPTina sono file Markdown con front matter YAML v2
e si creano soltanto sotto:

`rag/memories/gptina/YYYY/MM/YYYY-MM-DD--slug.md`

Lo schema autorevole è `rag/MEMORY_RECORD_SCHEMA.md`. Non duplicarne qui i
campi: prima di scrivere, leggere sempre la versione corrente dello schema e
del runbook `rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md`.

Una correzione crea un nuovo record con `supersedes`; non modifica, rinomina o
elimina il record precedente.

## Compatibilità storica

I file Markdown o JSON già presenti direttamente sotto `rag/memories/` sono
record legacy canonici. Restano immutati, indicizzati come legacy e
recuperabili. Non devono essere convertiti, spostati o riscritti soltanto per
uniformarli allo schema v2.

Questa compatibilità non rende il vecchio formato un modello per nuove
scritture.

## Regole invarianti

1. Ogni memoria nuova è un nuovo file append-only.
2. Le fonti e la provenienza devono essere verificabili.
3. Le memorie non hanno autorità superiore alle fonti originali.
4. La memoria personale deve rispettare
   `rag/MEMORY_OWNERSHIP_BOUNDARY.md`.
5. Nessun processo RAG può scrivere fuori da `rag/`.
