# Sentinel-1 against the SiTMAT stations (51 stations, 26 scenes each)

Radar: Planetary Computer `sentinel-1-rtc` (gamma0, VV and VH), 2026-04-01 to 2026-10-15, 3 x 3 pixels at 60 m around each station.

## 1. Across stations: does the radar say which stations are deepest?

| feature | rho with observed peak depth | rho with days deeper than 40 cm |
|---|---|---|
| vv_mean_db | 0.08 | 0.08 |
| vh_mean_db | 0.07 | -0.0 |
| vv_minus_vh_db | -0.02 | 0.1 |
| vv_anom_sd_db | -0.17 | 0.0 |
| vv_p90_minus_p10_db | -0.04 | -0.03 |

Strongest |rho|: 0.17. The neraca air gate asks for 0.3. **Not reached.**

## 2. Within a station: does a wetter scene fall on a shallower day?

Anomalies of VV (against the station's own orbit mean) and of observed depth (against the station mean), same local day: 1325 pairs at 51 stations.
Median within-station Spearman -0.62 (negative = brighter radar on shallower water table, the expected sign), 98% of stations negative, pooled -0.56.

## 3. Out of fold: does the radar predict held-out stations, and does it add to what we already know?

Linear models fitted with whole spatial blocks left out (4 blocks, the same blocks as the neraca air calibration). A model is useful only if its RMSE is below the no-skill line.

Target: observed peak depth (cm)

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 2.99 |  |
| radar ratio (vv_minus_vh_db) | 3 | -0.21 |
| radar VV, VH, ratio (vv_minus_vh_db, vv_mean_db, vh_mean_db) | 3.07 | -0.42 |
| known covariates (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m) | 2.86 | 0.43 |
| known covariates + radar ratio (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db) | 2.92 | 0.42 |
| known covariates + radar all (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db, vv_mean_db, vh_mean_db) | 3.07 | 0.3 |

Target: share of days deeper than 40 cm

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 0.13 |  |
| radar ratio (vv_minus_vh_db) | 0.129 | -0.08 |
| radar VV, VH, ratio (vv_minus_vh_db, vv_mean_db, vh_mean_db) | 0.133 | -0.05 |
| known covariates (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m) | 0.146 | -0.27 |
| known covariates + radar ratio (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db) | 0.141 | -0.14 |
| known covariates + radar all (peat_depth_cm, canal_dist_m, dist_khg_edge_m, elev_m, dist_river_m, vv_minus_vh_db, vv_mean_db, vh_mean_db) | 0.142 | -0.16 |

## 4. One orbit at a time

Features from a single relative orbit only, so viewing geometry is the same for every station of that orbit.

| orbit | stations | scenes per station | rho(ratio, peak depth) | rho(ratio, days > 40) | rho(VV, peak depth) |
|---|---|---|---|---|---|
| asc98 | 51 | 16 | 0.01 | 0.11 | 0.23 |
| des120 | 51 | 10 | -0.11 | 0.05 | -0.22 |

## 5. Land cover (ESA WorldCover at the station)

If the radar ratio only tells land cover apart, it will not rank stations that share a class.

| class | stations | median peak depth (cm) | median ratio (dB) | rho(ratio, peak depth) inside the class |
|---|---|---|---|---|
| tree (10) | 20 | 54 | 4.00 | 0.01 |
| shrub (20) | 1 | 53 | 6.64 | too few |
| grass (30) | 1 | 37 | 4.00 | too few |
| crop (40) | 17 | 54 | 3.95 | 0.21 |

Spearman of the ratio with land cover itself (tree share): 0.03; of peak depth with tree share: 0.1.

Out of fold, peak depth:

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 2.99 |  |
| land cover only (lc_tree, lc_shrub, lc_grass, lc_crop) | 3.04 | -0.36 |
| land cover + radar ratio (lc_tree, lc_shrub, lc_grass, lc_crop, vv_minus_vh_db) | 3.06 | -0.21 |
| radar ratio (vv_minus_vh_db) | 3 | -0.21 |

## 6. Concession (from the SiTMAT station id)

The id of every SiTMAT station starts with its concession code, which stands in for management (weirs, drainage targets); GFW concession polygons were not used (the wood-fibre layer is licensed view-only).

| concession | stations | median peak depth (cm) | median ratio (dB) |
|---|---|---|---|
| 32_BAP | 24 | 55 | 3.97 |
| 33_BMH | 19 | 52 | 4.06 |
| 18_SBA | 8 | 51 | 3.88 |

Concession explains 16% of the variance of peak depth among the 3 concessions with 3 or more stations (51 stations).
Inside concessions (both variables minus the concession mean): rho(ratio, peak depth) = -0.16; between concession medians (3 concessions): rho = None.

Out of fold with whole concessions left out (a new concession is the hard case), peak depth:

| model | out-of-fold RMSE | out-of-fold Spearman |
|---|---|---|
| no skill (training mean) | 3.29 |  |
| radar ratio (vv_minus_vh_db) | 3.31 | -0.59 |
