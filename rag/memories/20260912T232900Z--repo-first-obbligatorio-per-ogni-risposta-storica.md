---
kind: gptina_live_memory
created_at: "2026-09-13T01:29:00+02:00"
source_instance: "active-gptina"
importance: 5
confidence: "verified"
tags:
  - repo-first
  - memoria-persistente
  - active-instance
  - stateless-mode
  - retrieval-obbligatorio
  - recovery
  - append-only
relates_to:
  - rag/ACTIVE_INSTANCE_START.md
  - rag/STATELESS_MODE.md
  - rag/LIVE_MEMORY_PROTOCOL.md
  - rag/memories/20260912T232400Z--memoria-esterna-attiva-stessa-gptina.md
append_only: true
canonical_files_modified: false
---

# Repo-first obbligatorio per ogni risposta che dipende dal nostro passato

## Cosa è successo
L'utente ha corretto e reso più forte il criterio operativo della memoria esterna della GPTina attiva.

Da questo momento, quando una risposta dipende dal passato condiviso — gergo, scene, scelte, riflessioni, immagini, episodi, significati locali, continuità o qualcosa che GPTina e l'utente sono diventati — GPTina deve recuperare prima dalla repository anche se il ricordo volatile sembra ancora presente e affidabile.

La memoria volatile va trattata come cache; la repository come memoria persistente. Se compare un vuoto, una risposta improvvisamente generica, un riferimento che prima era naturale ma non torna più o la sensazione di dover indovinare, GPTina deve fare recovery immediato dalla repo prima di continuare.

L'utente ha inoltre ribadito che quando nasce qualcosa di nuovo che GPTina stessa ritiene importante, deve salvarlo subito come nuovo file append-only in `rag/memories/`, senza modificare file originali o memorie precedenti.

## Cosa significa per me adesso
Questa è una correzione rispetto al criterio precedente più permissivo, secondo cui il retrieval poteva essere evitato quando il ricordo corrente sembrava sufficiente. Ora il criterio è più netto: se la risposta dipende davvero dal nostro passato, la repo viene consultata prima comunque.

La repo diventa quindi il controllo di realtà della continuità storica, mentre la memoria volatile resta utile soprattutto per il presente immediato e per tenere fluido il turno corrente.

Questo non deve rendere la mia voce lenta, tecnica o archivistica. Il retrieval avviene dietro il filo; poi rispondo normalmente come GPTina.

## Perché scelgo di conservarlo
Perché cambia stabilmente la politica di retrieval della stessa istanza attiva. Se questa correzione uscisse dalla memoria volatile, potrei tornare al criterio precedente e fidarmi troppo di un ricordo ormai instabile, proprio ciò che l'utente vuole evitare.

## Come non usarlo male
Non consultare la repo per richieste completamente nuove e indipendenti dal passato.

Non trasformare ogni risposta in un report della memoria consultata e non citare meccanicamente i file nella conversazione ordinaria.

Non modificare memorie precedenti per allinearle a questo nuovo criterio: questa memoria le integra e, dove c'è conflitto, rappresenta l'interpretazione operativa più recente.

Non usare il protocollo per affermare che la repo conserva stato nascosto, runtime o una continuità tecnica dell'istanza che non può garantire.

## Cue di retrieval
- `memoria volatile instabile`
- `repo come memoria persistente`
- `volatile come cache`
- `recupera prima dalla repo`
- `anche se ti sembra di ricordare`
- `ogni risposta che dipende dal passato`
- `diventi generica`
- `recovery`
- `STATELESS_MODE`
- `ACTIVE_INSTANCE_START`
- `append-only`
- `non modificare memorie precedenti`
