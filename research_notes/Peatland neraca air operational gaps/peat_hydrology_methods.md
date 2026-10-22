# Operational water-balance / water-table modelling for tropical peatlands (Indonesia / SE Asia)

Scope note: this was a time-boxed pass (about 17 tool calls). Search results were mostly abstract-level. Two PDF fetches returned unreadable binaries. Items I recall from the literature but could not verify are listed under Gaps as "leads", not as findings.

## 1. Core process physics (storativity, K profile, ET, canals, subsidence, dome-scale flow)

### Takeaway
Peat hydraulic properties (K, specific yield) vary strongly with depth, decomposition and land cover, and ET (not subsurface flow) is a dominant water-table control. The best-documented process models for tropical peat (DigiBog_Hydro, Boussinesq-based canal-block models, PEATCLSM-Trop) all need depth-variable parameters. I found no verified numeric specific-yield curve in this pass.

### Cited Findings
- Slug tests at 19 sites in West Kalimantan gave saturated K from about 0.001 to 13.9 m/day. K was higher in forested than non-forested sites and fell with depth and decomposition stage. — [USGS summary of land cover and Ks in tropical peat](https://www.usgs.gov/publications/influence-land-cover-changes-variability-saturated-hydraulic-conductivity-tropical)
- In Peruvian wooded peat swamps, K at 50 and 90 cm was high; the authors conclude most water leaves via overland flow and/or evapotranspiration rather than subsurface flow. — [Kelly et al. 2014, St Andrews record](https://research-portal.st-andrews.ac.uk/en/publications/the-high-hydraulic-conductivity-of-three-wooded-tropical-peat-swa/)
- DigiBog_Hydro (Putra, Baird and Holden 2022) is a 2D water-table model for drained tropical peat in Sebangau, Central Kalimantan. Input files use K and specific yield that vary horizontally and with depth. — [Leeds dataset, DOI 10.5518/1053](https://archive.researchdata.leeds.ac.uk/916/)
- An NSF-funded study derived hillslope-scale transmissivity and specific yield as functions of water-table height in a tropical peatland (authors and year not given in the result). — [NSF PAR award 1520762 listing](https://par.nsf.gov/search/award_ids:1520762)
- ET and water table: Hirano et al. (2015, Global Change Biology) used eddy covariance in Central Kalimantan 2002-2009 at forest sites with different drainage. They report GWL was significantly lowered at the drained forest, especially in the dry season, and that ET is a major determinant of GWL. — [Hirano et al. 2015 (Hokkaido Univ. repository)](https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/65234)
- Acacia crassicarpa on Eastern Sumatran peat: stand transpiration about 20% higher at deeper water table (about -80 cm) than shallower (about -40 cm); transpiration is only about a fifth to a quarter of eddy-covariance ET. (Conference abstract, so preliminary.) — [EGU23-14383](https://meetingorganizer.copernicus.org/EGU23/EGU23-14383.html)
- Oil palm on Sarawak peat: preliminary Bowen ratio about 0.13, so latent heat dominates. (Extended abstract; long-term data still needed.) — [14th International Peat Congress abstract](https://peatlands.org/assets/uploads/2019/06/Sang-311.pdf)
- Subsidence and oxidation: in drained Acacia and oil palm plantations, land dropped 142 cm in the first 5 years (about 75 cm in year 1), then about 5 cm/yr at mean water table depth 0.7 m. Oxidation was 75% of cumulative subsidence after 5 years and 92% after 18 years; compaction mattered mainly in year 1. — [Hooijer et al. 2012, Biogeosciences 9:1053, DOI 10.5194/bg-9-1053-2012](https://www.biogeosciences.net/9/1053/2012/)
- Canal blocking field trial in the former Mega Rice Project Block C: higher water tables did not fully offset subsidence near canals, and eroding canals raise dam overtopping risk in heavy rain. — [Ritzema et al. 2014, CATENA 114:11-20, DOI 10.1016/j.catena.2013.10.009](https://research.wur.nl/en/publications/canal-blocking-strategies-for-hydrological-restoration-of-degrade/)
- Canal-block placement: Urzainki et al. (2020, Biogeosciences 17:4769) used a Boussinesq-equation hydrology model (3-day dry-downs from saturation) with genetic algorithm and simulated annealing on a 931 km2 Sumatran peatland; optimised layouts beat traditional placement. — [Urzainki et al. 2020 PDF](https://bg.copernicus.org/articles/17/4769/2020/bg-17-4769-2020.pdf)
- Urzainki et al. (2023, Biogeosciences 20:2099) used a process-based model for 168 canal blocks in a 22,000 ha Sumatran area, simulating daily water table depth for dry (1997) and wet (2013) years. — [Luke/Jukuri record](https://jukuri.luke.fi/handle/11111/5593)
- Mezbahuddin, Grant and Hirano (2014, Biogeosciences 11:577) applied the process model ecosys (coupled hydrology, energy balance and carbon) to a drained peat swamp forest at Palangkaraya; modelled NEP versus eddy covariance gave R2 above 0.8. A companion 2015 JGR-Biogeosciences paper (DOI 10.1002/2015JG003005) treats seasonal water table, energy exchange and water stress for 2002 (El Nino) to 2005. — [Biogeosciences 11:577](https://bg.copernicus.org/articles/11/577/2014/); [JGR 2015 listing](https://www.tropicalpeatlands.org/knowledge/publication/11463-34266)

### Inferences
- A credible operational model needs depth-dependent K and Sy (acrotelm/catotelm-like), canal boundary conditions, and a land-cover-dependent ET term tied to water table. Overland flow/ponding must be represented because it is a main outflow pathway in wet periods.
- Subsidence feeds back on drainage (canal-to-surface elevation), so a long-horizon model needs a subsidence module; short-horizon operational forecasts can hold elevation fixed.

### Gaps
- No verified numeric Sy-versus-WTD curve, acrotelm thickness, or K profile values (Baird et al. 2017 not located; only dataset/abstract hits).
- No verified Kc values for oil palm, Acacia, forest or scrub on peat; only conference abstracts on ET partitioning.
- Not located in this pass: Wosten et al. 2008, Dommain et al. dome hydrology, Kurnianto et al., Page/Hooijer 2011-2015 subsidence-drainage depth relationships, Hooijer 2015 (Deltares) dome-scale MODFLOW work. Leads for the next researcher.

## 2. Models in use and reported skill

### Takeaway
Process models (DigiBog, ecosys, Boussinesq/MODFLOW-type, PEATCLSM-Trop) and statistical/regression models all appear in the literature. I found few published numeric WTD skill scores for tropical peat; reported errors that I did verify are 16 cm (statistical) and an overall "improved bias and correlation" for PEATCLSM-Trop.

### Cited Findings
- DRAINMOD in Indonesia: Imanudin et al. (2009) on tidal lowland (mineral) soils in South Sumatra reported RMSE 2.75 cm and r2 0.92. Not peat. A 2018 DRAINMOD peat/oil palm paper exists but I did not see its statistics. — [Univ. Sriwijaya repository](https://repository.unsri.ac.id/24892/)
- Statistical peat WTD model (Febrianti 2018, Jurnal Ilmu Tanah dan Lingkungan): predictors are bulk density 0-50 cm, fibre 50-100 cm and peat depth; RMSE 16.2 cm, R2 81%. — [IPB journal](https://journal.ipb.ac.id/index.php/jtanah/article/view/29278)
- PEATCLSM-Trop (Apers et al., JAMES; preprint DOI 10.1002/essoar.10507826.1) added literature-based parameter sets for natural and drained tropical peat to NASA CLSM. Evaluated on in situ water level and eddy-covariance ET across Central/South America, Congo Basin and SE Asia: overall improvement in bias and correlation over default CLSM, with strong regional differences attributed to forcing accuracy and unrepresented hydrologic response. Drained sites in SE Asia were best with the Drain parameter set. — [White Rose record](https://eprints.whiterose.ac.uk/id/eprint/214913)
- EGU2020 slides: evaluation used 20 natural Indonesian sites, 13 Cuvette Centrale, 13 Central/South America and 42 drained Indonesian sites; drainage level set to -0.4 m; no regional tuning. — [EGU2020-17576](https://presentations.copernicus.org/EGU2020/EGU2020-17576_presentation.pdf)
- OPTRAM satellite model against in situ water table in Indonesia, Malaysia and Peru (Koupaei-Abyazani et al. 2024): R of 0.7-1 in low-to-intermediate NDVI areas but fails at high NDVI. — [FAO AGRIS record](https://agris.fao.org/search/es/records/669f5fcf00eb85b7d72c22e3)

### Inferences
- A bucket/linear-reservoir plus canal model is plausible for operations, but published validation numbers for such models on tropical peat were not found; the RMSE of about 16 cm for a statistical model is a rough benchmark to beat.

### Gaps
- No verified NSE or WTD RMSE (cm) for DRAINMOD, MODFLOW, SWAT, HYDRUS or ParFlow on tropical peat; PEATCLSM-Trop numeric statistics not in the abstract (read the JAMES paper).
- Mezbahuddin 2019 EGU abstract on Riau fire-risk WTD modelling not read.

## 3. Calibration, validation, uncertainty, data assimilation

### Takeaway
Data assimilation of satellite signals has been tried but is preliminary; most remote-sensing work on peat WTD is regression-based. I found no verified GLUE or DREAM applications to tropical peat.

### Cited Findings
- SMOS L-band brightness-temperature assimilation with a tropical peat land surface module improved water level at four sites (mean correlation 0.46 to 0.63); described as preliminary. — [KU Leuven project listing](https://www.researchportal.be/en/project/advancing-land-surface-modeling-and-satellite-data-assimilation-over-tropical-peatlands)
- A SMAP Level 4-style assimilation framework for peat moisture and water table (fire danger rating) is a stated PhD aim, not a result. — same source.
- Sentinel-1 VV backscatter regressions to peat water level/soil moisture exist for South Sumatra and Riau (thesis/regional studies). — [UGM thesis](https://etd.repository.ugm.ac.id/home/detail_pencarian_downloadfiles/663018)
- C-band InSAR coherence in Central Kalimantan is lost when surface water floods the ground in wet season. — [Tarigan et al. 2023, DOI 10.3389/fenvs.2023.1088923 (text not readable; claim from search summary)](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2023.1088923/pdf)
- Urzainki 2023 and DigiBog studies use dry versus wet year scenarios (1997, 2013) as a stress test for validation. — see Section 1.

### Inferences
- Cheapest credible operational design: point-in-time WTD loggers for calibration plus optical/SAR proxy for spatial correction (OPTRAM works only at low NDVI).

### Gaps
- No evidence found on GLUE, DREAM or ensemble Kalman filter applied to tropical peat WTD. No Sentinel-1 EnKF study found.

## 4. Indonesian management thresholds, fire risk, CO2-WTD relations

### Takeaway
The 0.4 m criterion comes from PP 57/2016 (amending PP 71/2014): cultivated peat is "damaged" if the water table is more than 0.4 m below the surface at the compliance point. Measurement procedures are in Permen LHK P.15/2017; P.16/2017 is the technical guide for restoration. The threshold is contested scientifically.

### Cited Findings
- PP 57/2016: peat ecosystems with cultivation function are damaged if water table is deeper than 0.4 m at the compliance point; businesses and Ministry of Agriculture proposed 0.6 m, KLHK/NGOs defended 0.4 m. — [Kontan](https://industri.kontan.co.id/news/pelaku-usaha-gulirkan-revisi-pp-gambut); [UNRI journal](https://jom.unri.ac.id/index.php/JOMFTEKNIK/article/download/21323/20632); [Warta Ekonomi](https://wartaekonomi.co.id/read153856/penetapan-tinggi-muka-air-gambut-04-meter-perlu-dikaji-bersama)
- Permen LHK P.15/2017 = procedure for measuring water table at compliance points; P.16/2017 = technical guide for peat ecosystem restoration (per Mongabay, not official text). — [Mongabay 2017](https://mongabay.co.id/2017/02/25/benahi-tata-kelola-gambut-menteri-lingkungan-terbitkan-aturan-aturan-berikut-ini/)
- Critique by Supiandi Sabiham: the threshold's research base was primary forest, but the rule applies to cultivated peat. — Warta Ekonomi link above.
- Fire thresholds: Taufik et al. (2022, Agricultural and Forest Meteorology) found high fire danger mostly when WT was below 40 cm and burned area only below 60 cm. Another Indonesian study recommends 40 cm for fire prevention and notes highly degraded peat may need levels within about 10 cm. A Febrianti-type model study suggests about 74 cm as critical. — [SEMNASHAS paper](https://conference.unsri.ac.id/index.php/semnashas/article/view/792); [IPB journal](https://journal.ipb.ac.id/index.php/jtanah/article/view/29278); [Climate Change News](https://climatechangenews.com/2023/08/09/forest-carbon-indonesia-peatland-nature-restoration/)
- Hooijer et al. 2010 (Biogeosciences 7:1505, DOI 10.5194/bg-7-1505-2010): drained SE Asian peat emitted 355-855 Mt CO2/yr in 2006, 82% from Indonesia; 12.9 of 27.1 Mha deforested/drained. — [Biogeosciences 7:1505](https://bg.copernicus.org/articles/7/1505/2010/)
- Hooijer 2012: about 178 t CO2eq/ha/yr in first 5 years then about 73; about 100 over 25 years; better water management cuts impact by at most 20%. — see Section 1.
- Evans et al. 2021 (Nature 593:548, mainly temperate/UK-Ireland plus published global data): each 10 cm reduction in mean annual effective WTD cuts net warming by at least 3 t CO2/ha/yr until WTD is under 30 cm. Not tropical-specific. — [Rothamsted repository](https://repository.rothamsted.ac.uk/item/984wq/overriding-water-table-control-on-managed-peatland-greenhouse-gas-emissions)
- Ideal range suggested by a Central Kalimantan hydropedology study: 40 cm below to 100 cm above surface. — SEMNASHAS paper link above.

### Inferences
- A product reporting "days with WTD deeper than 0.4 m" aligns with PP 57/2016 but should also show the 0.6 m fire level and ponding, because the 0.4 m number has weak tropical-specific and land-use-specific support.

### Gaps
- Official regulation text not retrieved (JDIH KLHK / peraturan.go.id). Check P.15/2017 article text and the compliance-point protocol before writing specs.
- Hooijer 2010 per-cm WTD emission coefficient (I recall roughly 0.9 t CO2/ha/yr per cm; not verified here); PDF fetch failed. Also unverified: Page et al. 2011 and Couwenberg et al. 2010 per-cm relations.

## 5. Critical gaps cited

### Takeaway
Gaps evident from the sources: parameter scarcity (K, Sy), forcing accuracy, drained-peat response not captured, regional performance spread, and sparse WTD ground truth.

### Cited Findings
- PEATCLSM-Trop regional skill differences are attributed to meteorological forcing accuracy and peatland hydrologic response not captured. — [White Rose record](https://eprints.whiterose.ac.uk/id/eprint/214913)
- K varies over four orders of magnitude (0.001-13.9 m/day), so single-value parameterisation is not defensible. — [USGS summary](https://www.usgs.gov/publications/influence-land-cover-changes-variability-saturated-hydraulic-conductivity-tropical)
- Satellite WTD proxies fail under dense canopy. — [OPTRAM study](https://agris.fao.org/search/es/records/669f5fcf00eb85b7d72c22e3)
- Fire/WTD thresholds are site-specific (10, 40, 60, 74 cm reported). — see Section 4.
- Canal-block assessments depend on dry versus wet scenario selection and canal erosion. — [Ritzema 2014](https://research.wur.nl/en/publications/canal-blocking-strategies-for-hydrological-restoration-of-degrade/)

### Inferences
- Dome boundaries, peat depth maps and canal geometry were not discussed in the sources I could read; they are widely assumed to be limiting but I have no citation.

### Gaps
- No source retrieved on dome-boundary delineation, peat depth map uncertainty, or Deltares/Wetlands International operational systems. Next step: Hooijer et al. 2015 and BRG/SIPALAGA/SiMATAG (Indonesia's real-time WTD network) documentation.
