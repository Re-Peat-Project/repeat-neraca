# Tropical peat hydraulic parameters for the physical neraca air

Research note, 2026-10-20. The question: the physical model takes specific yield Sy(z) and transmissivity T(z) from `urzainki2020_peat_tables.csv`, which was built with boreal retention curves. Is there a tropical alternative we can use?

## Short answer

Yes. There are tropical parameterisations, and one of them comes from the same lead author as our table (Urzainki et al. 2020):

- **Urzainki et al. (2023)** (Biogeosciences 20, 2099-2116, doi 10.5194/bg-20-2099-2023) rebuilt the canal-block model for tropical peat (Merang-Kepayang dome, 22,000 ha, South Sumatra). Sy and T are exponential functions of water table depth, "following the results of Cobb and Harvey (2019)", with two parameter sets (small and large conductivity). They are now in the code as `tropical-small` and `tropical-large`.
- **Cobb and Harvey (2019)** (Water Resources Research 55(11), 9351-9377, doi 10.1029/2019WR025411) derived Sy(z) and K(z) from water table, rainfall and topography at the Mendaram peat swamp, Brunei. The fitted knots are open data (PANGAEA 10.1594/PANGAEA.908210 and .908209).
- **Apers et al. (2022)** (J Adv Model Earth Syst 14, e2021MS002784) gives retention and conductivity parameters for natural and drained tropical peat, fitted to Indonesian and Malaysian data.
- Field values for Sumatra and Kalimantan exist too (Ismail et al. 2021, Kurnianto et al. 2019), and retention data for Riau (Taufik).

None of these replaces our table without a decision: the Urzainki 2023 sets are site-calibrated, not measured, and the measured values disagree with them (below).

## What our table does that tropical data do not

Values of the table in this repository (woody peat over sapric peat, Paivanen 1973 boreal retention curves) against tropical numbers. Depth is the water table below the surface.

| Depth | Our table Sy | Cobb and Harvey 2019 Sy (Brunei, measured) | Ismail et al. 2021 Sy (Padang Island, Riau) | Urzainki 2023 Sy (calibrated) |
|---|---|---|---|---|
| surface | 0.14 | 0.29 (at +0.01 m) | up to 0.3 | 0.60 |
| -0.3 m | 0.185 | 0.136 (0.130-0.141) | | 0.52 |
| -1.5 m | 0.225 | not measured | 0.1 | 0.28 |

| Depth | Our table T (m2/day) | Urzainki 2023 T, small / large (m2/day) |
|---|---|---|
| surface | 0.59 | 50 / 500 |
| -0.3 m | 0.17 | 23.6 / 236 |
| -1.0 m | 0.078 | 4.1 / 41 |

- **Sy goes the other way.** In our table Sy rises with depth (0.14 at the surface to 0.245 at -2 m). In every tropical source Sy falls with depth.
- **T is 100 to 1,000 times lower in our table.** Measured conductivity agrees with the tropical side: Cobb and Harvey give K = 6.2e-5 m/s (5.4 m/day) at -0.29 m, 1.2e-2 m/s at -0.005 m; Kurnianto et al. (2019) report 0.001 to 13.9 m/day in West Kalimantan, falling with depth; Apers et al. use 52 m/day horizontal conductivity for drained peat. The earlier sweep of transmissivity multipliers (x1 to x1000 in the neraca doc) was a way to bracket this.

## Sources and numbers

Numbers marked (verified) were read from the open full text or the dataset; the others are from abstracts.

| Source | Site | What it gives | Status |
|---|---|---|---|
| Urzainki et al. 2023, Table 2 | Merang-Kepayang peat dome, South Sumatra | Sy(zeta) = s1 exp(s2 zeta), s1 = 0.6, s2 = 0.5; T(zeta, d) = t1 (exp(t2 zeta) - exp(-t2 d)), t1 = 50 (scenario 1) or 500 (scenario 2), t2 = 2.5; zeta negative downwards, T in m2/day. Authors: "the peat hydraulic property set that best fitted the below-ground range and the dynamics of measured WTD" | (verified) |
| Cobb and Harvey 2019 (PANGAEA datasets) | Mendaram peat swamp, Brunei (natural) | Sy knots: -0.292 m 0.136; -0.183 m 0.167; -0.016 m 0.254; +0.011 m 0.291; +0.039 m 0.289; +0.168 m 0.686. K knots: -0.292 m 6.2e-5 m/s; -0.005 m 1.16e-2 m/s; +0.168 m 76 m/s. No data deeper than -0.29 m | (verified, 6 and 3 knots) |
| Ismail et al. 2021, Hydrology Research 52(6) | Padang Island, Riau | Sy from the rain-to-rise ratio as a function of pre-rain water table depth (method of Bourgault et al. 2016 and Cobb and Harvey 2019): up to 0.3 in the top peat, 0.1 at -1.5 m. Water table recession up to 3.5 cm/day in the most drained part | (verified, abstract and method sentence) |
| Apers et al. 2022, Table 1 | Indonesia and Malaysia sources | Natural: theta_s 0.88, h_s -0.024 m, Campbell b 7.4, K_s 6e-5 m/s. Drained: theta_s 0.68, h_s -0.04 m, b 9.6, K_s 2e-6 m/s, horizontal K 52 m/day | (verified) |
| Kurnianto et al. 2019, Mitig Adapt Strateg Glob Change | West Kalimantan | K from slug tests at 0.75, 3.5 and 5.5 m: 0.001 to 13.9 m/day, higher under forest, falling with depth and decomposition | abstract only |
| Taufik et al. 2019 (Geoderma), 2022 (Data in Brief), Mendeley dataset jj35xcx98v | Riau, Batanghari, Kubu Raya | Retention by humification class (fibric, hemic, sapric); water content at saturation, field capacity and wilting point at 10-30 and 50-70 cm in Riau. No van Genuchten parameters on the dataset page | not read in full |
| Liu et al. 2018, Menberu et al. 2021 | Mostly boreal | Pedotransfer functions and van Genuchten-Mualem parameters by bulk density; the data are northern | context only |

Not read: Cobb and Harvey's own text (the MIT copy refused the download), the Taufik papers, and Scite (the connector needs a paid plan). The Cobb knots above come from the dataset, which is the fitted result, not from the paper's discussion of them.

## What happens to the model with each table

`scripts/run_neraca.py --peat-table urzainki2020|tropical-small|tropical-large`, cached ERA5, 2026-04-01 to 2026-10-15, no evaporation stress, canal classes primary, secondary, tertiary. Full reports are in `docs/reports/peat_table/`. KHG-mean simulated curve against the mean of the stations:

| Site | Table | Canal drawdown | Bias (cm) | RMSE (cm) | RMSE without bias (cm) | r |
|---|---|---|---|---|---|---|
| Sugihan-Lumpur | boreal (ours) | 0.5 / 1.2 m | +22.7 / +22.8 | 56.6 / 56.6 | 51.8 / 51.8 | 0.96 |
| | tropical-small | 0.5 / 1.2 m | -15.0 / -4.3 | 23.9 / 25.6 | 18.7 / 25.3 | 0.95 / 0.96 |
| | tropical-large | 0.5 / 1.2 m | +8.8 / +52.1 | 21.6 / 62.8 | 19.7 / 35.1 | 0.96 / 0.95 |
| Kampar-Gaung | boreal (ours) | 0.5 / 1.2 m | -16.9 / -16.9 | 27.5 / 27.5 | 21.7 / 21.7 | 0.68 |
| | tropical-small | 0.5 / 1.2 m | -32.1 / -27.2 | 33.1 / 29.2 | 7.8 / 10.7 | 0.67 / 0.64 |
| | tropical-large | 0.5 / 1.2 m | -10.1 / +23.8 | 16.3 / 31.4 | 12.8 / 20.5 | 0.59 / 0.56 |

Sugihan-Lumpur, 2D tier at 500 m:

| Table | KHG mean bias / RMSE (cm) | Spearman across stations, peak depth | Per sub-KHG mean water table (cm) |
|---|---|---|---|
| boreal (ours) | +21.4 / 55.5 | 0.17 | 65 to 65 |
| tropical-small | -21.0 / 25.9 | -0.20 | 22 to 23 |
| tropical-large | -18.0 / 24.8 | -0.19 | 23 to 29 |

How to read this:

1. **The KHG-level amplitude improves a lot.** With a tropical table the RMSE on Sugihan-Lumpur falls from 56.6 to about 22-26 cm at the better canal drawdown, and the bias can be brought to a few cm. With the boreal table the simulated water table fell far deeper than observed.
2. **It is not independent evidence.** The Urzainki 2023 sets were chosen to fit measured water table depths at another site, and their surface Sy of 0.6 is about twice the highest measured value (0.29, Cobb and Harvey). A large effective Sy damps the drawdown, which is what the fit rewards here. Treat the improvement as "the model needs much more storage near the surface and much more conductivity than the boreal table gives", not as validation of 0.6 and 50-500.
3. **The results swing with the canal drawdown assumption** (for example tropical-large on Sugihan-Lumpur: +8.8 cm at 0.5 m, +52.1 cm at 1.2 m). Observed water tables sit at 35-55 cm, so a canal level of 1.2 m below the surface is not what the stations show; this is the same finding as before and a tropical table does not remove it.
4. **There is still no spatial skill.** Spearman across stations stays between -0.2 and 0.17 and every sub-KHG gets nearly the same curve (22-29 cm). The per-sub-KHG output remains unusable for ranking (`neraca_skill_ok = 0`). The KHG-level deficit in `neraca_khg.csv` is a mass balance and does not depend on the table.
5. **The constant Sy of 0.15 used for the deficit** sits inside the measured tropical range at depth (0.14 at -0.3 m, 0.1 at -1.5 m, up to 0.29-0.3 near the surface), so the earlier choice stands.

## Recommendation

- Keep `urzainki2020` as the default for now so that existing results do not move, and use `--peat-table tropical-small` or `tropical-large` for tropical KHG, saying in any report that the sets are site-calibrated.
- Before adopting one as the default: (a) replace the surface Sy of 0.6 by a measured shape (Cobb and Harvey near the surface, Ismail below, giving roughly 0.3 falling to 0.1 at -1.5 m); (b) take T from measured conductivity profiles (Cobb and Harvey, Kurnianto) instead of a calibrated scale; (c) fit nothing to our stations, so that the comparison with them stays a test.
- Retention data for Riau (Taufik) and the PEATCLSM-Trop retention parameters could give an independent Sy(z) from the retention curve. That needs the van Genuchten or Campbell parameters per layer and a choice of how to integrate them; not done.
- If a set is adopted, its numbers move into `config/parameters.yaml` (they are in `TROPICAL_SETS` in `testbed/groundwater.py` for now, so that the registry snapshot of existing runs does not change).

Reproduce: `python scripts/run_neraca.py --config ../re-peat/sites/sugihan_lumpur/neraca.yaml --peat-table tropical-small --tier 1 --classes primary,secondary,tertiary --drawdown 0.5,1.2` (and `--tier 2 --res 500`), with `REPEAT_DATA` and `REPEAT_WORK` set.

## References

- Apers, S., De Lannoy, G. J. M., Baird, A. J., Cobb, A. R., et al. (2022). Tropical peatland hydrology simulated with a global land surface model. Journal of Advances in Modeling Earth Systems, 14(3), e2021MS002784. https://doi.org/10.1029/2021MS002784
- Cobb, A. R., and Harvey, C. F. (2019). Scalar simulation and parameterization of water table dynamics in tropical peatlands. Water Resources Research, 55(11), 9351-9377. https://doi.org/10.1029/2019WR025411. Data: https://doi.org/10.1594/PANGAEA.908210 and https://doi.org/10.1594/PANGAEA.908209
- Ismail, I., Torabi Haghighi, A., Marttila, H., Kurniawan, U., Karyanto, O., and Kløve, B. (2021). Water table variations on different land use units in a drained tropical peatland island of Indonesia. Hydrology Research, 52(6), 1372-1388. https://doi.org/10.2166/nh.2021.062
- Kurnianto, S., et al. (2019). The influence of land-cover changes on the variability of saturated hydraulic conductivity in tropical peatlands. Mitigation and Adaptation Strategies for Global Change.
- Taufik, M., et al. (2019). Exploration of the importance of physical properties of Indonesian peatlands to assess critical groundwater table depths, associated drought and fire hazard. Geoderma. Taufik, M., et al. (2022). Groundwater table and soil-hydrological properties datasets of Indonesian peatlands. Data in Brief. Taufik, M. (2022). Peat water retention from different land-uses in Riau, Indonesia. Mendeley Data, https://doi.org/10.17632/jj35xcx98v.1
- Urzainki, I., Laurén, A., Palviainen, M., Haahti, K., Budiman, A., Basuki, I., Netzer, M., and Hökkä, H. (2020). Canal blocking optimization in restoration of drained peatlands. Biogeosciences, 17, 4769-4784. https://doi.org/10.5194/bg-17-4769-2020
- Urzainki, I., Palviainen, M., Hökkä, H., Persch, S., Chatellier, J., Wang, O., Mahardhitama, P., Yudhista, R., and Laurén, A. (2023). A process-based model for quantifying the effects of canal blocking on water table and CO2 emissions in tropical peatlands. Biogeosciences, 20(11), 2099-2116. https://doi.org/10.5194/bg-20-2099-2023
