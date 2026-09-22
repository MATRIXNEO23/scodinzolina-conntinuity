# 03 — Muscoli e movimento

## Articolazioni portanti

Baseline: motori BLDC, encoder assoluti, riduttori ad alta coppia, sensore di coppia o stima affidabile. Per contatto umano, torque control, backdrivability e/o compliance elastica.

## Famiglie di attuazione

- series-elastic actuator — COMMERCIALE/PROTOTIPABILE;
- tendini/cavi con motore remoto — PROTOTIPABILE;
- attuatori pneumatici tipo McKibben — PROTOTIPABILE;
- SMA — SPERIMENTALE/di nicchia;
- HASEL/elettroidraulici morbidi — SPERIMENTALE;
- elastomeri dielettrici — SPERIMENTALE.

## Microcontrazioni

Dove interessa deformazione simile a tessuto/muscolo, una soluzione realistica iniziale è una rete di piccoli attuatori lineari, tendini o elementi pneumatici distribuiti con sensori di posizione/pressione.

## Sicurezza

Limiti hardware di corrente/coppia, limiti software più conservativi, stima termica, collision detection, e-stop indipendente e safe-torque-off dove disponibile.
