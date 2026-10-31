# Outliers in the SiTMAT water-table record

Written by `scripts/check_station_outliers.py` with the screening rule of `groundwater/fieldcheck.py` (set 2026-10-29): a record is split at gaps of 7 days or more; pieces shorter than 14 days are left out; so are the first 7 days of each piece and runs of 7 or more identical values. Day-to-day jumps over 30 cm are counted, not removed. Readings are what passed SiTMAT's own QC.

National, `daily_long.csv` (2026-04-01 to 2026-10-22):

| kind | stations | readings | short pieces | settling days | stuck runs | left out | stations with a gap of 7+ days | day-to-day jumps > 30 cm |
|---|---|---|---|---|---|---|---|---|
| community | 73 | 3,167 | 223 | 343 | 166 | 732 (23%) | 38 (52%) | 62 |
| concession | 1,159 | 132,109 | 1,343 | 9,933 | 11,380 | 22,656 (17%) | 465 (40%) | 518 |

16.02.01_sugihan_lumpur, `03_neraca/inputs/stations_daily.csv` (readings above the ground: concession 0.2%):

| kind | stations | readings | short pieces | settling days | stuck runs | left out | stations with a gap of 7+ days | day-to-day jumps > 30 cm |
|---|---|---|---|---|---|---|---|---|
| concession | 51 | 10,041 | 0 | 357 | 1,874 | 2,231 (22%) | 0 (0%) | 6 |

14.02-04-05.01_kampar_gaung, `03_neraca/inputs/stations_daily.csv` (readings above the ground: concession 0.5%):

| kind | stations | readings | short pieces | settling days | stuck runs | left out | stations with a gap of 7+ days | day-to-day jumps > 30 cm |
|---|---|---|---|---|---|---|---|---|
| concession | 86 | 12,144 | 34 | 1,043 | 280 | 1,357 (11%) | 68 (79%) | 35 |

15.05-07-10.01_mendahara_batanghari, `03_neraca/inputs/model/stations_daily.csv` (readings above the ground: community 10.1%, concession 0.9%):

| kind | stations | readings | short pieces | settling days | stuck runs | left out | stations with a gap of 7+ days | day-to-day jumps > 30 cm |
|---|---|---|---|---|---|---|---|---|
| community | 9 | 603 | 27 | 63 | 15 | 105 (17%) | 9 (100%) | 21 |
| concession | 13 | 1,906 | 14 | 140 | 153 | 307 (16%) | 9 (69%) | 1 |
