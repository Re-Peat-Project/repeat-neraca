# A groundwater model for rewetting scenarios in the RE-PEAT neraca air: review, decisions, implementation and first test

Report of 2026-10-28, RE-PEAT GIS workstream, Departemen Teknik Geodesi UGM. Status: in development. The model runs for any KHG from its code and is scored against field data. Managed land is held at a target water table, and block and pumping scenarios from repeat-pump run against a baseline (first results for Mendahara-Batanghari, section 6.9). The model has passed the supply check where it can be made, but not the checks on levels and dynamics outside managed land.

Every number in this report comes from a file in the workspace; the file is named where the number is used. Labels on literature claims follow the research note they come from: *full text* (the body was read), *abstract* (abstract, catalogue or lab page only), *snippet* (a search summary only), *checked* (re-read against the source on 2026-10-28).

## Summary

- **Aim.** Simulate the water table (TMA) of a peat KHG under rewetting scenarios (canal blocks, pumping), and map where the peat stays deeper than 40 cm after an intervention.
- **Starting point.** The adopted neraca air has no stored water, no canal level and no blocks: a climatic balance per sub-KHG and an observation-based KHG deficit (section 1). A 2D groundwater model existed but had been frozen as a diagnostic after it gave every cell the same curve (section 1.3).
- **Review.** The models that have simulated canal blocks on tropical peat share the 2D groundwater-flow form of our solver. What separates them from our failed runs is their inputs: tropical transmissivity, 100 to 1,000 times our boreal table, and a canal level that responds to blocks (section 2).
- **Decisions.** The groundwater model is to become the neraca air once it passes a field gate, and the climatic balance stays as the fallback for KHG without an adequate DTM. One solver is now shared by repeat-neraca and repeat-pump. The gate was fixed in code before any run, and nothing is fitted (section 3).
- **Implementation.** A new command, `repeat-neraca-model`, builds its inputs from the KHG folder, fetches its forcing (cached), runs the solver with a canal level per canal class, records the water the canals exchange with the peat, and scores the result against field points next to two simple predictions (section 4). The established outputs are unchanged (74 of 74 files identical, section 4.4).
- **First test, Pulau Tebing Tinggi, 2015 survey.** All six configurations fail the gate (Spearman 0.01 to 0.05). The model is 48 to 71 cm too shallow (section 6). The survey itself cannot test the spatial pattern, however. Its depths do not follow distance to canal (Spearman 0.00) or peat thickness (0.02). Between field teams working the same 2 km block, the team accounts for 76% of the variance, and visit timing does not explain this (section 6.5).
- **Second test, Sugihan-Lumpur, 51 stations, 2026.** The timing is right (median per-station r 0.87) and the amplitude is not: the model drains to 122 cm (KHG mean, end of September) while the stations hold about 42 cm. Its canals take 58 mm out of the peat in the dry season, where the stations imply 290 mm supplied. The water table of this managed KHG is set by canal operation, which the model does not yet represent (section 6.4, 7).
- **Three KHG with stations (section 6.6).** At Sugihan-Lumpur, Kampar-Gaung and Mendahara-Batanghari the stations in managed land stay almost flat through the dry season (median drawdown 1 to 12 cm), while the model drains by 19 cm or more in every configuration. A measured, lower Sy (Ismail et al. 2021) makes it worse. Community stations at Mendahara-Batanghari drop 63 cm (raw record; 11 cm after screening, section 6.13). The missing term is water supplied to managed land.
- **Managed land held at a target (section 6.7).** Holding plantation licences at 0.4 m gives a water-management supply close to what the stations imply at Sugihan-Lumpur (233–324 mm against 290 mm) and within a factor of 2 at Mendahara-Batanghari. Community land outside licences is now the weak part: about 95 cm in the model against 29 cm observed at 6 stations (raw record; 44 cm after screening, section 6.13).
- **First intervention scenarios (section 6.9).** Blocks from repeat-pump cut the dry-season days deeper than 40 cm by 26 days within 150 m of a block and by 9 days at 150–350 m, with no effect beyond 1 km, which matches field reports. Pumping on the sub-KHG repeat-pump marks for water takes about 50 million m³ in June to September at Mendahara-Batanghari and reduces the sub-KHG still needing rewetting from 12 to 9 of 29.
- **What the target and canal levels rest on (sections 6.10, 6.11).** Concession station readings pile up just inside the 40 cm limit, so they cannot measure the managed water table; published plantation water tables are 0.6–0.85 m. Across targets of 0.4 to 0.8 m the open land changes by at most 1 cm, while the supply falls by a factor of 2 to 5. Canal levels measured in the Pulau Padang LiDAR (primary 0.8 m, secondary and tertiary about 0.3 m) are far shallower than the assumed 1.2 m and change the open land much more. No fixed canal level gives both the level and the dry-season drop of community land.
- **Canals inside cells and a canal water balance (section 6.12, D18, D19).** Canal cells outside managed land now stay free and exchange water with the canal in them; a canal store per sub-KHG lets the canal level fall through the dry season. Against a 5 m grid the leak term removes the wet bias of fixed cells (up to 19 cm at 200 m) to within 0.7 cm. On the three KHG, compared on the same cells, neither changes the open land by more than 5 days; the canal level itself (1.2 m against the LiDAR levels) moves it by 12 to 20 days. The store's canals sit a season median 0.17 to 0.55 m below the land, and mass closes to within 0.01%.
- **Outliers in the station record (section 6.13).** SiTMAT's QC passes restarts after gaps, settling days and stuck loggers: a screening rule leaves out 17% of concession and 23% of community readings nationally. At Mendahara-Batanghari the 63 cm dry-season fall of the community stations rests on a 3-day July fragment and a restart week at about 70 cm above the ground. On the screened record the stations sit at 44 cm and fall 11 cm (19 August to 30 September). On the 100 m grid the LiDAR canal levels match that level and fall (47 and 6 cm) and the canal store overshoots (56–63 and 24 cm); at 200 m the 4 comparable stations fall 2 cm against 21 cm simulated. Correlations have not been recomputed on the screened record.
- **Open decisions.** How to represent managed canal levels or supply; which evidence the gate rests on; whether to address the surface specific yield and the forcing (section 8).

## Questions and answers

Plain answers for readers new to groundwater modelling.

**What does the model produce: a map, or a table? Per sub-KHG or something else?**
A map. The KHG is cut into square cells, 100 m or 200 m across, and the model computes the water-table depth of every cell. A run writes:
- maps (GeoTIFF) of water-table depth per cell, one averaged over a chosen period and one for the last day;
- a daily table for the whole KHG: average depth, share of the area deeper than 40 cm, rain, ET, and the water the canals take from or give to the peat;
- tables at the stations or field points, comparing the model with what was measured;
- a report.

The basic unit is the grid cell. Each run also writes a table per sub-KHG (`model_units.csv`; one row for a KHG without sub-KHG units) and season maps: days each cell was deeper than 40 cm, the season's mean depth, and the water supplied to managed land (section 6.8).

**The water table changes over time. Does a result hold only for one date?**
The model calculates the water table every day from the start to the end of a run, so the result is a daily series for every cell. A map is either a snapshot of one day or a summary over a period, for example the average over the dry season. Runs save the period average, the last day, and season summaries (June to September by default), including the days each cell was deeper than 40 cm. Any other date or season can be chosen (`--season`).

**Why can we not yet run every KHG and simulate canal blocks and pumps?**
The program already runs any KHG from its code: it fetches its own data, and a run takes 6 to 35 minutes. What is missing is trust in the answer, and the intervention part:
1. It does not yet match reality well enough. At the stations it gets the timing right, but in managed land it lets the water table drop far more in the dry season than the stations show (section 6.6), and it does not yet tell wetter from drier places. A scenario map built on it would show the wrong areas as still needing rewetting.
2. Canal water levels are unknown, and they control the result. In managed land, companies hold canal water up with blocks, gates and pumping. The model assumes a fixed canal level, which is the main cause of point 1. Blocks and pumps work by changing canal levels, so this matters doubly.
3. Blocks and pumps are now in the model, taken from repeat-pump (section 6.9): a block holds the canal water of its reach, and pumping holds the served land at a target and reports the water it takes. They have been run for one KHG so far.
4. Many KHG lack good inputs. The model needs a good elevation map: LiDAR covers few KHG, and open DEMs can be off by as much as a peat dome's relief. Peat depth maps are weak too (at Tebing Tinggi the map barely matched the field measurements). Those KHG keep the climatic balance as the fallback.
5. Few KHG can be checked. Only KHG with enough water-table stations can show whether the model works; elsewhere it would run unchecked.

The machinery runs everywhere. Managed land and canal levels have to be right first, on the sites we can check; blocks and pumps come next. Only then are scenario maps reliable, and only on KHG with adequate inputs.

## 1. Starting point

### 1.1 The adopted neraca air (2026-10-26)

From `docs/neraca-air-method.md` and `README.md`:

- **Climatic balance per sub-KHG:** `WB = P (1 − I) (1 − C) − ET`, monthly. C = 0.12; I from the unit's WorldCover land cover. P is CHIRPS, taken as the KHG mean; ET is MOD16, with WaPOR as second source. A flag, `balance_stable_ok`, says whether the order of units holds across ET products and years (p < 0.01).
- **KHG supply deficit:** `deficit = max(0, −Σ(P − E) − Sy Δz_obs)`, 1 June to 31 October 2026, Sy 0.15, from SiTMAT stations and ERA5. Sugihan-Lumpur: about 290 mm (`docs/neraca-air.md`).

Neither output can answer a what-if question. The balance has no storage, canal level or blocks, so an intervention has nothing to act on. The deficit is a mass balance on observed water tables and has no spatial form.

### 1.2 Why a gridded model

The questions asked of the module are spatial and conditional: if blocks are built here, or pumps run there, which peat stays dry? That needs a state (the water table per cell), a mechanism for canals to drain or supply the peat, and a way for an intervention to change that mechanism. The 2D groundwater-flow equation with canals as boundary conditions provides all three. Every model in section 2 that simulated canal blocking has this structure.

### 1.3 Earlier attempts and how they failed

From `docs/neraca-air.md` (runs of 2026-10-16 to 2026-10-20, Sugihan-Lumpur and Kampar-Gaung, SiTMAT stations, ERA5 forcing):

1. **Bucket model** (retired 2026-10-26; `docs/bucket_experiments_README.md`). It fitted a drainage coefficient to the stations and failed its spatial skill check.
2. **Tier 1, one KHG-level water table.** Timing right, amplitude wrong. At Sugihan-Lumpur, rain minus evaporation from June to October was −306 mm. With Sy 0.14 to 0.2 that implies a 1.5 to 2 m fall, while the stations fell 14 cm. The simulated mean was 66 cm against 43 cm observed (correlation 0.96).
3. **Tier 2, 2D groundwater at 500 m.** "The canals do nothing." With the boreal peat table, transmissivity is about 0.5 m²/day at the surface and near zero by 0.6 m depth, so a drain takes years to affect the peat. Every free cell, and every station, followed the same curve; the water table per sub-KHG was identical (65 cm).
4. **More transmissivity made it worse.** Scaling T by 10 to 1,000 pulled the water table towards a canal level fixed 1.2 m below the surface, while the stations sat at 35 to 55 cm.
5. **Tier 2 with the tropical-large peat table** (`docs/reports/peat_table/sugihan_lumpur_t2_tropical-large.md`): sub-KHG means 23 to 29 cm; Spearman across 51 stations −0.14 (mean level) and −0.19 (peak depth).

The diagnosis recorded then: the observed water tables are held by water from outside the rain balance (canal, river and tidal inflow, gates, pumping), and the model had no such supply. The tier 2 diagnostic was frozen on 2026-10-26.

## 2. Review of models and data

Full review: `research_notes/groundwater_models_review.md`. Earlier notes it builds on: `docs/references.md`, `docs/tropical-peat-hydraulic-parameters.md`, `research_notes/Peatland neraca air operational gaps/`.

### 2.1 Models

| Model | Form | Canal and block | Pump | Water-table skill on tropical peat | Code, licence |
|---|---|---|---|---|---|
| Our tier 2 (Urzainki 2020 form) | 2D Boussinesq, regular grid | canal fixed at DEM − 1.2 m; a block lifts upstream canal cells to a set head | no | none; every cell gave the same curve | ours |
| Urzainki et al. 2020 | 2D Boussinesq, 100 m | as above | no | none; the authors state there was no quantitative validation (*full text*) | LukeEcomod/blopti, Python, MIT (*checked*) |
| Urzainki et al. 2023, Merang-Kepayang, 22,000 ha, 168 blocks | 2D peat (triangular mesh) coupled to a 1D canal network (diffusive wave) | canal stage is a state; block flow `Q_b = K_b max(0, h − p + z_b)^1.5` (*checked*) | no | qualitative only: microtopography "prevented any meaningful one-to-one quantitative comparison" with 141 dipwells (*checked*) | Txart/block_effectiveness, Python, MIT (*checked*) |
| MIKE SHE + MIKE Hydro River, Kurnianto et al. 2026, Pulau Padang | 3D/2D, 100 m, ~113,000 cells, 3 peat layers, tide boundary | 123 dams as broad-crested weirs, crest 0.6 m below ground; dynamic canal stage (*checked*) | none in the text (*checked*) | 2018 validation at 15 wells: RMSE 0.05–0.09 m, NSE 0.36–0.87 (*checked*) | DHI, commercial |
| SIMGRO, Jaenicke et al. 2010, Sebangau | quasi-3D finite element with channels | dams along canals; representation not stated | no | one dipwell: R² 0.74, "within 0.10 m" (*full text*, thesis chapter) | Alterra, legacy |
| MODFLOW via FREEWAT, Suryadi et al. 2021, Kahayan-Sebangau | 2D grid | block heights 0.2–0.6 m at canal spacing 200–400 m | WEL term exists, not used | NSE 0.73–0.95 near one canal, 30-day calibration only (*full text*, not re-checked) | open; flopy |
| DigiBog_Hydro, Putra, Baird & Holden 2022 | 2.5D Boussinesq, 1 m, synthetic 0.2 km² | dam = two fixed ditch levels | no | none (scenario study) (not re-checked: publisher refused access) | Fortran, GPL-3.0 (*checked*) |
| PEATCLSM-Trop, Apers et al. 2022 | 1D per 9 km cell | static ditch depth −0.68 m, spacing 31.4 m, K 52 m/d (*checked*); no network, no blocks | no | water-level anomaly R 0.68, drained SE Asia (*checked*) | NASA GEOS, Fortran |
| DRAINMOD, Imanudin et al. 2018 | 1D field, between parallel drains | outlet level | no | none found on peat (*abstract*) | NCSU, Windows |
| MONALAGA, PUI Gambut dan Kebencanaan, Universitas Riau | not documented online | product page lists canal-blocking scenarios (*checked*) | not stated | not published | not public |
| MPeat2D, Mahdiyasa et al. 2024 | 2D poroelastic bog development over ~5,000 years | none | none | none; temperate (*full text*) | MATLAB |

MONALAGA ("Model Neraca Air Lahan Gambut") was applied to KHG Pulau Tebing Tinggi in 2020 for BRGM, according to the UNRI product page (*checked*). The group's published peat balances are monthly Thornthwaite-Mather balances per sub-KHG, with no water table or canal level (*full text*, UNRI JOM 2021). Whether MONALAGA is that balance is not confirmed.

### 2.2 What the review implies for our solver

- **The equation is not the fault.** Urzainki 2023 and DigiBog solve the 2D Boussinesq equation; MIKE SHE, SIMGRO and MODFLOW solve the same Darcy flow. What separates them from our runs is two inputs:
  - **Transmissivity.** Tropical values: T 30 m²/d in the top metre and 2.2 m²/d below (Jaenicke 2010); horizontal Ksat of the top metre 8.6–173 m/d across land-cover classes (Kurnianto 2026, *checked*); Urzainki 2023 surface T 50 or 500 m²/d. Our boreal table: 0.59 m²/d at the surface (`docs/tropical-peat-hydraulic-parameters.md`).
  - **Canal stage.** Every model that simulates blocks lets the canal level respond to them, either through a canal network with a weir per block or a canal level set per season. A canal fixed at DEM − 1.2 m is the Urzainki 2020 rule, which its authors did not validate.
- **Grid.** 100 m is what Urzainki 2020 and Kurnianto 2026 used. Block effects fade within a few hundred metres of the canal, so 500 m is too coarse.
- **Expected size of block effects**, to sanity-check a run (lateral means into the peat from the canal):
  - lateral, Kurnianto 2026: drainage impact 9 cm at 100 m, under 5 cm by about 300 m, with dams; 19 cm at 100 m without (*checked*);
  - KHG-wide, Urzainki 2023: mean rise 1.44 cm (dry year) and 1.57 cm (wet year) (*checked*);
  - along the canal, Tebing Tinggi field reports: rewetting about 100 to 400 m upstream of a block (*abstract*, *snippet*).
- **Pumping.** None of the tropical studies read models a pump. It would be a new source term.
- **One-to-one validation at 100 m is limited** by sub-grid microtopography (Urzainki 2023). Compare distributions, exceedance shares and patterns with distance to canal.

### 2.3 Open satellite data

From the review, section 3. Forcing (CHIRPS, MOD16, WaPOR) is settled. For a gridded model:

| Role | Dataset | Use at Tebing Tinggi |
|---|---|---|
| Regional water-table check | SMAP L4 v8 band `depth_to_water_table_from_surface_in_peat` (PEATCLSM), ~11 km (*checked* on Earth Engine) | seasonal anomaly only |
| Water-table pattern and timing | Sentinel-1 InSAR surface oscillation; Kalimantan r 0.23–0.8 with groundwater level (Izumi et al. 2025, *checked*, abstract) | possible, needs per-site calibration and own processing |
| Sea boundary | FES2022b tides (*abstract*) | yes |
| Intervention effect | InSAR subsidence before and after blocks; fire counterfactual (Castro et al. 2026, *abstract*) | methods, not products |

### 2.4 Peat parameters measured in Sumatra and Kalimantan

`research_notes/peat_parameters_sumatra_kalimantan.md` (searched 2026-10-28, key numbers re-checked in the downloaded texts):

- **Specific yield.** A surface Sy of 0.6, as in both Urzainki 2023 sets, fits intact forest with the water table near the surface (about 0.56 derived from Deshmukh et al. 2023 at Kampar; 0.33–0.48 derived for Sebangau). Drained peat points to 0.1–0.3: Ismail et al. 2021 (0.3 at the surface, 0.1 at −1.5 m, Pulau Padang, *abstract*) and Kurnianto et al. 2026 (0.10–0.15, calibrated, *checked*).
- **Calibrated models disagree.** Urzainki 2023 (Sy 0.6) and Kurnianto 2026 (Sy 0.10–0.15, K 35–173 m/d in the top metre) both fit their stations on drained Sumatran peat.
- **Water tables in drained peat.** Acacia 70 ± 17 cm, adjacent forest 47 ± 22 cm (Evans et al. 2019, 312 sites, *checked*).
- **Dry-season recession** in South Sumatra, August 2019: 0.39 to 1.68 cm/d. One station, Padang Sugihan-2 (1.45 cm/d), lies inside KHG Sugihan-Lumpur (Irfan et al. 2021, *checked*).
- **ET.** 1,374–1,636 mm/yr on Central Kalimantan peat, falling by 19–33 mm for every 10 cm deeper minimum water table (Hirano et al. 2015, *checked*). No comparison of MOD16 or WaPOR with eddy covariance on Indonesian peat was found.

### 2.5 Burned peat

`research_notes/burned_peat_hydrology.md` (searched 2026-10-28; key numbers re-checked in the downloaded texts). The project owner asked whether recently burned peat has a lower infiltration rate and so more surface runoff.
- **Lower infiltration after fire is not established for tropical peat.** Across four Indonesian sites, 6–18 months after fire, permeability rose on average from 7.73 to 9.25 cm/h, and no change was significant (Setiawan et al. 2020). A clear drop in surface conductivity after burning, about threefold, is measured in UK blanket peat (Holden et al. 2014).
- **More surface water on burned land is partly supported, by a different mechanism.** Fire lowers the surface: −0.17, −0.10 and −0.06 m for the first three fires in Central Kalimantan (Konecny et al. 2016). Burned, drained former forest had 16% lower ET than undrained forest and open water in the rainy season (Hirano et al. 2015). Runoff in tropical peat is saturation-excess (Katimon et al. 2013).
- **For the model:** no infiltration cap for burned cells. A post-fire LiDAR DTM already holds the lowered surface. Lower ET on burned land needs ET per cell; a different surface Ks or Sy is defensible only as a sensitivity range.

## 3. Decisions

| # | Date | Decision | Reasons | Alternatives considered | Decided by |
|---|---|---|---|---|---|
| D1 | 2026-10-28 | The scenario model lives in repeat-neraca as a separate command. No new repository | One water model per project; repeat-neraca already holds the solver, peat tables and KHG readers | a new repository; a module in repeat-pump | project owner |
| D2 | 2026-10-28 | The groundwater model becomes the neraca air once it passes a field gate. The climatic balance stays as the fallback, and the downstream outputs switch only after the gate | Scenarios need a state and a canal mechanism (section 1.2). LiDAR covers few KHG, and open DEM errors are of the order of dome relief (`research_notes/Peatland neraca air operational gaps/open_satellite_data.md`), so many KHG cannot run a gridded model credibly | replace the balance at once; keep the two methods unrelated | project owner, on the proposal in this work |
| D3 | 2026-10-28 | One solver, owned by repeat-neraca (`repeat_neraca.groundwater`). repeat-pump depends on it through a GitHub archive pinned to tag `v0.2.0` | The solver and table existed twice, byte-identical. Users of the QGIS plugin must install without setting up repeat-neraca by hand | `git+https` (needs git on user machines); a copy in each package; the solver in repeat-common | project owner; install paths tested (section 4.3) |
| D4 | 2026-10-28 | Repository tidy: groundwater modules under `groundwater/`; command paths, console commands and output names unchanged | The package mixed three methods at one level | leave as is | project owner |
| D5 | 2026-10-28 | Model form: 2D nonlinear Boussinesq on a regular grid, implicit Euler with Picard iteration (the existing solver) | Section 2.2. It is open, in Python, already tested, and shared with repeat-pump | MODFLOW 6 via flopy (fallback if a canal network is too much to write); MIKE SHE (commercial); DRAINMOD and PEATCLSM-Trop (1D, no maps); DigiBog (1 m, Fortran) | proposal in this work |
| D6 | 2026-10-28 | Peat hydraulics: the tropical sets of Urzainki et al. 2023 (`tropical-small`, `tropical-large`) as the working options; the boreal table kept as the known failure; nothing fitted | Section 2.2. The surface Sy of 0.6 in both tropical sets is not supported by measurements (Cobb and Harvey: 0.29; Ismail et al.: up to 0.3), which `docs/tropical-peat-hydraulic-parameters.md` already records | fit Sy and T to the stations; use the measured Sy shape | proposal in this work; fitting deferred (D11) |
| D7 | 2026-10-28 | Canal boundary, first step: a fixed level per canal class (primary, secondary, tertiary), or a class left unfixed. The canal network with weirs comes with the block scenarios | Tests the transmissivity before the canal mechanism changes, so the two are not confounded | port Urzainki 2023's canal network now | proposal in this work |
| D8 | 2026-10-28 | Forcing: CHIRPS and MOD16, KHG mean, dekad totals spread evenly over their days, fetched from Earth Engine into `03_neraca/inputs/model/` | The same products as the climatic balance; a separate folder leaves the balance's 2018–2026 tables untouched | ERA5 (used by the deficit); daily CHIRPS | proposal in this work |
| D9 | 2026-10-28 | DTM: the corrected surface from repeat-dem where it exists; for DeltaDTM without one, the raw clip, said so in the report | DeltaDTM is itself a bare-earth product; Tebing Tinggi has no LiDAR and no corrected DTM yet | DEMNAS (1.86 m above the survey elevations, section 5) | proposal in this work |
| D10 | 2026-10-28 | Domain: the whole KHG, peat depth from the KHG's raster with gaps filled by the median; only field points recorded as peat are scored | Neither peat mask separates the survey's peat and mineral points (section 5). With the tropical sets, T depends on peat depth d through exp(−2.5 d), which is below 0.007 for d > 2 m, so the weak depth raster matters little | mask non-peat cells out; give them a small depth | proposal in this work |
| D11 | 2026-10-28 | Validation: a generic field-points table per KHG; zero depths read as missing; implausible depths flagged; a gate fixed in code before any run; two simple predictions scored the same way; no parameter fitted. If one is ever chosen from the scores, whole transects or teams are held out | The gate must not drift towards whatever a run produces. A model that cannot beat distance to canal adds nothing about where peat is dry | in-sample calibration; station-only checks | proposal in this work |
| D12 | 2026-10-28 | Reproducibility: every step runs from the KHG code; fetches are cached; every number in this report is written by a script | Workspace rule 4; scale to all 865 KHG | — | workspace rules |
| D13 | 2026-10-28 | Managed land is held at a target water table by water management: canals in plantation licences (PBPH, oil palm; 2025 licence layer) are fixed at the target, and each day a managed cell that fell below it is brought back. The water this takes is the model's water-management supply. Default target: 0.4 m, the PP 57/2016 compliance level. A calibrated alternative, `stations-loo`, gives each licence the median level of the concession stations outside it | Across three KHG, stations in managed land stay almost flat through the dry season while the model drained them (section 6.6); a fixed canal level supplies too little. For scenarios the question becomes how dry unmanaged land gets and what blocks or pumps change there | a supply term per canal cell sized from the deficit; canal levels per reach from stations | project owner, on the proposal in this work |
| D14 | 2026-10-28 | The gate for managed-land runs: stations in managed land are flagged as imposed and left out; levels and dynamics are scored on stations outside managed land; and the model's water-management supply must lie within a factor of 2 of the station-based deficit (`fieldcheck.SUPPLY_RATIO`). Amended the same day, after the Kampar-Gaung runs and at the project owner's request: the check also passes when the two are within 50 mm (`SUPPLY_ABS_MM`, about two weeks of dry-season ET). In a near-neutral dry season the deficit is close to zero, and a ratio of two small numbers fails on small absolute differences | Holding a target makes the stations in managed land agree by construction. What stays independent is unmanaged land and the supply | scoring all stations | proposal in this work, set before the first managed run |
| D15 | 2026-10-28 | Inputs from `_data` with fallbacks, applied cell by cell where possible. Each run writes `inputs.csv` (input, source, share of the KHG): peat depth from the KHG's raster, then the BBSDLP 1:50k depth classes (class midpoints; 8 m assumed for > 700 cm), then the KHG median; managed land from the national licence layer; target from regulation or stations | Not every KHG has every input; national layers cover all 865 KHG | one source per input, failing where it is missing | project owner (fallbacks requested), proposal in this work |
| D16 | 2026-10-28 | Peat base: no ET is taken from a cell whose water table is below the peat. Existing BRGM/PPEG canal blocks (3,057 realised at Kampar-Gaung) are left for the block step, with repeat-pump's directed canal network, instead of a radius rule now | With a measured low Sy at depth, unlimited ET took the water table below the peat (section 6.6). A radius rule for blocks would add a free parameter | blocks by radius now | proposal in this work |
| D17 | 2026-10-28 | Interventions come from repeat-pump. A block scenario fixes the canal cells of each block's reach (`sekat_reach`: the canal stretch a block holds water in, with the water depth below the land) at that level; where a managed or block level meet, the higher water level is kept. A pumping scenario holds the land repeat-pump marks for water supply (`interventions`, sub-KHG whose intervention includes water) at a target water table, like managed land; the water this takes is the pumping need. `scripts/compare_scenarios.py` compares scenarios with a baseline per sub-KHG | Both modules then use one canal network and one set of block positions; reach depths are relative to the land, so they apply on any DTM | a canal network inside repeat-neraca (Urzainki et al. 2023); pumps as point sources | project owner (blocks and pumps agreed), proposal in this work |
| D18 | 2026-10-29 | Canals narrower than a cell (`--canal-cells leak`): canal cells outside managed land stay free and exchange `q = 12 (L/dx) max(1, L/dx) T(z) (h_canal − h)` with the canal in them, L the mapped canal length in the cell. The factor 12 follows from the Hooghoudt parabola: under uniform recharge the mean head of a strip drained by a canal through it lies `q s²/(12 T)` above the canal, s the strip width, so a canal crossing a cell has a conductance of 12 T; a cell holding more canal than its width drains strips of width dx²/L. T is taken at the start of each step. Canals in managed land (held at the target) and block reaches stay fixed cells. Stations on the freed cells are scored, so the station set of a gate depends on the canal mode | Fixed whole cells (`all_touched`) covered 37–40% of the grid at 200 m and left most stations unscored. Against a 5 m grid that resolves the canal, fixed cells made the land 2–19 cm too wet; the leak with factor 12 was within 0.7 cm, the closest of the factors tried (section 6.12) | a river conductance with a bed resistance (unmeasured); the factor fitted to stations | project owner (asked for it), proposal in this work |
| D19 | 2026-10-29 | Canal water balance (`--canal-store`, implies D18): one canal store per sub-KHG (one for the whole KHG without units), its level y relative to the class levels of `--drawdown`, which act as the outlet sill. Each day `A Δy = Σ q_exchange + (P − E) A − A max(0, y)/τ`, with A the canal water surface (length times width per class), solved implicitly and iterated with the groundwater step (secant per store). A canal whose level falls to its bed is dry and only drains its cell. Widths 8/3/1 m and beds 3/1.5/1 m below the land for primary/secondary/tertiary, from Hooijer et al. 2012, Evans et al. 2019, Vernimmen et al. 2020, Urzainki et al. 2023 and Ismail et al. 2021; ET of the forcing on the water surface; τ = 1 day, with 0.1 day added as a band after Kampar-Gaung fell below the canal-depth range (section 6.12) | No fixed canal level gave the community stations both their level and their dry-season fall (section 6.11). No canal level series exists for these KHG, so the stage has to come from a balance | the diffusive-wave canal network of Urzainki et al. 2023 (canal slopes, roughness and outlet stages all unmeasured); a seasonal level from data (none in hand) | project owner, on the proposal in this work |
| D20 | 2026-10-29 | Station screening (`fieldcheck.screen`): split a record at gaps of 7 days or more; leave out pieces shorter than 14 days, the first 7 days of each piece and runs of 7 or more identical values; count day-to-day jumps over 30 cm. Thresholds chosen after looking at the Mendahara-Batanghari records. Used for reporting next to the raw record; the gates still score the raw record | SiTMAT's QC passes restarts at shifted levels and stuck loggers; at Mendahara-Batanghari the community stations' dry-season fall rested on them (section 6.13) | thresholds on the level itself (flooding is possible in low land); dropping whole stations | project owner (asked to acknowledge outliers), rule written in this work before scoring with it |
| D21 | 2026-10-29 | Recommended set-up: canals inside cells (D18) at the LiDAR levels (0.8/0.3/0.3 m), no canal store; managed land held at 0.4 m (band 0.4–0.8 m for supply); gates score the screened station record (`--screen-stations`). Defaults of the command are unchanged, so earlier runs reproduce byte for byte | The raw record carries logger restarts and stuck values; on the screened record and the 100 m grid this set-up matches the community stations, while the canal store overshoots and rests on an unmeasured outlet constant (section 6.12) | the canal store as default; scoring the raw record | project owner (asked to decide), proposal in this work |
| D22 | 2026-10-30 | Optional cap on the water management supply (`--supply-cap <mm>`, `deficit` or `climate`, the last from the KHG's own rain and ET, section 6.16): each managed cell is topped up to its target only until it has received the cap over the window (the last top-up exact); after that the cell falls with the water table. Off by default. With `deficit` the cap and its window come from the station-based deficit (`runs/deficit/neraca_khg.csv`) and the gate's supply check is not testable, since it would pass by construction | A level held at exactly the target everywhere, with no cell deeper, does not look like water and hides the spread the concession stations show (section 6.15); a supply that is limited lets the level fall where the water runs out | the hard target as the only option (kept as the default); a daily pump rate (not measured) | project owner (asked to decide whether the capped run becomes the recommended set-up), proposal in this work |
| D23 | 2026-10-30 | Existing canal blocks are in the model by default (`--existing-blocks brgm`): the BRGM/PPEG `Sekat Kanal` points of `00_inputs/blocks.gpkg`; canal cells within `--block-radius` (200 m) of a block are held at `--block-level` (0.4 m below the land), or at the class level where that is shallower. `--existing-blocks none` reproduces earlier runs byte for byte; run names get `_eb` | A canal behind a block keeps its water; the layer is the only record of existing blocks and was lying unused (D16 deferred it to a directed canal network). The layer has points only, no crest level, no flow direction, record year mostly 2018: the 0.4 m level and the 200 m radius are assumptions (the PP 57/2016 limit; field reports of rewetting 100 to 400 m along the canal) | a directed canal network with block reaches (needs the canal topology, which is incomplete and has dangles); leaving blocks out | project owner chose it as the default regardless of the test result; to be revisited if the level or radius is measured |
| D24 | 2026-10-30 | Canal levels of the recommended set-up (D21) differ by class: primary 0.80 m, secondary 0.32 m, tertiary 0.24 m below the land (were 0.8 / 0.3 / 0.3) | These are the median depths of the mapped canal line on the 2 m Pulau Padang LiDAR DTM (section 6.10, `docs/reports/lidar_canal_levels_14.10.01.md`: secondary 0.32 m, tertiary 0.24 m, interquartile ranges 0.13 to 0.75 and 0.08 to 0.65 m). The earlier 0.3 for both was a rounding of the two medians. Larger canals are deeper (Ismail et al. 2021: drains 1 to 10 m wide, up to 5 m deep). Still shallow bounds: the secondary and tertiary lines are partly below the DTM pixel and LiDAR returns little from water | 0.3 for both; a literature value (no source measures canal level by class) | project owner, who asked for the classes to differ |
Data in `_data` considered for the model, with what was used:

| Layer | Coverage | Used for |
|---|---|---|
| 2025 business licences (`landstatus/ALL_Updade__IZIN_USAHA…`) | national | managed land (PBPH, oil palm), clipped into `00_inputs/national/izin_usaha_2025.gpkg` on first use |
| Modelled peat depth per KHG (`Peat depth and DTM/PeatDepth_*`) | about 70 KHG in Sumatra and Kalimantan | peat depth (`00_inputs/peat_depth.tif`) |
| BBSDLP peat depth classes 1:50k (`kedalaman_gambut_bbsdlp.gpkg`) | national | peat-depth fallback, cell by cell |
| SiTMAT stations (`repeat-sitmat`) | 178 KHG with stations | targets in `stations-loo` mode; checks |
| LiDAR DTM (`lidar_klhk`, `lidar_pulau_padang_2016`), DeltaDTM, DEMNAS | regional; national | DTM by variant |
| BRGM/PPEG existing infrastructure (`infrastruktur_hidrologis_existing_BRGM_Indonesia.gpkg`) | national | not yet: block step (D16) |
| Peat ecosystem function 2017, forest area 2023 (`landstatus/`) | national | not in the physics; for breakdowns of results |
| Burnt area 2015–2026 | national | not in the physics: lower infiltration after fire is not established for tropical peat; the supported effects are a lower surface (in a post-fire LiDAR DTM already) and lower ET, which needs ET per cell (`research_notes/burned_peat_hydrology.md`) |

**The gate** (`groundwater/fieldcheck.py`, set before the first run): on the unflagged field points, the model's Spearman across points is at least 0.3 and above that of the distance-to-canal prediction, and its RMSE is below that of the constant prediction. The constant prediction is the median observed depth. The distance prediction is a regression of observed depth on ln(1 + distance to the nearest canal), fitted to the same points, so it is favoured.

## 4. Implementation

### 4.1 Package layout and modules

`repeat-neraca`, version 0.3.0 (0.2.0 before D18 and D19). The new and moved modules:

| Module | Content |
|---|---|
| `groundwater/solver.py`, `groundwater/data/` | 2D Boussinesq solver and peat tables; shared with repeat-pump (D3) |
| `groundwater/grid.py` | a KHG on a metric grid: boundary, DTM, peat depth, canals by class |
| `groundwater/simulate.py` | daily run with a fixed level per canal class; daily water flux from canal and edge cells into the peat, `Σ T_face (h_fixed − h_free)`; from 0.3.0 canals inside free cells (`Boundary.leak_length`, D18) and the canal store (`CanalStore`, D19) |
| `groundwater/fieldobs.py` | field water-table points as one generic table per KHG (`00_inputs/field_wtd.csv`), with a reader per survey format |
| `groundwater/fieldcheck.py` | scores, the two simple predictions, the gate, breakdowns, single-day sensitivity |
| `model.py` | the command `repeat-neraca-model --khg <code> --dem <variant>` |
| `scripts/model_sweep.py` | runs a set of configurations in parallel and writes one report |
| `scripts/check_field_inputs.py` | checks the survey against the gridded inputs and writes one report |

### 4.2 What a run does

1. Finds the KHG folder from the code (`repeat_common.khg.folder`) and builds its inputs (D9, D10).
2. Reads the daily forcing, fetching it from Earth Engine when missing (cached per year).
3. Starts saturated on the first day (a wet-season start) and steps one day at a time.
4. Records per day: the KHG-mean depth and the share deeper than 40 cm over the free cells, the water put into the peat by canal and edge cells, and the depth at every field point.
5. Writes `model_series.csv`, `model_depth_window.tif`, `model_depth_end.tif`, `field_points.csv`, `field_scores.json`, `field_day_sensitivity.csv`, `model_report.md`, `run_config.json` and `registry_snapshot.json` into `03_neraca/<dem>/runs/model/<run>/`.

### 4.3 The shared solver and its installation

repeat-pump's copy of the solver was adopted because it loads the peat table through `importlib.resources`, which also works when the package is installed normally. A test guards this. Install paths were tested with a local archive standing in for GitHub:

- A fresh install fetches repeat-neraca from the archive.
- The plugin's quick update leaves it alone while the pin is unchanged, and reinstalls it when the pin changes.
- For developers, repeat-pump must be installed before the editable repeat-neraca. Installing repeat-pump afterwards replaces the editable copy, and pip refuses both in one command.

A tracked `build/lib` folder was found to leak a stale copy of the old solver into archive installs, and was removed.

### 4.4 Checks that nothing established changed

0.3.0 (D18, D19): `solve()` takes two optional arguments, `leak_factor` and `leak_head`, and a choice of linear solver (`linear="direct"` by default; the leak runs use conjugate gradients, which matched the direct solve to 1e-10 m on the Kampar-Gaung grid at 200 m and took 3.1 s against 50 s for five days). With the defaults no existing line of the solver changes, so repeat-pump's calls are unaffected. A saved band run (Kampar-Gaung, 200 m, target 0.4 m) rerun with the new code gave 15 of 16 files byte-identical; `model_report.md` differs only in the run time. New run options add a tag to the run name (`_lk`, `_cs<τ>`) and keys to `run_config.json` only when they are set.

- A baseline of 74 output files was written before any change: climatic balance, map layers, tier 1, tier 1 with the tropical table and tier 2 at Sugihan-Lumpur, all from existing inputs. After the solver move and after the tidy, all 74 files were identical, registry hash included.
- Tests: repeat-neraca 54 passed, 2 skipped; repeat-pump 351 passed, 1 skipped (7 solver tests moved to repeat-neraca).

## 5. Test site and data: KHG Pulau Tebing Tinggi (14.10.03)

From `docs/reports/field_inputs_14.10.03.md` unless stated.

- **KHG.** 1,381 km². Canals inside the KHG: primary 96 km, secondary 408 km, tertiary 837 km (1,421 lines). 168 canal blocks, all marked built (`REALISASI`), with no build year (`Tahun` is 0 for all). Whether the 2015 survey predates the blocks is therefore an assumption.
- **DTM.** No LiDAR. DeltaDTM against the survey elevations: Pearson r 0.91, median 0.37 m lower; DEMNAS: r 0.81, 1.86 m higher. The survey does not say how its elevations were measured, so this is not on its own evidence of DTM quality.
- **Peat.** GFW peat extent marks 99% of both the survey's peat points and its mineral points as peat. The peat-depth raster marks 78% of peat points and 82% of mineral points, and its depth agrees with the measured thickness at r 0.10.
- **Field survey, 2015** (`_data/Peat depth and DTM/Tebingtinggi.csv`): 1,385 points; 1,132 on peat. The visit date is not recorded; the last rain before each visit falls between 24 October and 1 December 2015, so readings are scored over 24 October to 10 December.
  - 329 of 1,132 peat points have a water table of 0. The zeros cluster by field team (up to 91% of one team's points) and in mangrove (91%), and the ponding column is 0 everywhere, so a zero cannot be read as a saturated surface. Zeros are treated as missing.
  - Of the 803 peat points with a depth, 63 are deeper than 2 m and 41 deeper than the recorded peat base; these are flagged and the gate uses the unflagged points (`00_inputs/field_wtd.csv`).
- **Forcing, 2014-10 to 2015-12**: CHIRPS and MOD16, KHG mean (`03_neraca/inputs/model/`). Monthly values are in each run's report (section 6.2).
- **SiTMAT stations, 2026** (`00_inputs/sitmat/`; table in the input check, unflagged days): 5 concession stations with 200 to 201 days, median water level −17 to −24 cm (a sixth with 31 days, −39 cm); 3 community stations with 76 days, median −149 to −153 cm, range −198 to +2 cm. The concession stations are held shallow, the community ones are about 1.5 m deep.

## 6. Results

### 6.1 Sweep at 200 m

`docs/reports/model_sweep_14.10.03_200m.md`. Runs from 2014-10-01 (saturated) to 2015-12-10; nothing fitted. 528 unflagged peat points not on a fixed cell.

| peat table | canal level (m) | Spearman | Spearman within teams | bias (cm) | RMSE (cm) | gate | KHG mean depth in window (cm) | canal inflow in window (mm) |
|---|---|---|---|---|---|---|---|---|
| tropical-small | 0.6 | 0.04 | 0.02 | −71 | 81 | fail | 1–27 | −3.2 |
| tropical-small | 1.2 | 0.05 | 0.01 | −69 | 80 | fail | 2–29 | −4.6 |
| tropical-large | 0.6 | 0.01 | −0.03 | −55 | 70 | fail | 12–48 | −7.6 |
| tropical-large | 1.2 | 0.01 | −0.03 | −48 | 67 | fail | 17–56 | −9.6 |
| urzainki2020 | 0.6 | 0.02 | 0.08 | −61 | 73 | fail | 0–69 | 0.0 |
| urzainki2020 | 1.2 | 0.03 | 0.08 | −61 | 73 | fail | 0–69 | −0.1 |

Simple predictions on the same points: the constant median has RMSE 40 cm. Distance to canal has Spearman −0.00 and RMSE 39 cm. The gate's check "Spearman above the distance prediction" passes in every run only because that prediction scores zero. Single-day scores across the window vary little (for example tropical-large at 1.2 m: Spearman 0.03 to 0.05, bias −92 to −53 cm). At 200 m, 189 scored points fall on canal or edge cells and are left out; fixed cells are 3.4% (edge) and 17.8% (canals) of the KHG.

### 6.2 Behaviour through 2015

`03_neraca/deltadtm/runs/model/tropical-large_p1.2_s1.2_t1.2_e0.3_200m/model_report.md`, KHG mean over the free cells:

| month | P (mm) | ET (mm) | P − ET (mm) | depth at month end (cm) | share deeper than 40 cm | canal inflow (mm) |
|---|---|---|---|---|---|---|
| 2015-01 | 103 | 126 | −23 | 22 | 0.13 | −36.0 |
| 2015-02 | 51 | 125 | −73 | 39 | 0.35 | −10.0 |
| 2015-06 | 93 | 115 | −22 | 32 | 0.30 | −10.2 |
| 2015-07 | 74 | 113 | −39 | 42 | 0.42 | −6.2 |
| 2015-08 | 173 | 125 | 48 | 35 | 0.35 | −6.9 |
| 2015-09 | 84 | 110 | −26 | 42 | 0.43 | −4.8 |
| 2015-10 | 62 | 122 | −60 | 56 | 0.61 | −2.7 |
| 2015-11 | 291 | 113 | 178 | 24 | 0.24 | −4.6 |

The canals drain the peat (negative inflow) but little: 2.7 to 10 mm a month through the dry season. Over the field window the observed median is about 70 cm; the model's KHG mean falls to 56 cm at the end of October and recovers to 17 cm by 10 December as the November rain returns (window range in the run report).

### 6.3 Run at 100 m

`03_neraca/deltadtm/runs/model/tropical-large_p1.2_s1.2_t1.2_e0.3_100m/model_report.md`. Same configuration as the best-scoring 200 m run (tropical-large, canals 1.2 m), on a 100 m grid (run time 20.1 min).

| grid | points scored | Spearman | bias (cm) | RMSE (cm) | fixed cells: edge, canals | KHG-mean depth, end of October 2015 | KHG mean in window (cm) |
|---|---|---|---|---|---|---|---|
| 200 m | 528 | 0.01 | −48 | 67 | 3.4%, 17.8% | 56 cm | 17–56 |
| 100 m | 584 | −0.01 | −41 | 65 | 1.7%, 9.8% | 64 cm | 23–64 |

The gate fails at 100 m as well. The finer grid fixes half as many cells, scores more points and gives a slightly deeper water table, but the spatial score does not change: single-day Spearman across the window is −0.00 to 0.01. The check "Spearman above the distance prediction" passes only because −0.01 is above the distance prediction's −0.02. At this grid the share of the observed variance between field teams is 28% (584 points).

### 6.4 Sugihan-Lumpur against 51 SiTMAT stations, 2026

`_khg/16.02.01_sugihan_lumpur/03_neraca/lidar/runs/model/tropical-large_p1.2_s1.2_t1.2_e0.3_200m/model_report.md`. LiDAR DTM (25 m clip), 200 m grid, tropical-large, canals 1.2 m below the surface; 2025-11-01 (saturated) to 2026-09-30; CHIRPS and MOD16A2 without gap filling (`mod16nrt`, added for this run because the gap-filled product ends in 2025-12). Canal cells are 39.9% of the KHG at this grid. Run time 6.2 min. The station gate (`fieldcheck.score_stations`) was set before the run: the field gate on each station's mean level, and a median per-station correlation of the daily series of at least 0.5.

| month (2026) | P (mm) | ET (mm) | P − ET (mm) | KHG-mean depth at month end (cm) | canal inflow (mm) |
|---|---|---|---|---|---|
| May | 255 | 130 | 124 | 18 | −71.9 |
| June | 111 | 128 | −16 | 30 | −43.0 |
| July | 43 | 151 | −108 | 56 | −14.2 |
| August | 29 | 154 | −126 | 86 | −2.4 |
| September | 25 | 151 | −126 | 122 | 1.2 |

Stations (33 unflagged; 18 on canal or edge cells are flagged):

| | Spearman across stations | bias (cm) | RMSE (cm) |
|---|---|---|---|
| model | −0.21 | +34 | 37 |
| distance to canal | 0.15 | 0 | 4 |
| constant | — | 1 | 4 |

- **Timing:** median per-station correlation 0.87; the mean curve of the unflagged stations correlates at 0.94 (observed mean 42 cm, simulated 77 cm).
- **Amplitude:** drawdown over the record, median 12 cm observed against 126 cm simulated; Spearman of the drawdown across stations 0.22.

Dynamics here are scored on the 33 stations off canal and edge cells. A first version of the scoring also counted the 18 stations on such cells, which only show the fixed canal level; the figures were corrected on 2026-10-28 after a rerun (`fieldcheck.score_stations`).
- **Supply:** from 2026-06-01 to 2026-10-09 the station-based deficit (`repeat-neraca-run`) is 290 mm; the model's canals took 58 mm out of the peat.
- **Spatial signal:** the station levels hardly differ (the constant prediction is within 4 cm RMSE; the three concessions account for 2% of the variance).
- **Gate:** fail (the spatial checks fail; the dynamics check passes).

**Canals held at 0.4 m** (`.../model/tropical-large_p0.4_s0.4_t0.4_e0.3_200m/model_report.md`; the PP 57/2016 compliance level as a management assumption, not fitted; run time 5.8 min):

| | canals 1.2 m below the surface | canals 0.4 m below the surface |
|---|---|---|
| mean depth of the 33 stations, model (observed 42 cm) | 77 cm (bias +34) | 37 cm (bias −6) |
| RMSE of station levels (33 unflagged) | 37 cm | 11 cm |
| Spearman across stations | −0.21 | −0.24 |
| mean-curve r; median station r | 0.94; 0.87 | 0.95; 0.90 |
| median drawdown over the record (observed 12 cm) | 126 cm | 72 cm |
| canal water into the peat, 2026-06-01 to 2026-10-09 (stations imply 290 mm supplied) | −58 mm | +1 mm |
| KHG-mean depth at the end of September | 122 cm | 84 cm |

A canal level held near the surface brings the mean level to the stations, but only cuts the dry-season drawdown from 126 to 72 cm. The canals start to supply water only once the peat beside them falls below their level: 14 mm in August and 25 mm in September. That is far short of what the stations imply. The gate still fails: levels within 4 cm of each other leave the spatial checks nothing to find.

### 6.5 The field data themselves

`docs/reports/model_sweep_14.10.03_200m.md`, section "The field data":

- Spearman of the observed depth with distance to the nearest canal 0.00, and with the recorded peat thickness 0.02.
- Share of the observed variance between field teams: 31% over all 528 points, and 76% between teams that worked the same 2 km block (258 points).
- With each team's mean removed, the Spearman of the observed depth with distance to the nearest canal is 0.14 (every unflagged point, canal cells included). It is weak, and positive: points farther from canals read slightly deeper, the opposite of canal drainage.
- The team effect does not follow the visit dates: across 25 teams with at least 5 dated points, the Spearman of a team's median depth with its median last-rain date is 0.13.

### 6.6 Three KHG with stations, two peat sets, three canal settings

`docs/reports/model_station_runs.md` (written by `scripts/summarise_model_runs.py` from the run folders). All runs use the LiDAR DTM, CHIRPS and MOD16A2 without gap filling, 2025-11-01 (saturated) to 2026-09-30. Levels and dynamics are scored on stations off canal and edge cells. The sites were chosen by `scripts/rank_station_sites.py` (`docs/reports/station_sites.md`). Kampar-Gaung has the most stations and the widest spread of station levels (11 cm, against 3 cm at Sugihan-Lumpur). Mendahara-Batanghari is the only KHG with at least 5 concession and 3 community stations. The `drained-ismail-large` set takes Sy from Ismail et al. 2021 (`Sy = 0.3 exp(0.73 z)`, our fit) and T from Urzainki 2023.

| KHG | peat set | canal level (m) | stations | Spearman model / distance | bias (cm) | RMSE / constant (cm) | median station r | drawdown obs / sim (cm) |
|---|---|---|---|---|---|---|---|---|
| Sugihan-Lumpur | tropical-large | 1.2 | 33 | −0.21 / 0.15 | +34 | 37 / 4 | 0.87 | 12 / 126 |
| Sugihan-Lumpur | tropical-large | 0.4 | 33 | −0.24 / 0.15 | −6 | 11 / 4 | 0.90 | 12 / 72 |
| Sugihan-Lumpur | drained-ismail-large | 1.2 | 33 | −0.25 / 0.15 | +144 | 145 / 4 | 0.77 | 12 / 642 |
| Sugihan-Lumpur | drained-ismail-large | 0.4 | 33 | −0.33 / 0.15 | +12 | 15 / 4 | 0.90 | 12 / 108 |
| Kampar-Gaung | tropical-large | 1.2 | 55 | 0.05 / 0.34 | +3 | 19 / 12 | 0.65 | 1 / 31 |
| Kampar-Gaung | tropical-large | 0.4 | 55 | 0.03 / 0.34 | −23 | 27 / 12 | 0.65 | 1 / 19 |
| Kampar-Gaung | drained-ismail-large | 1.2 | 55 | 0.10 / 0.34 | +17 | 28 / 12 | 0.67 | 1 / 82 |
| Kampar-Gaung | drained-ismail-large | 0.4 | 55 | 0.21 / 0.34 | −17 | 21 / 12 | 0.63 | 1 / 33 |
| Mendahara-Batanghari (100 m) | tropical-large | 1.2 | 15 | −0.32 / 0.17 | +45 | 60 / 11 | 0.38 | 21 / 64 |
| Mendahara-Batanghari (100 m) | tropical-large | 1.2, plantations 0.4 | 15 | −0.09 / 0.17 | +23 | 48 / 11 | 0.38 | 21 / 40 |

Every run fails the gate. Mendahara-Batanghari by kind of station (medians, stations off canal cells; `.../tropical-large_p1.2_s1.2_t1.2_mp0.4_s0.4_t0.4_e0.3_100m/model_report.md`):

| stations | level observed / simulated (cm) | dry-season drawdown observed / simulated (cm) |
|---|---|---|
| concession (9; 8 in plantation licences) | 37 / 28 | 6 / 52 |
| community (6) | 29 / 95 | 63 / 38 |

Holding plantation canals at 0.4 m (PBPH and oil palm licences, 22% of the KHG, 31% of its canal cells) brings the concession level close to the stations. Concession water tables barely move through the dry season (6 cm), while community land drops 63 cm; the model drains concession land by 52 cm.

**ET falling with depth** (`--et-stress`, PEATCLSM-Trop thresholds) changed nothing at Sugihan-Lumpur with canals at 0.4 m. The model's water table reaches the natural-peat threshold (−0.70 m) only at the end of September, where 95% of ET is still realised (`.../tropical-large_p0.4_s0.4_t0.4_e0.3_200m_etnatural/model_report.md`).

### 6.7 Managed land held at a target (D13, D14)

`docs/reports/model_station_runs.md`, runs whose name contains `_mt`. Canals outside licences at 1.2 m; plantation licences (PBPH, oil palm) held at 0.4 m or at leave-one-concession-out station targets; peat base on; peat-depth gaps filled from BBSDLP. Gate D14, set before the runs: stations in managed land are left out; levels need at least 8 stations outside managed land, dynamics and supply are checked with fewer.

| KHG | managed share of KHG | peat set | target | water supplied to managed land, June to early October | station-based deficit | stations outside managed land | gate |
|---|---|---|---|---|---|---|---|
| Sugihan-Lumpur | 77% | tropical-large | 0.4 m | 244 mm | 290 mm | 0 | pass (supply only) |
| Sugihan-Lumpur | 77% | tropical-large | stations-loo (0.43–0.44 m) | 233 mm | 290 mm | 0 | pass (supply only) |
| Sugihan-Lumpur | 77% | drained-ismail-large | 0.4 m | 324 mm | 290 mm | 0 | pass (supply only) |
| Kampar-Gaung | 44% | tropical-large | 0.4 m | 42 mm | 7 mm | 0 | pass (supply only, within 50 mm) |
| Kampar-Gaung | 44% | tropical-large | stations-loo | 41 mm | 7 mm | 0 | pass (supply only, within 50 mm) |
| Kampar-Gaung | 44% | drained-ismail-large | 0.4 m | 104 mm | 7 mm | 0 | fail (supply) |
| Mendahara-Batanghari (100 m) | 22% | tropical-large | 0.4 m | 194 mm | 119 mm | 7 | fail (dynamics) |
| Mendahara-Batanghari (100 m) | 22% | tropical-large | stations-loo | 209 mm | 119 mm | 7 | fail (dynamics) |
| Mendahara-Batanghari (100 m) | 22% | drained-ismail-large | 0.4 m | 250 mm | 119 mm | 7 | fail |
| Mendahara-Batanghari (100 m), canals outside licences at 0.6 m | 22% | tropical-large | 0.4 m | 181 mm | 119 mm | 7 | fail (dynamics) |

With canals outside licences at 0.6 m instead of 1.2 m, the community stations come out at 66 cm (observed 29 cm) and drop 23 cm (observed 63 cm); the mean level of the 7 stations outside licences matches (37 cm simulated, 36 cm observed). A shallower canal level corrects the level of unmanaged land but not its swing. The lower Sy of Ismail et al. 2021 does not supply the swing either: with canals at 0.6 m it gives 93 cm and a 27 cm drop at the community stations, and a managed supply of 239 mm, which fails the supply check (`drained-ismail-large_p0.6_s0.6_t0.6_mt0.4_e0.3_100m_pb_dbbsdlp`). How community water tables move is not reproduced yet. The 6 stations start in late July 2026 and cover only the falling limb, which limits what they can test.

The one independent test of levels outside managed land is Mendahara-Batanghari's 6 community stations, off canal cells. Observed level 29 cm and drawdown 63 cm; model 95 cm and 38 cm with tropical-large, 165 cm and 99 cm with the Ismail Sy. The median per-station correlation there is 0.38. The leave-one-concession-out targets at Sugihan-Lumpur (0.43–0.44 m) are close to the regulatory 0.4 m.

### 6.8 Season outputs per sub-KHG, and a dry and a wet year

Each run now writes, for a season (default June to September of the run's last year):
- `model_season_days_deeper_40cm.tif`: days each cell of open land (free cells not held by water management) was deeper than 40 cm;
- `model_season_mean_depth.tif` and `model_season_managed_supply.tif` (mm supplied to each managed cell);
- `model_units.csv`: per sub-KHG (or the KHG as one row when it has no sub-KHG units) the open and managed area, the open land's mean depth and days deeper than 40 cm, the share of open land deeper than 40 cm for more than half the season, and the water supplied to the managed land.

Range over the sub-KHG units, 2026, managed land held at 0.4 m, tropical-large (each run's `model_units.csv`):

| KHG | units | open land: mean depth (cm) | open land: days deeper than 40 cm (of 122) | managed supply (mm) |
|---|---|---|---|---|
| Sugihan-Lumpur (canals 1.2 m outside licences) | 30 | 35 to 97 | 51 to 120 | 181 to 319 |
| Kampar-Gaung (canals 1.2 m) | 28 | 12 to 45 | 1 to 69 | 13 to 152 |
| Mendahara-Batanghari (canals 0.6 m) | 29 | 23 to 62 | 30 to 105 | 101 to 316 |

**Dry and wet year** (Sugihan-Lumpur, same set-up, gap-filled MOD16; runs `year2019_dry` and `year2022_wet`; the years chosen from the climatic-balance calendar, 6 and 0 deficit months). June to September:

| year | P − ET | water supplied to managed land | open land at the end of September |
|---|---|---|---|
| 2019 (El Niño) | −285 mm | 163 mm (480 million m³) | mean depth 79 cm, all deeper than 40 cm |
| 2022 | +602 mm | 1 mm | mean depth 9 cm, 7% deeper than 40 cm |

The supply follows the dryness of the season and is near zero in a wet year. No stations cover 2019 or 2022, so these runs show behaviour, not skill. Some units stay dry even in the wet year: in unit S02, open land was deeper than 40 cm on 96 of 122 days in 2019 and 48 in 2022.

### 6.9 First intervention scenarios (D17), Mendahara-Batanghari

`docs/reports/scenarios_15.05-07-10.01.md` (written by `scripts/compare_scenarios.py`). Interventions from repeat-pump's LiDAR run of this KHG: 160 block reaches (`sekat_reach`) and the sub-KHG it marks for water supply (29% of the KHG). Baseline: tropical-large, managed land held at 0.4 m, canals outside licences at 0.6 m.

| scenario | change in days deeper than 40 cm, open land | water supplied in the season, all held land | sub-KHG still needing rewetting |
|---|---|---|---|
| baseline | — | 54.6 million m³ | 8 of 29 |
| blocks | −0.3 days on average; no cell 10 days better | 54.6 million m³ | 8 of 29 |
| blocks and pumping | −0.5 days on average | 105.1 million m³ | 7 of 29 |

Averaged over the KHG the blocks barely change the water table (within 150 m of a reach: 13.6 fewer days, `scenarios_15.05-07-10.01.md`). Part of the reason is the baseline, not the blocks. repeat-pump places blocks assuming the unblocked canals sit 1.0 m below the land (`balance_drawdown_m`), and its reaches hold water at a median 0.59 m. With this baseline's canals already at 0.6 m, most reaches raise nothing. A consistent comparison needs the baseline canal level that repeat-pump assumes; the scenarios on the 1.2 m baseline are below.

With canals outside licences at 1.2 m (`docs/reports/scenarios_15.05-07-10.01_canals1.2.md`):

| scenario | open land: days deeper than 40 cm (area-weighted, of 122) | water supplied in the season | sub-KHG still needing rewetting |
|---|---|---|---|
| baseline | 60.9 | 58.5 million m³ | 12 of 29 |
| blocks | 60.2 | 58.3 million m³ | 12 of 29 |
| blocks and pumping | 58.0 (on the land left open) | 108.7 million m³ | 9 of 29 |

The effect of the blocks is local:

| distance from a block reach | mean change in days deeper than 40 cm | cells at least 10 days better |
|---|---|---|
| 0–150 m | −26.2 | 62% |
| 150–350 m | −8.9 | 35% |
| 350–1,000 m | −0.8 | 1% |
| beyond 1 km | 0.0 | 0% |

This reach matches the literature: under 5 cm of lateral effect by about 300 m (Kurnianto et al. 2026) and rewetting about 100–400 m from blocks in Tebing Tinggi field reports (section 2.2). The 160 reaches touch a small share of this densely canalled KHG, so the KHG-wide average moves little. Pumping on the sub-KHG repeat-pump marks for water holds 29% of the KHG at 0.4 m. It takes about 50 million m³ more in June to September and brings the sub-KHG still needing rewetting from 12 to 9. The area-weighted figures come from each run's `model_units.csv`; the order of the scenarios, not the absolute water table, is the result to use, given the open problems of section 7.

### 6.10 What the managed target and the canal levels rest on (checked 2026-10-29)

**Concession stations follow the compliance limit** (`docs/reports/concession_levels.md`, `scripts/check_concession_levels.py`). The 131,987 unflagged daily readings of 1,157 SiTMAT concession stations (April to October 2026) pile up just inside 40 cm: 2.5 times as many readings at −40 cm as at −41 cm, while the 3,057 community readings show no such step. 53% of concession stations have a median between −40 and −30 cm, 18% deeper than −40 cm. Published plantation water tables are deeper: Acacia 70 ± 17 cm (Evans et al. 2019), 0.70–0.73 m (Hooijer et al. 2012), oil palm canal water about −0.6 m and Acacia about −0.85 m at 5–9 m elevation in 2018–2025 (Vernimmen and Hooijer 2026); RSPO's design target for oil palm is 50–70 cm in collection drains (`research_notes/canal_levels_evidence.md`). Whether operators hold water at the limit or report it there, the concession stations are not independent evidence of the managed water table. A target taken from them (`stations-loo`, 0.43–0.44 m at Sugihan-Lumpur) is the 0.4 m compliance level again.

This also limits the supply check of D14. The station-based deficit is the rain deficit minus Sy times the stations' drawdown (`deficit.py`); where the stations stay flat, it is close to the rain deficit, which is also what holding a target takes. The agreement at Sugihan-Lumpur (233–324 mm against 290 mm) therefore shows that the model is consistent with the stations, not that the stations measure the managed water table.

**Canal levels in LiDAR** (`docs/reports/lidar_canal_levels_14.10.01.md`, `scripts/check_lidar_canal_levels.py`). Transects across the mapped canals of Pulau Padang on the 2 m LiDAR DTM (flown November 2016) find the lowest point within 10 m of the line in 35–46% of cases, against 7% by chance. At the line the DTM lies a median 0.80 m below the land at primary canals, 0.32 m at secondary and 0.24 m at tertiary (control 100 m away: 0.05–0.06 m). Over water the DTM interpolates from the banks, and tertiary drains (about 1 m wide, Ismail et al. 2021) are below the pixel size, so the secondary and tertiary values are shallow bounds; Vernimmen et al. 2020 measure canal water depth only for canals wider than 3 m. The 20–25 m LiDAR of the other KHG cannot resolve canals. The 1.2 m of every class in the model is the unvalidated offset w of Urzainki et al. 2020, closest to unmanaged dry-season canals (below −1.5 m in the ex-Mega Rice Project, Vernimmen and Hooijer 2026); 0.6 m lies in the published managed range.

**Canal stage, not canal exchange.** Mapped canals are 290–450 m apart in the plantation licences of Sugihan-Lumpur, Mendahara-Batanghari and Kampar-Gaung and 420–915 m outside them (canal length over licence area), so a 100 m grid resolves them. Field drains, 75–200 m apart in plantations (Evans et al. 2019; Hooijer et al. 2024), are not mapped. Hooijer et al. 2024 find the peat water table 0.05 m below the canal water in a plantation landscape and explain it by such drains. Where drains are that dense, the water table follows the canal stage, and the stage is the input that matters.

### 6.11 A band of managed targets, and canal levels from LiDAR (runs of 2026-10-29)

`docs/reports/managed_target_band.md` (`scripts/summarise_target_band.py`). Set-up as section 6.7 (tropical-large, peat base, BBSDLP depth fallback, LiDAR DTM, 2025-11-01 to 2026-10-01), with canals outside licences at the Pulau Padang LiDAR levels (primary 0.8 m, secondary and tertiary 0.3 m, section 6.10) and managed land held at 0.4, 0.6 or 0.8 m. Season June to September 2026, area-weighted over the sub-KHG.

| KHG | canals outside licences p/s/t (m) | target (m) | open land: mean depth (cm) | open land: days deeper than 40 cm (of 122) | supply to managed land (mm) | station-based deficit (mm) |
|---|---|---|---|---|---|---|
| Sugihan-Lumpur | 1.2/1.2/1.2 | 0.4 | 49 | 68 | 244 | 290 |
| Sugihan-Lumpur | 0.8/0.3/0.3 | 0.4 / 0.6 / 0.8 | 37 / 38 / 38 | 56 / 56 / 56 | 243 / 149 / 103 | 290 |
| Kampar-Gaung | 1.2/1.2/1.2 | 0.4 | 23 | 24 | 42 | 7 |
| Kampar-Gaung | 0.8/0.3/0.3 | 0.4 / 0.6 / 0.8 | 15 / 15 / 15 | 5 / 5 / 5 | 40 / 16 / 8 | 7 |
| Mendahara-Batanghari | 1.2/1.2/1.2 | 0.4 | 45 | 61 | 194 | 119 |
| Mendahara-Batanghari | 0.6/0.6/0.6 | 0.4 | 34 | 51 | 181 | 119 |
| Mendahara-Batanghari | 0.8/0.3/0.3 | 0.4 / 0.6 / 0.8 | 30 / 30 / 30 | 41 / 41 / 41 | 172 / 124 / 92 | 119 |

Community stations at Mendahara-Batanghari (6, off canal cells), level and dry-season drawdown, observed 29 and 63 cm:

| canals outside licences p/s/t (m) | level simulated (cm) | drawdown simulated (cm) |
|---|---|---|
| 1.2/1.2/1.2 | 95 | 38 |
| 0.6/0.6/0.6 | 66 | 23 |
| 0.8/0.3/0.3 | 44–45 | 12–13 |

- **The managed target sets the supply, not the open land.** From 0.4 to 0.8 m the open land changes by at most 1 cm and 0 days at all three KHG; the supply falls by a factor of 2 to 5. Results on open land, and so the block effects judged there, do not rest on the 0.4 m assumption; supply and pumping volumes do and are reported as a band. Against the station-based deficit the supply check passes at every target at Kampar-Gaung and Mendahara-Batanghari and fails at 0.8 m at Sugihan-Lumpur (103 against 290 mm); section 6.10 explains why this check carries little weight.
- **The canal level outside licences sets the open land.** The LiDAR levels cut the days deeper than 40 cm from 68 to 56 (Sugihan-Lumpur), 24 to 5 (Kampar-Gaung) and 61 to 41 (Mendahara-Batanghari).
- **A fixed canal level cannot give both the level and the swing of community land.** Shallower canals bring the community level closer (95 to 44 cm, observed 29) and flatten the dry-season drawdown (38 to 12 cm, observed 63). The stations need canals that are high in the wet season and fall in the dry season, which a fixed level per class cannot represent. This is the case for a canal stage that varies in time (section 8, item 4), from data or from a canal water balance. *Revised in section 6.13:* the observed 29 cm and 63 cm rest on outliers in the station record; on the screened record and the 100 m grid, the LiDAR canal levels match the community stations' level and fall (sections 6.12, 6.13).
- **Canal cells take a large share of the grid.** Canals are rasterised as whole fixed cells (`all_touched`): 40% of Sugihan-Lumpur at 200 m, and 12 of 13 concession stations at Mendahara-Batanghari fall on a canal cell and are left out. A canal narrower than a cell holds the whole cell at its level. D18 (section 6.12) frees the canal cells outside managed land; canals in managed land stay fixed at the target, so the 12 concession stations are still left out.
- **Block scenarios** need a baseline deeper than the reach levels of repeat-pump (median 0.59 m at Mendahara-Batanghari, section 6.9); on canals at 0.3 m most reaches would raise nothing. The 1.0 m baseline of D17 stays for them.

### 6.12 Canals inside cells and a canal water balance (D18, D19; runs of 2026-10-29)

`docs/reports/canal_modes.md` (`scripts/summarise_target_band.py`) and `docs/reports/subcell_canal_check.md` (`scripts/check_subcell_canal.py`). Set-up as section 6.11 with the target at 0.4 m and canals outside licences at the LiDAR levels (primary 0.8 m, secondary and tertiary 0.3 m), which the store runs use as the outlet sill. Season June to September 2026.

**Numerical check of the leak term.** Parallel canals in flat peat, 90 days at 4 mm/day from saturation, against a 5 m grid that resolves a 10 m canal:

| canal spacing (m) | grid (m) | bias of the land mean, fixed cells (cm) | bias, leak factor 12 (cm) | cell RMSE, fixed / leak (cm) |
|---|---|---|---|---|
| 300 | 100 | +4.7 | −0.2 | 6.4 / 1.3 |
| 300 | 200 | +18.5 | −0.6 | 20.1 / 3.8 |
| 500 | 100 | +1.6 | +0.7 | 3.8 / 1.5 |
| 500 | 200 | +8.1 | −0.4 | 11.1 / 6.5 |

Factors 4, 8 and 24 were also run; 12 had the lowest RMSE in three of the four cases and the smallest bias in all four (at 500 m and 200 m, 24 had an RMSE of 5.1 cm with a +2.9 cm bias).

**Open land, compared on the same cells** (the open cells of the fixed-cell run; leak and store runs also count canal cells as open land, which adds 26 to 83% to its area):

| KHG, grid | days deeper than 40 cm: fixed / leak / store τ 1 d / store τ 0.1 d | canals at 1.2 m, fixed | canal cells fixed: fixed / leak runs | canal depth below the land, season median, τ 1 / 0.1 d (m) |
|---|---|---|---|---|
| Sugihan-Lumpur, 200 m | 56 / 54 / 51 / 55 | 68 | 40% / 30% | 0.42 / 0.55 |
| Kampar-Gaung, 200 m | 5 / 5 / 3 / 5 | 24 | 37% / 25% | 0.17 / 0.30 |
| Mendahara-Batanghari, 100 m | 41 / 41 / 38 / 43 | 61 | 23% / 7% | 0.41 / 0.48 |

**Community stations at Mendahara-Batanghari** (the 6 stations off canal cells in the fixed-cell run, in every run; screened record: section 6.13):

| canals outside licences | level, raw record: obs / sim (cm) | drawdown, raw: obs / sim (cm) | level, screened: obs / sim (cm) | drawdown, screened: obs / sim (cm) |
|---|---|---|---|---|
| 1.2 m, fixed | 29 / 95 | 63 / 38 | 44 / 101 | 11 / 25 |
| 0.6 m, fixed | 29 / 66 | 63 / 23 | 44 / 70 | 11 / 13 |
| LiDAR levels, fixed | 29 / 44 | 63 / 12 | 44 / 47 | 11 / 6 |
| LiDAR levels, leak (D18) | 29 / 46 | 63 / 15 | 44 / 48 | 11 / 9 |
| LiDAR levels, store τ 1 d (D19) | 29 / 52 | 63 / 35 | 44 / 56 | 11 / 24 |
| LiDAR levels, store τ 0.1 d | 29 / 58 | 63 / 35 | 44 / 63 | 11 / 24 |

- **Canals inside cells change the open land little.** On the same cells the leak changes days deeper than 40 cm by 0 to 2. Its effect is on what the model represents: canal cells are no longer held at the canal level (fixed canal cells fall from 23% to 7% of Mendahara-Batanghari at 100 m), and the stations on them are scored.
- **The resolution check did not separate the two modes on a real KHG.** At Mendahara-Batanghari, days deeper than 40 cm were 41 and 39 at 100 and 200 m with fixed cells, 41 and 38 with the leak (same cells). The comparison is confounded: managed land held at the target is 302 km² at 100 m and 195 km² at 200 m. The community drawdown of the leak runs moves with the grid (raw record, 9 stations: 8 cm at 100 m, 18 cm at 200 m).
- **The canal store makes the canals fall.** At Mendahara-Batanghari and Sugihan-Lumpur the canals sit a season median 0.41 to 0.55 m below the land, inside the gate range of 0.2–2.5 m; at Kampar-Gaung 0.17 m with τ = 1 day (fails the range) and 0.30 m with τ = 0.1 day (passes). τ = 0.1 day was added after the Kampar-Gaung run at τ = 1 day failed the range; it is reported as a band and no value is chosen. The coupling closes mass to within 0.006% of the canal exchange. The range is wide, so passing it says little.
- **On the raw record the store looked like progress; on the screened record it overshoots.** It triples the raw dry-season fall (12 to 35 cm) and deepens the level (44 to 52–58 cm). The screened record shows the community land falling 11 cm from 19 August to 30 September; at 100 m the store gives 24 cm, the fixed LiDAR levels 6 cm and the leak 9 cm. At 200 m the 4 comparable stations fall 2 cm on the screened record against 21 cm (fixed) and 22 cm (leak). The station correlations were not recomputed on the screened record.
- **Gate results.** The community check (level and drawdown within 20 cm, `fieldcheck.COMMUNITY_TOL_CM`, raw record) fails in every run at 100 m. At 200 m the leak run passes it on the 9 stations its gate scores, but the 3 added stations sit on canal cells and barely fall; on the 4 stations of the fixed-cell run it fails (49/33 against 29/63). With D18 the set of scored stations depends on the canal mode; the gate is unchanged and reports its own set. The median station correlation is 0.32–0.35 in the leak and store runs against 0.38 with fixed cells, below 0.5 in all.
- **Not yet done:** canal cells in managed land stay fixed at the target (25–30% of the cells at Kampar-Gaung and Sugihan-Lumpur); the sill of the store is the Pulau Padang LiDAR level applied to other KHG; τ and the canal widths and beds are a priori values; block scenarios have not been run with D18 or D19.

### 6.13 Outliers in the station record (checked 2026-10-29)

`docs/reports/station_outliers.md` (`scripts/check_station_outliers.py`). SiTMAT's QC flags readings outside −500 to 100 cm and single spikes over 60 cm. It passes a logger that restarts after a gap at a shifted level, a logger stuck at one value, and steps between days. A screening rule was written in `fieldcheck.screen` before its effect on any score was computed; its thresholds were chosen after looking at the Mendahara-Batanghari restart week and the stuck station: records are split at gaps of 7 days or more; pieces shorter than 14 days are left out, as are the first 7 days of each piece (settling) and runs of 7 or more identical values; day-to-day jumps over 30 cm are counted.

| record | kind | stations | readings | left out | stations with a gap of 7+ days | jumps > 30 cm |
|---|---|---|---|---|---|---|
| national, April to October 2026 | concession | 1,159 | 132,109 | 22,656 (17%), of which 11,380 in stuck runs | 465 (40%) | 518 |
| national | community | 73 | 3,167 | 732 (23%) | 38 (52%) | 62 |
| Sugihan-Lumpur | concession | 51 | 10,041 | 2,231 (22%), of which 1,874 in stuck runs | 0 | 6 |
| Kampar-Gaung | concession | 86 | 12,144 | 1,357 (11%) | 68 (79%) | 35 |
| Mendahara-Batanghari | concession | 13 | 1,906 | 307 (16%) | 9 (69%) | 1 |
| Mendahara-Batanghari | community | 9 | 603 | 105 (17%) | 9 (100%) | 21 |

- **The community result of sections 6.6 to 6.11 rests on outliers.** All 9 community stations at Mendahara-Batanghari report 3 days from 21 July 2026, then nothing for about three weeks. They restart in the week of 11 August at levels up to 85 cm above the ground and move 60 to 100 cm within a week. The raw "level 29 cm, fall 63 cm" is the mean and the last-minus-first-week difference over such a record. One station holds exactly 0 for about two weeks. On the screened record the 6 stations off canal cells sit at 44 cm and fall 11 cm over 19 August to 30 September. Whether the land was flooded in early August cannot be told from these records.
- **Stuck runs are common in concession records:** 9% of the national concession readings and 19% at Sugihan-Lumpur sit in runs of 7 or more identical daily values. Together with the pile-up at −40 cm (section 6.10) this weakens what concession stations can test.
- Other users of the SiTMAT record are not screened yet: the station-based KHG deficit (`deficit.py`, through `repeat_common.tma`, which drops only SiTMAT's range and spike flags), and with it the reference of the D14 supply check; national stage 3; the repeat-sitmat dashboard.
- The scores and gates in this report use the raw record. Whether the gate should score screened records is a decision (section 8, item 5); the comparison in section 6.12 shows both.

### 6.14 Recommended set-up (D21, runs of 2026-10-29)

Canals inside cells at the LiDAR levels, managed land at 0.4 m, stations screened. Season June to September 2026, area-weighted over the sub-KHG (`model_units.csv` of `tropical-large_p0.8_s0.3_t0.3_mt0.4_lk_scr_e0.3_<res>m_pb_dbbsdlp`). Map: `re-peat/reports/project_report/figures/model_days_maps_final.png` (`model_days_maps_final` in `re-peat/tools/project_report_figures.py`).

| KHG | grid | open land: days deeper than 40 cm | open land: mean depth (cm) | supply to managed land (mm) | gate |
|---|---|---|---|---|---|
| Sugihan-Lumpur | 200 m | 49 | 40 | 243 | pass (supply only; no station outside managed land) |
| Kampar-Gaung | 200 m | 6 | 18 | 40 | pass (supply only) |
| Mendahara-Batanghari | 100 m | 40 | 32 | 173 | fail: median station r 0.30 (check 0.5) and Spearman below the distance prediction; passes Spearman ≥ 0.3, RMSE below the constant, community level and drawdown (8 stations: 39/44 cm level, 6/3 cm drawdown) and supply |

The gate is now testable on screened records and fails only on dynamics and on beating distance to canal at Mendahara-Batanghari. The maps are indicative: the model is in development.

### 6.15 ET falling with depth and the drained-peat set against the D21 set-up (runs of 2026-10-30)

Mendahara-Batanghari, LiDAR, 100 m, 2025-11-01 to 2026-10-01, D21 set-up, stations screened. One change per run; run folders `imp_a_baseline_screened`, `imp_b_etstress`, `imp_c_ismail` under `03_neraca/lidar/runs/model/`. Gates unchanged.

| run | change | Spearman (9 stations outside held land) | bias (cm) | RMSE (cm) | median station r | community level obs / sim (cm) | supply (mm) | gate |
|---|---|---|---|---|---|---|---|---|
| imp_a | none (reproduces section 6.14: 173 mm, r 0.30) | 0.45 | 5 | 16 | 0.30 | 39 / 44 | 173 | fail |
| imp_b | `--et-stress drained` | 0.45 | 5 | 16 | 0.30 | 39 / 44 | 173 | fail |
| imp_c | `drained-ismail-large` (Sy of drained peat) | 0.70 | 30 | 51 | 0.29 | 39 / 52 | 231 | fail |

- ET stress gives the same station scores as the baseline. The water table stays shallow at these stations (mean level 28 to 44 cm), above the depth where ET is cut, as at Sugihan-Lumpur (section 6.6).
- The Ismail set ranks the stations better (Spearman 0.70, above the distance prediction) and puts the levels 30 cm too deep on average (RMSE 51 cm against 19 cm for the constant), and its community drawdown is 0 cm against 6 cm observed. It also raises the supply to managed land to 231 mm against the station deficit of 119 mm (within the factor 2).
- **Known limitation, managed land.** Concession levels are imposed in the model (held at 0.4 m) because the station readings follow the PP 57/2016 limit. On the screened records (`scripts/check_concession_levels.py --screen`, `docs/reports/concession_levels_screened.md`; 109,343 readings from 1,054 concession stations, 2026-04-08 to 2026-10-22) the readings peak at -39 to -40 cm and fall by half at -41 cm: 2.0 times as many at -40 as at -41 cm at concession stations, against 1.4 at the 47 community stations (2.5 and 1.5 on the unscreened record). 56% of concession station medians lie between -40 and -30 cm. The community ratio is above 1, so the contrast is a difference in degree. Readings at the limit do not show whether operators hold the water there or report it there. The model therefore takes managed land as a scenario band (0.4, 0.6, 0.8 m) and does not predict its level.
- **Water removed as ponding (surface runoff), diagnostic.** The solver drops head above the land each step (`remove_ponding`). `--log-ponding` writes `model_ponded.csv` (mm over the free cells, share of cells that ponded; estimated as head above the land times Sy at the surface). Run `imp_d_ponding`, the baseline with the flag; its other outputs are byte-identical to `imp_a_baseline_screened`. Over the year the model removes 498 mm against 2,222 mm of rain (22%). By month (mm): November 103, December 160, January 68, February 0.3, March 4, April 36, May 93, June 34, July to September about 0. In the wet months it is 30 to 40% of the rain, with up to 60% of the cells ponded on a day. In the dry season it is nil, so surface runoff does not set the dry-season level here. It would matter for how full the canals are at the start of the dry season, and only in a model with a canal store; the store (D19) already overshoots and its outlet constant is unmeasured, so routing the runoff to canals was not added.
- **Stations on canal cells as canal levels: not possible with these records.** Read from `station_scores.csv` of the D21 runs. The stations flagged `on_fixed_cell` (31 at Kampar-Gaung, 18 at Sugihan-Lumpur, 4 at Mendahara-Batanghari) sit in managed land and are held at 0.4 m in the model; their median distance to a canal is 96 to 123 m, so they are not in canal water. Only 11 stations lie within 30 m of a canal (Mendahara-Batanghari 4, Kampar-Gaung 5, Sugihan-Lumpur 2), and 10 of them are concession stations. Eight of the ten concession stations read 38 to 45 cm, the compliance pile-up above, so a canal level cannot be separated from it; the other two read 30 and 63 cm (Kampar-Gaung), and the one community station reads 13 cm. The class levels (0.8 / 0.3 / 0.3 m) stay as measured at Pulau Padang only.
- **Canal level band** (Mendahara-Batanghari, LiDAR, 100 m, D21 set-up; runs `band_canal_shallow`, `imp_a_baseline_screened`, `band_canal_deep`; `scripts/summarise_canal_band.py`, `docs/reports/canal_band_15.05-07-10.01.md`). The three classes of the national existing-canal layer (primary, secondary, tertiary) are shifted together.

  | canal level below the land, primary / secondary and tertiary (m) | open land mean depth (cm) | days deeper than 40 cm | supply to managed land (mm) | Spearman (9 stations) | bias (cm) | RMSE (cm), constant 18.6 |
  |---|---|---|---|---|---|---|
  | 0.5 / 0.15 | 24 | 29 | 167 | 0.77 | -6 | 16.3 |
  | 0.8 / 0.3 | 32 | 40 | 173 | 0.45 | 5 | 16.0 |
  | 1.2 / 0.6 | 43 | 64 | 181 | 0.02 | 28 | 37.3 |

  The unmeasured canal level moves the open land by about 10 cm per step; the range per sub-KHG is 19 cm at the median and 44 cm at most. The supply to managed land barely changes (167 to 181 mm), since managed land is held. The stations rank best at the shallow setting and worst at the deep one, which fails the RMSE check against a constant. Only 9 stations lie outside held land (8 community, 1 concession), and the levels were not fitted to them, so this places the canal levels between the shallow and middle settings as the plausible range and does not fix a value. The canal level is the largest single unknown for open land. On the gate, the shallow setting passes five of six checks (only the median station r, 0.33 against 0.5, fails; the middle setting also fails the Spearman against the distance prediction), and the deep setting fails five.
- **One class at a time** (same site and set-up, others at 0.8 / 0.3 / 0.3 m; `docs/reports/canal_class_band_15.05-07-10.01.md`; runs `cls_*`).

  | class shifted | level (m) | open land mean depth (cm) | days deeper than 40 cm | Spearman (9 stations) | RMSE (cm), constant 18.6 |
  |---|---|---|---|---|---|
  | primary | 0.5 / 1.2 | 29 / 34 | 38 / 41 | 0.40 / 0.45 | 16.7 / 15.7 |
  | secondary | 0.15 / 0.6 | 30 / 35 | 36 / 48 | 0.40 / 0.23 | 16.7 / 21.4 |
  | tertiary | 0.15 / 0.6 | 29 / 37 | 34 / 55 | 0.60 / -0.22 | 13.9 / 32.2 |

  The tertiary canals move the open land most (8 cm between 0.15 and 0.6 m, and 21 more days deeper than 40 cm), then secondary (5 cm) and primary (5 cm between 0.5 and 1.2 m). Tertiary canals are the longest class in the clip (2,922 km, against 1,954 km secondary and 1,688 km primary), so part of this is length. The stations favour a shallow tertiary level (Spearman 0.60, RMSE 13.9 cm, below the distance prediction's 14.5) and reject a deep one. The canal layer is incomplete, partly unconnected and partly mis-classed (`docs/reports/canal_topology_15.05-07-10.01.md`: 734 components, 453 of them a single segment; about a third of the line ends free; gaps most common in the tertiary class), so the class effects show how much the class assignment matters, not which canals set the water table. A canal coded tertiary that is a primary canal is counted in the tertiary row.
- Neither ET stress nor the drained-peat set improves the gate. The D21 set-up stays the recommended one. Dynamics (median station r about 0.3) are unchanged by either change, so the limit is not in Sy or ET.

### 6.16 Supply cap on managed land (D22, run of 2026-10-30)

Success criteria, written before the run (Mendahara-Batanghari, LiDAR, 100 m, D21 set-up plus `--supply-cap deficit`, run `cap_deficit`, against `imp_a_baseline_screened`):
1. The default path is unchanged: a run without the flag gives byte-identical `model_series.csv`, depth rasters, `model_units.csv` and `station_scores.csv` (run `chk_default`).
2. The community stations outside managed land score no worse than `imp_a` (Spearman 0.45, bias 5 cm, RMSE 16 cm, median station r 0.30).
3. Simulated season-mean level at the concession station cells is compared with their observed spread (observed 27 to 45 cm at Mendahara-Batanghari); it is a sanity bound, not a pass or fail gate, because the concession readings follow the compliance limit.
4. The share of managed land deeper than 60 cm in the season mean is reported. A large share would show the model's drainage, not the managed water table.
5. The supply check of the gate is not testable with this cap (taken from the deficit); report the supply and say so. (A first version of the code left the check in; the three capped runs were rerun on 2026-10-30 with it left out, `supply_check.cap_from_deficit` is true in their `station_scores.json`.)

Result (Mendahara-Batanghari, LiDAR, 100 m; `cap_deficit`, cap 119 mm over 2026-06-01 to 2026-10-01, against `imp_a_baseline_screened`):

| | imp_a (hard target) | cap_deficit |
|---|---|---|
| supply to managed land, 2026-06-01 to 2026-10-13 (mm) | 173 | 110 |
| managed land season mean depth, 5th / 25th / 50th / 75th / 95th percentile (cm) | 19 / 27 / 33 / 40 / 40 | 19 / 28 / 36 / 40 / 40 |
| managed land deeper than 60 cm, season mean | 0.0% | 0.2% |
| managed land on 2026-10-01: median depth (cm), share at 40 cm or deeper, share deeper than 60 cm | 40, 94%, 0.0% | 43, 97%, 1.6% |
| 9 stations outside managed land: Spearman, bias (cm), RMSE (cm) | 0.45, 5, 16 | 0.45, 5, 16 |
| 12 concession station cells, simulated level (cm) | 11 to 40 | 11 to 40, same as imp_a to 1 cm |

1. The default path is unchanged: `chk_default` (no flag) is byte-identical to `imp_a` in `model_series.csv`, both depth rasters, `model_units.csv` and `station_scores.csv`. Met.
2. The community stations score the same. Met.
3. The concession station cells do not move (observed 16 to 50 cm). Not changed by the cap.
4. 0.2% of managed land is deeper than 60 cm in the season mean, 1.6% on the last day. The cap lets the level fall a little (median 43 cm on the last day against 40) and no more.
5. The supply check is not testable with this cap; the supply is 110 mm against the deficit of 119 mm by construction.

The cap releases the water table only a few centimetres. The likely reason (not checked cell by cell) is that the model's water table falls slowly once the supply stops, so a limited supply does not produce a deep concession water table within this season. The cap therefore does not remove the uniform level on the last day (97% of the managed cells at 40 cm or deeper). It stays an option (`--supply-cap`), not the recommended set-up (D21), and the decision on it is left to the project owner. The season mean map already shows managed land varying between 19 and 40 cm; the uniform 40 cm is a feature of the last day, when most cells are at the target.

#### Supply from the KHG's own climate (`--supply-cap climate`, run of 2026-10-31)

The cap value and window come from the KHG's rain and ET, so the supply check of the gate stays testable. `repeat_neraca/supply_rule.py`: the dry window is the 14 consecutive dekads (circular, 36 a year) with the largest mean ET minus rain over 2018-2025 (pixel-weighted mean of the sub-KHG balance files, CHIRPS and gap-filled MOD16); the cap is the ET minus rain of the run over that window, floored at 0. All three KHG give the window starting at dekad 16 (1 June). In an average year of the record the shortfall over that window is negative (rain above ET) at all three, so the cap is the amount of the run year: 2026 is a dry year, comparable to 2019. `scripts/supply_rule.py` writes the comparison (`docs/reports/supply_rule.md`). Runs with class canal levels, existing blocks, `--managed-target 0.4`, `--canal-cells leak`, screened stations (Mendahara-Batanghari 100 m, the others 200 m):

| KHG | station deficit (mm) | climate cap (mm) | managed supply, uncapped (mm) | managed supply, capped (mm) | supply check |
|---|---|---|---|---|---|
| Mendahara-Batanghari | 119 | 202 | not run with these options | 159 | pass |
| Kampar-Gaung | 7 | 11 | 40 | 8 | pass |
| Sugihan-Lumpur | 290 | 377 | 243 | 235 | pass |

The climate cap exceeds the station deficit by 1.3 to 1.7 times because the station figure also subtracts the storage the stations see released. It binds only at Kampar-Gaung. Station gates at Kampar-Gaung and Sugihan-Lumpur are not testable (stations flagged). At Mendahara-Batanghari the other gate checks are as in the deficit-cap run. The dry window needs the 2018 onwards balance files; a KHG without them stops with a message.

### 6.17 Existing canal blocks as default (D23, runs of 2026-10-30)

Mendahara-Batanghari, LiDAR, 100 m, D21 set-up; `chk_noblocks` (`--existing-blocks none`), `eb_default` (default), against `imp_a_baseline_screened`.

- **Reproducibility.** `chk_noblocks` is byte-identical to `imp_a` in `model_series.csv`, both depth rasters, `model_units.csv` and `station_scores.csv`.
- **Test with the stations, before the change.** The 422 existing blocks of the KHG (all `Sekat Kanal`, recorded 2018) do not explain the shallow readings beside canals: the four stations outside managed land within 60 m of a canal (13, 15, 21 and 35 cm) are 14 to 27 km from the nearest recorded block; the one station near a block (290 m) reads 44 cm. Over the 9 stations, observed depth has Spearman 0.53 with distance to the nearest canal and -0.15 with distance to the nearest block. The dry-canal and subsided-margin explanations of the canal research report stay open.
- **Effect of the default.** 2,175 canal cells are held at the block level. Season mean depth changes by more than 0.05 cm in 2,966 of 201,226 cells (1.5%); median change among those 0.5 cm (5th to 95th percentile 0.1 to 9.4 cm), and the open-land mean depth per sub-KHG changes by at most 0.5 cm (KHG: 31.8 cm both). The 9 stations score the same (Spearman 0.45; bias 5.4 and 5.5 cm; RMSE 16.0 and 16.2 cm). The blocks mostly lift the primary canals (0.8 m to 0.4 m), since the secondary and tertiary class levels (0.3 m) are already shallower.
- **Reading.** At Mendahara-Batanghari the recorded existing blocks have a small effect and do not close the gap with the stations. Their value is for KHG with many blocks near open land; Kampar-Gaung (2,884) and Sugihan-Lumpur (2,861) have far more and are not yet rerun.

Existing blocks, the supply cap and the class canal levels together (Mendahara-Batanghari, LiDAR, 100 m; runs `eb_cap_deficit` with 0.8 / 0.3 / 0.3 m and `eb_cap_lv32_24` with 0.80 / 0.32 / 0.24 m, both with `--supply-cap deficit`; the supply check is left out of the gate):

| | imp_a (hard 0.4 m, no blocks) | eb_cap_deficit | eb_cap_lv32_24 |
|---|---|---|---|
| open land mean depth, season (cm) | 31.8 | 31.8 | 30.9 |
| open land days deeper than 40 cm | 39.6 | 39.7 | 37.2 |
| 9 stations: Spearman, bias (cm), RMSE (cm; constant 18.6) | 0.45, 5.4, 16.0 | 0.45, 5.5, 16.2 | 0.48, 2.8, 14.4 |
| median station r | 0.30 | 0.30 | 0.31 |
| managed land season mean depth, mean (cm); deeper than 60 cm | 32.4; 0.0% | 33.5; 0.2% | 33.5; 0.2% |

The class levels move the open land about 1 cm shallower and the station fit a little (RMSE 14.4 cm); the gate still fails on the median station r and on beating the distance prediction. The nine stations were not used to choose the levels. Map: `watertable_map.png` in the `eb_cap_lv32_24` run folder (`scripts/plot_watertable_map.py`, with its known limitations printed under it).

## 7. Interpretation

1. **The gate failed, but the test cannot discriminate.** The survey depths follow neither distance to canal nor peat thickness, within teams or between them, and differ mainly by field team. That holds whether the team effect comes from method or from visit dates the survey does not record. No model of the water table can reproduce it. A model that matched the true water table would still score near zero against these readings, so the failure says nothing about the model's spatial skill.
2. **The bias is informative, but ambiguous.** Every configuration is 48 to 71 cm shallower than the readings. From June to October 2015 the monthly P − ET in section 6.2 sums to −99 mm (our arithmetic). At the tropical sets' surface Sy of 0.6, that lowers the water table by about 17 cm; reaching the observed 70 cm would need Sy near 0.14, or a few hundred mm of extra drainage or evaporation. The bias cannot tell a too-high Sy from forcing that is too wet or from missing drainage. The measured surface Sy at tropical sites is about 0.3 (D6), half the calibrated value used.
3. **The canals exchange little water even with tropical-large.** Dry-season drainage of a few mm a month is small against the rain balance. This is the regime of the earlier tier 2 failure, now at a 20-fold finer grid and 100 to 1,000 times the transmissivity. It may come from the canal level rule: a level fixed below the local surface, with no flow along the canal and no supply.
4. **At Sugihan-Lumpur the model has the right timing and the wrong amplitude, because it lacks supply.** The stations hold about 42 cm through a dry season in which P − ET is −376 mm from June to September (monthly table, section 6.4; our arithmetic). The model, with canals fixed 1.2 m below the surface, drains to 122 cm. The station-based deficit (290 mm supplied) and the model's canal flux (58 mm drained) point the same way. The water table in this managed KHG is set by how the canals are operated, which the model does not represent. This repeats the tier-2 finding of October 2026 (section 1.3), now on LiDAR, at 200 m and with tropical peat parameters. Specific yield cannot explain it: at Sy 0.6, −376 mm lowers the water table by about 63 cm, while the stations moved 12 cm. Holding the canals at 0.4 m (section 6.4) corrects the mean level (bias −4 cm) but leaves a 72 cm drawdown, because lateral seepage from a canal at a fixed level supplies little until the peat beside it falls below that level. The stations' flat dry-season levels need either more supply than seepage from held canals gives (water management at the stations, which concession monitoring points may sit close to), or less water loss at depth than MOD16 implies (ET that falls as the water table deepens, section 2.4). The present data cannot separate the two.
5. **The gate is hard to pass where managed levels are uniform.** When station levels differ by a few cm, the constant prediction sets an RMSE bar of 4 cm, and a Spearman across stations measures little. For managed KHG the informative checks are the dynamics: drawdown amplitude, the supply term, and the contrast between managed and unmanaged land. Changing the gate is a decision for the team (section 8); it has not been changed.
6. **Across three KHG, the stations stay almost flat through the dry season and the model drains.**
   - The observed median drawdown is 1 cm at Kampar-Gaung, 12 cm at Sugihan-Lumpur and 6 cm for Mendahara-Batanghari's concession stations. The model gives 19–642 cm, depending on peat set and canal level.
   - Community land at Mendahara-Batanghari does drop (63 cm), so the flatness belongs to managed land.
   - The measured, lower Sy of drained peat (Ismail et al. 2021) makes every drawdown larger. It helps the spatial ranking a little at Kampar-Gaung (Spearman 0.21) but not enough to beat distance to canal (0.34).
   - With Sy near 0.03 at depth and ET at full rate however deep the water table, the water table can fall below the peat itself (642 cm at Sugihan-Lumpur, where peat is about 1.3 m thick). A realistic low Sy needs ET that stops at depth and a peat base.
   - The common missing term is water supplied to managed land: canal water held up by blocks, gates or pumping, more than seepage from a fixed canal level gives.
7. **Holding managed land at a target reproduces the supply where the dry season was dry.**
   - At Sugihan-Lumpur the water that holding the plantations at 0.4 m takes (233–324 mm, June to early October) is close to the 290 mm the stations imply. At Mendahara-Batanghari it is within a factor of 2 (194–209 mm against 119 mm) with the tropical-large set.
   - At Kampar-Gaung the dry season was near-neutral (the stations rose 11 cm) and the deficit is 7 mm. A ratio test on a near-zero deficit fails on small absolute differences (41 mm against 7 mm), so the supply check now also passes within 50 mm (D14, amended after these runs). With it, Kampar-Gaung passes with the tropical-large set and fails with the Ismail set (104 mm). Station records cover 2026 only, so the check cannot yet be repeated for a wet and a dry year at one site.
   - Every station off a canal cell at Sugihan-Lumpur and Kampar-Gaung lies inside a licence. Their levels are now set by the target, so these sites test only the supply.
8. **Unmanaged land is now the weak part.** At Mendahara-Batanghari the model puts community land at about 95 cm against 29 cm observed. It drops less than observed through the dry season (38 against 63 cm), with a station correlation of 0.38. The canal level outside licences (1.2 m) is a guess: farm drains are under 1 m wide (Ismail et al. 2021), and community canals may not draw the peat down that far. The test rests on 6 stations.
9. **What the result does not show.** It does not show that the model has no spatial skill, nor that it has some. It does not test the response to blocks; nothing in the workspace was measured before and after blocking.

### Limitations

- KHG-mean forcing; dekad totals spread evenly over their days.
- DeltaDTM not corrected by repeat-dem; no LiDAR.
- Peat depth from a raster that agrees poorly with the field thickness (r 0.10); no reliable peat mask.
- Canal levels fixed per class; no canal network, blocks, tides or pumps yet.
- The edge ring is held 0.3 m below the local surface, a river rule, while Tebing Tinggi's edge is mostly coast.
- Surveyed depths with a strong team effect and no recorded dates; the 2015 blocks status is an assumption.

## 8. Decisions needed

0. **The canal boundary in managed land.** Sugihan-Lumpur (section 7, point 4) shows that a canal level fixed below the surface drains a peat that management keeps wet. A canal level held near the surface in concessions, for example at the 0.4 m compliance level of PP 57/2016, is a management assumption, not a fitted value, and can be tested against the stations' drawdown and the supply deficit. The alternative is a supply term at canal cells sized from the deficit.
1. **What the gate rests on.** The Tebing Tinggi survey cannot test the spatial pattern (section 7, point 1), and the Sugihan-Lumpur station levels carry little spatial signal (section 7, point 5). Options:
   - the 2026 SiTMAT stations at Tebing Tinggi (5 concession stations held at about 20 cm, 3 community stations at about 150 cm), one season. The contrast between the two groups is itself a test of whether the model separates managed from unmanaged land. A 2026 run needs WaPOR or non-gap-filled MOD16 for ET, since MOD16A2GF ends in December 2025;
   - a site with stations and LiDAR: Sugihan-Lumpur (51 stations) or Pulau Padang (LiDAR 2016, the MIKE SHE study of Kurnianto 2026 on the same island);
   - the KHG supply deficit as a second check: the canal and edge inflow of the model against the station-based deficit where both exist.
2. **Specific yield and ET.** The literature (section 2.4) supports a surface Sy of 0.1–0.3 for drained peat, against 0.6 in the tropical sets, and ET that falls as the water table deepens. A lower Sy makes every drawdown larger: closer to the readings at Tebing Tinggi (section 7, point 2), further from the stations at Sugihan-Lumpur, where the model already drains too far. ET that falls with depth works the other way and slows drawdown. At Sugihan-Lumpur neither replaces the missing supply, so both belong after the canal boundary (item 0). A Sy(z) of about 0.3 at the surface falling to 0.1 at −1.5 m can be added as a third peat set, labelled as literature-based, not calibrated.
3. **The canal boundary for block scenarios:** port Urzainki 2023's canal network and weir equation, or MODFLOW 6 with stage per reach (D5, D7). A lumped canal store per sub-KHG now exists (D19); it has no reaches, so blocks still act through fixed reach levels (D17).
4. **Managed land and canal levels after section 6.10 (proposal, not decided).**
   - The managed target cannot be measured with SiTMAT. Treat it as a scenario input with a band, for example 0.4 m (the rule), 0.6 m (RSPO and published oil palm) and 0.8 m (published Acacia), and report how unmanaged land and the block effects change across the band, not one value.
   - Canal levels outside managed land per class from measurement where a fine LiDAR DTM exists (Pulau Padang: primary 0.8 m, secondary and tertiary at least 0.3 m), and otherwise a stated default inside the published range, replacing 1.2 m. A baseline at repeat-pump's 1.0 m stays for block scenarios (D17).
   - A canal network with a stage that falls through the dry season (Urzainki et al. 2023) stays a later option: it adds machinery, and its own inputs (outlet stage, canal geometry) are as unmeasured as the levels it replaces. *Done in part (D19):* a lumped store per sub-KHG. On the screened community record it overshoots the dry-season fall (section 6.12), so the fixed LiDAR levels with canals inside cells (D18) are the better default for now.
5. **Score the gates on screened station records (D20)?** *Decided 2026-10-29 (D21): yes, with `--screen-stations`.* The screened record changes the community result at Mendahara-Batanghari from a 63 cm to an 11 cm fall. Scoring the gates on it would change what every station gate measures, so it is left to the project owner; the rule itself is fixed in code.

**Recorded for later (decided 2026-10-28): MODFLOW 6.** Deferred, and listed in `re-peat/docs/12-parked.md`. MODFLOW 6 through flopy would give a standard, peer-recognised engine with a water budget per boundary, canal packages (RIV, DRN, SFR), pumps (WEL) and a Newton solver. Its costs are layering the peat (about 8–10 layers, thin at the top, to follow T(z) falling by a factor e every 0.4 m) and a compiled binary that the QGIS plugin would have to download. It faces the same open questions as our solver: the canal boundary in managed land, specific yield and the gate. flopy 3.11.0 (CC0, Python ≥ 3.11) and MODFLOW 6.8.1 (Windows binary, 2026-09-23) were checked on PyPI and GitHub on 2026-10-28.

## 9. Reproduction

```bash
# environment: REPEAT_KHG, REPEAT_DATA, REPEAT_HUB, EE_PROJECT (AGENTS.md)
python -m repeat_neraca.groundwater.fieldobs --khg 14.10.03 --source "$REPEAT_DATA/Peat depth and DTM/Tebingtinggi.csv" --format tebingtinggi2015
python scripts/check_field_inputs.py --khg 14.10.03 --source "$REPEAT_DATA/Peat depth and DTM/Tebingtinggi.csv" --out docs/reports/field_inputs_14.10.03.md
python scripts/model_sweep.py --khg 14.10.03 --start 2014-10-01 --end 2015-12-11 --res 200 \
    --tables tropical-small,tropical-large,urzainki2020 --drawdown 0.6,1.2 --out docs/reports/model_sweep_14.10.03_200m.md
repeat-neraca-model --khg 14.10.03 --start 2014-10-01 --end 2015-12-11 --res 100 --peat-table tropical-large --drawdown 1.2 --fetch
repeat-neraca-model --khg 16.02.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --res 200 --peat-table tropical-large --drawdown 1.2 \
    --et mod16nrt --fetch          # needs 03_neraca/inputs/stations*.csv (repeat-neraca-stations) and runs/deficit/neraca_khg.csv
# section 6.6 (SITMAT_PROCESSED set): candidate sites, community stations for Mendahara-Batanghari, the runs, the table
python scripts/rank_station_sites.py --out docs/reports/station_sites.md
repeat-neraca-stations --config ../re-peat/sites/15.05-07-10.01_mendahara_batanghari/neraca.yaml --kinds concession,community     --min-coverage 0.3 --out $REPEAT_KHG/15.05-07-10.01_mendahara_batanghari/03_neraca/inputs/model
for t in tropical-large drained-ismail-large; do for d in 1.2 0.4; do
  repeat-neraca-model --khg 16.02.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --res 200 --peat-table $t --drawdown $d --et mod16nrt --fetch
  repeat-neraca-model --khg 14.02-04-05.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --res 200 --peat-table $t --drawdown $d --et mod16nrt --fetch
done; done
repeat-neraca-model --khg 15.05-07-10.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --res 100 --peat-table tropical-large --drawdown 1.2 --et mod16nrt --fetch
repeat-neraca-model --khg 15.05-07-10.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --res 100 --peat-table tropical-large --drawdown 1.2     --drawdown-managed 0.4 --et mod16nrt          # clips the 2025 licence layer into 00_inputs/national/ on first use
# section 6.7: managed land held at a target (KHG and grid: 16.02.01 and 14.02-04-05.01 at 200 m, 15.05-07-10.01 at 100 m)
for t in "tropical-large --managed-target 0.4" "tropical-large --managed-target stations-loo" "drained-ismail-large --managed-target 0.4"; do
  repeat-neraca-model --khg 16.02.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --et mod16nrt --drawdown 1.2 --peat-base       --depth-fallback bbsdlp --res 200 --peat-table $t
done
# sections 6.7-6.8: canals outside licences at 0.6 m (Mendahara-Batanghari), and a dry and a wet year at Sugihan-Lumpur
repeat-neraca-model --khg 15.05-07-10.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --et mod16nrt --drawdown 0.6 --peat-base     --depth-fallback bbsdlp --res 100 --peat-table tropical-large --managed-target 0.4
python -m repeat_common.fetch_gee_balance --khg 16.02.01 --whole-khg --products chirps,mod16,mod16nrt --start 2018-11-01 --end 2026-10-01     --no-landcover --out $REPEAT_KHG/16.02.01_sugihan_lumpur/03_neraca/inputs/model --cache $REPEAT_KHG/16.02.01_sugihan_lumpur/cache/gee_balance_model
for y in "2018-11-01 2019-11-01 year2019_dry" "2021-11-01 2022-11-01 year2022_wet"; do set -- $y
  repeat-neraca-model --khg 16.02.01 --dem lidar --et mod16 --drawdown 1.2 --peat-base --depth-fallback bbsdlp --peat-table tropical-large       --managed-target 0.4 --res 200 --start $1 --end $2 --run $3
done
# section 6.9: scenarios from repeat-pump (blocks, water supply) against a baseline, then the comparison
C="--khg 15.05-07-10.01 --dem lidar --start 2025-11-01 --end 2026-10-01 --et mod16nrt --drawdown 1.2 --peat-base --depth-fallback bbsdlp --res 100 --peat-table tropical-large --managed-target 0.4"
repeat-neraca-model $C; repeat-neraca-model $C --blocks pump; repeat-neraca-model $C --blocks pump --supply pump
R=$REPEAT_KHG/15.05-07-10.01_mendahara_batanghari/03_neraca/lidar/runs/model
python scripts/compare_scenarios.py --baseline $R/tropical-large_p1.2_s1.2_t1.2_mt0.4_e0.3_100m_pb_dbbsdlp     --scenario $R/tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_e0.3_100m_pb_dbbsdlp $R/tropical-large_p1.2_s1.2_t1.2_mt0.4_blk_sup0.4_e0.3_100m_pb_dbbsdlp     --out docs/reports/scenarios_15.05-07-10.01_canals1.2.md
# sections 6.10-6.11: concession levels, canal levels in LiDAR, managed-target band with LiDAR canal levels (SITMAT_PROCESSED set)
python scripts/check_concession_levels.py --out docs/reports/concession_levels.md
python scripts/check_lidar_canal_levels.py --khg 14.10.01 --dtm "$REPEAT_DATA/lidar_pulau_padang_2016/DTM_2mFloat.tif" --flown "November 2016" --out docs/reports/lidar_canal_levels_14.10.01.md
for k in "16.02.01 200" "14.02-04-05.01 200" "15.05-07-10.01 100"; do set -- $k; for mt in 0.4 0.6 0.8; do
  repeat-neraca-model --khg $1 --dem lidar --start 2025-11-01 --end 2026-10-01 --et mod16nrt --drawdown primary=0.8,secondary=0.3,tertiary=0.3       --peat-base --depth-fallback bbsdlp --res $2 --peat-table tropical-large --managed-target $mt
done; done
python scripts/summarise_target_band.py --runs "$REPEAT_KHG/*/03_neraca/lidar/runs/model/tropical-large_*_mt0.[468]_e0.3_*_pb_dbbsdlp" --out docs/reports/managed_target_band.md
# section 6.12: canals inside cells (D18) and the canal store (D19); the numerical check; section 6.13: station outliers
python scripts/check_subcell_canal.py --out docs/reports/subcell_canal_check.md
C="--dem lidar --start 2025-11-01 --end 2026-10-01 --et mod16nrt --drawdown primary=0.8,secondary=0.3,tertiary=0.3 --peat-base --depth-fallback bbsdlp --peat-table tropical-large --managed-target 0.4"
for k in "16.02.01 200" "14.02-04-05.01 200" "15.05-07-10.01 100"; do set -- $k
  repeat-neraca-model --khg $1 --res $2 $C --canal-cells leak
  repeat-neraca-model --khg $1 --res $2 $C --canal-store
  repeat-neraca-model --khg $1 --res $2 $C --canal-store --canal-tau 0.1
done
repeat-neraca-model --khg 15.05-07-10.01 --res 200 $C; repeat-neraca-model --khg 15.05-07-10.01 --res 200 $C --canal-cells leak
M=03_neraca/lidar/runs/model
python scripts/summarise_target_band.py --runs "$REPEAT_KHG/*/$M/tropical-large_p0.8_s0.3_t0.3_mt0.4_e0.3_*_pb_dbbsdlp" "$REPEAT_KHG/*/$M/tropical-large_p0.8_s0.3_t0.3_mt0.4_lk*_e0.3_*_pb_dbbsdlp" \
    "$REPEAT_KHG/*/$M/tropical-large_p1.2_s1.2_t1.2_mt0.4_e0.3_*_pb_dbbsdlp" "$REPEAT_KHG/15.05*/$M/tropical-large_p0.6_s0.6_t0.6_mt0.4_e0.3_100m_pb_dbbsdlp" --out docs/reports/canal_modes.md
# D21, recommended set-up (section 6.14)
for k in "16.02.01 200" "14.02-04-05.01 200" "15.05-07-10.01 100"; do set -- $k; repeat-neraca-model --khg $1 --res $2 $C --canal-cells leak --screen-stations; done
python ../re-peat/tools/project_report_figures.py  # or call model_days_maps_final()
python scripts/check_station_outliers.py --khg 16.02.01 14.02-04-05.01 15.05-07-10.01 --out docs/reports/station_outliers.md
python scripts/summarise_model_runs.py --runs "$REPEAT_KHG/*/03_neraca/*/runs/model/[tdyu]*" --out docs/reports/model_station_runs.md
python -m pytest -q
```

## 10. Files

| Where | What |
|---|---|
| `repeat-neraca/src/repeat_neraca/` | `model.py`; `groundwater/simulate.py`, `fieldobs.py`, `fieldcheck.py` (new); the solver and grid modules (moved) |
| `repeat-neraca/scripts/` | `model_sweep.py`, `check_field_inputs.py`, `rank_station_sites.py`, `summarise_model_runs.py`, `compare_scenarios.py`, `check_concession_levels.py`, `check_lidar_canal_levels.py`, `summarise_target_band.py`, `check_subcell_canal.py`, `check_station_outliers.py` |
| `repeat-neraca/tests/test_model.py` | tests of the new modules |
| `repeat-neraca/docs/reports/` | `model_sweep_14.10.03_200m.md`, `field_inputs_14.10.03.md`, `station_sites.md` (and `.csv`), `model_station_runs.md`, `scenarios_15.05-07-10.01.md`, `scenarios_15.05-07-10.01_canals1.2.md`, `concession_levels.md`, `lidar_canal_levels_14.10.01.md`, `managed_target_band.md`, `subcell_canal_check.md`, `canal_modes.md`, `station_outliers.md` |
| `repeat-neraca/research_notes/` | `groundwater_models_review.md` (models and data), `peat_parameters_sumatra_kalimantan.md` (parameters, with Ismail et al. 2021 in full), `burned_peat_hydrology.md`, `canal_levels_evidence.md` (canal levels and plantation water tables) |
| `_khg/14.10.03_pulau_tebing_tinggi/` | `00_inputs/field_wtd.csv` (listed in `local_manifest.csv`), `03_neraca/inputs/model/` (forcing), `03_neraca/deltadtm/runs/model/` (runs), `logs/` |
| `re-peat/tools/pipeline/localize.py` | keeps manifest rows written by other tools |
| `repeat-pump` | solver removed; depends on `repeat-neraca` v0.2.0 (the pin is unchanged: 0.3.0 is not tagged, so the plugin keeps the 0.2.0 solver until a v0.3.0 tag exists and the pin moves) |

## References

- Apers, S., De Lannoy, G. J. M., Baird, A. J., Cobb, A. R., et al. (2022). Tropical peatland hydrology simulated with a global land surface model. J Adv Model Earth Syst 14, e2021MS002784. doi 10.1029/2021MS002784
- Castro et al. (2026). Effective restoration can avoid peatland fires. iScience. doi 10.1016/j.isci.2026.116041
- Cobb, A. R., Harvey, C. F. (2019). Scalar simulation and parameterization of water table dynamics in tropical peatlands. Water Resour Res 55(11), 9351–9377. doi 10.1029/2019WR025411
- Imanudin et al. (2018). J Wetlands Environ Manage 6(1), 12–26.
- Ismail et al. (2021). Hydrology Research 52(6).
- Izumi et al. (2025). Remote Sens Appl Soc Environ (InSAR peat surface oscillation, Kalimantan).
- Jaenicke, J., Wösten, H., Budiman, A., Siegert, F. (2010). Mitig Adapt Strateg Glob Change 15, 223.
- Kurnianto et al. (2026). J Hydrol Reg Stud 64, 103185. doi 10.1016/j.ejrh.2026.103185
- Mahdiyasa et al. (2024). Earth Surf Dynam 12, 929.
- PUI Gambut dan Kebencanaan, Universitas Riau. Produk unggulan (MONALAGA). https://puigk.unri.ac.id/id/produk-unggulan
- Putra, Baird, Holden (2022). Hydrol Process. doi 10.1002/hyp.14470
- Suryadi et al. (2021). J Eng Technol Sci 53(2). doi 10.5614/j.eng.technol.sci.2021.53.2.5
- Sutikno et al. (2023). Water Management for Integrated Peatland Restoration in Pulau Tebing Tinggi PHU. Springer. doi 10.1007/978-981-99-0906-3_9
- Urzainki, I., Laurén, A., Palviainen, M., Haahti, K., Budiman, A., Basuki, I., Netzer, M., Hökkä, H. (2020). Canal blocking optimization in restoration of drained peatlands. Biogeosciences 17, 4769–4784. doi 10.5194/bg-17-4769-2020
- Urzainki et al. (2023). Biogeosciences 20, 2099–2116. doi 10.5194/bg-20-2099-2023
