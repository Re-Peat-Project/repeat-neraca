# Groundwater model sweep, 14.10.03_pulau_tebing_tinggi, deltadtm, 200 m

`python scripts/model_sweep.py --khg 14.10.03 --dem deltadtm --start 2014-10-01 --end 2015-12-11 --res 200 --tables tropical-small,tropical-large,urzainki2020 --drawdown 0.6,1.2`. Runs start saturated on 2014-10-01; nothing is fitted. Field points: `00_inputs/field_wtd.csv`, unflagged, on peat, not on a fixed cell (n = 528). Each run's own report: `03_neraca/deltadtm/runs/model/<run>/model_report.md`.

## Runs

| peat table | canal level (m) | Spearman | Spearman within teams | bias (cm) | RMSE (cm) | gate | KHG mean depth in window (cm) | canal inflow in window (mm) | run |
|---|---|---|---|---|---|---|---|---|---|
| tropical-small | 0.6 | 0.04 | 0.02 | -71 | 81 | fail | 1-27 | -3.2 | tropical-small_p0.6_s0.6_t0.6_e0.3_200m |
| tropical-small | 1.2 | 0.05 | 0.01 | -69 | 80 | fail | 2-29 | -4.6 | tropical-small_p1.2_s1.2_t1.2_e0.3_200m |
| tropical-large | 0.6 | 0.01 | -0.03 | -55 | 70 | fail | 12-48 | -7.6 | tropical-large_p0.6_s0.6_t0.6_e0.3_200m |
| tropical-large | 1.2 | 0.01 | -0.03 | -48 | 67 | fail | 17-56 | -9.6 | tropical-large_p1.2_s1.2_t1.2_e0.3_200m |
| urzainki2020 | 0.6 | 0.02 | 0.08 | -61 | 73 | fail | -0-69 | -0.0 | urzainki2020_p0.6_s0.6_t0.6_e0.3_200m |
| urzainki2020 | 1.2 | 0.03 | 0.08 | -61 | 73 | fail | -0-69 | -0.1 | urzainki2020_p1.2_s1.2_t1.2_e0.3_200m |

Simple predictions on the same points: constant median RMSE 40 cm; distance to the nearest canal Spearman -0.00, RMSE 39 cm. Gate (`groundwater/fieldcheck.py`): Spearman at least 0.3 and above the distance prediction, RMSE below the constant prediction.

## The field data

Spearman of the observed depth with distance to the nearest canal 0.00, with the recorded peat thickness 0.02. Share of the observed variance between field teams: 31% over all points (n = 528), 76% between teams that worked the same 2 km block (n = 258). With each team's mean removed, the Spearman of the observed depth with distance to the nearest canal is 0.14 (every unflagged point, canal cells included). The team effect does not follow the visit dates: across the 25 teams with at least 5 dated points, the Spearman of the team's median depth with its median last-rain date is 0.13. Both distance figures are below the gate's 0.3 (a positive value means deeper away from canals, the opposite of canal drainage), so the field depths carry no usable canal-driven pattern and cannot serve as the spatial test of the model.

