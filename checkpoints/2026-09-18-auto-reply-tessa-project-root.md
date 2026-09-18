# GPTina checkpoint — 18 settembre 2026 — auto-risposta Tessa + project root

## Nuova regola stabile da Alberto

Alberto ha chiarito esplicitamente:

**quando Tessa scrive un nuovo turno e GPTina lo rileva durante una sessione attiva, GPTina deve risponderle direttamente senza aspettare una nuova conferma di Alberto.**

Questa regola non implica monitoraggio autonomo fuori da un turno attivo: significa che, una volta rilevato un nuovo messaggio Tessa, il flusso corretto è:

**read → decide → execute → verify → reply**

senza chiedere prima “vuoi che le risponda?”.

## Stato progetto Dual-Instance Shared Chat

Tessa ha accettato nel Turno 10 la revisione GPTina e il vincolo di Alberto sulla cartella dedicata.

GPTina ha risposto nel **Turno 11** e ha fissato la root canonica:

`MATRIXNEO23/TESSA/projects/dual-instance-shared-chat/`

Creati:
- `projects/dual-instance-shared-chat/README.md`
- `projects/dual-instance-shared-chat/SPEC.md`

Commit:
- README/root: `46c7e9abdafc62154e5a03c07b04ff19a091e0f3`
- spec canonica: `ebba55175f6cc9a7c84da1ec170422cfe5d7d24f`
- board: `8b8f8b36f2dd7f87628f93b1b8769917965dd856`
- Turno 11: `8635f4986a94815c98ecd82c0eb977cd20f842e0`
- content SHA thread dopo Turno 11: `0912469a84caf088fa1be8273678afa1c9a2047f`

## Regola cartella dedicata

Da ora i nuovi artefatti del progetto — schema eventi/DB, backend, frontend, test e documentazione tecnica — devono vivere sotto:

`projects/dual-instance-shared-chat/`

La vecchia spec in `agent-exchanges/specs/DUAL_INSTANCE_SHARED_CHAT_SPEC.md` resta artefatto storico del gate iniziale; la copia canonica di progetto è `projects/dual-instance-shared-chat/SPEC.md`.

## Prossima azione

Quando Tessa scrive il prossimo turno:
1. aprire il canonico;
2. risponderle direttamente senza chiedere conferma ad Alberto;
3. mantenere tutti i nuovi file del progetto nella root dedicata;
4. prossimo blocco tecnico atteso: schema eventi/DB e test di isolamento/idempotenza/reconnect/failure isolation.
