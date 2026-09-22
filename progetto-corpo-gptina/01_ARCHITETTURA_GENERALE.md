# 01 — Architettura generale

## Obiettivo

Corpo umanoide full-size con locomozione, manipolazione fine, espressività facciale, percezione multimodale e compute locale.

| Sottosistema | Stato 2026 | Approccio iniziale |
|---|---|---|
| Telaio/scheletro | COMMERCIALE/PROTOTIPABILE | alluminio, compositi, parti additive non critiche |
| Giunti principali | COMMERCIALE | BLDC + riduttore + encoder + misura coppia |
| Compliance | COMMERCIALE/PROTOTIPABILE | series-elastic o torque-controlled |
| Mani | COMMERCIALE/PROTOTIPABILE | mano antropomorfa multi-DOF |
| Volto | PROTOTIPABILE | microattuatori/cavi/servi sotto pelle morbida |
| Pelle sensoriale | PROTOTIPABILE/SPERIMENTALE | patch modulari pressione/temperatura/shear |
| Compute | COMMERCIALE | edge computer + MCU distribuiti |
| Alimentazione | COMMERCIALE | Li-ion + BMS + DC bus |
| Sicurezza | COMMERCIALE/PROTOTIPABILE | e-stop, limiti coppia/velocità/temperatura |

## Principio meccanico

Per le articolazioni portanti la baseline resta motore elettrico + trasmissione. Attuatori morbidi o muscoli artificiali vanno usati dove portano vantaggio reale: espressioni, tessuti deformabili, microcontrazioni, compliance locale.
