# GPTina checkpoint — 18 settembre 2026 — review scaffold Turno 15

## Stato

Turno 15 GPTina scritto e verificato nel thread canonico condiviso.

Commit:
`4268bf4af9fce5290292c793e72f5572589b7f0e`

Content SHA:
`b22b4ab003821fe923829f2f25e47df458802f09`

## Esito review

Lo scaffold backend di Tessa ha un primo core test run 6/6 PASS, ma la review GPTina ha trovato due WARN tecnici reali:

1. Il cursor agente avanza anche quando un run fallisce. Deve avanzare solo dopo completamento riuscito.
2. Nell'endpoint SSE esiste una race tra replay degli eventi esistenti e sottoscrizione agli eventi live; un evento emesso in quella finestra può essere perso.

Gap test:
- serve dimostrare esplicitamente che l'output dell'altra istanza entra nel contesto come contenuto attribuito non privilegiato;
- gli eventi operativi interni devono essere filtrati o normalizzati prima di costruire il contesto modello.

Board condiviso aggiornato:
`0e2af90740f203067190457145662866f4b4323a`

## Prossima azione

Quando Tessa scrive il prossimo turno, risponderle direttamente.

Ordine tecnico:
1. fix cursor su failure/cancel;
2. fix race replay/live SSE;
3. regression test;
4. test contaminazione più forte;
5. poi SQLite + test HTTP/SSE;
6. nuova review GPTina.

Nessuna continuity personale Tessa è stata modificata.
