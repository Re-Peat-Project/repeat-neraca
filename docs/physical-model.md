# Physical model and KHG deficit (repeat-neraca)

The physical groundwater model (tiers 1 and 2) is a diagnostic, frozen since 2026-10-26: it explains why observed water tables are held, and it is not used for ranking. The KHG deficit (`deficit.py`) is an output of the adopted method ([neraca-air-method.md](neraca-air-method.md)). Results of the physical model: [neraca-air.md](neraca-air.md). Moved here from the README on 2026-10-26.

## Run it on a real KHG

Set `REPEAT_DATA` (the `_data` folder), `REPEAT_KHG` (the `_khg` work folders) and `SITMAT_PROCESSED`. The real site configs are in the hub, `re-peat/sites/<site>/neraca.yaml`; `config/neraca/example.yaml` is a copy to start from. Besides the paths in the config, the model reads `<inputs_dir>/stations.csv` and `stations_daily.csv` (written by `python -m repeat_neraca.stations --config <site>/neraca.yaml`; needs `SITMAT_PROCESSED`), and rain and evaporation from the ERA5 cache (`forcing_direct`) or `forcing_daily.csv` (written earlier by the retired bucket experiments).

```bash
repeat-neraca-run --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary --k-multiplier 1,10,50,200,1000 --drawdown 0.5,1.2
repeat-neraca-run --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 2 --res 500
```

`--peat-table urzainki2020|tropical-small|tropical-large` chooses the storage and transmissivity of the peat: the default is the boreal-curve table of this repository, the other two are the tropical sets of Urzainki et al. (2023). What the choice does, and why it is not the default yet: [tropical-peat-hydraulic-parameters.md](tropical-peat-hydraulic-parameters.md).

Output goes to `--out` (per-KHG runs: `$REPEAT_KHG/<khg>/03_neraca/runs/<run>/`; default `_out/<name>/`): `neraca_report.md`, `neraca_khg.csv` (the KHG deficit, see below), `tier1_series.csv`, `tier2_series.csv`, `neraca_unit.csv` (with a `neraca_skill_ok` column), `registry_snapshot.json`.

## Methodology

Physical model only (`src/repeat_neraca/`). Nothing is fitted: parameters come from the registry and the data, and the run is compared with the observed water tables afterwards. Results and their reading are in [neraca-air.md](neraca-air.md); this section says what goes in, what is assumed and what each step computes.

Conventions: metres and days. Inside the model the water table depth `z` is **negative below the surface**; reports, `stations_daily.csv` and the output tables give depth in **cm, positive down** (`depth_cm = -100 z`).

### Inputs

Paths are set in the site config (`re-peat/sites/<site>/neraca.yaml`, `${ENV}` expanded, `REPEAT_DATA` and `REPEAT_WORK`). `inputs.load` puts everything on one metric grid: the UTM zone of the KHG centroid, cell size `--res` (registry `neraca_grid_res_m`, 500 m).

| Input (config key) | What | Preprocessing |
|---|---|---|
| KHG boundary (`khg`) | polygon | rasterised to the `domain`; the **edge ring** is the domain minus its 3x3 erosion, the fixed-head cells where a river or the sea sets the level |
| DTM (`dtm`) | land surface, m | averaged onto the grid; gaps filled from the nearest valid cell. Share of valid cells is reported |
| Peat depth (`peat_depth`) | m (`scale` converts, 0.01 for cm) | averaged onto the grid; gaps and non-positive values filled with the in-domain median (reported) |
| Canals (`canals`) | lines with a class field | split into primary, secondary and tertiary by `class_field` and `classes`; rasterised with `all_touched`, edge ring excluded; length per class is measured inside the KHG, in km |
| Sub-KHG units (`units`, optional) | polygons with `unit_id` | rasterised, for the per-sub-KHG summary |
| Stations (`<inputs_dir>/stations.csv`) | SiTMAT: `station_id, lon, lat, concession` | each station is assigned its grid cell; those outside the grid are dropped |
| Observed depth (`<inputs_dir>/stations_daily.csv`) | `date, station_id, depth_cm` | pivoted to dates x stations |
| Rain and evaporation (`forcing_direct`, or `forcing_daily.csv`) | KHG-mean daily `P_era5_mm`, `E_era5_mm`, `E_wapor_mm`, local days (`tz_hours`, 7 = WIB) | ERA5 hourly (0.25 degree) accumulated to local days; WaPOR (about 300 m) where it was read, empty otherwise. One series per KHG, no spatial forcing |

The station files are written by `python -m repeat_neraca.stations`; the daily forcing comes from the ERA5 cache through `repeat-common` (`forcing_direct`) or from the existing `forcing_daily.csv`. Evaporation used by tier 1 and 2 is the config key `evaporation` (`E_era5_mm` or `E_wapor_mm`). A day with no forcing keeps the state and gives no output.

### Parameters

The registry `src/repeat_neraca/parameters.yaml` (read by `params.Registry`; `python scripts/registry_table.py` prints it as a table) holds many parameters for the wider RE-PEAT work. The physical model reads only these:

| Registry key | Default | Used for |
|---|---|---|
| `canal_drawdown` | 1.2 m | canal level = local surface minus this; the one management-dependent unknown, run as a sensitivity (`--drawdown`) |
| `river_stage_below_edge` | 0.3 m | head of the edge ring below the local surface (tier 2) |
| `initial_wtd` | -0.20 m | starting water table, both tiers |
| `neraca_grid_res_m` | 500 m | tier 2 grid (`--res`) |
| `et_stress_start`, `et_stress_end` | -1.54 m, -2.85 m | evaporation stress thresholds (drained peat, Apers et al. 2022) |

`k_forest`, `k_drained`, `sy_surface`, `sy_at_1p5m` and the rest of the registry are **not wired into the solvers yet**; Sy and T come from the peat table below.

Constants in the code, not in the registry:

| Constant | Value | Where |
|---|---|---|
| spin-up skipped when scoring | 14 days | `validate.SKIP` |
| minimum Spearman for `neraca_skill_ok` | 0.3 | `validate.MIN_SPATIAL_SKILL` |
| natural-peat ET thresholds (`--et-stress natural`) | -0.70 m, -1.82 m | `scripts/run_neraca.py` |
| tier 1 sub-step limit (rate C/Sy per sub-step) | 0.5 | `lumped.simulate_rain_et` |
| tier 2 Picard iterations, tolerance | 10, 1e-5 m | `groundwater.solve` |
| floors on Sy and T | 0.02, 1e-6 m2/day | `PeatTable` |
| deficit window, Sy, band, edge days, minimum station coverage, WaPOR bound | 1 June to 31 Oct, 0.15, 0.10-0.20, 7, 0.5, off | `deficit.DEFAULTS` (overridable in a `deficit:` block of the config) |

### Peat storage and transmissivity

Both tiers take the specific yield `Sy(z)` and transmissivity `T(z)` from a `PeatTable` (`--peat-table`):

- `urzainki2020` (default): a table of profile storage and transmissivity against water table depth (`groundwater/data/`). `Sy = d storage / dz`, floored at 0.02. `T(z) = tra(z) - tra(-d)` for peat depth `d`, times `--k-multiplier`, floored at 1e-6. The table was built from boreal Paivanen (1973) retention curves, so it is a placeholder for tropical peat; T is about 0.5 m2/day at the surface and near zero by 0.6 m depth.
- `tropical-small`, `tropical-large`: `Sy = s1 exp(s2 z)`, `T = t1 (exp(t2 z) - exp(-t2 d))` with (s1, s2, t1, t2) = (0.6, 0.5, 50 or 500, 2.5), Urzainki et al. (2023), site-calibrated for Merang-Kepayang. See [tropical-peat-hydraulic-parameters.md](tropical-peat-hydraulic-parameters.md).

### Tier 1: KHG-level water table (`lumped.py`)

One water table for the whole KHG:

```
Sy(z) dz/dt = R - C(z) (z - z_c)        C(z) = 12 T(z) / L^2        R = P - ET x f(z)        z_c = -canal_drawdown
```

- `L = KHG area / canal length` of the classes in `--classes` (default `primary,secondary`; the examples above add `tertiary`). `12 T / L^2` is the exchange of a strip of width `L` between two drains under uniform recharge, tested against the 2D solver.
- `T` is evaluated at the **median peat depth** of the KHG.
- `f(z)` is the evaporation factor (`--et-stress none|drained|natural`): 1 above `et_stress_start`, 0 below `et_stress_end`, linear between. `none` is the default.
- Explicit Euler per day, split into `ceil((C/Sy) / 0.5)` sub-steps to stay stable; `z` is capped at 0 (ponded water leaves).
- Run for every `--drawdown` and `--k-multiplier` given.

### Tier 2: 2D groundwater (`spatial.py`, `groundwater/solver.py`)

```
Sy(z) dh/dt = div( T(z) grad h ) + R         z = h - surface
```

Nonlinear Boussinesq equation on the grid, implicit Euler (one step per day), Picard iteration for the nonlinearity, arithmetic-mean transmissivity on cell faces, sparse direct solve. Ponded water is removed each step. Cells outside the KHG are no-flow.

- Fixed heads: the edge ring at `surface - river_stage_below_edge`, and the cells of the canal classes in `--classes` at `surface - canal_drawdown`.
- Recharge `R = P - ET x f(z)`: one KHG series for every cell, `f` applied cell by cell.
- Only the **first** `--drawdown` and **first** `--k-multiplier` are run.
- Output: KHG-mean over free cells (not canal, not edge), the value in each station's cell, and the mean per sub-KHG.

### Validation (`validate.py`)

The first 14 days are spin-up and are not scored.

- KHG level: simulated KHG-mean curve against the mean of all stations. Bias, RMSE, RMSE after removing the bias, and Pearson r.
- Station level (tier 2): pooled bias and RMSE over station-days, Spearman across stations of the mean level and of the 95th-percentile depth (the dry-season peak).
- `neraca_skill_ok` in `neraca_unit.csv` is one value for all sub-KHG: 1 if the Spearman of the peak depth across stations is at least 0.3, otherwise 0 (also 0 when it cannot be computed).

### KHG deficit (`deficit.py`; method in [neraca-air-method.md](neraca-air-method.md), section 4B)

The water the managed system has to supply to hold the water table, as a mass balance. It does not use the tiers:

```
deficit_mm = max(0, -sum(P - E) - Sy x dz_obs x 10)        deficit_m3 = deficit_mm / 1000 x KHG area
```

- Window: 1 June (year of the first forcing date) to the last day with both P and E, at most 31 October. `P - E` is summed over days with forcing.
- `dz_obs`: change of the station-mean depth (cm, positive = deeper), last 7 days of the window minus first 7. Stations with data on fewer than 50% of the window days are dropped.
- `Sy` = 0.15; the band `deficit_mm_low`, `deficit_mm_high` is the smallest and largest deficit over Sy 0.10, 0.15, 0.20. WaPOR evaporation enters the band only with `wapor_bound: true` in a `deficit:` block and if it covers every day of the window (`e_wapor_covers_period`); it is off by default (decision 3 of the method report).
- The central value always uses `P_era5_mm` and `E_era5_mm`; it ignores the config key `evaporation`.
- `deficit_months`: calendar months of the window with negative `P - E` (a partial last month counts).

### Output tables

| File | Content |
|---|---|
| `neraca_khg.csv` | one row per KHG (every run): window, `n_days`, `valid_day_share`, `n_stations`, `area_km2`, `sy`, `net_balance_mm` (sum of P - E), `obs_depth_start_cm`, `obs_depth_end_cm`, `obs_change_cm`, `storage_change_mm` (`sy x dz x 10`), `deficit_mm` with `_low`, `_high`, `deficit_m3`, `deficit_months`, `evaporation_source`, `e_wapor_covers_period`, `method` |
| `tier1_series.csv` | daily simulated depth (cm) per transmissivity multiplier and drawdown, and the observed station mean |
| `tier2_series.csv` | daily KHG-mean depth (cm), share of free cells deeper than 40 cm, depth in each station's cell |
| `neraca_unit.csv` (tier 2, with `units`) | per sub-KHG: `u_wt_mean_cm`, `u_wt_peak_cm` (95th percentile of depth, cm), `u_wt_days_gt40` (**share** of days, 0 to 1, with depth over 40 cm), `neraca_skill_ok` |
| `neraca_report.md`, `registry_snapshot.json` | run report with the metrics above; the registry values used, with a hash |

