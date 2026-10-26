# Neraca air: plan to finalise the method

> **Status 2026-10-26: done.** The adopted method, the three decisions and their evidence are in [neraca-air-method.md](neraca-air-method.md) (sections 2 and 5). The open choices of section 4 below were settled there: C and interception as established; rain as KHG mean; MOD16 as central ET; stability tested against a random order at p < 0.01 on ET agreement and year stability; ERA5 kept for the deficit, WaPOR bound off. This plan is kept as the record of how the method was reached.

Draft for the team, 2026-10-26. Sources: the 2021 Kahayan-Sebangau Earth Engine scripts ([research_notes/gee_2021_kahayan_sebangau.md](../research_notes/gee_2021_kahayan_sebangau.md)), a review of those scripts done in an earlier chat (claims from it that were not checked are marked *not checked*), the results so far ([neraca-air.md](neraca-air.md), [bucket_reports/](bucket_reports/)) and the earlier plan in `../neraca_air_recap.md`.

## 1. Where the method stands

| Line of work | Output | Result so far |
|---|---|---|
| KHG deficit (`deficit.py`) | Water the managed system supplies to hold the observed water table, June to October: `max(0, -Σ(P - E) - Sy Δz_obs)` | Works. Sugihan-Lumpur 290 mm (227-296), Kampar-Gaung 7 mm (0-12). 2026 only, since the SiTMAT stations cover only 2026 |
| Physical model, tiers 1 and 2 | Water table from P - ET, canals as drains | Timing right at KHG level, amplitude wrong. Every cell follows the same curve, so per sub-KHG `neraca_skill_ok = 0` |
| Climatic balance per sub-KHG (the 2021 method) | `WB = P (1 - I) (1 - C) - ET`, monthly, in `repeat-prioritisation/src/repeat_prioritisation/common/indicators.py` and `bucket/balance_compare.py` | Tested on 2019-2021. The sub-KHG order depends on the source (TerraClimate against ERA5, ρ = 0.12 at Sugihan-Lumpur). TerraClimate's order changes from year to year at Kampar-Gaung (median ρ 0.13); ERA5 and WaPOR hold better (median ρ 0.67-0.91) |

The third line descends from the 2021 scripts, which compute `pr - aet/10 - C pr` on TerraClimate with C = 0.25. One script uses 0.35 for ten of the sixteen sub-KHG, with no reason given. Two upgrades suggested in the review already exist here: storage converted to water table through Sy (tier 1, `deficit.py`), and a canal outflow term (tiers 1 and 2).

Still missing: a per-sub-KHG signal that holds up across years.

## 2. Proposed final method

Two outputs, kept apart as in data contract C5.

**KHG level: supply deficit.** `deficit.py` with its definition unchanged. Two proposed changes, both needing team agreement:

- Read P and ET from the Earth Engine series of section 3, so the deficit and the sub-KHG balance use the same forcing. This reverses the choice of 2026-10-20 (ERA5 evaporation as the central value, WaPOR as the other bound). If the team keeps ERA5 central, the GEE series adds a second rain source and nothing else changes.
- Compute the same deficit for each sub-KHG that holds enough SiTMAT stations, from its own stations and forcing. That would be the first per-unit deficit resting on observations.

**Sub-KHG level: climatic water balance calendar.** The 2021 method with Bambang's parameters, which are taken as established (decided 2026-10-26):

```
WB_u,t = P_u,t (1 - I_u) (1 - C) - ET_u,t        C = 0.12, I_u = interception share of the unit's land cover (0 % open land to 16.4 % forest)
```

These are the values already in `repeat-prioritisation/src/repeat_prioritisation/common/pipeline.py`. C = 0.12 is the measured Pulau Padang value (Aditya & Cahyono 2018); the 2021 scripts' 0.25 was a placeholder by their own comment ("bisa diganti jika tahu nilai C"). P - ET is written beside WB.

for each sub-KHG `u` and dekad `t` over several years, summarised as a monthly calendar of surplus and deficit. The ranking indicators are dry-season cumulative WB and the number of deficit months, as a climatology over all years with their year-to-year spread. They enter the ranking only if they pass the stability check V4 (section 5).

The physical tiers remain a diagnostic of why the observed water table stays up (supply, canal level). They stay off the ranking path until a supply term exists (`neraca-air.md`, "Not done yet", item 2).

National stage 3 (`repeat-prioritisation/src/repeat_prioritisation/national/stage3.py`) uses the TerraClimate deficit and rain, which end in 2024-12. Moving it to the same series is a separate decision. It covers 865 KHG, so it runs as a per-KHG reduction, and `scripts/check_era5_vs_terraclimate.py` shows how such a comparison was done before.

## 3. Data, all through Earth Engine

Periods and grids read through the Earth Engine API on 2026-10-26 (project `ee-danylaksono`); units and scales from the GEE catalogue pages, read the same day.

| Term | Product | Grid | Period on GEE | Units, scale | Role |
|---|---|---|---|---|---|
| P | CHIRPS daily, `UCSB-CHG/CHIRPS/DAILY` | 0.05° (5.6 km) | 1981-01-01 to 2026-09-30 | mm/day | central |
| P | IMERG V07, `NASA/GPM_L3/IMERG_V07` | 0.1° | 1998 to 2026-10-23 | | second source, latest weeks |
| P, ET | ERA5-Land daily, `ECMWF/ERA5_LAND/DAILY_AGGR` | 0.1° | 1950 to 2026-10-13 | | continuity with the current ERA5 forcing |
| ET | WaPOR v3 L1 AETI dekadal, `FAO/WAPOR/3/L1_AETI_D` | 326 m | 2018-01-01 to 2026-10-11 | mean mm/day over the dekad, scale 0.1 | central |
| ET | MOD16A2 v061, `MODIS/061/MOD16A2` (gap-filled `MOD16A2GF` to 2025-12) | 500 m, 8-day | 2021 to 2026-09-30; GF from 2000 | 8-day sum, kg/m2/8day, scale 0.1 | second source |
| P, ET | TerraClimate, `IDAHO_EPSCOR/TERRACLIMATE` | 4.6 km, monthly | to 2024-12 | `aet` scale 0.1 | reproducing 2021 only; it does not reach the 2026 stations |

- **Interception and WaPOR.** The catalogue defines AETI as "the sum of the soil evaporation (E), canopy transpiration (T), and evaporation from rainfall intercepted by leaves (I)", so with WaPOR the `(1 - I)` term overlaps with ET. The established formula is kept as it is; the overlap is stated in the report, and P - ET is written beside WB so the size of the term is visible.
- **Time step:** the dekad, WaPOR's own. WaPOR dekad total = value × 0.1 × days in the dekad (the catalogue page gives "mm/day" in the description and "mm" in the band table; the description is taken). CHIRPS days are summed to dekads. MOD16 8-day sums are spread evenly over their days, and the last composite of a year is 5 or 6 days. Months for the calendar.
- **Period:** 2018 (start of WaPOR v3) to the latest dekad. That covers the 2019 and 2023 dry seasons and the 2026 station window.
- **Resolution:** each product is reduced on its own grid, never resampled to fit, and the extractor reports the pixel count per sub-KHG and product. At 5.6 km rain may vary little inside a KHG, which would leave ET to make most of the contrast between sub-KHG. The coarse ERA5 grid still gave a 19 mm/month spread at Sugihan-Lumpur, so V4 tests this with the pixel counts. The smallest Kahayan-Sebangau unit (35 km2) holds about one CHIRPS pixel.
- **Rain check** against station rain where `repeat_common.fetch_metar` has it. Bias correction only if the check shows a bias.

## 4. Open choices

| Item | Values in play | Plan |
|---|---|---|
| Runoff coefficient C, interception | settled: Bambang's C = 0.12 and interception by land cover (section 2) | none |
| Water table data | settled: SiTMAT scrape only (`repeat-sitmat`, 2026-04-01 to 2026-10-22, 1,283 stations); no new data unless the project owner adds it | every station-based check is one dry season |
| ET product | WaPOR v3, MOD16, ERA5-Land | V2 and V4; WaPOR central unless V4 says otherwise |
| Stability threshold for the sub-KHG balance to enter the ranking | none set | Proposed: median year-to-year Spearman ≥ 0.5 and agreement between sources at ρ ≥ 0.5. For the team to set |

## 5. Validation

| Step | Check | Data |
|---|---|---|
| V1 | Reproduce the 2021 Kahayan-Sebangau chart from Python (TerraClimate, C = 0.25, 16 sub-KHG) | `users/akramsp/BatasSubKHG_KahayanSebangau` |
| V2 | KHG-mean P - E from the GEE series for 2026-06-01 to 2026-10-09 against the ERA5 values in `deficit.py` (Sugihan-Lumpur -307 mm, Kampar-Gaung +9 mm) | existing `forcing_daily.csv` |
| V3 | Deficit months at Pulau Padang against Amal (2022): January to March, June, July, worst in February in the north | Pulau Padang sub-KHG |
| V4 | `balance_compare` criteria on the GEE series, 2018 to now: spread across sub-KHG against spread across sources, agreement between sources, year-to-year stability | selected KHG with sub-KHG units |
| V5 | Per-sub-KHG deficit against the sub-KHG balance where a unit has stations: does a unit with a larger climatic deficit need more supply? | SiTMAT 2026 |

## 6. Build steps

1. `repeat_common.fetch_gee_balance`: per sub-KHG dekadal P and ET for each product above, with pixel counts, written to `_khg/<code>_<name>/03_neraca/inputs/balance_<product>_dekad.csv`. Catalogue entries of kind `cloud`. Sub-KHG polygons from `02_delineation/subkhg_units.gpkg`; the 2021 assets only for V1.
2. V1 and V2.
3. `deficit.py` reads the new forcing (if agreed); per-sub-KHG deficit where stations allow.
4. Climatology and indicators in `repeat_neraca`, written to `neraca_unit.csv` as new columns (for example `u_wb_dry_mm`, `u_deficit_months`, `u_wb_spread_mm`), with data contract C5 updated in the hub. `repeat-prioritisation` then reads these in place of its own balance in `indicators.py`, so sub-KHG ranking and neraca use the same numbers.
5. V3 to V5 on the selected KHG, reported in `docs/reports/`.

## 7. Recap items proposed for removal

Nothing removed yet; confirm first.

| Recap item | Reason |
|---|---|
| spateGAN-ERA5 rain (§2a), CorrDiff (§4), N3 ensemble neraca | Heavy machinery, against the lean-scope rule in `AGENTS.md`. CHIRPS and IMERG on GEE cover the need |
| WeatherNext 2 forecasts (§2a) | Operational forecasting is outside this module's prioritisation role |
| Copernicus CLMS ET (§2b), GLEAM4 | WaPOR v3 is on GEE at 326 m to October 2026; GLEAM is too coarse for sub-KHG (the recap says so) |
| KLH TMAT, SiMATAG, village loggers, archived SIPALAGA, Batanghari/Kubu Raya dataset, Amal (2022) full text (§2c, §6) | No new data comes in; water table data are the SiTMAT scrape only |
| N4, N5 (data assimilation, LSTM residual), N7 | Need longer station records than one season, or new data |
| Variable C (by class, by antecedent water table, §3.4) | C = 0.12 is established |

Kept for later, not removed:

- **Sentinel-1 water table proxy (§2d).** Results are mixed. Within a station, brighter radar falls on shallower days (median ρ -0.62 at Sugihan-Lumpur, -0.38 at Kampar-Gaung). Across stations it passed the screen only at Kampar-Gaung (ρ 0.53, against 0.17 at Sugihan-Lumpur). See `bucket_reports/*_sentinel1.md`.
- **N1, N2 (block-state runoff, graph routing).** They depend on a canal and supply term the physical model does not have yet.

## 8. Finalising the repository

Status 2026-10-26: the bucket package is retired, the GEE fetcher, `balance.py` and `stations.py` are built (items 1 and the moves below are done; steps 2 to 7 remain).

**Retire the bucket package (`src/repeat_neraca/bucket/`).** It fitted a drainage coefficient to the stations and failed its spatial skill check; the Sentinel-1, canal-level and covariate studies were side tests. Its reports stay in `docs/bucket_reports/`; the committed code is in git history, and the uncommitted edits it carried at removal (path renames in docstrings and `forcing_compare.py`) are kept as `docs/bucket_reports/bucket_uncommitted_edits_2026-10-26.patch`. Checks after the move: `stations.py` writes station files byte-identical to the old ones on both sites; `run_neraca.py` tier 1 gives byte-identical `neraca_khg.csv` and `tier1_series.csv` (the report differs only in the registry hash, which changed when C and the interception values were added). Two pieces were still in use and moved:

| Piece | Used by | Goes to |
|---|---|---|
| `balance_compare.py` (the 2021 balance per sub-KHG, its interception per WorldCover class, the stability checks) | becomes the sub-KHG balance and check V4 | `src/repeat_neraca/balance.py`, reading the GEE series |
| `export_inputs.py` station part (`stations.csv`, `stations_daily.csv`) | the deficit and tiers 1-2 | `src/repeat_neraca/stations.py`, reading `repeat-sitmat` output through `repeat_common.tma` |
| `export_inputs.py` forcing part (`forcing_daily.csv`, ERA5 via cache) | the deficit and tiers 1-2 | replaced by `repeat_common.fetch_gee_balance` |

Then remove: `bucket/` (13 modules), `tests/test_canal_level.py`, `test_neraca_model.py`, `test_sentinel1.py`, the `experiments` extra in `pyproject.toml`, the `neraca_experiments.yaml` site configs, and the bucket inputs of `repeat-prioritisation/src/repeat_prioritisation/subkhg/report.py` (it reads `neraca_report.json`, `neraca_covariates.md` and `neraca_calibration.png` from the bucket run). The Sentinel-1 study stays documented in its report for later.

**Physical tiers 1 and 2:** keep, frozen, as the diagnostic behind the deficit (why the water table is held). No further development without a supply term, and that term cannot be checked with one season of stations.

**Remaining work, in order:**

1. GEE extractor (`repeat_common.fetch_gee_balance`) and the moves above.
2. Sub-KHG units for the selected KHG: only Kampar-Gaung and Sugihan-Lumpur have `02_delineation/subkhg_units.gpkg`. For Kahayan-Sebangau the 16 units of 2021 (`users/akramsp/BatasSubKHG_KahayanSebangau`) can serve until `repeat-delineation` has run, and then serve as a reference to compare our delineation and balance against (research note, "Use for comparison").
3. V1 to V5.
4. *(Done 2026-10-26.)* `neraca_balance_unit.csv` in C5; `repeat-prioritisation` merges it through `extra_indicators`, maps the rank-sum's water-balance slots to it and blanks it where `balance_stable_ok` is 0. Need-score weights stay 0 (team decision).
5. One runner (`scripts/run_neraca.py`) that writes `neraca_khg.csv` and `neraca_unit.csv` per KHG into `_khg/<code>_<name>/03_neraca/runs/`.
6. README, `neraca-air.md` and the recap rewritten to the final method; the recap's removed items deleted.
7. QGIS Processing wrapper (recap target), after the above.

## 9. Running for any KHG (requirement of 2026-10-26)

The method must extend from the selected KHG to every KHG in Indonesia without hand steps.

Done:
- `python -m repeat_neraca.batch --selected | --khg <codes> | --all` runs the fetch and the balance per KHG from the registry code alone. A KHG without sub-KHG units runs as one unit from `batas_khg_indonesia.gpkg` (`fetch_gee_balance --whole-khg`), so every KHG gets a calendar and KHG-level indicators.
- Fetches are one request per product-year, cached in the KHG's `cache/`, run in parallel; WorldCover shares are counted in 0.1° pieces, so large units do not time out. A failing KHG is logged and skipped. One summary table, `_khg/neraca_balance_summary.csv`.
- Each fetched table has a provenance `.json` (collection, scale, period, API version, fetch date per year); each balance run a `registry_snapshot.json`.

Still needed for all 865:
- Sub-KHG units: `repeat-delineation` has to run per KHG (until then the KHG-level fallback).
- Boundaries: all 865 KHG of the registry are in `batas_khg_indonesia.gpkg` (checked 2026-10-26), so `--all` does not fail on them. KHG set after SK.129/2017 (for example Maluka-Martapura, SK.270/2022) are not in the registry at all; adding one needs a registry row and its boundary from `_data/klhk_khg_feg_50k.gpkg`.
- The KHG deficit needs SiTMAT stations and a site config; only KHG with stations can have it.
- Time and quota: a KHG-level fetch took about a minute with 9 workers (Pulau Bengkalis, 27 product-year requests plus land cover), so `--all` is roughly 14 hours and 865 × 27 requests. The batch resumes from its cache, so it can run in chunks (`--khg` with part of the registry).

## Sources

- Results and earlier choices: [neraca-air.md](neraca-air.md), [bucket_reports/sugihan_lumpur_balance_compare.md](bucket_reports/sugihan_lumpur_balance_compare.md), [bucket_reports/kampar_gaung_balance_compare.md](bucket_reports/kampar_gaung_balance_compare.md), [bucket_reports/sugihan_lumpur_sentinel1.md](bucket_reports/sugihan_lumpur_sentinel1.md), [bucket_reports/kampar_gaung_sentinel1.md](bucket_reports/kampar_gaung_sentinel1.md), [research_notes/runoff_coefficient_pulau_padang.md](../research_notes/runoff_coefficient_pulau_padang.md).
- Periods and grids: Earth Engine API, 2026-10-26. Units, scales and the AETI definition: GEE catalogue pages for `FAO_WAPOR_3_L1_AETI_D`, `IDAHO_EPSCOR_TERRACLIMATE` and `MODIS_061_MOD16A2`, read 2026-10-26.
- From the review, *not checked*: Hirano et al. (2015) eddy-covariance ET in Central Kalimantan as an ET check; Wösten et al. (2008), water table between -40 cm and +100 cm; Mu et al. (2011) for MOD16; Funk et al. (2015) for CHIRPS.
