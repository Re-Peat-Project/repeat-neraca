# Sentinel-1 against the SiTMAT stations (86 stations, 26 scenes each)

Radar: Planetary Computer `sentinel-1-rtc` (gamma0, VV and VH), 2026-04-01 to 2026-10-15, 3 x 3 pixels at 60 m around each station.

## 1. Across stations: does the radar say which stations are deepest?

| feature | rho with observed peak depth | rho with days deeper than 40 cm |
|---|---|---|
| vv_mean_db | 0.38 | 0.11 |
| vh_mean_db | -0.36 | -0.27 |
| vv_minus_vh_db | 0.53 | 0.26 |
| vv_anom_sd_db | -0.24 | -0.06 |
| vv_p90_minus_p10_db | -0.02 | -0.02 |

Strongest |rho|: 0.53. The neraca air gate asks for 0.3. Reached by at least one feature (a screen over several features and two targets; section 3 is the test).

## 2. Within a station: does a wetter scene fall on a shallower day?

Anomalies of VV (against the station's own orbit mean) and of observed depth (against the station mean), same local day: 1483 pairs at 86 stations.
Median within-station Spearman -0.38 (negative = brighter radar on shallower water table, the expected sign), 84% of stations negative, pooled -0.31.

## 3. Out of fold: does the radar predict held-out stations, and does it add to what we already know?

Linear models fitted with whole spatial blocks left out (4 blocks, the same blocks as the neraca air calibration). A model is useful only if its RMSE is below the no-skill line.

Target: observed peak depth (cm)

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 24.6 |  |
| radar ratio (vv_minus_vh_db) | 20.6 | 0.44 |
| radar VV, VH, ratio (vv_minus_vh_db, vv_mean_db, vh_mean_db) | 21.4 | 0.41 |
| known covariates (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m) | 26.7 | -0.0 |
| known covariates + radar ratio (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db) | 28.8 | 0.35 |
| known covariates + radar all (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db, vv_mean_db, vh_mean_db) | 30.9 | 0.33 |

Target: share of days deeper than 40 cm

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 0.335 |  |
| radar ratio (vv_minus_vh_db) | 0.367 | 0.09 |
| radar VV, VH, ratio (vv_minus_vh_db, vv_mean_db, vh_mean_db) | 0.37 | 0.02 |
| known covariates (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m) | 0.324 | 0.24 |
| known covariates + radar ratio (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db) | 0.427 | 0.24 |
| known covariates + radar all (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db, vv_mean_db, vh_mean_db) | 0.449 | 0.21 |

## 4. One orbit at a time

Features from a single relative orbit only, so viewing geometry is the same for every station of that orbit.

| orbit | stations | scenes per station | rho(ratio, peak depth) | rho(ratio, days > 40) | rho(VV, peak depth) |
|---|---|---|---|---|---|
| asc171 | 86 | 16 | 0.52 | 0.26 | 0.36 |
| des18 | 85 | 10 | 0.52 | 0.24 | 0.39 |

## 5. Land cover (ESA WorldCover at the station)

If the radar ratio only tells land cover apart, it will not rank stations that share a class.

| class | stations | median peak depth (cm) | median ratio (dB) | rho(ratio, peak depth) inside the class |
|---|---|---|---|---|
| tree (10) | 64 | 59 | 6.26 | 0.48 |
| grass (30) | 5 | 40 | 6.20 | too few |
| crop (40) | 6 | 44 | 4.13 | too few |

Spearman of the ratio with land cover itself (tree share): 0.32; of peak depth with tree share: 0.2.

Out of fold, peak depth:

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 24.6 |  |
| land cover only (lc_tree, lc_grass, lc_crop) | 25.4 | -0.18 |
| land cover + radar ratio (lc_tree, lc_grass, lc_crop, vv_minus_vh_db) | 21.2 | 0.42 |
| radar ratio (vv_minus_vh_db) | 20.6 | 0.44 |

## 6. Concession (from the SiTMAT station id)

The id of every SiTMAT station starts with its concession code, which stands in for management (weirs, drainage targets); GFW concession polygons were not used (the wood-fibre layer is licensed view-only).

| concession | stations | median peak depth (cm) | median ratio (dB) |
|---|---|---|---|
| 109_THIP | 34 | 81 | 6.85 |
| 17_SPA | 9 | 54 | 4.29 |
| 177_MSK | 9 | 49 | 4.10 |
| 25_AAI | 8 | 43 | 4.04 |
| 03_BNS | 6 | 101 | 7.72 |
| 122_GIN | 6 | 43 | 7.01 |
| 40_RIA | 4 | 42 | 4.36 |
| 107_RSUP | 3 | 30 | 5.85 |
| 45_SPAM | 3 | 47 | 4.01 |
| 92_RSTM | 3 | 40 | 5.77 |
| 53_MKS | 1 | 39 | 4.07 |

Concession explains 64% of the variance of peak depth among the 10 concessions with 3 or more stations (85 stations).
Inside concessions (both variables minus the concession mean): rho(ratio, peak depth) = 0.21; between concession medians (10 concessions): rho = 0.19.

Out of fold with whole concessions left out (a new concession is the hard case), peak depth:

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 28.1 |  |
| radar ratio (vv_minus_vh_db) | 23 | 0.21 |
