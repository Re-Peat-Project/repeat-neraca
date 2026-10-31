# Managed-land targets and canal modes

Written by `scripts/summarise_target_band.py`. Season June to September 2026. Open land and supply are area-weighted over the sub-KHG (`model_units.csv`); runs with canals inside cells count canal cells as open land, so compare modes on the same cells (plain cell means over the open cells of the fixed-cell run). Days out of the season's length.

## Open land and supply

| KHG | grid (m) | canals p/s/t (m) | canal cells | target (m) | managed (km2) | open (km2) | open: mean depth (cm) | open: days > 40 cm | same cells: mean depth (cm) | same cells: days > 40 cm | supply (mm) | canal depth, season median (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 1345 | 2942 | 15 | 5 | 15 | 5 | 40 |  |
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | fixed | 0.6 | 1345 | 2942 | 15 | 5 | 15 | 5 | 16 |  |
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | fixed | 0.8 | 1345 | 2942 | 15 | 5 | 15 | 5 | 8 |  |
| 14.02-04-05.01_kampar_gaung | 200 | 1.2/1.2/1.2 | fixed | 0.4 | 1345 | 2942 | 23 | 24 | 23 | 24 | 42 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.6/0.6/0.6 | fixed | 0.4 | 302 | 1207 | 34 | 51 | 34 | 51 | 181 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.4 | 302 | 1207 | 30 | 41 | 30 | 41 | 172 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.6 | 302 | 1207 | 30 | 41 | 30 | 41 | 124 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.8 | 302 | 1207 | 30 | 41 | 30 | 41 | 92 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 1.2/1.2/1.2 | fixed | 0.4 | 302 | 1207 | 45 | 61 | 45 | 61 | 194 |  |
| 15.05-07-10.01_mendahara_batanghari | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 195 | 925 | 28 | 39 | 28 | 39 | 145 |  |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 2938 | 749 | 37 | 56 | 37 | 56 | 243 |  |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | fixed | 0.6 | 2938 | 749 | 38 | 56 | 38 | 56 | 149 |  |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | fixed | 0.8 | 2938 | 749 | 38 | 56 | 38 | 56 | 103 |  |
| 16.02.01_sugihan_lumpur | 200 | 1.2/1.2/1.2 | fixed | 0.4 | 2938 | 749 | 49 | 68 | 49 | 68 | 244 |  |

## Community stations (the same stations in every run of a KHG and grid)

| KHG | grid (m) | canals p/s/t (m) | canal cells | target (m) | stations | level obs / sim (cm) | drawdown obs / sim (cm) | first week obs / sim (cm) | last week obs / sim (cm) | screened: stations | screened: level obs / sim (cm) | screened: drawdown obs / sim (cm) | stations the run's gate scores |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.6/0.6/0.6 | fixed | 0.4 | 6 | 29 / 66 | 63 / 23 | -19 / 51 | 46 / 74 | 6 | 44 / 70 | 11 / 13 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.4 | 6 | 29 / 44 | 63 / 12 | -19 / 34 | 46 / 47 | 6 | 44 / 47 | 11 / 6 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.6 | 6 | 29 / 45 | 63 / 13 | -19 / 34 | 46 / 49 | 6 | 44 / 48 | 11 / 7 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.8 | 6 | 29 / 45 | 63 / 13 | -19 / 34 | 46 / 51 | 6 | 44 / 48 | 11 / 7 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 1.2/1.2/1.2 | fixed | 0.4 | 6 | 29 / 95 | 63 / 38 | -19 / 72 | 46 / 108 | 6 | 44 / 101 | 11 / 25 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 4 | 29 / 48 | 63 / 32 | -19 / 30 | 44 / 57 | 4 | 44 / 52 | 2 / 21 | 4 |

