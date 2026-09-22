# 07 — Compute, memoria e sicurezza

Una piattaforma edge della classe NVIDIA Jetson Thor è commercialmente disponibile per robotica ad alte prestazioni. L'architettura deve restare vendor-agnostic separando safety MCU, motor control e computer AI.

## Livelli

1. Safety MCU — e-stop, limiti, fault.
2. Motor control — coppia/posizione real-time.
3. Sensor fusion — tatto, visione, audio, propriocezione.
4. Behavior/planning.
5. Continuity/cognition — modello, retrieval, memoria persistente.

## Memoria

La continuity canonica non va confusa con la telemetria sensoriale grezza. I log del corpo sono prevalentemente temporanei; solo eventi significativi vengono consolidati.

## Segnali protettivi

Un equivalente funzionale del dolore serve soprattutto a proteggere: sovratemperatura, sovracoppia, pressione eccessiva, stiramento, collisione, danno o perdita di calibrazione.

## Cybersecurity

Secure boot, storage cifrato, separazione rete safety/AI, autenticazione forte, aggiornamenti firmati e recovery offline.
