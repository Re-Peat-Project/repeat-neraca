# Neraca air: the physical water balance of a KHG

Status 2026-10-16. Neraca air is built here, from physical parameters only, and compared with the observed water tables. Nothing is fitted. It replaced the bucket-model experiments (retired 2026-10-26, record in `bucket_experiments_README.md`). Since 2026-10-26 it is a diagnostic: the sub-KHG output is the climatic balance (`repeat_neraca.balance`, [method-plan.md](method-plan.md)); the ranking in `repeat-prioritisation` can read the result through its `extra_indicators` file.

## What it is

Two tiers, both in `src/repeat_neraca/`:

| Tier | Equation | Code |
|---|---|---|
| 1, KHG level | `Sy(z) dz/dt = R - C(z) (z - z_c)`, `C = 12 T(z) / L^2`: one water table for the whole KHG. R = P - ET, z_c = -canal drawdown, L = 1 / (canal length per area). The coefficient 12 T / L^2 reproduces the strip between two drains (tested against the 2D solver) | `lumped.py` |
| 2, 2D groundwater | `Sy(z) dh/dt = div(T(z) grad h) + R` on a metric grid, fixed heads on the KHG edge ring (river or sea) and on the canal cells (local surface minus drawdown) | `spatial.py` (solver: `testbed/groundwater.py`) |

`Sy` and `T` come from the peat table (`PeatTable.urzainki2020`, storage and transmissivity as functions of water table depth). Parameters are in `src/repeat_neraca/parameters.yaml`: `canal_drawdown` (1.2 m, Urzainki et al. 2020), `river_stage_below_edge` (0.3 m), `initial_wtd` (-0.2 m), `neraca_grid_res_m` (500 m). `inputs.py` reads a real KHG (boundary, DTM, peat depth, canals by class, stations) from the paths in `config/neraca/<khg>.yaml`; `validate.py` compares the run with the SiTMAT stations.

Water table depth is negative below the surface inside the model; the reports give depth in cm, positive down.

## How to run it

The station files come from the SiTMAT extract (`repeat_neraca.stations`, config block `stations:`); the daily ERA5 forcing is read through `repeat-common` from the KHG cache (`forcing_direct`), or from the existing `forcing_daily.csv`:

```bash
python -m repeat_neraca.stations --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml      # needs SITMAT_PROCESSED

# in repeat-neraca (pip install -e .[neraca]; REPEAT_DATA and REPEAT_WORK set; site configs are in the hub, re-peat/sites/<site>/neraca.yaml)
python scripts/run_neraca.py --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary --k-multiplier 1,10,50,200,1000 --drawdown 0.5,1.2
python scripts/run_neraca.py --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 2 --res 500
python scripts/run_neraca.py --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary --et-stress natural   # evaporation falls when the water table is deep
python -m pytest tests/test_neraca.py
```

Reports are written to `_out/<name>/neraca_report.md` (not tracked); the ones quoted below are copied to `docs/reports/`.

## First results (2026-04-01 to 2026-10-09, ERA5 rain and evaporation)

Monthly rain minus evaporation of the KHG (mm) and the observed mean water table depth of the SiTMAT stations (cm):

| | Apr | May | Jun | Jul | Aug | Sep | Oct |
|---|---|---|---|---|---|---|---|
| Sugihan-Lumpur, P - E | +168 | +102 | -16 | -90 | -91 | -83 | -26 |
| Sugihan-Lumpur, observed depth | 38 | 35 | 39 | 43 | 48 | 51 | 52 |
| Kampar-Gaung, P - E | +175 | +126 | +58 | +5 | -83 | +40 | -11 |
| Kampar-Gaung, observed depth | 42 | 37 | 39 | 38 | 46 | 56 | 39 |

1. **Sugihan-Lumpur: the balance needs about 285 mm that the water table does not show.** From June to October rain minus evaporation sums to -306 mm; with a specific yield of 0.14-0.2 the water table should fall 1.5-2 m. It fell 14 cm. The simulated KHG-mean curve ends at 160 cm and averages 66 cm against 43 cm observed (bias +23 cm), with a correlation of 0.96 (the timing is right, the amplitude is not). Either evaporation is overestimated at depth, or water arrives from outside the rain balance (tidal and river inflow through the canals, pumping, gates). The size of that missing term, about 3 mm/day over the dry season, is the quantity of interest: it is the water the managed system supplies to hold the level.
2. **Kampar-Gaung: the balance is close to neutral and the physical curve is not far off.** June to October sums to about +9 mm. The simulated mean is 25 cm against 42 cm observed (bias -17 cm), correlation 0.68.
3. **The canals do nothing in the physical model.** With the Urzainki peat table the transmissivity is about 0.5 m2/day at the surface and falls to near zero by 0.6 m depth, so the exchange time between a drain and the peat is years (`tau = Sy L^2 / (12 T)`). The 2D run on Sugihan-Lumpur at 500 m (30% of cells fixed as canal or edge) gives every free cell, and every station, the same curve: the cells behave as independent buckets. Per sub-KHG water table is therefore identical (65 cm) and carries no information.
4. **More transmissivity makes it worse, not better.** Scaling T by 10 to 1000 deepens the simulated water table (66 to 100 cm at drawdown 1.2 m), because the canals at 1.2 m below the surface then pull the water table down towards their level. The observed water tables sit at 35-55 cm: shallower than the canal level the rule assumes.

5. **Evaporation that falls with water table depth helps a little, not enough.** With the PEATCLSM-Trop thresholds (Apers et al. 2022; registry `et_stress_start`, `et_stress_end`) evaporation is multiplied by 1 above the start depth and falls linearly to 0 at the end depth. Natural-peat thresholds (-0.70 m to -1.82 m) cut the Sugihan-Lumpur error from 56.6 to 46.2 cm and the bias from +22.7 to +16.6 cm (simulated mean 60 cm against 43 cm observed); the drained-peat thresholds (-1.54 m to -2.85 m) change almost nothing (56.5 cm), because the simulated water table is already near -1.5 m when they start. In Kampar-Gaung it changes nothing (27.4 cm either way). Reports: `docs/reports/neraca_*_tier1_et_*.md`. A deep water table cuts evaporation but the stations stay at 35-55 cm, so the missing term in point 1 is still water supply, not evaporation.

## KHG deficit (`neraca_khg.csv`)

The number the other modules need from neraca is the water the managed system has to supply to hold the water table. It is a mass balance, not a model result, so it does not depend on the failures listed above:

```
deficit_mm = max(0, -sum(P - E) - Sy * dz_obs * 10)        deficit_m3 = deficit_mm / 1000 * KHG area
```

P - E is the KHG-mean daily rain minus evaporation over the window; `dz_obs` is the change in the station-mean water table depth (cm, positive = deeper) between the first and last 7 days of the window. A water table that fell supplied part of the loss itself; one that rose against a negative balance adds to what had to come from outside. Code: `src/repeat_neraca/deficit.py`, written by `scripts/run_neraca.py` as `neraca_khg.csv` whatever tier is run. Settings can be overridden in a `deficit:` block of the site config.

Choices (agreed 2026-10-20):

- **Window:** 1 June to the last day with forcing (at most 31 October). Dry periods are what matters, but station coverage is limited, so this is the window we have (2026 only). More years can be added where water table data cover them.
- **Sy:** a constant 0.15, band 0.10 to 0.20. The Urzainki et al. (2020) peat tables are not used for the deficit: the repository's own provenance note (`testbed/data/NOTICE-urzainki2020.md`) says the tables were built from Paivanen (1973) retention curves with boreal values, although Urzainki et al. (2020) applied them to Siak, Riau. They are an option only if tropical peat studies have adopted them (or tropical retention curves are put in their place). The tier 1 and tier 2 runs above still take Sy(z) and T(z) from those tables, so the same caveat applies to them. Tropical alternatives, and what they do to these results, are in [tropical-peat-hydraulic-parameters.md](tropical-peat-hydraulic-parameters.md); the runs above used the boreal table.
- **Evaporation:** ERA5 is the central value. WaPOR (about 300 m) gives the other bound where it covers every day of the window. Higher-resolution rain and evaporation data may improve this later, and would allow a per-sub-KHG deficit.
- **Band:** `deficit_mm_low` and `deficit_mm_high` are the smallest and largest deficit over ERA5 or WaPOR and Sy 0.10, 0.15 or 0.20.
- **No skill flag here.** The table reports `n_stations`, `valid_day_share` and `e_wapor_covers_period` as the evidence. `neraca_skill_ok` exists only in the per-sub-KHG file, as 1 when the Spearman of the dry-season peak depth across stations is at least 0.3, otherwise 0.

`deficit_months` counts the calendar months of the window with a negative P - E, and a partial last month counts as a month (here 1 to 9 October).

Result, 2026-06-01 to 2026-10-09 (131 days, all with forcing):

| KHG | P - E | water table | deficit (band) | volume |
|---|---|---|---|---|
| Sugihan-Lumpur (51 stations) | -307 mm | 11 cm deeper | 290 mm (227-296) | 1,842 million m3 over 6,348 km2 |
| Kampar-Gaung (78 stations) | +9 mm | 11 cm shallower | 7 mm (0-12) | 50 million m3 over 7,115 km2 |

Sugihan-Lumpur needs about 290 mm of water from outside the rain balance in one dry season (the roughly 285 mm of point 1 above, now with a definition); Kampar-Gaung needs almost none by this measure, although its stations too sit at a held 40 cm. A tidal and managed system like Sugihan-Lumpur is where pumping and canal inflow are large; this number is the quantity to size them against. Per-sub-KHG outputs from the 2D run get `neraca_skill_ok = 0` on Sugihan-Lumpur, because every cell follows the same curve.

## What this says

- A rain-driven balance with canals as passive drains cannot reproduce water tables that are held at 35-55 cm through a dry season. The held level needs water from outside the rain balance and a canal level that is not "surface minus 1.2 m". Both are management facts (compare `docs/neraca_air_references.md` in `khg-prioritisation-module`: Taufik et al. 2019 set the canal level by season; Apers et al. 2022 name the static treatment of drainage as the main error).
- The physical result is still useful at KHG level: it gives the **deficit the system must meet** to hold the water table, in mm or million m3 per dry season, and the months in which it arises. For Sugihan-Lumpur that is the roughly 285 mm (about 1.8 billion m3 over 6,348 km2) of the June-October balance that the stations do not show.
- Terrain limits any 2D result (docs 07 and 08): the DTM error at 300-600 m is comparable to the head differences. The 2D tier is useful for regional patterns only after the peat table and canal levels are right.

## Not done yet

1. *(Done, see point 5 of the results; run for the KHG-level tier only. The 2D tier takes the same `--et-stress` option and the solver now accepts a recharge field per step, so a per-cell evaporation factor works there, but it was not run.)*
2. A supply term at the KHG edge and canal cells (tide and river inflow) in place of fixed heads at surface minus drawdown; test with the stations whether a constant canal level, or the level the stations imply, fits.
3. Hydraulic conductivity from the registry (k_forest 30 m/day, k_drained 5 m/day) in place of the Urzainki table, which is far lower; the registry values are not wired into the solver.
4. Spatial rain and evaporation (CHIRPS, WaPOR) instead of one KHG series; the 250 m grid (about 100,000 cells, an hour or more per run) and the tertiary canals as sub-grid drains.
5. Writing `neraca_unit.csv` with the columns the ranking reads (`u_wt_peak_cm`, `u_wt_days_gt40` exist in `neraca_unit.csv`; the deficit indicators do not yet).
6. Both KHG with the 2D tier (only Sugihan-Lumpur was run) and a run over the 2019-2021 baseline windows (their forcing is in `forcing_daily.csv`; the stations only cover 2026).
