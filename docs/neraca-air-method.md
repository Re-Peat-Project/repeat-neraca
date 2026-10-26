# Neraca air: the method adopted

Methodological report, repeat-neraca 0.1.0, 2026-10-26. Diagram: [figures/neraca_method.drawio](figures/neraca_method.drawio) (open in draw.io or the VS Code Draw.io extension; rebuilt by `docs/figures/make_neraca_method.py`). Plan and history: [method-plan.md](method-plan.md).

## 1. What neraca air delivers

| Level | Output | Answers | Method |
|---|---|---|---|
| Sub-KHG | `u_wb_mean`, `u_deficit_months`, `p_minus_et_mean_mm` per unit, with `balance_stable_ok` | How much water the climate leaves each sub-KHG, in how many months a year it falls short, and whether the order of units can be trusted | Climatic water balance of the 2021 Kahayan-Sebangau study on Earth Engine rain and evapotranspiration (section 4A) |
| KHG | monthly calendar of the balance; `deficit_mm`, `deficit_m3` | When the KHG is in deficit; how much water the managed system supplied to hold the observed water table through the 2026 dry season | Same balance at KHG level; mass balance on the SiTMAT stations (section 4B) |

The two levels are kept apart (data contract C5, `re-peat/docs/11-data-contracts.md`). The physical groundwater model stays in the repository as a diagnostic and is not on the ranking path (section 4C).

## 2. What was added to the 2021 Earth Engine method

The starting point is the neraca air of the 2021 Kahayan-Sebangau study (Bambang Kun Cahyono and Akram Sripandam P., Earth Engine repository `users/bambangkun/NDVI_DenganSentinel2`; [research note](../research_notes/gee_2021_kahayan_sebangau.md)). Its formula and parameters are kept: `WB = P (1 - I)(1 - C) - ET` with C = 0.12 and interception by land cover, values the project takes as established.

| | 2021 method | Added in repeat-neraca |
|---|---|---|
| Rain | TerraClimate, 4.6 km, monthly, 2010-2020 | CHIRPS daily (5.6 km) to 2026-09, summed by dekad; used as the KHG mean for every sub-KHG, because CHIRPS and IMERG disagree on which sub-KHG are wetter (section 5, decision 1) |
| Evapotranspiration | TerraClimate AET, modelled | MODIS MOD16 (500 m) central, WaPOR v3 (326 m) as second source; MOD16's annual level lies within measured eddy-covariance ET for tropical peat, WaPOR and TerraClimate below it (decision 3) |
| Runoff C | 0.25 placeholder in the scripts; 0.35 for ten of 16 units in one script, without a stated reason | 0.12 (Aditya & Cahyono 2018) from the registry; the 0.25 / 0.35 split is not used. With C = 0.25 everywhere, the 2021 units differ by only 49-54 mm/month; the split moved ten of them by about 21 mm/month |
| Interception | not in the scripts (shares cited in the prioritisation code as from the same study) | Shares per WorldCover v200 class (10 m) per unit, counted on Earth Engine in 0.1° pieces |
| Spatial and time handling | charts at 2,500 m on a 4.6 km product; one month per map | Every product reduced on its own grid, never resampled; valid pixel count and time coverage per value; months and years used only when complete |
| Trust in the sub-KHG order | not tested | `balance_stable_ok`: the two ET products must agree on the order of ET, and the order must hold between years, each above the p < 0.01 level of a random order (decision 2). The ranking reads P − ET, not `u_wb_mean`, because `u_wb_mean`'s order follows forest share through the fixed interception term |
| KHG deficit | none | Water supplied from outside the rain balance in the 2026 dry season, from the observed water table at SiTMAT stations |
| Checks | none | 2021 scripts reproduced within 0.1 mm; deficit months at Pulau Padang against Amal (2022); rain against IMERG; ET against eddy covariance; per-unit deficit on stations |
| Reproducibility | Code Editor scripts with leftovers from other sites | Python package (`repeat-neraca`, four commands), any KHG from its registry code, batch over the registry, cached and resumable fetches with provenance, registry snapshot per run, tests, clean-install check |

## 3. Inputs

| Input | File or source | Grid, unit | Period | Licence | Used in |
|---|---|---|---|---|---|
| Sub-KHG units | `_khg/<khg>/02_delineation/subkhg_units.gpkg` (`unit_id`), from repeat-delineation; a KHG without them runs as one unit from `_data/batas_khg_indonesia.gpkg` | polygons | | project | A |
| Rain P | CHIRPS daily, `UCSB-CHG/CHIRPS/DAILY` | 0.05° (5.6 km), mm/day | 1981-01-01 to 2026-09-30 | public domain | A |
| Evapotranspiration, central | MODIS MOD16A2GF v061, `MODIS/061/MOD16A2GF` | 500 m, kg/m2 per 8 days, scale 0.1 | 2000 to 2025-12 | no restrictions (LP DAAC) | A |
| Evapotranspiration, second source | WaPOR v3 L1 AETI dekadal, `FAO/WAPOR/3/L1_AETI_D` | 326 m, mean mm/day of the dekad, scale 0.1 | 2018-01-01 to 2026-10-11 | free use (FAO) | A |
| Land cover | ESA WorldCover v200, `ESA/WorldCover/v200` | 10 m, classes | 2021 | CC-BY-4.0 | A (interception) |
| Rain reference (checks) | IMERG Final monthly V07, `NASA/GPM_L3/IMERG_MONTHLY_V07` | 0.1°, mm/hr | 1998 to 2025-09 | free public use (NASA) | checks |
| Water table | SiTMAT concession stations, `repeat-sitmat/sitmat_out/processed` | daily depth, cm | 2026-04-01 to 2026-10-22 | as scraped | B |
| Rain and evaporation, KHG mean | ERA5 daily through `repeat_common.forcing` (cache), or `03_neraca/inputs/forcing_daily.csv` | 0.25°, mm/day | windows of the site config | Copernicus | B |
| KHG boundary | `_khg/<khg>/00_inputs/khg.gpkg` | polygon | | SK.129/MENLHK/2017 | B |

Periods were read through the Earth Engine API; units, scales and licences from the Earth Engine catalogue pages (2026-10-26). All are catalogued with kind `cloud` in `re-peat/sites/data_catalog.csv`. SiTMAT is the only water table data (one dry season); its rain column is empty, and the workspace holds no rain gauge.

## 4. Processing

### A. Sub-KHG climatic water balance

**Step 1. Rain and ET per unit per dekad** (`repeat_common.fetch_gee_balance`, Earth Engine).

- Dekads: days 1-10, 11-20 and 21 to the end of the month. The total of a period is the sum over the source images that overlap it of (daily rate × days of overlap). The daily rate is the value × scale, divided by the image length when the value is a total (CHIRPS day, MOD16 8-day composite) and as is when it is a mean rate (WaPOR). MOD16 fill codes (above 32,700) are masked.
- Each period is the area-weighted mean per unit on the product's own grid, with the count of valid pixels and the share of the period covered.
- WorldCover class shares per unit for the interception term, counted in 0.1° pieces.
- One request per product and year, in parallel, cached in the KHG's `cache/`; `balance_<product>_dekad.json` records collection, scale, period, API version and fetch date per year.

**Step 2. Monthly balance and indicators** (`repeat-neraca-balance`).

```
WB(u, month) = P_KHG (1 - I_u) (1 - C) - ET_u          I_u = Σ_class share(u, class) × I_class
```

- `P_KHG`: area-weighted KHG mean of the month, the same for every unit (`--rain-mode unit` keeps rain per unit). `ET_u`: MOD16, with WaPOR as second source.
- A month counts when all its dekads are fully covered for both P and ET; a year when all 12 months do. Over the complete years:
  - `u_wb_mean`: mean monthly WB, mm/month; `u_deficit_months`: months with WB < 0, per year (definitions of `repeat-prioritisation/common/indicators.py`);
  - `p_minus_et_mean_mm`: P − ET without C and I; between units of a KHG this is the ET signal;
  - `wb_year_sd_mm`: spread of the yearly mean between years.
- `balance_stable_ok` = 1 when (a) MOD16 and WaPOR order the units' mean ET alike and (b) the yearly balance keeps its order (median Spearman over all pairs of complete years), each above the 99th percentile of the same statistic for a random order of the same number of units (simulated, `balance.null_quantiles`). Fewer than 5 units: empty.

### B. KHG supply deficit

**Step 3. Station files** (`repeat-neraca-stations --config re-peat/sites/<khg>/neraca.yaml`): SiTMAT stations inside the KHG with readings on at least 50 % of the window days.

**Step 4. Deficit** (`repeat-neraca-run`, `deficit.py`):

```
deficit_mm = max(0, -Σ(P - E) - Sy × Δz_obs × 10)        deficit_m3 = deficit_mm / 1000 × KHG area
```

ERA5 P and E; window 1 June to the last day with forcing (at most 31 October); `Δz_obs` is the change of the station-mean depth between the first and last 7 days. The band spans Sy 0.10-0.20.

### C. Diagnostic only

The physical model (tier 1 `lumped.py`, tier 2 `spatial.py`) reproduces the timing of the KHG-mean water table but not its level and gives every sub-KHG the same curve. It shows that the observed level is held by water from outside the rain balance. The bucket model fitted to the stations was retired on 2026-10-26 (record in `bucket_reports/`).

## 5. Decisions and their evidence

Three choices were investigated before fixing the method. Reports: [forcing_products.md](reports/forcing_products.md), [balance_design.md](reports/balance_design.md), [unit_deficit_v5.md](reports/unit_deficit_v5.md).

### Decision 1. Does the balance rank sub-KHG, and with what weight?

| Evidence | Sugihan-Lumpur (30 units) | Kampar-Gaung (26) | Kahayan-Sebangau 2021 units (16) |
|---|---|---|---|
| CHIRPS against IMERG, order of unit mean rain | −0.34 | −0.06 | |
| MOD16 against WaPOR, order of unit mean ET (99th percentile of a random order) | 0.46 (0.43) | −0.33 (0.46) | 0.50 (0.58) |
| `u_wb_mean` against forest share, KHG-mean rain, MOD16 | −0.44 | −0.07 | −0.82 |
| P − ET against forest share | 0.07 | 0.52 | 0.11 |
| Per-unit station deficit 2026 against P − ET (9 units) | 0.10 | deficit 0 in every unit | |

- Rain cannot separate sub-KHG: two products order the units differently. Rain is therefore taken as the KHG mean.
- With common rain, `u_wb_mean` follows forest share: the interception term is 6-16 % of about 240 mm/month of rain and fixed by land cover, larger than the ET differences between units (standard deviation 3-7 mm/month). P − ET does not follow forest share and carries the water signal.
- The ET products agree on the order above chance only at Sugihan-Lumpur, and barely. The 2026 station deficit does not confirm that order (Spearman 0.10 on 9 units).

Adopted: the rank-sum's water slot reads `p_minus_et_mean_mm` where `balance_stable_ok` is 1; `u_deficit_months` is not ranked; the need score gives the balance weight 0. This replaces the earlier suggestion of weight 1.0: the evidence does not support a weight.

### Decision 2. Stability threshold.

- The earlier test compared balances of two ET products that share the same rain, so the shared rain made them agree. The test now compares ET itself.
- A fixed 0.5 is not equally strict for every number of units. The thresholds are the 99th percentile for a random order: one Spearman 0.43 (30 units), 0.46 (26), 0.58 (16), 0.72 (10); median of 28 year pairs 0.11-0.16. The year test is weak: a land-cover term fixed in time keeps the order between years whatever the water does, so the ET test carries the decision.

Adopted: p < 0.01 against a random order, on ET agreement and year stability. Result: Sugihan-Lumpur 1, Kampar-Gaung 0, Kahayan-Sebangau (2021 units) 0.

### Decision 3. Forcing of the KHG deficit.

| Evidence | Sugihan-Lumpur | Kampar-Gaung |
|---|---|---|
| Rain against IMERG, 21 dry-season months 2019-2021: CHIRPS / ERA5 bias | +27 % / +18 % | +7 % / +7 % |
| ET 2018-2025, mm/yr: MOD16 / WaPOR | 1,441 / 1,180 | 1,385 / 1,101 |
| ERA5 evaporation against MOD16 / WaPOR, same months | −6 % / +17 % | +2 % / +28 % |
| Monthly correlation, ERA5 E with MOD16 | −0.11 | 0.07 |

Measured annual ET over tropical peat: 1,636, 1,553 and 1,374 mm/yr at undrained, drained and drained-burnt sites in Central Kalimantan (Hirano et al. 2015) and 1,579 mm/yr in a Sarawak peat forest (Tang et al. 2019). MOD16 (1,385-1,490 mm/yr over the three KHG) lies in that range; WaPOR (1,100-1,215) and TerraClimate (1,260 at Kahayan-Sebangau) lie below the lowest site. WaPOR in the deficit's forcing file was also stale: six dekads of 2026 (11 June to 10 August) had been replaced upstream since the file was cached on 2026-10-16.

Adopted: ERA5 stays the deficit's forcing (its evaporation total matches MOD16; its rain is as close to IMERG as CHIRPS). WaPOR is no longer a bound of the band (`wapor_bound`, off by default). This replaces the earlier suggestion to switch the deficit to CHIRPS and WaPOR: switching would have lowered ET by a quarter and the deficit with it. MOD16 becomes the central ET of the balance for the same reason.

## 6. Parameters

From the registry `src/repeat_neraca/parameters.yaml` unless stated.

| Parameter | Value | Source | Used in |
|---|---|---|---|
| Runoff coefficient C (`runoff_coefficient`) | 0.12 | Aditya & Cahyono 2018, Pulau Padang (range 0.07-0.18); taken as established | A |
| Interception I (`interception_*`) by WorldCover class | tree cover 0.164, mangroves 0.164, shrubland 0.08, herbaceous wetland 0.05, grassland 0.03, cropland 0.03, other classes 0 | Kahayan-Sebangau study 2021 (B.K. Cahyono) | A |
| Stability level (`balance.NULL_Q`) | 99th percentile of a random order | decision 2 | A |
| Rain mode, central ET | KHG mean; MOD16 | decisions 1 and 3 | A |
| Specific yield Sy | 0.15 (band 0.10-0.20) | agreed 2026-10-20 (`neraca-air.md`) | B |
| Deficit window | 1 June to last forcing day, at most 31 October | agreed 2026-10-20 | B |
| Station coverage | ≥ 50 % of window days | `repeat_common.tma` default | B |

## 7. Outputs

All in the KHG work folder, `_khg/<khg>/03_neraca/`.

| File | Content |
|---|---|
| `inputs/balance_<product>_dekad.csv` (+ `.json`) | `unit_id, start, end, days, mm, n_px, time_cov`; provenance |
| `inputs/units_landcover.csv` | `unit_id, area_km2, wc_<class>` |
| `runs/balance/neraca_balance_unit.csv` | `u_wb_mean` (mm/month), `u_deficit_months` (per year), `p_minus_et_mean_mm`, `wb_year_sd_mm`, `interception_share`, `n_px_<product>`, `wb_mean_wapor`, `deficit_months_wapor`, `n_years`, `balance_stable_ok` |
| `runs/balance/neraca_balance_monthly.csv`, `neraca_balance.md`, `registry_snapshot.json` | monthly WB per unit and ET source; report with calendar, ET order and forest share; parameters used |
| `inputs/stations.csv`, `inputs/stations_daily.csv` | SiTMAT stations, daily depth (cm, positive down) |
| `runs/deficit/neraca_khg.csv` | KHG deficit with band, volume, deficit months and evidence columns |
| `_khg/neraca_balance_summary.csv` | one row per KHG from `repeat-neraca-batch` |

The prioritisation merges `neraca_balance_unit.csv` through `extra_indicators` (section 5, decision 1); `common.pipeline.gate_balance` leaves the balance columns empty where `balance_stable_ok` is 0.

## 8. Checks and results (2026-10-26)

| Check | Result | Report |
|---|---|---|
| Period arithmetic, whole-KHG unit, balance formula and flag | pass (`repeat-common/tests`, `repeat-neraca/tests`) | |
| A period equal to one source image gives that image's value, reduced directly on its grid | max difference 5e-14 mm (WaPOR), 1e-6 mm (TerraClimate); no MOD16 fill codes in the KHG | `scripts/check_gee_balance.py` |
| WorldCover shares in 0.1° pieces against one request | identical | |
| V1: 2021 Kahayan-Sebangau scripts reproduced against their expression on Earth Engine | within 0.1 mm | [kahayan_sebangau_2021_reproduction.md](reports/kahayan_sebangau_2021_reproduction.md) |
| V2: Earth Engine P and ET against ERA5, June-September 2026 | Sugihan-Lumpur: CHIRPS 208 against ERA5 140 mm; Kampar-Gaung: WaPOR ET 384 against ERA5 E 508 mm | [forcing_2026_gee_vs_era5.md](reports/forcing_2026_gee_vs_era5.md) |
| V3: deficit months at Pulau Padang (KHG level, 2018-2025) against Amal (2022): January-March, June, July, worst February | February 6 of 8 years, July 5 of 8, January 3, March 2, June 1-2; August 2-3 (not in Amal) | [pulau_padang_deficit_months.md](reports/pulau_padang_deficit_months.md) |
| V4: order of sub-KHG (section 5) | Sugihan-Lumpur 1, Kampar-Gaung 0, Kahayan-Sebangau 2021 units 0 | [balance_design.md](reports/balance_design.md) |
| V5: per-unit station deficit against the balance (Sugihan-Lumpur, 9 units) | P − ET 0.10, `u_wb_mean` 0.32, `u_deficit_months` 0.49; no unit deficit at Kampar-Gaung | [unit_deficit_v5.md](reports/unit_deficit_v5.md) |
| Clean install outside the workspace | tests pass; balance, station and deficit outputs byte-identical | README |

Selected KHG (`repeat-neraca-batch`, KHG-mean CHIRPS rain, MOD16, complete years 2018-2025):

| KHG | units | mean WB (mm/month) | deficit months per year | year-to-year Spearman (median) | balance_stable_ok |
|---|---|---|---|---|---|
| Pulau Padang | KHG | 39.1 | 3.00 |  |  |
| Pulau Bengkalis | KHG | 27.7 | 3.50 |  |  |
| Pulau Tebing Tinggi | KHG | 40.2 | 3.88 |  |  |
| Sungai Saleh - Sungai Sugihan | KHG | 83.7 | 2.25 |  |  |
| Sungai Sugihan - Sungai Lumpur | 30 sub-KHG | 69.5 | 2.44 | 0.79 | 1 |
| Sungai Mendahara - Sungai Batanghari | KHG | 61.9 | 2.38 |  |  |
| Sungai Air Hitam Laut - Sungai Buntu Kecil | KHG | 66.9 | 2.38 |  |  |
| Sungai Mempawah - Sungai Peniti | KHG | 62.8 | 2.50 |  |  |
| Sungai Pungurbesar - Sungai Kapuas | KHG | 90.7 | 1.38 |  |  |
| Sungai Kahayan - Sungai Sebangau | KHG | 64.6 | 2.88 |  |  |
| Sungai Kapuas - Sungai Barito | KHG | 72.1 | 2.50 |  |  |
| Sungai Balangan - Sungai Batangalai | KHG | 64.7 | 2.50 |  |  |
| Sungai Buru Mappi - Sungai Buru Obaa | KHG | 164.7 | 0.62 |  |  |
| Sungai Kampar - Sungai Gaung (test site) | 26 sub-KHG | 59.2 | 2.65 | 0.67 | 0 |

Cawang-Lalang is not run (awaiting confirmation). KHG deficit, 1 June to 9 October 2026: Sugihan-Lumpur 290 mm (285-296), 1,842 million m3; Kampar-Gaung 7 mm (2-12), 50 million m3.

## 9. Limits

- Water table data cover one dry season (SiTMAT, 2026). The deficit exists for 2026 only, and the balance cannot be checked against water tables over 2018-2025.
- Within a KHG the water signal between sub-KHG is weak with open data: rain is too coarse, and the ET products agree above chance at one of three unit sets. The balance mostly informs the KHG level and comparisons between KHG.
- Interception is counted twice with satellite ET (MOD16 and WaPOR include it); the formula is kept as established, and the ranking reads P − ET.
- 12 of the 13 selected KHG have no delineated sub-KHG yet and run at KHG level.
- Products are revised upstream (WaPOR 2026 changed within ten days); the fetched tables and provenance files are the record.
- Ranking weights are provisional and not agreed with the team.

## 10. How to run

`pip install repeat-common[gee]` then `repeat-neraca[all]` (README). Environment: `EE_PROJECT=ee-danylaksono`, `REPEAT_KHG`, `REPEAT_DATA`, `REPEAT_HUB`, `SITMAT_PROCESSED` (for B).

```bash
repeat-neraca-batch --selected --end 2026-10-01                    # or --khg <codes>, or --all
repeat-neraca-balance --inputs $REPEAT_KHG/<khg>/03_neraca/inputs --out $REPEAT_KHG/<khg>/03_neraca/runs/balance
repeat-neraca-stations --config ../re-peat/sites/<khg>/neraca.yaml
repeat-neraca-run --config ../re-peat/sites/<khg>/neraca.yaml --tier 1 --classes primary,secondary,tertiary --out $REPEAT_KHG/<khg>/03_neraca/runs/deficit

# checks
python scripts/check_gee_balance.py --khg 14.02-04-05.01
python scripts/reproduce_2021.py --inputs $REPEAT_KHG/62.11-14.02_kahayan_sebangau/03_neraca/inputs/units_2021 --out docs/reports/kahayan_sebangau_2021_reproduction.md
python scripts/check_forcing_2026.py --khg-dir $REPEAT_KHG/16.02.01_sugihan_lumpur --khg-dir $REPEAT_KHG/14.02-04-05.01_kampar_gaung --out docs/reports/forcing_2026_gee_vs_era5.md
python scripts/check_forcing_products.py --khg-dir $REPEAT_KHG/16.02.01_sugihan_lumpur --khg-dir $REPEAT_KHG/14.02-04-05.01_kampar_gaung --out docs/reports/forcing_products.md
python scripts/check_balance_design.py --inputs <three input folders> --v5 docs/reports/unit_deficit_v5.csv --out docs/reports/balance_design.md
python scripts/check_deficit_months.py --run $REPEAT_KHG/14.10.01_pulau_padang/03_neraca/runs/balance_khg_level --out docs/reports/pulau_padang_deficit_months.md
python scripts/check_unit_deficit.py --khg-dir $REPEAT_KHG/16.02.01_sugihan_lumpur --khg-dir $REPEAT_KHG/14.02-04-05.01_kampar_gaung --out docs/reports/unit_deficit_v5.md
python docs/figures/make_neraca_method.py
```

IMERG for the rain check: `repeat_common.fetch_gee_balance --khg <code> --products imerg --step month --start 2018-01-01 --end 2025-10-01 --no-landcover`. The Kahayan-Sebangau 2021 units: `--units users/akramsp/BatasSubKHG_KahayanSebangau --id-field SubKHG --out $REPEAT_KHG/62.11-14.02_kahayan_sebangau/03_neraca/inputs/units_2021`.

## 11. Sources

- 2021 scripts: Earth Engine repository `users/bambangkun/NDVI_DenganSentinel2`, commit `4bebab11`; [research note](../research_notes/gee_2021_kahayan_sebangau.md).
- Runoff coefficient and Pulau Padang deficit months: [runoff_coefficient_pulau_padang.md](../research_notes/runoff_coefficient_pulau_padang.md) (Amal 2022 abstract; Aditya & Cahyono 2018 as cited in repeat-prioritisation).
- Eddy-covariance ET: Hirano, T. et al. (2015), Evapotranspiration of tropical peat swamp forests, *Global Change Biology* 21(5) ([record](https://consensus.app/papers/details/b1d60f2034725b508dd6e127e158cf65/)); Tang, A.C.I. et al. (2019), The exchange of water and energy between a tropical peat forest and the atmosphere, *Science of the Total Environment* ([record](https://consensus.app/papers/details/3de309693d475e9c9dcc1740533af632/)). Values from the abstracts, read 2026-10-26.
- Deficit definition and earlier choices: [neraca-air.md](neraca-air.md).
- Datasets: Earth Engine catalogue pages for `UCSB-CHG/CHIRPS/DAILY` (Funk et al. 2015, doi 10.1038/sdata.2015.66), `MODIS/061/MOD16A2GF` (doi 10.5067/MODIS/MOD16A2GF.061), `FAO/WAPOR/3/L1_AETI_D`, `ESA/WorldCover/v200` (Zanaga et al. 2022, doi 10.5281/zenodo.7254221), `NASA/GPM_L3/IMERG_MONTHLY_V07` (Huffman et al. 2019, doi 10.5067/GPM/IMERG/3B-MONTH/07) and `IDAHO_EPSCOR/TERRACLIMATE` (Abatzoglou et al. 2018, doi 10.1038/sdata.2017.191), read 2026-10-26.
