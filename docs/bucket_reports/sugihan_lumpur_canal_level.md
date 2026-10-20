# Canal level per concession, KHG 16.02.01

Model: `Sy dz/dt = (E - P) + (zc - z)/gamma` per station, one canal level zc per concession (method and the two ways of leaving stations out in `neracaair/canal_level.py`). `constant`: one level for the whole season. `seasonal`: one level for April-May and one for June-October (the structure of Taufik et al. 2019, who set the canal level by season). Scores are out of fold on the observed water table; the calibration baseline is the mean observed curve of the training stations.

## Constant canal level

51 stations in 3 concessions (3 with 3 or more stations, 51 stations); 2026-04-01 to 2026-10-09. Fitted on all stations: Sy 0.5, gamma 25 days. Canal level per concession (cm): 18_SBA 42, 32_BAP 42, 33_BMH 42.

**Within a concession** (one station left out; the canal level is fitted on the other stations of its concession)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 7.2 | 0.26 |
| mean curve of the other stations of the same concession | 5.5 | 0.40 |
| mean curve of all other stations (the calibration baseline) | 5.6 | n/a |

**New concession** (whole concession left out; canal level = median of the others)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 7.0 | 0.33 |
| mean curve of the stations outside the concession (the calibration baseline) | 5.9 | n/a |

**Ranking stations inside one concession** (Spearman of simulated and observed peak depth; needs 8 or more stations to mean anything)

| concession | stations | rho |
|---|---|---|
| 18_SBA | 8 | 0.01 |
| 32_BAP | 24 | 0.11 |
| 33_BMH | 19 | -0.07 |

## Seasonal canal level

51 stations in 3 concessions (3 with 3 or more stations, 51 stations); 2026-04-01 to 2026-10-09. Fitted on all stations: Sy 0.5, gamma 50 days. Canal level per concession (cm, April-May / June-October): 18_SBA 56 / 32, 32_BAP 52 / 36, 33_BMH 56 / 36.

**Within a concession** (one station left out; the canal level is fitted on the other stations of its concession)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 6.5 | 0.48 |
| mean curve of the other stations of the same concession | 5.5 | 0.40 |
| mean curve of all other stations (the calibration baseline) | 5.6 | n/a |

**New concession** (whole concession left out; canal level = median of the others)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 7.4 | 0.27 |
| mean curve of the stations outside the concession (the calibration baseline) | 5.9 | n/a |

**Ranking stations inside one concession** (Spearman of simulated and observed peak depth; needs 8 or more stations to mean anything)

| concession | stations | rho |
|---|---|---|
| 18_SBA | 8 | 0.01 |
| 32_BAP | 24 | 0.10 |
| 33_BMH | 19 | -0.07 |

