# Satellite retrieval of WTD, peat soil moisture and surface motion in tropical peatlands, and in-situ calibration/validation data

Note on search depth: about 20 tool calls, mostly web-search summaries plus a handful of page fetches. Several entries below come from search-engine summaries of abstracts or repository pages, not full-text reads. Those are flagged "abstract-level". Nothing here was verified against full-text results tables unless stated.

## 1. Published methods and accuracy for WTD / soil moisture from open satellite data (S1, L-band, SMAP, optical, ML)

### Takeaway
Direct, validated satellite WTD retrieval for tropical peat is thin. The best-documented results are modest. Sentinel-1 VV backscatter against WTD gave only r = -0.65 at one Riau site. OPTRAM gives r of 0.7-1 (best-pixel) only in open or low-NDVI peat and fails (mean r -0.04 to 0.24) under higher-NDVI cover. I found no peer-reviewed RMSE-in-cm for an operational S1, ALOS-2, SMAP, TVDI or ML-fusion WTD product over Indonesian peat.

### Cited Findings
- OPTRAM (SWIR transformed reflectance vs NDVI trapezoid, Landsat 7/8 at 30 m) tested against in-situ WTD in Indonesia, Malaysia and Peru. Best-pixel R was 0.7-1 in low-to-intermediate NDVI areas. In higher-NDVI (forested) areas mean R was -0.04 to 0.24. Authors say trees are less sensitive to WTD fluctuations. Koupaei-Abyazani et al. 2024, JGR Biogeosciences 129 — [DOI 10.1029/2024JG008116](https://doi.org/10.1029/2024JG008116) ([abstract page](https://pubs.ssec.wisc.edu/pub/view/15698)). Abstract-level; no RMSE reported in the abstract. "Best pixel" selection uses the pixel with highest Pearson R, so it is optimistic and not an independent validation.
- Sentinel-1 backscatter, Riau (Rokan River area, Acacia plantations): VV sigma0 (dB) had the highest correlation with Sipalaga-measured groundwater level, r = -0.648 (moderate). Linear model Y = -101.629 - 7.414x. Yananto et al. 2022, Int. J. Remote Sensing and Earth Sciences 18(2):203-216 — [DOI 10.30536/j.ijreses.2021.v18.a3618](https://doi.org/10.30536/j.ijreses.2021.v18.a3618) ([source page](https://www.tropicalpeatlands.org/knowledge/publication/11463-24980)). No RMSE or R2 given in the summary I saw. Implied R2 is about 0.42 (r squared, my arithmetic).
- Airborne LiDAR (not open satellite) for canal water table depth: validated against 145 field measurements in eastern Sumatra and West Kalimantan; accurate within 0.25 m for 86% and within 0.5 m for 99%; R2 = 0.74. Vernimmen et al. 2020, Water 12(5):1486 — [DOI 10.3390/w12051486](https://doi.org/10.3390/w12051486). Useful as an upper-bound reference for canal-water-level mapping, not a satellite method.
- SMAP-based peat soil moisture: a first remotely sensed soil-moisture dataset for Sumatra, Borneo and Peninsular Malaysia from a new SMAP retrieval algorithm; drier soil in the 30 days before fire associated with larger burned area — [CIFOR/GPC record](https://www.tropicalpeatlands.org/knowledge/publication/11463-17349) (abstract-level; author/DOI not captured).
- SMAP soil moisture bias-corrected with 12 BRG (Peatland Restoration Agency) stations, MT-DCA algorithm — [Kyoto Univ DPRI paper](https://www.dpri.kyoto-u.ac.jp/hapyo/22/pdf/C206.pdf) (conference-level; metrics not captured).
- ecosys-modelled (not satellite-retrieved) soil moisture and WTD improved neural-network two-weekly fire forecasts for tropical peat and non-peat — Mezbahuddin et al. 2023, Sci. Rep. — [PMC9837124](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9837124/), DOI 10.1038/s41598-022-27075-0.
- PALSAR-2 L-band: Widodo et al. 2019 converted PALSAR-2 land deformation to water table depth using Wosten models, in Central Kalimantan; depth beyond 40 cm treated as degraded/fire-prone; paper reports 88% precision for fire association vs 5% for the installed WTD network — [Geosciences 9(11):484](https://www.mdpi.com/2076-3263/9/11/484). Abstract-level; the 88% vs 5% figures come from a search summary and need checking against the paper.
- L-band backscatter vs groundwater: Hoekman et al. (SarVision) described planned work relating PALSAR-1/2 backscatter, canopy cover, soil moisture and gauge data — [JAXA K&C report](https://www.eorc.jaxa.jp/ALOS/jp/activity/kyoto/pdf/1-11_PKC1_DirkHoekman.pdf). Project plan; no coefficients seen.
- Izumi et al. 2019 (ALOS-2 full-pol soil moisture over Indonesian peat) exists per the reference list of [Geosciences 9(11):484](https://www.mdpi.com/2076-3263/9/11/484). Results not retrieved.

### Inferences
- A defensible expectation for S1-only WTD over peat is moderate skill (r about 0.5-0.7) at single sites, and worse over closed canopy. Do not promise cm-level RMSE from open optical or C-band data alone.
- OPTRAM-type indices are most credible for open, degraded or plantation peat. Canopy dominates over forested peat, so forest WTD likely needs model or InSAR/L-band constraint.
- Reported correlations are mostly site-specific, calibrated and validated in-sample. Transferability is unproven in what I found.

### Gaps
- No found study with RMSE (cm) or R2 for TVDI, NDWI/SWIR, LST-based or ML-fusion WTD over Sumatra/Kalimantan/Malaysia. Searches returned none; may exist but not surfaced.
- No cross-site transfer (leave-one-site-out) results found for S1 or L-band WTD models.
- SMAP-vs-WTD direct validation not found.
- Full texts for Yananto 2022 (RMSE), Widodo 2019 and Izumi 2019 not read.

## 2. InSAR / peat surface oscillation as WTD and subsidence proxy; NISAR availability

### Takeaway
InSAR is validated mostly for long-term subsidence rates (RMSE about 1-2 cm/yr at Bengkalis; under 5 mm/yr at ALOS-2 vs peat-camera sites per an abstract), and L-band beats C-band. Using seasonal oscillation as a WTD proxy is still proof-of-concept, with C-band coherence a major limit. NISAR L-band data became public from July 2026.

### Cited Findings
- Hoyt et al. 2020 (Nature Geoscience): ALOS L-band InSAR, 2007-2011 data, about 90 m resolution, about 2.7 Mha of Southeast Asian peat; over 90% of area subsiding, almost an inch (about 2.5 cm) per year on average (press paraphrase) — [DOI 10.1038/s41561-020-0575-4](https://doi.org/10.1038/s41561-020-0575-4); [press summary](https://www.sciencedaily.com/releases/2020/06/200604111645.htm). This is a subsidence study, not a WTD retrieval, and used ALOS-1 not ALOS-2. A NERC paper notes that slowing of subsidence seen from satellites has not been confirmed by long-term ground observations — [NORA](https://nora.nerc.ac.uk/id/eprint/533790/1/N533790JA.pdf).
- Umarhadi et al. 2021, Land Degrad. Dev. 32(16):4779-4794, Bengkalis Island: S1 and PALSAR-2 SBAS 2018-2019; mean vertical velocity -1.41 cm/yr (S1) and -2.65 cm/yr (PALSAR-2); RMSE 1.383 cm/yr (PALSAR-2) and 1.988 cm/yr (S1) against groundwater-derived reference displacement; S1 underestimated subsidence by 0.96 cm/yr — [DOI 10.1002/ldr.4061](https://doi.org/10.1002/ldr.4061) ([record](https://ir.lib.ugm.ac.id/id/eprint/5549)).
- Central Kalimantan 2017-2022 C-band SBAS: retrieved displacement for 34.4-59.8% of tested peat area (391-826 km2); coherence is lost when water floods above the ground in the wet season; correlation of SBAS displacement with in-situ peat surface and GWL is higher in the dry season than in wet season or full year (no numeric values on the page); GWL can vary from +1 m to -2 m — "Tropical peatland hydrological dynamics affect the efficacy of C-band SBAS InSAR approaches", ScienceDirect PII S0034425725004134 (Remote Sensing of Environment per PII prefix, my inference) — [UGM news page](https://fkt.ugm.ac.id/2025/11/07/tropical-peatland-hydrological-dynamics-affect-the-efficacy-of-c-band-small-baseline-subset-insar-approaches/). Authors and DOI not captured; secondary source.
- APSIS-InSAR, North Selangor, Malaysia: 1,520 interferograms from 128 image combinations, 10 Oct 2014-29 Apr 2020, about 20 m resolution; C-band partly penetrates canopy, intermittently; no ground validation, no WTD comparison; seasonal oscillations of 10-20 cm (cited from other work) exceed the 5.6 cm wavelength so fringe ambiguity may cause underestimation — Ledger et al. 2024, PLoS ONE 19(2):e0298939 — [DOI 10.1371/journal.pone.0298939](https://doi.org/10.1371/journal.pone.0298939).
- Izumi et al. (Sentinel-1A, 3 years, Indonesia, temporal-subset SBAS) improved number of coherent scatterers; no groundwater validation in readable text — [Remote Sensing 14(23):5825](https://wtlab.iis.u-tokyo.ac.jp/wataru/publication/pdf/remotesensing-14-05825-v3.pdf) (DOI not captured).
- Sentinel-1 D-InSAR, South Sumatra: subsidence 28-80 cm/yr early after drainage falling to 16-48 cm/yr for used peatland — [Frontiers Env. Sci. 2023, DOI 10.3389/fenvs.2023.1088923](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2023.1088923/text) (as summarised by search; verify).
- EGU 2025 abstract: InSAR consistent with long-term ground-truth peat motion at Central Kalimantan sites with mean RMSE below 5 mm/yr, using ALOS-2 and peat cameras — [EGU25-8505](https://meetingorganizer.copernicus.org/EGU25/EGU25-8505.html). Conference abstract only.
- Temperate comparison: Sentinel-1 coherence recovery in autumn after dry summer tracks WT dynamics in an Estonian bog — [Tampuu et al.](https://acris.aalto.fi/ws/portalfiles/portal/43528722/Tampuu_Long_term_interferometric_rs.pdf).
- NISAR: initial public L-band release began 20 July 2026 (data acquired on or after 17 June 2026); first-year science-operations data being added over coming months, full science record expected by end of 2026; a pre-calibration global dataset (17 Oct 2025-20 Jan 2026) was released Feb 2026; access via ASF DAAC / Earthdata Search / Vertex / asf_search — [NASA Earthdata](https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes); [ASF](https://asf.alaska.edu/notices/nisar-l-band-data-now-publicly-available/); [availability overview](https://nisar-docs.asf.alaska.edu/availability-overview/). No peatland-specific NISAR product or study found.

### Inferences
- The brief's "Hoyt 2020 oscillation" framing does not match the paper: Hoyt reports subsidence rates, not oscillation-based WTD. I did not retrieve Cobb's own oscillation papers.
- For dry-season windows, L-band (ALOS-2, NISAR) is the better bet for phase continuity over peat, given Umarhadi's RMSE ranking and the C-band flooding-decorrelation finding. NISAR's year-one archive should allow first operational tests in late 2026-2027.
- Subsidence velocities in cm/yr are validated to about 1-2 cm/yr; converting oscillation to WTD would need a peat-specific specific-yield/compression relation, adding uncertainty.

### Gaps
- Cobb et al. oscillation-WTD papers and Sentinel-1 oscillation validation numbers not retrieved.
- Authors/DOI for the 2025 RSE paper not confirmed.
- Umarhadi's separate Central Kalimantan work not confirmed.
- NISAR peat-specific performance unknown.

## 3. Data assimilation of satellite observations into peat hydrological models

### Takeaway
The most developed approach is PEATCLSM (tropical variants) assimilating SMOS/SMAP L-band brightness temperature in the NASA Catchment/SMAP L4 framework. Only the Congo evaluation gave numbers I found, with modest correlation gain. I found no Indonesia-specific operational assimilation study.

### Cited Findings
- PEATCLSM-Trop (natural, "Trop,Nat") assimilating SMOS L-band Tb: in Cuvette Centrale (Congo), assimilation improved water level at 4 evaluation sites, mean correlation 0.46 to 0.63; unmodelled lateral inflow from upstream mineral areas flagged. Parameters were built on Southeast Asian peat data — [EGU22-7430](https://meetingorganizer.copernicus.org/EGU22/EGU22-7430.html) (conference abstract; Apers et al. 2022 JAMES is the primary reference, not read).
- A PhD project aims to add tropical peatland hydrology including anthropogenic drainage and radiative-transfer corrections for open water and dense vegetation into SMAP L4-type assimilation — [project page](https://www.researchportal.be/en/project/advancing-land-surface-modeling-and-satellite-data-assimilation-over-tropical-peatlands).
- Northern predecessor used a spatially distributed ensemble Kalman filter updating soil moisture and WTD — same sources.

### Inferences
- Drainage (canals) is the missing process for Indonesia; natural-peat PEATCLSM will likely be biased for drained landscapes unless canal water level is imposed.

### Gaps
- No Indonesia/Malaysia assimilation validation with numbers; no assimilation of InSAR motion into peat hydrology models found.

## 4. In-situ networks and open datasets

### Takeaway
Data exist but are fragmented. Open, citable logger datasets are few and small (8 stations; Brunei; Sebangau). The national telemetry network (SIPALAGA) is large but has gaps and reliability problems, and open-access terms are unconfirmed.

### Cited Findings
- SIPALAGA (BRGM/BRG telemetry web platform): a 2019-2021 study used its water-level telemetry; hourly availability 76-93%; 17% of records had missing values — [CIFOR/GPC publication 11463-17530](https://www.tropicalpeatlands.org/knowledge/publication/11463-17530). Note: the search tool misread BRGM as the French geological survey. In the Indonesian context it is Badan Restorasi Gambut dan Mangrove (formerly BRG); that is my correction, not from the source.
- PRIMS (BRG's Peatland Restoration Information Management System): tracks restoration planning/implementation and hotspots; no water-level station info in the source — [Jakarta Post 2019](https://newgelora.thejakartapost.com/news/2019/06/21/indonesian-peatland-agency-develops-online-platform-to-monitor-restoration).
- SESAME-II telemetry: demand estimate over 14,000 measurement spots (demand, not installed); many installed systems not operating properly — [Japanese ODA document](https://www.mofa.go.jp/mofaj/gaiko/oda/seisaku/kanmin/chusho_h25/pdfs/5a08-2.pdf) (summary-level).
- BRIN reportedly developing its own groundwater-level system for peat fire early warning (no station counts) — [RRI](https://rri.co.id/voice-of-indonesia/technology/2699200/brin-develops-tech-to-monitor-groundwater-and-cut-peatland-fires).
- FAO 2021 Practical Guidance for Peatland Restoration Monitoring in Indonesia — [PDF](https://luk.tsipil.ugm.ac.id/rawa/FAO/2021-PracticalGuidanceforPeatlandRestorationMonitoringinIndonesia.pdf) (listed; content not read).
- Taufik et al. 2022, Data in Brief 41:107903: daily measured groundwater depth at 8 in-situ stations, Batanghari (Sumatra) and Kubu Raya (Kalimantan) agricultural peat — [DOI 10.1016/j.dib.2022.107903](https://doi.org/10.1016/j.dib.2022.107903); [GPC record](https://www.tropicalpeatlands.org/knowledge/publication/11463-25021). Record length not captured.
- Leeds repository: Sebangau water-level loggers and rainfall, Aug 2019-Jan 2020, forested, blocked and drained sites — [DOI 10.5518/960](https://doi.org/10.5518/960) ([archive](https://archive.researchdata.leeds.ac.uk/832/)).
- PANGAEA: Mendaram peat swamp, Brunei, Solinst pressure-transducer water level series (Cobb and Harvey) — [PANGAEA.908207](https://doi.pangaea.de/10.1594/PANGAEA.908207), [908208](https://doi.pangaea.de/10.1594/PANGAEA.908208) (also 908210, 908214 related).
- Mega Rice Project, Central Kalimantan: continuous groundwater and canal level at over 40 observation wells (Yamamoto et al.) — [IPC abstract](https://peatlands.org/assets/uploads/2019/06/Yamamoto-335.pdf); no archive found.
- Zenodo 10.5281/zenodo.6997968: modelled (EPIC-IIASA) monthly WTD for Indonesian peat 2001-2010 at 0.25 degrees, not observations — [IIASA](https://pure.iiasa.ac.at/rest/eprint/18476/abstract.txt).
- Eddy covariance, Sarawak (Betong, secondary peat swamp forest): tower from Oct 2010, annual NEE/RE/GPP 2011-2014, with GWL and volumetric soil water content; three-site CH4 study (undrained forest, secondary forest, oil palm) Feb 2014-Jan 2017 — [Montana State](https://scholarworks.montana.edu/handle/1/15331), [CH4 paper](https://scholarworks.montana.edu/handle/1/14982).
- The OPTRAM paper's author list includes flux-site investigators for Indonesia, Malaysia (Hirano, Melling, Wong, Hergoualc'h) — [DOI record](https://doi.org/10.1029/2024JG008116).

### Inferences
- The OPTRAM 2024 validation implies WTD records from flux sites in Indonesia, Malaysia and Peru exist and may be shareable by collaboration, but public-repository status is unconfirmed.
- SIPALAGA gaps (17% missing) require gap flagging and QC before use as validation truth.

### Gaps
- Not found: station counts and record lengths for SIPALAGA, PRIMS, SESAME/TMAT, Deltares, CIFOR Dataverse, Sarawak Tropical Peat Research Institute; BMKG/BBWS hydrometric access; AsiaFlux/FLUXNET entries for Palangka Raya, Sebangau; open-licence status of SIPALAGA data. A direct check of those portals is needed.

## 5. Validation protocols, metrics, minimum sample size

### Takeaway
I found no tropical-peat-specific standard protocol or minimum-sample guidance. The literature uses r, R2, RMSE and (for InSAR) RMSE in cm/yr against groundwater-derived or peat-camera references.

### Cited Findings
- Metrics in use: Pearson r (Yananto 2022; Koupaei-Abyazani 2024), R2 and fraction within 0.25/0.5 m (Vernimmen 2020), RMSE in cm/yr for InSAR (Umarhadi 2021) — sources as above.
- InSAR reference options: groundwater converted to displacement (Umarhadi 2021) and peat cameras (EGU25-8505).
- Dry-season versus whole-year stratification changes correlations materially (Central Kalimantan SBAS, UGM page above).
- Sample sizes in published work: 8 stations (Taufik 2022), 12 BRG stations (SMAP bias correction), 145 field measurements (Vernimmen 2020).

### Inferences
- A credible design should (my recommendation, not sourced): use independent sites held out from calibration (leave-one-site-out), report RMSE and bias in cm plus r, stratify by land cover/NDVI and season, and treat best-pixel correlations as upper bounds. Given n of 8-12 stations in published work, claims should be framed as site-level demonstrations.

### Gaps
- No source found for formal minimum sample sizes (stations, observations) or a community protocol for peat WTD validation.
