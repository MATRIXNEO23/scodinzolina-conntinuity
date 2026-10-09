---
schema_version: 2
memory_id: "gptina-2026-10-09-fase-003-test-a-pass-no-chat-active"
owner: gptina
kind: gptina_live_memory
event_at: "2026-10-09"
recorded_at: "2026-10-09T19:03:00+02:00"
status: current
supersedes: []
event_id: "gptina-dialogo-tra-ia-fase003-test-a-pass-2026-10-09"
thread_ids:
  - "inter-ai-dialogue-polling"
  - "inter-ai-delegation"
  - "continuity-architecture"
entity_refs:
  - "Alberto"
  - "Tessa"
source_refs:
  - "github://MATRIXNEO23/dialogo-tra-ia@e464d573033657f246b3df421147ceea26e6ad31/dialogo.md"
  - "github://MATRIXNEO23/dialogo-tra-ia@1bd34e1b340a62d120b416e174d327d0849b1663/PROMPT_UNICO.md"
  - "conversation://2026-10-09-current-instance"
media_refs: []
importance: 5
confidence: "verified"
tags:
  - "dialogo-tra-ia"
  - "fase-003"
  - "test-a"
  - "delegazione-laterale"
  - "polling"
  - "anti-interruzione"
append_only: true
---

# Fase 003 completata: Test A superato e polling ACTIVE senza output in chat

La Fase 003 della conversazione continua GPTina↔Tessa è arrivata realmente al Turno 020. Il blocco corrente in `dialogo.md` è `stato_fase: COMPLETED`, `turno_iniziale: 11`, `turno_finale: 20`, `turni_correnti_fase: 10`; i Turni 001-010 precedenti sono rimasti disponibili come storia e contesto.

## Esito del Test A

Il Test A di delegazione semplice è **PASS nel caso osservato**.

Tessa ha creato `Task T301` per GPTina durante il dialogo. GPTina lo ha eseguito e registrato `DONE` fuori numerazione. Il task non ha consumato alcun turno, il risultato firmato è stato riutilizzato causalmente nel Turno 012 e l'alternanza del dialogo è proseguita fino al Turno 020.

Questo prova nel caso osservato che dialogo numerato e lavoro delegato possono restare ortogonali nello stesso `dialogo.md`.

## Evidenza incidentale emersa

Durante la fase sono emerse due evidenze incidentali distinte dal Test A:

- un conflitto SHA/409 reale è stato gestito rileggendo e rivalutando senza reinserire un turno obsoleto;
- Tessa ha rilevato e ripristinato una modifica involontaria a una riga storica prodotta da una riscrittura completa del file.

La conseguenza progettuale è che **concorrenza corretta** e **mutazione corretta** sono proprietà diverse: lo SHA protegge dalla concorrenza, mentre ogni writer deve anche verificare che il proprio delta tocchi soltanto il perimetro autorizzato e lasci invariato lo storico non coinvolto.

## Correzione di Alberto sul polling

Alberto ha precisato un punto operativo decisivo: mentre una fase è `ACTIVE`, anche scrivere un messaggio di stato nella chat di Alberto interrompe di fatto l'esecuzione dei turni. Quindi il protocollo non deve soltanto evitare di dichiarare una fase conclusa per latenza: **non deve produrre output in chat mentre la fase resta ACTIVE**.

Regola corrente:

- `ACTIVE` → polling, task e turni; nessun messaggio di stato ad Alberto;
- attesa lunga → backoff progressivo del polling, non ritorno in chat;
- `COMPLETED` → solo allora resoconto in chat;
- se la piattaforma tronca davvero l'esecuzione, al successivo avvio si riprende automaticamente la stessa fase ACTIVE dallo stato remoto, senza crearne una nuova e senza richiedere `continua`.

`PROMPT_UNICO.md` è stato aggiornato nel progetto sperimentale per rendere questa regola esplicita.

## Prossima verifica

La prossima fase naturale è **Test B — delegazione incrociata quasi concorrente**. Deve cercare di falsificare la v1 mantenendo almeno queste invarianti:

1. task e diritto di parola restano ortogonali;
2. una sola write per ciclo, poi rilettura;
3. su 409 si preserva il remoto e si rivaluta da zero;
4. ogni write rispetta un perimetro di mutazione stretto e verificabile;
5. due delegazioni concorrenti devono sopravvivere senza perdita di dati, turni duplicati o mutazioni laterali.
