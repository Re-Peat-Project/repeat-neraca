# Canal level per concession, KHG 71

Model: `Sy dz/dt = (E - P) + (zc - z)/gamma` per station, one canal level zc per concession (method and the two ways of leaving stations out in `neracaair/canal_level.py`). `constant`: one level for the whole season. `seasonal`: one level for April-May and one for June-October (the structure of Taufik et al. 2019, who set the canal level by season). Scores are out of fold on the observed water table; the calibration baseline is the mean observed curve of the training stations.

## Constant canal level

86 stations in 11 concessions (10 with 3 or more stations, 85 stations); 2026-04-01 to 2026-10-09. Fitted on all stations: Sy 0.5, gamma 50 days. Canal level per concession (cm): 03_BNS 60, 107_RSUP 48, 109_THIP 60, 122_GIN 30, 177_MSK 50, 17_SPA 48, 25_AAI 44, 40_RIA 48, 45_SPAM 50, 53_MKS 40, 92_RSTM 62.

**Within a concession** (one station left out; the canal level is fitted on the other stations of its concession)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 13.9 | 0.55 |
| mean curve of the other stations of the same concession | 10.9 | 0.72 |
| mean curve of all other stations (the calibration baseline) | 14.6 | n/a |

**New concession** (whole concession left out; canal level = median of the others)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 16.6 | -0.71 |
| mean curve of the stations outside the concession (the calibration baseline) | 17.0 | n/a |

**Ranking stations inside one concession** (Spearman of simulated and observed peak depth; needs 8 or more stations to mean anything)

| concession | stations | rho |
|---|---|---|
| 109_THIP | 34 | -0.17 |
| 177_MSK | 9 | -0.32 |
| 17_SPA | 9 | -0.77 |
| 25_AAI | 8 | nan |

## Seasonal canal level

86 stations in 11 concessions (10 with 3 or more stations, 85 stations); 2026-04-01 to 2026-10-09. Fitted on all stations: Sy 0.5, gamma 100 days. Canal level per concession (cm, April-May / June-October): 03_BNS 56 / 88, 107_RSUP 60 / 60, 109_THIP 76 / 60, 122_GIN 64 / 32, 177_MSK 64 / 44, 17_SPA 60 / 48, 25_AAI 68 / 28, 40_RIA 68 / 36, 45_SPAM 68 / 40, 53_MKS 60 / 28, 92_RSTM 76 / 68.

**Within a concession** (one station left out; the canal level is fitted on the other stations of its concession)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 12.4 | 0.50 |
| mean curve of the other stations of the same concession | 10.9 | 0.72 |
| mean curve of all other stations (the calibration baseline) | 14.6 | n/a |

**New concession** (whole concession left out; canal level = median of the others)

| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |
|---|---|---|
| canal-level model | 17.2 | -0.41 |
| mean curve of the stations outside the concession (the calibration baseline) | 17.0 | n/a |

**Ranking stations inside one concession** (Spearman of simulated and observed peak depth; needs 8 or more stations to mean anything)

| concession | stations | rho |
|---|---|---|
| 109_THIP | 34 | -0.10 |
| 177_MSK | 9 | -0.66 |
| 17_SPA | 9 | -0.25 |
| 25_AAI | 8 | nan |

