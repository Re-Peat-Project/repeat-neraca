# Rewetting scenarios, 15.05-07-10.01_mendahara_batanghari

`python scripts/compare_scenarios.py --baseline tropical-large_p1.2_s1.2_t1.2_mt0.4_e0.3_100m_pb_dbbsdlp --scenario tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_e0.3_100m_pb_dbbsdlp tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp`. Baseline run: `tropical-large_p1.2_s1.2_t1.2_mt0.4_e0.3_100m_pb_dbbsdlp`. Season: days deeper than 40 cm out of 122. Open land: land not held by water management in that run. Still needs rewetting: more than 50% of the unit's open land deeper than 40 cm for more than half the season.

## tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_e0.3_100m_pb_dbbsdlp

blocks: 05_pump\lidar\mendahara_batanghari.gpkg, layer sekat_reach (160 reaches). Mean change in days deeper than 40 cm over cells open in both runs: -0.7 days; share of those cells with at least 10 days fewer: 0%. Water supplied in the season, all held land: baseline 58.5 million m3, scenario 58.3 million m3. Units still needing rewetting: 12 of 29 (baseline 12). Map: `tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_e0.3_100m_pb_dbbsdlp/days_deeper_40cm_change.tif`.

By distance from the block reaches:

| distance from a block reach | cells | mean change (days) | cells at least 10 days better |
|---|---|---|---|
| 0–150 m | 2009 | -26.2 | 62% |
| 150–350 m | 2693 | -8.9 | 35% |
| 350–1000 m | 7064 | -0.8 | 1% |
| beyond 1000 m | 108945 | -0.0 | 0% |

| unit | open km2 | days deeper 40 cm, baseline | days deeper 40 cm, scenario | mean depth baseline / scenario (cm) | still needs rewetting | supply mm, scenario |
|---|---|---|---|---|---|---|
| 15.05-07-10.01_S01 | 33.9 | 77.0 | 77.0 | 56 / 56 | yes |  |
| 15.05-07-10.01_S02 | 53.6 | 70.0 | 70.0 | 50 / 50 | yes |  |
| 15.05-07-10.01_S03 | 48.8 | 68.0 | 68.0 | 47 / 47 |  | 213.0 |
| 15.05-07-10.01_S04 | 47.9 | 68.0 | 68.0 | 48 / 48 |  |  |
| 15.05-07-10.01_S05 | 39.7 | 59.0 | 59.0 | 40 / 40 |  | 281.0 |
| 15.05-07-10.01_S06 | 107.2 | 45.0 | 45.0 | 32 / 32 |  |  |
| 15.05-07-10.01_S07 | 64.8 | 83.0 | 83.0 | 57 / 57 | yes | 219.0 |
| 15.05-07-10.01_S08 | 24.9 | 86.0 | 86.0 | 64 / 64 | yes |  |
| 15.05-07-10.01_S09 | 35.1 | 78.0 | 78.0 | 62 / 62 | yes | 298.0 |
| 15.05-07-10.01_S10 | 76.7 | 75.0 | 73.0 | 58 / 55 | yes | 352.0 |
| 15.05-07-10.01_S11 | 42.7 | 56.0 | 56.0 | 40 / 40 |  | 252.0 |
| 15.05-07-10.01_S12 | 85.0 | 60.0 | 55.0 | 46 / 41 |  | 429.0 |
| 15.05-07-10.01_S13 | 27.8 | 48.0 | 48.0 | 35 / 35 |  | 172.0 |
| 15.05-07-10.01_S14 | 37.5 | 68.0 | 67.0 | 46 / 45 | yes | 213.0 |
| 15.05-07-10.01_S15 | 46.9 | 61.0 | 61.0 | 46 / 46 |  | 233.0 |
| 15.05-07-10.01_S16 | 21.9 | 106.0 | 106.0 | 87 / 87 | yes | 203.0 |
| 15.05-07-10.01_S17 | 37.9 | 30.0 | 30.0 | 23 / 23 |  | 113.0 |
| 15.05-07-10.01_S18 | 49.0 | 37.0 | 37.0 | 28 / 28 |  | 105.0 |
| 15.05-07-10.01_S19 | 6.9 | 83.0 | 83.0 | 67 / 67 | yes | 191.0 |
| 15.05-07-10.01_S20 | 27.6 | 37.0 | 33.0 | 27 / 25 |  | 124.0 |
| 15.05-07-10.01_S21 | 11.3 | 92.0 | 92.0 | 71 / 71 | yes | 185.0 |
| 15.05-07-10.01_S22 | 0.0 |  |  |  |  | 189.0 |
| 15.05-07-10.01_S23 | 34.6 | 36.0 | 36.0 | 26 / 26 |  | 166.0 |
| 15.05-07-10.01_S24 | 22.5 | 110.0 | 110.0 | 94 / 94 | yes | 369.0 |
| 15.05-07-10.01_S25 | 3.2 | 120.0 | 120.0 | 106 / 106 | yes | 200.0 |
| 15.05-07-10.01_S26 | 6.8 | 66.0 | 66.0 | 47 / 47 |  | 141.0 |
| 15.05-07-10.01_S27 | 47.3 | 54.0 | 54.0 | 40 / 40 |  | 236.0 |
| 15.05-07-10.01_S28 | 110.8 | 57.0 | 57.0 | 44 / 44 |  | 475.0 |
| 15.05-07-10.01_S29 | 54.6 | 34.0 | 34.0 | 26 / 26 |  |  |

## tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp

blocks: 05_pump\lidar\mendahara_batanghari.gpkg, layer sekat_reach (160 reaches); water supply: 05_pump\lidar\mendahara_batanghari.gpkg, layer interventions (29% of the KHG held at 0.4 m). Mean change in days deeper than 40 cm over cells open in both runs: -1.0 days; share of those cells with at least 10 days fewer: 0%. Water supplied in the season, all held land: baseline 58.5 million m3, scenario 108.7 million m3. Units still needing rewetting: 9 of 29 (baseline 12). Map: `tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp/days_deeper_40cm_change.tif`.

By distance from the block reaches:

| distance from a block reach | cells | mean change (days) | cells at least 10 days better |
|---|---|---|---|
| 0–150 m | 1963 | -26.6 | 63% |
| 150–350 m | 2637 | -9.1 | 35% |
| 350–1000 m | 6894 | -0.8 | 1% |
| beyond 1000 m | 70794 | -0.0 | 0% |

| unit | open km2 | days deeper 40 cm, baseline | days deeper 40 cm, scenario | mean depth baseline / scenario (cm) | still needs rewetting | supply mm, scenario |
|---|---|---|---|---|---|---|
| 15.05-07-10.01_S01 | 0.0 | 77.0 |  |  |  | 147.0 |
| 15.05-07-10.01_S02 | 0.0 | 70.0 |  |  |  | 135.0 |
| 15.05-07-10.01_S03 | 0.0 | 68.0 |  |  |  | 153.0 |
| 15.05-07-10.01_S04 | 0.0 | 68.0 |  |  |  | 135.0 |
| 15.05-07-10.01_S05 | 39.7 | 59.0 | 59.0 | 40 / 40 |  | 278.0 |
| 15.05-07-10.01_S06 | 107.2 | 45.0 | 45.0 | 32 / 32 |  |  |
| 15.05-07-10.01_S07 | 64.8 | 83.0 | 83.0 | 57 / 56 | yes | 219.0 |
| 15.05-07-10.01_S08 | 24.9 | 86.0 | 86.0 | 64 / 64 | yes |  |
| 15.05-07-10.01_S09 | 0.0 | 78.0 |  |  |  | 153.0 |
| 15.05-07-10.01_S10 | 76.7 | 75.0 | 73.0 | 58 / 55 | yes | 352.0 |
| 15.05-07-10.01_S11 | 42.7 | 56.0 | 56.0 | 40 / 40 |  | 252.0 |
| 15.05-07-10.01_S12 | 85.0 | 60.0 | 55.0 | 46 / 41 |  | 429.0 |
| 15.05-07-10.01_S13 | 27.8 | 48.0 | 48.0 | 35 / 35 |  | 172.0 |
| 15.05-07-10.01_S14 | 37.5 | 68.0 | 67.0 | 46 / 45 | yes | 213.0 |
| 15.05-07-10.01_S15 | 46.9 | 61.0 | 61.0 | 46 / 46 |  | 233.0 |
| 15.05-07-10.01_S16 | 21.9 | 106.0 | 106.0 | 87 / 87 | yes | 203.0 |
| 15.05-07-10.01_S17 | 37.9 | 30.0 | 30.0 | 23 / 23 |  | 113.0 |
| 15.05-07-10.01_S18 | 49.0 | 37.0 | 37.0 | 28 / 28 |  | 105.0 |
| 15.05-07-10.01_S19 | 6.9 | 83.0 | 83.0 | 67 / 67 | yes | 191.0 |
| 15.05-07-10.01_S20 | 27.6 | 37.0 | 33.0 | 27 / 25 |  | 124.0 |
| 15.05-07-10.01_S21 | 11.3 | 92.0 | 92.0 | 71 / 71 | yes | 185.0 |
| 15.05-07-10.01_S22 | 0.0 |  |  |  |  | 189.0 |
| 15.05-07-10.01_S23 | 34.6 | 36.0 | 36.0 | 26 / 26 |  | 166.0 |
| 15.05-07-10.01_S24 | 22.5 | 110.0 | 109.0 | 94 / 93 | yes | 369.0 |
| 15.05-07-10.01_S25 | 3.2 | 120.0 | 120.0 | 106 / 104 | yes | 198.0 |
| 15.05-07-10.01_S26 | 0.0 | 66.0 |  |  |  | 135.0 |
| 15.05-07-10.01_S27 | 0.0 | 54.0 |  |  |  | 141.0 |
| 15.05-07-10.01_S28 | 0.0 | 57.0 |  |  |  | 125.0 |
| 15.05-07-10.01_S29 | 54.6 | 34.0 | 34.0 | 26 / 26 |  |  |

