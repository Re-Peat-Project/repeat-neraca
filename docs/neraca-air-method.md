# Neraca air: the method adopted

Methodological report, repeat-neraca, 2026-10-26. Diagram: [figures/neraca_method.drawio](figures/neraca_method.drawio) (open in draw.io or the VS Code Draw.io extension). Plan and decisions behind it: [method-plan.md](method-plan.md).

## 1. What neraca air delivers

| Level | Output | Answers | Method |
|---|---|---|---|
| Sub-KHG | `u_wb_mean`, `u_deficit_months` per unit | Which sub-KHG have the least water from the climate, and in how many months a year | Climatic water balance of the 2021 Kahayan-Sebangau study, on Earth Engine rain and evapotranspiration (section 3A) |
| KHG | `deficit_mm`, `deficit_m3` | How much water the managed system supplied to hold the observed water table through the dry season | Mass balance on the SiTMAT stations (section 3B) |

The two are kept apart (data contract C5, `re-peat/docs/11-data-contracts.md`). The prioritisation merges the sub-KHG table through `extra_indicators`: `u_wb_mean` and `u_deficit_months` replace its own TerraClimate columns and fill the water-balance slots of the rank-sum; they are left empty where `balance_stable_ok` is 0 (`common.pipeline.gate_balance`), and keep weight 0 in the need score until the team sets one. The physical groundwater model stays in the repository as a diagnostic and is not on the ranking path (section 3C).

## 2. Inputs

| Input | File or source | Grid, unit | Period | Licence | Used in |
|---|---|---|---|---|---|
| Sub-KHG units | `_khg/<khg>/02_delineation/subkhg_units.gpkg` (`unit_id`), from repeat-delineation; a KHG without them runs as one unit from `_data/batas_khg_indonesia.gpkg` | polygons | | project | A |
| Rain P | CHIRPS daily, `UCSB-CHG/CHIRPS/DAILY` (Earth Engine) | 0.05° (5.6 km), mm/day | 1981-01-01 to 2026-09-30 | public domain | A |
| Evapotranspiration ET, central | WaPOR v3 L1 AETI dekadal, `FAO/WAPOR/3/L1_AETI_D` | 326 m, mean mm/day of the dekad, scale 0.1 | 2018-01-01 to 2026-10-11 | free use (FAO) | A |
| Evapotranspiration ET, second source | MODIS MOD16A2GF v061, `MODIS/061/MOD16A2GF` | 500 m, kg/m2 per 8 days, scale 0.1 | 2000 to 2025-12 | no restrictions (LP DAAC) | A |
| Land cover | ESA WorldCover v200, `ESA/WorldCover/v200` | 10 m, classes | 2021 | CC-BY-4.0 | A (interception) |
| Water table | SiTMAT concession stations, `repeat-sitmat/sitmat_out/processed` (`SITMAT_PROCESSED`) | daily depth, cm | 2026-04-01 to 2026-10-22 | as scraped | B |
| Rain and evaporation, KHG mean | ERA5 daily through `repeat_common.forcing` (cache), or `03_neraca/inputs/forcing_daily.csv` | 0.25°, mm/day | windows of the site config | Copernicus | B |
| KHG boundary | `_khg/<khg>/00_inputs/khg.gpkg` | polygon | | SK.129/MENLHK/2017 | B |

Dataset periods were read through the Earth Engine API and units, scales and licences from the Earth Engine catalogue pages, both on 2026-10-26. The datasets are catalogued with kind `cloud` in `re-peat/sites/data_catalog.csv`. No further water table data are expected: SiTMAT is one dry season.

## 3. Processing

### A. Sub-KHG climatic water balance

**Step 1. Rain and ET per unit per dekad** (`python -m repeat_common.fetch_gee_balance`, Earth Engine project `ee-danylaksono`).

- Periods are dekads: days 1-10, 11-20 and 21 to the end of the month.
- The total of a period is the sum over the source images that overlap it of (daily rate × days of overlap). The daily rate is the image value × scale, divided by the image length when the value is a total (CHIRPS day, MOD16 8-day composite) and taken as is when it is a mean rate (WaPOR). MOD16 values above 32,700 are fill codes and are masked.
- Each period is reduced to the mean per unit, area weighted, on the product's own grid (its CRS and transform). Nothing is resampled. The number of valid pixels and the share of the period covered by images are written with every value.
- WorldCover class shares per unit (10 m) for the interception term, counted in 0.1° pieces of each unit and summed, so no request times out.
- One request per product and year, run in parallel and cached in the KHG's `cache/`; `balance_<product>_dekad.json` records the collection, scale, period, API version and the date each year was fetched. Earth Engine products are revised upstream, so the CSV is the record of what a run used.

**Step 2. Monthly balance and indicators** (`python -m repeat_neraca.balance`).

```
WB(u, month) = P (1 - I_u) (1 - C) - ET          I_u = Σ_class share(u, class) × I_class
```

- A month counts only when all its dekads are fully covered for both P and ET; a year counts only when all 12 months do. Indicators are means over the complete years:
  - `u_wb_mean`: mean monthly WB, mm/month;
  - `u_deficit_months`: months with WB < 0, per year;
  - `wb_year_sd_mm`: spread of the yearly mean WB between years.
- These definitions are those of `repeat-prioritisation/common/indicators.py`, so the unit table can replace the prioritisation's own TerraClimate balance through `extra_indicators`.
- Stability: Spearman of the yearly mean WB across units for every pair of years, and of `u_wb_mean` between the two ET sources. `balance_stable_ok` = 1 when the median year-to-year value and the source-to-source value are both at least 0.5.
- WaPOR AETI and MOD16 ET include evaporation of intercepted rain. With them the `(1 - I)` term counts interception a second time. The formula is kept as established; `p_minus_et_mean_mm` gives the balance without C and I so the size of that term is visible.

### B. KHG supply deficit

**Step 3. Station files** (`python -m repeat_neraca.stations --config re-peat/sites/<khg>/neraca.yaml`): SiTMAT stations inside the KHG with readings on at least 50 % of the window days (2026-04-01 to 2026-10-15).

**Step 4. Deficit** (`deficit.py`, written by `scripts/run_neraca.py` as `neraca_khg.csv`):

```
deficit_mm = max(0, -Σ(P - E) - Sy × Δz_obs × 10)        deficit_m3 = deficit_mm / 1000 × KHG area
```

Window 1 June to the last day with forcing (at most 31 October). `Δz_obs` is the change in the station-mean depth (cm) between the first and last 7 days. A water table that fell supplied part of the loss itself; the rest came from outside the rain balance (tide, river, canals, pumping). The band `deficit_mm_low` to `deficit_mm_high` spans Sy 0.10-0.20 and ERA5 or WaPOR evaporation.

### C. Diagnostic only

The physical model (tier 1 `lumped.py`, tier 2 `spatial.py`: `Sy(z) dz/dt = R - C(z)(z - z_c)` and the 2D Boussinesq equation on DTM, peat depth and canals) reproduces the timing of the KHG-mean water table but not its level, and gives every sub-KHG the same curve. It explains why the observed level is held (water from outside the rain balance) and is not used for ranking. The bucket model fitted to the stations was retired on 2026-10-26 (record in `bucket_reports/`).

## 4. Parameters

From the registry `src/repeat_neraca/parameters.yaml` unless stated.

| Parameter | Value | Source | Used in |
|---|---|---|---|
| Runoff coefficient C (`runoff_coefficient`) | 0.12 | Aditya & Cahyono 2018, Pulau Padang (range 0.07-0.18); Bambang Kun Cahyono's value, taken as established | A |
| Interception I (`interception_*`) by WorldCover class | tree cover 0.164, mangroves 0.164, shrubland 0.08, herbaceous wetland 0.05, grassland 0.03, cropland 0.03, other classes 0 | Kahayan-Sebangau study 2021 (B.K. Cahyono) | A |
| Stability threshold (`balance.MIN_STABILITY`) | Spearman 0.5 | provisional, not agreed with the team | A |
| Specific yield Sy | 0.15 (band 0.10-0.20) | agreed 2026-10-20 (`neraca-air.md`) | B |
| Deficit window | 1 June to last forcing day, at most 31 October | agreed 2026-10-20 | B |
| Station coverage | ≥ 50 % of window days | `repeat_common.tma` default | B |

## 5. Outputs

All in the KHG work folder, `_khg/<khg>/03_neraca/`.

| File | Content |
|---|---|
| `inputs/balance_<product>_dekad.csv` | `unit_id, start, end, days, mm, n_px, time_cov`: period total in mm per unit, valid pixels, time coverage |
| `inputs/units_landcover.csv` | `unit_id, area_km2, wc_<class>` |
| `runs/balance/neraca_balance_unit.csv` | per unit: `u_wb_mean` (mm/month), `u_deficit_months` (per year), `wb_year_sd_mm`, `p_minus_et_mean_mm`, `interception_share`, `n_px_<product>`, `wb_mean_mod16`, `deficit_months_mod16`, `n_years`, `balance_stable_ok` |
| `runs/balance/neraca_balance_monthly.csv` | `month, unit_id, WB_mm, et_source` |
| `runs/balance/neraca_balance.md` | spread, source agreement, stability, KHG calendar of monthly WB |
| `inputs/stations.csv`, `inputs/stations_daily.csv` | SiTMAT stations and daily depth (cm, positive down) |
| `runs/<run>/neraca_khg.csv` | KHG deficit: `deficit_mm` (low, high), `deficit_m3`, `deficit_months`, `n_stations`, window and evidence columns |

All KHG at once: `python -m repeat_neraca.batch` (section 8) writes one row per KHG to `_khg/neraca_balance_summary.csv`.

## 6. Checks and results (2026-10-26)

| Check | What | Result | Report |
|---|---|---|---|
| Arithmetic | dekads, image lengths, overlap weights; whole-KHG unit from names with different spacing | pass (`repeat-common/tests/test_fetch_gee_balance.py`) | |
| Identity | a period equal to one source image gives that image's own value, reduced directly on its grid (Kampar-Gaung, 26 units) | WaPOR dekad: max difference 5e-14 mm; TerraClimate month: 1e-6 mm. MOD16 fill codes in the KHG: none | `scripts/check_gee_balance.py` |
| Tiled land cover | WorldCover shares counted in 0.1° pieces against one request (Kahayan-Sebangau, 16 units) | identical shares and areas | |
| Balance | formula, complete-year rule, partly covered months | pass (`tests/test_balance.py`) | |
| V1 | reproduce the 2021 Kahayan-Sebangau scripts (TerraClimate 2010-2020, C = 0.25) against the 2021 expression on Earth Engine at 2,500 m | within 0.1 mm per sub-KHG and month | [reports/kahayan_sebangau_2021_reproduction.md](reports/kahayan_sebangau_2021_reproduction.md) |
| V2 | Earth Engine P and ET against the ERA5 forcing of the deficit, 2026-06-01 to 09-30 | Sugihan-Lumpur: CHIRPS 208 mm against ERA5 140 mm, WaPOR ET 419 against ERA5 E 420; P - E -211 against -281 mm. Kampar-Gaung: rain alike (513, 528), WaPOR ET 384 against ERA5 508; P - E +130 against +21 mm. WaPOR read through Earth Engine is higher than the WaPOR column of the deficit file (419 against 367, 384 against 351 mm, both with WaPOR on all 122 days) | [reports/forcing_2026_gee_vs_era5.md](reports/forcing_2026_gee_vs_era5.md) |
| V3 | deficit months at Pulau Padang (KHG level, 2018-2025) against Amal (2022): January-March, June, July, worst in February | February in deficit in 6 of 8 years, July 5 of 8, January 3, March 2, June 1-2; August also 2-3 of 8 (not in Amal) | [reports/pulau_padang_deficit_months.md](reports/pulau_padang_deficit_months.md) |
| V4 | order of sub-KHG stable between years and between ET sources | Sugihan-Lumpur (30 units): years 0.65, sources 0.78, flag 1. Kahayan-Sebangau (16 units of 2021): 0.85, 0.89, flag 1. Kampar-Gaung (26 units): years 0.72, sources 0.11, flag 0 | `runs/balance*/neraca_balance.md` per KHG |
| V5 | per-unit deficit on each unit's own stations and Earth Engine P and ET (June-September 2026) against the balance indicators, units with at least 3 stations | Sugihan-Lumpur, 9 units: Spearman with u_wb_mean -0.53, with u_deficit_months +0.22, with the 2026 WB -0.98 (close to mechanical: the deficit uses the same P and ET, and the station term spans only 8 mm against 151 mm). Kampar-Gaung, 6 units: deficit 0 in every unit (positive balance), no correlation | [reports/unit_deficit_v5.md](reports/unit_deficit_v5.md) |
| Regression | station files and deficit after the bucket package was removed | byte-identical on both sites | |

From V1, for Kahayan-Sebangau: with C = 0.25 everywhere the 16 sub-KHG differ by only 49-54 mm/month on TerraClimate; the 0.25 / 0.35 split of one 2021 script moves ten of them by about 21 mm/month, so most of the 2021 differences between units came from the split.

Selected KHG (batch run, CHIRPS and WaPOR, complete years 2018-2025):

| KHG | units | mean WB (mm/month) | deficit months per year | year-to-year Spearman (median) | balance_stable_ok |
|---|---|---|---|---|---|
| Pulau Padang | KHG | 48.1 | 2.75 |  |  |
| Pulau Bengkalis | KHG | 54.5 | 2.25 |  |  |
| Pulau Tebing Tinggi | KHG | 52.5 | 3.00 |  |  |
| Sungai Saleh - Sungai Sugihan | KHG | 101.8 | 1.62 |  |  |
| Sungai Sugihan - Sungai Lumpur | 30 sub-KHG | 92.1 | 1.97 | 0.65 | 1 |
| Sungai Mendahara - Sungai Batanghari | KHG | 90.1 | 1.62 |  |  |
| Sungai Air Hitam Laut - Sungai Buntu Kecil | KHG | 81.4 | 2.12 |  |  |
| Sungai Mempawah - Sungai Peniti | KHG | 101.4 | 1.12 |  |  |
| Sungai Pungurbesar - Sungai Kapuas | KHG | 123.3 | 0.62 |  |  |
| Sungai Kahayan - Sungai Sebangau | KHG | 87.6 | 1.88 |  |  |
| Sungai Kapuas - Sungai Barito | KHG | 93.5 | 1.38 |  |  |
| Sungai Balangan - Sungai Batangalai | KHG | 91.2 | 1.62 |  |  |
| Sungai Buru Mappi - Sungai Buru Obaa | KHG | 184.0 | 0.50 |  |  |
| Sungai Kampar - Sungai Gaung (test site) | 26 sub-KHG | 83.0 | 1.83 | 0.72 | 0 |

Cawang-Lalang is not run (awaiting confirmation). KHG-level rows have no order between units to check. The KHG deficit is unchanged: Sugihan-Lumpur 290 mm (227-296), Kampar-Gaung 7 mm (0-12), 1 June to 9 October 2026.

## 7. Limits

- Water table data cover one dry season (SiTMAT, 2026). The deficit cannot be computed for other years, and the balance cannot be checked against water tables over its 2018-2025 record.
- Rain is coarse: CHIRPS has 8-24 valid pixels per Sugihan-Lumpur unit, 10-46 at Kampar-Gaung and 5-67 on the Kahayan-Sebangau 2021 units; WaPOR 378 to 14,397. Across units, mean 2018-2025 rain varies less than ET: standard deviation 5.4 mm/month for CHIRPS against 7.1 for WaPOR at Sugihan-Lumpur (4.8 and 7.3 at Kampar-Gaung). Where the two ET products disagree on the order (Kampar-Gaung), the balance does not rank the units, and the flag says so.
- With WaPOR and MOD16 interception is counted twice (section 3A). The formula is kept because the parameters are established.
- KHG without delineated units run at KHG level: 12 of the 13 selected KHG for now (only Sugihan-Lumpur has units; Kampar-Gaung is a test site outside the list).
- The stability threshold 0.5 is not agreed with the team, and neither are the weights of the ranking that will read these indicators.
- CHIRPS, WaPOR and MOD16 are revised upstream and can change between fetches; the fetched tables and their provenance files are the record.

## 8. How to run

Workspace `.venv`, `EE_PROJECT=ee-danylaksono`, `REPEAT_KHG` (the `_khg` folder), `REPEAT_DATA` (`_data`), `SITMAT_PROCESSED` (for B).

```bash
# A, a list of KHG (codes or names from re-peat/sites/khg_registry.csv), or --selected, or --all
python -m repeat_neraca.batch --selected --end 2026-10-01

# A, one KHG step by step
python -m repeat_common.fetch_gee_balance --khg 16.02.01 --products chirps,wapor,mod16 --start 2018-01-01 --end 2026-10-01
python -m repeat_neraca.balance --inputs $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/inputs --out $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/runs/balance

# B, a KHG with a site config and stations
python -m repeat_neraca.stations --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml
python scripts/run_neraca.py --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1 --classes primary,secondary,tertiary

# checks and the diagram
python scripts/check_gee_balance.py --khg 14.02-04-05.01
python scripts/reproduce_2021.py --inputs $REPEAT_KHG/62.11-14.02_kahayan_sebangau/03_neraca/inputs/units_2021 --out docs/reports/kahayan_sebangau_2021_reproduction.md
python scripts/check_forcing_2026.py --khg-dir $REPEAT_KHG/16.02.01_sugihan_lumpur --khg-dir $REPEAT_KHG/14.02-04-05.01_kampar_gaung --out docs/reports/forcing_2026_gee_vs_era5.md
python scripts/check_deficit_months.py --run $REPEAT_KHG/14.10.01_pulau_padang/03_neraca/runs/balance_khg_level --out docs/reports/pulau_padang_deficit_months.md
python scripts/check_unit_deficit.py --khg-dir $REPEAT_KHG/16.02.01_sugihan_lumpur --khg-dir $REPEAT_KHG/14.02-04-05.01_kampar_gaung --out docs/reports/unit_deficit_v5.md
python docs/figures/make_neraca_method.py
```

The Kahayan-Sebangau 2021 units are fetched with `--units users/akramsp/BatasSubKHG_KahayanSebangau --id-field SubKHG --out $REPEAT_KHG/62.11-14.02_kahayan_sebangau/03_neraca/inputs/units_2021` (and `--products terraclimate_pr,terraclimate_aet --step month --start 2010-01-01 --end 2021-01-01` for V1).

## 9. Sources

- 2021 scripts: Earth Engine repository `users/bambangkun/NDVI_DenganSentinel2`, commit `4bebab11`; [../research_notes/gee_2021_kahayan_sebangau.md](../research_notes/gee_2021_kahayan_sebangau.md).
- Runoff coefficient and Pulau Padang deficit months: [../research_notes/runoff_coefficient_pulau_padang.md](../research_notes/runoff_coefficient_pulau_padang.md) (Amal 2022, abstract; Aditya & Cahyono 2018 as cited in repeat-prioritisation).
- Deficit definition and agreed choices: [neraca-air.md](neraca-air.md).
- Datasets: Earth Engine catalogue pages for `UCSB-CHG/CHIRPS/DAILY` (Funk et al. 2015, doi 10.1038/sdata.2015.66), `FAO/WAPOR/3/L1_AETI_D`, `MODIS/061/MOD16A2GF` (doi 10.5067/MODIS/MOD16A2GF.061), `ESA/WorldCover/v200` (Zanaga et al. 2022, doi 10.5281/zenodo.7254221) and `IDAHO_EPSCOR/TERRACLIMATE` (Abatzoglou et al. 2018, doi 10.1038/sdata.2017.191), read 2026-10-26.
