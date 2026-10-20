# Forcing test: kampar_gaung

Out-of-fold, block cross-validation (see `neracaair/README.md`). Periods differ where a source stops earlier (CHIRPS final data ends 2026-09-30).

| forcing | period scored | stations | RMSE with drainage (cm) | RMSE without (cm) | baseline RMSE (cm) | temporal r with | temporal r without | spatial rho peak (without) | drainage term | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ERA5 rain + ERA5 evaporation | 2026-04-01 to 2026-10-09 | 86 | 16.5 | 20.4 | 15.3 | 0.63 | 0.13 | -0.10 | kept | not usable |
| era5 rain + wapor evaporation | 2026-04-01 to 2026-10-09 | 86 | 18.9 | 24.0 | 15.3 | 0.41 | -0.12 | -0.09 | dropped | not usable |
