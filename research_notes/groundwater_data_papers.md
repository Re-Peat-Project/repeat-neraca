# Groundwater data and papers for the tropical peat model

Searched 2026-10-29. Scope: open data and papers that can help the open problems of the groundwater model (`docs/groundwater-model-report.md`, sections 2, 7 and 8):

1. canal boundary in managed land (canal levels, water supply in concessions);
2. specific yield (Sy) and ET falling with water-table depth;
3. a validation dataset for spatial pattern and dynamics (water-table series with coordinates, Sumatra or Kalimantan);
4. block effects measured before and after blocking;
5. water tables in unmanaged and community land.

Items the report or the task already lists (Taufik 2022 and 2023, Yananto 2021, Widodo 2019, Umarhadi 2022, Urzainki, Kurnianto, Apers, Ismail, Cobb & Harvey, Hooijer, Evans 2019, Deshmukh 2023, Hirano 2015, Ohkubo 2021, Wösten, Ritzema) appear here only where a data link or a new detail was found.

How each item was checked:
- **Crossref**: DOI, title, authors, year and journal read from api.crossref.org; abstract read where Crossref holds it.
- **Repository record**: Zenodo, figshare, Dryad, DataCite or PANGAEA API record read; file list, licence and description taken from it.
- **File read**: data file or readme downloaded and opened.
- **Full text**: article HTML downloaded and searched.
- **Page summary**: a web page read through a summarising fetch; numbers from these are less certain.

## Corrections to earlier notes

- `research_notes/Peatland neraca air operational gaps/README.md` says no open canal level series was found and no licence was confirmed. The Sebangau dataset (Putra et al. 2021, DOI 10.5518/960, item A1) has ditch-level loggers at the blocked and drained sites, under CC BY 4.0.
- `research_notes/groundwater_models_review.md` lists the Dadap et al. 2021 canal map as "by request to the author". The Stanford Digital Repository lists it as a 5 m raster under CC BY 3.0 (item A11). The file list could not be read.

## A. Open datasets

### A1. Sebangau forested, blocked and drained sites (Putra, Holden & Baird)

- Data: Putra, S. S., Holden, J., & Baird, A. (2021). *Water-level and rainfall data of Sebangau Tropical Peatland, Kalimantan, Indonesia* [Data set]. University of Leeds. https://doi.org/10.5518/960
- Paper: Putra, S. S., Holden, J., & Baird, A. J. (2021). The effects of ditch dams on water-level dynamics in tropical peatlands. *Hydrological Processes, 35*, e14174. https://doi.org/10.1002/hyp.14174
- Verified: Crossref and abstract; DataCite record; repository page (page summary); `readme.txt` read.
- Data: 22 CSV files and a readme, CC BY 4.0. Three sites, 22 August 2019 to 17 January 2020. Forested: 6 vented water-table loggers (3-hour interval) and manual readings. Blocked: 4 water-table loggers, 2 ditch-level loggers (files `blocked_auto_wl_US`, `_DS`), 7 manual wells. Drained: 3 water-table loggers, 2 ditch-level loggers, 7 manual wells. Rainfall and Penman-Monteith PET from two weather stations. Units per the readme: water level in cm relative to a local benchmark per site, water table in cm relative to the local surface per well. Well positions and station locations are given in the paper, not in the files. Coordinates: not in the files.
- Abstract numbers: dry-season drawdown 9.3 mm/d (forested), 9.6 mm/d (blocked), 12.7 mm/d (drained); ditches were dry in the dry season; in the wet season the share of time with water table deeper than 40 cm was 0% at the blocked site and 0 to 38% at the drained site.
- Helps: **4** (blocked against drained at the same time; a paired comparison, not before and after), **1** (measured ditch levels next to peat levels), **2** (drawdown rates with PET at the same site).

### A2. Apers et al. 2022 evaluation sites (Table B1) and model output

- Paper (known): Apers et al. (2022), *J Adv Model Earth Syst 14*, e2021MS002784.
- Data: Apers, S., Bechtold, M., & De Lannoy, G. J. M. (2022). *PEATCLSM_Trop: Integrating peat-specific land surface hydrology of natural and drained tropical peatlands in the GEOS CLSM framework* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6011689
- Verified: Zenodo API record; Table B1 extracted from the PMC full text (PMC9285420) and parsed.
- Data, Zenodo: netCDF output at 9 km (EASEv2) for CLSM, PEATCLSM Trop Nat and Trop Drain, CC BY 4.0. Model output only, no field data.
- Data, Table B1: 87 Southeast Asian sites with longitude, latitude (to 0.001°), drained or undrained, period and source. 59 are SIPALAGA stations (IDs such as `IN_BRG_140412_01`, Sungai Gaung, Riau; mostly 2019 to 2020): Riau 20, West Kalimantan 8, Central Kalimantan 14, Jambi 6, South Sumatra 6, South Kalimantan 4, Papua 1 (our count from the table). 12 are SATREPS sites (Central Kalimantan, Riau, Jambi, West Kalimantan). The rest are published sites in Brunei, Palangkaraya, Sebangau, Air Hitam (Jambi) and Selangor. The data statement says the water-level and ET data "are available at the sources indicated in Table B1"; the table names SIPALAGA and SATREPS, with no URL in the parsed text.
- New detail for problem 2: transpiration shuts off over a fraction F_wilt that is 0 above a water level of −0.70 m and 1 below −1.82 m for natural peat, and 0 above −1.54 m and 1 below −2.85 m for drained peat, linear in between (page summary of the full text).
- Helps: **3** (a coordinate list of SIPALAGA stations from 2019 to 2020 to match against SiTMAT stations and request histories), **2** (an ET reduction rule with thresholds).

### A3. Cobb & Harvey, Mendaram peat swamp (Brunei): water level, Sy and K tables

- Data: Cobb, A. R., & Harvey, C. F. (2019). PANGAEA collection 10.1594/PANGAEA.908215 with *Specific yield from the Mendaram peat swamp in Brunei Darussalam* (https://doi.org/10.1594/PANGAEA.908210), *Hydraulic conductivity ...* (https://doi.org/10.1594/PANGAEA.908209), water-level series for trails 6, 7, 8 and 10 (908201, 908206, 908207, 908208), throughfall (908214) and flowtube data (908211).
- Paper (known): Cobb, A. R., & Harvey, C. F. (2019). Scalar simulation and parameterization of water table dynamics in tropical peatlands. *Water Resources Research, 55*(11), 9351–9377. https://doi.org/10.1029/2019WR025411
- Verified: PANGAEA text files for 908208, 908209 and 908210 read; Crossref.
- Data: tab-delimited text, CC BY 4.0. Trail 10 water level: 20-minute Solinst logger, 6 Feb 2012 to 30 Jan 2013, at 4.375604 N, 114.354962 E.
- Sy knots as published (water level relative to the surface; the column is labelled "Specific yield function [m/s]" in PANGAEA, although the values read as dimensionless): −0.29 m: 0.136; −0.18 m: 0.167; −0.02 m: 0.254; +0.01 m: 0.291; +0.04 m: 0.289; +0.17 m: 0.686, with 95% bounds.
- K knots as published (m/s): −0.29 m: 6.2e-5; −0.005 m: 0.0116; +0.17 m: 76.1. Our arithmetic: 6.2e-5 m/s is about 5.4 m/d and 0.0116 m/s about 1,000 m/d. These are calibrated hillslope values from the scalar model, not core measurements.
- Helps: **2** (a measured Sy(z) that falls from about 0.25 at the surface to about 0.14 at −0.3 m in intact forest, a second source beside Ismail 2021).

### A4. Hirano, Palangkaraya daily groundwater level, and JapanFlux tower records

- Data: Hirano, T. (2023). *DailyGWL.xlsx* [Data set]. figshare. https://doi.org/10.6084/m9.figshare.22321129
- Data: Hirano, T., & Ohkubo, S. (2025). *JapanFlux2024 ID-PaD Palangkaraya drained forest* (https://doi.org/10.17592/001.2024102232), *ID-Pag Palangkaraya Undrained Forest* (https://doi.org/10.17592/001.2024102233), *ID-PaB Palangkaraya Drained Burnt forest* (https://doi.org/10.17592/001.2024102213) [Data sets]. Arctic Data archive System (ADS), Japan.
- Verified: figshare API record and file read; DataCite records for JapanFlux. The ADS pages were down for maintenance on 2026-10-29, so variables and periods of the JapanFlux files are not confirmed (*partly confirmed*).
- Data, figshare: one xlsx, CC BY 4.0, two sheets with columns Year, DOY, GWL (m): undrained forest 2015 to 2018 (1,461 days), drained forest 2013 to 2017 (1,618 days). Coordinates not in the file. Apers Table B1 places the undrained forest at 113.908 E, 2.322 S and the drained forest at 114.036 E, 2.346 S.
- Data, JapanFlux: CC BY 4.0; eddy covariance sensible heat, latent heat and CO2 per the DataCite description; tower points PaD −2.346071, 114.036408 (about 400 m from a 25 m wide canal); Pag −2.323917, 113.904392; PaB −2.340796, 114.0379 (about 200 m from the canal).
- Helps: **2** (latent heat next to groundwater level at drained, undrained and burnt sites, the basis of Hirano 2015's ET against minimum water-table relation), **3** (daily series, a forest pair for dynamics).

### A5. Oil palm smallholdings and forest, Jambi (Warren-Thomas et al.)

- Data: Warren-Thomas, E., Agus, F., Akbar, P. G., et al. (2022). *No evidence for trade-offs between bird diversity, yield and water table depth on oil palm smallholdings: implications for tropical peatland landscape restoration* [Data set]. Dryad. https://doi.org/10.5061/dryad.rr4xgxd9v
- Paper: Warren-Thomas, E., Agus, F., Akbar, P. G., Crowson, M., Hamer, K. C., Hariyadi, B., ... Hill, J. K. (2022). *Journal of Applied Ecology, 59*(5), 1231–1247. https://doi.org/10.1111/1365-2664.14135
- Verified: Crossref and abstract; Dryad API record and file list. The README could not be downloaded (Dryad now needs a token), so columns and coordinates are not confirmed (*partly confirmed*).
- Data: CC0. `Water_tables_loggers.csv` (10.2 MB), `Rainfall.csv`, yield and predictor tables. 41 smallholder oil palm farms, 12-month mean water table per plot −52 to −3 cm (August 2018 to August 2019), and 21 plots in an 11,000 ha protected peat swamp forest (−3 to +15 cm). Jambi; the peatland is not named in the abstract.
- Helps: **5** (one of very few logger datasets on smallholder land, with forest next to it), **3** (dynamics over a year).

### A6. Restoration trial along Sembilang National Park, South Sumatra (Hooijer et al. 2024)

- Paper: Hooijer, A., Vernimmen, R., Mulyadi, D., Triantomo, V., Hamdani, Lampela, M., et al. (2024). Benefits of tropical peatland rewetting for subsidence reduction and forest regrowth: results from a large-scale restoration trial. *Scientific Reports, 14*, 10721. https://doi.org/10.1038/s41598-024-60462-3
- Verified: Crossref; full text downloaded and searched.
- Content: former *Acacia crassicarpa* plantation, 4,800 ha, 257 compacted peat dams (blocks every 500 m), monitored 7.5 years from January 2016. 20 dipwells on a 4.2 km transect at mostly 250 m spacing, monthly water table and subsidence; monthly canal levels upstream and downstream of blocks 2021 to 2023; bypasses designed to keep canal water within 0.5 m of the surface, mostly closed in 2023. Water table about −0.6 m near the main road canal and about −0.3 m in the best rewetted zone; subsidence 7.1 cm/yr near the road canal, 3.2 cm/yr in the rewetted plantation, 2.2 cm/yr in forest about 2 km from canals.
- Data: "available from the corresponding author on reasonable request". Not open.
- Helps: **4** (the longest blocked-plantation record found; transect against distance to canal; block-by-block canal levels), **1** (canal levels held by blocks and bypasses in a former concession).

### A7. Rainfall-driven water-table maps for forested peat (Hooijer & Vernimmen 2026)

- Data: Hooijer, A., & Vernimmen, R. (2026). *Rainfall and water table depth maps for Southeast Asia peatlands* (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/69mbg22fxf.1
- Paper: Hooijer, A., & Vernimmen, R. (2026). Modelling water table depth variation in Southeast Asia forested peatlands using satellite rainfall data. *Scientific Reports, 16*, 26515. https://doi.org/10.1038/s41598-026-64641-2
- Verified: Crossref; DataCite record; full text downloaded and searched. The Mendeley page lists no individual files (*file formats not confirmed*; the paper says "GIS format").
- Content: daily bucket model on IMERG rain, WTD(t) = WTD(t−1) + (P − (ET + WF))/Sy, capped at the surface; calibrated on four long forest records (Sarawak 8 yr, Central Kalimantan 16 yr, Riau 6 yr, South Sumatra 5 yr); best fit with constant Sy 0.48 and ET + WF of 50 mm/d above the surface. Mean annual minimum WTD in forest ranges from −0.3 to −0.9 m across the region. CC BY 4.0, 10 km.
- Helps: **5** and **3** (an independent, regional reference for undrained forest WTD per KHG; a check that the model's unmanaged forest cells reach a plausible dry-season minimum), **2** (shows that Sy and ET trade off in a fit; their 0.48 is a fitted value, not measured).

### A8. Peat physical properties with coordinates (Taufik, Mendeley)

- Data: Taufik, M. (2024). *Physical peat properties of lowland tropical peatland subject to wildfire* [Data set]. Mendeley Data. https://doi.org/10.17632/2wcm6362y8.1
- Verified: DataCite record (description only; files not opened).
- Data: CC BY 4.0. 66 peat cores from two habitats; bulk density, porosity, water retention and fitted retention-curve parameters, with coordinates, depth, vegetation and date. A search snippet places the sampling in Jambi and Central Kalimantan in the 2019 and 2023 dry seasons (not confirmed from the record).
- Helps: **2** (retention curves give drainable porosity, a bound on Sy(z), at known points).

### A9. Bengkalis Island coastal peat (Kagawa et al.)

- Data: Kagawa, H., Yamamoto, K., Sutikno, S., et al. (2026). *Dataset for: Estimation of particulate organic carbon export to the ocean from lateral degradations of tropical peatland coasts* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.19159833
- Paper: Kagawa, H., Yamamoto, K., Sutikno, S., Haidar, M., Basir, N., Koyama, A., et al. (2026). *Biogeosciences, 23*, 2119–2154. https://doi.org/10.5194/bg-23-2119-2026
- Verified: Zenodo API record; two CSV files opened; article read by page summary (*partly confirmed*).
- Data: CC BY 4.0, CSV. `Water_level_WP1.csv`: 10-minute level (m) from 1 December 2014; the article describes it as the level of a waterway (channel) logged in a PVC well, to 31 January 2015. Also RTK-GNSS ground surveys 2013 to 2016, 10-minute weather at Selat Baru and Perapat Tunggal (2018, 2021), daily rain, DTM elevations. No coordinates for WP1 in the text read.
- Helps: **1** (a short channel-level record on Bengkalis), limited.

### A10. Water table on peat in Kalimantan from loggers and cameras (Yulianti et al. 2024)

- Paper: Yulianti, L., Evans, C. D., & Jovani-Sancho, A. J. (2024). Water table dynamic and peat motion in forest and burnt area in Central Kalimantan Province, Indonesia. *IOP Conference Series: Earth and Environmental Science, 1421*, 012005. https://doi.org/10.1088/1755-1315/1421/1/012005
- Verified: Crossref and abstract. No data deposit found.
- Content: loggers and time-lapse cameras at six locations (Hampangen, Tumbang Nusa, Sebangau National Park, a burnt area), December 2022 to June 2023; mean WTD −0.31 m at Sebangau, +0.12 m at Hampangen.
- Helps: **5**, weak (short, no open data).

### A11. Canal map of Southeast Asian peatlands (Dadap)

- Data: Dadap, N. (2020). *Drainage Canals in Southeast Asian Peatlands* [Raster data set]. Stanford Digital Repository. https://doi.org/10.25740/yj761xk5815
- Paper: Dadap, N. C., Hoyt, A. M., Cobb, A. R., Oner, D., Kozinski, M., Fua, P. V., Rao, K., Harvey, C. F., & Konings, A. G. (2021). Drainage canals in Southeast Asian peatlands increase carbon emissions. *AGU Advances, 2*(1), e2020AV000321. https://doi.org/10.1029/2020AV000321
- Verified: Crossref and abstract; repository page (page summary; *file list not confirmed*).
- Data: 5 m raster of canals and roads from July to September 2017 Planet imagery, Borneo, Sumatra, Peninsular Malaysia, CC BY 3.0.
- Helps: **1**, indirectly (a second canal geometry to compare with the KLHK canal layer; it is also the canal source Vernimmen & Hooijer 2026 used, item B1).

## B. Methods

### B1. Canal water depth from LiDAR (Vernimmen et al. 2020; Vernimmen & Hooijer 2026)

- Vernimmen, R., Hooijer, A., Mulyadi, D., Setiawan, I., Pronk, M., & Yuherdha, A. T. (2020). A new method for rapid measurement of canal water table depth using airborne LiDAR, with application to drained peatlands in Indonesia. *Water, 12*(5), 1486. https://doi.org/10.3390/w12051486
  - Verified: Crossref and abstract (the MDPI page refused automated access).
  - Method: on a 1 m LiDAR DTM, in each 100 m cell the water level is the minimum value and the land surface the median; canal water depth (CWD) = surface − water. Within 0.25 m of field values for 86% of 145 points, R² 0.74 (eastern Sumatra, West Kalimantan). Dry-season 2011 CWD in a drained Central Kalimantan area was mostly below −1.5 m.
- Vernimmen, R., & Hooijer, A. (2026). Satellite LiDAR reveals patterns in water table depth and flood risk in SE Asia coastal lowland and peatland plantations. *Frontiers in Environmental Science, 14*, 1869652. https://doi.org/10.3389/fenvs.2026.1869652
  - Verified: Crossref; article read by page summary (first 100,000 of 124,000 characters).
  - Method: ICESat-2 crossings of Dadap canals, water from ATL03 photons within 5 m of the canal centreline, land from ATL08 100 to 250 m on each side; 15,575 crossings, 2018 to 2025, 64% on peat.
  - Results: on peat, oil palm canal depth about −0.22 m at 1 to 3 m elevation to −0.63 m at 7 to 9 m; Acacia about 0.2 m deeper (to about −0.85 m). Interannual variation within 0.1 m at aggregate level, lowest in 2019 and 2023. They suggest CWD + 0.1 m as a proxy for peat water-table depth. Data "will be made available by the authors"; no repository.
- Helps: **1**, directly. These give measured canal levels in concessions by crop and elevation, in place of the assumed 0.4 m held level (report section 8, item 0). The airborne method can run on the LiDAR DTMs already in `_data` (Sugihan-Saleh 2020, Pulau Padang 2016); its result is a snapshot at the flight date. The ICESat-2 method needs ATL03 photons; the workspace holds ATL08 only (`_data/icesat2/`).

### B2. MODFLOW calibrated on 265 dipwells, Central Kalimantan (Hikouei et al.)

- Hikouei, I. S., Eshleman, K. N., Saharjo, B. H., Graham, L. L. B., Applegate, G., & Cochrane, M. A. (2025). Machine-learning based spatiotemporal performance analysis of degraded tropical peatland groundwater level numerical model. *Groundwater for Sustainable Development, 29*, 101413. https://doi.org/10.1016/j.gsd.2025.101413
- Hikouei, I. S., Eshleman, K. N., Saharjo, B. H., Graham, L. L. B., Applegate, G., & Cochrane, M. A. (2023). Using machine learning algorithms to predict groundwater levels in Indonesian tropical peatlands. *Science of the Total Environment, 857*, 159701. https://doi.org/10.1016/j.scitotenv.2022.159701
- Verified: Crossref for both; 2025 abstract read on the USC repository page (page summary); 2023 abstract from a search snippet (*partly confirmed*).
- Content (2025): MODFLOW on degraded peat in Central Kalimantan, calibrated and validated on monthly readings at 265 dipwells (2011 to 2019), NSE 0.97 and 0.95; Ks varies strongly in space, pilot points raise NSE to 0.98. Data statement: "The authors do not have permission to share data." Whether blocks are represented was not stated in the page read. (2023): random forest and XGBoost against regression for 2010 to 2012 on a drained, burnt dome; elevation and rain were the main predictors.
- Helps: **3** (shows that a dense dipwell network exists and that a Darcy model fits it monthly; the network is likely the KFCP area, *not confirmed*), **2** (spatially variable K).

### B3. Bucket model with Sy and ET + lateral loss (Hooijer & Vernimmen 2026)

See A7. A one-line model with an explicit Sy, a constant ET and a surface cap fits 5 to 16 year forest records; useful as a lower bound of complexity for unmanaged forest cells.

### B4. ecosys simulation of WTD and fluxes at Palangkaraya (Mezbahuddin et al. 2014)

- Mezbahuddin, M., Grant, R. F., & Hirano, T. (2014). Modelling effects of seasonal variation in water table depth on net ecosystem CO2 exchange of a tropical peatland. *Biogeosciences, 11*(3), 577–599. https://doi.org/10.5194/bg-11-577-2014
- Verified: Crossref and abstract.
- Content: process model coupling WTD and fluxes at the drained Palangkaraya forest, 2002 to 2005, tested against eddy covariance (R² above 0.8 for hourly CO2).
- Helps: **2**, as a reference for how a process model handles ET under deep water tables at a site with open data (A4).

### B5. Moisture release of peat as the water table falls (Kurnain 2019)

- Kurnain, A. (2019). Moisture release of tropical peat soils as decreasing water table. *Tropical Wetland Journal, 1*(1), 33–37. https://doi.org/10.20527/twj.v1i1.15
- Verified: Crossref and abstract.
- Content: hanging-column tests with the water table at 0, 10, 20, 30, 50 and 100 cm; a 3-parameter release model; more decomposed peat stores less and retains more.
- Helps: **2** (a laboratory route to Sy(z) by decomposition class).

### B6. High permeability of a natural dome (Baird et al. 2017)

- Baird, A. J., Low, R., Young, D., Swindles, G. T., Lopez, O. R., & Page, S. (2017). High permeability explains the vulnerability of the carbon store in drained tropical peatlands. *Geophysical Research Letters, 44*(3), 1333–1339. https://doi.org/10.1002/2016GL072245
- Verified: Crossref and abstract.
- Content: an ombrotrophic dome with permeability "similar to that of gravel"; simulations show ditch-drained domes keep water tables deep.
- Helps: **2** (supports the high-T sets), context for **1** (high K means canal level controls the adjacent peat strongly).

### B7. Canal blocking field studies at Pulau Tebing Tinggi

- Sutikno, S., Rinaldi, R., Putri, R. A., & Khotimah, G. K. (2020). Study on the impact of canal blocking on groundwater fluctuation for tropical peatland restoration. *IOP Conference Series: Materials Science and Engineering, 933*, 012052. https://doi.org/10.1088/1757-899X/933/1/012052
- Malik, H., Purnama, I. L. S., Sudarmadji, Santosa, L. W., & Naufal, M. (2022). Groundwater level fluctuations in peatlands as responses to canal block construction in Sungai Tohor, Tebing Tinggi Island, Indonesia. *IOP Conference Series: Earth and Environmental Science, 1041*, 012047. https://doi.org/10.1088/1755-1315/1041/1/012047
- Verified: Crossref and abstracts.
- Content: Sutikno: KHG Pulau Tebing Tinggi; three transects, dipwells at 1, 51, 101 and 201 m from the canal; rewetting up to 400 m upstream of a block; effect reaches 201 m across the canal when the canal rise exceeds 0.6 m. Malik: one logger, one year after BRG blocks at Sungai Tohor, levels 8.78 to 9.72 m (datum not stated in the abstract).
- Data: none open.
- Helps: **4**, at the test KHG (the 0.6 m canal-rise threshold and 200 m reach are numbers a block scenario can be checked against).

### B8. Regression model of GWL from SESAME data, Dompas, Riau (Pratama et al. 2020)

- Pratama, H., Sutikno, S., & Yusa, M. (2020). Modeling of groundwater level fluctuation in the tropical peatland area of Riau, Indonesia. *IOP Conference Series: Materials Science and Engineering, 796*, 012037. https://doi.org/10.1088/1757-899X/796/1/012037
- Verified: Crossref and abstract.
- Content: rainfall and GWL from SESAME equipment in Dompas village; GWL stayed below 0.4 m all year.
- Helps: **5** (a village station, likely outside licences, *not confirmed*).

## C. SIPALAGA and SESAME (BRG/BRGM) related

The station network was called SESAME (sensory data transmission service assisted by Midori Engineering) in early papers and is served through SIPALAGA. Apers et al. (A2) list 59 SIPALAGA stations with coordinates.

### C1. Irfan et al., South Sumatra stations (Sugihan, Saleh, Lumpur)

- Irfan, M., Kurniawati, N., Ariani, M., Sulaiman, A., & Iskandar, I. (2020). Study of groundwater level and its correlation to soil moisture on peatlands in South Sumatra. *Journal of Physics: Conference Series, 1568*, 012028. https://doi.org/10.1088/1742-6596/1568/1/012028
- Irfan, M., Satya, O. C., Arsali, Ariani, M., Sulaiman, A., & Iskandar, I. (2021). What is the rate of groundwater level decline on peatlands in South Sumatera during the 2019 extreme dry season? *Journal of Physics: Conference Series, 1816*, 012008. https://doi.org/10.1088/1742-6596/1816/1/012008 (known)
- Irfan, M., Koriyanti, E., Saleh, K., Hadi, Safrina, S., Awaludin, et al. (2024). Dynamics of peatland fires in South Sumatra in 2019: Role of groundwater levels. *Land, 13*(3), 373. https://doi.org/10.3390/land13030373
- Irfan, M., Safrina, S., Awaludin, A., Koriyanti, E., Sutopo, S., Kurniawati, N., Saleh, K., & Iskandar, I. (2026). Impact of La Nina 2021 on soil moisture and groundwater level on peatlands in South Sumatra. *AIP Conference Proceedings, 3463*, 040001. https://doi.org/10.1063/5.0337576
- Data: Irfan, M., Iskandar, I., Nurkhakim, M. Y., Ariani, M., Kurniawati, N., & Saputra, A. D. (2026). *Peatland groundwater level composites, uncertainty layers, and Ridge model coefficients for South Sumatra, Indonesia* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23047759 (other version: 10.5281/zenodo.23008826)
- Verified: Crossref for all papers; abstracts for 2020, 2021, 2024 (2026 AIP: metadata only); Zenodo API record and file list. The MDPI page refused automated access.
- Content: 2020: four SESAME stations, Saleh River 1 and 2, Lumpur River 1 and 2; GWL against soil moisture r 0.87 to 0.97. 2024: six BRG stations; suggests keeping GWL above −0.45 ± 0.09 m to limit hotspots.
- Data, Zenodo: CC BY 4.0 (scripts MIT). 1 km GeoTIFF GWL for a wet window (1 to 13 April 2019) and a dry window (13 to 25 November 2019) over South Sumatra KHG, EPSG:32748, with uncertainty and bootstrap layers, Ridge coefficients and Earth Engine scripts. The record states that the station GWL and rain data are not included and are "subject to the data provider's access conditions". Apers et al. (A2), by contrast, call the SIPALAGA data public. The two statements differ; access terms should be checked with BRGM.
- Helps: **3** (station names in KHG Sugihan-Lumpur and Saleh-Sugihan, our test KHG; the 1 km wet and dry rasters are a spatial pattern to compare with), **2** (dry-season recession rates).

### C2. Khakim et al. 2022, KHG Air Sugihan - Air Saleh

- Khakim, M. Y. N., Bama, A. A., & Tsuji, T. (2022). Spatiotemporal variations of soil moisture and groundwater level in a South Sumatra peatland, Indonesia during 2015–2018. *Geography, Environment, Sustainability, 15*(2), 58–70. https://doi.org/10.24057/2071-9388-2021-137
- Verified: Crossref and abstract; article page by page summary.
- Content: Sentinel-1 soil moisture regressed to field water level in KHG Sungai Air Sugihan - Sungai Air Saleh; dry-season WTD about 0.7 m in 2017 and 2018. The acknowledgments thank BRG "for providing SESAME data"; stations and coordinates are not named on the page.
- Helps: **3** (a satellite water-level map method already tried in a selected KHG).

### C3. Other SIPALAGA uses

Apers (A2) used SIPALAGA daily data from 4 February 2019. Yananto 2021 (known) used SIPALAGA in Riau. Hikouei (B2) did not use SIPALAGA. No paper found that publishes SIPALAGA series as a file.

## D. Not found, or found but not confirmed

- **Before and after blocking (problem 4): no open dataset was found.** Hooijer 2024 (A6) has a 7.5-year blocked plantation record on request only. The Sebangau data (A1) compare blocked and drained sites at the same time. Tebing Tinggi studies (B7) report results with no data.
- **Canal level series in concessions (problem 1)**: no open time series found. The ICESat-2 and airborne LiDAR methods (B1) are the measured alternative.
- Hoyt, A. M., Chaussard, E., Seppalainen, S. S., & Harvey, C. F. (2020). Widespread subsidence and carbon emissions across Southeast Asian peatlands. *Nature Geoscience, 13*(6), 435–440. https://doi.org/10.1038/s41561-020-0575-4. Crossref confirmed; no data repository found in the search.
- Khasanah, N., & van Noordwijk, M. (2019). Subsidence and carbon dioxide emissions in a smallholder peatland mosaic in Sumatra, Indonesia. *Mitigation and Adaptation Strategies for Global Change, 24*(1), 147–163. https://doi.org/10.1007/s11027-018-9803-2. Crossref only (CC BY 4.0); the article page could not be read. A lead for problem 5.
- CIFOR replication data: *Degradation increases peat greenhouse gas emissions in undrained tropical peat swamp forests* (https://doi.org/10.17528/cifor/data.00291, 2023) and *Hergoualc'h et al. (2017) Total and heterotrophic soil respiration in a swamp forest and oil palm plantations on peat in Central Kalimantan* (https://doi.org/10.17528/cifor/data.00061). Crossref metadata only; the CIFOR Dataverse did not respond, so whether they hold water-table series is not known.
- Deshmukh 2023 (known): Zenodo source data for the Nature figures, https://doi.org/10.5281/zenodo.7728463 (CC BY 4.0, six xlsx files of figure data). Whether these include the GWL series was not checked.
- Taufik 2022 Data in Brief (known): no separate repository record was found through DataCite.
- Tang, A. C. I., et al. (2018). *Methane flux data from a tropical peat swamp forest in Sarawak, Malaysia* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.1161966. One xlsx; whether it holds water table is not known.

## E. Shortlist, ranked

Ranked by: open access, coordinates, Sumatra or Kalimantan, and time series rather than snapshots.

1. **Apers et al. 2022 Table B1** (A2): 59 SIPALAGA stations and 12 SATREPS sites with coordinates and periods, Sumatra and Kalimantan; the key to finding long SIPALAGA records for our KHG. Problems 3, 2.
2. **Putra et al. 2021, Leeds 10.5518/960** (A1): open, CC BY 4.0, blocked and drained sites with ditch and peat loggers plus PET. Problems 4, 1, 2. Coordinates only via the paper.
3. **Vernimmen et al. 2020 and Vernimmen & Hooijer 2026** (B1): measured canal water depth in plantations, and a method we can run on our LiDAR. Problem 1.
4. **Warren-Thomas et al. 2022, Dryad** (A5): open CC0 logger data on 41 smallholder farms and forest in Jambi. Problem 5. Coordinates to confirm from the README.
5. **Cobb & Harvey 2019, PANGAEA** (A3): open Sy(z) and K(z) tables with logger series. Problem 2.
6. **Hirano figshare and JapanFlux** (A4): open daily GWL and eddy-covariance records at drained, undrained and burnt sites. Problems 2, 3.
7. **Irfan et al. 2020 to 2026 and Zenodo 23047759** (C1): stations inside Sugihan-Lumpur and Saleh-Sugihan, and open 1 km wet and dry GWL rasters. Problem 3.
8. **Hooijer et al. 2024** (A6): the best before-and-after blocking record, on request only. Problem 4.
9. **Hooijer & Vernimmen 2026 maps** (A7): open regional WTD for undrained forest. Problems 5, 3.
