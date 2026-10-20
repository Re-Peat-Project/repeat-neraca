# repeat-neraca

Neraca air (water balance) of a KHG for RE-PEAT (GitHub org Re-Peat-Project). Two things live here:

| Package | What | Status |
|---|---|---|
| `src/repeat_neraca/` | **Physical model**, no fitted parameters: KHG-level water table (`lumped.py`), 2D groundwater (`spatial.py`, solver in `testbed/groundwater.py`), parameter registry (`params.py`, `config/parameters.yaml`), a synthetic KHG testbed and the Urzainki et al. 2020 benchmark | the current model; see [docs/neraca-air.md](docs/neraca-air.md) |
| `src/repeat_neraca/bucket/` | **Bucket-model experiments** fitted to SiTMAT stations, Sentinel-1, finer forcing, canal level | kept as a record; failed its spatial skill check on Kampar-Gaung. See [docs/bucket_experiments_README.md](docs/bucket_experiments_README.md) |

Renamed 2026-10-20: the physical model was package `watershare` (with a `neraca` subpackage), now `repeat_neraca`; the experiments were package `neracaair`, now `repeat_neraca.bucket` (`python -m repeat_neraca.bucket.run`); `neraca_unit_tier2.csv` is now `neraca_unit.csv`. Generated reports and HTML pages made before that date (`docs/reports/`, `docs/bucket_reports/`) still name the old modules.

Note that the experiments write their own `neraca_unit.csv` (bucket-model indicators) into their own output folder. It is a different table from the physical model's `neraca_unit.csv` (water table per sub-KHG, `neraca_skill_ok`); the folder tells which.

## Install

```bash
pip install -e ../repeat-common            # needed by repeat_neraca.bucket; the physical model itself reads files only
pip install -e ".[neraca]"                 # real-KHG inputs for the physical model
pip install -e ".[neraca,experiments,dev]" # also the bucket experiments and pytest
python -m pytest -q
```

`repeat_neraca.params.Registry` finds `config/parameters.yaml` relative to the source tree, so use an editable install.

## Run the physical model on a real KHG

Set `REPEAT_DATA` (the REPEAT-LH `_data` folder) and `REPEAT_WORK` (derived data: clipped vectors, sub-KHG polygons, the ERA5 cache, the station files). The real site configs are in the hub, `re-peat/sites/<site>/neraca.yaml`; `config/neraca/example.yaml` is a copy to start from. Besides the paths in the config, the model reads `<inputs_dir>/stations.csv` and `stations_daily.csv` (written by `python -m repeat_neraca.bucket.export_inputs`), and rain and evaporation from the ERA5 cache (`forcing_direct`) or `forcing_daily.csv`.

```bash
python scripts/run_neraca.py --config ../re-peat/sites/sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary --k-multiplier 1,10,50,200,1000 --drawdown 0.5,1.2
python scripts/run_neraca.py --config ../re-peat/sites/sugihan_lumpur/neraca.yaml --tier 2 --res 500
```

`--peat-table urzainki2020|tropical-small|tropical-large` chooses the storage and transmissivity of the peat: the default is the boreal-curve table of this repository, the other two are the tropical sets of Urzainki et al. (2023). What the choice does, and why it is not the default yet: [docs/tropical-peat-hydraulic-parameters.md](docs/tropical-peat-hydraulic-parameters.md).

Output goes to `_out/<name>/`: `neraca_report.md`, `neraca_khg.csv` (the KHG deficit, see below), `tier1_series.csv`, `tier2_series.csv`, `neraca_unit.csv` (with a `neraca_skill_ok` column), `registry_snapshot.json`.

## What neraca hands to the other modules

`re-peat/docs/11-data-contracts.md`, section C5: a KHG-level table (`neraca_khg.csv`) and a sub-KHG table (`neraca_unit.csv`, written for now as `neraca_unit.csv`). With the current physical model the per-sub-KHG numbers carry no ranking information (`neraca_skill_ok = 0`); the usable result is the KHG-level deficit, a mass balance defined in [docs/neraca-air.md](docs/neraca-air.md#khg-deficit-neraca_khgcsv).

## Third-party data

`src/repeat_neraca/testbed/data/` holds peat tables from Urzainki et al. (2020); read `NOTICE-urzainki2020.md` there before redistributing.

## Layout

```
src/repeat_neraca/         physical model, registry, testbed
src/repeat_neraca/bucket/  bucket-model experiments (config.py holds the settings they need)
config/             parameters.yaml (registry), neraca/<khg>.yaml (inputs of a real KHG)
scripts/            run_neraca.py, benchmark_urzainki2020.py, registry_table.py
tests/              physical-model tests (pytest) and the experiments' tests
docs/               neraca-air.md, references.md, reports/ (physical model), bucket_reports/ (experiments)
```
