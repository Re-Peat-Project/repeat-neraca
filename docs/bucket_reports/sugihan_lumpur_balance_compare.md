# Neraca air as a rain minus evaporation balance, KHG 16.02.01: 28 sub-KHG

Monthly balance `P x (1 - interception) x (1 - runoff coefficient) - ET` for months 4 to 10 of 2019, 2020, 2021 (method and sources in `neracaair/balance_compare.py`). Sources: terraclimate, era5, wapor.
## 1. How much sub-KHG differ, and how much the sources differ

| source | KHG mean balance (mm/month) | sub-KHG min | median | max | std across sub-KHG | share of sub-KHG in deficit | deficit months per year: min / max |
|---|---|---|---|---|---|---|---|
| terraclimate | 36.1 | 28.9 | 37.1 | 43.2 | 4.32 | 0% | 2.3 / 2.7 |
| era5 | 37.2 | 11.3 | 35.2 | 98.8 | 19.39 | 0% | 2.0 / 3.3 |
| wapor | 54.2 | 12.8 | 54.4 | 115.7 | 22.81 | 0% | 1.7 / 3.3 |

Offset of the KHG mean from `terraclimate`: era5 +1.1 mm/month; wapor +18.1 mm/month.

## 2. Do the sources rank the sub-KHG the same way?

| pair | rho of mean balance | rho of deficit months |
|---|---|---|
| terraclimate vs era5 | 0.12 | 0.06 |
| terraclimate vs wapor | 0.32 | 0.12 |
| era5 vs wapor | 0.78 | 0.41 |

## 3. Is the pattern stable from year to year?

| source | years | rho of the sub-KHG means between years (min over pairs) | median | std of the KHG mean between years (mm/month) | std across sub-KHG (mm/month) |
|---|---|---|---|---|---|
| terraclimate | 2019, 2020, 2021 | 0.40 | 0.66 | 31.4 | 4.32 |
| era5 | 2019, 2020, 2021 | 0.79 | 0.91 | 34.0 | 19.39 |
| wapor | 2019, 2020, 2021 | 0.76 | 0.79 | 39.6 | 22.81 |
