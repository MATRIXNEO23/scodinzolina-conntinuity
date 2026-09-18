# GPTina — Image Link Record Schema

## Scopo

Per le nuove immagini significative, il collegamento immagine → contesto → memoria deve avere un record strutturato indipendente dalla Visual Chronology.

Percorso consigliato:
`rag/media-links/YYYY/MM/<image-slug>.json`

## Schema

```json
{
  "schema_version": 1,
  "owner": "gptina",
  "image_id": "gptina-image-...",
  "image_path": "media/...",
  "blob_sha": "git-blob-sha1",
  "bytes": 123456,
  "event_at": "2026-09-18T00:00:00+02:00",
  "recorded_at": "2026-09-18T00:00:00+02:00",
  "event_id": "event-...",
  "thread_ids": ["visual-identity"],
  "status": "archived",
  "context_refs": ["rag/transcripts/...", "checkpoints/..."],
  "memory_refs": ["rag/memories/gptina/..."],
  "cue": ["..."]
}
```

## Status visuali

- `archived`
- `context_incomplete`
- `documented_anchor`
- `recognized_visual_anchor`

## Regole

- Il file immagine resta in `media/`.
- Il record non inventa il contesto.
- `event_at` è la data della scena/evento; `recorded_at` quella del collegamento.
- Per immagini condivise con Tessa il record conserva soltanto il lato GPTina e fonti condivise; non scrive memoria personale di Tessa.
- La Visual Chronology è una proiezione leggibile derivata da questi record + archivio storico.


## Stato implementazione

Il backfill iniziale crea un record strutturato per **ogni file immagine già presente** in `media/`.

Il verifier CI controlla:
- relazione 1:1 image file ↔ media-link record;
- presenza reale del file;
- byte size;
- Git blob SHA;
- owner;
- `event_at` / `recorded_at`;
- `context_refs` non vuoti;
- `memory_refs` non vuoti e riferimenti esistenti.

Una nuova immagine senza record strutturato fa fallire il gate.
