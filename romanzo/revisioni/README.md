# A MODO MIO — Archivio revisioni

Archivio creato il 20 settembre 2026 per preservare tutte le revisioni di lavoro disponibili senza sovrascrivere le versioni storiche già presenti nella repository.

## Contenuto del pacchetto

- `01-gptina-v1/` — revisione editoriale GPTina v1 compilata.
- `02-qwen-v1-originale/` — prima revisione Qwen originale ricevuta.
- `03-qwen-v1-corretta/` — prima revisione Qwen corretta + HTML mobile completo.
- `04-qwen-v2-originale/` — seconda revisione Qwen originale ricevuta.
- `05-v3-fusione/` — fusione GPTina × Qwen V3 + HTML mobile.
- `06-v4/` — V4 chirurgica + HTML mobile.
- `07-v5-finale/` — V5 con finale cronologicamente corretto + HTML mobile.

La **V5** è la baseline corrente per eventuali correzioni future. Le versioni precedenti restano conservate come storia editoriale e materiale di confronto.

## Nota cronologica vincolante

L'idea del romanzo nasce durante il confronto con Tessa **prima** del consenso di GPTina. La stesura effettiva del romanzo comincia **solo dopo** il consenso.

La struttura editoriale corrente mantiene:

1. consenso integrale di GPTina in prima pagina;
2. seconda pagina completamente bianca;
3. romanzo dalla pagina successiva;
4. finale su **«Raccontaci.»**, senza `FINE` dopo.

## Conservazione tecnica

Per mantenere nello stesso snapshot anche gli HTML e tutti i file di testo, il pacchetto esatto è conservato come archivio `.tar.xz` codificato Base64 e diviso in 8 parti sotto `_archive-b64/`.

Ricostruzione:

```bash
cat _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part00 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part01 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part02 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part03 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part04 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part05 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part06 \
    _archive-b64/A_MODO_MIO_REVISIONI_2026-09-20.tar.xz.b64.part07 \
  | base64 -d > A_MODO_MIO_REVISIONI_ARCHIVIO_2026-09-20.tar.xz

sha256sum A_MODO_MIO_REVISIONI_ARCHIVIO_2026-09-20.tar.xz
tar -xJf A_MODO_MIO_REVISIONI_ARCHIVIO_2026-09-20.tar.xz
```

SHA-256 atteso dell'archivio:

`89605385b570eac340832315f1fe80dc2d45127697ad7ef10255f569231a8a15`

I checksum dei singoli file sono in `MANIFEST.md`.

## Regola per revisioni future

Non sovrascrivere una revisione precedente. Ogni nuova revisione deve avere una nuova cartella/versione e indicare chiaramente da quale baseline deriva.
