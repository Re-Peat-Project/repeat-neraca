# SiTMAT concession water levels and the 40 cm compliance limit

Written by `scripts/check_concession_levels.py` from `$SITMAT_PROCESSED/daily_long.csv` (2026-04-08 to 2026-10-22), unflagged daily values between -300 and +50 cm, screened per station as the gates are (`fieldcheck.screen`, D20). Levels are cm, negative below the surface.

- Readings: 109,343 from 1,054 concession stations; 2,333 from 47 community stations.
- Readings at -40 cm against -41 cm: 2.0 times as many at concession stations, 1.4 at community stations.
- Concession station medians: 56% between -40 and -30 cm, 19% deeper than -40 cm, 25% shallower than -30 cm.
- Concession days equal to the day before (median station): 26%; stations with a standard deviation under 2 cm: 16%.
- Change from June to September, concession stations with both months (633), 10/25/50/75/90th percentile (cm): -43 / -19 / -8 / -0 / 4.

Share of each group's readings per 1 cm bin (per mille):

| level (cm) | concession | community |
|---|---|---|
| -20 | 10.6 | 3.9 |
| -21 | 8.5 | 5.6 |
| -22 | 10.0 | 4.7 |
| -23 | 10.2 | 4.3 |
| -24 | 12.9 | 2.1 |
| -25 | 14.9 | 3.0 |
| -26 | 12.7 | 5.6 |
| -27 | 14.3 | 6.9 |
| -28 | 17.2 | 6.4 |
| -29 | 17.9 | 5.1 |
| -30 | 25.1 | 2.6 |
| -31 | 23.3 | 3.9 |
| -32 | 29.4 | 1.7 |
| -33 | 35.5 | 6.4 |
| -34 | 40.3 | 3.9 |
| -35 | 44.8 | 8.6 |
| -36 | 49.9 | 4.7 |
| -37 | 54.9 | 6.0 |
| -38 | 63.4 | 8.1 |
| -39 | 65.8 | 7.7 |
| -40 | 58.4 | 8.1 |
| -41 | 28.7 | 6.0 |
| -42 | 22.7 | 9.0 |
| -43 | 19.7 | 6.4 |
| -44 | 16.0 | 6.4 |
| -45 | 14.7 | 6.0 |
| -46 | 12.0 | 7.7 |
| -47 | 11.2 | 6.4 |
| -48 | 10.7 | 6.9 |
| -49 | 9.1 | 5.6 |
| -50 | 9.3 | 7.3 |
| -51 | 7.6 | 9.4 |
| -52 | 6.9 | 6.4 |
| -53 | 7.4 | 7.3 |
| -54 | 6.4 | 9.9 |
| -55 | 5.3 | 6.0 |
| -56 | 4.5 | 7.3 |
| -57 | 3.9 | 5.6 |
| -58 | 3.7 | 7.3 |
| -59 | 2.9 | 6.9 |
| -60 | 3.1 | 6.9 |

Reading: concession readings pile up just inside the limit and fall off below it; community readings do not. Whether operators hold water at the limit or report it there, these readings are not independent evidence of the managed water table: a target taken from them is the 0.4 m compliance level under another name.
