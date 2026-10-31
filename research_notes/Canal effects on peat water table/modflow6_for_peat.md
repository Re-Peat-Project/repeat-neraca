# MODFLOW 6 (via flopy) for the water table of a tropical peat KHG with canals, blocks and pumps

Research note, 2026-10-30. Read first: `research_notes/groundwater_models_review.md` (2026-10-28) and `docs/groundwater-model-report.md` section 8 and decision D5 (MODFLOW 6 parked as fallback). This note lists only what is new or what changes those conclusions.

Source labels: **doc** = MODFLOW 6 / flopy / modflowapi documentation page fetched 2026-10-30 (some fetched through a page-extraction query, so quotes are from the extractor's answer on that page); **full text** = body read; **snippet** = search summary only; **not fetched** = a claim I could not retrieve a source for. Anything marked *general knowledge, not fetched* must be checked before it goes into a report.

Search coverage was limited: Scite required a paid plan (unavailable), two page fetches failed (a DOI redirect and one USGS PDF timed out), and no run of MODFLOW was made. Several asked topics have no fetched source (see Gaps in each section).

## 1. Published use of MODFLOW for tropical peat water table and canal blocking

### Takeaway
Only thin evidence was reachable. Tropical peat MODFLOW studies found are small-domain, FREEWAT/MODFLOW with a boundary head at the canal and block height scenarios; none states calibration beyond NSE on wells near one canal. The previous notes' view (the equation is not the fault; inputs are) is unchanged. A correction: the Academia paper I found is a different paper from Suryadi et al. 2021 (see below), so do not merge their details.

### Cited Findings
- Suryadi et al. 2021 (J. Eng. Technol. Sci. 53(2)), "Effectiveness Analysis of Canal Blocking in Sub-peatland Hydrological Unit 5 and 6, Kahayan-Sebangau" exists with the DOI already in the project notes; only search listings were retrieved this session (snippet), so the earlier "full text" reading in `groundwater_models_review.md` is the only detailed source and was not re-checked. — [ResearchGate listing](https://www.researchgate.net/publication/351306008_Effectiveness_Analysis_of_Canal_Blocking_in_Sub-peatland_Hydrological_Unit_5_and_6_Kahayan_Sebangau_Central_Kalimantan_Indonesia), [Semantic Scholar listing](https://www.semanticscholar.org/paper/Effectiveness-Analysis-of-Canal-Blocking-in-Unit-5-Suryadi-Soekarno/87ed1976d63e0e7dc4fb6a8168c7a97b7d8391ee) (snippet)
- A second FREEWAT/MODFLOW peat paper: Chalid, Humam and Prasetyo, "The Modelling of Groundwater Table Management for Canal Blocking Scenarios in Sub Peatland Hydrological Unit", Int. J. Science, Technology & Management, doi 10.46729/IJSTM.V1I4.67. Model area 300 x 1000 m; hydraulic conductivity 50 m/d (5.78e-4 m/s); calibration chose the K with the largest NSE and correlation; a 0.5 m canal block scenario "completely eliminated deficit months". Sy, layers and the canal boundary type are not stated on the page (partial text from the Academia page, extractor answer). — [Academia page](https://www.academia.edu/50651044/The_Modelling_of_Groundwater_Table_Management_for_Canal_Blocking_Scenarios_In_Sub_Peatland_Hydrological_Unit)
- Urzainki et al. 2023 (already in notes) keeps a 2D peat model and states that its model updates the WTD but not the canal water level in the peat model, and that real blocks are permeable; the canal stage is a state of a separate canal model. Open-access full paper at Helsinki: <https://researchportal.helsinki.fi/files/265007377/bg_20_2099_2023.pdf> (snippet of that PDF; the BG page abstract also says blocks are most effective in peatlands with high hydraulic conductivity). — [BG article](https://bg.copernicus.org/articles/20/2099/2023/) (snippet)
- Groundwater Project book "Groundwater in Peat and Peatlands" (Price, McCarter, Quinton), ch. 7.1: MODFLOW is named as a free, documented option for landscape-scale peatland flow; saturated-flow models can represent the dominant processes because the peat is thin and the water table near the surface; the authors name the exponential decrease of K with depth in the upper layers as the main discretisation challenge, because it creates the transmissivity feedback (flow depends on water table elevation). Studies cited there with MODFLOW-type saturated flow in boreal/temperate peat: Reeve et al. 2000, Quillet et al. 2017, Lapen et al. 2005, Sutton 2021. — [GW Project 7.1](https://books.gw-project.org/groundwater-in-peat-and-peatlands/chapter/7-1-numerical-flow-and-transport-models/) (full text of the chapter)
- Reeve et al. peat vertical-flow study used constant K per layer, with K of 1e-2 and 1e-4 etc. for layers 1 to 6 (snippet of PDF listing only), a precedent for a stepwise K(z). — [Reeve et al. PDF (UC Davis mirror)](https://meadows.ucdavis.edu/sites/g/files/dgvnsk10941/files/2021-05/1-s2.0-S0022169499001833-main.pdf) (snippet)
- Kurnianto et al. 2019 conference paper (search snippet): forested peat K averaged 0.63 +/- 0.36 m/d against 0.20 +/- 0.13 m/d under oil palm. This sits below the 8.6-173 m/d horizontal Ksat range in the existing notes for the top metre; the two conflict and the difference (method, depth) is not resolved here. — [IPC 2016 abstract](https://peatlands.org/assets/uploads/2019/06/ipc16p165-168kurniantopeterson.etal_.pdf) (snippet)
- A temperate lowland fen forecast with a groundwater model (2025, ScienceDirect) and a Frontiers 2022 study ("Aquifer-Peatland Hydrological Connectivity") used MODFLOW (the Frontiers one: steady-state, MODFLOW 2005 per peatland). Neither is a drained-peat canal study. — [Frontiers](https://www.frontiersin.org/journals/earth-science/articles/10.3389/feart.2022.835817/full) (snippet)

### Inferences
- MODFLOW has been used on peat in studies of 1 to 2 orders smaller domain than a KHG and with constant K per layer; no source found reports MODFLOW 6, Newton, or a depth-dependent exponential T(z) for tropical peat. A MODFLOW 6 trial for tropical peat would be new, so the result cannot be benchmarked against a published MODFLOW skill.
- The FREEWAT/MODFLOW tropical studies reached good NSE only near one canal over a short calibration; they say nothing about skill across a KHG. That matches the project's finding that the whole-KHG test is the hard one.

### Gaps
- No full text of Suryadi et al. 2021 or Chalid et al. retrieved (grid, layers, packages, Sy, calibration period, canal boundary type unknown).
- No MODFLOW 6 or MODFLOW-NWT tropical peat paper found; no peat-specific example in the MODFLOW 6 examples repository was found.
- Consensus, Scite, alphaXiv were not used (Scite blocked by plan; others not tried). A literature search with them could find more.

## 2. Representing T(zeta) and Sy(zeta) in MODFLOW 6

### Takeaway
MODFLOW 6 gives each cell one K and (for convertible cells) one Sy, so an exponential T(z) and Sy(z) must be built from layers, as the peat literature says. The Newton formulation keeps cells wet ("Cells will not dry when this option is used"), which removes the NWT-style rewetting problem but does not remove the thin-top-layer accuracy and convergence questions; those are untested and need the trial. A possible new route, not in the notes: update K from the API each step (an external loop) instead of layering, flagged as an inference.

### Cited Findings
- NPF `ICELLTYPE`: 0 = saturated thickness held constant; >0 = saturated thickness varies with computed head when head is below the cell top. K is a cell value (K11, K22, K33 optional); all active cells need K > 0. — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc, full page)
- NPF default horizontal conductance averaging is harmonic mean. Options: `ALTERNATIVE_CELL_AVERAGING` = LOGARITHMIC, AMT-LMK (arithmetic-mean thickness, logarithmic-mean K), AMT-HMK (arithmetic-mean thickness, harmonic-mean K). Not usable with XT3D. — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- NPF `HIGHEST_CELL_SATURATION`: uses the maximum cell bottom for the saturation used in horizontal conductance, "intended to prevent flow from leaving a dry cell", applied only with Newton-Raphson; combined with AMT-HMK it reproduces MODFLOW-USG upstream weighting (LAYCON=4). — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- NPF `REWET` (WETFCT, IWETIT, IHDWET) exists for the standard formulation, plus the `WETDRY` array; off by default. — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- NPF `TVK6`: a time-varying hydraulic conductivity file lets K change at specified times or stress periods. — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- NPF `VARIABLECV` / `DEWATERED` and `PERCHED` control vertical conductance in dewatered convertible cells (vertical conductance is otherwise fixed at the initial head). — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- GWF name file `NEWTON`: activates the Newton-Raphson formulation for flow between connected convertible cells and for stress packages that support Newton terms; "Cells will not dry when this option is used"; `UNDER_RELAXATION` under-relaxes head when levels fall below the bottom of the model below a cell. — [NAM doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-nam.html) (doc)
- STO: `ICONVERT` 0 = confined storage; >0 = confined storage when head is above the cell top, "a mixed formulation of unconfined and confined storage" below the top. `SY` is required if any cell is convertible. `SS_CONFINED_ONLY` makes compressible storage only apply when head is at or above the top (the MODFLOW-2005 approach). `STEADY-STATE`/`TRANSIENT` per stress period. — [STO doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-sto.html) (doc, extractor answer)
- Lu et al. 2024 (Water Resour. Res. 60, e2022WR034334): MODFLOW 6 "inherits both the strengths and weaknesses of MODFLOW-NWT"; Newton needs a Jacobian and smoothing of conductance, storage and some source/sink terms, and upstream weighting is first-order accurate where harmonic mean and the other options are second order; they propose a Picard-based always-active-cell method as an alternative. — [Lu et al. 2024](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022WR034334) (full page, extractor answer)
- MODFLOW-NWT Problem 2 in the MODFLOW 6 examples uses upper ten layers convertible and lower four confined, Sy 0.2 (snippet). — [MF6 example ex-gwf-nwt-p02](https://modflow6-examples.readthedocs.io/en/master/_examples/ex-gwf-nwt-p02.html) (snippet)
- iMOD (Deltares) FAQ: layers that represent unconfined aquifers are often set inconvertible for a numerical reason (snippet only; the reason was not read). — [iMOD FAQ](https://deltares.github.io/imod-python/faq/modeling.html) (snippet)
- The USGS MODFLOW 6 documentation (tm6a55) has a "Saturated Cell Fraction" passage that fixes a value at "1 x 10..." (truncated in the snippet; value and meaning not retrieved). — [USGS tm6a55](https://pubs.usgs.gov/tm/06/a55/tm6a55.pdf) (snippet)

### Inferences
- A single layer cannot reproduce T(zeta) = t1 (exp(t2 zeta) - exp(-t2 d)): MODFLOW computes T as K times saturated thickness, linear in head. Stepwise K per layer (as Reeve et al. did) approximates the exponential; with an e-fold every ~0.4 m, layers of about 0.1 to 0.2 m at the top and coarser below keep K within ~25-40% across a layer. That layer count (the 8-10 already in the notes) is my arithmetic from the exponential, not a published rule.
- Sy(zeta) works the same way: each convertible layer has one Sy, applied when the water table sits in that layer. Layers thin in the top 0.5 m give a stepwise Sy(z). Storage with the water table above a layer top is the confined SS term, so set SS small and rely on SY.
- A thin top layer with Newton is where convergence is most likely to suffer (rapid change of saturation, ET and recharge applied to the top active cell). This is untested in any source retrieved and is the first thing to try in the trial.
- Option not in the notes: keep one layer (or a few) and let an external loop (modflowapi, or TVK6 per stress period) set K = T(h)/b from the previous head. That is a Picard-by-hand scheme and would mirror our solver, but it loses the advantage of Newton convergence; treat it as a comparison arm, not the main route.
- The MODFLOW 6 default horizontal averaging (harmonic K, arithmetic-mean thickness for AMT options) is not our arithmetic-mean T. Within one layer harmonic-K and the arithmetic mean differ only where K varies sharply between neighbours (canal cells, block cells, managed vs open land). Parity runs should set `ALTERNATIVE_CELL_AVERAGING` explicitly and test sensitivity.

### Gaps
- No peat-specific MODFLOW 6 example was found. No source on recommended minimum layer thickness with Newton, or on the saturated cell fraction value, was retrieved.
- Time stepping scheme of MODFLOW 6 (implicit backward Euler per time step) is *general knowledge, not fetched*.
- The Painter and Basagaoglu 2007 dry-cell paper appeared in search (Edwards Aquifer PDF, snippet: Newton more robust than Picard because it uses derivative information) but was not read.

## 3. Canals, blocks, pumps, managed cells, recharge, ET, ponding, time series

### Takeaway
Fetched documentation supports DRN (with depth-scaled discharge under Newton), WEL (negative Q = extraction, `AUTO_FLOW_REDUCE`), EVT (extinction depth and segments), UZF (surface depression, rejected infiltration, mover) and the MVR hook. SFR, LAK, CHD, RIV and RCH pages were not retrieved, so those mappings are *general knowledge, not fetched*. The groundwater-only part of our model maps onto MODFLOW 6 easily; the managed-cell top-up with a supply cap and the ponded-water removal need either DRN/WEL tricks or an API loop.

### Cited Findings
- DRN: `ELEV` (drain elevation) and `COND` (conductance of the aquifer-drain interface); `AUXDEPTHNAME` scales discharge between ELEV and ELEV + depth, linearly under the standard formulation and cubically under Newton-Raphson; `AUXMULTNAME` multiplies COND; `MOVER` allows routing discharge to other features. — [DRN doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-drn.html) (doc, extractor answer)
- WEL: Q positive = recharge (injection), negative = discharge (extraction); `AUTO_FLOW_REDUCE`, `AUTO_FLOW_REDUCE_CSV`, `TS6` (time series) and `MOVER` are options; an observation type `wel-reduction` reports the reduction when AUTO_FLOW_REDUCE is on. The option's definition text was not retrieved. — [WEL doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-wel.html) (doc, extractor answer)
- EVT: `SURFACE` (ET surface elevation), `RATE` (maximum ET flux), `DEPTH` (extinction depth), optional segments `PXDP`/`PETM` (proportion of extinction depth and of the maximum rate at the segment bottom, PXDP strictly between 0 and 1 and increasing), `SURF_RATE_SPECIFIED` with `PETM0`; `FIXED_CELL` stops ET being reassigned to a cell below when the specified cell is inactive; `READASARRAYS`; PETM, PETM0 and aux values can come from time series. — [EVT doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-evt.html) (doc, extractor answer)
- UZF: `SURFDEP` (surface depression depth); output `rej-inf` (rejected infiltration) and `uzf-gwd` (groundwater discharge to land surface); `MOVER` option; `SIMULATE_ET` removes ET from the unsaturated zone first, then the saturated zone, and `SQUARE_GWET` holds constant ET between land surface and land surface minus extinction depth, then reduces smoothly to zero; saturated water content `THTS` should be consistent with the Sy in STO; `FINF`, `PET`, `EXTDP` accept time-series names. — [UZF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-uzf.html) (doc, extractor answer)
- NPF/NAM state that Newton supports stress packages "that support calculation of Newton-Raphson terms for groundwater exchanges" (which ones is on the package pages, not retrieved). — [NAM doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-nam.html) (doc)

### Inferences (mapping to our model; none of these is from a fetched source unless it repeats a line above)
- Canal cells held at a level: CHD (fixed head), or RIV/DRN with a large conductance where the canal should only drain. Sub-cell canals with an exchange conductance are a close match to a DRN or RIV cell with COND = exchange conductance (*general knowledge, not fetched*).
- Blocks: a reach whose canal head is raised, i.e. higher DRN/CHD elevation on block reaches, as in our solver. A true weir with flow-through-block equations (Urzainki-style) would need SFR or LAK with MVR; that is the "canal network" option the owner deferred and MODFLOW 6 makes available (SFR/LAK not fetched).
- Pumps: WEL with negative Q on canal or peat cells; supply cap implemented as a limit on pumped volume per day; `AUTO_FLOW_REDUCE` helps when the cell cannot supply (definition not fetched).
- Managed cells topped up to a target with a supply cap: no direct package. Options: (a) a WEL of positive Q in each managed cell, recomputed each day by the API from head and the cap; (b) a CHD at the target depth for managed cells, which supplies without limit (matches no-cap runs only); (c) a DRN at the target elevation plus a WEL. Option (a) needs the API loop (section 5).
- Ponded water removed each step: use a DRN at land surface with high conductance (drains water that rises above the surface), or UZF `SURFDEP` with MVR; the DRN is the simpler parity match. MODFLOW 6 does not remove water above land surface by itself in the top layer unless something drains it (*general knowledge, not fetched*; verify with a test).
- Recharge/ET: RCH with net rain (rain minus ET) is the lightest parity match to our forcing; EVT adds extinction depth and would replace our ET handling, which is a model change, not a parity step. UZF is only worth trying later.
- Time-varying inputs: time series (TS6) for WEL/EVT/UZF values and per-period lists; 330 daily stress periods can also be written as one file per package with a TS file (TS/TAS pages not fetched).

### Gaps
- Not fetched: SFR, LAK, MVR, CHD, RIV, RCH, TS, TAS and IMS pages. Whether a pump or block can be inside SFR/LAK without hand-written weirs, and how SFR handles runoff and ponding, was not checked.
- No peat or tropical example with canals in MODFLOW 6 found.

## 4. Practical workflow: flopy, 700 x 700 grid, 330 daily periods, binary, install, API

### Takeaway
flopy installs the binary with a documented command; the API package is pip/conda installable and CC0. No source retrieved gives run time, memory or solver settings for a 500,000-cell model, so those are test outputs, not research results.

### Cited Findings
- FloPy includes a `get-modflow` utility to install USGS MODFLOW and related programs for Windows, Mac or Linux; it downloads versioned archives from the GitHub releases API; executables are compiled with Intel Fortran; a required `bindir` says where to install; special values include `:python` (Python's bin/Scripts dir), `:flopy`, `:home`, `:windowsapps`. By default it installs the MODFLOW-ORG/executables distribution, which includes `mf6` and over 20 other programs; the main MODFLOW 6 repo and nightly-build distributions contain only `mf6`, `mf5to6`, `zbud6` and a shared library (listed there as `libmf6.dylib`, i.e. the macOS name; the Windows library name was not shown). — [FloPy get-modflow docs](https://flopy.readthedocs.io/en/latest/md/get_modflow.html) (doc, extractor answer; docs version 3.12.0.dev0)
- modflowapi is "an extension to xmipy for the MODFLOW API", a joint development of the USGS and Deltares; needs Python 3.11+, numpy, pandas, xmipy; `pip install modflowapi` or `conda install -c conda-forge modflowapi`; CC0-1.0 licence; version 1.0.1 released Sep 2026 (develop is 1.1.0.dev0); examples include a Quickstart and a Head Monitor notebook (monitor heads during a simulation). — [modflowapi GitHub](https://github.com/MODFLOW-ORG/modflowapi) (full page)
- Papers using the MODFLOW 6 API for Python-driven feedback: Hughes et al. 2022, Environ. Model. Softw. 148:105257 (the API paper); Larsen et al. 2024, Groundwater 62(1):157-166 "An Agricultural Package for MODFLOW 6 using the application programming interface"; White et al. 2023 closed-loop contaminant treatment package. These show externally computed, per-step water management coupled to MODFLOW 6. — [modflowapi GitHub README](https://github.com/MODFLOW-ORG/modflowapi) (full page; the papers themselves not read)
- The step-by-step functions (initialize/update/finalize, get_value/set_value, callbacks) were not on the PyPI page; the extractor found no statement. — [PyPI modflowapi](https://pypi.org/project/modflowapi/) (page fetched, content absent)

### Inferences
- A daily loop with water-management feedback (read heads, compute top-up and pump flows, set WEL Q, step) is the use case the cited API papers show; per-day Python overhead at 500,000 cells is a numpy array read and write, which should be small next to the solve, but this is untested.
- The QGIS plugin would need to bring (i) flopy, (ii) the `mf6` executable (and for the API route, the shared library), downloaded by `get-modflow` or bundled; the previous note's "compiled binary the plugin would have to download" stands. A plugin zip that bundles a Windows `mf6.exe` avoids a runtime download but needs a licence check (below).
- USGS software is normally public domain; this was not verified in a fetched source here (*general knowledge, not fetched*). Verify the licence text of the MODFLOW 6 repository before bundling.

### Gaps
- No run time, memory or solver settings (IMS: complexity, outer/inner tolerances, linear solver, parallel) retrieved for a 500,000-cell, 330-period model; no MODFLOW 6 parallel (MPI) availability on Windows checked.
- No pip-installable `mf6` wheel was verified (e.g. via a conda-forge `modflow6` package); not checked.
- Licence file of MODFLOW 6 not fetched.

## 5. A fair parity test against our Boussinesq solver

### Takeaway
No source for a published parity design was retrieved; this section is a plan from first principles plus the fetched documentation about averaging and Newton behaviour. Treat all analytical statements as *general knowledge, not fetched*.

### Cited Findings
- MODFLOW 6 default horizontal conductance averaging is harmonic mean; AMT-LMK/AMT-HMK and LOGARITHMIC alternatives exist; `HIGHEST_CELL_SATURATION` with Newton changes the saturation used for flow out of a nearly dry cell. — [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- Newton: cells do not dry; standard formulation: cells can go dry, rewetting is optional. — [NAM doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-nam.html), [NPF doc](https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html) (doc)
- Lu et al. 2024 report that upstream weighting is first-order accurate and that the Newton route needs smoothing of conductance and storage terms, so exact agreement between a Newton MODFLOW 6 and a Picard code is not expected near dry cells. — [Lu et al. 2024](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022WR034334) (full page, extractor answer)
- Our expected block effect sizes (lateral 9 cm at 100 m and below 5 cm at about 300 m with dams; KHG mean 1.4-1.6 cm) are in `groundwater_models_review.md` section 2 (Kurnianto 2026, Urzainki 2023) and are the sanity band for scenario runs.

### Inferences (test design, my own)
- Expected discrepancies, in order of likely size: (1) face averaging: harmonic K per layer in MODFLOW 6 against arithmetic-mean T in our solver, differing at canal, block and managed-land boundaries; (2) vertical discretisation of T(zeta) and Sy(zeta): a stepwise K and Sy against a continuous function, tunable by layer count; (3) time stepping and convergence: implicit Euler in both (MODFLOW 6 is *general knowledge, not fetched*), but different iteration tolerances; (4) dry-cell handling and ponded water: our rule removes ponded water each step, MODFLOW 6 needs a drain at the surface; (5) canal exchange: sub-cell canal conductance vs DRN/RIV conductance and the leakage terms in the first layer.
- Verification tools: mass balance (MODFLOW 6 budget closes by default; compare cumulative storage change, recharge, ET, canal and pump flows with our budget terms per day), and the maximum head difference after calibrating nothing.

## 6. Ordered test plan (1-2 weeks)

Success is stated before the runs so a gate is not moved afterwards (project rule).

1. **Day 1: environment.** In a new venv, `pip install flopy modflowapi`; run `get-modflow :python` (or a fixed `bindir`), confirm `mf6 --version` is 6.8.1 or later. Record versions in the trial report. Gate: a 10 x 10 flopy example runs and its budget closes.
2. **Days 1-2: 1D ditch strip, steady and transient, constant T and Sy.** Single layer, convertible cell with Newton, two fixed-head ditch cells, uniform recharge. Compare to the textbook Dupuit-Forchheimer ditch solution (*general knowledge, not fetched*) and to our solver. Gate: head differences at mid-strip below 1 cm for constant K; budget error below 0.01% of recharge (thresholds are proposed, set before running).
3. **Days 2-4: layered T(zeta), Sy(zeta) strip.** Same strip with the exponential T and the two Sy sets (0.3 to 0.1 over 1.5 m; 0.6). Build 8, 12 and 20 layers with thin tops (e.g. 0.1 m near the surface). Compare against our solver run on the same strip at fine time step. Report: head profile difference, run time, Newton iterations per step, any non-convergence on thin layers (the open question in section 2). Gate: converge on every step with 12 layers; mid-strip head difference below 2 cm against our solver after the averaging choice is made (test `ALTERNATIVE_CELL_AVERAGING` options).
4. **Days 4-5: boundary parity on a small 2D block (e.g. 30 x 30 cells).** Add: sub-cell canal as DRN/RIV with our exchange conductance, a block reach, a pump WEL, ponded-water removal (surface DRN). Compare day by day for 30 days, including budgets term by term. Gate: every budget term within 1% of ours or the difference explained by item (1)-(5) above.
5. **Days 5-7: managed-cell top-up with supply cap via modflowapi.** Implement the daily loop in Python (read heads, set WEL Q per managed cell). Compare with our solver's managed-cell rule on the same strip. Gate: same stored volume and same total supply within 2%. Time the loop; this decides plugin feasibility.
6. **Days 7-10: KHG-scale run.** Sugihan-Lumpur or Kampar-Gaung, 100 m grid, the layered model, 330 daily periods, our forcing and canals. Measure memory and wall time; try IMS settings (outer and inner tolerances, linear solver). Gate: finishes in a time within 3 times our solver's (the owner can reset), no memory failure on the project machine, budget closes.
7. **Days 10-12: skill and scenario comparison.** Compare simulated heads with the same station and field gates as `groundwater/fieldcheck.py` (same screening rule, D20/D21), per sub-KHG; run the pump scenario and the block scenario at 0.4/0.6/0.8 m; compare effect sizes by distance band (within about 350 m of a reach) against the existing solver and the literature band above. Success: MODFLOW 6 reproduces the existing solver's baseline levels at the stations within the same gate and its block effect within the literature band; a MODFLOW result that differs from our solver by more than the layering and averaging explain is a finding about one of them, to be investigated, not settled by choosing the better-looking one.
8. **Days 12-14: decision record.** Write the outcome as a D-entry in `docs/groundwater-model-report.md`: accuracy against our solver, speed, install burden for the plugin (the `mf6` binary, the shared library if the API loop is used, flopy), and whether the managed-cell top-up can stay outside the solver.

## Evidence gaps that would change this plan
- If thin top layers do not converge with Newton (test 3), layering is the blocker the project note feared; fall back to the TVK6/API "variable K, one layer" arm described in section 2.
- If the API loop is slow at 500,000 cells (test 5), managed-cell top-up has to be a CHD at the target depth, which gives no supply cap.

## Source index
- NPF: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-npf.html
- NAM: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-nam.html
- STO: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-sto.html
- EVT: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-evt.html
- DRN: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-drn.html
- WEL: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-wel.html
- UZF: https://modflow6.readthedocs.io/en/stable/_mf6io/gwf-uzf.html
- FloPy get-modflow: https://flopy.readthedocs.io/en/latest/md/get_modflow.html
- modflowapi: https://github.com/MODFLOW-ORG/modflowapi
- Lu et al. 2024: https://doi.org/10.1029/2022WR034334
- GW Project 7.1: https://books.gw-project.org/groundwater-in-peat-and-peatlands/chapter/7-1-numerical-flow-and-transport-models/
- Chalid et al.: https://www.academia.edu/50651044/The_Modelling_of_Groundwater_Table_Management_for_Canal_Blocking_Scenarios_In_Sub_Peatland_Hydrological_Unit
- Urzainki et al. 2023: https://bg.copernicus.org/articles/20/2099/2023/
