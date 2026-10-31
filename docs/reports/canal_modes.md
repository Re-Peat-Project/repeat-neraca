# Managed-land targets and canal modes

Written by `scripts/summarise_target_band.py`. Season June to September 2026. Open land and supply are area-weighted over the sub-KHG (`model_units.csv`); runs with canals inside cells count canal cells as open land, so compare modes on the same cells (plain cell means over the open cells of the fixed-cell run). Days out of the season's length.

## Open land and supply

| KHG | grid (m) | canals p/s/t (m) | canal cells | target (m) | managed (km2) | open (km2) | open: mean depth (cm) | open: days > 40 cm | same cells: mean depth (cm) | same cells: days > 40 cm | supply (mm) | canal depth, season median (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 1345 | 2942 | 15 | 5 | 15 | 5 | 40 |  |
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | leak | 0.4 | 1345 | 3836 | 18 | 6 | 15 | 5 | 40 |  |
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | store, tau 0.1 d | 0.4 | 1345 | 3836 | 18 | 12 | 15 | 5 | 40 | 0.30 |
| 14.02-04-05.01_kampar_gaung | 200 | 0.8/0.3/0.3 | store, tau 1 d | 0.4 | 1345 | 3836 | 14 | 3 | 13 | 3 | 40 | 0.17 |
| 14.02-04-05.01_kampar_gaung | 200 | 1.2/1.2/1.2 | fixed | 0.4 | 1345 | 2942 | 23 | 24 | 23 | 24 | 42 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.6/0.6/0.6 | fixed | 0.4 | 302 | 1207 | 34 | 51 | 34 | 51 | 181 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.4 | 302 | 1207 | 30 | 41 | 30 | 41 | 172 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | leak | 0.4 | 302 | 1522 | 32 | 40 | 29 | 41 | 173 |  |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | store, tau 0.1 d | 0.4 | 302 | 1522 | 34 | 49 | 30 | 43 | 177 | 0.48 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | store, tau 1 d | 0.4 | 302 | 1522 | 30 | 42 | 27 | 38 | 174 | 0.41 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 1.2/1.2/1.2 | fixed | 0.4 | 302 | 1207 | 45 | 61 | 45 | 61 | 194 |  |
| 15.05-07-10.01_mendahara_batanghari | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 195 | 925 | 28 | 39 | 28 | 39 | 145 |  |
| 15.05-07-10.01_mendahara_batanghari | 200 | 0.8/0.3/0.3 | leak | 0.4 | 195 | 1477 | 33 | 40 | 27 | 38 | 145 |  |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 2938 | 749 | 37 | 56 | 37 | 56 | 243 |  |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | leak | 0.4 | 2938 | 1369 | 40 | 49 | 37 | 54 | 243 |  |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | store, tau 0.1 d | 0.4 | 2938 | 1369 | 47 | 68 | 38 | 55 | 243 | 0.55 |
| 16.02.01_sugihan_lumpur | 200 | 0.8/0.3/0.3 | store, tau 1 d | 0.4 | 2938 | 1369 | 40 | 57 | 36 | 51 | 243 | 0.42 |
| 16.02.01_sugihan_lumpur | 200 | 1.2/1.2/1.2 | fixed | 0.4 | 2938 | 749 | 49 | 68 | 49 | 68 | 244 |  |

## Community stations (the same stations in every run of a KHG and grid)

| KHG | grid (m) | canals p/s/t (m) | canal cells | target (m) | stations | level obs / sim (cm) | drawdown obs / sim (cm) | first week obs / sim (cm) | last week obs / sim (cm) | screened: stations | screened: level obs / sim (cm) | screened: drawdown obs / sim (cm) | stations the run's gate scores |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.6/0.6/0.6 | fixed | 0.4 | 6 | 29 / 66 | 63 / 23 | -19 / 51 | 46 / 74 | 6 | 44 / 70 | 11 / 13 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | fixed | 0.4 | 6 | 29 / 44 | 63 / 12 | -19 / 34 | 46 / 47 | 6 | 44 / 47 | 11 / 6 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | leak | 0.4 | 6 | 29 / 46 | 63 / 15 | -19 / 34 | 46 / 52 | 6 | 44 / 48 | 11 / 9 | 9 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | store, tau 0.1 d | 0.4 | 6 | 29 / 58 | 63 / 35 | -19 / 35 | 46 / 74 | 6 | 44 / 63 | 11 / 24 | 9 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 0.8/0.3/0.3 | store, tau 1 d | 0.4 | 6 | 29 / 52 | 63 / 35 | -19 / 30 | 46 / 65 | 6 | 44 / 56 | 11 / 24 | 9 |
| 15.05-07-10.01_mendahara_batanghari | 100 | 1.2/1.2/1.2 | fixed | 0.4 | 6 | 29 / 95 | 63 / 38 | -19 / 72 | 46 / 108 | 6 | 44 / 101 | 11 / 25 | 6 |
| 15.05-07-10.01_mendahara_batanghari | 200 | 0.8/0.3/0.3 | fixed | 0.4 | 4 | 29 / 48 | 63 / 32 | -19 / 30 | 44 / 57 | 4 | 44 / 52 | 2 / 21 | 4 |
| 15.05-07-10.01_mendahara_batanghari | 200 | 0.8/0.3/0.3 | leak | 0.4 | 4 | 29 / 49 | 63 / 33 | -19 / 30 | 44 / 58 | 4 | 44 / 54 | 2 / 22 | 9 |

