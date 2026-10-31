# Canals narrower than a cell: leak term against a fine grid

Written by `scripts/check_subcell_canal.py`. Parallel canals 300 and 500 m apart, level 0.8 m below flat land, peat 4 m, `tropical-large`, 90 days at 4 mm/day from saturation. Reference: 5 m grid, canal 10 m wide. At 100 m the canal runs through a cell centre, at 200 m 50 m off it. Depths on the last day.

| spacing (m) | reference land mean (cm) | grid (m) | canal | cell RMSE against the reference (cm) | bias of the land mean (cm) | land mean depth (cm) |
|---|---|---|---|---|---|---|
| 300 | 108.4 | 100 | fixed cells | 6.4 | +4.7 | 103.7 |
| 300 | 108.4 | 100 | leak k = 4 | 6.5 | -4.2 | 112.5 |
| 300 | 108.4 | 100 | leak k = 8 | 2.0 | -1.9 | 110.3 |
| 300 | 108.4 | 100 | leak k = 12 | 1.3 | -0.2 | 108.6 |
| 300 | 108.4 | 100 | leak k = 24 | 3.6 | +2.0 | 106.4 |
| 300 | 108.4 | 200 | fixed cells | 20.1 | +18.5 | 89.9 |
| 300 | 108.4 | 200 | leak k = 4 | 12.0 | -4.6 | 113.0 |
| 300 | 108.4 | 200 | leak k = 8 | 8.9 | -4.6 | 112.9 |
| 300 | 108.4 | 200 | leak k = 12 | 3.8 | -0.6 | 109.0 |
| 300 | 108.4 | 200 | leak k = 24 | 9.0 | +8.6 | 99.8 |
| 500 | 101.5 | 100 | fixed cells | 3.8 | +1.6 | 99.8 |
| 500 | 101.5 | 100 | leak k = 4 | 5.1 | +0.9 | 100.6 |
| 500 | 101.5 | 100 | leak k = 8 | 2.3 | +0.5 | 101.0 |
| 500 | 101.5 | 100 | leak k = 12 | 1.5 | +0.7 | 100.8 |
| 500 | 101.5 | 100 | leak k = 24 | 2.2 | +1.1 | 100.4 |
| 500 | 101.5 | 200 | fixed cells | 11.1 | +8.1 | 93.4 |
| 500 | 101.5 | 200 | leak k = 4 | 10.6 | +1.1 | 100.4 |
| 500 | 101.5 | 200 | leak k = 8 | 8.8 | -1.1 | 102.6 |
| 500 | 101.5 | 200 | leak k = 12 | 6.5 | -0.4 | 101.8 |
| 500 | 101.5 | 200 | leak k = 24 | 5.1 | +2.9 | 98.6 |

Bias: positive when the coarse grid is wetter than the reference. Fixed cells count at the canal level.
