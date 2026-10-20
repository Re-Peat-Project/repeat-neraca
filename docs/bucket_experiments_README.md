# Neraca air (water balance)

> **Experiments (2026-10-16, moved to repeat-neraca 2026-10-20).** Neraca air as a physical model (a KHG-level water table and a 2D groundwater model, no fitted parameters) is `docs/neraca-air.md` and `src/repeat_neraca/` in this repository. The package `src/repeat_neraca/bucket/` is kept as the record of the experiments below
> (bucket model fitted to stations, Sentinel-1, finer forcing, canal level per concession) and for the file interface: `python -m repeat_neraca.bucket.export_inputs`
> writes the daily forcing and the station files that the physical model (`repeat_neraca`) reads. `scripts/run_neraca.py` writes `neraca_unit.csv`, which the ranking can read through `extra_indicators`.

**Status: built and tested once, on Sungai Kampar - Sungai Gaung. It failed its own skill check (see "First test"): its outputs are not used in the ranking.**

## Definition

Neraca air is the daily balance between water supplied and water lost for the peat of a sub-KHG, and what that does to the water table. It is ours, defined from the data we can get; it is not a copy of an earlier method.

For each sub-KHG and day:

```
N(d)  = P(d) - E(d)                     daily neraca air, mm. Positive = surplus, negative = deficit
z(d)  = max( z(d-1) - (N(d) - L) / (10 * Sy) ,  0 )
```

- `P`, `E`: rain and evaporation from ERA5 (hourly, 0.25 degrees), summed over local days (WIB, UTC+7) and averaged over the sub-KHG.
- `z`: water-table depth below the surface, cm. It cannot rise above the surface (surplus runs off). It is **not** capped at the peat bottom: stations on 50 cm of peat show water tables beyond 100 cm, in the mineral soil below.
- `D`: peat depth, cm (from the peat depth raster). It enters only the storage decline: the share of the peat column that the water table has left.
- `Sy`: effective storage coefficient: how many mm of net deficit lower the water table by 1 cm (per 10). It is **not** looked up. It comes from the fit to SiTMAT stations, and being effective it absorbs drainage and local effects. It comes from concession stations only.
- `L`: drainage loss, mm/day, `L = k * c`. `c` (0 to 1) is the canal proximity of the sub-KHG, `c = exp(-d / ell)` with `d` the distance to the nearest canal. `k` is fitted too. It is kept only if it improves skill on stations that were not used for the fit; otherwise `k = 0`.
- Start: `z(0) = z0` on 1 April (the end of the wet season is assumed), fitted as one number. The months before June are spin-up; indicators use the dry months (June to October).

No forest or interception term: in this program such terms made forested units look drier and cancelled the forest indicator.

## Outputs (one row per sub-KHG, `neraca_unit.csv`)

| Column | Meaning | Higher means |
|---|---|---|
| `u_wb_daily_mean` | mean daily neraca air over the dry months, mm/day | less need |
| `u_deficit_months_dry` | dry months (Jun-Oct) whose total neraca air is negative, 0 to 5 | more need |
| `u_dry_days_mean` | mean length of runs of days with rain under 1 mm | more need |
| `u_storage_decline_pct` | share of the peat column drained at the driest point: mean over the sub-KHG of `min(z_peak, D) / D`, % | more need |
| `u_wt_peak_cm` | simulated deepest water table, cm | more need |
| `u_wt_days_gt40` | share of dry-season days with the simulated water table deeper than 40 cm (the same rule as `u_tma`) | more need |

`u_deficit_months_dry` has its own name because it counts 5 dry months, not the 12 months of `u_deficit_months`. Merging it under that name would silently change the meaning; the rank-sum method reads it through `scoring.ranksum_columns`.

The file is merged into a sub-KHG run through `extra_indicators:` (see [../subkhg/README.md](../subkhg/README.md)). A new column is scored once it has a weight; **outputs get a need-score weight only if they pass the spatial skill check below.**

## What the module can and cannot separate

Rain and evaporation come at 25 km, so `P - E` is almost the same everywhere inside a KHG. Differences between sub-KHG can then only come from peat depth, canal proximity and the sub-KHG's own cells. Two consequences:

- `u_storage_decline_pct` is, with flat forcing, mostly a rescaled 1 / peat depth. It would duplicate (with the opposite sign) the peat depth indicator of the rank-sum.
- The module is useful for the ranking only to the extent that the simulated water table reproduces **which places dry out more**, not just when the whole KHG dries out. This is why skill is measured two ways.

## How it is checked (SiTMAT stations)

Stations inside the KHG (concession kind, flagged readings dropped, at least 50% coverage), over the calibration window (1 April to the last valid ERA5 day):

- **Temporal skill:** per-station correlation of the daily simulated and observed water table. Shows whether the seasonal drawdown and its timing are right.
- **Spatial skill:** Spearman across stations of simulated against observed peak depth and days deeper than 40 cm. This is what the ranking needs. It is compared with a **no-skill baseline** (every station follows the KHG-mean observed curve) and with single covariates (peat depth alone, canal distance alone).
- **Fit and score on different stations:** `Sy`, `k` and `z0` are fitted on stations in some spatial blocks and scored on the other blocks (leave-one-block-out).

## Layout

```
repeat_neraca/bucket/
  forcing.py    ERA5 daily rain and evaporation on local days, cached per KHG window
  model.py      the water-table bucket and the sub-KHG indicators
  calibrate.py  stations, fit, spatial cross-validation, skill
  run.py        python -m repeat_neraca.bucket.run --config ...  ->  neraca_unit.csv, neraca_report.json  (--forcing-only, --calibrate-only)
  covariates.py python -m repeat_neraca.bucket.covariates --config ...  ->  what explains the station water tables
  canal_level.py python -m repeat_neraca.bucket.canal_level --config ...  ->  a canal level per concession (neraca_canal_level.md)
  sentinel1.py  python -m repeat_neraca.bucket.sentinel1 --config ...   ->  does Sentinel-1 radar tell deep from shallow stations (neraca_sentinel1.md)
```

## First test (Sungai Kampar - Sungai Gaung, 2026-10-16)

86 SiTMAT concession stations, 2026-04-01 to 2026-10-09, scored on spatial blocks left out of the fit. Steps, settings and reasons:
`re-peat/sites/kampar_gaung/README.md` (the hub); all numbers: `re-peat/sites/kampar_gaung/reports/kampar_gaung.md`.

- **Temporal skill is moderate:** median per-station correlation 0.63 with the drainage term.
- **Spatial skill is nil:** Spearman across held-out stations -0.03 (peak depth) and -0.02 (days deeper than 40 cm); the out-of-fold RMSE
  (16.5 cm) is worse than the no-skill baseline (15.3 cm). **Verdict: not usable for ranking** (also written to `neraca_report.json`,
  to the log, and to the column `neraca_skill_ok`).
- **The fit runs to the edge of every grid** (Sy 3.0 against a physical value below about 0.5, k 4.0 mm/day, z0 40 cm): the best bucket is
  nearly flat at 40 cm. The observed mean water table sits at about 40 cm (the regulatory limit) from April to August and drops to
  60-70 cm in September, which looks like managed water levels (weirs), not rain minus evaporation.
- **No simple covariate explains which stations are deepest** (Spearman 0.34 or less for peat depth, elevation, canal distance and density, river
  distance, distance to the KHG edge, NDMI, NDVI).
- **The outputs are rescaled covariates:** `u_storage_decline_pct` has a Spearman of -0.91 with mean peat depth across the 26 sub-KHG, and
  `u_wt_peak_cm` / `u_wt_days_gt40` have 0.82 / 0.68 with canal proximity (tables in `re-peat/sites/kampar_gaung/reports/kampar_gaung.md`).
- The peat depth raster has a floor at 50 cm (37% of its valid pixels), so `u_storage_decline_pct` is a mechanical 80% wherever peat is at the floor.

What a spatially useful neraca air would need: rainfall and evaporation finer than 25 km, and information on how water levels are
managed (weirs, canal blocks, concession practice). Until then it can only say when a whole KHG dries out.

## Second test: Sentinel-1 radar at the stations (2026-10-16)
Sentinel-1 RTC backscatter (VV, VH; 26 scenes per station, April-October 2026) at the 86 stations, report in
[bucket_reports/kampar_gaung_sentinel1.md](bucket_reports/kampar_gaung_sentinel1.md). It is the first thing tried here that carries a signal:
- **Within a station**, a brighter-than-usual VV scene falls on a shallower-than-usual water table (median Spearman -0.38, 84% of stations negative).
- **Across stations**, the VV minus VH ratio ranks the observed peak depth (Spearman 0.53). With whole blocks left out, a one-feature model
  has out-of-fold RMSE 20.6 cm against 24.6 cm for no skill (out-of-fold Spearman 0.44).
- **But not for the share of days deeper than 40 cm** (out-of-fold RMSE 0.37 against 0.34 for no skill), and adding the known covariates makes it worse.
- **Robustness checks:** each orbit on its own gives the same across-station Spearman (0.52 for both asc171 and des18, so viewing geometry is not the cause). Inside the WorldCover tree class (64 stations) it is 0.48, and land cover alone has no out-of-fold skill (RMSE 25.4 against 24.6 cm), so the ratio is not just telling land cover apart.
- **Concession is the larger part of it.** The SiTMAT station id starts with its concession code. Concession alone explains 64% of the variance of peak depth (10 concessions with 3+ stations), and the radar ratio separates concessions (the deepest, 109_THIP and 03_BNS, have the brightest ratio, 6.9 and 7.7 dB). Inside concessions the radar correlation drops to 0.21, and with whole concessions left out the out-of-fold RMSE is 23 against 28 cm (Spearman 0.21). So radar partly sees how a concession is managed, and much less which station inside it is deepest. 34 of the 86 stations belong to one concession.
- Limits: 4 spatial blocks only, so the out-of-fold figures are rough; WorldCover cannot separate acacia, oil palm and natural forest (most stations are "tree"), and GFW concession polygons were not used: the wood-fibre layer is licensed "View Only, Not Downloadable", and oil palm alone would miss the acacia that dominates the Kampar peninsula.
Next steps if pursued: treat the concession as the unit for management (its polygon and operating water-level target would be the missing input), then a radar wetness layer per sub-KHG as an indicator (no weight until it is checked against held-out burned area).

## Not in this version

- Lateral flow and canal outflow from the DTM and flow directions.
- Rainfall finer than 25 km (GSMaP at 10 km, or gauges) and evaporation that differs by land cover.
- Years before the baseline are not simulated (each year costs about 11 minutes of reads per KHG).

## Third test: finer rain and evaporation (2026-10-16)
`bash scripts/forcing_test.sh <khg>` then `python -m repeat_neraca.bucket.forcing_compare` (tables in `bucket_reports/*_forcing_test.md`).
- **WaPOR v3 evaporation (300 m) in place of ERA5 evaporation made the fit worse in both KHG:** out-of-fold RMSE without the drainage term 24.0 against 20.4 cm
  (Kampar-Gaung, 86 stations) and 14.2 against 11.3 cm (Sugihan-Lumpur, 51 stations); with the term 18.9 against 16.5 and 7.6 against 6.4. Neither passes (baselines 15.3 and 5.7 cm); the spatial Spearman stays near zero.
  WaPOR evaporation is lower than ERA5 (mean 3.4 against 3.9 mm/day), so the simulated water table sits shallower still. This does not show WaPOR is worse as a product, only that a
  finer evaporation field does not repair a model with no management term.
- **CHIRPS v3 rain (5 km): not done.** data.chc.ucsb.edu answered HTTP 403 to every request after a first 198-file parallel read, and still did at the time of writing. The reader now takes two files at a
  time and caches each day; once the block lifts, `bash scripts/forcing_test.sh sugihan_lumpur` (and `kampar_gaung`) completes the comparison (the WaPOR runs are rerun but cheap).
  CHIRPS final data ends 2026-09-30, so the scored window is shorter.

## Fourth test: the team's balance (rain minus evaporation) per sub-KHG (2026-10-16)
The Kahayan-Sebangau study's neraca air is `WB = P (1 - interception) (1 - runoff coefficient) - ET`, monthly, with deficit months counted; it never predicts a water table and the concession only
matters afterwards (exclusions, who manages the land). `python -m repeat_neraca.bucket.balance_compare --config ... --sources terraclimate,era5,wapor` computes it per sub-KHG for April-October of 2019-2021
from TerraClimate (4 km), ERA5 (25 km) and ERA5 rain with WaPOR evaporation (300 m). There is nothing to score it against, so the test asks whether it can separate sub-KHG at all
(tables in `bucket_reports/*_balance_compare.md`):
- **Sub-KHG differ by less than the year does.** Standard deviation across sub-KHG is 4-23 mm/month, while the KHG-wide mean changes by 22-40 mm/month between years, and the sources differ in level by 1-34 mm/month. No sub-KHG is in deficit on average over April-October with any source; deficit months per year are 1-3.
- **Sources agree in Kampar-Gaung, not in Sugihan-Lumpur.** Spearman across sub-KHG of the mean balance: TerraClimate vs ERA5 0.83 (Kampar-Gaung) but 0.12 (Sugihan-Lumpur); TerraClimate vs WaPOR 0.57 and 0.32; ERA5 vs WaPOR 0.73 and 0.78 (both use ERA5 rain).
- **The pattern is not stable.** TerraClimate's sub-KHG ranking correlates 0.05-0.13 between years in Kampar-Gaung (0.40-0.66 in Sugihan-Lumpur); ERA5 and WaPOR 0.57-0.91.
- **ERA5's spread follows its 25 km cells.** In Sugihan-Lumpur ERA5 gives a spread of 19 mm/month against 4 for TerraClimate, from sub-KHG falling in different grid cells, not from a hydrological difference. A steady pattern is not a true one.
- **Reading:** as built, the balance ranks sub-KHG weakly and not reliably; the rain field is the limit (the three sources use coarse rain). It stays useful at KHG level (which months are short of water, and how a year compares), and its weight stays 0 in the need score until a finer rain field is tested (CHIRPS is pending the server block).

## Fifth test: a canal level per concession (2026-10-16)
Idea from Taufik et al. 2019 (Ambio): drainage as a pull of the water table towards a canal level, `Sy dz/dt = (E - P) + (zc - z)/gamma`, with zc fitted **per concession** (read from the SiTMAT station id) and Sy,
gamma shared. `python -m repeat_neraca.bucket.canal_level --config ...` fits it with a constant level and with a level that changes in June, and scores it out of fold (`bucket_reports/*_canal_level.md`).
- **Knowing the canal level helps a little, a monitored neighbour helps more.** Kampar-Gaung, one station left out and its concession's level fitted on the others: RMSE 12.4 cm (seasonal level; 13.9 constant)
  against 14.6 cm for the all-station mean curve, but 10.9 cm for simply copying the mean curve of the other stations in the same concession. Sugihan-Lumpur: 6.5 cm against 5.6 and 5.5. Rain and evaporation add nothing beyond the concession's own record.
- **A new concession cannot be predicted.** With a whole concession left out (level = median of the others) there is no skill: RMSE 17.2 against 17.0 cm in Kampar-Gaung and 7.4 against 5.9 in Sugihan-Lumpur; the Spearman of peak depth across stations
  is negative in Kampar-Gaung (-0.41). Across concessions that are monitored the ranking is 0.5 (the concession levels do the work); **inside one concession the model ranks stations at about 0** (-0.66 to 0.10).
- **The fitted dry-season canal levels differ a lot between concessions in Kampar-Gaung** (28-88 cm; 03_BNS holds 88 cm, 53_MKS and 25_AAI 28 cm), and in Sugihan-Lumpur they sit at 32-36 cm from June, after 52-56 cm in April-May. Sy ends at the edge of its grid (0.5) again.
- **Reading:** the water table is set by the canal level, as the literature says, and the canal level is a management fact the weather data cannot supply. The fitted canal level per concession is itself a useful observed indicator of how drained a concession is
  (it would need concession polygons to attach to sub-KHG); as a predictor for sub-KHG without stations it fails.

## Future work (status 2026-10-16: neraca air parked, not used in the ranking)

Neraca air has no spatial skill yet, so its outputs carry no weight in the sub-KHG need score. To change that:

1. **Management information (the main gap).** Concession explains 64% of the variance of station peak depth. Needed from the concession holders or the
   data owners: concession polygons, weir and canal-block locations with their operating rules, and water-level targets. GFW wood-fibre polygons are
   view-only; oil palm polygons alone miss acacia. With these, model the water table per concession (target level plus rain-driven departures).
2. **Sentinel-1 as an indicator.** Within-station and across-station signal exists (runbook section, `neraca_sentinel1.md`). To do: more seasons
   (stations hold one season), test inside concessions with more stations, a per-sub-KHG radar wetness layer, and a check against held-out burned
   area or hotspots before giving it any weight.
3. **Finer rainfall.** WaPOR evaporation was tried and did not help (above); CHIRPS rain is pending a server block; GSMaP 0.1 degree and MOD16 (not on Planetary Computer, needs Earthdata login) are untried. Use the same block
   cross-validation and verdict gate. List in `docs/data_sources.md`.
4. **More stations and years.** 86 stations in 10 concessions (34 in one) and 4 spatial blocks make every out-of-fold figure rough. Ask SiTMAT for earlier years; with more
   blocks, validate on whole concessions.
5. **Peat depth floor.** 37% of the raster is exactly 50 cm; a better depth layer would remove the mechanical link between storage decline and depth.
6. **Outcome check of the whole ranking.** Neither neraca air nor the need score is validated against held-out burned area or hotspots (`years.validation` is empty).
7. **Other KHG.** Everything here is one KHG (71). Whether concession dominance and the radar signal hold elsewhere is unknown.

References for the definition and the tests above (the team's report, `re-peat`, and the wider peat hydrology literature): [docs/neraca_air_references.md](../docs/neraca_air_references.md).
