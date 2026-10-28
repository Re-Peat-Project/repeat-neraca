# Peat hydraulic parameters and evapotranspiration, Sumatra and Kalimantan

Research note, 2026-10-28. Question: the groundwater model uses the Urzainki et al. (2023) tropical sets, `Sy(z) = 0.6 exp(0.5 z)` and `T(z) = t1 exp(2.5 z)` with t1 = 50 or 500 m²/d. Is a surface specific yield of 0.6 supported for Sumatran and Kalimantan peat, and what do measurements say about T and ET? Builds on `docs/tropical-peat-hydraulic-parameters.md`, which already covers Cobb and Harvey 2019, Apers et al. 2022, Jaenicke et al. 2010 and the Kurnianto 2019 K range.

Labels: *full text*, *abstract*, *derived* (our arithmetic from the source's numbers), *checked* (re-read in the downloaded text on 2026-10-28), *second-hand* (a value cited by another paper).

## Values

| Parameter | Value | Depth | Site | Land use | Method | Source | Label |
|---|---|---|---|---|---|---|---|
| Sy | 0.05 to slightly above 0.30, falling with pre-rain water table depth (logarithmic trend, Fig. 10b); up to 0.3 in the top peat, 0.1 at −1.5 m; at Sd-TP at most 0.15 with pre-rain depth below −0.75 m | estimated down to −1.7 m | Pulau Padang, Riau | plantation-drained and farm-drained | rain-to-rise ratio of 42 events above 5 mm (Bourgault et al. 2016; Cobb and Harvey 2019) | Ismail et al. 2021, Hydrology Research 52(6), 1372, doi 10.2166/nh.2021.062 | *full text* (section below) |
| Sy | 0.15 (peat swamp forest), 0.10 (smallholder), 0.15 (industrial plantation), 0.10 (mangrove); ranges 0.08–0.3 and 0.05–0.2 | one value per column | Pulau Padang | by land cover | Ismail's method as prior, then calibrated in MIKE SHE | Kurnianto et al. 2026, J Hydrol Reg Stud, doi 10.1016/j.ejrh.2026.103185, Table 1 | *checked* |
| Implied Sy | 4.2 / 7.5 ≈ 0.56 | water table near the surface | Kampar Peninsula, Riau | the site of the 4.2 mm/d ET is not clear from the extracted text | daily ET 4.2 mm/d; ET-driven drawdown 7.5 mm/d on days without rain (total recession 10.3 mm/d) | Deshmukh et al. 2023, Nature, doi 10.1038/s41586-023-05860-9 | *checked* values, *derived* ratio |
| Implied Sy | ≈ 0.33–0.48 | dry season | Sebangau, Central Kalimantan | forest, blocked, drained | ET-only drawdown 9.3–12.7 mm/d (Putra et al. 2021, *abstract*) against eddy-covariance ET of 4.2–4.5 mm/d (Hirano et al. 2015) | Putra et al. 2021, Hydrol Process, doi 10.1002/hyp.14174 | *derived* |
| Horizontal K | 0–1 m: 172.8 (forest), 51.84 (smallholder), 34.56 (industrial), 8.64 (mangrove) m/d; 1–2 m: 69.12, 17.28, 17.28, 0.17; > 2 m: 4.32, 4.32, 1.32, 0.17 | three layers | Pulau Padang | by land cover | slug tests as priors, then calibrated | Kurnianto et al. 2026, Table 1 | *checked* |
| Ks | forest 0.63 ± 0.36, oil palm 0.20 ± 0.13, shrub 0.16 ± 0.08 m/d (mean ± s.e.) | 1.0, 3.5, 6.0 m | West Kalimantan | forest, oil palm, shrub | slug tests | Kurnianto, Peterson et al., 16th International Peat Congress, pp. 165–168 | *full text* |
| K | vertical 50–53 cm/h (about 12 m/d), horizontal 113 cm/h (about 27 m/d); porosity 92–95% | laboratory cores | Perigi, OKI (KHG Sugihan-Saleh) | agriculture | constant head | Imanudin et al. 2026, JDMLM, doi 10.15243/jdmlm.2026.132.9847 | *abstract* |
| K, older values | 0.48–12.48 m/d (Sajarwan 2001); above 10 m/d in the top layer (Takahashi and Yonetani 1997); 10–30 m/d from pumping tests in Sarawak; SIMGRO used 20 m/d | various | Sebangau, Sarawak | various | compilation | de Vries 2003, Alterra report 797 | *second-hand* |
| ET, annual | 1636 ± 53 (undrained forest), 1553 ± 117 (drained forest), 1374 ± 75 (drained burnt) mm/yr, energy balance closed | — | Palangka Raya, Central Kalimantan | peat swamp forest | eddy covariance, 4 years | Hirano et al. 2015, Glob Change Biol, doi 10.1111/gcb.12653 | *checked* |
| ET and water table | each 10 cm deeper minimum monthly water table cuts annual ET by 19, 33 and 26 mm at the three sites | — | same | same | same | same | *checked* |
| ET, annual | 1457 ± 152 mm/yr; ET fell 33–69% for a 0 to 1 m drawdown | — | Central Kalimantan | degraded, drained, burnt forest | eddy covariance, about 13 years | Ohkubo et al. 2021, J Hydrol, doi 10.1016/j.jhydrol.2021.126906 | *full text* |
| ET, annual | oil palm 851 ± 177; secondary forest 1093 ± 180; primary forest 1116 ± 259 mm/yr (energy balance not closed) | — | Sarawak | oil palm, forest | eddy covariance | Musin et al., conference slides | *full text* (slides) |
| Water table | Acacia 70 ± 17 cm; adjacent forest 47 ± 22 cm below the surface; subsidence 4.3 cm/yr in Acacia | — | 312 sites, Sumatra | Acacia, forest | manual dipwells | Evans et al. 2019, Geoderma, doi 10.1016/j.geoderma.2018.12.028 | *checked* |
| Water table | −0.65 ± 0.17 m (Acacia) | — | Kampar | Acacia | dipwells | Deshmukh et al. 2023 | *checked* |
| Dry-season recession | 1.68, 1.45, 1.41, 0.85, 0.75, 0.39 cm/d at Sungai Saleh-1, Padang Sugihan-2, Karang Agung, Padang Sugihan-3, Cinta Jaya-1, Cinta Jaya-2 | — | South Sumatra BRG stations, August 2019, no rain | various | linear fit | Irfan et al. 2021, J Phys Conf Ser 1816, 012008, doi 10.1088/1742-6596/1816/1/012008 | *checked* |
| Recession | Sd-TP 3.5 to 1.0 cm/d for water table −0.8 to −1.8 m; Sd-AK 1.8 to 0.5 cm/d for −0.4 to −0.7 m (master recession curves, 10 recessions each) | — | Pulau Padang | plantation-drained; farm-drained | loggers, 10 min | Ismail et al. 2021 | *full text* |

Padang Sugihan-2 lies inside KHG Sugihan-Lumpur and Padang Sugihan-3 about 0.1 km outside it, by the coordinates in Irfan et al. 2021 placed on `_data/batas_khg_indonesia.gpkg` (three decimals, so the second is borderline). Baird et al. 2017 (GRL), sometimes cited for Sebangau, is a study of San San Pond Sak, Panama, and is left out.

## Ismail et al. 2021, full text (read 2026-10-28, PDF supplied by the project owner)

Ismail, I., Torabi Haghighi, A., Marttila, H., Kurniawan, U., Karyanto, O., Kløve, B. (2021). Water table variations on different land use units in a drained tropical peatland island of Indonesia. Hydrology Research 52(6), 1372–1388, doi 10.2166/nh.2021.062. CC BY-NC-ND 4.0. A BRG–UGM project; the first author is at UGM Faculty of Forestry and the University of Oulu. "Data cannot be made publicly available; readers should contact the corresponding author."

**Site and data.**
- Pulau Padang, about 100,000 ha; peat 7–9 m at the stations.
- Plantation drains: 1 m (tertiary) to 10 m (primary) wide, up to 5 m deep, spacing 130 m. Farm drains are under 1 m wide.
- Four logging stations from April 2017 to late 2018, recording every 10 min with sensors to 2 m: Sd-TP and Sd-AK ("severely drained", under 2 km from plantation drainage), Ld-SA and Ld-Me ("less drained"). A fifth station was destroyed.
- Transects T1–T8, measured by hand in May 2018: 108 farm, 31 shrub and 14 forest points (Fig. 8d).

**Water table depth.** Means over 325 simultaneous days: Sd-TP −1.17 m, Ld-SA −0.79 m, Sd-AK −0.60 m, Ld-Me −0.44 m (Fig. 7b).
- Sd-TP, 100 m from a plantation drainage outlet, was deeper than 1.5 m for 20% of the time.
- Ld-Me was below −0.4 m for more than 80% of the time.
- Forest without drainage, north of Ld-Me: −0.2 to −0.3 m. Forest under 0.5 km from a plantation drain: −1.1 m.
- Elevation explained almost nothing (R² 0.03). "A combination of land cover and drainage intensity generally explained most of the spatial variability"; land cover alone did not.

**Drain functionality.** Sd-AK lies under 1.5 km from plantation drainage but stays shallow: "nearby plantation drains had been blocked to maintain shallow water table ... Water table dynamics were affected not only by distance to plantation drainage, but also by drain functionality."

**Rain and rise.**
- Rain events under 5 mm gave no consistent rise. Rise against rain: R² 0.76 overall and 0.93 at Sd-TP (14, 16 and 12 events at Sd-TP, Sd-AK and Ld-Me).
- The water table rose about 2 h after rain started; in one event it rose 0.4 m/h, then fell 0.008 m/h.

**Recession.**
- The rate falls with depth: Sd-TP 3.5 to 1.0 cm/d over −0.8 to −1.8 m; Sd-AK 1.8 to 0.5 cm/d over −0.4 to −0.7 m.
- "Recession rate near pulp plantations remained high (0.01 m/day) at −1.5 m depth"; "drainage extends discharge flow to deeper layers."

**Other.**
- Tides up to 2 m nearby, but the mean water levels at the two stations nearest the coast were 4.43 and 5.71 m above sea level, with no diurnal signal.
- Regional ET is about 1,300 mm/yr.

**Use in the model.**
- A literature-based Sy(z) for drained peat. An exponential through the abstract's two values, `Sy = 0.3 exp(0.73 z)`, is our fit, not the authors'. Figure 10b gives the scatter but no fitted coefficients.
- Test targets per land-use class: mean depth under heavy plantation drainage, farm drainage and undrained forest; the recession rate against depth. Pulau Padang has a 2 m LiDAR DTM (2016) in `_data/lidar_pulau_padang_2016/`.
- Canal level set by drain function (blocked or open), not by class alone, which matches the managed-land option of `repeat-neraca-model`.
- The station series are not public. Requesting them from the corresponding author is the owner's decision.

## What this means for the model

1. **A surface Sy of 0.6 fits intact forest with the water table near the surface, not drained peat.** The values derived from Kampar (about 0.56) and Sebangau (0.33–0.48) come from forest or mixed sites. Drained peat points to 0.1–0.3: Ismail (0.3 at the surface, 0.1 at −1.5 m), Kurnianto 2026 (0.10–0.15, calibrated). Where drained water tables sit, at −0.65 to −0.70 m (Deshmukh, Evans), the Urzainki curve gives 0.6 e^(−0.35) ≈ 0.42 (*derived*).
2. **Calibrated models disagree.** Urzainki 2023 (Sy 0.6, t1 50–500) and Kurnianto 2026 (Sy 0.10–0.15, K 35–173 m/d in the top metre) both fit their own stations on drained Sumatran peat. Calibration alone does not settle Sy.
3. **Recession rates give only a lower bound,** Sy ≥ ET / rate, and the bound depends on ET at depth. With ET 4 mm/d, Padang Sugihan-2 (1.45 cm/d) gives Sy ≥ 0.28; with ET 2 mm/d, ≥ 0.14 (*derived*). Dry-spell recession and rain-to-rise at the Sugihan-Lumpur stations, by depth class, are the observations that would test Sy(z) directly.
4. **T.** At a water table of −0.5 m, Kurnianto's plantation column gives about 35 m²/d, between Urzainki small (14 m²/d) and large (143 m²/d) (*derived*). Kurnianto's T also falls more slowly with depth than t2 = 2.5. Slug tests (0.2–0.6 m/d) are two orders below the calibrated values; grid-scale models use the calibrated range.
5. **ET.** Measured ET on Kalimantan peat is 1,370–1,650 mm/yr, falling as the water table deepens. No comparison of MOD16 or WaPOR with eddy covariance on Indonesian peat was found. ET that falls with depth (as in tier 1's `--et-stress`) would reduce drawdown in a dry season and is not in the groundwater model yet.

## Gaps

- Ismail et al. 2021 full text (publisher bot check); Wösten et al. 2008 numbers; Takahashi's original papers.
- Taufik et al. 2022 retention parameters (supplement and Mendeley dataset), the best independent Sy(z) for Riau and South Sumatra.
- Measured canal water levels for OKI and Sugihan.
- MOD16 or WaPOR against eddy covariance on Indonesian peat.
