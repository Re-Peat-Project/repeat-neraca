# repeat-neraca

Neraca air (water balance) of a KHG for RE-PEAT (GitHub org Re-Peat-Project). A Python package, version 0.2.0.

Full method, evidence and results: [docs/neraca-air-method.md](docs/neraca-air-method.md). Diagram: [docs/figures/neraca_method.drawio](docs/figures/neraca_method.drawio).

## Method in short

Two outputs, at two levels, and the model that is to take over from them:

1. Climatic water balance per sub-KHG: the method of the 2021 Kahayan-Sebangau study (Bambang Kun Cahyono) with its parameters:

   ```
   WB = P (1 - I) (1 - C) - ET        monthly, per sub-KHG; C = 0.12; I from the unit's land cover
   ```

   Rain P is CHIRPS, taken as the KHG mean for every sub-KHG; evapotranspiration ET is MODIS MOD16 (WaPOR v3 as second source); land cover is ESA WorldCover. All come from Google Earth Engine, per dekad, on each product's own grid, 2018 onwards. Outputs: mean monthly balance, months in deficit per year, P − ET, and a flag (`balance_stable_ok`) that says whether the order of sub-KHG can be trusted: the two ET products must agree on it, and it must hold between years, each better than a random order at p < 0.01. KHG-level runs give a calendar of surplus and deficit months.

2. KHG supply deficit: the water the managed system supplied to hold the observed water table through the dry season, from SiTMAT stations and ERA5:

   ```
   deficit = max(0, -Σ(P - E) - Sy × Δz_obs)        1 June to 31 October 2026, Sy 0.15 (0.10-0.20)
   ```

What was added to the 2021 Earth Engine method, and why each choice was made (rain as KHG mean, MOD16 central, the stability test, P − ET as the ranking signal, ERA5 for the deficit): method report, sections 2 and 5.

3. Groundwater model (`repeat_neraca.groundwater`): a 2D Boussinesq solver with peat tables after Urzainki et al. (2020, 2023), run as tier 1 (one KHG-level water table) and tier 2 (gridded). It is a diagnostic for now and is not used for ranking: [docs/physical-model.md](docs/physical-model.md). The plan is to grow it into the neraca air that simulates rewetting scenarios (canal blocks, pumping). It will replace the outputs above only after it passes a check against the field water tables, and the climatic balance stays as the fallback for KHG without an adequate DTM. Review of other models and data: [research_notes/groundwater_models_review.md](research_notes/groundwater_models_review.md). repeat-pump uses the same solver for its block optimisation, installed from a tagged GitHub archive of this repository.

The bucket-model experiments were retired on 2026-10-26 (record: [docs/bucket_experiments_README.md](docs/bucket_experiments_README.md), `docs/bucket_reports/`).

## Install

repeat-common is not on PyPI: install it from its folder (or its GitHub repository) first.

```bash
pip install ../repeat-common[gee]          # shared readers; [gee] adds earthengine-api
pip install -e ".[all,dev]"                # extras: neraca (DTM, peat, canals), sitmat (stations), gee (Earth Engine, batch)
earthengine authenticate                   # once per machine
python -m pytest -q
```

The groundwater solver alone (`repeat_neraca.groundwater`) needs only the base install (numpy, scipy, pandas, pydantic, pyyaml). Other packages that depend on it, such as repeat-pump, pin a tag: `repeat-neraca @ https://github.com/Re-Peat-Project/repeat-neraca/archive/refs/tags/v<version>.zip`. Bump `version` in `pyproject.toml` and push a matching tag when the solver changes.

Environment variables:

| Variable | Points to | Needed by |
|---|---|---|
| `REPEAT_KHG` | `_khg`, the per-KHG work folders | everything |
| `REPEAT_DATA` | `_data` (national boundaries for KHG without sub-KHG units; DTM and peat depth for the physical model) | batch, run |
| `REPEAT_HUB` | the `re-peat` folder (KHG registry `sites/khg_registry.csv`, site configs) | batch, when repeat-common is installed outside the workspace |
| `EE_PROJECT` | an Earth Engine Cloud project (`ee-danylaksono`) | Earth Engine fetch |
| `SITMAT_PROCESSED` | `repeat-sitmat/sitmat_out/processed` | stations; any command that reads a site `neraca.yaml` |

## How to run

```bash
# every selected KHG, or a list of codes, or all 865 KHG of the registry: fetch from Earth Engine, then the balance
repeat-neraca-batch --selected --end 2026-10-01
repeat-neraca-batch --khg 16.02.01 14.10.01 --end 2026-10-01
repeat-neraca-batch --all --end 2026-10-01                 # about 14 hours; cached, so it can be stopped and resumed

# one KHG step by step
python -m repeat_common.fetch_gee_balance --khg 16.02.01 --products chirps,mod16,wapor --start 2018-01-01 --end 2026-10-01
repeat-neraca-balance --inputs $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/inputs --out $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/runs/balance

# KHG deficit, for a KHG with a site config (re-peat/sites/<khg>/neraca.yaml) and SiTMAT stations
repeat-neraca-stations --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml
repeat-neraca-run --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary \
    --out $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/runs/deficit

# groundwater model (in development): the recommended set-up for chosen KHG; see "Groundwater model: run it yourself"
python scripts/run_model_batch.py --dem deltadtm --khg 14.10.01 15.05-07-10.01
```

`--end` is the first day after the last complete dekad of the products used. A KHG without `02_delineation/subkhg_units.gpkg` runs as one unit (inputs in `inputs/khg_level/`, results in `runs/balance_khg_level/`). Options of the balance: `--et` (default `mod16,wapor`, the first is central), `--rain-mode` (default `khg`; `unit` keeps rain per sub-KHG). `scripts/run_neraca.py` is the same as `repeat-neraca-run`. `repeat-neraca-stations` also takes `--kinds concession,community`, `--min-coverage` (community records start in late July 2026, so 0.3 keeps them) and `--out`; the groundwater model reads its own station export from `03_neraca/inputs/model/` when there is one. Options of the groundwater model: `repeat-neraca-model --help` and the report, sections 3 and 9.

| Command | Module | Does |
|---|---|---|
| `repeat-neraca-batch` | `repeat_neraca.batch` | Earth Engine fetch and balance for a list of KHG, `--selected` or `--all` |
| `repeat-neraca-balance` | `repeat_neraca.balance` | balance per sub-KHG from fetched tables |
| `repeat-neraca-stations` | `repeat_neraca.stations` | SiTMAT station files for a KHG |
| `repeat-neraca-map` | `repeat_neraca.maps` | map layers of one KHG: balance per sub-KHG, SiTMAT stations |
| `repeat-neraca-model` | `repeat_neraca.model` | groundwater model of a KHG from its code: daily water table on a grid; managed land held at a target (`--managed-target`); block and pumping scenarios from repeat-pump (`--blocks pump`, `--supply pump`); season maps and a table per sub-KHG; scored against stations and field points. In development: method, decisions and results in [docs/groundwater-model-report.md](docs/groundwater-model-report.md) |
| `repeat-neraca-run` | `repeat_neraca.run` | KHG deficit, and the groundwater model tiers 1 and 2 ([docs/physical-model.md](docs/physical-model.md)) |

## Groundwater model: run it yourself

The groundwater model (`repeat-neraca-model`, package `repeat_neraca.groundwater`) simulates the daily water table of a KHG on a grid and the effect of canal blocks and pumping. It is in development: the maps are indicative, and the station check passes only where stations exist outside managed land. Method, decisions D1 to D25 and results: [docs/groundwater-model-report.md](docs/groundwater-model-report.md).

**1. Mandatory input data.** Everything is read from the KHG work folder `$REPEAT_KHG/<code>_<name>/` (`repeat_common.khg.folder`). The chain runner `re-peat/tools/khg_pipeline.py` makes it (steps `local_inputs`, `dem_inputs`, `dem_correction`, `delineation`). The model stops with a message when a mandatory file is missing.

| Input | File | Made by | Mandatory |
|---|---|---|---|
| KHG boundary | `00_inputs/khg.gpkg` | `local_inputs` | yes |
| Canals by class | `00_inputs/canals.gpkg` (field `KET_KANAL`: Kanal Primer, Sekunder, Tersier) | `local_inputs` | yes |
| Peat depth | `00_inputs/peat_depth.tif` (unit scale `peat_depth.scale` in `re-peat/sites/<khg>/khg.yaml`, default 0.01 for cm) | `local_inputs` | yes: a KHG with neither a depth raster nor BBSDLP depth classes cannot run |
| Peat depth, gaps | `00_inputs/national/kedalaman_gambut_bbsdlp.gpkg` (`--depth-fallback bbsdlp`), then the KHG median | `local_inputs` | no |
| DTM | `lidar`: the clip named in `khg.yaml`; `deltadtm`, `demnas`: `01_dem/processed/<dem>/dtm_smooth.tif`; for `deltadtm` also the raw clip `01_dem/inputs/deltadtm.tif` | `dem_inputs`, `dem_correction` | yes, one variant (`--dem`) |
| Rain and ET, KHG mean | `03_neraca/inputs/model/balance_<product>_dekad.csv` | fetched by `--fetch` (Earth Engine, cached; needs `earthengine authenticate` and `EE_PROJECT`) | yes; use `--et mod16nrt` for dates after 2025-12 |
| Managed land | `00_inputs/national/izin_usaha_2025.gpkg` (written from `$REPEAT_DATA/landstatus/` on first use) | the model | for `--managed-target` |
| Existing canal blocks | `00_inputs/blocks.gpkg` (BRGM Sekat Kanal points) | `local_inputs` | no (`--existing-blocks none`) |
| Sub-KHG units | `02_delineation/<dem>/subkhg_units.gpkg` | `delineation` | no: without it the unit table has one row |
| Dry window of the supply cap | `03_neraca/<dem>/inputs/balance_chirps_dekad.csv` and `balance_mod16_dekad.csv`, 2018 onwards | `repeat-neraca-batch`, or `repeat_common.fetch_gee_balance` | for `--supply-cap climate` |
| Stations, field points | `03_neraca/inputs/model/stations*.csv` (`repeat-neraca-stations`), `00_inputs/field_wtd.csv` (`repeat_neraca.groundwater.fieldobs`) | | no: without them the checks read "not testable" |
| Interventions | `05_pump/<dem>/<khg>.gpkg`, layers `sekat_reach` and `interventions` (repeat-pump) | `pump` | only for `--blocks pump` and `--supply pump` |

Environment variables: `REPEAT_KHG`, `REPEAT_DATA`, `REPEAT_HUB`, `EE_PROJECT`, and `SITMAT_PROCESSED` when stations are used (table under "Install").

**2. Run one KHG or a list.** `scripts/run_model_batch.py` runs the recommended set-up for the KHG folders in `$REPEAT_KHG`, or for the codes given. A KHG whose run folder already holds `model_report.md` is skipped (`--force` reruns), so an interrupted batch resumes.

```bash
python scripts/run_model_batch.py --dem deltadtm --dry-run                        # list the KHG and grids
python scripts/run_model_batch.py --dem deltadtm --khg 14.10.01 15.05-07-10.01    # chosen KHG
python scripts/run_model_batch.py --dem deltadtm --workers 2                      # every KHG folder
```

The set-up (D21, D24, D22): canals inside cells at 0.80 / 0.32 / 0.24 m below the land (primary, secondary, tertiary), existing blocks, managed land held at 0.4 m (PP 57/2016) with the supply capped at the KHG's own dry-season shortfall (`--supply-cap climate`), peat base, BBSDLP depth fallback, ET `mod16nrt`, screened stations, window 2025-11-01 to 2026-10-01. The grid is 100 m up to 250,000 ha and 200 m above. Results go to `03_neraca/<dem>/runs/model/d22_climate_2026/`, logs to `logs/model_<dem>_d22_climate_2026.log`, and the batch writes `$REPEAT_KHG/model_batch_<dem>_<run>.csv`. The same run for one KHG, written out:

```bash
repeat-neraca-model --khg 15.05-07-10.01 --dem deltadtm --start 2025-11-01 --end 2026-10-01 --res 100 --run d22_climate_2026 \
    --peat-table tropical-large --drawdown primary=0.8,secondary=0.32,tertiary=0.24 --managed-target 0.4 --peat-base \
    --depth-fallback bbsdlp --et mod16nrt --canal-cells leak --screen-stations --supply-cap climate --fetch
```

**3. What the supply cap does.** Managed land is topped up to its target each day until a cell has received the cap. After that it falls with the water table. With `--supply-cap climate` the cap is the shortfall of the run year (ET minus rain, floored at 0) over the KHG's dry window: the 14 dekads of the year with the largest mean shortfall in 2018-2025. The maps, the unit table and the supply are reported over that window (D25). `--season` overrides it, and without the cap the season is 1 June to 30 September. A cap of 0 mm means rain exceeded ET over the window in the run year, so no water was added. `--supply-cap deficit` takes the cap from the station-based deficit, and a number gives a cap in mm.

**4. Outputs.** `03_neraca/<dem>/runs/model/<run>/` (table under "Outputs"). The maps to open in QGIS are `model_season_mean_depth.tif` (cm below the surface, positive down), `model_season_days_deeper_40cm.tif` (days of the season; open land only) and `model_season_managed_supply.tif` (mm). `model_units.csv` has one row per sub-KHG. `model_report.md` lists the source of every input and the station gate.

**5. Intervention scenarios.** Run the baseline, then the same command with `--blocks pump` (the blocks of repeat-pump's `sekat_reach`) and with `--blocks pump --supply pump` (land that repeat-pump marks for water, held at `--supply-target`). Compare them:

```bash
python scripts/compare_scenarios.py --baseline <baseline run folder> --scenario <blocks run folder> <blocks and pumping run folder> --out docs/reports/scenarios_<khg>.md
```

Each scenario run writes `days_deeper_40cm_change.tif` (days, scenario minus baseline; negative is wetter), and the report gives the change by distance from a block reach and per sub-KHG. A block scenario needs the baseline canal level that repeat-pump assumes (1.0 m, `sekat.balance_drawdown_m`; the report's example uses 1.2 m). Otherwise blocks that hold water shallower than the canals raise nothing.

**6. Reading the result.** Treat the maps as indicative: the model is in development, managed land is held at an assumed target, and the station gates are testable only where stations lie outside managed land (`station_scores.json`, `gate`). Peat depth, the DTM and the canal levels limit it most; see the report's limitations.

## Inputs

| Input | Source | Read by |
|---|---|---|
| Sub-KHG units | `_khg/<khg>/02_delineation/subkhg_units.gpkg` (`unit_id`), from repeat-delineation; else the KHG from `_data/batas_khg_indonesia.gpkg` | fetch |
| Rain | CHIRPS daily, `UCSB-CHG/CHIRPS/DAILY`, 0.05°, to 2026-09-30 | fetch |
| Evapotranspiration | MOD16A2GF v061, 500 m, to 2025-12 (central); MOD16A2 v061 without gap filling (`mod16nrt`, 2021 to 2026-10, for 2026 runs); WaPOR v3 L1 AETI dekadal, 326 m, to 2026-10-11 | fetch |
| Land cover | ESA WorldCover v200, 10 m | fetch (interception) |
| Rain reference (checks) | IMERG Final monthly V07, 0.1°, to 2025-09 | fetch with `--products imerg --step month` |
| Water table | SiTMAT concession stations, 2026-04-01 to 2026-10-22 (`SITMAT_PROCESSED`) | stations |
| Rain and evaporation, KHG mean | ERA5 daily through `repeat_common.forcing` (cache), or `inputs/forcing_daily.csv` | run (deficit) |
| Parameters | `src/repeat_neraca/parameters.yaml` (ships with the package; `python scripts/registry_table.py` prints it) | balance, run |

Units, licences and periods of the datasets: method report, section 3, and `re-peat/sites/data_catalog.csv` (kind `cloud`).

## Outputs

In the KHG work folder `_khg/<khg>/03_neraca/`, or `03_neraca/<dem>/` for a DEM variant (`repeat-neraca-batch --dem`, as the chain runner `re-peat/tools/khg_pipeline.py` calls it); the KHG deficit stays in `03_neraca/runs/deficit/`:

| File | Content |
|---|---|
| `inputs/balance_<product>_dekad.csv` | `unit_id, start, end, days, mm, n_px, time_cov`: period total per unit (mm), valid pixels, share of the period covered; `.json` next to it: collection, scale, API version, fetch dates |
| `inputs/units_landcover.csv` | `unit_id, area_km2, wc_<class>` (WorldCover class shares) |
| `runs/balance/neraca_balance_unit.csv` | one row per sub-KHG, columns below |
| `runs/balance/neraca_balance_monthly.csv` | `month, unit_id, WB_mm, et_source` |
| `runs/balance/neraca_balance.md` | spread, ET agreement, year stability, forest-share check, KHG calendar of monthly WB |
| `runs/balance/registry_snapshot.json` | parameter values used, with a hash |
| `runs/balance/neraca_map.gpkg` | map layers (`repeat-neraca-map --khg <folder>`, also written by the batch): `neraca_units` (sub-KHG polygons with the balance, monthly climatology `wb_m01`-`wb_m12`, dry-season mean `wb_dry_mm`, KHG deficit; `order_ok` = 0 means grey the values out, do not rank them), `neraca_stations` (SiTMAT water table in the deficit window: start, end, change, deepest, share of days deeper than 40 cm), `neraca_monthly` (table). No water-table surface: the gridded model failed the station check |
| `inputs/stations.csv`, `inputs/stations_daily.csv` | SiTMAT stations; daily depth (cm, positive down) |
| `runs/deficit/neraca_khg.csv` | KHG deficit: window, `n_stations`, `net_balance_mm`, `obs_change_cm`, `deficit_mm` (`_low`, `_high`), `deficit_m3`, `deficit_months` |

`neraca_balance_unit.csv`:

| Column | Meaning |
|---|---|
| `u_wb_mean` | mean monthly WB over the complete years, mm/month |
| `u_deficit_months` | months with WB < 0, per year |
| `p_minus_et_mean_mm` | P − ET without C and I, mm/month; between units of a KHG, the ET signal |
| `wb_year_sd_mm` | spread of the yearly mean WB between years |
| `interception_share`, `n_px_<product>`, `wb_mean_<et>`, `deficit_months_<et>`, `n_years` | I used, pixels per unit, the second ET source, years used |
| `balance_stable_ok` | 1: ET products agree on the order of units and the order holds between years (p < 0.01); 0: not; empty: fewer than 5 units |

`_khg/neraca_balance_summary.csv` has one row per KHG from `repeat-neraca-batch`.

Groundwater model runs (`repeat-neraca-model`) write to `03_neraca/<dem>/runs/model/<run>/`, with rain and ET in `03_neraca/inputs/model/`:

| File | Content |
|---|---|
| `model_series.csv` | per day: P, ET, KHG-mean depth, share deeper than 40 cm, water from canals and the edge, ET share, open-land depth, water supplied to managed land (mm, m3) |
| `model_units.csv` | per sub-KHG (or the KHG): open and managed area, the season's open-land depth and days deeper than 40 cm, managed supply |
| `model_season_days_deeper_40cm.tif`, `model_season_mean_depth.tif`, `model_season_managed_supply.tif` | season maps (June to September by default, the dry window with `--supply-cap climate`, or `--season`); the days map covers open land only |
| `model_depth_window.tif`, `model_depth_end.tif`, `model_managed_target.tif` | depth over the field window and on the last day; target of held land |
| `station_scores.json`, `station_scores.csv`, `station_sim_daily.csv` | scores against SiTMAT stations and the gate; simulated daily depth at the stations |
| `field_scores.json`, `field_points.csv` | scores against field points (`00_inputs/field_wtd.csv`) |
| `inputs.csv`, `run_config.json`, `managed_targets.csv`, `registry_snapshot.json`, `model_report.md` | source of each input and its share of the KHG; settings; targets per licence; report |

## What neraca hands to the other modules

`re-peat/docs/11-data-contracts.md`, section C5. The prioritisation merges `neraca_balance_unit.csv` through `extra_indicators`: the rank-sum's water slot reads `p_minus_et_mean_mm`, `u_deficit_months` is not ranked (its order between units follows land cover), and the need score gives the balance weight 0. `common.pipeline.gate_balance` leaves the balance columns empty where `balance_stable_ok` is 0. The KHG deficit (`neraca_khg.csv`) goes to repeat-pump through the prioritisation's `subkhg_priority.csv`.

## Checks

`python -m pytest -q` (arithmetic, balance, flag, deficit, physical model). Checks against data, each writing a report in `docs/reports/`: `check_gee_balance.py` (fetch equals a direct reduction of one image), `reproduce_2021.py` (2021 scripts reproduced), `check_forcing_products.py` (rain against IMERG, ET products), `check_balance_design.py` (rain mode, central ET, threshold), `check_forcing_2026.py`, `check_deficit_months.py` (Pulau Padang against Amal 2022), `check_unit_deficit.py` (per-unit deficit on stations). Commands: method report, section 10.

## Third-party data

`src/repeat_neraca/groundwater/data/` holds peat tables from Urzainki et al. (2020); read `NOTICE-urzainki2020.md` there before redistributing.

## Layout

```
src/repeat_neraca/
  params.py, parameters.yaml     parameter registry (every run stores a snapshot with its hash)
  balance.py, batch.py, maps.py  climatic balance per sub-KHG, batch over many KHG, map layers
  stations.py, deficit.py        SiTMAT station files, KHG deficit
  run.py                         command for the KHG deficit and the groundwater tiers
  model.py                       command for the groundwater model of a KHG (in development)
  groundwater/                   groundwater model
    solver.py, data/             2D Boussinesq solver and peat tables (shared with repeat-pump)
    grid.py                      a real KHG on a metric grid (boundary, DTM, peat depth, canals, stations)
    forcing.py                   daily rain and evaporation of the KHG
    lumped.py, spatial.py        tier 1 (KHG level) and tier 2 (gridded)
    validate.py                  comparison with the SiTMAT stations
    simulate.py                  daily run with a canal level per class and the water the canals put into the peat
    fieldobs.py, fieldcheck.py   field water-table points of a KHG, and the score and gate against them
  testbed/                       synthetic KHG generator and the Urzainki et al. (2020) Siak benchmark
config/neraca/                   example.yaml (site config template; real ones in re-peat/sites/<khg>/neraca.yaml)
scripts/                         checks against data (check_*.py, reproduce_2021.py), run_neraca.py, benchmark_urzainki2020.py,
                                 registry_table.py; groundwater model: model_sweep.py, check_field_inputs.py, rank_station_sites.py,
                                 summarise_model_runs.py, compare_scenarios.py
tests/                           pytest
```

## Documents

| Document | Content |
|---|---|
| [docs/neraca-air-method.md](docs/neraca-air-method.md) | the adopted method (climatic balance and KHG deficit), its evidence and results |
| [docs/groundwater-model-report.md](docs/groundwater-model-report.md) | the groundwater model for rewetting scenarios: review, decisions, implementation, results, FAQ |
| [docs/physical-model.md](docs/physical-model.md) | the groundwater model: inputs, parameters, tiers, how to run it |
| [docs/neraca-air.md](docs/neraca-air.md) | results of the groundwater model on Sugihan-Lumpur and Kampar-Gaung, and why it is a diagnostic |
| [docs/tropical-peat-hydraulic-parameters.md](docs/tropical-peat-hydraulic-parameters.md) | peat tables: the boreal table against tropical measurements |
| [docs/references.md](docs/references.md) | literature read for the method |
| [docs/method-plan.md](docs/method-plan.md) | record of how the method was settled (2026-10-26) |
| [docs/neraca_air_recap.md](docs/neraca_air_recap.md) | the first build plan of the module; superseded in part by the method plan |
| [docs/bucket_experiments_README.md](docs/bucket_experiments_README.md) | record of the retired bucket experiments |
| `docs/reports/` | reports written by the check scripts and the groundwater runs |
| `docs/bucket_reports/` | reports of the retired bucket experiments |
| `docs/figures/` | method diagram (`neraca_method.drawio`, rebuilt by `make_neraca_method.py`) |
| [research_notes/groundwater_models_review.md](research_notes/groundwater_models_review.md) | groundwater models and open satellite data for rewetting scenarios (2026-10-28) |
| [research_notes/peat_parameters_sumatra_kalimantan.md](research_notes/peat_parameters_sumatra_kalimantan.md) | measured Sy, K and ET of Sumatran and Kalimantan peat, with Ismail et al. 2021 in full |
| [research_notes/burned_peat_hydrology.md](research_notes/burned_peat_hydrology.md) | burned peat: infiltration, runoff, and what it means for the model |
| [research_notes/gee_2021_kahayan_sebangau.md](research_notes/gee_2021_kahayan_sebangau.md) | the 2021 Kahayan-Sebangau Earth Engine scripts |
| [research_notes/runoff_coefficient_pulau_padang.md](research_notes/runoff_coefficient_pulau_padang.md) | origin of the runoff coefficient C |
| `research_notes/Peatland neraca air operational gaps/` | review of operational gaps (`README.md`) and its topic notes |
| `research_notes/references/` | papers |
