# Tooling, benchmarks and operational engineering for a Python peatland water-balance package

Repo stats (stars, last push, license) were pulled via the GitHub API on 2026-10-21 and are cited as [GitHub API](https://api.github.com) lookups of the repo URL given in each line. Items I could not verify are in the Gaps sections.

## 1. Existing peat hydrology tools and code (reuse / compare / benchmark)

### Takeaway
The only open, directly comparable peat-dome plus canal-network code found is Urzainki's blopti (2020, MIT, dormant) and its 2023 successor, whose repo URL I could not confirm. PEATCLSM is a Fortran change inside NASA GEOS and is not realistically reusable as a library. The maintained general hydrology stack (MODFLOW 6 via flopy, Deltares wflow/Ribasim/iMOD/HydroMT, ParFlow) is active, but none ships a peat or canal-drainage workflow. A new package would mainly benchmark against these and reuse the data/IO layer.

### Cited Findings
**Peat-specific code**
- Urzainki et al. 2020 (Biogeosciences 17, 4769) is open: code and data are MIT-licensed, archived on Zenodo doi:10.5281/zenodo.3741043 and hosted at GitHub LukeEcomod/blopti. Model: quasi-3D Boussinesq groundwater equation, FiPy finite volume, daily step, 100 m rasters, transmissivity integrated over depth-varying K (Wosten 2008 decomposition classes), specific yield from van Genuchten curves using boreal peat values, canal pixels forced to canal water level (DEM minus 1.2 m unblocked), constant-head outer boundary, forcing = P minus ET. Study area: Siak, Riau, 931 km2 peatland. — [BG 2020](https://bg.copernicus.org/articles/17/4769/2020/)
- Same paper states the authors "did not validate the hydrological model against actual field data" because no extensive public dataset existed; parameters are from the literature. — [BG 2020](https://bg.copernicus.org/articles/17/4769/2020/)
- blopti repo: 2 stars, MIT, last push 2020-09-24, i.e. dormant. — [LukeEcomod/blopti](https://github.com/LukeEcomod/blopti)
- Urzainki et al. 2023 (Biogeosciences 20, 2099) is a coupled model: a canal network module (diffusive-wave open-channel flow, Manning friction, block discharge relation) and a peat hydrological module (2D groundwater flow, specific yield, piecewise transmissivity, explicit finite volume on an unstructured triangular mesh), alternating each time step. Inputs: 100 m DEM and peat depth (interpolated to 50 m), canal vector topology, daily P-ET. Study area 22,000 ha in Sumatra, 168 dams, 219 km canals. Validation: qualitative comparison against 141 dipwells in 2020, "unbiased" with comparable range, at 100 m resolution. The page lists a "Model code and software" credit for "Hydrology model and open data"; I did not retrieve a repo URL. — [BG 2023](https://bg.copernicus.org/articles/20/2099/2023/)
- Group's other repos (LukeEcomod org, Univ. Helsinki/Luke): SpaFHy-Peat (forest hydrology model for drained peatlands, MIT, 1 star, last push 2026-01-15) and pyAPES_main (pushed 2026-10-21) are active but boreal-focused. — [SpaFHy-Peat](https://github.com/LukeEcomod/SpaFHy-Peat), [LukeEcomod](https://github.com/LukeEcomod)
- PEAT-CLSM (Bechtold et al.) replaces the TOPMODEL-based CLSM hydrology in NASA GEOS with a peatland-specific treatment; the tropical extension is Apers et al. 2022 (JAMES 14, doi 10.1029/2021MS002784, CC BY 4.0), evaluated at 96 water-level sites (39 natural: 5 Central/South America, 4 Congo, 30 SE Asia; 57 drained, all SE Asia) and 3 eddy-covariance ET sites (PE-QFR in Peru plus undrained and drained Indonesian peat swamp forest from Hirano et al. 2015), forced by hourly MERRA-2 with gauge-corrected precipitation. The authors note MERRA-2 tropical precipitation is error-prone. — [Apers 2022 PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9285420/)
- PEATCLSM code on GitHub: mbechtold/PEATCLSM_T, "Peatland hydrology changes to catchment.F90 of the GEOS-ESM land model component", 0 stars, last push 2023-09-06, no license listed. It is a patch to a Fortran model, not a package. — [mbechtold/PEATCLSM_T](https://github.com/mbechtold/PEATCLSM_T)
- Michiel-Lamens/OPTRAM-PEATCLSM-calibration (0 stars, no license, pushed 2026-10-07) holds code for a paper on using process-based simulations (PEATCLSM) as hydrological reference for calibrating an optical water-table proxy. Useful as a pattern; not verified as peer-reviewed. — [repo](https://github.com/Michiel-Lamens/OPTRAM-PEATCLSM-calibration)
- OPTRAM tropical evaluation (Koupaei-Abyazani et al. 2024, JGR Biogeosciences, DOI 10.1029/2024JG008116 as reported by search): in situ WTD from Indonesia, Malaysia, Peru vs 30 m Landsat OPTRAM; correlation about 0.7 to 1 in sparse/non-forest, little or none under dense vegetation. — [SSEC pub page](https://pubs.ssec.wisc.edu/pub/view/15698), [CIFOR](https://cifor-icraf.org/knowledge/publication/9219)
- Existing ML WTD model: Indonesian peatland groundwater-level prediction (STOTEN 2022, Central Kalimantan peat dome, 2010-12): gradient boosting beat random forest and multilinear regression near canals; elevation and precipitation strongest predictors. Deep-learning WTD paper used BRGM sensors at 15 stations 2018-2021. No code link found for either. — [ASEAN Haze Portal summary](https://hazeportal.asean.org/?p=13613), [Horizon repository](https://repository.horizon.ac.id/items/show/9149)
- ToFEWSI (peat fire early warning): ecosys eco-hydrology model supplied WTD/soil moisture to an ANN fire forecast; weather+hydrology gave R2 about 0.8 and MAE about 40 per two weeks vs R2 about 0.4 and MAE about 100 for weather only (two-week fire counts). Inputs CHIRPS + ERA5 in spin-up. Code: jinyun1tang/ECOSYS (77 stars, BSD-3, pushed 2026-03-06) and 4SAnalyticsnModelling/TOFEWSI-ECOSYS-ANN (1 star, MIT, last push 2022-04-27); small tadasnik/tofewsi repo (2020). — [Nature Sci Rep paper on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9837124/), [ECOSYS](https://github.com/jinyun1tang/ECOSYS), [TOFEWSI-ECOSYS-ANN](https://github.com/4SAnalyticsnModelling/TOFEWSI-ECOSYS-ANN)
- GitHub repo searches for "peatland water table", "peat water table depth", "peatland hydrology model", "peat canal blocking", "peatland drainage groundwater" returned no relevant repos at all (only the PEATCLSM and OPTRAM hits above), i.e. no widely used open tropical peat WTD package appears to exist. — GitHub search via `gh search repos` on 2026-10-21

**DRAINMOD**
- DRAINMOD (NC State, field-scale drained-soil water balance): only small repos found; drainmod/drainmod-releases (1 star, pushed 2026-03-19) appears to be a release channel, not source. Other hits are unrelated or personal. — [drainmod/drainmod-releases](https://github.com/drainmod/drainmod-releases)

**General hydrogeology / hydrology engines (suitability for peat dome + canals)**
- flopy (MODFLOW 6 Python interface): 640 stars, last push 2026-10-19, release 3.11.0. Peat-dome 2D unconfined flow with drains/river (DRN/RIV/SFR/MAW) packages is a standard MODFLOW setup; SFR can represent a canal network with stage routing; blocks as weirs need custom treatment. Peat-specific nonlinear transmissivity (K decreasing with depth) is reproducible via layering or variable K. — [modflowpy/flopy](https://github.com/modflowpy/flopy)
- Deltares Ribasim (water-resource allocation/network): 62 stars, MIT, pushed 2026-10-21, release v2026.1.2. Node-link network model; suited to canal network storage/routing, not 2D groundwater. — [Deltares/Ribasim](https://github.com/Deltares/Ribasim)
- Deltares iMOD Python: 41 stars, MIT, pushed 2026-10-21; xarray-based pre/post-processing and MODFLOW 6 coupling (iMOD WQ). — [Deltares/imod-python](https://github.com/Deltares/imod-python)
- Deltares wflow (Wflow.jl): 166 stars, MIT, pushed 2026-10-20; HydroMT (125 stars, MIT) and hydromt_wflow (33 stars, GPL-3.0) for data-driven model setup. Conceptual distributed catchment model with kinematic/local-inertial routing; lacks a dedicated peat dome groundwater with canal-head boundary. — [Wflow.jl](https://github.com/Deltares/Wflow.jl), [HydroMT](https://github.com/Deltares/hydromt), [hydromt_wflow](https://github.com/Deltares/hydromt_wflow)
- ParFlow: 216 stars, last push 2026-10-16, license listed NOASSERTION. Integrated variably-saturated surface/subsurface 3D with overland flow; heavy and HPC-oriented, overkill for operational peat dome WTD. — [ParFlow/parflow](https://github.com/ParFlow/parflow)
- ECMWF earthkit-hydro (34 stars, Apache-2.0, pushed 2026-10-15) for river-network operations on gridded data. — [ecmwf/earthkit-hydro](https://github.com/ecmwf/earthkit-hydro)

### Inferences
- Defensible benchmark ladder: (a) reimplement or call blopti's Boussinesq core (MIT permits reuse) as the process-based baseline; (b) a MODFLOW 6 via flopy twin of the same domain as a numerical cross-check; (c) PEATCLSM published outputs or Apers 2022 site statistics as a global-model comparator; (d) ML baselines (gradient boosting on elevation and rainfall) since published ML work reports that those predictors dominate.
- Because blopti was never validated and the 2023 paper validated only qualitatively, a package that publishes quantitative dipwell skill scores would itself be a contribution.
- Wflow/Ribasim are better as complementary catchment/canal-routing components than as a peat WTD engine.

### Gaps
- Could not find the repository URL for the Urzainki 2023 model (end matter was truncated in my fetch); check the "Code and data availability" section at https://bg.copernicus.org/articles/20/2099/2023/.
- No confirmed code/data availability statement for Apers 2022 (fetch truncated). The Zenodo or Dataverse record for PEATCLSM tropical code is unverified.
- 'Peat Hydrology Tool', 'Peatland Water Management Tool', 'Peatland-ES-UK' were not located in searches; I did not verify whether they exist as open software. SESAME is a BRGM sensor-station network (not a model), see Section 3.
- Wflow.jl/Ribasim peat-specific use cases and flopy peat examples were not searched; suitability statements above are my judgement.
- ParFlow, flopy license strings returned as NOASSERTION by the API (likely custom/CC0-type text); check before reuse.

## 2. Benchmark and test datasets (open licenses)

### Takeaway
Open, citable dipwell time series for tropical peat are thin: the best leads are a Zenodo-style Indonesian groundwater dataset (8 stations, Batanghari and Kubu Raya), the 96-site water level collection compiled for Apers 2022, and BRGM's SESAME/SIPALAGA sensors (access terms unclear). Rainfall and flux benchmarks are easier (IMERG, CHIRPS, AmeriFlux PE-QFR).

### Cited Findings
- Daily groundwater depth for peatlands in Indonesia from 8 in-situ stations in two regions (Batanghari, Sumatra; Kubu Raya, Kalimantan), agricultural peatlands, linked to the drought-fire work of Taufik et al. 2022; DOI and license not shown in what I retrieved. — [ASEAN Haze Portal](https://hazeportal.asean.org/?p=12602) (page redirected on fetch, content from search snippet only)
- Apers 2022 compiled 96 water-level sites and three eddy-covariance ET sites (AmeriFlux PE-QFR; Hirano et al. 2015 Indonesian drained and undrained peat swamp forest). — [Apers 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9285420/)
- BRGM SIPALAGA: Peatland Ground Water Monitoring System of automatic sensors, 142 GWL monitoring units in 7 fire-prone provinces in 2020; studies say data use is not yet optimal. PRIMS (Peatland Restoration Information Management System) covers six provinces. SESAME stations record temperature, rainfall, groundwater level and soil moisture; one study used 42 BRG SESAME stations with Sentinel-1. — [IPB journal](https://journal.ipb.ac.id/index.php/jsilvik/article/download/55265/28060), [Jakarta Post](https://newgelora.thejakartapost.com/news/2019/06/21/indonesian-peatland-agency-develops-online-platform-to-monitor-restoration)
- 141 dipwells (2020) and six patrol-post weather stations were used for the 2023 Urzainki check in Sumatra (data availability not confirmed). — [BG 2023](https://bg.copernicus.org/articles/20/2099/2023/)
- Sebangau, Kalimantan: Putra, Holden and Baird 2021 (automated and manual dipwells, three sites); Sulaiman et al. report 27 years of GWL in Central Kalimantan peat forests. Public data availability not confirmed. — [Haze portal result](https://hazeportal.asean.org/?p=12602) (listing only)
- Rainfall: IMERG Early, Late, Final latency about 4 h, 14 h, 3.5 months; Early and Late use climatological gauge adjustment, Final uses monthly gauge analysis. — [NASA IMERG docs](https://gpm.nasa.gov/taxonomy/term/1417), [NTRS](https://ntrs.nasa.gov/api/citations/20190028284/downloads/20190028284.pdf)
- Other candidate benchmarks mentioned in sources: CHIRPS (used by ToFEWSI), MERRA-2 with gauge-corrected precipitation (Apers).
- Harmonized peatland dataset for Indonesia v0.1 (IIASA): peat extent/depth style base layer. — [IIASA PURE](https://pure.iiasa.ac.at/18393)

### Inferences
- A pragmatic test suite: Taufik 8-station set (daily WTD, drained agricultural peat) for calibration/validation; Apers 96-site list for cross-site generalization; AmeriFlux PE-QFR for ET sanity; IMERG vs station rainfall for the bias-correction module.
- Use blopti's synthetic Siak setup as a deterministic regression test (no field data needed).

### Gaps
- No verified license for any WTD dataset above; Zenodo/DOI for the 8-station set not obtained.
- FLUXNET/ICOS/AmeriFlux Indonesian site availability (e.g. Hirano's Palangka Raya towers) not verified; Hirano data are possibly request-based.
- Canal water level time series: no open dataset found.
- No open BRGM/SIPALAGA download terms found; likely needs agreement.

## 3. Operational pipeline engineering

### Takeaway
All needed building blocks are active, permissively licensed Python packages. Specifically, ingestion goes through earthengine-api/Xee, odc-stac, earthaccess, ecmwf-opendata or cdsapi. Storage and IO use xarray, rioxarray, Zarr and COG. Orchestration is Prefect or Airflow, or a GitHub Actions cron. Versioning uses DVC or Icechunk. Operational precedents (GloFAS, SiPongi, ToFEWSI/FRS) show the need for ensembles, skill-score reporting and openly published reforecasts.

### Cited Findings
**Ingestion and data-access libraries (stars; last push; license)**
- earthengine-api: 3462; 2026-10-20; Apache-2.0 — [google/earthengine-api](https://github.com/google/earthengine-api); Xee (xarray backend for GEE): 376; 2026-10-07; Apache-2.0 — [google/Xee](https://github.com/google/Xee)
- odc-stac: 205; 2026-10-07; Apache-2.0 — [opendatacube/odc-stac](https://github.com/opendatacube/odc-stac); pystac-client: 209; 2026-10-20 — [stac-utils/pystac-client](https://github.com/stac-utils/pystac-client); stackstac: 272; last push 2024-08-10; MIT, i.e. effectively unmaintained, prefer odc-stac — [gjoseph92/stackstac](https://github.com/gjoseph92/stackstac)
- earthaccess (NASA CMR/Earthdata): 645; 2026-10-20; MIT — [nsidc/earthaccess](https://github.com/nsidc/earthaccess); harmony-py: 71; 2026-10-06 — [nasa/harmony-py](https://github.com/nasa/harmony-py)
- openEO Python client: 219; 2026-10-20; Apache-2.0 (org Open-EO) — [Open-EO/openeo-python-client](https://github.com/Open-EO/openeo-python-client); openeo-python-driver 12 stars; 2026-10-17
- ECMWF: ecmwf-opendata 340; 2026-10-16; Apache-2.0 — [ecmwf/ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata); cdsapi 322; last push 2026-03-12 — [ecmwf/cdsapi](https://github.com/ecmwf/cdsapi); earthkit-data 122; 2026-10-15 — [ecmwf/earthkit-data](https://github.com/ecmwf/earthkit-data); climetlab (deprecated in practice, last push 2024-11-13) — [ecmwf/climetlab](https://github.com/ecmwf/climetlab); anemoi-core 167; 2026-10-21 (ML forecast framework)
- BMKG wrapper PyBMKG (MIT) exists, see [PyPI](https://pypi.org/project/PyBMKG)

**Array, format and serving stack**
- xarray 4212; 2026-10-21 — [pydata/xarray](https://github.com/pydata/xarray); rioxarray 626; 2026-10-19 — [corteva/rioxarray](https://github.com/corteva/rioxarray); rasterio 2583; zarr-python 2077 (MIT) — [zarr-developers/zarr-python](https://github.com/zarr-developers/zarr-python); Icechunk (transactional Zarr store, 693 stars, Apache-2.0, 2026-10-21) — [earth-mover/icechunk](https://github.com/earth-mover/icechunk); kerchunk 367; 2026-09-15; flox 137; xESMF 252; dask 13935; distributed 1696
- rio-cogeo 394; 2026-10-21; BSD-3 — [cogeotiff/rio-cogeo](https://github.com/cogeotiff/rio-cogeo); TiTiler 1194; 2026-10-20; MIT (dynamic tiles for web maps) — [developmentseed/titiler](https://github.com/developmentseed/titiler); stac-fastapi 324; 2026-10-21; STAC spec 935; 2026-10-10 — [radiantearth/stac-spec](https://github.com/radiantearth/stac-spec); pangeo-forge-recipes 134
- Planetary Computer examples (STAC patterns): 460; 2026-09-24 — [microsoft/PlanetaryComputerExamples](https://github.com/microsoft/PlanetaryComputerExamples)

**Orchestration, reproducibility, QA**
- Prefect 24052; 2026-10-21; Apache-2.0 — [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect); Apache Airflow 47240; 2026-10-21 — [apache/airflow](https://github.com/apache/airflow); ecFlow (ECMWF workflow) 65 — [ecmwf/ecflow](https://github.com/ecmwf/ecflow)
- DVC 15934; 2026-10-19 — [iterative/dvc](https://github.com/iterative/dvc); DataLad 668 — [datalad/datalad](https://github.com/datalad/datalad); Great Expectations 11889 (data validation)
- GitHub Actions cron is an option for small daily jobs (my engineering judgement; no source retrieved).

**Operational precedents**
- GloFAS: ensemble forecasts with H-TESSEL + LISFLOOD forced by ECMWF IFS; 2023 skill assessment shows beating persistence in over 93% of catchments at short/medium range, skill vs climatology in over 80% of catchments at 16-30 days, but no or negative skill at long lead in tropical Africa, western South America coast, snow-dominated catchments; a headline skill score is published as a map layer; real-time forecasts and 20-year reforecasts are openly available via the C3S CDS. A reviewer notes GloFAS does not treat hydrological uncertainty so ensembles may be overconfident at short lead times. — [HESS 2023](https://hess.copernicus.org/articles/27/1/2023/)
- Indonesian systems: SiPongi (KLHK) updates hotspots in near-real time from Terra/Aqua, SNPP, NOAA-20; a 2021 "Sipongi+" stage lists weather forecast, peat water level and LFC (slide only, unconfirmed). Fire Risk System (FRS; Columbia University with IPB) provides seasonal provincial/district fire warnings for Central Kalimantan and Riau, with a 2025-era F1000Research evaluation vs hotspot counts. ToFEWSI aimed at a web tool predicting peat fire risk up to three months ahead. — [Israr slides, UMD](https://gslcluc1.umd.edu/sites/default/files/Israr_D3_Session%20I.pdf), [F1000Research](https://f1000research.com/articles/15-1154), [Manchester ToFEWSI](https://research.manchester.ac.uk/en/projects/towards-a-fire-early-warning-systm-for-indonesia-tofewsi/)
- Global Water Watch (Deltares): GitHub org global-water-watch has global-water-watch-website (4 stars, pushed 2026-10-18) and gww-api (3 stars, last push 2023-03-30); no main pipeline repo found. — [website repo](https://github.com/global-water-watch/global-water-watch-website), [gww-api](https://github.com/global-water-watch/gww-api)
- Delft-FEWS: no public GitHub repo found at Deltares/Delft-FEWS (404); distributed via Deltares.

### Inferences
- Recommended design: config-driven (YAML/pydantic) pipeline; ingest into versioned Zarr (Icechunk) and publish COG + STAC for maps; Prefect or Airflow in production, GitHub Actions only for small demos; containerized; provenance via run metadata plus DVC. This is a synthesis of the tooling above, not a cited best practice.
- Rainfall: Early IMERG for nowcast, replaced by Final plus gauge calibration through a hindcast cycle; gauge bias correction should be evaluated on held-out stations with CRPS/bias metrics, and Early/Final differences documented because Early only carries climatological gauge adjustment.
- Gap-filling: Sentinel-1 SAR for cloud-affected optical (OPTRAM works mostly in sparse vegetation), with uncertainty flags.
- Verification: follow GloFAS pattern: reforecast/hindcast archive, skill vs persistence and climatology benchmarks, a headline skill score on the dashboard, and be explicit where there is no skill. Ensemble spread should include hydrological parameter uncertainty (GloFAS critique).
- Bulletins in Indonesian can be templated (Jinja) from the same dataset; align with SiPongi/BRGM PRIMS outputs rather than compete.

### Gaps
- Prefect/Airflow vs Actions tradeoffs, CF-convention tooling (cf-xarray), gap-filling algorithms for SAR/optical and gauge-bias methods (e.g. quantile mapping, geostatistical merging) were not searched; no sources retrieved.
- SEAS5 open-data licence and availability (ECMWF open data covers some IFS products; whether SEAS5 hindcasts are free for operational use) not verified; CDS C3S seasonal terms should be checked. CHIRPS-GEFS also not verified.
- Whether SiPongi+ really publishes peat water level and how (API?) is unconfirmed.

## 4. Standards and Indonesian data policy

### Takeaway
Use CF-compliant NetCDF/Zarr, COG and STAC for FAIR outputs. Indonesian operational use must respect BMKG's terms (machine access via official API with PTSP agreement, possible PNBP fees, scraping prohibited) and align with Kebijakan Satu Peta (Perpres 9/2016, amended by Perpres 23/2021) and BIG's geoportal.

### Cited Findings
- BMKG terms (updated 2026-03-02): automated system-to-system retrieval must use the official API and web scraping/robots are not permitted; users needing API access, integration or cooperation contact BMKG's PTSP; use is subject to PNBP rules; BMKG cartographic products, infographics and education materials are BMKG intellectual property; no CC license found; PyBMKG-type wrappers are MIT but cover code only. A Dart wrapper notes attribution to BMKG is required. — [BMKG Ketentuan Penggunaan](https://www.bmkg.go.id/ketentuan-penggunaan), [PPSDM BMKG](https://ppsdm.bmkg.go.id/term-of-use)
- Kebijakan Satu Peta (One Map Policy): Perpres 9/2016, amended by Perpres 23/2021 (151 thematic maps target); principle one reference, one standard, one database, one geoportal at 1:50,000. Integrated thematic maps at portalksp.ina-sdi.or.id; Keppres 20/2018 gave data-sharing access to government officials; Geoportal KSP 2.0 launched July 2024, reportedly open to civil society too. BIG is the data steward; 2019 reports 84 of 85 themes compiled from 19 ministries and 24 provinces. — [CNBC Indonesia on KSP](https://www.cnbcindonesia.com/news/20181211130308-4-45849/kebijakan-satu-peta-a-la-jokowi-begini-penjelasan-lengkapnya), [Kemhan on Geoportal 2.0](https://www.kemhan.go.id/2024/07/19/menhan-prabowo-wakili-presiden-jokowi-di-peluncuran-geoportal-kebijakan-satu-peta-2-0-dan-white-paper-opm-beyond-2024.html), [Mongabay Indonesia](https://mongabay.co.id/2020/02/27/kebijakan-satu-peta-masih-abaikan-peta-kelola-rakyat/)
- GloFAS publishes forecasts and reforecasts through the C3S CDS (open access precedent). — [HESS 2023](https://hess.copernicus.org/articles/27/1/2023/)
- STAC spec (Apache-2.0) and COG/Zarr tooling are active (see Section 3).

### Inferences
- Treat BMKG rainfall as a gated input: pipeline should keep a pluggable gauge source, store only derived/bias-corrected products if redistribution is restricted, and carry attribution metadata.
- Publish outputs as STAC items with CF attributes and a clear license (CC BY 4.0 where inputs allow) to meet FAIR; link peat extent/depth inputs to the Satu Peta/BIG layers.

### Gaps
- FAIR principles, CF conventions version, and Zarr v3/GeoZarr status were not researched here; no sources retrieved.
- BIG's formal data-sharing/licensing rules (e.g. Ina-Geoportal terms, Perpres 27/2014 on JIGN) were not retrieved.
- Whether BRGM/KLHK peat data may be redistributed is unknown; PNBP fee amounts for BMKG data not found.
