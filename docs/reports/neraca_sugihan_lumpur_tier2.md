# Physical neraca air, sugihan_lumpur

Forcing window `calibration`: 2026-04-01 to 2026-10-15, 192 days with forcing; mean P - E -0.19 mm/day (evaporation column `E_era5_mm`). Registry snapshot 124a9b79a170. No parameter is fitted.

KHG 6,348 km2 on a 500 m grid (25,391 cells); DTM valid on 100% of it, peat depth on 77% (gaps filled with the median, 1.2 m). Canal length inside the KHG (km): primary 782, secondary 3,011, tertiary 10,436. Canal classes holding the canal level: primary, secondary. Observed: 51 stations.

## Tier 2: 2D groundwater

Canal drawdown 1.2 m; canal and edge cells fixed (7,588 of 25,391 cells, 30%).

| scale | bias (cm) | RMSE (cm) | r | notes |
|---|---|---|---|---|
| KHG mean of free cells | +21.4 | 55.5 | 0.96 | simulated mean 64.4 cm, observed 43.0 cm |
| stations (cell of each station) | +37.7 | 63.0 | | Spearman across stations: mean level -0.13, peak depth 0.17; observed mean level 43 cm, simulated 81 cm; observed peak depth 39-56 cm |

Per sub-KHG (mean water table depth over the window): min 65, median 65, max 65 cm (28 sub-KHG; table in `neraca_unit_tier2.csv`).

