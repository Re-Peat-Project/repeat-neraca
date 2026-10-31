# Supply rule candidates, 2025-11-01 to 2026-10-01

Written by `scripts/supply_rule.py` from the model's rain (CHIRPS) and ET (mod16nrt), KHG mean, mm per dekad. `trough` is the largest rise of the cumulative (ET - rain) inside the period; `window` is sum(ET - rain), floored at 0, over the period of the station deficit; `station` is the station-based deficit.

| khg                                 |   dekads |   rain_mm |   et_mm |   trough_mm | trough_from   | trough_to   | dry_window          |   dry_clim_mm |   dry_year_mm |   dry_dekads_in_year | window                   |   window_mm |   station_mm |   station_net_balance_mm (ERA5) |   stations |
|:------------------------------------|---------:|----------:|--------:|------------:|:--------------|:------------|:--------------------|--------------:|--------------:|---------------------:|:-------------------------|------------:|-------------:|--------------------------------:|-----------:|
| 15.05-07-10.01_mendahara_batanghari |       33 |    2222.2 |  1409.9 |       295.4 | 2026-07-01    | 2026-10-01  | dekad 16 of 36 + 14 |        -258.2 |         202.1 |                   12 | 2026-06-01 to 2026-10-13 |       202.1 |        119.1 |                           152.3 |         12 |
| 14.02-04-05.01_kampar_gaung         |       33 |    2027.8 |  1382.7 |       162.3 | 2026-07-11    | 2026-09-21  | dekad 16 of 36 + 14 |        -332.4 |          11.5 |                   12 | 2026-06-01 to 2026-10-09 |        11.5 |          7.1 |                            -9.3 |         78 |
| 16.02.01_sugihan_lumpur             |       33 |    2079   |  1421.2 |       376.5 | 2026-06-01    | 2026-10-01  | dekad 16 of 36 + 14 |        -212.4 |         376.5 |                   12 | 2026-06-01 to 2026-10-09 |       376.5 |        290.2 |                           306.7 |         51 |

