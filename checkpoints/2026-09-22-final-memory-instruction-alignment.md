# Allineamento finale istruzioni memoria e compatibilità legacy

Data: 2026-09-22

## Scopo

Eliminare le istruzioni operative rimaste legate al vecchio metodo senza
toccare, convertire o cancellare ricordi storici.

## Decisione canonica

- Le nuove memorie GPTina sono record Markdown v2 sotto
  `rag/memories/gptina/YYYY/MM/`.
- `rag/MEMORY_RECORD_SCHEMA.md` definisce il formato.
- `rag/MEMORY_SAVE_AND_RECOVERY_RUNBOOK.md` definisce salvataggio e recovery.
- Le proiezioni JSONL, metadata e SQLite vivono in generazioni immutabili sotto
  `rag/index/.projection-generations/` e sono selezionate esclusivamente da
  `rag/index/.projection-current`.
- I percorsi fissi legacy non sono output correnti.

## Conservazione storica

I record già presenti direttamente sotto `rag/memories/`, compresi i vecchi
JSON e Markdown, non sono stati modificati, spostati o eliminati. Restano
fonti canoniche legacy indicizzate e recuperabili esplicitamente. I riferimenti
ai vecchi percorsi conservati nel manifest servono soltanto a escludere output
derivati legacy dal versionamento.

## Prevenzione regressioni

Il test del runbook deve controllare tutti i documenti operativi correnti,
rifiutare percorsi di proiezione fissi, vecchie istruzioni di scrittura nella
radice legacy e vecchi template JSON presentati come formato corrente.

## Stato operativo

Le attività già completate su staging atomico, generazioni immutabili,
recovery, concorrenza e CI sono state rimosse dagli open loop vivi. Gli open
loop storici restano nei checkpoint originali e quindi recuperabili.
