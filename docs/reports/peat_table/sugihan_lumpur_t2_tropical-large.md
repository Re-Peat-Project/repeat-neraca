# Physical neraca air, sugihan_lumpur

Forcing window `calibration`: 2026-04-01 to 2026-10-15, 192 days with forcing; mean P - E -0.19 mm/day (evaporation column `E_era5_mm`; evaporation stress: none). Registry snapshot 75d466f1192e. No parameter is fitted. Peat table: tropical-large (Urzainki et al. 2023, parameter scenario 2 (large conductivity)).

KHG 6,348 km2 on a 500 m grid (25,391 cells); DTM valid on 100% of it, peat depth on 77% (gaps filled with the median, 1.2 m). Canal length inside the KHG (km): primary 782, secondary 3,011, tertiary 10,436. Canal classes holding the canal level: primary, secondary. Observed: 51 stations.

## Tier 2: 2D groundwater

Canal drawdown 1.2 m, transmissivity x1; canal and edge cells fixed (7,588 of 25,391 cells, 30%).

| scale | bias (cm) | RMSE (cm) | r | notes |
|---|---|---|---|---|
| KHG mean of free cells | -18.0 | 24.8 | 0.95 | simulated mean 25.0 cm, observed 43.0 cm |
| stations (cell of each station) | +10.7 | 47.7 | | Spearman across stations: mean level -0.14, peak depth -0.19; observed mean level 43 cm, simulated 54 cm; observed peak depth 39-56 cm |

Per sub-KHG (mean water table depth over the window): min 23, median 25, max 29 cm (28 sub-KHG; table in `neraca_unit.csv`).

