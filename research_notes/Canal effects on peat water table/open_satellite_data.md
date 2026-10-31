# Open satellite and global datasets to make a peat water-table and canal model more realistic (Indonesia)

Searched 2026-10-30. Evidence labels: *full text* = article or report text read; *page* = article page read through a summarising fetch (numbers less certain); *abstract* = abstract only; *snippet* = search-result summary only (weakest). Already in project notes and not repeated: Hooijer and Vernimmen 2026 canal depth and IMERG bucket maps, Dadap canal map record, Apers/PEATCLSM sites, Irfan Zenodo rasters, Khakim 2022, Izumi 2025 numbers (r 0.23-0.8), SMAP L4 band name, NISAR start, Zahro 2025 (`groundwater_data_papers.md`, `groundwater_models_review.md` section 3, report 2.3). Sentinel-1 use already made by the project: `re-peat/reports/investigations/licence_edge_s1.md` (VV change wet to dry inside one cover class, relative moisture only).

Note on sources: several Indonesian rainfall-comparison and canal-detection papers could only be read as search snippets; those are flagged. Nothing here is from memory.

## 1. Sentinel-1 (backscatter, InSAR, open water) as a water-table proxy on tropical peat

### Takeaway
No published r or R2 between Sentinel-1 backscatter and water table on Indonesian peat was found. The tropical evidence is InSAR displacement (peat surface oscillation, subsidence), which works only on part of the area and best in the dry season; the quantitative backscatter skill comes from temperate peat, where it fails once the water table is deeper than about 0.6 m. For the model this means Sentinel-1 gives a relative wetness or coherence mask, and surface-oscillation time series at a few calibrated sites, not a water-table map.

### Cited Findings
- Mleczko et al. 2025 (Central Kalimantan, Sentinel-1 SBAS 2017-2022, against local GWL and peat-surface networks): in the wet season coherence is lost once water floods above the ground; in the dry season coherence lasts longer; correlations between SBAS displacement and in-situ GWL/surface data were more varied (higher range) in the dry season; SBAS returned displacement over only 34.4-59.8% of the peat area (391-826 km2), excluding dense forest and open water; very large level fluctuations may not be detected. No r or R2 values in the abstract. Rated abstract (NORA record and Consensus) — [NORA](https://nora.nerc.ac.uk/id/eprint/540352/), [Consensus record](https://consensus.app/papers/details/10021063f5cd5e719caa17ab6ed932e8/?utm_source=claude_desktop)
- Izumi et al. 2025 (Kalimantan, three years Sentinel-1 TInSAR, STL decomposition): peat surface oscillation (PSO) linearly related to GWL, r 0.23-0.8; PSO was 2.8-8.3% of GWL variation; amplitude larger in degraded than less degraded peat. The abstract does not say how many stations or which land covers. Abstract — [Consensus record](https://consensus.app/papers/details/875115b95e7f5692b18e1f74f1d81130/?utm_source=claude_desktop)
- Izumi et al. 2022 (IGARSS, Kalimantan, Jan 2018 to Jan 2020): large displacement in 2019 linked to GWL decline in the positive Indian Ocean Dipole year. Abstract — [Consensus record](https://consensus.app/papers/details/4a5f24d1fd355435ba13346cebcf388f/?utm_source=claude_desktop)
- Setyaningrum et al. 2026 (Central Kalimantan, SBAS 2017-2022): displacement -12.6 to +3.6 cm/yr, largest subsidence around drainage canals and infrastructure; Pearson r = -0.44 (p<0.001) between GWL and subsidence; cross-correlation peak r = -0.6 at a 10-month lag; rainfall r = -0.33 at lag 4. Abstract — [Consensus record](https://consensus.app/papers/details/785b7c97329d57e2bab556c896fe6a6a/?utm_source=claude_desktop)
- Umarhadi et al. 2021 (Bengkalis): Sentinel-1 mean velocity -1.41 cm/yr vs PALSAR-2 -2.65 cm/yr (2018-2019); RMSE against GWL-derived subsidence 1.988 cm/yr (S1) vs 1.383 (PALSAR-2); S1 underestimated subsidence by 0.96 cm/yr. Abstract — [Consensus record](https://consensus.app/papers/details/befc92337edf526090df9e3c8630c64f/?utm_source=claude_desktop)
- Tarigan et al. 2023 (Merang-Ngirawan KHG, South Sumatra, 80,000 ha, Sentinel-1A D-InSAR, yearly pairs 2014-2021): about 69% of pixels had coherence above 0.2; subsidence 28-80 cm/yr early, 16-48 cm/yr later; higher in used zone than blocked restoration zone for every pair; no regression against water table. Page — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2023.1088923/full)
- Backscatter on tropical peat, 2017 conference paper (Novresiandi et al.): peat and non-peat have similar annual sigma0 pattern, peat higher; the gap widens in the dry season, mostly VV; peat-depth classes overlap. Abstract only, not a water-table test — [Consensus record](https://consensus.app/papers/details/b7eabad7f6345eddbf7448ae6057feb8/?utm_source=claude_desktop)
- Analogues, not tropical. Drömling, Germany (drained temperate peat grassland, 60 wells): mean temporal Spearman 0.45 (+-0.17); correlation drops when mean WTD is deeper than about -0.60 m. Abstract — [Asmuß et al. 2019](https://consensus.app/papers/details/c3205572515b5310af157a610585351e/?utm_source=claude_desktop). Flow Country, Scotland (blanket bog): random forest on Sentinel-1 R2 0.66, RMSE 2.1 cm; multiple regression R2 0.59, RMSE 4.5 cm; WTD range only 0-35 cm. Abstract — [Toča et al. 2023](https://consensus.app/papers/details/03dc8c9016a65fa38f024d9dbe2aac93/?utm_source=claude_desktop)
- L-band HH backscatter against relative GWL, Mawas peat dome (Central Kalimantan, PALSAR-1, instruments on a 23 km bridge): correlations 0.63-0.84 under intact deep-peat forest; shallow peat under canopy gave a different, less steep slope; other environmental factors large. Full text (ESA Tropical Peat View final report, Hoekman) — [ESA TPV final report](https://eo4society.esa.int/wp-content/uploads/2020/07/ESA-TPV-Final-report.pdf)
- Mahakam floodplain PALSAR work: peat forest backscatter changed little with inundation and level-backscatter correlation was poor where level range was small. Snippet via a Hoekman JAXA presentation summary — [JAXA PDF](https://www.eorc.jaxa.jp/ALOS/jp/activity/kyoto/pdf/1-11_PKC1_DirkHoekman.pdf)
- NISAR L-band: public release began 2026-07-20 (observations from 2026-06-17), free through ASF DAAC and Earthdata, full record expected end of 2026. No Indonesian peat product or study found. Snippet — [NASA Earthdata](https://www.earthdata.nasa.gov/data/alerts-outages/nisar-l-band-data-now-publicly-available)
- Sentinel-1 open water and flood detection: no quantitative accuracy for Sentinel-1 flood or open-water mapping on Indonesian peat (canopy or canals) was found. Snippet-level search result stating only that other radar and optical sensors see open-water flooding only, not waterlogging under vegetation — [JAXA PDF](https://www.eorc.jaxa.jp/ALOS/jp/activity/kyoto/pdf/1-11_PKC1_DirkHoekman.pdf)

### Inferences
- The strongest published tropical signal is surface oscillation tied to GWL changes (r up to 0.8 at stations), and it needs per-site calibration; the oscillation explains only a few percent of GWL variation in amplitude terms, so it gives timing and relative amplitude, not level. Usable as a spatial check on where recession is large (degraded vs less degraded) at KHG scale, on dry-season intervals, over open and plantation land.
- Under forest and flooded ground C-band fails; the 0.6 m depth limit in the German study matches our observation that across-station backscatter correlation is weak. Do not expect backscatter to validate dry-season depths.
- L-band (PALSAR-2 ScanSAR already on Earth Engine; NISAR from 2026) is the better physical choice under canopy; the only tropical evidence is one dome in Central Kalimantan.
- Setyaningrum's finding that subsidence is largest around canals offers a distance-to-canal pattern check that the model can be compared with directly, using InSAR rate versus modelled mean drawdown by canal distance band.

### Gaps
- No open Sentinel-1 or PALSAR water-table product for Sumatra with accuracy numbers. Full texts of Mleczko, Izumi 2025 and Setyaningrum were not read, so station counts, depth ranges and land covers behind the r values are unknown.
- No Sentinel-1 canal-water or canopy-flooding accuracy on peat.

## 2. Optical canal detection, canal completeness, and whether canals hold water

### Takeaway
Two published canal maps exist for comparison (Dadap 2021 at 5 m, Planet July-September 2017; Haidar and Takeuchi 2022 SPOT-6/7 U-Net, Riau), and a radar canal-gap detector (Sentinel-1 NRT, ESA Tropical Peat View) found 85.5% of canal length in a validation block. No test of JRC Global Surface Water or Sentinel-2 NDWI for canal water in the dry season was found, and the limits of 10-30 m pixels against canals a few metres wide point to omission.

### Cited Findings
- Dadap et al. 2021: first regional canal map of Southeast Asian peatlands, high-resolution imagery plus CNN; drainage in at least 65% of peatlands; subsidence 3.2 times greater in intensively drained areas than in non-drained; adding canal data improved a subsidence model by 30%. Abstract (via Crossref-based fetch) — [AGU Advances](https://doi.org/10.1029/2020AV000321). Dataset (5 m raster, July-September 2017 Planet imagery, CC BY 3.0, Stanford): see `groundwater_data_papers.md` item A11. A follow-up quoted in a search result notes that the map treats roads as canals and uses relaxed true-positive criteria, adding uncertainty (snippet) — [search result for the Stanford record](https://geo.btaa.org/catalog/stanford-yj761xk5815)
- Haidar and Takeuchi 2022, U-Net with ResNet-34 on 1.5 m pan-sharpened SPOT-6/7, labels over 660 km2 in Indragiri Hilir, Riau, split 70/20/10: IoU 0.75 and 0.68 on validation, 0.67 and 0.59 on test for the two models. Snippet from sciforum record fragments — [sciforum](https://sciforum.net/paper/13655). The same snippet notes canal networks are not necessarily connected because of sedimentation, poor maintenance or canal blocking. SPOT-6/7 is commercial; the imagery is not open.
- ESA Tropical Peat View, Sentinel-1 near-real-time canal-gap detection, validated against visual interpretation of SPOT-6/7: overall detection rate 85.5%; 9.3 km of 64.2 km reference canal length missed; accuracy falls below 50% for the 5-10 m width class and for canals more than 80 degrees from the azimuth direction; 7.3 km of extra canal gaps were later found in SPOT after Sentinel-1 flagged them; some false alarms persist near canals. Full text of the final report; applies to canals through forest (canal gaps in canopy), not canals in open land — [ESA TPV final report](https://eo4society.esa.int/wp-content/uploads/2020/07/ESA-TPV-Final-report.pdf)
- Pixel limits (analogue, not peat): rivers about 20 m wide appear as one or two Sentinel-2 pixels; a 2026 ESSD paper states that many canals are only a few metres wide, below the 10-30 m pixels of Sentinel-2 and Landsat. Snippets from search results — [MDPI Remote Sensing 14(19)](https://www.mdpi.com/2072-4292/14/19/4693), [ESSD 18, 1855](https://essd.copernicus.org/articles/18/1855/2026/). JRC Global Surface Water is Landsat at 30 m; a small-reservoir paper in the same search notes omission errors at 30 m (snippet, not about canals).
- No study testing JRC GSW or Sentinel-2 NDWI for dry-season water in peat canals was found. The only measured statement on canal water in the dry season in the project notes is Putra et al. 2021 (Sebangau ditches dry in the dry season; abstract, in `groundwater_data_papers.md` A1).
- ICESat-2 canal levels, Vernimmen and Hooijer 2026, give the nearest evidence on canal water depth by region and crop (details in section 3).

### Inferences
- The incomplete national layer can be audited cheaply against Dadap (open, 5 m): a length-by-class overlay and missing-segment list per KHG. Roads are mixed in, so require a Sentinel-2 or road-layer filter. Mapped canals from 2017 will miss canals dug later.
- Sentinel-1 dry-season canal-gap detection is a way to find canals under forest canopy and test connectivity; it does not work on narrow canals oriented across the look direction.
- A canal "holds water" test with optical open-water frequency is plausible only for wide primary canals (about 10 m or more); secondary and tertiary canals will fall below pixel size. A 10 m Sentinel-2 NDWI or MNDWI time series per canal segment, dry-season minimum frequency, is a cheap pilot but is unvalidated; label it so.

### Gaps
- Dadap map validation numbers (precision, recall, IoU) were not retrievable (Wiley returned 403). File list on Stanford not read.
- No test of GSW or Sentinel-2 water in canals; no NICFI-specific canal model found (Dadap used Planet basemaps; whether those were the NICFI tropical basemaps was not confirmed).
- Haidar and Takeuchi values are from fragments; check the DOI 10.3390/ohow2022-13655 before citing.

## 3. Satellite LiDAR (ICESat-2 ATL08/ATL13, GEDI) for canal level and water table

### Takeaway
ICESat-2 plus a DTM is the only satellite route that has produced canal water depth at scale on Indonesian peat (15,575 crossings, 2018-2025), but it has no same-date field validation, uses a global-geoid offset assumption (0.75 m), and excludes canals running north-south. GEDI is not useful for canal water; as ground elevation it is noisy under peat forest.

### Cited Findings
- Vernimmen and Hooijer 2026, Frontiers Env Sci 14:1869652. Page read to character 100,000 of 124,720: water surface from ATL03 photons (median of photons in a 5 m band, at least 5 photons, IQR 25 cm or less, crossing angle above 30 degrees, photon spacing 0.7 m); land from ATL08 100 m segments sampled 100-250 m each side of the canal, excluded if more than 0.5 m difference across the canal. 15,575 measurements, Oct 2018 to Sep 2025, 9,946 (64%) on peat, 69% of those in oil palm. No numerical error for water surface elevation; no same-date field validation ("not possible"). Indirect checks only. The airborne-LiDAR predecessor reached R2 0.74, 86% within 0.25 m on 145 sites. Elevations are in EGM2008; local mean sea level in SE Asia may be 0.5-1 m lower, authors assume an average 0.75 m offset. Mean CWD sensitivity: including values up to 0.25 m above surface lifts mean from -0.42 to -0.29 m; slope threshold 0.5 to 1 m shifts it to -0.46. Annual variation within 0.1 m. Suggested proxy: water table = CWD + 0.1 m (peat levels about 0.05 m above canal levels in Hooijer 2024). Jambi appears only as a peat area on a figure; no Jambi statistics. Limitations: map gaps, 30 degree crossing constraint excludes near north-south canals (orbit inclination 92 degrees). Page — [Frontiers](https://www.frontiersin.org/articles/10.3389/fenvs.2026.1869652/full)
- DeltaDTM (used for land level): overall bias -0.03 m, MAE 0.42 m pooled over validation sites including one in Indonesia, not broken out for peat forest (snippet) — [DeltaDTM paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10917791/). In the Vernimmen page: absolute error within 0.5 m outside dense natural forest (Pronk et al. 2024), lowest accuracy in burnt peat with ferns.
- ICESat-2 ATL08 terrain height over peat domes in Kalimantan and Sumatra against airborne DTMs: RMSE 0.83 m overall, 0.68-2.68 m across KHG, R2 0.89 (Berninger and Siegert, snippet) — [search result for LMU repository](https://epub.ub.uni-muenchen.de/90354).
- GEDI over peat, Brunei (Cobb et al. 2023, Science of Remote Sensing 10.1016/j.srs.2022.100074), against 300 km2 airborne LiDAR: spatial filtering cut GEDI L2A RMSE from 15.98 m to 1.97 m (snippet; ATL08 figure not isolated).
- ATL13 (inland water) on Lake Toba: RMSE 0.06 m for lakes; reduced accuracy for small inland waters, no canal test found (snippet) — [ACRS 2025 abstract](https://acrs-aars.org/proceeding/ACRS2025/fp_abs-208.pdf).

### Inferences
- For Mendahara-Batanghari and Kampar-Gaung (oil palm and Acacia concessions), regional ICESat-2 CWD values (about -0.22 m at 1-3 m elevation to -0.63 m at 7-9 m for oil palm, in the notes) are priors for the canal level under managed land, with an uncertainty that includes the 0.75 m geoid assumption. Running the same method on our canals needs ATL03 photons, which the workspace does not hold (only ATL08).
- ICESat-2 repeat tracks are about 91 days and sparse; it gives a canal-level snapshot distribution per land cover and elevation, not a time series per canal.
- GEDI adds nothing for canal level; the project already judges its ground elevation unfit.

### Gaps
- No ATL13 or ATL03 canal accuracy against logger data. Last 24,720 characters of Vernimmen and Hooijer not read.
- Data for the 15,575 crossings "will be made available by the authors" with no repository (from `groundwater_data_papers.md`).

## 4. Soil moisture and water-table products (SMAP L4 incl. PEATCLSM, SMAP/S1, ESA CCI, optical indices, GRACE)

### Takeaway
SMAP L4 v8 has a PEATCLSM water-table band, but it is 9 km (11 km pixel in Earth Engine), the tropical parameter status in the operational product is not confirmed, and the published tropical evaluation is of the research version. Optical OPTRAM works on open and low-NDVI peat (R 0.7-1 with a best-pixel pick) and fails under forest. GRACE is far too coarse.

### Cited Findings
- SMAP L4 v8 in Earth Engine, band `depth_to_water_table_from_surface_in_peat` (m, range -5 to 0.15, positive above ground), 3-hourly, pixel 11,000 m (9 km EASE grid), public domain; the page gives conflicting end dates (2026-10-27 or 2025-10-14). Page — [Earth Engine catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_008)
- SMAP L4 v7 added the PEATCLSM module and an updated global peat map; peatland water-table, surface moisture and ET dynamics "considerably improved" against in-situ data over v6; water-table metrics were computed on model-only Nature Run 2008-2018, not the assimilation product. Snippet of NASA NTRS presentation and validation report; whether the operational run uses the tropical parameter sets was not found — [NTRS 20230000260](https://ntrs.nasa.gov/citations/20230000260), [NSIDC SPL4SMGP v7](https://nsidc.org/data/spl4smgp/versions/7)
- PEATCLSM tropical (Apers et al. 2022): in situ evaluation at Southeast Asian sites with overall improvement in bias and correlation over default CLSM; strong regional performance differences tied to forcing accuracy; the drained version did less well in the 2006 drought. Snippet of EGU presentation and abstract; the PMC full text blocked automated access, so the R and bias numbers were not read — [PMC9285420](https://pmc.ncbi.nlm.nih.gov/articles/PMC9285420/)
- OPTRAM (Landsat 7/8, 30 m) against in-situ water table at tropical peat sites in Indonesia, Malaysia and Peru (Koupaei-Abyazani et al. 2024, JGR Biogeosciences): R 0.7-1 in minimally forested and non-forested low to intermediate NDVI with a "best pixel" approach; R average -0.04 to 0.24 in high-NDVI areas. No RMSE reported on the page read. Abstract (page) — [Wisc SSEC record](https://pubs.ssec.wisc.edu/pub/view/15698). A northern-peatland analogue (53 sites) found the OPTRAM-water-table link often disappears when the water table deepens beyond 0 to -100 cm depending on site (snippet).
- Sentinel-1 soil moisture (10 m, SEPAL, support vector regression) in Central Kalimantan peat correlated with groundwater level with land-cover-dependent response (IOP Conf. Ser. 2021, snippet). Khakim et al. 2022 for Sugihan-Saleh is in the project notes.
- Peat moisture data for validation: a Scientific Data-style daily peat moisture dataset from 21 Sumatran stations, 2018-2019 (Taufik, already in the workspace as SIPALAGA/Mendeley data) — [PMC9936326](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9936326/)
- SMAP soil moisture for peat fire (Sumatra, Borneo, Peninsular Malaysia, 2015 burning season): drier soil up to 30 days before fire correlated with burned area (snippet) — [tropicalpeatlands.org](https://www.tropicalpeatlands.org/knowledge/publication/11463-17349).
- GRACE: native footprint at least 90,000 km2; finer grids are resampled; in a 23,000 km2 Kalimantan basin its sub-basin reliability is poorly characterized (HESS 2026 snippet) — [HESS 30, 4771](https://hess.copernicus.org/articles/30/4771/2026/). Global hydrological models carry negligible wetland storage variability (same preprint snippet).
- ESA CCI soil moisture and SMAP downscaled to 1 km with Sentinel-1: no validation on tropical peat was found (a Brazil dry-forest study gives SMAP r 0.85 vs CCI r 0.41; non-peat, snippet).
- Not found: TVDI applied to tropical peat water table.

### Inferences
- SMAP L4 water-table band is a regional seasonal anomaly check at 9-11 km, a handful of pixels per KHG. Because our KHG are 10,000-200,000 ha (100-2,000 km2), it gives one to ten pixels; it cannot test pattern, and whether the level is physically comparable to ours is unproven.
- OPTRAM is the one open index with tropical peat water-table evidence, restricted to open and low-NDVI land. It could give a dry-season pattern over cleared, smallholder or burnt land (where the model is weakest) with Landsat 30 m or Sentinel-2 SWIR 20 m, but the "best pixel" selection is calibrated per station; without calibration it is a relative index. Treat as a candidate test, not a validated product.
- GRACE: drop.

### Gaps
- No peer-reviewed R or bias for SMAP L4 peat water table in Indonesia; the full Apers tables were not read (blocked).
- OPTRAM RMSE and the number of sites were not obtained.

## 5. Forcing improvements and 30 m topography

### Takeaway
No source found shows gridded rain or ET beating CHIRPS and MOD16 on Indonesian peat for daily water-table modelling. Daily rainfall skill of all open products is modest, and rankings differ by site. Topography is the stronger constraint: the DEM error under canopy (metres) exceeds the head differences the model resolves.

### Cited Findings
- Rainfall product comparisons in Sumatra and Kalimantan (all search snippets from Indonesian-language journals, not verified): West Sumatra, three stations, CHIRPS best daily accuracy but daily correlation about 0.17; another West Sumatra study found GPM-IMERG most reliable at longer scales; Lampung Selatan 2018-2020, GSMaP best at rain detection (CSI), IMERG best daily linearity, all with sizable errors; Balikpapan favoured GSMaP daily, IMERG overestimating, CHIRPS underestimating; Sulawesi (MAUSAM) CHIRPS ranked first. Conclusion in the search summary: best product depends on metric and location — [Itera JSAT](https://journal.itera.ac.id/index.php/jsat/article/view/702), [Faktor Exacta](https://journal.lppmunindra.ac.id/index.php/Faktor_Exacta/article/view/27697), [MAUSAM](https://mausamjournal.imd.gov.in/index.php/MAUSAM/article/download/6791/5888/33545)
- IMERG drove a 5-16 year bucket model on forest peat records (Hooijer and Vernimmen 2026) — already in `groundwater_data_papers.md` A7; not repeated.
- ET over tropical peat: the tower evidence is Hirano et al. 2015 (Palangkaraya, 2002-2009, ET tracks net radiation, stable in undrained forest) and Ohkubo 2021 (about 13 years, drained burnt site); no comparison of WaPOR, MOD16 or PML_V2 with peat flux towers was found. WaPOR V2 validation exists for Africa (14 eddy-covariance stations, Blatchford et al. 2020). Snippets — [Hirano 2015](https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/65234), [Ohkubo 2021](https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/90757)
- DEMs: FABDEM developers report forest mean absolute error 2.88 m against 5.15 m for GLO-30 and median error 0.45 m against 12.95 m for GLO-30 in dense canopy (developer conference abstract, via snippet; not independent). An Indian independent check found FABDEM MAE 4.73 m in alluvial plains (non-peat). DeltaDTM MAE 0.42 m pooled, Indonesia in the validation set (snippet). A Central Kalimantan peat study reports a vertical accuracy of 1.38 m at 95% but the DTM tested is not stated — [GIM International](https://www.gim-international.com/content/article/deltadtm-mapping-coastal-terrain-elevation), [PMC10917791](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10917791/)
- Cobb et al. 2023 and Berninger and Siegert: satellite LiDAR ground elevation is usable only after filtering; RMSE about 1-2.7 m (section 3).

### Inferences
- Changing the rain product is unlikely to improve the water table unless a station rain series exists locally; a station check of CHIRPS at the stations that ship rain with SiTMAT/SIPALAGA would tell whether bias matters, and it uses data already in the workspace.
- Per-sub-KHG forcing is cheap in Earth Engine (already used); per-cell forcing at 100 m adds nothing with 5-10 km native rain. Gradient information on rain comes from orography and coastline only.
- A canopy and error-aware DTM (DeltaDTM, Meta canopy-corrected) remain essential; the sub-metre canal head differences are below the DTM error under forest, so canal-relative levels should come from local LiDAR where available, not from satellite DEMs.

### Gaps
- No quantitative peat-specific skill for IMERG, GSMaP or CHIRPS (only unverified Indonesian snippets); none for MOD16, PML_V2, WaPOR on tropical peat. FABDEM was not tested on peat forest in any source found.

## 6. What can validate spatial pattern, and what can tell whether canals hold water

### Takeaway
No open satellite product gives a validated water-table map at 100 m on Indonesian peat. Spatial-pattern checks are possible only as relative patterns: InSAR subsidence and oscillation by distance to canal (the pattern the model predicts), OPTRAM on open land, and L-band backscatter. Canals holding water cannot be decided from optical open-water maps for secondary and tertiary canals; ICESat-2 regional canal depths give priors for primary and secondary canals in plantations.

### Cited Findings
- All evidence above; see sections 1-5. In particular, subsidence is largest around canals (Setyaningrum 2026, abstract) and used land subsides more than blocked land (Tarigan 2023, page).

### Inferences
Ranking (expected usefulness for this model, 3 = high, 0 = none; judgements from the evidence above, not measured):

| Option | (a) Validate spatial pattern | (b) Do canals hold water | (c) Find undigitised canals | (d) Improve forcing | Effort |
|---|---|---|---|---|---|
| Sentinel-1 SBAS InSAR rate and oscillation (own processing) | 2 (relative, by canal distance; partial coverage) | 0 | 0 | 0 | High: SBAS stack and station calibration, 1-2 weeks per KHG |
| Sentinel-1 backscatter wet-dry change (already used) | 1 (relative moisture, weak under canopy and deep tables) | 0 | 0 | 0 | Done |
| PALSAR-2 ScanSAR (EE) or NISAR L-band backscatter | 1-2 (one tropical dome shows r 0.63-0.84; untested at KHG scale) | 1 (flooding under canopy) | 0 | 0 | Medium |
| Sentinel-1 canal-gap detection (TPV-type) | 0 | 0 | 2 (85.5% length detected in one test; weak for narrow or across-track canals; forest only) | 0 | High: method not available as open code (not found) |
| Dadap 5 m canal raster as audit layer | 0 | 0 | 3 (open, CC BY 3.0, 2017 only; includes roads) | 0 | Low: 1-2 days |
| Sentinel-2 or Landsat water frequency (NDWI, JRC GSW) | 0 | 1 (only wide canals; untested) | 1 | 0 | Low-medium, untested |
| ICESat-2 ATL03 canal crossings plus DTM | 0 | 2 (levels per class and elevation, no time series; geoid offset 0.75 m assumed) | 0 | 0 | Medium-high: ATL03 download and photon processing |
| Airborne LiDAR canal depth on KLHK LiDAR DTMs (project data) | 0 | 3 (snapshot at flight date, 86% within 0.25 m in the source) | 1 | 0 | Medium |
| OPTRAM (Landsat/Sentinel-2 SWIR) on open land | 2 (R 0.7-1 at stations in low-NDVI land; per-station calibration) | 0 | 0 | 0 | Medium |
| SMAP L4 v8 peat water-table band | 1 (9-11 km, regional anomaly only) | 0 | 0 | 0 | Low (already on EE) |
| GRACE | 0 | 0 | 0 | 0 | Not worth doing |
| IMERG / GSMaP in place of or beside CHIRPS | 0 | 0 | 0 | 1 (no peat skill evidence; rankings inconsistent) | Low |
| WaPOR / PML_V2 beside MOD16 | 0 | 0 | 0 | 1 (no peat tower validation found) | Low |
| FABDEM, GLO-30 | 0 | 0 | 0 | 1 (topography; forest error metres) | Low |

Priority for the project: (1) airborne-LiDAR canal depth on existing LiDAR DTMs and ICESat-2 priors for canal levels in concessions, (2) Dadap overlay to audit the national canal layer, (3) a Sentinel-1 InSAR rate by canal-distance band at Kampar-Gaung or Mendahara-Batanghari as a spatial check, (4) an OPTRAM pilot on open land at the station KHG.

### Gaps
- No source gives an open, validated water-table map for Sumatran peat at 100 m. Canal-holding-water tests from optical data are unpublished for peat canals.
- Not read: full text of Mleczko 2025, Izumi 2025, Setyaningrum 2026, Koupaei-Abyazani 2024 and Apers 2022 results tables. Fetch these before quoting beyond the figures above.
