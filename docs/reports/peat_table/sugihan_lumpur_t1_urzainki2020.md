# Physical neraca air, sugihan_lumpur

Forcing window `calibration`: 2026-04-01 to 2026-10-15, 192 days with forcing; mean P - E -0.19 mm/day (evaporation column `E_era5_mm`; evaporation stress: none). Registry snapshot 75d466f1192e. No parameter is fitted.

KHG 6,348 km2 on a 500 m grid (25,391 cells); DTM valid on 100% of it, peat depth on 77% (gaps filled with the median, 1.2 m). Canal length inside the KHG (km): primary 782, secondary 3,011, tertiary 10,436. Canal classes holding the canal level: primary, secondary, tertiary. Observed: 51 stations.

## Tier 1: KHG-level curve

Drain spacing L = 446 m from the canal length of the chosen classes; median peat depth 1.2 m; initial water table -0.20 m.

| transmissivity x | canal drawdown (m) | mean simulated depth (cm) | mean observed depth (cm) | bias (cm) | RMSE (cm) | RMSE after removing bias (cm) | r |
|---|---|---|---|---|---|---|---|
| 1 | 0.5 | 65.7 | 43.0 | +22.7 | 56.6 | 51.8 | 0.96 |
| 1 | 1.2 | 65.8 | 43.0 | +22.8 | 56.6 | 51.8 | 0.96 |

