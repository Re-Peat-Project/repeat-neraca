# Canal levels in the LiDAR DTM, KHG 14.10.01

Written by `scripts/check_lidar_canal_levels.py` from `DTM_2mFloat.tif` (2 m, flown November 2016) and the KHG's mapped canals. Depths are m below the land (transect median), window ±10 m around the line.

| class | transects | at the line: 25th / median / 75th percentile (m) | control at 100 m, median (m) | lowest point at the line | chance |
|---|---|---|---|---|---|
| Kanal Primer | 416 | 0.31 / 0.80 / 1.30 | 0.06 | 46% | 7% |
| Kanal Sekunder | 593 | 0.13 / 0.32 / 0.75 | 0.05 | 44% | 7% |
| Kanal Tersier | 2372 | 0.08 / 0.24 / 0.65 | 0.06 | 35% | 7% |

The value at the line is the canal water level on the flight date, or a shallower bound where the DTM interpolates over water. Transects where the mapped line misses the canal by more than the window dilute the median towards the control.
