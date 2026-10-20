# Neraca air as a rain minus evaporation balance, KHG 71: 26 sub-KHG

Monthly balance `P x (1 - interception) x (1 - runoff coefficient) - ET` for months 4 to 10 of 2019, 2020, 2021 (method and sources in `neracaair/balance_compare.py`). Sources: terraclimate, era5, wapor.
## 1. How much sub-KHG differ, and how much the sources differ

| source | KHG mean balance (mm/month) | sub-KHG min | median | max | std across sub-KHG | share of sub-KHG in deficit | deficit months per year: min / max |
|---|---|---|---|---|---|---|---|
| terraclimate | 37.8 | 17.1 | 39.3 | 54.9 | 9.73 | 0% | 1.0 / 2.3 |
| era5 | 44.8 | 22.1 | 45.5 | 74.5 | 11.67 | 0% | 1.0 / 2.3 |
| wapor | 71.3 | 37.2 | 71.7 | 110.3 | 16.97 | 0% | 0.7 / 1.3 |

Offset of the KHG mean from `terraclimate`: era5 +7.0 mm/month; wapor +33.5 mm/month.

## 2. Do the sources rank the sub-KHG the same way?

| pair | rho of mean balance | rho of deficit months |
|---|---|---|
| terraclimate vs era5 | 0.83 | 0.81 |
| terraclimate vs wapor | 0.57 | 0.47 |
| era5 vs wapor | 0.73 | 0.25 |

## 3. Is the pattern stable from year to year?

| source | years | rho of the sub-KHG means between years (min over pairs) | median | std of the KHG mean between years (mm/month) | std across sub-KHG (mm/month) |
|---|---|---|---|---|---|
| terraclimate | 2019, 2020, 2021 | 0.05 | 0.13 | 22.5 | 9.73 |
| era5 | 2019, 2020, 2021 | 0.57 | 0.67 | 28.2 | 11.67 |
| wapor | 2019, 2020, 2021 | 0.58 | 0.74 | 31.1 | 16.97 |
