# Open satellite and global gridded datasets for a tropical peatland water balance (Sumatra/Kalimantan/Papua)

Scope note: research done with about 14 web searches (snippet-level, few full-page fetches), as of Oct 2026. Items marked "[unverified, background]" come from the researcher's prior knowledge of product documentation and were NOT confirmed by a source in this session; the report writer should treat them as leads, not facts. Peat-specific validation evidence is thin for almost every product; that is itself a key finding.

## 1. Precipitation

### Takeaway
IMERG V07 (Early ~4 h, Late ~14 h, Final ~4 months) and CHIRPS v3 (prelim 2 days after pentad, final monthly) are the practical GEE-accessible choices. I found no peatland-specific rainfall validation; Indonesian evidence is from mountain/urban sites and shows IMERG-F overestimation and large small-scale variability. Gauge anchoring (BMKG, BRIN, BRGM station networks) remains necessary.

### Cited Findings
- IMERG latency: Early about 4 h (forward morphing only), Late about 14 h (forward and backward morphing), Final about 4 months after the observation month (adds monthly gauge analysis). — [NASA GPM IMERG Early/Late/Final pages](https://gpm.nasa.gov/taxonomy/term/1357), [Late](https://gpm.nasa.gov/taxonomy/term/1415), [Final](https://gpm.nasa.gov/taxonomy/term/1417)
- IMERG V07: initial and retrospective processing of Early, Late and Final completed as of August 2024; current algorithm listed as V07B, data from January 1998. UCAR notes that the changing GPM constellation can create artifacts in multi-year change studies. — [NASA GPM Final Run](https://gpm.nasa.gov/taxonomy/term/1417), [UCAR dataset record](https://ckanprod.data-commons.k8s.ucar.edu/dataset/faaceb56-2017-465b-bb47-c34634cc6445)
- Kototabang (West Sumatra, mountainous) 15-year comparison with an optical rain gauge: IMERG-Final overestimated rainfall at all time scales, performance improved with longer aggregation, and false-alarm rate was high due to small-scale spatial variability. — [Kototabang IMERG study](https://prisma.simaster.ugm.ac.id/karya_files/statistical-comparison-of-imerg-precipitation-products-with-optical-rain-gauge-observations-over-kototabang--indonesia-dcfcd07e645d245babe887e5e2daa016)
- Single-gauge bias correction of IMERG in mountainous Sumatra: linear scaling gave the best improvement, and correction worked better at daily than hourly resolution. — [Bias correction of IMERG, Sumatra](https://tis.wu.ac.th/index.php/tis/article/view/7592)
- CHIRPS v3 released early 2025 (DOI 10.15780/G2JQ0P). GEE IDs: `UCSB-CHC/CHIRPS/V3/DAILY_SAT`, `UCSB-CHC/CHIRPS/V3/DAILY_RNL`, `UCSB-CHC/CHIRPS/V3/PENTAD` (note CHC, not CHG). Preliminary version is available 2 days after the end of a pentad; the final is produced monthly, typically in the third week of the following month. Coverage from 1981. — [CHC newsletter June 2025](https://climatehazardscenter.beehiiv.com/p/climate-hazards-center-june-2025-newsletter), [GEE DAILY_SAT](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_SAT?hl=hi), [GEE PENTAD](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_PENTAD?hl=ru), [CHC CHIRPS page](https://chc.ucsb.edu/node/497)
- CHIRPS has shown substantial daily-scale bias in global evaluation (Dinku et al. 2018, as cited in a secondary paper); a 2020-2024 CHIRPS/IMERG/GSMaP validation at Balikpapan (East Kalimantan) against SYNOP exists but results were not retrieved. — [cee-2026-0011](https://reference-global.com/download/article/10.2478/cee-2026-0011.pdf)
- ERA5-Land vs CHIRPS over Indonesia 1990-2022: similar annual totals and annual cycle; bias is seasonal and regional (low bias often in JJA dry season in south Sumatra/Java/south Kalimantan/Sulawesi/part of Papua, high bias in other season; snippet truncated). South Sumatra peatland study: reanalysis showed only weak seasonal variation in diurnal rainfall amplitude versus in-situ. — [ERA5-Land Indonesia trends (UI)](https://dara.ui.ac.id/research-output/13124f9e-9f15-463e-b3c0-4c9e7b28e63b)
- A Riau process-model (ecosys) study used ERA5 forcing and corroborated peat moisture and WTD against SMAP and site data, without isolating ERA5 rainfall bias. — [ESS Open Archive](https://essopenarchive.org/doi/full/10.1002/essoar.10501280.1)

### Inferences
- Combining IMERG Late (operational, ~14 h) with CHIRPS v3 prelim/final and a gauge-based monthly rescaling (BMKG/BRIN/BRGM) is the sensible operational design; IMERG Early only for flood/fire triggers.
- Peat landscapes are lowland coastal/inland with convective afternoon-night rainfall; daily-scale random error will be large, so use at least pentad to monthly water balance aggregation or bias-correct per KHG with local gauges.
- [unverified, background] GSMaP (JAXA, ~4 h NRT, GEE `JAXA/GPM_L3/GSMaP/v8/operational` and `.../reanalysis`), MSWEP (Beck et al., not on GEE, access via GloH2O, free for research with request), CMORPH (NOAA CDR), PERSIANN-CDR/CCS (CHRS, also on GEE for CDR) and BMKG/BRIN gauges exist but were not verified here; MSWEP v2.8 vs the newer MSWEP status should be checked.

### Gaps
- No peat-specific rainfall product validation (bias per product over Riau, Central Kalimantan, South Sumatra, Merauke). Balikpapan CHIRPS/IMERG/GSMaP results not retrieved.
- No verified info on GSMaP, MSWEP, CMORPH, PERSIANN versions/latency, BMKG/BRIN data access terms, or whether GPM core satellite faces end-of-life issues in 2026.
- CHIRPS v3 GEE ingestion lag not documented; GEE catalog end dates differ by cached page (check live).

## 2. Evapotranspiration and PET

### Takeaway
No source found that validates MOD16, PML_V2, GLEAM or others against Indonesian peat eddy-covariance towers (Central Kalimantan peat swamp forest flux data exist for 2002-2009). GLEAM4 (0.1 deg, daily) and PML_V2 (500 m, 8-day) are the most defensible open products; MOD16 is widely available but suffers in cloudy tropics [unverified, background].

### Cited Findings
- GLEAM4 (Miralles et al. 2025, Scientific Data 12:416, doi:10.1038/s41597-025-04610-y): 0.1 deg daily; hybrid approach with a neural network learning evaporative stress from eddy-covariance and sap-flow data, scaling potential evaporation. GLEAM4.1a spans 1980-2023 (reanalysis radiation/temperature); 4.1b spans 2003-2023 (mostly satellite driven); Zenodo v4.2 released 23 Jan 2025; also at gleam.eu. — [Springer Nature community post](https://communities.springernature.com/posts/unveiling-gleam4-the-latest-breakthrough-in-global-land-evaporation), [Zenodo](https://zenodo.org/records/14724263), [EPFL record](https://infoscience.epfl.ch/items/205324d2-a05c-4b26-a390-c9419dcd92d8)
- PML_V2 (Zhang et al. 2019, RSE 222:165-182): 500 m, 8-day ET, components and GPP; GEE `CAS/IGSNRR/PML/V2_v018` (earlier v017, 0.1.4 marked deprecated in the catalog; the German catalog page flags v018 as deprecated too, check the live catalog for a newer version); CC-BY 4.0; catalog states agreement with 95 flux sites. — [GEE PML V2 v018](https://developers.google.cn/earth-engine/datasets/catalog/CAS_IGSNRR_PML_V2_v018?hl=es-419), [v018 (de) deprecated tag](https://developers.google.com/earth-engine/datasets/catalog/CAS_IGSNRR_PML_V2_v018?hl=de)
- MOD16A2/MYD16A2 Collection 6.1: 8-day, 500 m; C61 has no algorithm change versus C6 (calibration/polarization updates in L1B). No retirement notice found; GEE IDs `MODIS/061/MOD16A2`, `MODIS/061/MYD16A2`; catalog end dates vary by cached page. — [MOD16 User Guide V61](https://LPDAAC.USGS.GOV/documents/931/MOD16_User_Guide_V61.pdf), [GEE MYD16A2](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MYD16A2?hl=pl)
- Low-latitude (30S-30N, 40 flux sites) evaluation: GLEAM generally had highest R2, smallest PBIAS and best RMSE versus MOD16 (C5, C6) and ALEXI; unclear if peat sites included. — [Atmosfera summary of the low-latitude evaluation](https://www.atmosfera.unam.mx/evaluation-of-remote-sensing-based-evapotranspiration-products-at-low-latitude-eddy-covariance-sites/)
- Amazon (LBA, 9 towers): MOD16 and GLEAM both represent observed ET; cropland (28 sites): MOD16 and PML-V2 similar accuracy. Neither is peat. — [LBA study (UFRGS)](https://lume.ufrgs.br/bitstream/10183/179377/1/001067225.pdf), [Crop ET validation](https://www.ygxb.ac.cn/en/article/doi/10.11834/jrs.20222008)
- Ground truth: Central Kalimantan peat swamp forest eddy covariance, 4-6 years in 2002-2009 at three sites of different disturbance. — [Tropical Peatlands knowledge hub](https://www.tropicalpeatlands.org/knowledge/publication/11463-24006)

### Inferences
- Use GLEAM4 as baseline AET (daily, 0.1 deg is coarse for KHG-scale, but peat domes are large), PML_V2 for 500 m spatial patterns, and cross-check against the Kalimantan flux tower literature. Open-water evaporation from canals/flooded peat is not captured as such by land-ET products.
- Cloud cover degrades optical LAI/albedo inputs to MOD16/PML; gap-filled composites hide this uncertainty.
- [unverified, background] ERA5-Land (GEE `ECMWF/ERA5_LAND/DAILY_AGGR`, hourly 9 km, ~5 day latency; ERA5 (not Land) ~5 days) provides PET inputs; SSEBop/WaPOR (WaPOR v3 covers Africa/Near East plus global at 300 m since v3, check Indonesia coverage), ECOSTRESS (irregular, 70 m, ISS sampling, cloud limited), LSA SAF/Himawari-9 radiation (AHI, 10 min) and CERES/CAMS radiation are candidates for refined PET but were not verified.

### Gaps
- No peat-specific quantitative error figures (RMSE, bias) for any ET product.
- WaPOR, SSEBop, ECOSTRESS, LSA SAF/Himawari radiation, ERA5-Land PET not researched in this session.
- PML_V2 current version/deprecation status ambiguous across catalog pages.

## 3. Soil moisture, water table, SAR, InSAR, NISAR

### Takeaway
Direct, peer-reviewed SAR-to-WTD relations for Indonesian peat are weak-to-moderate (Riau Sentinel-1 VV vs groundwater level r = -0.648); InSAR subsidence is a better proxy of hydrological state but coherence collapses in wet/flooded conditions. NISAR L-band is now public (provisional) and the best new hope.

### Cited Findings
- Riau study: strongest correlation between Sentinel-1 VV backscatter and measured groundwater level was r = -0.648 (moderate). — [Tropical Peat Watch/SBAS search result (UGM)](https://ir.lib.ugm.ac.id/id/eprint/5549)
- South Sumatra (KHGSS, Sugihan-Saleh), 2015-2018: multiple regression on Sentinel-1 and ECMWF data estimated soil moisture and groundwater level; recommended mean annual water table shallower than 0.40 m for fire risk. — [JAXA K&C / NERC NORA search result](https://nora.nerc.ac.uk/id/eprint/540352/)
- Central Kalimantan SBAS-InSAR 2017-2022 with Sentinel-1: groundwater swings from +1 to -2 m; coherence lost during wet-season flooding, better in dry season. — [Frontiers in Env. Sci. 2023](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2023.1088923/pdf)
- Kalimantan 3-year Sentinel-1 time series: large subsidence in 2019 linked to GWL decline under positive IOD. — [Izumi et al. 2022](https://repository.unp.ac.id/id/eprint/581/)
- Bengkalis Island SBAS: PALSAR-2 (L-band) overall RMSE 1.383 cm/yr vs Sentinel-1 1.988 cm/yr. — [SBAS multifrequency paper](https://www.iges.or.jp/jp/pub/sbas/en)
- Tropical Peat Watch (Wageningen/SarVision/LAPAN, Post-K&C): planned PALSAR-1/2 + Sentinel-1 monitoring, backscatter vs groundwater gauges, L-band suited to flooding under canopy and excess drainage along canals; open-data status of outputs not confirmed. — [JAXA K&C report (Hoekman)](https://www.eorc.jaxa.jp/ALOS/jp/activity/kyoto/pdf/1-11_PKC1_DirkHoekman.pdf)
- SMAP over dense vegetation overestimates soil moisture; polarization-based correction cut forest bias 0.127 -> 0.060 cm3/cm3 against US CRN; forests are underrepresented in SMAP validation. — [Science of Remote Sensing 2024 (DOAJ)](https://doaj.org/article/94e9df90a1c0470a980ebc1c07e5261c), [SMAP NEON presentation](https://smap.jpl.nasa.gov/internal_resources/586)
- Dadap et al. 2019: SMAP-based surface soil moisture dataset for tropical peatlands (Sumatra, Borneo, Peninsular Malaysia); drier soil up to 30 days before fire tracked with larger burned area. — [Tropical Peatlands hub](https://www.tropicalpeatlands.org/knowledge/publication/11463_17349)
- NISAR: first public release 20 July 2026 for observations from 17 June 2026 onward (labelled PROVISIONAL in ASF docs; do not mix with BETA); earlier first-year data to be added over coming months, full record expected by end of 2026; pre-calibration L1-L3 set (Oct 2025-Jan 2026) released Feb 2026; access via Earthdata Search, ASF Vertex, asf_search; S-band samples at ISRO Bhoonidhi. — [NASA Earthdata](https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes), [ASF availability](https://nisar-docs.asf.alaska.edu/availability-overview/)

### Inferences
- Use SAR as a relative wetness/flood-under-canopy indicator calibrated per site against dipwells, not as a transferable absolute WTD model. SMAP surface moisture saturates and is biased over closed canopy; peat water table lies below the sensing depth.
- NISAR L-band (12-day repeat) should improve under-canopy flooding and InSAR coherence over peat but backlog and provisional status mean validation is needed before operational use.
- [unverified, background] Sentinel-1 GEE `COPERNICUS/S1_GRD`; OPERA DISP-S1 and RTC-S1 products via NASA Earthdata/ASF; ASCAT/SMOS/SMAP L4 (`NASA/SMAP/SPL4SMGP/008`) coarse (9-36 km).

### Gaps
- No quantitative SAR-WTD transfer functions verified for Kalimantan/Papua; no SMAP L4 water table validation in Indonesia found.
- OPERA DISP-S1 coverage over Indonesia, ASCAT, SMOS not researched; ALOS-2 PALSAR-2 data access terms (JAXA mosaic free 25 m yearly, scene data restricted) unverified.

## 4. Surface water, flooding, canals

### Takeaway
Canal mapping exists as an open regional CNN product (65% of peatlands drained) but with road/canal confusion; Sentinel-2/Sentinel-1 flood methods and JRC GSW were not verified here.

### Cited Findings
- Regional drainage canal map (AGU Advances 2021): CNN on high-res imagery, drainage in at least 65% of peatlands, drainage density varies within land use. — [DOAJ AGU Advances](https://doaj.org/article/931c5c365b2f4fa38104bcfd8735d87c), [MIT DSpace](https://dspace.mit.edu/handle/1721.1/132970)
- Haidar and Takeuchi 2022: Stanford-hosted map based on 5 m Planet basemaps, IoU 0.85 with 25 m matching tolerance, roads mislabelled as canals; follow-up with 1.5 m SPOT-6/7 from LAPAN over 660 km2 in Indragiri Hilir, Riau. — [Sciforum abstract](https://sciforum.net/paper/download/13655/abstract_pdf)
- Community canal mapping (OSM Tasking Manager) in Musi Banyuasin, South Sumatra. — [UGM thesis](https://etd.repository.ugm.ac.id/home/detail_pencarian_downloadfiles/684880)

### Inferences
- Canal geometry (width/depth, dams) is not derivable from these maps; field survey or BRGM canal-blocking records are needed for the hydraulic term.
- [unverified, background] JRC GSW (`JRC/GSW1_4/GlobalSurfaceWater`, 30 m, to 2021, monthly history `JRC/GSW1_4/MonthlyHistory`), Sentinel-2 NDWI/MNDWI, Sentinel-1 flood methods and Dynamic World are typically cloud-limited (optical) or confused by vegetation (C-band); verify.

### Gaps
- No verified accuracy for JRC GSW in forested peat swamp; no Sentinel-1 flood mapping validation in Indonesian peat; license of canal dataset unconfirmed.

## 5. Topography

### Takeaway
DEM vertical error (several metres) is comparable to or greater than peat dome relief (often 1-5 m over km), so open DEMs are inadequate for hydraulic gradients without LiDAR/GNSS correction. No peat-dome-specific validation found.

### Cited Findings
- FABDEM reduced mean absolute error in forested areas from 5.15 m to 2.88 m relative to Copernicus GLO-30; across 65 LiDAR flood-prone sites FABDEM ranked first; a 2023 comparison found FABDEM's edge over Copernicus not statistically significant. — [EGU22-8994](https://meetingorganizer.copernicus.org/EGU22/EGU22-8994.html), [FABDEM outperforms (UAEU)](https://research.uaeu.ac.ae/en/publications/the-fabdem-outperforms-the-global-dems-in-representing-bare-terra/), [IJDE Dec 2024 (DOAJ)](https://doaj.org/article/87fa65b8ab4b4f3a888fbe40764fd41a)
- Indonesia open DEMs vs GPS (2023): SRTM-1 5.529 m, DEMNAS 8.172 m, ASTER GDEM 13.632 m (FABDEM not tested). — [Geodesy and Cartography (DOAJ)](https://doaj.org/article/fe4d6f6349d648a0a17cac909fd84b3c)

### Inferences
- Vegetation-height bias in canopy-penetration-poor X/C-band DEMs over peat swamp forest means FABDEM/GLO-30 are likely biased positively; relative elevations within a KHG may still be usable after dipwell/GNSS tie-in.
- [unverified, background] GEE IDs: `COPERNICUS/DEM/GLO30`; FABDEM via Source Cooperative/Zenodo (CC BY-NC-SA 4.0, non-commercial); DEMNAS from BIG (0.27 arc-sec ~8 m, free registration, derived from IFSAR/TERRASAR-X/ALOS PALSAR); GEDI L2A/L3 (`LARSE/GEDI/GEDI02_A_002_MONTHLY`) and ICESat-2 ATL08 give sparse ground points useful for DEM correction (ICESat-2 ~ decimetre-level over bare ground).

### Gaps
- No peat-dome-specific DEM error figures; LiDAR availability by BIG/BRGM unverified.

## 6. Peat extent, depth, land cover, fire

### Takeaway
Peat depth maps are modelled with ~70 cm RMSE globally and weak on Borneo/New Guinea highlands; site-scale open-data models can reach high accuracy locally. Land cover and fire layers were not verified in this session.

### Cited Findings
- PeatDepth-ML (Biogeosciences 23:2959, 2026): blocked leave-one-out RMSE 70.1 +/- 0.9 cm, median depth 134 cm (IQR 87-187) over >30 cm peat; trained on Peat-DBase (>200,000 measurements); poorer in coastal areas and highlands incl. Borneo and New Guinea. Widyastuti et al. 2025 is another global map built from regional models. — [BG 2026 paper](https://bg.copernicus.org/articles/23/2959/2026/), [UVic record](https://dspace.library.uvic.ca/items/858185b2-1f88-49c0-86e1-21c43d8c8948)
- Rudiyanto et al. 2018 (Geoderma): 30 m peat thickness at Bengkalis Island (~50,000 ha) from SRTM, Sentinel and PALSAR with open-source ML, up to 98% variance explained, median relative error 5% (single site). — [Landsat/NASA article](https://landsat.gsfc.nasa.gov/article/open-digital-mapping-for-assessing-carbon-storage-in-tropical-peatlands)
- PRIMS (BRG/BRGM): web GIS for restoration monitoring in seven priority provinces; designed to record water level and soil water content; BRG known as BRG until 2021 then BRGM; SIPALAGA described in 2019 as a wildfire early detection system; GWL monitoring infrastructure installed per peat hydrological unit (KHG). SIMTAK not confirmed. — [Jakarta Post 2019](https://newgelora.thejakartapost.com/news/2019/06/21/indonesian-peatland-agency-develops-online-platform-to-monitor-restoration), [Jakarta Post 2023](https://www.thejakartapost.com/adv/2023/12/20/ensuring-safe-peatland.html), [NU Online](https://www.nu.or.id/lingkungan/prims-langkah-inovatif-brg-pantau-lahan-gambut-aq0eC)

### Inferences
- [unverified, background] PEATMAP (Xu et al. 2018), KLHK KHG/peat maps via Geoportal KLHK / Satu Peta, ESA WorldCover (10 m, 2020/2021, `ESA/WorldCover/v200`), Hansen GFC (`UMD/hansen/global_forest_change_2023_v1_11`, v1.12 may exist), MapBiomas Indonesia, FIRMS VIIRS/MODIS hotspots (NRT ~3 h), MCD64A1 / `ESA/CCI/FireCCI/5_1` burned area, oil palm maps (Descals et al. 2021) and acacia maps exist; none verified here. BRGM's dipwell data access policy is a likely bottleneck.

### Gaps
- No verified info on KHG map accuracy/licence, PEATMAP/Peat depth data licence, MapBiomas Indonesia, burned-area/hotspot accuracy over peat, or acacia/oil-palm map accuracy.

## 7. GRACE/GRACE-FO

### Takeaway
GRACE-based storage is too coarse for KHG-scale peat water balance; a 2026 Kalimantan basin study found it only plausibly resolves ~42% of groundwater storage change estimates even at 23,000 km2.

### Cited Findings
- Lower Kutai Basin (E. Kalimantan, 23,000 km2), HESS 30:4771 (2026): on average only 42% of delta-GWS estimates plausible from GRACE due to ocean leakage and scale mismatch; preprint: 21-60% per realization across 54 realizations, land-ocean correlation up to 0.68. — [HESS 2026](https://hess.copernicus.org/articles/30/4771/2026/), [EGUsphere preprint](https://egusphere.copernicus.org/preprints/2025/egusphere-2025-2941/egusphere-2025-2941-ATC2.pdf)
- Kalimantan basins: ML reconstruction of TWS across the ~11-month GRACE/GRACE-FO gap (test r = 0.943). Papua 2005-2024: +0.38 cm/yr groundwater storage trend with GRACE/GLDAS. — [Geoid (ITS)](https://journal.its.ac.id/index.php/geoid/article/view/2329), [Inderaja (ITS)](https://journal.its.ac.id/index.php/inderaja/article/download/9810/7996/26104)

### Inferences
- Use GRACE only as a regional closure check on the sum of P - ET - Q, not for per-KHG storage. [unverified, background] GRACE-FO status and the nominal ~300 km resolution were not confirmed.

### Gaps
- GRACE-FO 2026 operational status and next-generation (GRACE-C) not verified.

## 8. Practical platforms and access

### Takeaway
GEE, NASA Earthdata/ASF and Indonesian portals (PRIMS, Geoportal) host the key data; GEE catalog IDs are verified above for CHIRPS v3, PML_V2 and MODIS 061 ET only.

### Cited Findings
- NISAR access: Earthdata Search, ASF Vertex, ASF SearchAPI, `asf_search` Python package. — [NASA Earthdata](https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes)
- IMERG V07 via GES DISC (`GPM_3IMERGHH`, `GPM_3IMERGM`). — [GES DISC catalog](https://www.earthdata.nasa.gov/es/data/catalog/ges-disc-gpm-3imergm-07)
- PRIMS: BRG web GIS. — see Section 6 sources.

### Inferences
- [unverified, background] GEE IMERG: `NASA/GPM_L3/IMERG_V07` (30-min); Copernicus Data Space (Sentinel-1/2 archive, openEO), Planetary Computer (STAC for Sentinel, Landsat, ERA5, JRC GSW), Indonesia Satu Peta/Geoportal KLHK and BIG InaGeoportal; verify availability and licenses.

### Gaps
- Copernicus Data Space, Planetary Computer, Satu Peta/Geoportal contents not researched; BRGM data sharing terms unknown.

## Cross-cutting limitations
- Search tool returned abstracts/snippets; no ATBDs were read. Quantitative error figures exist for DEMs, peat depth, SAR-WTD (r = -0.648), SMAP forest bias, IMERG Kototabang qualitatively only.
- Several GEE catalog pages showed inconsistent end dates and deprecation flags across languages; confirm in the live catalog before specifying versions.
