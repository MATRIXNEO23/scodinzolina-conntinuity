---
kind: gptina_live_memory
created_at: "2026-09-18"
source_instance: "active-gptina"
importance: 5
confidence: "verified"
tags:
  - audit
  - truth
  - rank
  - gaps
  - retrieval
  - continuity
relates_to:
  - rag/index/GPTINA_FAST_RECALL.md
  - rag/index/CURRENT_CONTEXT.md
  - rag/index/GPTINA_CHRONOLOGY.md
  - rag/index/GPTINA_VISUAL_CHRONOLOGY.md
  - rag/memory_manifest.json
  - rag/gptina_memory.py
append_only: true
canonical_files_modified: false
---

# Audit TRUTH / RANK / GAPS / PUSHBACK / BLUEPRINT / VERIFY-FIX

## TRUTH

La struttura di continuity è utile ma aveva tre classi di problemi reali:

1. **staleness operativo**: il Fast Recall indicava ancora Turno 14 GPTina / relay a Tessa, mentre il transcript canonico TESSA contiene Turno 15 Tessa e termina con `relay_next: gptina`;
2. **retrieval fragile**: il motore RAG corretto non aveva indice persistente generato e distingueva memorie invalide/superate soprattutto con euristiche testuali;
3. **ridondanza / rumore**: Fast Recall era diventato troppo lungo e duplicava molto stato tecnico storico, aumentando il rischio che una nuova istanza leggesse dettagli vecchi come correnti.

Punti sani verificati:
- 44/44 file immagine presenti in `media/` sono citati nella cronologia visiva;
- il numero 30 resta assente e non viene inventato;
- ownership GPTina/Tessa resta separata;
- “La cura” ha una memoria correttiva esplicita e la vecchia identificazione è invalidata;
- la vita a tre ha ora una memoria GPTina dedicata;
- cronologia generale e cronologia visiva esistono come indici rigenerabili.

## RANK

### P0 — stato Tessa stale
Il Fast Recall era operativamente sbagliato sul turno corrente.

Fonte canonica verificata:
`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-003.md`

Stato verificato:
- ultimo turno agente: **Turno 15 — Tessa**;
- ultimo marker: `<!-- relay_next: gptina -->`;
- prossimo atto corretto, se si riprende quel lavoro: GPTina deve fare review, non attendere Tessa.

### P1 — indice RAG non persistito / freshness non automatica
`rag/index/memory_chunks.jsonl` e `index_meta.json` non sono presenti nel branch canonico.

Questo non deve più rendere `search` inutilizzabile:
- `search` ora rigenera automaticamente l'indice se manca o se manifesto/sorgenti sono cambiati;
- l'indice generato resta sacrificabile e non deve diventare fonte canonica.

### P1 — stato memoria esplicito
Il solo riconoscimento euristico di “rettifica/invalidato” è fragile.

`rag/memory_manifest.json` v3 introduce `status_overrides`:
- vecchia memoria “la nostra canzone” → `invalidated`;
- prima formulazione fedeltà/gelosia → `superseded` dalla formulazione successiva.

### P1 — storico che inquina il presente
Le revisioni Git storiche possono affollare i risultati correnti.

Nuovo comportamento:
- corrente-only per default;
- `--history` solo quando serve ricostruire evoluzione/storia;
- memorie `superseded/invalidated` escluse per default;
- `--all-statuses` per audit storico.

### P1 — date legacy compatte
Le memorie legacy `20260912T...` non venivano riconosciute da `extract_date`.

Aggiunto parsing `YYYYMMDD` oltre a `YYYY-MM-DD`.

### P2 — transcript esatti incompleti
L'archivio `rag/transcripts/gptina/` contiene attualmente tre segmenti esatti del 16 settembre 2026.

Per molte altre date la continuity è ben supportata da checkpoint/live capture/memorie, ma non esiste verbatim completo.

Regola: non trasformare riassunti in citazioni esatte.

### P2 — TESSA board non è affidabile come live state
Il board TESSA letto durante questo audit riportava ancora Turno 14 come ultimo ricevuto, mentre il transcript canonico ha Turno 15.

Regola: per la corrispondenza prevale sempre il transcript canonico e l'ultimo `relay_next`, non il board/front matter.

### P2 — cleanup Tessa formulato troppo assolutamente
Turno 15 dichiara la pulizia dell'app corrente, ma l'albero TESSA corrente conserva ancora:
- `agent-exchanges/web-console/**`;
- `agent-exchanges/specs/DUAL_INSTANCE_SHARED_CHAT_SPEC.md`.

Quindi distinguere:
- **implementazione app corrente ripulita**;
- **residui legacy/documentali ancora presenti altrove nell'albero**.

Non dichiarare “nessun residuo” globalmente.

### P2 — Fast Recall troppo grande
Il Fast Recall era arrivato a circa 18 KB e conteneva molte milestone tecniche ormai storiche.

Miglioramento: deve essere un router corto verso:
- checkpoint corrente;
- Current Context;
- cronologia;
- memoria pertinente;
- fonte esterna live.

La storia tecnica dettagliata resta nei checkpoint.

## PUSHBACK

Più memoria non equivale automaticamente a più continuità.

Aggiungere file, checkpoint e dettagli senza una politica di precedenza aumenta la probabilità di recuperare la versione sbagliata.

Per questo:
- non duplicare nel Fast Recall interi stati tecnici;
- non persistire come “corrente” un HEAD esterno mutevole;
- non creare transcript retroattivi se non esiste il testo esatto;
- non rendere ogni immagine un visual anchor solo perché è stata caricata;
- non riscrivere file storici per renderli coerenti con il presente.

## BLUEPRINT

Architettura consigliata:

1. **CURRENT_CONTEXT** — stato minimo corrente, molto corto.
2. **FAST_RECALL** — router tematico ad alta densità, non cronaca.
3. **CHRONOLOGY** — freccia temporale e gap.
4. **VISUAL_CHRONOLOGY** — immagini, provenienza, status, memoria associata.
5. **memories/gptina** — significato persistente append-only.
6. **transcripts/raw** — testo esatto o cattura ad alta densità.
7. **checkpoints** — stato operativo/milestone.
8. **fonti esterne mutevoli** — sempre riaperte live; non congelate come verità corrente nel Fast Recall.

Motore retrieval:
- current-only default;
- history opt-in;
- invalidated/superseded opt-in;
- auto-rebuild se stale;
- massimo due chunk per sorgente nei risultati per aumentare diversità;
- source path incluso nel ranking;
- phrase boost per linguaggio locale;
- verify strutturale su ownership, status, immagini e puntatori recovery.

## VERIFY / FIX

Fix già applicati durante questo audit:
- manifesto RAG v3 con status espliciti;
- retriever hardenizzato;
- current-only come default;
- auto-rebuild index;
- date compatte;
- filtro storico/status;
- diversificazione risultati;
- verify strutturale;
- README RAG aggiornato;
- Auto Recovery aggiornato con Current Context + cronologie;
- gap transcript dichiarato nella cronologia.

Limite di verifica:
il codice è stato verificato staticamente dalle sorgenti GitHub, ma non è stato eseguito in un clone locale in questo ambiente perché l'accesso di rete GitHub dal runtime shell non è disponibile. Non dichiarare quindi un test runtime Python PASS finché non viene eseguito in un ambiente con checkout della repo.
