# GPTina — archivio cronologico dei turni visibili

owner: gptina
append_only_source: true

Questo spazio conserva il contesto conversazionale visibile in forma cronologica, separato dalle memorie curate di GPTina.

## Scopo

- Il transcript conserva **ciò che è stato detto**.
- `rag/memories/gptina/` conserva **ciò che GPTina sceglie come importante** e come lo interpreta.
- `checkpoints/` conserva fotografie ad alta densità dello stato raggiunto.
- `rag/index/` contiene mappe rigenerabili per il richiamo rapido.

Nessuno di questi livelli sostituisce gli altri.

## Struttura

Usare segmenti immutabili organizzati cronologicamente:

`rag/transcripts/gptina/YYYY/MM/DD/YYYY-MM-DDTHHMM-local--segment-NNN.md`

Ogni segmento contiene, quando disponibili con certezza, i turni USER/GPTINA esattamente come visibili all'utente. Non include istruzioni di sistema, developer, chain-of-thought, tool call interni o dati non visibili.

## Cadenza

Durante una conversazione attiva, creare un nuovo segmento circa ogni **6–8 turni visibili** (circa 3–4 scambi completi), oppure prima se avviene una svolta che non deve rischiare di uscire dalla finestra volatile.

La cadenza non è un cronometro rigido: conta non lasciare accumulare troppo contesto non ancora esternalizzato.

## Regola append-only

Un segmento già creato non va riscritto per renderlo più elegante o coerente. Se manca qualcosa o una ricostruzione successiva migliora il quadro, creare un nuovo segmento/addendum che rimandi al precedente.

Se il testo esatto dei turni non è più disponibile, **non chiamare il file “integrale”**. Etichettarlo chiaramente come `reconstructed-summary` o `context-recovery`.

## Immagini e file

Quando un turno produce un'immagine o un artifact importante, il transcript può registrare il nome del file e il significato conversazionale. La presenza canonica del binario va però verificata nella sua cartella (`media/` o altra destinazione) prima di considerarlo archiviato.

## Retrieval

Per ricostruire un episodio:

1. partire dall'indice cronologico o tematico in `rag/index/`;
2. aprire il segmento della data/ora indicata;
3. usare le memorie curate per capire perché quel segmento conta;
4. tornare alle fonti canoniche più vecchie quando il riferimento precede questo archivio.

## Confini

Questo spazio appartiene a GPTina. La policy `rag/MEMORY_OWNERSHIP_BOUNDARY.md` resta superiore: lettura incrociata consentita, scrittura incrociata vietata. Non usare questo archivio per modificare o riscrivere memorie di Tessa.
