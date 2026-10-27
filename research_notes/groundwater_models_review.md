# Groundwater models for rewetting what-if scenarios

Research note, 2026-10-28. Question: which model can simulate the water table (TMA) of a peat KHG under a rewetting scenario (canal blocks, pumping), and map where it stays deeper than 40 cm afterwards? The established neraca air method (`docs/neraca-air-method.md`) is not touched; this is for a separate scenario model. Candidate test site: KHG Pulau Tebing Tinggi (14.10.03).

Builds on, does not repeat: `docs/references.md`, `docs/tropical-peat-hydraulic-parameters.md`, `research_notes/Peatland neraca air operational gaps/` (`peat_hydrology_methods.md`, `open_satellite_data.md`, `wtd_retrieval_validation.md`).

Labels: *full text* (body read), *abstract* (abstract, catalogue or lab page), *snippet* (search summary only), *checked* (re-read by us on 2026-10-28 against the source).

## 1. Models

| Model | Form | Canal and block | Pump | Water table skill on tropical peat | Code, licence |
|---|---|---|---|---|---|
| Our tier 2 (Urzainki 2020 form) | 2D Boussinesq, regular grid | canal fixed at DEM − 1.2 m; block lifts upstream canal pixels to a set head | no | none: every cell gave the same curve (`docs/neraca-air.md`) | ours |
| Urzainki et al. 2020 | 2D Boussinesq, 100 m, FiPy | as above | no | none; the authors state there was no quantitative validation (*full text*) | LukeEcomod/blopti, Python, MIT (*checked*) |
| Urzainki et al. 2023, Merang-Kepayang, 22,000 ha, 168 blocks | 2D peat (triangular mesh) coupled to a 1D canal network, diffusive wave | canal stage is a state; block flow `Q_b = K_b max(0, h − p + z_b)^1.5` (*checked*) | no | qualitative only: microtopography "prevented any meaningful one-to-one quantitative comparison" with 141 dipwells (*checked*) | Txart/block_effectiveness, Python, MIT (*checked*); Txart/HydroTroPe has no licence (*checked*) |
| MIKE SHE + MIKE Hydro River, Kurnianto et al. 2026, Pulau Padang | 3D/2D, 100 m, ~113,000 cells, 3 peat layers, tide boundary | 123 dams as broad-crested weirs, crest 0.6 m below ground; dynamic canal stage (*checked*) | none in the text (*checked*) | 2018 validation, 15 wells (9 automatic, 6 manual): RMSE 0.05–0.09 m, NSE 0.36–0.87 (*checked*, Table 2) | DHI, commercial |
| SIMGRO, Jaenicke et al. 2010, Sebangau | quasi-3D finite element with channels | dams along canals; how they enter the model is not stated | no | one dipwell: R² 0.74, "within 0.10 m" (*full text*, thesis chapter) | Alterra, legacy (ArcView-era) |
| MODFLOW via FREEWAT, Suryadi et al. 2021, Kahayan-Sebangau sub-PHU 5–6 | 2D grid | block heights 0.2–0.6 m at canal spacing 200–400 m; package not clear | WEL term exists, not used | NSE 0.73–0.95 at wells within 50 m of one canal, 30-day calibration only (*full text*, not re-checked) | MODFLOW, open; flopy possible |
| DigiBog_Hydro, Putra, Baird & Holden 2022 | 2.5D Boussinesq, 1 m, synthetic 0.2 km² plot | dam = two fixed ditch levels; bunds as low-K cells | no | none (scenario study) (*full text* per search, not re-checked: publisher returned 403) | DigiBog/DigiBog_Hydro, Fortran, GPL-3.0 (*checked*) |
| PEATCLSM-Trop, Apers et al. 2022 | 1D per 9 km cell | static ditch depth −0.68 m, spacing 31.4 m, K 52 m/d (*checked*); no network, no blocks | no | water level anomaly R 0.68, drained SE Asia (*checked*) | NASA GEOS, Fortran |
| DRAINMOD, Imanudin et al. 2018, oil palm on peat, Sumatra | 1D field, mid-spacing between parallel drains (Hooghoudt, Kirkham) | outlet level (controlled drainage) | no | none found on peat (*abstract*) | NCSU, Windows; licence not confirmed |
| MONALAGA, PUI Gambut dan Kebencanaan, Universitas Riau | not documented online | the product page lists canal-blocking scenarios (*checked*) | not stated | not published | not public |
| MPeat2D, Mahdiyasa et al. 2024 | 2D poroelastic bog development over ~5,000 years | none | none | none; temperate, not applied to Indonesia (*full text*) | MATLAB, Zenodo |

On MONALAGA: the UNRI product page (https://puigk.unri.ac.id/id/produk-unggulan) gives it as "Model Neraca Air Lahan Gambut" and lists "BRGM, Penyusunan Neraca Air KHG Pulau Tebing Tinggi, Riau (2020)" (*checked*). The same group's published peat balances (Sutikno et al.) are a monthly Thornthwaite-Mather water balance per sub-KHG, with no water table or canal level (*full text*, UNRI JOM papers 2021). Whether MONALAGA is that balance is not confirmed. The 2020 Tebing Tinggi report is not online.

## 2. What the literature says about our failed solver

1. **The 2D Boussinesq form is not the fault.** Urzainki 2023 and DigiBog keep it; MIKE SHE and MODFLOW solve the same Darcy flow. What separates the models with a result from ours is the inputs:
   - **Transmissivity.** Working tropical values: T = 30 m²/d (0–1 m) and 2.2 m²/d below (Jaenicke 2010); horizontal Ksat of the 0–1 m layer 8.6–173 m/d across the land-cover columns of Table 1, from slug tests and calibration (Kurnianto 2026, *checked*). Our boreal table: ~0.5 m²/d at the surface. With ours a canal cannot reach the peat, so a block cannot either.
   - **Canal stage.** Every model that simulates blocks lets the canal level respond: a 1D canal network with a weir per block (Urzainki 2023, MIKE SHE), or a canal level set per season (DigiBog; SWAP in Taufik 2019). A canal fixed at DEM − 1.2 m reproduces Urzainki 2020, which was never validated.
2. **Grid.** 100 m is what Urzainki 2020 and Kurnianto 2026 used, and Kurnianto ran ~113,000 cells. A 1,381 km² KHG at 100 m is ~138,000 cells, so it is feasible. 500 m is too coarse for effects that fade within a few hundred metres.
3. **Expected size of a block effect**, to sanity-check any run. Lateral distance means distance from the canal into the peat; along-canal distance means distance up the canal from the block.
   - Lateral, Kurnianto 2026: drainage impact into the adjacent forest averaged 9 cm at 100 m and fell below 5 cm at about 300 m with dams. Without dams it averaged 19 cm at 100 m and reached beyond 300 m (*checked*, section 3.4).
   - KHG-wide, Urzainki 2023: mean rise 1.44 cm (dry year) and 1.57 cm (wet year). Blocks did not hold the water table above −40 cm everywhere in the dry year (*checked*).
   - Along the canal, Tebing Tinggi field reports (Sutikno et al. 2023, *abstract*; UNRI JOM, *snippet* and *full text*): rewetting reaches about 100 to 400 m upstream of a block.

   A lateral effect over kilometres is wrong. Along the canal a raised stage can reach further: canal-blocking guidelines space blocks up to 2 km apart on dome tops. No effect at all points to T or the canal boundary.
4. **Pumping.** None of the tropical studies read models a pump. A pump would be a new source term on canal or peat cells (MODFLOW WEL is the standard form).
5. **One-to-one validation at 100 m is limited.** Urzainki 2023 could not do it. Compare distributions, depth-exceedance shares, and patterns with distance to canal instead.
6. **Unverified lead.** A search summary says a discussion comment on the Urzainki 2023 preprint (bg-2022-218) flags an error in the peat module's mathematics. Read it before porting that code.

## 3. Open satellite data, by role in the model

Forcing (CHIRPS, MOD16, WaPOR) is settled and not repeated here.

| Role | Dataset | Evidence | Tebing Tinggi |
|---|---|---|---|
| Regional water table check | SMAP L4 v8, `NASA/SMAP/SPL4SMGP/008` band `depth_to_water_table_from_surface_in_peat` (PEATCLSM); ~11 km, 3-hourly, to 2026-10-24 (*checked*, Earth Engine) | Not found: whether the operational product uses the tropical parameters | Seasonal anomaly only: the island is a few pixels |
| Water table pattern and timing | Sentinel-1 InSAR surface oscillation, own processing (OPERA DISP-S1 covers North America only, *abstract*) | Kalimantan: r 0.23–0.8 with groundwater level; elevation change 2.8–8.3% of the water table variation (Izumi et al. 2025, *checked*, abstract). C-band coherence lost on flooded ground (*abstract*) | Maybe; needs per-site calibration against stations |
| Wetness index | Sentinel-1 GRD; ALOS-2 PALSAR-2 ScanSAR L2.2 on Earth Engine (backscatter only) | Our test: within a station ρ −0.62 / −0.38; across stations weak (`docs/bucket_reports/*_sentinel1.md`) | Relative index only |
| L-band under canopy | NISAR: provisional products from June 2026 (*abstract*, ASF) | No peat study yet; Indonesian coverage not checked | Later |
| Sea and strait boundary | FES2022b tides (pyFES; *abstract*) | No Malacca Strait validation found | Yes, as tidal stage at the island edge |
| River stage | SWOT raster 100 m, 21-day (*abstract*) | Swath coverage of Tebing Tinggi not checked | Maybe, as a check only |
| Canal network | Dadap et al. 2021 CNN map, by request to the author (*abstract*) | Geometry only, no width, depth or blocks | Our KLHK canal layer is already there |
| Intervention effect | InSAR subsidence before and after blocks (Zahro et al. 2025, ALOS-2, *abstract*); fire counterfactual (Castro et al. 2026, iScience, *abstract*) | Methods, not open products | Maybe, with Sentinel-1 |

## 4. Tebing Tinggi as the test site

What is in the workspace (read 2026-10-28):

| Data | Content | Limit |
|---|---|---|
| `_data/Peat depth and DTM/Tebingtinggi.csv` | 1,385 survey points; 803 of 1,132 peat points with water table depth (median 77 cm); peat type (hemik 372, saprik 286, mixtures; fibrik 47 alone), thickness, nearby drainage (open 142, controlled 108), community or company land | One snapshot, late October to November 2015 (El Niño). The date field is empty; the dates come from the "last rain" column. Water table 0 is probably no data |
| `_khg/14.10.03_pulau_tebing_tinggi/00_inputs/` | 1,421 canals (116 km primary, 414 km secondary, 859 km tertiary), 168 blocks, 10 SiTMAT stations (2026) | The block layer has no year or status |
| `01_dem/inputs/` | DeltaDTM, DEMNAS | No LiDAR. Pulau Padang has a 2 m LiDAR DTM (2016) |

The data can test the baseline spatial pattern: water table against distance to canal, drainage class, land use. That is the test tier 2 failed. They cannot test the response to a block, because nothing in the workspace was measured before and after blocking. Block effects would rest on the literature ranges in section 2.

Not in the workspace: the UNRI MONALAGA Tebing Tinggi report (2020) and the hydrology studies of 2018–2019, with whatever dipwell data lie behind them. Requesting them is the owner's decision.

## 5. Options for the scenario model

| Option | What it takes | For | Against |
|---|---|---|---|
| A. A separate scenario entry point that reuses the tier 2 solver, with tropical T, 100 m and canal level set per reach (tiers 1 and 2 and the deficit unchanged) | peat table option; a canal level input | smallest step; tests whether T alone revives the canals | canal level still prescribed, no flow along canals |
| B. Port the Urzainki 2023 canal network (MIT, Python) onto our grid | 1D canal network from the canal layer and DEM; weir per block | blocks act through canal stage, as in every model that worked | the network needs canal bed and width; the flagged maths error must be checked |
| C. MODFLOW 6 via flopy, RIV/DRN with stage per reach, WEL for pumps | flopy; canal stage per reach | standard, open, has a pump term | canal stage still an input unless SFR is used; a new dependency |
| D. MIKE SHE | licence | best published skill nearby (Pulau Padang) | commercial, not Python |

A then B is the lean path. A tells, at low cost, whether the tropical T is what was missing. B adds what the block scenarios need. C is the fallback if writing a canal network is too much.

## Sources

- Urzainki et al. 2020, Biogeosciences 17:4769, doi 10.5194/bg-17-4769-2020
- Urzainki et al. 2023, Biogeosciences 20:2099, doi 10.5194/bg-20-2099-2023
- Kurnianto et al. 2026, J Hydrol Reg Stud 64:103185, doi 10.1016/j.ejrh.2026.103185 (PDF: https://nora.nerc.ac.uk/id/eprint/541143/)
- Jaenicke et al. 2010, Mitig Adapt Strateg Glob Change 15:223 (thesis chapter: https://edoc.ub.uni-muenchen.de/11761/2/Jaenicke_Julia.pdf)
- EMRP Technical Guideline 4, Canal Blocking (2009), one block per 2 km on dome tops to one per 200 m at dome edges (*full text*, not re-checked): https://luk.staff.ugm.ac.id/rawa/PLG/EMRP/TechnicalGuideline4-CanalBlocking.pdf
- Suryadi et al. 2021, J Eng Technol Sci 53(2), doi 10.5614/j.eng.technol.sci.2021.53.2.5
- Putra, Baird & Holden 2022, Hydrol Process, doi 10.1002/hyp.14470
- Apers et al. 2022, J Adv Model Earth Syst 14, doi 10.1029/2021MS002784
- Imanudin et al. 2018, J Wetlands Environ Manage 6(1):12–26 (https://www.tropicalpeatlands.org/knowledge/publication/11463-19717)
- Mahdiyasa et al. 2024, Earth Surf Dynam 12:929 (https://esurf.copernicus.org/articles/12/929/2024/)
- PUI-GK Universitas Riau, product page (https://puigk.unri.ac.id/id/produk-unggulan) and action research list (https://puigk.unri.ac.id/id/pengalaman-riset-aksi)
- Sutikno et al. 2023, Springer chapter, doi 10.1007/978-981-99-0906-3_9
- Izumi et al. 2025, Remote Sens Appl Soc Environ (https://u.muroran-it.ac.jp/imrsl/?p=354)
- Zahro et al. 2025, Sci Rep (https://u.muroran-it.ac.jp/imrsl/?p=390); Castro et al. 2026, iScience, doi 10.1016/j.isci.2026.116041
- Dadap et al. 2021, AGU Advances, doi 10.1029/2020AV000321
- Earth Engine catalogue: `NASA/SMAP/SPL4SMGP/008`; FES2022b (https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html); NISAR availability (https://nisar-docs.asf.alaska.edu/availability-overview/)
