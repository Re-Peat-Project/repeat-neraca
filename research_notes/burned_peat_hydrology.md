# Burned peat: infiltration, runoff and the groundwater model

Research note, 2026-10-28. Question from the project owner: is it true that "recently burned peatland has a lower water infiltration rate, so burned areas produce more surface runoff"? And should the groundwater model give burned cells different parameters?

Labels: *full text*, *abstract*, *checked* (the number was re-read in the downloaded text on 2026-10-28).

## Short answer

The statement has two parts, and the evidence treats them differently.

- **Lower infiltration after fire: not established for tropical peat.** The two paired tropical studies found show no significant change or a mixed one. In the larger one, permeability went *up* on average. A clear drop in surface conductivity after fire is measured in UK blanket peat. Water repellency after fire is measured in boreal moss and peat.
- **More surface water on burned land: partly supported, by a different mechanism.** Fire lowers the peat surface and reduces ET, so a burned area sits closer to the water table and floods more readily: runoff when the soil is already saturated, not because rain cannot soak in. No measured runoff on burned tropical peat was found.

The claim probably comes from wildfire hydrology on mineral soils, where fire leaves a water-repellent layer and rain runs off before it soaks in. In Indonesia it merges with "kering tak balik", the irreversible drying of peat described by Andriesse (FAO 1988), which is caused by drying, not specifically by fire.

## Evidence

| Finding | Value | Site, peat | Time since fire | Method | Source | Label |
|---|---|---|---|---|---|---|
| Burned against unburned peat, pooled over 4 sites | permeability 7.73 → 9.25 cm/h (+19.6%); bulk density 0.19 → 0.21 g/cm³; no change significant (F-test, 5%) | Riau (2 sites), OKI South Sumatra, Barito Kuala South Kalimantan; acacia, oil palm, forest | 6–18 months | rings at 0–5 and 5–10 cm, laboratory | Setiawan et al. 2020, IOP Conf Ser Earth Environ Sci 504, 012020, doi 10.1088/1755-1315/504/1/012020 | *checked* |
| Direction differs by site | at one Bengkalis site burned Ks higher under acacia, lower under rubber | Bengkalis | 9 months | as above | same | *full text* |
| Burned forest against natural forest, 0–10 cm | Ks 3.39 against 6.76 cm/h; the two forests are at different sites (Tumbang Nusa, Sebangau), so site and burn are confounded; 3 plots | Central Kalimantan | about 6 years | rings | Adji et al. 2023, doi 10.3844/ojbsci.2023.251.263 | *full text* |
| Ks by land cover | forest 0.63 ± 0.36, oil palm 0.20, shrub 0.16 m/d; forest higher than every non-forest class | Ketapang, West Kalimantan | "recent" | slug tests at 1.0/3.5/6.0 m (aquifer, not surface) | Kurnianto et al., 16th International Peat Congress; Kurnianto et al. 2019, doi 10.1007/s11027-018-9802-3 | *full text* (congress), *abstract* (journal) |
| Water repellency | water drop penetration 10.1–13.5 s in burned scrub against 4.1–4.8 s under rubber (hydrophobic above 5 s) | Pulang Pisau, Central Kalimantan; 3 samples per land use | not stated | air-dried samples, so potential, not field, repellency | Damanik et al. 2021, Jurnal Agri Peat 22(2), 65–72 | *full text* |
| Irreversible drying | dried peat "very difficult to re-wet"; loses 40–75% of water-holding capacity; burning not discussed | general | — | review | Andriesse 1988, FAO Soils Bulletin 59 | *full text* |
| Surface lowering by fire | mean burned depth 0.179 ± 0.089 m; −0.17, −0.10, −0.06 m for the first three fires; −0.13 m on average where 4–7 fires | former Mega Rice Project, Central Kalimantan | multi-fire | LiDAR | Konecny et al. 2016, Glob Change Biol, doi 10.1111/gcb.13186 | *checked* |
| Bulk density near the surface | burned 0.115 ± 0.020 (n = 313) against forest 0.121 ± 0.018 g/cm³ | same | — | pits | same | *checked* |
| Burned, drained former forest | water table close to undrained forest despite the canal, "chiefly caused by large ground subsidence due to peat fires"; surface "studded with open water" in the rainy season; ET 1,374 ± 75 against 1,636 ± 53 mm/yr | Palangka Raya | years after 1997 and 2002 fires | eddy covariance 2004–2009 | Hirano et al. 2015, doi 10.1111/gcb.12653 | *checked* |
| Repellency as an explanation, not measured | ET loss "may be due to the hydrophobic dried peat soil, which prevents rainwater infiltration" | Palangka Raya | — | eddy covariance | Ohkubo et al. 2021, doi 10.1016/j.jhydrol.2021.126906 | *full text* |
| Runoff mechanism in tropical peat | saturation-excess near-surface flow dominates; infiltration-excess limited | drained agricultural peat, Malaysia (not burned) | — | hydrographs | Katimon et al. 2013, doi 10.1080/02626667.2013.815759 | *full text* |
| Ks after burning, UK | about 3 times lower on recently burned plots; recovered where the last burn was more than 15 years before | blanket peat | 4 months – 15+ years | tension infiltrometer | Holden et al. 2014, Hydrol Process, doi 10.1002/hyp.9875 | *checked* |
| Counter-evidence, UK | overland flow less frequent on burned peat (9% against 17% of visits), water table 5.3 cm deeper | blanket peat, 10 catchments | 2–10+ years | plots | Holden et al. 2015, doi 10.1002/2014WR016782 | *abstract* |
| Repellency, boreal | burned feathermoss the most repellent; unburned Sphagnum not repellent | Alberta | 1 year | drop tests | Kettridge et al. 2014, doi 10.1016/j.jhydrol.2014.03.019 | *abstract* |
| Repellency depends on water content | sharp threshold below about 1.4 g/g; burning intensifies it | laboratory | — | drying | Moore et al. 2017, doi 10.1016/j.jhydrol.2017.09.036 | *abstract* |
| Specific yield after fire, boreal | fire exposes denser peat, lowering surface Sy | Alberta | recent | cores, simulation | Thompson and Waddington 2013, doi 10.1002/wrcr.20278 | *abstract* |

## What this means for the groundwater model

1. **No infiltration cap for burned cells.** Tropical evidence does not support it, and runoff in tropical peat is saturation-excess. The model already treats it that way: water above the surface is removed each day.
2. **Surface lowering is the defensible effect, and a LiDAR DTM flown after the fires already contains it.** For other DTMs, the Konecny depths per fire are a basis for a correction, but they come from one landscape.
3. **Lower ET on burned land** (about −16% at one Central Kalimantan site, Hirano et al. 2015) is supported. It would need ET per cell, which the model does not have yet; ET is a KHG mean.
4. **Surface Ks and Sy for burned cells only as a sensitivity range:** Ks × 1/3 to × 1.2 (Holden 2014; Setiawan 2020); Sy lower in the top layer (direction from boreal peat, no tropical value).

## Gaps

- Specific yield of burned tropical peat.
- Measured runoff or overland flow on burned tropical peat.
- Field infiltration tests on burned against unburned tropical peat.
- Recovery time after fire in tropical peat.

Not read: Kurnianto 2019 full text (closed access), Sulaeman et al. 2021 full text (publisher blocked), Wösten et al. 2006 beyond the abstract.
