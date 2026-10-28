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
```

`--end` is the first day after the last complete dekad of the products used. A KHG without `02_delineation/subkhg_units.gpkg` runs as one unit (inputs in `inputs/khg_level/`, results in `runs/balance_khg_level/`). Options of the balance: `--et` (default `mod16,wapor`, the first is central), `--rain-mode` (default `khg`; `unit` keeps rain per sub-KHG). `scripts/run_neraca.py` is the same as `repeat-neraca-run`.

| Command | Module | Does |
|---|---|---|
| `repeat-neraca-batch` | `repeat_neraca.batch` | Earth Engine fetch and balance for a list of KHG, `--selected` or `--all` |
| `repeat-neraca-balance` | `repeat_neraca.balance` | balance per sub-KHG from fetched tables |
| `repeat-neraca-stations` | `repeat_neraca.stations` | SiTMAT station files for a KHG |
| `repeat-neraca-map` | `repeat_neraca.maps` | map layers of one KHG: balance per sub-KHG, SiTMAT stations |
| `repeat-neraca-run` | `repeat_neraca.run` | KHG deficit, and the groundwater model tiers 1 and 2 ([docs/physical-model.md](docs/physical-model.md)) |

## Inputs

| Input | Source | Read by |
|---|---|---|
| Sub-KHG units | `_khg/<khg>/02_delineation/subkhg_units.gpkg` (`unit_id`), from repeat-delineation; else the KHG from `_data/batas_khg_indonesia.gpkg` | fetch |
| Rain | CHIRPS daily, `UCSB-CHG/CHIRPS/DAILY`, 0.05°, to 2026-09-30 | fetch |
| Evapotranspiration | MOD16A2GF v061, 500 m, to 2025-12 (central); WaPOR v3 L1 AETI dekadal, 326 m, to 2026-10-11 | fetch |
| Land cover | ESA WorldCover v200, 10 m | fetch (interception) |
| Rain reference (checks) | IMERG Final monthly V07, 0.1°, to 2025-09 | fetch with `--products imerg --step month` |
| Water table | SiTMAT concession stations, 2026-04-01 to 2026-10-22 (`SITMAT_PROCESSED`) | stations |
| Rain and evaporation, KHG mean | ERA5 daily through `repeat_common.forcing` (cache), or `inputs/forcing_daily.csv` | run (deficit) |
| Parameters | `src/repeat_neraca/parameters.yaml` (ships with the package; `python scripts/registry_table.py` prints it) | balance, run |

Units, licences and periods of the datasets: method report, section 3, and `re-peat/sites/data_catalog.csv` (kind `cloud`).

## Outputs

In the KHG work folder `_khg/<khg>/03_neraca/`:

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
  groundwater/                   groundwater model
    solver.py, data/             2D Boussinesq solver and peat tables (shared with repeat-pump)
    grid.py                      a real KHG on a metric grid (boundary, DTM, peat depth, canals, stations)
    forcing.py                   daily rain and evaporation of the KHG
    lumped.py, spatial.py        tier 1 (KHG level) and tier 2 (gridded)
    validate.py                  comparison with the SiTMAT stations
  testbed/                       synthetic KHG generator and the Urzainki et al. (2020) Siak benchmark
config/neraca/                   example.yaml (site config template; real ones in re-peat/sites/<khg>/neraca.yaml)
scripts/                         checks against data (check_*.py, reproduce_2021.py), run_neraca.py, benchmark_urzainki2020.py,
                                 registry_table.py
tests/                           pytest
```

## Documents

| Document | Content |
|---|---|
| [docs/neraca-air-method.md](docs/neraca-air-method.md) | the adopted method (climatic balance and KHG deficit), its evidence and results |
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
| [research_notes/gee_2021_kahayan_sebangau.md](research_notes/gee_2021_kahayan_sebangau.md) | the 2021 Kahayan-Sebangau Earth Engine scripts |
| [research_notes/runoff_coefficient_pulau_padang.md](research_notes/runoff_coefficient_pulau_padang.md) | origin of the runoff coefficient C |
| `research_notes/Peatland neraca air operational gaps/` | review of operational gaps (`README.md`) and its topic notes |
| `research_notes/references/` | papers |
