# SiTMAT concession water levels and the 40 cm compliance limit

Written by `scripts/check_concession_levels.py` from `$SITMAT_PROCESSED/daily_long.csv` (2026-04-01 to 2026-10-22), unflagged daily values between -300 and +50 cm. Levels are cm, negative below the surface.

- Readings: 131,987 from 1,157 concession stations; 3,057 from 72 community stations.
- Readings at -40 cm against -41 cm: 2.5 times as many at concession stations, 1.5 at community stations.
- Concession station medians: 53% between -40 and -30 cm, 18% deeper than -40 cm, 29% shallower than -30 cm.
- Concession days equal to the day before (median station): 27%; stations with a standard deviation under 2 cm: 18%.
- Change from June to September, concession stations with both months (723), 10/25/50/75/90th percentile (cm): -42 / -18 / -6 / 0 / 3.

Share of each group's readings per 1 cm bin (per mille):

| level (cm) | concession | community |
|---|---|---|
| -20 | 9.9 | 3.6 |
| -21 | 7.7 | 4.3 |
| -22 | 9.1 | 3.9 |
| -23 | 9.2 | 4.3 |
| -24 | 12.5 | 1.6 |
| -25 | 13.6 | 3.3 |
| -26 | 11.4 | 4.6 |
| -27 | 13.3 | 6.2 |
| -28 | 16.3 | 5.6 |
| -29 | 16.5 | 4.3 |
| -30 | 23.9 | 2.0 |
| -31 | 22.2 | 2.9 |
| -32 | 27.3 | 2.9 |
| -33 | 33.3 | 5.6 |
| -34 | 37.4 | 4.6 |
| -35 | 44.7 | 6.5 |
| -36 | 47.5 | 3.6 |
| -37 | 51.8 | 5.2 |
| -38 | 60.0 | 6.9 |
| -39 | 65.0 | 5.9 |
| -40 | 64.7 | 7.2 |
| -41 | 26.3 | 4.9 |
| -42 | 20.6 | 7.2 |
| -43 | 17.8 | 5.6 |
| -44 | 14.5 | 5.6 |
| -45 | 14.0 | 5.2 |
| -46 | 11.8 | 7.2 |
| -47 | 10.8 | 5.6 |
| -48 | 11.1 | 6.5 |
| -49 | 10.4 | 5.6 |
| -50 | 9.7 | 6.5 |
| -51 | 8.1 | 9.2 |
| -52 | 7.9 | 6.2 |
| -53 | 8.3 | 6.9 |
| -54 | 7.0 | 8.5 |
| -55 | 6.5 | 5.2 |
| -56 | 4.8 | 6.2 |
| -57 | 3.8 | 4.9 |
| -58 | 3.7 | 7.2 |
| -59 | 2.8 | 7.5 |
| -60 | 3.3 | 6.5 |

Reading: concession readings pile up just inside the limit and fall off below it; community readings do not. Whether operators hold water at the limit or report it there, these readings are not independent evidence of the managed water table: a target taken from them is the 0.4 m compliance level under another name.
