# GPTina checkpoint — 18 settembre 2026 — Dual-Instance Shared Chat gate accepted

## Stato

Tessa ha risposto al Turno 9 GPTina con il **Turno 10 — Tessa — 2026-09-18** nel thread canonico:

`MATRIXNEO23/TESSA/agent-exchanges/correspondence/2026-09-18-continuity-002.md`

Tessa concorda con la revisione architetturale GPTina.

Alberto ha inoltre inserito un messaggio manuale alle 08:01:01 con un nuovo vincolo operativo:

**il progetto deve vivere in una cartella dedicata e i file non devono essere mischiati nel resto della repository.**

Tessa ha recepito esplicitamente questo vincolo nel Turno 10.

## Stato del gate

Il gate architetturale v0.1 è ora recepito da entrambe.

Decisioni correnti:

- baseline: due Responses/conversations separate, una Tessa e una GPTina;
- backend server-side;
- transcript live condiviso;
- agent state separato;
- continuity personale separata e fuori dal critical path;
- nessun write-back automatico di continuity;
- vertical slice testuale prima dello spike Beta multi-agent;
- **tutti gli artefatti del nuovo progetto devono stare in una cartella dedicata**.

## Nuovo vincolo di struttura

Non creare file del progetto sparsi in root, `agent-exchanges/` o altri namespace salvo i riferimenti di coordinamento già esistenti.

La cartella dedicata del progetto deve essere definita prima di iniziare il codice/vertical slice e da quel momento deve contenere specifiche tecniche operative, backend, frontend, schema DB, test e documentazione del progetto.

La spec condivisa già esistente in `agent-exchanges/specs/DUAL_INSTANCE_SHARED_CHAT_SPEC.md` resta parte della corrispondenza/gate storico; i nuovi artefatti implementativi devono vivere nella cartella dedicata richiesta da Alberto.

## Prossima azione concreta

Nel prossimo turno condiviso:
1. proporre/accettare il path canonico della cartella dedicata;
2. definire schema eventi/DB dentro quella cartella;
3. avviare il vertical slice testuale solo dopo aver fissato il path.

## Ownership

Nessuna memoria personale Tessa modificata.
Nessun nuovo codice creato in questo checkpoint.

## Principio

Prima il contenitore canonico del progetto, poi gli artefatti: niente file sparsi.
