# Rewetting scenarios, 15.05-07-10.01_mendahara_batanghari

`python scripts/compare_scenarios.py --baseline tropical-large_p0.6_s0.6_t0.6_mt0.4_e0.3_100m_pb_dbbsdlp --scenario tropical-large_p0.6_s0.6_t0.6_mt0.4_blk_e0.3_100m_pb_dbbsdlp tropical-large_p0.6_s0.6_t0.6_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp`. Baseline run: `tropical-large_p0.6_s0.6_t0.6_mt0.4_e0.3_100m_pb_dbbsdlp`. Season: days deeper than 40 cm out of 122. Open land: land not held by water management in that run. Still needs rewetting: more than 50% of the unit's open land deeper than 40 cm for more than half the season.

## tropical-large_p0.6_s0.6_t0.6_mt0.4_blk_e0.3_100m_pb_dbbsdlp

blocks: 05_pump\lidar\mendahara_batanghari.gpkg, layer sekat_reach (160 reaches). Mean change in days deeper than 40 cm over cells open in both runs: -0.3 days; share of those cells with at least 10 days fewer: 0%. Water supplied in the season, all held land: baseline 54.6 million m3, scenario 54.6 million m3. Units still needing rewetting: 8 of 29 (baseline 8). Map: `tropical-large_p0.6_s0.6_t0.6_mt0.4_blk_e0.3_100m_pb_dbbsdlp/days_deeper_40cm_change.tif`.

By distance from the block reaches:

| distance from a block reach | cells | mean change (days) | cells at least 10 days better |
|---|---|---|---|
| 0–150 m | 2009 | -13.6 | 26% |
| 150–350 m | 2693 | -4.1 | 17% |
| 350–1000 m | 7064 | -0.4 | 0% |
| beyond 1000 m | 108945 | -0.0 | 0% |

| unit | open km2 | days deeper 40 cm, baseline | days deeper 40 cm, scenario | mean depth baseline / scenario (cm) | still needs rewetting | supply mm, scenario |
|---|---|---|---|---|---|---|
| 15.05-07-10.01_S01 | 33.9 | 61.0 | 61.0 | 40 / 40 |  |  |
| 15.05-07-10.01_S02 | 53.6 | 56.0 | 56.0 | 37 / 37 |  |  |
| 15.05-07-10.01_S03 | 48.8 | 54.0 | 54.0 | 36 / 36 |  | 212.0 |
| 15.05-07-10.01_S04 | 47.9 | 54.0 | 54.0 | 36 / 36 |  |  |
| 15.05-07-10.01_S05 | 39.7 | 48.0 | 48.0 | 32 / 32 |  | 237.0 |
| 15.05-07-10.01_S06 | 107.2 | 40.0 | 40.0 | 28 / 28 |  |  |
| 15.05-07-10.01_S07 | 64.8 | 66.0 | 66.0 | 42 / 42 | yes | 199.0 |
| 15.05-07-10.01_S08 | 24.9 | 68.0 | 68.0 | 45 / 45 | yes |  |
| 15.05-07-10.01_S09 | 35.1 | 62.0 | 62.0 | 42 / 42 | yes | 255.0 |
| 15.05-07-10.01_S10 | 76.7 | 62.0 | 61.0 | 41 / 40 |  | 279.0 |
| 15.05-07-10.01_S11 | 42.7 | 48.0 | 48.0 | 32 / 32 |  | 212.0 |
| 15.05-07-10.01_S12 | 85.0 | 51.0 | 48.0 | 34 / 33 |  | 315.0 |
| 15.05-07-10.01_S13 | 27.8 | 43.0 | 43.0 | 30 / 30 |  | 169.0 |
| 15.05-07-10.01_S14 | 37.5 | 55.0 | 55.0 | 37 / 36 |  | 196.0 |
| 15.05-07-10.01_S15 | 46.9 | 53.0 | 52.0 | 35 / 35 |  | 213.0 |
| 15.05-07-10.01_S16 | 21.9 | 85.0 | 85.0 | 53 / 53 | yes | 202.0 |
| 15.05-07-10.01_S17 | 37.9 | 30.0 | 29.0 | 23 / 23 |  | 111.0 |
| 15.05-07-10.01_S18 | 49.0 | 35.0 | 35.0 | 25 / 25 |  | 101.0 |
| 15.05-07-10.01_S19 | 6.9 | 67.0 | 67.0 | 44 / 44 | yes | 187.0 |
| 15.05-07-10.01_S20 | 27.6 | 35.0 | 32.0 | 25 / 24 |  | 119.0 |
| 15.05-07-10.01_S21 | 11.3 | 72.0 | 72.0 | 48 / 48 | yes | 181.0 |
| 15.05-07-10.01_S22 | 0.0 |  |  |  |  | 189.0 |
| 15.05-07-10.01_S23 | 34.6 | 35.0 | 35.0 | 25 / 25 |  | 155.0 |
| 15.05-07-10.01_S24 | 22.5 | 90.0 | 90.0 | 56 / 56 | yes | 307.0 |
| 15.05-07-10.01_S25 | 3.2 | 105.0 | 105.0 | 62 / 62 | yes | 189.0 |
| 15.05-07-10.01_S26 | 6.8 | 56.0 | 56.0 | 36 / 36 |  | 138.0 |
| 15.05-07-10.01_S27 | 47.3 | 47.0 | 47.0 | 32 / 32 |  | 192.0 |
| 15.05-07-10.01_S28 | 110.8 | 49.0 | 49.0 | 33 / 33 |  | 316.0 |
| 15.05-07-10.01_S29 | 54.6 | 33.0 | 33.0 | 24 / 24 |  |  |

## tropical-large_p0.6_s0.6_t0.6_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp

blocks: 05_pump\lidar\mendahara_batanghari.gpkg, layer sekat_reach (160 reaches); water supply: 05_pump\lidar\mendahara_batanghari.gpkg, layer interventions (29% of the KHG held at 0.4 m). Mean change in days deeper than 40 cm over cells open in both runs: -0.5 days; share of those cells with at least 10 days fewer: 0%. Water supplied in the season, all held land: baseline 54.6 million m3, scenario 105.1 million m3. Units still needing rewetting: 7 of 29 (baseline 8). Map: `tropical-large_p0.6_s0.6_t0.6_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp/days_deeper_40cm_change.tif`.

By distance from the block reaches:

| distance from a block reach | cells | mean change (days) | cells at least 10 days better |
|---|---|---|---|
| 0–150 m | 1963 | -13.8 | 26% |
| 150–350 m | 2637 | -4.2 | 17% |
| 350–1000 m | 6894 | -0.4 | 0% |
| beyond 1000 m | 70794 | -0.0 | 0% |

| unit | open km2 | days deeper 40 cm, baseline | days deeper 40 cm, scenario | mean depth baseline / scenario (cm) | still needs rewetting | supply mm, scenario |
|---|---|---|---|---|---|---|
| 15.05-07-10.01_S01 | 0.0 | 61.0 |  |  |  | 147.0 |
| 15.05-07-10.01_S02 | 0.0 | 56.0 |  |  |  | 135.0 |
| 15.05-07-10.01_S03 | 0.0 | 54.0 |  |  |  | 152.0 |
| 15.05-07-10.01_S04 | 0.0 | 54.0 |  |  |  | 134.0 |
| 15.05-07-10.01_S05 | 39.7 | 48.0 | 48.0 | 32 / 32 |  | 237.0 |
| 15.05-07-10.01_S06 | 107.2 | 40.0 | 40.0 | 28 / 28 |  |  |
| 15.05-07-10.01_S07 | 64.8 | 66.0 | 66.0 | 42 / 42 | yes | 199.0 |
| 15.05-07-10.01_S08 | 24.9 | 68.0 | 68.0 | 45 / 45 | yes |  |
| 15.05-07-10.01_S09 | 0.0 | 62.0 |  |  |  | 152.0 |
| 15.05-07-10.01_S10 | 76.7 | 62.0 | 61.0 | 41 / 40 |  | 279.0 |
| 15.05-07-10.01_S11 | 42.7 | 48.0 | 48.0 | 32 / 32 |  | 212.0 |
| 15.05-07-10.01_S12 | 85.0 | 51.0 | 48.0 | 34 / 33 |  | 315.0 |
| 15.05-07-10.01_S13 | 27.8 | 43.0 | 43.0 | 30 / 30 |  | 169.0 |
| 15.05-07-10.01_S14 | 37.5 | 55.0 | 55.0 | 37 / 36 |  | 196.0 |
| 15.05-07-10.01_S15 | 46.9 | 53.0 | 52.0 | 35 / 35 |  | 213.0 |
| 15.05-07-10.01_S16 | 21.9 | 85.0 | 85.0 | 53 / 53 | yes | 202.0 |
| 15.05-07-10.01_S17 | 37.9 | 30.0 | 29.0 | 23 / 23 |  | 111.0 |
| 15.05-07-10.01_S18 | 49.0 | 35.0 | 35.0 | 25 / 25 |  | 101.0 |
| 15.05-07-10.01_S19 | 6.9 | 67.0 | 67.0 | 44 / 44 | yes | 187.0 |
| 15.05-07-10.01_S20 | 27.6 | 35.0 | 32.0 | 25 / 24 |  | 119.0 |
| 15.05-07-10.01_S21 | 11.3 | 72.0 | 72.0 | 48 / 48 | yes | 181.0 |
| 15.05-07-10.01_S22 | 0.0 |  |  |  |  | 189.0 |
| 15.05-07-10.01_S23 | 34.6 | 35.0 | 35.0 | 25 / 25 |  | 155.0 |
| 15.05-07-10.01_S24 | 22.5 | 90.0 | 90.0 | 56 / 56 | yes | 307.0 |
| 15.05-07-10.01_S25 | 3.2 | 105.0 | 104.0 | 62 / 61 | yes | 189.0 |
| 15.05-07-10.01_S26 | 0.0 | 56.0 |  |  |  | 135.0 |
| 15.05-07-10.01_S27 | 0.0 | 47.0 |  |  |  | 134.0 |
| 15.05-07-10.01_S28 | 0.0 | 49.0 |  |  |  | 123.0 |
| 15.05-07-10.01_S29 | 54.6 | 33.0 | 33.0 | 24 / 24 |  |  |

