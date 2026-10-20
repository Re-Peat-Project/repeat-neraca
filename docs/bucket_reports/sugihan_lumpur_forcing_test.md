# Forcing test: sugihan_lumpur

Out-of-fold, block cross-validation (see `neracaair/README.md`). Periods differ where a source stops earlier (CHIRPS final data ends 2026-09-30).

| forcing | period scored | stations | RMSE with drainage (cm) | RMSE without (cm) | baseline RMSE (cm) | temporal r with | temporal r without | spatial rho peak (without) | drainage term | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ERA5 rain + ERA5 evaporation | 2026-04-01 to 2026-10-09 | 51 | 6.4 | 11.3 | 5.7 | 0.90 | 0.77 | 0.23 | dropped | not usable |
| era5 rain + wapor evaporation | 2026-04-01 to 2026-10-09 | 51 | 7.6 | 14.2 | 5.7 | 0.88 | 0.58 | 0.21 | dropped | not usable |
