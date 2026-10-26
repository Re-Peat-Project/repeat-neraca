# 2021 neraca air scripts, KHG Kahayan-Sebangau (Earth Engine)

Recorded 2026-10-26 from the Earth Engine script repository shared by Bambang Kun Cahyono (lead of the 2021 Kahayan-Sebangau project):
`https://earthengine.googlesource.com/users/bambangkun/NDVI_DenganSentinel2`, read at commit `4bebab11c4c4e862b2768ebf868281f75605d016`. How to clone it from this workspace: `AGENTS.md`, Environment. A clone at that commit is kept, outside git, in `_data/raw/gee_bambangkun_NDVI_DenganSentinel2/`; the scripts are not copied into this repository.

## Scripts

| Script | Created | Authors in header | Domain | What it computes |
|---|---|---|---|---|
| `NeracaAir_KahayanSebangau` | 2021-09-27 | none (header says "KHG Pulau Padang") | whole KHG, `users/bambangkun/BatasKHG_KahayanSebangau` | `WB = P - aet/10 - 0.25 P`, monthly 2010-2020, chart per KHG, map of one month |
| `Pelatihan_NeracaAir_KahayanSebangau` | 2021-11-26 | Bambang Kun Cahyono, Akram Sripandam P | whole KHG | same as above (training copy) |
| `Pelatihan_NeracaAir_KahayanSebangau2` | 2021-11-26 | same | whole KHG | same balance, charts only |
| `Pelatihan_HujanHarian_KahayanSebangau` | 2021-11-26 | same | whole KHG | CHIRPS daily rain, 2021-01-01 to 2021-08-31, KHG-mean chart |
| `Akram_NeracaAir_1` | 2021-12-17 | BKC, TAD, ASP | 16 sub-KHG, `users/akramsp/BatasSubKHG_KahayanSebangau` | same balance, one chart series per sub-KHG |
| `Akram_NeracaAir_2` | 2021-12-17 | none (header says "KHG Tebing Tinggi Pulau Padang") | 16 sub-KHG, `users/akramsp/SubKHG_<n>_KS` | balance with C = 0.25 or 0.35 per sub-KHG (table below), area chart per sub-KHG, map with a date slider |
| `Akram_NeracaAir_3` | 2021-12-17 | BKC, TAD, ASP | 16 sub-KHG | balance with C = 0.25, maps of 2019 and 2020 means |

All use TerraClimate (`IDAHO_EPSCOR/TERRACLIMATE`) bands `pr`, `aet` and `ro`, 2010-2020. The other scripts in the repository (NDVI, NDMI, tasselled cap, LULC, biomass) are not about the water balance.

## The balance as written

```
WB = pr - aet/10 - C x pr        C = 0.25 (all scripts), or 0.25 / 0.35 per sub-KHG (Akram_NeracaAir_2)
```

- The TerraClimate `ro` band is loaded and passed to the expression but not used in it. Runoff is the constant share `C x pr`. The code comment: "nilai 0.25 bisa diganti jika tahu nilai C berdasarkan data P dan Delta S".
- `aet` is divided by 10 in the balance, which matches the catalogue (`aet` scale 0.1, mm; `pr` and `ro` in mm with no scale; 4,638.3 m pixels; GEE catalogue page read 2026-10-26). The ET chart plots the raw band with the axis label "ET (0.1 * mm)".
- The catalogue warns: "TerraClimate should not be used directly for independent assessments of trends."
- No interception term. The interception shares now in `repeat-prioritisation/common/pipeline.py` (0 to 16.4 %, cited there as "Kahayan-Sebangau study, 2021") are not in these scripts.
- The monthly loop sums the images of each calendar month; TerraClimate is monthly, so each sum holds one image.
- Charts reduce at 2,500 m (`seriesByRegion`) or at the default scale (`ui.Chart.image.series`); TerraClimate is about 4.6 km.

`Akram_NeracaAir_2`, runoff coefficient per sub-KHG as written in the chart code (no basis given in the script; both versions are also shown as map layers for every sub-KHG):

| C | sub-KHG |
|---|---|
| 0.35 | 1, 2, 4, 8, 11, 12, 13, 14, 15, 16 |
| 0.25 | 3, 5, 6, 7, 9, 10 |

## Leftovers and slips

- Headers name KHG Pulau Padang (`NeracaAir_KahayanSebangau`) and KHG Tebing Tinggi Pulau Padang (`Akram_NeracaAir_2`); `Akram_NeracaAir_2` names the merged collection `mempawah` and its boundary layer "Batas Sub KHG Mempawah". Export names say `PulauPadang`. The scripts were adapted from other sites.
- `NeracaAir_KahayanSebangau` maps the image of `filterDate('2020-08-01')` under the layer name "neraca air Jan 2019". The single-date filter works only because it equals the image timestamp.
- `Akram_NeracaAir_3` maps the 2019-01 mean under the name "WB mean Jan 20", and maps the TerraClimate `ro` band while its charts show `C x pr` as runoff.
- `system:time_start` is set to an `ee.Date`, not milliseconds.

## Assets (checked 2026-10-26 with project `ee-danylaksono`)

| Asset | Readable | Content |
|---|---|---|
| `users/bambangkun/BatasKHG_KahayanSebangau` | no ("not found") | KHG boundary |
| `users/akramsp/BatasSubKHG_KahayanSebangau` | yes | 16 polygons, fields `SubKHG` (`SubKHG_1` to `SubKHG_16`), `Id` |
| `users/akramsp/SubKHG_1_KS` ... `SubKHG_16_KS` | yes (1 and 16 tested) | one polygon each, fields `SubKHG`, `Id`, `Shape_Area`, `Shape_Leng` |

The 16 polygons span 113.58-114.28 E, 3.47-2.17 S, 4,523 km2 in total (registry: KHG Sungai Kahayan - Sungai Sebangau, 451,507 ha), so they are Kahayan-Sebangau despite the leftover names. Unit areas range from 35 km2 to 1,496 km2; the smallest covers under two TerraClimate pixels.

## Use for comparison

The 16 sub-KHG of `users/akramsp/BatasSubKHG_KahayanSebangau` may serve as a reference for our own output: once `repeat-delineation` has run on Kahayan-Sebangau, compare its sub-KHG with these (overlap, boundaries) and compare the balance indicators on both unit sets. Until then they stand in as the Kahayan-Sebangau units (`_khg/62.11-14.02_kahayan_sebangau/03_neraca/inputs/units_2021/`, `runs/balance_units_2021/`).

## Open points (not pursued)

Bambang's parameters (C = 0.12, interception by land cover) are taken as established (decided 2026-10-26), so these stay as provenance gaps only:

1. Where do C = 0.25 and 0.35 come from, and why does each sub-KHG get the value it does?
2. The team's C = 0.12 (range 0.07-0.18) is cited in `repeat-prioritisation/common/pipeline.py` as measured on Pulau Padang, "Aditya & Cahyono 2018". Is there a report or thesis with the measurement, and over what period and land cover?
3. Where do the interception shares (0 % open land to 16.4 % forest) come from?
4. Were the 16 sub-KHG delineated by a documented rule (elevation, canals, hydrology)?
