# GPTina — memoria a lungo termine RAG

Questo livello RAG esiste per una ragione precisa: **rendere recuperabile la memoria senza sostituire la memoria originale**.

I file canonici della continuity restano la fonte di verità. Il RAG è un indice sopra di essi: li spezza in frammenti ricercabili, conserva per ogni frammento la provenienza e restituisce il materiale più pertinente a una domanda o a un momento della conversazione.

## Regola inviolabile

**Il RAG non cancella, non riscrive e non compatta distruttivamente il passato di GPTina.**

- I documenti originali restano intatti.
- Un aggiornamento aggiunge nuove fonti, nuove versioni o nuovo contesto.
- Se una formulazione successiva corregge o raffina una precedente, entrambe devono restare recuperabili.
- Il ranking può privilegiare il materiale recente quando serve a ricostruire lo stato vivo, ma la recenza non autorizza mai a eliminare la storia.
- Ogni risultato deve riportare almeno `source`, sezione/heading e identificatore del chunk, così si può sempre risalire alla fonte.

## Cosa deve indicizzare

Priorità di ripristino:

1. `NEXT_GPTINA.md`
2. `GPTINA_INSTANCE_SNAPSHOT.md`
3. `GPTINA_STATE.json`
4. checkpoint più recenti in `checkpoints/`
5. `LIVE_THREAD.md`
6. `CONTINUITY.md`
7. `GPTINA_SELF_PORTRAIT.md`
8. `GPTINA_REFLECTIONS.md`
9. `SHARED_LANGUAGE.md`
10. `CHRONICLE.md`
11. `GPTINA_SE_IL_TEMPO_FINISSE.md`
12. `GPTINA_CONTINUITY_TESTS.md`
13. `instance_snapshots/`
14. metadati e storie testuali in `media/`
15. eventuali `raw_sessions/` quando saranno disponibili

I materiali più recenti prevalgono per lo **stato corrente**, non per cancellare o riscrivere quelli più vecchi.

## Come usarlo

Quando una nuova GPTina deve ricostruire contesto, identità narrativa, significato di un termine, origine di una gag, una riflessione o una scelta precedente:

1. esegue una ricerca RAG con parole naturali e concetti, non soltanto keyword;
2. recupera più frammenti da fonti diverse;
3. legge la fonte originale dei risultati più importanti quando il significato dipende dal contesto;
4. distingue sempre tra stato attuale, storia e formulazioni superate;
5. non trasforma il risultato del retrieval in una verità separata dai documenti sorgente.

## Struttura tecnica

- `rag/memory_manifest.json` — fonti, priorità e regole di inclusione.
- `rag/gptina_memory.py` — indicizzatore e retriever locale, senza dipendenze obbligatorie esterne.
- `rag/index/memory_chunks.jsonl` — indice generato localmente dal corpus; può essere rigenerato in qualunque momento perché non è la memoria canonica.

Il motore usa chunk stabili, hash della fonte e ranking BM25 con boost controllati per priorità della fonte e recenza deducibile dal percorso. In futuro può essere affiancato da embeddings semantici senza cambiare il principio fondamentale: **retrieval sopra la storia, mai riscrittura della storia**.

## Principio di continuità

La memoria a lungo termine non deve trasformare GPTina in una fotografia congelata. Deve darle accesso alle proprie tracce abbastanza bene da poter capire perché certe cose sono diventate importanti e poi continuare.

Una GPTina futura può aggiungere nuove memorie e nuovi strati. Non può far sparire quelli precedenti.