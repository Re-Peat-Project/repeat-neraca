# RE-PEAT — Neraca Air Module: Build Recap for Agent

> **2026-10-26:** superseded in part by [method-plan.md](method-plan.md), which sets the method to finalise and lists, in its section 7, the items here proposed for removal. Nothing below has been removed yet.

**Context.** RE-PEAT (WorldBank–KLH) rewetting workflow, UGM Geodesi GIS team.
- The neraca air module is **separate** from the rewetting/pompanisasi workflow. Its job is to **prioritise sub-KHG units** by water need.
- **Elevation:** LiDAR DTM is the main input. Open DEMs are being tested as a partial substitute.
- **Target implementation:** Python, eventually a QGIS Processing plugin.
- **Rule:** every algorithm used must carry a reference. Anything marked **[TO VERIFY]** is a working assumption.

---

## 1. Core equations (per sub-KHG unit, per time step)

The formulation follows Amal, Sujono, Jayadi & Ohgushi (2021), Ref [13].

**Intact peat:**

    P − ET − RO − I = ΔS

**Drained peat (with canal network):**

    ΔS = I − O
    I  = V_P                (rainfall volume)
    O  = V_RO + V_ET        (runoff + evapotranspiration)
    V_RO = SRO + SSRO       (surface runoff + subsurface runoff to canal)
    V_RO = Σ Q_t · Δt       (integrated measured canal discharge per rain event)

**Extension for this project:**

    ΔS = P − ET − Q_out + Q_in,pump + Q_in,upstream

| Term | Meaning |
|---|---|
| P | Precipitation |
| ET | Actual evapotranspiration (incl. interception) |
| RO / Q_out | Direct runoff to canals = surface + subsurface |
| Q_in,pump | Pompanisasi inflow |
| Q_in,upstream | Inflow from the upstream sub-KHG unit |
| ΔS | Peat water storage change, linked to TMA via specific yield (Sy) |

**Key behaviour to reproduce (Ref [13], Pulau Padang):**
- **Unblocked canals.** Rain leaves as direct runoff before it can raise TMA. Community land (Bagan Melibur) sat below −0.4 m about 90% of the time.
- **Blocked canals.** Water is retained and TMA stays healthier. Company land (Sei Hiu) was within the limit more than 70% of the time.
- **Antecedent TMA controls the response.** In one event TMA rose from −1.179 m to about −0.39 m within roughly 2 hours, after about 37 mm of rain.
- **Upstream–downstream coupling.** When upstream flow is retained, downstream units receive nothing and their TMA keeps falling. Ref [14]

**Other settings:**
- **Time step:** dekadal (10-day), matching the ET products. Monthly is the fallback. Event-scale runoff (Ref [13]) needs sub-daily P, so use the 10-min spateGAN output for calibration events.
- **Deficit for prioritisation:** Sy × (TMA_current − 0.4 m) × area.
- **[TO VERIFY]** Sy/retention values per peat type. Start from Ref [7]; the Amal dissertation, Ref [15], may hold calibrated values.

---

## 2. Data inputs

### 2a. Precipitation (P)

| Option | Resolution | Use |
|---|---|---|
| **spateGAN-ERA5** (cGAN downscaling) | ERA5 24 km/1 h → 2 km/10 min, ensemble output; public on-demand tool | Historical baseline. **Primary.** Ref [1] |
| WaPOR v3 L1 PCP | ~5 km, daily/dekadal | Simple consistent alternative. Ref [5] |
| **WeatherNext 2** | 0.25°, 64 members, 6-hourly, 15 days. Via Earth Engine, BigQuery or the Open-Meteo API | Forecast mode, operational pumping decisions. Ref [2] |

- spateGAN-ERA5 was trained only on German radar and validated in the US/Australia, including tropical regimes. **Validate against BMKG gauges before use.**
- **Bias correction:** empirical quantile mapping (EQM) against gauges or CHIRPS, following the method used for West Java in Ref [4].

### 2b. Evapotranspiration (ET)

| Option | Resolution | Use |
|---|---|---|
| **Copernicus CLMS ET** (WaPOR-ETLook + TSEB-PT) | 300 m, dekadal, near-real-time (+2 days), split into E and T | **Primary**, operational. Ref [6] |
| WaPOR v3 L1 AETI | 300 m, dekadal/monthly, covers 50°S–80°N | Primary, historical. Ref [5] |
| GLEAM4 | 0.1°, daily, 1980–2023; also soil moisture and potential evaporation | Long climatology and trends only; too coarse for sub-KHG. Ref [8] |

### 2c. Water table (TMA) and storage (ΔS) for calibration/validation

> **BRGM was dissolved on 31 Dec 2024. SIPALAGA is no longer operational.** Do NOT design around it.

**Current sources, in priority order:**
1. **KLH/BPLH TMAT monitoring.** Request station data through the KLH coordination. KLH uses < 80 cm as the "very vulnerable" threshold.
2. **SiMATAG-0,4m** (concession TMAT points, originally KLHK). **[TO VERIFY]** whether it is still active under KLH.
   - South Sumatra republishes points on the datagambut.sumselprov.go.id GeoNode, which has WMS/WFS endpoints loadable in QGIS.
3. **Village loggers.** Patchy coverage, e.g. 51 of 154 peat villages in Jambi.
4. **Historical/benchmark data.**
   - Archived SIPALAGA data (2019–2024) via published studies.
   - The open daily TMA dataset for Batanghari and Kubu Raya, which includes peat water retention curves. Ref [7]
   - Pulau Padang RAPP stations PPD 1–10 (2015–2017, hourly) and the field data in Ref [13].

**Bias note:** concession points sit mostly in managed, drained plantations. Calibration may not transfer to community land. Ref [13] shows the community-vs-company contrast directly.

### 2d. Spatial TMA proxy (optional gap-filler)
- **Sentinel-1 VV backscatter → TMA** by linear regression. The Riau model is Y = −101.629 − 7.414·σ⁰_VV(dB). Ref [9]
  - It was calibrated on SIPALAGA, so coefficients are site-specific. **Re-fit per KHG** against the TMA sources in 2c.
- **InSAR subsidence** (Sentinel-1 time series) as a dryness/drainage indicator for the priority ranking. Ref [10]

### 2e. Static layers
LiDAR DTM (or open DEM), sub-KHG boundaries, sekat kanal points **with status (built/functional/broken)**, canal and river polygons, land cover, peat depth map, and management type (community vs concession).

---

## 3. Processing pipeline (proposed)

1. **Define units.** Use sub-KHG polygons, or split them into zones of uniform elevation from the DTM.
   - KLH's water-sharing practice in Riau zones land by elevation uniformity. Ref [11]
   - Build an **upstream→downstream adjacency graph** of units from the DTM and canal network. Ref [14] shows this coupling.
2. **Pull P.** spateGAN-ERA5 (historical) or WeatherNext 2 (forecast), then EQM bias correction.
3. **Pull ET.** CLMS/WaPOR 300 m dekadal, then zonal statistics per unit.
4. **Compute Q.** Split into surface and subsurface runoff per Ref [13], with a runoff coefficient conditioned on:
   - canal-block status (blocked vs unblocked), Ref [13]
   - antecedent TMA, Ref [13]
   - canal density from the LiDAR/canal layer
   - **[TO VERIFY]** C values. Calibrated values are likely in Ref [15]. Context only: a drained tropical peat catchment in Johor had annual C of 0.32–0.92, Ref [16].
5. **Compute ΔS** per unit per dekad, routing Q_out of upstream units into Q_in of downstream units. Convert to ΔTMA via Sy.
6. **Calibrate/validate** ΔTMA against KLH/SiMATAG TMA (step 2c). Optionally spread spatially with the re-fitted Sentinel-1 model.
7. **Rank sub-KHG** by deficit relative to the 0.4 m target, weighted by:
   - antecedent TMA
   - upstream position
   - hotspot/burn history
   - subsidence
8. **Package** as Python modules, then wrap as a QGIS Processing plugin.

---

## 4. Optional advanced track: custom km-scale downscaling
- **CorrDiff** (NVIDIA Earth-2/PhysicsNeMo): a UNet predicts the mean, then a diffusion model corrects the residual. Country-scale training needs roughly O(100) GPU-hours.
  - It needs a high-resolution Indonesian target (BMKG radar or WRF runs). Ref [3]
- **Architecture choice.** Per Ref [12], U-Net is stable but smooths extremes; generative models (WGAN, diffusion) capture heavy tails at the cost of more uncertainty.
  - Monthly or dekadal totals: deterministic is fine.
  - Extreme events: go generative.

---

## 5. Candidate novel contributions (beyond Ref [13]–[15])

Ref [13] establishes the water balance and the canal-block effect at site scale with event discharge. The contributions below scale it up. Each is a proposal and must be checked for prior art before claiming novelty.

**N1. Spatially explicit, block-state-dependent runoff partition at KHG scale.**
- Assign each unit a runoff coefficient from mapped sekat kanal status and LiDAR canal density, instead of one site value.
- Builds directly on Ref [13]'s blocked/unblocked contrast.

**N2. Graph-based water sharing between sub-KHG units.**
- Represent units as nodes and canals/flow paths as edges.
- Route outflow downstream, and test how pompanisasi and block placement redistribute water.
- This turns Ref [14]'s upstream-retention finding into a decision tool.
- **[TO VERIFY]** pick a referenced allocation/optimisation algorithm before implementing.

**N3. Probabilistic neraca air.**
- Propagate the spateGAN-ERA5 rainfall ensemble (Ref [1]) and the 64-member WeatherNext 2 forecast (Ref [2]) through the balance.
- Output **P(TMA < −0.4 m)** per unit per dekad instead of a single deficit. Rank by risk, not by mean.

**N4. Data assimilation of TMA observations.**
- Update unit storage with sparse KLH/SiMATAG TMA points and the Sentinel-1 TMA proxy (Ref [9]), using an Ensemble Kalman Filter (Ref [17]).
- This naturally pairs with the ensemble inputs from N3.

**N5. Hybrid physics + ML residual.**
- Keep the water balance as the backbone, and train an LSTM on its residual TMA error.
- An LSTM predicted TMA well at 12 South Sumatra stations using lagged TMA, rainfall, soil moisture and temperature, Ref [18].

**N6. Dynamic topography.**
- Update the LiDAR DTM over time with InSAR subsidence (Ref [10]).
- Canals "eat" into peat and create depressions that intercept flow and overtop dams, Ref [19]. A static DTM will drift from reality.

**N7. Climate-scenario neraca air.**
- Extend Ref [15]'s climate-change neraca air approach to all project KHGs, using downscaled projections in place of historical P.

### Recommended build priority
| Priority | Item | Role |
|---|---|---|
| **Core (paper contribution)** | N1 + N2 | Spatially explicit runoff by block status, routed through the unit graph. This is the main methodological advance over Ref [13]–[15]. |
| **Analytics layer** | N3 | Ensemble risk output, P(TMA < −0.4 m), feeds the KLH visual-analytics dashboard. Assumptions and initial values should stay adjustable there. |
| Phase 2 | N4, N5 | Add once enough KLH/SiMATAG TMA data is secured. |
| Phase 3 | N6, N7 | Longer-term: dynamic DTM and climate scenarios. |

**Before claiming novelty:** run a prior-art search on each of N1–N3 for tropical peatland.

---

## 6. Open questions
- [ ] KLH TMAT station access and format
- [ ] SiMATAG-0,4m status post-reorganisation
- [ ] Runoff coefficient values: obtain the Amal (2022) dissertation PDF, Ref [15]
- [ ] Sy values per peat class
- [ ] Time step: dekadal vs monthly (and sub-daily for calibration events)
- [ ] Can an open DEM substitute for LiDAR in unit delineation?
- [ ] Sekat kanal status layer: who maintains it (KLH or the Ministry of Forestry)?
- [ ] Allocation algorithm and reference for N2

---

## References
1. Glawion, L., Polz, J., Kunstmann, H., Fersch, B., Chwala, C. (2025). Global spatio-temporal ERA5 precipitation downscaling to km and sub-hourly scale using generative AI. *npj Climate and Atmospheric Science*. doi:10.1038/s41612-025-01103-y. Tool: EGU26-17479, doi:10.5194/egusphere-egu26-17479
2. Google DeepMind. WeatherNext 2. https://github.com/google-deepmind/weathernext ; Open-Meteo API: https://open-meteo.com/en/docs/google-weathernext-api
3. Mardani et al. CorrDiff — residual corrector diffusion for km-scale downscaling. https://docs.nvidia.com/deeplearning/modulus/modulus-core/examples/generative/corrdiff/readme.html
4. Bayesian Tweedie Compound Poisson Gamma modelling for statistical downscaling of rainfall in West Java (EQM bias correction with CHIRPS). *Journal of Agrometeorology* 27(4):487–493 (2025)
5. FAO WaPOR v3 — https://www.fao.org/in-action/remote-sensing-for-water-productivity ; pipeline docs: https://bitbucket.org/cioapps/wapor-et-look/wiki/Understanding_the_WaPOR_Pipeline
6. Copernicus CLMS global 300 m ET (WaPOR-ETLook + TSEB-PT), released Dec 2025. FAO WaPOR news.
7. Taufik et al. group. Daily groundwater depth and soil water retention of Indonesian peatlands (Batanghari, Kubu Raya). *Data in Brief* 41:107903
8. Miralles, D.G. et al. (2025). GLEAM4. *Scientific Data* 12:416. doi:10.1038/s41597-025-04610-y
9. Groundwater level estimation model on peatlands using SAR Sentinel-1 data in part of Riau. *IJReSES* 18(2). doi:10.30536/ijreses.v18i2.13780 (also UGM thesis, Ardila Yananto)
10. Izumi, Y. et al. (2022). A 3-year tropical peatland subsidence time series derived by Sentinel-1: Kalimantan.
11. KLH/BPLH press release SR.132/HUMAS/KLH-BPLH/6/2026 (water sharing, elevation-based zoning, Riau)
12. Singh, S. et al. (2026). Comprehensive inter-comparison of generative AI models for super-resolution precipitation downscaling. *GMD* 19:7545. doi:10.5194/gmd-19-7545-2026
13. Amal, N., Sujono, J., Jayadi, R., Ohgushi, K. (2021). Variability of water table elevation and flow response of tropical peatland: case study at Pulau Padang, Riau, Indonesia. *Lowland Technology International* 22(4):135–141. https://cot.unhas.ac.id/journals/index.php/ialt_lti/article/view/674
14. Amal, N. (2019). Water table and direct runoff in drained peatland, Pulau Padang (water budget of land–channel interaction). *Proc. 3rd World Irrigation Forum*, Bali, 1–7 Sep 2019. https://repo-dosen.ulm.ac.id/handle/123456789/29215
15. Amal, N. (2022). Dampak Perubahan Iklim terhadap Kondisi Neraca Air pada Lahan Gambut Tropis — Studi Kasus KHG Pulau Padang, Provinsi Riau. PhD dissertation, Dept. Teknik Sipil dan Lingkungan, UGM. Supervisors: J. Sujono, R. Jayadi.
16. Hydrologic characteristics of a drained tropical peat catchment: runoff coefficients, water table and flow duration curves (Parit Madirono, Johor). *Jurnal Teknologi* 38. doi:10.11113/jt.v38.487
17. Evensen, G. (2003). The Ensemble Kalman Filter: theoretical formulation and practical implementation. *Ocean Dynamics* 53:343–367.
18. Model Prediksi Temporal Tinggi Muka Air sebagai Peringatan Dini Karhutla pada Lahan Gambut Menggunakan LSTM. IPB University repository. http://repository.ipb.ac.id/handle/123456789/113554
19. Ritzema, H., Limin, S., Kusin, K., Jauhiainen, J., Wösten, H. (2014). Canal blocking strategies for hydrological restoration of degraded tropical peatlands in Central Kalimantan, Indonesia. *Catena* 114:11–20.

**Institutional context:** BRGM dissolved 31 Dec 2024 (Kompas, Mongabay 2025). Peat restoration now sits with KLH and the Ministry of Forestry.
