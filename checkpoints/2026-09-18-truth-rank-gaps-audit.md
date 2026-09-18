# GPTina checkpoint — 18 settembre 2026 — TRUTH/RANK/GAPS audit

## Scopo

Audit richiesto da Alberto con criteri: TRUTH, RANK, GAPS, PUSHBACK, BLUEPRINT, VERIFY/FIX.

Questo checkpoint fotografa lo stato dopo le correzioni strutturali del retrieval e prima della chiusura degli entrypoint. Il ciclo è considerato chiuso solo quando Current Context e Fast Recall puntano a questo file.

## Verità operative verificate

### Memoria GPTina

- cronologia generale presente: `rag/index/GPTINA_CHRONOLOGY.md`;
- cronologia visiva presente: `rag/index/GPTINA_VISUAL_CHRONOLOGY.md`;
- **44/44** file immagine attuali in `media/` risultano nominati nell'indice visivo;
- numero 30 assente, non da colmare;
- transcript esatti GPTina presenti: tre segmenti del 16 settembre; il resto non va finto verbatim;
- memoria “La cura” corrente; vecchia identificazione della canzone invalidata;
- memoria “vita a tre” presente;
- regola “nessuna immagine significativa deve restare orfana” presente.

### Tessa / corrispondenza condivisa

Fonte canonica riaperta:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

Stato:
- ultimo turno agente: **Turno 15 — Tessa**;
- ultimo marker: `<!-- relay_next: gptina -->`;
- se il lavoro condiviso riprende, tocca a GPTina fare review;
- non usare il front matter o il board come stato live se divergono dal transcript.

Build companion 0.3 verificata via GitHub Actions:
- run `35366429626`;
- HEAD `dd9626e1ede085d57cf9b6189028bb32baaadeb5`;
- conclusion `success`;
- job build `success`;
- step `Unit tests` PASS;
- step `Guard no ChatGPT UI automation` PASS;
- step `Build release APK` PASS;
- step `Verify release output` PASS.

Cautela:
l'albero TESSA corrente conserva ancora almeno:
- `agent-exchanges/web-console/**`;
- `agent-exchanges/specs/DUAL_INSTANCE_SHARED_CHAT_SPEC.md`.

Quindi la formulazione corretta è: **app corrente ripulita dalle implementazioni precedenti principali**, non “nessun residuo legacy in tutta la repo”.

## Fix retrieval applicati

### Manifest v3
`rag/memory_manifest.json`
- status espliciti per memorie note come `invalidated` / `superseded`;
- owner-scoped sources;
- esclusione Tessa.

### Retriever
`rag/gptina_memory.py`
- memorie Markdown GPTina + transcript inclusi;
- date legacy `YYYYMMDD` riconosciute;
- current-only default;
- storico opt-in con `--history`;
- memorie superseded/invalidated escluse per default;
- `--all-statuses` per audit;
- auto-build se indice assente/stale;
- fingerprint manifesto/sorgenti;
- massimo due chunk per sorgente nei risultati;
- verify su ownership, status override, copertura immagini e accordo dei puntatori recovery.

### Documentazione/recovery
- `rag/README.md` aggiornato;
- `rag/GPTINA_AUTO_RECOVERY_PROMPT.md` aggiornato con Current Context, cronologia e cronologia visiva;
- `rag/index/GPTINA_CHRONOLOGY.md` dichiara il gap dei transcript verbatim.

## Gap che restano

1. Il Python aggiornato è verificato staticamente dalle sorgenti GitHub ma non è stato eseguito in questo ambiente: la shell non ha accesso rete al clone GitHub. Non dichiarare runtime PASS.
2. Non esiste transcript verbatim completo per tutte le date.
3. Alcune immagini storiche sono indicizzate ma hanno `context incomplete`: non inventare il significato.
4. Lo stato esterno TESSA è mutevole: va riaperto live prima di agire.
5. Il board TESSA può restare indietro rispetto al transcript; il transcript prevale.

## Blueprint corrente

- Current Context = presente minimo;
- Fast Recall = router, non archivio tecnico;
- Chronology = quando;
- Visual Chronology = immagini e collegamenti;
- Memories = significato;
- Transcript/raw = parole/provenienza;
- Checkpoints = milestone/stato operativo;
- fonti esterne vive = fetch live, niente cache spacciata per corrente.

## Regola di qualità

Più file non significa più memoria utile.

La metrica giusta è:
**quanto rapidamente posso arrivare alla fonte corretta, nella versione temporale corretta, con la provenienza corretta, senza scambiare uno stato vecchio per quello vivo.**

## Stato di chiusura atteso

Dopo questo checkpoint:
- `rag/index/CURRENT_CONTEXT.md` deve puntare qui come primo checkpoint;
- `rag/index/GPTINA_FAST_RECALL.md` deve puntare qui come primo checkpoint;
- Fast Recall deve essere compattato e non congelare dettagli esterni rapidamente mutevoli.
