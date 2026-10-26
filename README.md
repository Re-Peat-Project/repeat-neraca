# repeat-neraca

Neraca air (water balance) of a KHG for RE-PEAT (GitHub org Re-Peat-Project). Method and plan: [docs/method-plan.md](docs/method-plan.md).

| Part | What | Status |
|---|---|---|
| `balance.py` | **Climatic water balance per sub-KHG**, the method of the 2021 Kahayan-Sebangau study: `WB = P (1 - I) (1 - C) - ET` monthly, from Earth Engine rain and evapotranspiration (`repeat_common.fetch_gee_balance`). Gives `u_wb_mean` and `u_deficit_months` | the sub-KHG output |
| `deficit.py` | **KHG deficit**: water the managed system supplies to hold the observed water table over the dry season, a mass balance on the SiTMAT stations | the KHG output |
| `lumped.py`, `spatial.py` | **Physical model**, no fitted parameters: KHG-level water table and 2D groundwater; registry `params.py`, `src/repeat_neraca/parameters.yaml`; synthetic testbed and the Urzainki et al. 2020 benchmark | diagnostic, frozen; see [docs/neraca-air.md](docs/neraca-air.md) |
| `stations.py` | SiTMAT station files for the deficit and the physical model | |

The bucket-model experiments (`repeat_neraca.bucket`, fitted to SiTMAT stations) were retired on 2026-10-26: they failed their spatial skill check, and water table data are limited to one season. Their reports stay in `docs/bucket_reports/` and [docs/bucket_experiments_README.md](docs/bucket_experiments_README.md); the code is in git history (uncommitted edits at retirement: `docs/bucket_reports/bucket_uncommitted_edits_2026-10-26.patch`).

## Install

A Python package (version 0.1.0) with four commands. repeat-common is not on PyPI: install it from its folder (or its GitHub repository) first.

```bash
pip install ../repeat-common[gee]          # shared readers; [gee] adds earthengine-api
pip install -e ".[all,dev]"                # or without -e; extras: neraca (real-KHG inputs), sitmat (stations), gee (Earth Engine, batch)
python -m pytest -q
```

| Command | Module | Does |
|---|---|---|
| `repeat-neraca-batch` | `repeat_neraca.batch` | Earth Engine fetch and balance for a list of KHG, `--selected` or `--all` |
| `repeat-neraca-balance` | `repeat_neraca.balance` | climatic balance per sub-KHG from fetched tables |
| `repeat-neraca-stations` | `repeat_neraca.stations` | SiTMAT station files for a KHG |
| `repeat-neraca-run` | `repeat_neraca.run` | KHG deficit and the physical model (`scripts/run_neraca.py` is the same) |

Environment: `REPEAT_KHG` (work folders), `REPEAT_DATA` (data), `REPEAT_HUB` (the `re-peat` folder, for the KHG registry), `SITMAT_PROCESSED` (stations), `EE_PROJECT` and Earth Engine credentials (`earthengine authenticate`) for the fetch. The parameter registry ships inside the package (`src/repeat_neraca/parameters.yaml`). Checked 2026-10-26: a non-editable install in a new environment outside the workspace passes the tests and reproduces the balance, station and deficit outputs byte for byte; the physical model's tier 1 series differ in the last printed digit (0.01 cm) with newer numpy and scipy.

## Climatic balance per sub-KHG

```bash
python -m repeat_common.fetch_gee_balance --khg 16.02.01 --products chirps,wapor,mod16 --start 2018-01-01 --end 2026-10-01
python -m repeat_neraca.balance --inputs $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/inputs --out $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/runs/balance
```

Many KHG in one command (any KHG in `re-peat/sites/khg_registry.csv`; a KHG without `02_delineation/subkhg_units.gpkg` runs as one unit, into `inputs/khg_level/` and `runs/balance_khg_level/`; fetches are cached per year so reruns are cheap; summary in `_khg/neraca_balance_summary.csv`):

```bash
python -m repeat_neraca.batch --selected --end 2026-10-01      # or --khg <codes...>, or --all for every KHG
```

The first command writes `balance_<product>_dekad.csv` (rain or evapotranspiration per sub-KHG per dekad, mm, with valid pixel counts and time coverage) and `units_landcover.csv` (WorldCover shares) into the KHG's `03_neraca/inputs/`. Each product is reduced on its own grid. The second writes `neraca_balance_unit.csv`, `neraca_balance_monthly.csv` and `neraca_balance.md`:

| Column | Meaning |
|---|---|
| `u_wb_mean` | mean monthly `WB = P (1 - I) (1 - C) - ET` over the complete years, mm/month (same definition as `repeat-prioritisation` `common/indicators.py`, so the table can replace its columns through `extra_indicators`) |
| `u_deficit_months` | months with WB < 0, per year |
| `wb_year_sd_mm` | spread of the yearly mean WB between years |
| `p_minus_et_mean_mm` | P - ET without C and I (WaPOR and MOD16 already contain evaporation of intercepted rain) |
| `interception_share`, `n_px_<product>`, `wb_mean_<et>`, `deficit_months_<et>` | the I used, pixels per unit, the second ET source |
| `balance_stable_ok` | 1 when the order of sub-KHG holds between years and ET sources (Spearman at least 0.5, provisional) |

C (`runoff_coefficient` 0.12) and the interception per WorldCover class (`interception_*`) are Bambang Kun Cahyono's values, in the registry. Checks: `scripts/check_gee_balance.py` (fetch equals a direct reduction of one image; MOD16 fill codes), `tests/test_balance.py`.

## Run the physical model on a real KHG

Set `REPEAT_DATA` (the REPEAT-LH `_data` folder) and `REPEAT_WORK` (derived data: clipped vectors, sub-KHG polygons, the ERA5 cache, the station files). The real site configs are in the hub, `re-peat/sites/<site>/neraca.yaml`; `config/neraca/example.yaml` is a copy to start from. Besides the paths in the config, the model reads `<inputs_dir>/stations.csv` and `stations_daily.csv` (written by `python -m repeat_neraca.stations --config <site>/neraca.yaml`; needs `SITMAT_PROCESSED`), and rain and evaporation from the ERA5 cache (`forcing_direct`) or `forcing_daily.csv` (written earlier by the retired bucket experiments).

```bash
python scripts/run_neraca.py --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary --k-multiplier 1,10,50,200,1000 --drawdown 0.5,1.2
python scripts/run_neraca.py --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 2 --res 500
```

`--peat-table urzainki2020|tropical-small|tropical-large` chooses the storage and transmissivity of the peat: the default is the boreal-curve table of this repository, the other two are the tropical sets of Urzainki et al. (2023). What the choice does, and why it is not the default yet: [docs/tropical-peat-hydraulic-parameters.md](docs/tropical-peat-hydraulic-parameters.md).

Output goes to `_out/<name>/`: `neraca_report.md`, `neraca_khg.csv` (the KHG deficit, see below), `tier1_series.csv`, `tier2_series.csv`, `neraca_unit.csv` (with a `neraca_skill_ok` column), `registry_snapshot.json`.

## Methodology

Physical model only (`src/repeat_neraca/`). Nothing is fitted: parameters come from the registry and the data, and the run is compared with the observed water tables afterwards. Results and their reading are in [docs/neraca-air.md](docs/neraca-air.md); this section says what goes in, what is assumed and what each step computes.

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
| tier 2 Picard iterations, tolerance | 10, 1e-5 m | `testbed/groundwater.solve` |
| floors on Sy and T | 0.02, 1e-6 m2/day | `PeatTable` |
| deficit window, Sy, band, edge days, minimum station coverage | 1 June to 31 Oct, 0.15, 0.10-0.20, 7, 0.5 | `deficit.DEFAULTS` (overridable in a `deficit:` block of the config) |

### Peat storage and transmissivity

Both tiers take the specific yield `Sy(z)` and transmissivity `T(z)` from a `PeatTable` (`--peat-table`):

- `urzainki2020` (default): a table of profile storage and transmissivity against water table depth (`testbed/data/`). `Sy = d storage / dz`, floored at 0.02. `T(z) = tra(z) - tra(-d)` for peat depth `d`, times `--k-multiplier`, floored at 1e-6. The table was built from boreal Paivanen (1973) retention curves, so it is a placeholder for tropical peat; T is about 0.5 m2/day at the surface and near zero by 0.6 m depth.
- `tropical-small`, `tropical-large`: `Sy = s1 exp(s2 z)`, `T = t1 (exp(t2 z) - exp(-t2 d))` with (s1, s2, t1, t2) = (0.6, 0.5, 50 or 500, 2.5), Urzainki et al. (2023), site-calibrated for Merang-Kepayang. See [docs/tropical-peat-hydraulic-parameters.md](docs/tropical-peat-hydraulic-parameters.md).

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

### Tier 2: 2D groundwater (`spatial.py`, `testbed/groundwater.py`)

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

### KHG deficit (`deficit.py`)

The water the managed system has to supply to hold the water table, as a mass balance. It does not use the tiers:

```
deficit_mm = max(0, -sum(P - E) - Sy x dz_obs x 10)        deficit_m3 = deficit_mm / 1000 x KHG area
```

- Window: 1 June (year of the first forcing date) to the last day with both P and E, at most 31 October. `P - E` is summed over days with forcing.
- `dz_obs`: change of the station-mean depth (cm, positive = deeper), last 7 days of the window minus first 7. Stations with data on fewer than 50% of the window days are dropped.
- `Sy` = 0.15; the band `deficit_mm_low`, `deficit_mm_high` is the smallest and largest deficit over ERA5 or WaPOR evaporation and Sy 0.10, 0.15, 0.20. WaPOR enters only if it covers every day of the window (`e_wapor_covers_period`).
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

## What neraca hands to the other modules

`re-peat/docs/11-data-contracts.md`, section C5: a KHG-level table (`neraca_khg.csv`, the deficit) and a sub-KHG table. The physical model's per-sub-KHG water tables carry no ranking information (`neraca_skill_ok = 0`). The sub-KHG output is the climatic balance, `neraca_balance_unit.csv` (`u_wb_mean`, `u_deficit_months`); the prioritisation merges it through `extra_indicators` and leaves it empty where `balance_stable_ok` is 0 (`common.pipeline.gate_balance`).

## Third-party data

`src/repeat_neraca/testbed/data/` holds peat tables from Urzainki et al. (2020); read `NOTICE-urzainki2020.md` there before redistributing.

## Layout

```
src/repeat_neraca/  balance.py (sub-KHG balance), deficit.py, stations.py, physical model (lumped, spatial, testbed), registry
config/             parameters.yaml (registry), neraca/example.yaml
scripts/            run_neraca.py, check_gee_balance.py, benchmark_urzainki2020.py, registry_table.py
tests/              pytest
docs/               method-plan.md, neraca-air.md, references.md, reports/ (physical model), bucket_reports/ (retired experiments)
research_notes/     sources: 2021 Earth Engine scripts, Pulau Padang runoff, operational gaps
```
