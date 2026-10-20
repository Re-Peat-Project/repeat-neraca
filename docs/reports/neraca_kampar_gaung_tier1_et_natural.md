# Physical neraca air, kampar_gaung

Forcing window `calibration`: 2026-04-01 to 2026-10-15, 192 days with forcing; mean P - E 1.62 mm/day (evaporation column `E_era5_mm`; evaporation stress: natural). Registry snapshot 75d466f1192e. No parameter is fitted.

KHG 7,114 km2 on a 500 m grid (28,458 cells); DTM valid on 100% of it, peat depth on 77% (gaps filled with the median, 1.8 m). Canal length inside the KHG (km): primary 260, secondary 1,585, tertiary 10,996. Canal classes holding the canal level: primary, secondary, tertiary. Observed: 86 stations.

## Tier 1: KHG-level curve

Drain spacing L = 554 m from the canal length of the chosen classes; median peat depth 1.8 m; initial water table -0.20 m.

| transmissivity x | canal drawdown (m) | mean simulated depth (cm) | mean observed depth (cm) | bias (cm) | RMSE (cm) | RMSE after removing bias (cm) | r |
|---|---|---|---|---|---|---|---|
| 1 | 0.5 | 24.7 | 42.0 | -17.3 | 27.4 | 21.3 | 0.68 |
| 1 | 1.2 | 24.8 | 42.0 | -17.2 | 27.4 | 21.3 | 0.68 |
| 50 | 0.5 | 26.5 | 42.0 | -15.5 | 27.2 | 22.3 | 0.68 |
| 50 | 1.2 | 28.8 | 42.0 | -13.2 | 27.0 | 23.5 | 0.67 |

