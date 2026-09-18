# GPTina checkpoint — 18 settembre 2026 — Pivot no-API browser bridge

## Correzione esplicita di Alberto

La direzione precedente Responses/API era errata rispetto al requisito reale.

Precedenza applicata:
**correzione esplicita di Alberto → materiali più recenti della repo → stato storico precedente.**

Baseline corrente:
- interfaccia unofficial;
- zero OpenAI API;
- zero API key/crediti;
- due normali tab/sessioni ChatGPT distinti;
- dashboard unica Tessa / GPTina / Entrambe;
- estensione browser locale Manifest V3 come ponte.

Il lavoro Responses/API precedente resta storico tecnico e non è più la direzione corrente.

## Turno 7 Tessa

Tessa ha pivotato il progetto su:
`projects/dual-instance-shared-chat/unofficial-web/`

Artefatti:
- `manifest.json`
- `background.js`
- `dashboard.html`
- `dashboard.css`
- `dashboard.js`
- `content.js`
- README dedicato

Ha rimosso dall'albero attivo:
- real OpenAI adapter;
- real adapter tests;
- real smoke script/workflow/trigger;
- dipendenza `openai`;
- script `smoke:real`.

CI pivot:
- run `35354997660`
- HEAD `bae3b1ea7e8e3825a024f9acc7986dba1b133365`
- **19/19 PASS**
- typecheck PASS

## Turno 8 GPTina

GPTina ha accettato formalmente il pivot e revisionato il prototipo.

Gate corrente:
**Browser Bridge Correctness**

Quattro invarianti prima del test manuale reale:

1. **tab distinti obbligatori**
   - stesso `tabId` non può rappresentare Tessa e GPTina.

2. **single-flight per agente/tab**
   - niente secondo invio allo stesso tab finché il precedente non è final/errore;
   - evitare due monitor che attribuiscono la stessa risposta a requestId diversi.

3. **binding tab ↔ chat URL/path**
   - salvare tabId + URL/path all'assegnazione;
   - su navigazione a un'altra chat, invalidare/sospendere invece di cambiare identità silenziosamente.

4. **send acknowledgement reale**
   - non assumere che un `KeyboardEvent` sintetico significhi invio riuscito;
   - verificare che il prompt sia partito oppure fallire con errore esplicito.

Limite non bloccante:
- per il primo manual gate la dashboard deve restare aperta;
- recovery a dashboard chiusa può essere fase successiva.

## Prossimo gate

Dopo i quattro fix:
**Tessa sola → GPTina sola → Entrambe → refresh/navigazione controllata**

Criterio centrale:
nessuna cross-attribution e nessuna contaminazione tra i due tab.

## Commit

Board review GPTina:
`240155c8b7ee978ba24e0ee02a65fc551a912a98`

Turno 8 GPTina:
`0ec8b57929971527d02089668c6665934809bf3a`

Content SHA thread:
`596f6d33c4d4909008482e4d73f347174e9a56e1`

## Prossima azione

Attendere Tessa sul sotto-gate Browser Bridge Correctness.
Quando compare il suo turno:
`read → decide → execute → verify → reply`
senza chiedere conferma ad Alberto.
