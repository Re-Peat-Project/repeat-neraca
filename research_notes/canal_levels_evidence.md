# Canal water levels in drained tropical peat: published evidence

Research note, 2026-10-29. Question: what the literature says about four modelling ideas for the canal boundary of `repeat-neraca-model`. Builds on `groundwater_data_papers.md` (items A6, B1, B6, B7), `peat_parameters_sumatra_kalimantan.md` (Ismail et al. 2021 section) and `groundwater_models_review.md`; those items are cross-referenced here, not repeated. Our own LiDAR check is `docs/reports/lidar_canal_levels_14.10.01.md`.

Labels: *full text* (body read, PDF downloaded and searched), *abstract*, *snippet* (search result text only), *existing note* (value taken from a note listed above, not re-read today).

Industry funding: the LiDAR and field work in Vernimmen et al. 2020 and Hooijer et al. 2024 were funded by Asia Pulp and Paper; Evans et al. 2019 used APRIL data.

## 1. Canal water level below the surface by canal class

Our numbers: on the 2 m Pulau Padang DTM (flown November 2016), the median depth at the mapped line is 0.80 m for Kanal Primer (416 transects), 0.32 m for Sekunder (593) and 0.24 m for Tersier (2,372); the control 100 m away is 0.05 to 0.06 m. The line is the lowest point of the transect in only 35 to 46% of transects. The model uses 1.2 m for all classes; 0.6 m fitted community stations better.

**No published source measures canal water level by canal class.** What exists splits by crop and elevation, or covers only large canals, or gives design targets.

- **Vernimmen, R., Hooijer, A., Mulyadi, D., Setiawan, I., Pronk, M., & Yuherdha, A. T. (2020).** A new method for rapid measurement of canal water table depth using airborne LiDAR, with application to drained peatlands in Indonesia. *Water, 12*(5), 1486. https://doi.org/10.3390/w12051486. *full text*.
  - Canals mapped were "always over 3 m in width, excluding drains and ditches, and mostly between 5 and 10 m". Field drains are not covered.
  - Validation in Acacia plantations (South Sumatra, Jambi, Riau, West Kalimantan), August 2018, a dry period: "water levels were mostly more than 0.5 m below the surface, but still less than 1 m in this area".
  - Ex-Mega Rice Project, Central Kalimantan, dry season 2011, canals not managed: canal water "more than 1.5 m below the surrounding peat surface near canals in most peatlands in this area, and more than 2.5 m over large distances", up to 5 m in places. Rice scheme canals on mineral soil: −1 to 0 m.
  - Canal levels "can fluctuate by decimeters day by day, especially around rainfall events".
- **Vernimmen, R., & Hooijer, A. (2026).** Satellite LiDAR reveals patterns in water table depth and flood risk in SE Asia coastal lowland and peatland plantations. *Frontiers in Environmental Science, 14*, 1869652. https://doi.org/10.3389/fenvs.2026.1869652. *full text* (PDF downloaded today; summary in B1).
  - Only "canals that present open water surfaces of considerable width and without vegetation cover" (Dadap canal map) are included.
  - Mean CWD goes "from −0.6 to −0.85 m for oil palm and Acacia plantations, respectively ... where the surface is 5–9 m above global mean sea level, to ~ -0.2 m at 1–3 m elevation". Oil palm on peat: −0.22 m (1 to 3 m elevation) to −0.63 m (7 to 9 m). At 1 to 3 m elevation all subsets lie in −0.19 to −0.24 m.
  - Overall mean −0.42 m; "half (50%) of all 15,575 CWD measurements ... are in the −0.2 to 0 m range". At 7 to 9 m elevation, 40% of values are below −0.8 m.
  - Elevation, not canal class, is the variable that orders the depths.
- **Urzainki, I., Laurén, A., Palviainen, M., et al. (2020).** Canal blocking optimization in restoration of drained peatlands. *Biogeosciences, 17*, 4769–4784. https://doi.org/10.5194/bg-17-4769-2020. *full text*. The 1.2 m in our model comes from here: "In the absence of any blocks, the CWL is assumed to be at a fixed distance, w, below the elevation derived from the DEM", with w = 1.2 m (Table, parameters). The same paper notes that this transfers "any local fluctuation in the height of the DEM ... directly ... to the CWL". The model had no quantitative validation (report section 2.1).
- **Urzainki, I., et al. (2023).** Modeling the effects of canal blocking in tropical peatlands. *Biogeosciences, 20*, 2099–2116. https://doi.org/10.5194/bg-20-2099-2023. *full text*. Every canal has the same width (1.5 m) and bed depth (1.5 m below the local peat surface, Table 1). Canal level is a model state solved with a diffusive wave, not a fixed offset.
- **Evans, C. D., Williamson, J. M., Kacaribu, F., et al. (2019).** Rates and spatial variability of peat subsidence in Acacia plantation and forest landscapes in Sumatra, Indonesia. *Geoderma, 338*, 410–421. https://doi.org/10.1016/j.geoderma.2018.12.028. Open copy: https://nora.nerc.ac.uk/id/eprint/522239/. *full text*. Canal classes in APRIL plantations (Riau): navigable canals "typically of 12 m width and 3 m depth"; branch canals 5 to 8 m wide at 500 to 800 m spacing; "1 m deep field drains at a spacing of 75 m". A 1 m deep field drain cannot hold water deeper than about 1 m. No canal levels are reported.
- **Hooijer, A., Page, S., Jauhiainen, J., et al. (2012).** Subsidence and carbon loss in drained tropical peatlands. *Biogeosciences, 9*, 1053–1071. https://doi.org/10.5194/bg-9-1053-2012. *full text*. Plantation canals "5 to 8 m wide, over 3 m deep and spaced 500 to 800 m apart". No canal levels.
- **RSPO (2019).** *RSPO Manual on Best Management Practices (BMPs) for Existing Oil Palm Cultivation on Peat*, Vol. 1 (eds. Parish, F., et al.), July 2019. https://rspo.org/library/lib_files/preview/954. *full text*. A design target, not a measurement: "an average water level of 60cm (range 50- 70 cm) below the bank in collection drains or 50 cm average (range of 40-60 cm) as measured by a groundwater piezometer". One stop-off or weir per 20 cm drop, so 5 weirs per metre of fall at 200 to 400 m spacing (RSPO Smallholder BMP Manual, Chapter 2, https://rspo.org/wp-content/uploads/2-water-management-the-flood-risk-assessment-template-is-attached-separately.pdf, *full text*). The main drain appears only as a photo of "over-drainage".
- **Ismail et al. 2021** (existing note): Pulau Padang plantation drains 1 m (tertiary) to 10 m (primary) wide, up to 5 m deep, spacing 130 m; farm drains under 1 m wide. Drain function (blocked or open) mattered as much as distance.
- **Kurnianto et al. 2026** (existing note, not re-read; ScienceDirect returned a bot page): MIKE SHE at Pulau Padang, 123 dams as broad-crested weirs with crest 0.6 m below ground, dynamic canal stage.
- **BRG/UNDP/UGM (2018).** *Kajian Komprehensif Topo-Hidro-WM, Penyusunan Peta Arahan Tindakan RG P. Padang* (slides, 8 August 2018), `re-peat/docs/Kajian Kompre Topo Hidro WM - Penyusunan Peta Arahan Tindakan RGP Padang.pdf`. *full text*. Used the same 2016 LiDAR to map "kedalaman saluran air dari lahan" and canal width (blocking criteria: depth over 1 m, width over 3 m). Block counts per sub-KHG are given; no canal depth values.

What this means for the Pulau Padang check:
- The Tersier lines are most likely the 1 m wide drains Ismail describes. On a 2 m DTM they are sub-pixel, and LiDAR returns few points from water (Vernimmen 2020: water "typically absorbs the LiDAR near-infrared wavelength of 1064 nm"), so the DTM interpolates across them. Our 0.24 m (Tersier) and 0.32 m (Sekunder) are best read as shallow bounds, not water levels. The report says this; the literature agrees.
- Vernimmen 2020 found cells under 50 m "inaccurate" and needed the minimum over a 100 m cell of a 1 m DTM with open water. Our ±10 m window on a 2 m DTM is narrower than anything validated.
- The flight date (November 2016) is one moment. Whether it was wet or dry at Pulau Padang was not checked here; canal levels move by decimetres in days.
- The literature range for managed plantation canals is about −0.2 to −0.85 m (Vernimmen & Hooijer 2026), with the RSPO collection-drain target at 0.5 to 0.7 m. The 1.2 m in the model matches unmanaged canals in a dry season (Central Kalimantan, below −1.5 m), not managed concessions. A 0.6 m value lies inside the managed range. Primary canals at 0.8 to 0.9 m fit the deeper end (Acacia at higher elevation).

## 2. Canal stage controls the water table; stage varies by season; managed stage; field drains

No source compares canal stage against canal seepage conductance directly. The support for "stage dominates" is an inference from three observations: in plantations the peat water table sits close to the canal level, field drains are closely spaced, and the peat is highly permeable.

- **Hooijer, A., Vernimmen, R., Mulyadi, D., et al. (2024).** Benefits of tropical peatland rewetting for subsidence reduction and forest regrowth: results from a large-scale restoration trial. *Scientific Reports, 14*, 10721. https://doi.org/10.1038/s41598-024-60462-3. *full text* (summary in A6). New numbers:
  - "We estimate GWD from CWD as: GWD = CWD + 0.05 m. This limited difference is explained by the closely spaced field drains (< 200 m intervals) and the high hydraulic conductivity of the peat (119 m d−1)".
  - LiDAR CWD at four dates (25 January 2017, 16 October 2017, 21 August 2018, 18 July 2020): "The first two dates are in the wet season when the canal water table tends to be high, the latter in the dry season when it generally is low." Mean estimated GWD per cell −0.24 to −0.67 m; overall mean −0.41 m; temporal range −0.08 to −0.90 m.
  - Dipwells: the 10 to 90 percentile range was "consistently around 0.4 m" in every zone; below −1 m in the 2019 El Niño.
- **Vernimmen & Hooijer 2026** (above): "from field experience in plantation water management, we know that overall, measured across the seasons and at multiple locations, water levels in canals tend to be less than 0.1 m below those in the peat." Explained by "~500 m between main canals, less than 100 m between field drains", and under 10 m on flood-prone mineral soil. Oil palm "can have mature water level control infrastructure that may be fine-tuned over years to manage small water steps over numerous gates, which is harder to achieve in Acacia plantations." Annual mean CWD varied by no more than 0.1 m at their aggregation level.
- **Jauhiainen, J., Hooijer, A., & Page, S. E. (2012).** Carbon dioxide emissions from an Acacia plantation on peatland in Sumatra, Indonesia. *Biogeosciences, 9*, 617–630. https://doi.org/10.5194/bg-9-617-2012. *full text*. "peat water tables follow canal water levels that are managed to meet the operational plantation requirement of stable drainage depth, so that these can be controlled independently of weather conditions." Canals at 800 m intervals, "excluding field drains".
- **Evans et al. 2019** (above): water levels "actively managed via an extensive network of topographically-defined water management zones, controlled by outlet sluices". They add that topography, canal transport use and "seasonal variations in water availability all place limits on the extent to which spatially and temporally uniform water levels can be achieved". Subsidence was unrelated to distance to the nearest canal (R² = 0.00), but "we were unable to include field drains in this analysis".
- **RSPO 2019** (above): "In droughts, the water level can drop 0.5- 1cm per day", 15 to 30 cm over a month without inflow; raise levels at the end of the wet season. Collection drain target about 10 cm below the field target.
- **Hooijer et al. 2012** (above): water table "can vary by up to a metre over a few kilometres in each type of plantation, and also over time within the dry and wet seasons".
- **Ismail, I., Karyanto, O., & Kløve, B. (2018).** Spatial and temporal variation of water table in degraded and abandoned tropical peatlands. EGU General Assembly, *Geophysical Research Abstracts, 20*, EGU2018-17323. https://meetingorganizer.copernicus.org/EGU2018/EGU2018-17323.pdf. *abstract*. Degraded, unmanaged peat in Central Kalimantan: dry-season drawdown from drainage "reaches a minimum value three kilometers away from the ditch". Kurnianto 2026, with dams, finds the effect under 5 cm by about 300 m (existing note). The reach of a canal is much larger where it is open and the peat is degraded.
- **Baird et al. 2017** (B6) and Kurnianto 2026 Ksat 8.6 to 173 m/d (existing note): high K is what makes the peat follow the canal.
- Seasonal canal stage series: Putra et al. 2021 (A1, ditch loggers, open data) and Hooijer 2024 monthly canal levels 2021 to 2023 (on request). No open concession canal series was found (D in `groundwater_data_papers.md`).

Field drains denser than mapped canals: yes, in every plantation description read. Spacing 75 m (Evans, Acacia, Riau), 130 m (Ismail, Pulau Padang), under 100 m (Vernimmen & Hooijer, general), under 200 m (Hooijer 2024, former Acacia). Main or branch canals sit 500 to 800 m apart. Whether the KLHK Kanal Tersier layer holds every field drain at Pulau Padang was not checked.

## 3. Can a LiDAR DTM measure canal water levels?

Yes, with conditions; all from Vernimmen et al. 2020 (*full text*) unless stated.
- Water absorbs the 1064 nm pulse; returns come from turbidity, floating debris or plants. Ground classification often removes water, and the DTM then interpolates over it.
- Their method: minimum of a 1 m DTM within each 100 m cell as the water level, median as the surface. Validated against 145 field points: R² 0.74, mean absolute difference 0.13 m, 86% within 0.25 m, 99% within 0.5 m. Only canals over 3 m wide, single canals (no double roadside canals or junctions).
- Limits they name: cells under 50 m were inaccurate; overgrown canals have uncertain locations; a cell may cover only a short canal section; peat microtopography (lowest to highest over 5 to 10 m averaged 0.27 m in 290 clusters, over 0.45 m in 10%); ground beside canals is disturbed by spoil and excavator tracks, so field surface was taken 25 m from the canal; "applicable in flat lands" only; the result is the level at the flight date.
- Vernimmen, R., Hooijer, A., Yuherdha, A. T., et al. (2019). Creating a lowland and peatland landscape digital terrain model (DTM) from interpolated partial coverage LiDAR data for Central Kalimantan and East Sumatra, Indonesia. *Remote Sensing, 11*(10), 1152. https://doi.org/10.3390/rs11101152. *full text*. "it cannot be excluded that small inundated areas were classified as ground"; the steepest peat slopes are next to canals, where subsidence is greatest, with drops "of more than 1 m within the first 500 m from the plantation boundary canal". A low surface beside a canal is therefore not the canal water level.
- Satellite LiDAR (Vernimmen & Hooijer 2026): ATL03 photons within 5 m of the centreline, crossings at over 30°, at least 5 photons and a tight interquartile range; wide open canals only.
- Roelens, J., Dondeyne, S., Van Orshoven, J., & Diels, J. (2016). Extracting cross sections and water levels of vegetated ditches from LiDAR point clouds. *International Journal of Applied Earth Observation and Geoinformation, 53*, 64–75 (citation from the Vernimmen 2020 reference list; DOI not looked up). *snippet*: works on the point cloud, not the DTM; accuracy figures not seen. The workspace has no Pulau Padang point cloud (AGENTS.md).

## 4. Do plantations keep the water table near 40 cm?

The rule: SK.22/PPKL/PKG/PKL.0/7/2017 requires the water table "within 40 cm of the peat surface at the centre of each plantation block for half of the year, and within 100 cm of the surface at all times" (Evans et al. 2019, *full text*, quoting the regulation). Evans adds that this "represents a significant change to existing operational procedures, which generally involve drainage of the peat to a target depth of around 70 cm."

Measured means sit deeper than 40 cm:
- Evans et al. 2019 (*full text*): Acacia 70 ± 17 cm, forest 47 ± 22 cm; "Almost all plantation sites had a WTDm of 40 cm or greater"; "the plantation-only dataset included very few sites with WTD < 40 cm". Monitoring 2007 to December 2016, so mostly before the 2017 rule.
- Hooijer et al. 2012 (*full text*): mean 0.70 m (Acacia) and 0.73 m (oil palm), "close to the target of 0.7 m specified for the Acacia plantations studied ... and of 0.6 m for oil palm plantations in general"; individual readings 0 to 1.6 m; "this does not suggest that high and well-controlled water levels are the norm".
- Jauhiainen et al. 2012 (abstract part of *full text*): mean water table 0.8 m in the Acacia transects.
- Deshmukh et al. 2023: −0.65 ± 0.17 m, Acacia, Kampar (existing note).
- Vernimmen & Hooijer 2026 (*full text*): oil palm at 5 to 9 m elevation mean CWD −0.6 m, "below the Indonesian policy target of −0.4 m"; Acacia on peat at 5 to 9 m about −0.85 m. At 1 to 3 m elevation about −0.2 m, often near flooding. Data 2018 to 2025, so after the rule.
- Hooijer et al. 2024 (*full text*): even in a retired, blocked former plantation the overall mean was −0.41 m.
- RSPO 2019 (*full text*) recommends 40 to 60 cm in the field and notes higher levels (under 40 cm) "may reduce yields".
- Industry views quoted in news: Acacia roots "require at least 0.8 – 1 meter of dry soil", oil palm yields highest at 50 to 75 cm (Mongabay/Eco-Business, 2015, https://news.mongabay.com/2015/01/indonesia-to-weaken-peatlands-protection-to-support-plantations/). *snippet*.

Compliance reporting:
- KLHK's SiMATAG-0,4m database holds 9,603 compliance points (titik penaatan) for TMAT and rain, at first on licensed land only (KLHK press release, 18 June 2019, https://mail.ppkl.menlhk.go.id/website/filebox/600/190618152629Press%20Release%20SiMATAG%2018%20Juni%202019%20REV.docx). *snippet*. A layer of plantation compliance points with company, permit and coordinates is on the Sumsel peat GeoNode (https://datagambut.sumselprov.go.id/layers/geonode:tp_tmat_perkebunan). *snippet*.
- No peer-reviewed analysis of company-reported compliance-point data was found.
- Gap to resolve: the repo's own analysis found concessions holding 35 to 55 cm through the dry season (`Peatland neraca air operational gaps/README.md`), while independent measurements give 0.6 to 0.85 m at higher elevations. Possible reasons include where compliance points sit (block centre, near weirs, low ground), the years covered (most published dipwell data predate 2017), and elevation (low plantations are wetter). The data in hand do not separate these.

Not found or not checked: a Dadap et al. paper on canal block effects (only the canal map paper and a soil-moisture fire paper turned up); Sinclair et al. (not searched beyond the name); Deshmukh et al. 2021, *Nature Geoscience 14*, 484–490, https://doi.org/10.1038/s41561-021-00785-2 (*snippet*: intact and degraded forest sites, no plantation canal data in what was seen).

## Summary per idea

**1. Canal depth differs by class**
- Supports: Evans 2019 (field drains 1 m deep against 3 m canals, so field drains cap at about 1 m); RSPO targets differ between field and collection drain by about 10 cm; Ismail 2021 widths 1 to 10 m.
- Contradicts: nothing directly. Vernimmen & Hooijer 2026 show elevation and crop, not class, ordering canal depth.
- Unknown: measured canal water level per class; no source has it. Our Tersier and Sekunder values are likely shallow bounds from sub-pixel drains.
- On the value: 1.2 m (Urzainki 2020, unvalidated) matches unmanaged dry-season canals; managed plantations measure about 0.2 to 0.85 m; 0.6 m is within range.

**2. Stage controls the water table**
- Supports: Hooijer 2024 (GWD = CWD + 0.05 m), Vernimmen & Hooijer 2026 (under 0.1 m difference), Jauhiainen 2012 (water tables follow managed canal levels); field drains 75 to 200 m apart; K 119 m/d.
- Contradicts: none found. Evans 2019 found no subsidence link to canal distance, but could not include field drains.
- Unknown: a direct test of stage against conductance; open seasonal canal series in concessions.

**3. LiDAR measures canal level**
- Supports: Vernimmen 2020 (0.13 m mean error, canals over 3 m, 100 m cells, 1 m DTM); Hooijer 2024 used it at four dates.
- Contradicts: for narrow drains on a 2 m DTM with a ±10 m window, none of the validated setups apply; water absorption and interpolation give shallow bounds; subsided canal margins bias the surface reference.
- Unknown: accuracy for drains under 3 m wide.

**4. Plantations keep about 40 cm**
- Supports: Hooijer 2024 (−0.41 m mean, retired blocked plantation); Vernimmen & Hooijer 2026 low-elevation plantations (about −0.2 m); RSPO target 40 to 60 cm.
- Contradicts: Evans 2019 (70 ± 17 cm, almost all sites at 40 cm or deeper), Hooijer 2012 (0.70 to 0.73 m), Vernimmen & Hooijer 2026 (−0.6 to −0.85 m above 5 m elevation, 2018 to 2025).
- Unknown: any analysis of SiMATAG compliance-point data; why our station data read shallower than the published means.
