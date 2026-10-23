# Runoff term: Pulau Padang studies (Amal, Sujono, Jayadi)

Recorded 2026-10-23. Covers the source of the runoff coefficient the team uses (C = 0.12, range 0.07-0.18, "two months, Pulau Padang", `docs/references.md` section 1) and how the runoff term could be built in the neraca module.

**What was read:** Amal et al. 2021 in full text (`research_notes/references/amal et al (2021).pdf`); the Amal 2022 ETD record (abstract only, fetched 2026-10-23); the Kurnianto et al. 2026 NORA record (abstract only, fetched 2026-10-23). Items marked *not checked* came from a pasted research summary and were not verified.

## Sources

| Source | Status | What it says |
|---|---|---|
| Amal, N. 2022. *Dampak Perubahan Iklim terhadap Kondisi Neraca Air pada Lahan Gambut Tropis: Studi Kasus di KHG Pulau Padang, Provinsi Riau.* Disertasi, Doktor Teknik Sipil, UGM. Supervisors Joko Sujono, Rachmad Jayadi. [ETD 208041](https://etd.repository.ugm.ac.id/penelitian/detail/208041) | abstract | KHG Pulau Padang split into **11 sub-KHG**; intact forest compared with drained HTI. Runoff enters the balance through a **runoff coefficient**. Balance used for storage change now and under CMIP5 RCP 4.5 and 8.5. −40 cm used as the minimum recommended water table. Current deficit months: **January, February, March, June, July**; worst in February in the north of the island. Future deficits unlikely because projected rainfall rises. Initial water table decides the flow response to rain. Share of time below −40 cm: HTI >95%, forest at most 68% (Indonesian abstract); the English abstract gives >90% and 60% |
| Amal, N., Sujono, J., Jayadi, R., Ohgushi, K. 2021. Variability of water table elevation and flow response of tropical peatland: case study at Pulau Padang, Riau, Indonesia. *Lowland Technology International* 22(4): 135-141 | *full text* | Field campaign November-December 2017 (two months), plus RAPP water-table loggers 2015-2017 (PPD 1, 2, 9 plantation; PPD 3, 4, 10 forest; PPD 8 buffer). Balance `ΔS = P − ET − RO − I`; event runoff volume from canal discharge (eq. 2-5). **No runoff coefficient value is given in the paper.** Bagan Melibur (community land, no canal blocks): water table −0.6 to −1.9 m, rain "directly flows as runoff to downstream". Sei Hiu (company land, canal blocks): −0.4 to −0.6 m. Event of 6 Nov: water table −1.179 m, 6.3 mm in 20 min already gave 60 L/s discharge before the water table moved |
| Kurnianto, S. et al. (incl. C.D. Evans, S.E. Page) 2026. Hydrological dynamics in a tropical peatland mosaic at Pulau Padang, Indonesia. *J Hydrol Reg Stud* 64: 103185, doi 10.1016/j.ejrh.2026.103185. CC BY 4.0, [NORA 541143](https://nora.nerc.ac.uk/id/eprint/541143/) | abstract | MIKE SHE–MIKE Hydro with LiDAR, imagery and field data, driven by 2015-2018 rain. ET is 62-98% of annual rain. Forest to managed land: about 1% less ET, **about 6% more runoff**, negligible storage change. Interannual rainfall: **up to eightfold** differences in runoff and about 120 mm reversal in storage. Canal dams kept drawdown under 5 cm within about 300 m of the outer canals. First affiliation is APRIL (the concession operator) |
| Holden, J., Burt, T.P. 2003. Runoff production in blanket peat covered catchments. *Water Resour Res* 39(7) | cited by Amal 2021 | Runoff in peat is generated in the top few centimetres; overland flow mostly at the surface. Blanket peat, UK |
| Chow, Maidment, Mays 1988, *Applied Hydrology*, ch. 15 | *not checked* | Rational / runoff-coefficient method |
| Jayadi et al. 2024, AWAM conference, multi-satellite rainfall in a runoff model | *not checked* | Possible help in choosing a rainfall product |

## Points to note

1. The 2021 paper and the dissertation abstract disagree on site labels. The paper calls Bagan Melibur community land without canal blocks and Sei Hiu company land with blocks; the dissertation abstract calls Sei Hiu "drained" and Bagan Melibur "intact". Check the full text before using either site as a forest reference.
2. The 2021 field data cover two wet-season months. If C = 0.07-0.18 came from this campaign, it has no dry-season or land-cover breakdown. The per-class C values, if any, are in the dissertation full text (ETD shows only abstract, contents and bibliography; UGM sign-in may give the PDF; Jayadi is at UGM Teknik Sipil).
3. Kurnianto et al. suggest rainfall input matters more than land-cover-specific C. Read with the APRIL affiliation in mind.

## Proposed runoff term (not built)

1. Direct runoff `RO = C × P` per sub-KHG per time step, as in Amal 2022 and the current `balance_compare.py` and `repeat-prioritisation/common/indicators.py`.
2. C as a lookup by land-cover class (intact forest, HTI, community land, burnt) in config, replacing the single 0.12. Fill from Amal 2022 once the full text is available; until then every class gets 0.12.
3. Optional: scale C with the previous step's water table (saturation-excess runoff rises as the water table nears the surface). Fits rewetting scenarios, where blocking raises the water table. No published tropical C-versus-water-table relation was found; this would need fitting.
4. Validation targets: Amal 2022 deficit months (Jan-Mar, Jun-Jul, worst February in the north) for KHG Pulau Padang.
