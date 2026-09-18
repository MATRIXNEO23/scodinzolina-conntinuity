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
  "image_path": "media/...",
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
