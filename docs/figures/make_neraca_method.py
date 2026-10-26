#!/usr/bin/env python3
"""Write docs/figures/neraca_method.drawio, the method diagram of docs/neraca-air-method.md (plain mxGraph XML; open in draw.io).

  python docs/figures/make_neraca_method.py

Edit the boxes here and rerun, or edit the .drawio in draw.io (then this script no longer matches it).
"""
from pathlib import Path
from xml.sax.saxutils import escape

cells, n = [], [1]


def _id():
    n[0] += 1
    return f"c{n[0]}"


def box(x, y, w, h, text, style):
    i = _id()
    cells.append(f'<mxCell id="{i}" value="{escape(text, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i


def edge(a, b, label="", dashed=False):
    st = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;strokeColor=#5f6b7a;fontSize=10;" + ("dashed=1;" if dashed else "")
    cells.append(f'<mxCell id="{_id()}" value="{escape(label)}" style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry"/></mxCell>')


B = "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=6;spacingTop=2;fontSize=11;"
INP, PRO = B + "fillColor=#eef3fb;strokeColor=#5b7db8;", B + "fillColor=#fff4e0;strokeColor=#c98a1b;"
PAR, OUT = B + "fillColor=#f3f3f3;strokeColor=#888888;dashed=1;", B + "fillColor=#e8f5ea;strokeColor=#3f8f50;"
USE, DIA = B + "fillColor=#f5ecf7;strokeColor=#8a5a9c;", B + "fillColor=#f7f7f7;strokeColor=#aaaaaa;fontColor=#666666;"
OLD, NEW = B + "fillColor=#fdf3e7;strokeColor=#b07a2a;", B + "fillColor=#e9f3fb;strokeColor=#2f6f9f;"
HDR = "text;html=1;fontSize=14;fontStyle=1;align=left;verticalAlign=middle;"
BAND = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#cccccc;dashed=1;align=left;verticalAlign=top;spacingLeft=8;fontSize=13;fontStyle=1;fontColor=#444444;"

box(20, 10, 1500, 30, "Neraca air, RE-PEAT: method adopted 2026-10-26 (repeat-neraca 0.1.0)", "text;html=1;fontSize=18;fontStyle=1;align=left;")
box(20, 42, 1500, 40, "<b>Any KHG, one command:</b> repeat-neraca-batch --selected | --khg &lt;codes&gt; | --all (865 KHG of khg_registry.csv). "
    "Per KHG: work folder _khg/&lt;code&gt;_&lt;name&gt;/; steps 1-2 below; a KHG without sub-KHG units runs as one unit (--whole-khg). Fetches cached per year; summary _khg/neraca_balance_summary.csv.", PRO)
for x, t in [(30, "INPUTS"), (420, "PROCESSING"), (900, "OUTPUTS  (_khg/&lt;khg&gt;/03_neraca/)")]:
    box(x, 88, 340, 24, t, HDR)
box(1260, 88, 250, 24, "USED BY", HDR)
# A
box(15, 115, 1510, 490, "A. Sub-KHG level: climatic water balance (formula and parameters of the 2021 Kahayan-Sebangau study)", BAND)
u = box(30, 145, 340, 52, "<b>Sub-KHG units</b> 02_delineation/subkhg_units.gpkg (repeat-delineation)<br>none yet: KHG boundary from batas_khg_indonesia.gpkg as one unit", INP)
ch = box(30, 205, 340, 62, "<b>Rain P: CHIRPS daily</b><br>0.05° (5.6 km), 1981 to 2026-09-30, public domain<br>used as the <b>KHG mean</b> for every unit", INP)
md = box(30, 275, 340, 62, "<b>ET (central): MODIS MOD16A2GF</b><br>500 m, 8-day sum ×0.1, fill codes masked<br>2000 to 2025-12; level within eddy-covariance range", INP)
wa = box(30, 345, 340, 62, "<b>ET (second source): WaPOR v3 L1 AETI</b><br>326 m, dekadal mean mm/day ×0.1, 2018 to 2026-10-11<br>20-30 % below eddy covariance", INP)
wc = box(30, 415, 340, 52, "<b>Land cover: ESA WorldCover v200</b> 10 m, 2021, CC-BY-4.0", INP)
im = box(30, 475, 340, 52, "<b>Checks only:</b> IMERG Final monthly (rain reference), TerraClimate (2021 reproduction)", INP)
f1 = box(420, 205, 400, 132, "<b>1. repeat_common.fetch_gee_balance</b> (Earth Engine, EE_PROJECT)<br>• dekads 1-10, 11-20, 21-end<br>• period total = Σ images (daily rate × overlap days)<br>• mean per unit on each product's own grid, no resampling; valid pixels, time coverage<br>• WorldCover shares per unit, counted in 0.1° pieces<br>• one request per year, cached; provenance .json", PRO)
b2 = box(420, 355, 400, 142, "<b>2. repeat_neraca.balance</b><br>• dekads → months (fully covered months only); complete years<br>• <b>WB = P (1 − I) (1 − C) − ET</b>, I = Σ share<sub>class</sub> × I<sub>class</sub><br>• u_wb_mean, u_deficit_months; also P − ET (water signal between units)<br>• <b>balance_stable_ok</b>: MOD16 and WaPOR agree on the order of ET, and the order holds between years, each above the p &lt; 0.01 random-order level", PRO)
pa = box(420, 507, 400, 88, "<b>Parameters</b> (repeat_neraca/parameters.yaml; B.K. Cahyono, established)<br>C = 0.12 · I: tree, mangrove 0.164 · shrub 0.08 · herbaceous wetland 0.05 · grass, crop 0.03 · other 0<br>stability: 99th percentile of a random order (0.43 for 30 units, 0.58 for 16)", PAR)
o1 = box(900, 205, 330, 80, "<b>inputs/</b> (or inputs/khg_level/)<br>balance_&lt;product&gt;_dekad.csv: unit_id, start, end, days, mm, n_px, time_cov (+ .json provenance)<br>units_landcover.csv: area_km2, wc_&lt;class&gt;", OUT)
o2 = box(900, 355, 330, 142, "<b>runs/balance/</b> (or runs/balance_khg_level/)<br>neraca_balance_unit.csv: <b>u_wb_mean</b> (mm/month), <b>u_deficit_months</b> (per year), <b>p_minus_et_mean_mm</b>, wb_year_sd_mm, interception_share, n_px_*, balance_stable_ok<br>neraca_balance_monthly.csv · neraca_balance.md (calendar, ET order, forest share) · registry_snapshot.json", OUT)
r1 = box(1260, 355, 250, 122, "<b>repeat-prioritisation</b> (C5)<br>rank-sum water slot = P − ET; u_deficit_months not ranked (follows land cover); empty where balance_stable_ok = 0; need-score weight 0", USE)
for a in (u, ch, md, wa, wc):
    edge(a, f1)
edge(f1, o1); edge(o1, b2, "read"); edge(b2, o2); edge(pa, b2, dashed=True); edge(o2, r1)
# B
box(15, 620, 1510, 250, "B. KHG level: supply deficit (mass balance on observed water tables)", BAND)
st = box(30, 650, 340, 62, "<b>Water table: SiTMAT stations</b><br>repeat-sitmat/sitmat_out/processed (SITMAT_PROCESSED)<br>concession stations, 2026-04-01 to 2026-10-22 only", INP)
er = box(30, 720, 340, 62, "<b>Rain and evaporation: ERA5 daily</b><br>repeat_common.forcing (cache) or forcing_daily.csv<br>E within −6 to +2 % of MOD16; rain as close to IMERG as CHIRPS", INP)
kb = box(30, 790, 340, 40, "<b>KHG boundary</b> 00_inputs/khg.gpkg", INP)
s1 = box(420, 650, 400, 52, "<b>3. repeat-neraca-stations</b> (site config neraca.yaml)<br>stations inside the KHG, ≥ 50 % of window days", PRO)
d1 = box(420, 715, 400, 70, "<b>4. deficit.py</b> (repeat-neraca-run)<br><b>deficit = max(0, −Σ(P − E) − Sy · Δz<sub>obs</sub>)</b>, 1 June to last forcing day (≤ 31 Oct)", PRO)
pb = box(420, 795, 400, 52, "<b>Parameters</b>: Sy 0.15 (band 0.10-0.20) · ERA5 P and E · Δz from first and last 7 days", PAR)
o3 = box(900, 650, 330, 62, "<b>inputs/</b> stations.csv, stations_daily.csv (depth_cm, positive down)", OUT)
o4 = box(900, 725, 330, 70, "<b>runs/deficit/neraca_khg.csv</b>: deficit_mm (low, high), deficit_m3, deficit_months, n_stations", OUT)
r2 = box(1260, 725, 250, 70, "<b>repeat-pump</b> (subkhg_priority.csv deficit_mm), prioritisation report", USE)
edge(st, s1); edge(kb, s1); edge(s1, o3); edge(o3, d1, "read"); edge(er, d1); edge(d1, o4); edge(pb, d1, dashed=True); edge(o4, r2)
# C
box(15, 885, 1510, 95, "C. Diagnostic only (not on the ranking path)", BAND)
box(30, 915, 790, 55, "<b>Physical model</b>, tiers 1 and 2 (lumped.py, spatial.py): Sy(z) dz/dt = R − C(z)(z − z<sub>c</sub>) and 2D Boussinesq; DTM, peat depth, canals by class. Explains why observed water tables are held (supply from outside the rain balance); per-sub-KHG skill 0, frozen.", DIA)
box(900, 915, 610, 55, "Retired 2026-10-26: bucket model fitted to SiTMAT (failed spatial skill check); record in docs/bucket_reports/. Not used: TerraClimate (ends 2024-12), runoff C 0.25 / 0.35 of the 2021 scripts.", DIA)
# D
box(15, 995, 1510, 300, "D. What was added to the 2021 Earth Engine method (B.K. Cahyono, Kahayan-Sebangau, users/bambangkun/NDVI_DenganSentinel2)", BAND)
old = box(30, 1025, 470, 260, "<b>2021 method (kept: formula, C, interception)</b><br>• WB = pr − aet/10 − C·pr, monthly<br>• TerraClimate rain and AET (4.6 km), 2010-2020<br>• C = 0.25 placeholder (0.35 for ten units in one script); team value C = 0.12 and interception by land cover from the same study<br>• charts and maps in the Code Editor, one KHG<br>• 16 sub-KHG drawn by hand<br>• no check against observations", OLD)
new = box(520, 1025, 990, 260, "<b>Added in repeat-neraca</b><br>• <b>Data:</b> CHIRPS rain (5.6 km, to 2026-09), MOD16 and WaPOR ET (500 m, 326 m), WorldCover interception shares; dekadal; native grids, pixel and time coverage per value; provenance per fetch<br>• <b>Rain as KHG mean:</b> CHIRPS and IMERG disagree on which sub-KHG are wetter (Spearman −0.34, −0.06)<br>• <b>Central ET MOD16:</b> 1,385-1,490 mm/yr against eddy covariance 1,374-1,636 (Hirano et al. 2015) and 1,579 (Tang et al. 2019); WaPOR and TerraClimate 1,100-1,260<br>• <b>Stability test</b> against a random order (p &lt; 0.01): ET products must agree on the order of ET; years must keep the order<br>• <b>Ranking signal P − ET:</b> u_wb_mean follows forest share through the fixed interception term (Spearman −0.44 to −0.82)<br>• <b>KHG deficit</b> on SiTMAT stations (water supplied from outside the rain balance) and the KHG calendar of deficit months<br>• <b>Checks:</b> 2021 reproduced within 0.1 mm; Pulau Padang deficit months match Amal (2022); per-unit deficit on stations<br>• <b>Package and scale:</b> any KHG from its code, batch over the registry, tests, clean-install check", NEW)
edge(old, new, "extended")

xml = ('<mxfile host="repeat-neraca"><diagram id="neraca" name="Neraca air method"><mxGraphModel dx="1600" dy="1320" grid="1" gridSize="10" guides="1" '
       'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1560" pageHeight="1320" background="#ffffff" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>\n")
out = Path(__file__).with_name("neraca_method.drawio")
out.write_text(xml, encoding="utf-8")
print(f"wrote {out} ({len(cells)} cells)")
