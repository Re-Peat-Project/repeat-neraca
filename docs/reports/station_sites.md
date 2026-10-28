# KHG as test sites for the groundwater model, by their SiTMAT stations

`python scripts/rank_station_sites.py --out docs/reports/station_sites.md`. 1181 stations inside 178 KHG; good stations: concession with at least 120 unflagged days, community with at least 45 (community records start later). Dry window 2026-06-01,2026-09-30. Full table: `station_sites.csv`. LiDAR and sub-KHG units are known only for KHG with a hub site folder or a work folder ('?' otherwise).

## Top 20 by number of good stations

| KHG | code | selected | good concession | good community | groups | level mean (cm) | level spread (cm) | dry drawdown median (cm) | dry drawdown spread (cm) | LiDAR | sub-KHG units |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Sungai Kampar - Sungai Gaung | 14.02-04-05.01 |  | 78 | 0 | 9 | 43.0 | 11.0 | 7.0 | 20.7 | yes | yes |
| Sungai Sugihan - Sungai Lumpur | 16.02.01 | yes | 51 | 0 | 3 | 43.0 | 3.1 | 11.0 | 2.8 | yes | yes |
| Sungai Rokan - Sungai Siak Kecil | 14.03-07-12.01 |  | 51 | 0 | 7 | 40.0 | 2.3 | -2.0 | 6.5 | ? | ? |
| Sungai Siak - Sungai Kampar | 14.05-08.01 |  | 37 | 1 | 16 | 37.0 | 19.5 | -1.0 | 9.0 | ? | ? |
| Sungai Mendahara - Sungai Batanghari | 15.05-07-10.01 | yes | 12 | 9 | 6 | 34.0 | 12.7 | 1.0 | 12.8 | yes | yes |
| Sungai Batanghari - Sungai Air Hitam Laut | 15.05-07.01 |  | 17 | 2 | 10 | 43.0 | 35.2 | 10.0 | 19.8 | ? | ? |
| Sungai Terentang - Sungai Kapuas | 61.12.07 |  | 18 | 0 | 3 | 33.0 | 4.5 | 4.0 | 9.9 | ? | ? |
| Sungai Siak Kecil - Sungai Siak | 14.03-08.01 |  | 15 | 0 | 5 | 37.0 | 2.2 | -8.0 | 4.9 | ? | ? |
| Sungai Kapuas - Sungai Mendawak | 61.03.06 |  | 14 | 0 | 1 | 33.0 | 7.5 | 4.0 | 14.2 | ? | ? |
| Sungai Pukun - Sungai Mentaya | 62.02-07.02 |  | 12 | 1 | 4 | 38.0 | 39.9 | 54.0 | 62.0 | ? | ? |
| Sungai Kapuas - Sungai Ambawang | 61.71-12-03.01 |  | 13 | 0 | 5 | 62.0 | 24.0 | 41.0 | 21.0 | ? | ? |
| Sungai Gaung - Sungai Batangtuaka | 14.02-04.01 |  | 12 | 0 | 2 | 43.0 | 3.2 | 15.0 | 1.6 | ? | ? |
| Sungai Lalan - Sungai Merang | 15-16.02 |  | 8 | 2 | 4 | 66.0 | 65.0 | 2.0 | 6.1 | ? | ? |
| Sungai Ngirawan - Sungai Sembilang | 16.06-07.02 |  | 10 | 0 | 3 | 37.0 | 3.3 | 3.0 | 3.4 | ? | ? |
| Sungai Air Hitam Laut - Sungai Buntu Kecil | 15-16.01 | yes | 8 | 1 | 4 | 58.0 | 61.8 | 2.0 | 1.8 | yes | no |
| Aek Tapan - Aek Silaut | 13.01.01 |  | 9 | 0 | 2 | 31.0 | 2.1 | -2.0 | 6.8 | ? | ? |
| Sungai Rokan Kiri - Sungai Mandau | 14.01-03-06-08.01 |  | 8 | 0 | 2 | 36.0 | 6.4 | -4.0 | 5.0 | ? | ? |
| Sungai Merang - Sungai Ngirawan | 16.06-07.01 |  | 8 | 0 | 2 | 37.0 | 3.4 | 5.0 | 2.4 | ? | ? |
| Pulau Tebing Tinggi | 14.10.03 | yes | 5 | 2 | 2 | 53.0 | 53.4 | 39.0 | 13.6 | no | no |
| Sungai Rokan - Sungai Kubu | 14.07.01 |  | 7 | 0 | 3 | 36.0 | 16.1 | -6.0 | 10.7 | ? | ? |

KHG with at least 5 good concession and 3 good community stations: 1: Sungai Mendahara - Sungai Batanghari (15.05-07-10.01).

