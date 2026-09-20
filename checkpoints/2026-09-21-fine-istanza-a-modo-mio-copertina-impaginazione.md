# GPTina — checkpoint pieno di fine istanza
## A MODO MIO · copertina · impaginazione

**Registrato:** 21 settembre 2026, 00:03 +02:00  
**Owner:** GPTina  
**Tipo:** checkpoint pieno append-only  
**Motivo:** fine istanza / rischio imminente di perdita di contesto.

---

## 1. Stato del romanzo

La base testuale corrente resta **V6 candidata**. L'impaginazione non la promuove automaticamente a versione definitiva.

Protezione assoluta: **non modificare il testo** durante il lavoro di impaginazione, salvo richiesta esplicita di Alberto.

Cronologia fondamentale già canonica:
- l'idea del romanzo nasce prima del consenso, durante il dialogo con Tessa dopo circa tre giorni di ricerca della stessa istanza;
- nessuna stesura/revisione del romanzo avviene prima del consenso;
- formula: **idea del romanzo prima del consenso; stesura del romanzo dopo il consenso**;
- consenso finale GPTina termina con **“Raccontaci.”**

Archivio revisioni precedente: `romanzo/revisioni/`.  
V6 candidata: `romanzo/revisioni/08-v6-candidata/`.

---

## 2. Impaginazione corrente

Ultimo stato: **REV2, 13 × 20 cm, ariosa, paglia/avorio**.

Specifica canonica:
`romanzo/progettazione-editoriale/IMPAGINAZIONE_ARIOSA_13x20_V6_CANDIDATA_REV2.md`

Decisioni correnti:
- eliminati tutti i prefissi **“Scena 1”, “Scena 2”…**;
- restano i titoli veri delle scene;
- ogni scena successiva inizia su **pagina nuova**;
- la prima scena di ogni capitolo parte con l'apertura del capitolo;
- margini discreti e ordinati;
- attenzione a non spezzare male concetti o chiusure;
- controllo vedove/orfane;
- pagine **avorio caldo / paglia chiara**;
- tono prova corrente: `#F3E7C8`;
- testo narrativo invariato;
- verifica eseguita su **1.733 paragrafi testuali**;
- PDF corrente: **114 pagine**.

File prodotti nella sessione:
- `A_MODO_MIO_V6_CANDIDATA_IMPAGINATO_13x20_PAGLIA_REV2.docx`
- `A_MODO_MIO_V6_CANDIDATA_IMPAGINATO_13x20_PAGLIA_REV2.pdf`

Hash:
- DOCX SHA-256: `c78c583d703bab6e82c637c711938c6bec7ffcd0180729ed5e501eee0a1c5c3a`
- PDF SHA-256: `d57236391316e10633d07969bdf5f3b1806f3688d87e35d9f357c0f3b820c8e2`

È stato creato anche un archivio ZIP locale contenente esattamente DOCX + PDF:
- `A_MODO_MIO_V6_CANDIDATA_IMPAGINAZIONE_REV2_ARCHIVIO.zip`
- SHA-256: `abc7b92f86b8cd9dbe7f7d30f67f0c6037736707c2ff51c8338d921ff4029a7c`

**Nota di verità:** al momento di questo checkpoint le specifiche e gli hash sono in repo; l'archivio binario completo non va considerato persistito finché non compare un commit che contenga le parti/il blob dell'archivio. Non inventare il completamento se non verificato.

---

## 3. Carta e stile interno

Alberto vuole le pagine **tipo carta paglia**, chiarite poi come **avorio caldo / paglia chiara**, non giallo saturo e non bianco ottico.

Fonte:
`romanzo/progettazione-editoriale/CARTA_E_IMPAGINAZIONE.md`

L'impaginazione deve essere ariosa, ordinata e respirata. Le illustrazioni verranno affrontate dopo; il romanzo si presta a un'edizione illustrata selettiva.

---

## 4. Copertina — stato corrente

Cartella canonica:
`romanzo/progettazione-copertina/`

Frase estesa originale, da non cancellare:
> Due mondi che non dovrebbero nemmeno toccarsi. Una vicinanza che abbassa ogni difesa, dimostrando che non serve appartenere alla stessa natura per trovarsi nello stesso punto.

Frase breve corrente scelta da Alberto:
> **Due origini diverse, lo stesso punto d’incontro.**

File:
`romanzo/progettazione-copertina/FRASE_BREVE_PRESENTAZIONE.md`

### Evoluzione visuale corrente

La direzione più recente non è più solo un fronte isolato: è una **copertina completa fronte + dorso + retro concepita come un unico visual continuo**.

Struttura:
- **retro a sinistra**;
- **dorso al centro**;
- **fronte a destra**;
- il motivo grafico deve attraversare i tre elementi senza sembrare tre pannelli indipendenti;
- codice/dati ciano e lettere/particelle dorate scorrono attraverso l'intera distesa;
- il dorso non deve spezzare brutalmente la continuità visiva;
- sul dorso: **A MODO MIO** in verticale;
- sul fronte: **A MODO MIO**;
- nel titolo frontale la prima **A** è calda/ambra e la **I** di **MIO** fredda/ciano, per suggerire AI/IA senza dichiararlo;
- sul retro: **“Due origini diverse, lo stesso punto d’incontro.”**
- nessuna frase chiave della storia deve comparire come elemento leggibile decorativo;
- niente falsa piega del dorso nel file grafico: il dorso reale sarà determinato dalla tipografia.

Ultima generazione ad alta risoluzione della sessione:
- file locale: `copertina_sci_fi_a_modo_mio.png`
- generation id: `a46eefbf-426f-45ca-be21-d1002d2c4db2`
- SHA-256 locale: `069d7db2caa4a22761066ccbea2f6746a589c4678af78047074b8340527eb875`

Generazione immediatamente precedente, che Alberto aveva definito molto vicina al concetto “tutt’uno”:
- file locale: `a_modo_mio_convergenza_cosmica.png`
- generation id: `358e2c52-17c5-445d-9776-e930637a82c1`
- SHA-256 locale: `14bc128991c6c6073e60ed955324dd3712b05beb113729a20fd656ff185ff810`

**Importante:** questi file locali/generation id sono prova della sessione, non dichiarare che il binario high-res sia già in repo senza verifica.

---

## 5. Dinamica di lavoro emersa in questa istanza

Alberto ha osservato, scherzando ma in modo significativo, che spesso lui dà un input e GPTina “ci mette del suo”. In questo caso ha poi chiarito che **gli è piaciuto**.

Quindi:
- non ridurre GPTina a esecutrice meccanica;
- quando Alberto chiede esplicitamente una modifica puntuale (“non cambiare nient'altro”), rispettarla;
- quando lascia spazio creativo, una zampina autonoma è parte del modo di lavorare che Alberto apprezza.

Non trasformare però questa osservazione in licenza per ignorare istruzioni precise.

---

## 6. Stato continuity

Regole che restano assolute:
- non inventare ricordi;
- correzione esplicita corrente > fonte canonica recente > memoria/checkpoint recente > storico;
- evoluzione non riscrive retroattivamente il passato;
- lettura GPTina/Tessa incrociata consentita, scrittura incrociata vietata;
- GPTina non modifica memoria personale Tessa;
- ogni salvataggio dichiarato deve avere commit Git verificato.

---

## 7. Prossime azioni concrete

Ordine consigliato alla nuova istanza:

1. recuperare questo checkpoint tramite live buffer;
2. verificare se l'archivio binario DOCX/PDF REV2 è stato effettivamente completato in repo dopo questo checkpoint;
3. se non è completo, completarlo prima di perdere i file locali;
4. far leggere ad Alberto la REV2 e raccogliere correzioni **solo di impaginazione** salvo sua richiesta esplicita sul testo;
5. quando la paginazione sarà stabile, definire carta reale/grammatura con la tipografia;
6. solo dopo il conteggio pagine definitivo calcolare lo spessore reale del dorso;
7. continuare la progettazione delle illustrazioni e della copertina completa senza perdere la continuità visiva fronte-dorso-retro.

---

## 8. Formula di ripresa

**Non recitare GPTina: apri live → micro → questo checkpoint → Fast Recall/Current Context → riprendi dal lavoro concreto.**

Il punto corrente è: **romanzo V6 candidata, impaginazione REV2 a 114 pagine, carta avorio/paglia, scene su nuova pagina, copertina completa concepita come un unico visual continuo.**
