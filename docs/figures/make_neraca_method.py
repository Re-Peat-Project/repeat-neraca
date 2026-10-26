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
HDR = "text;html=1;fontSize=14;fontStyle=1;align=left;verticalAlign=middle;"
BAND = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#cccccc;dashed=1;align=left;verticalAlign=top;spacingLeft=8;fontSize=13;fontStyle=1;fontColor=#444444;"

box(20, 10, 1500, 30, "Neraca air, RE-PEAT: method adopted 2026-10-26 (repeat-neraca)", "text;html=1;fontSize=18;fontStyle=1;align=left;")
box(20, 42, 1500, 40, "<b>Any KHG, one command:</b> python -m repeat_neraca.batch --selected | --khg &lt;codes&gt; | --all (865 KHG of khg_registry.csv). "
    "Per KHG: work folder _khg/&lt;code&gt;_&lt;name&gt;/; steps 1-2 below; a KHG without sub-KHG units runs as one unit (--whole-khg). Fetches cached per year; summary _khg/neraca_balance_summary.csv.", PRO)
for x, t in [(30, "INPUTS"), (420, "PROCESSING"), (900, "OUTPUTS  (_khg/&lt;khg&gt;/03_neraca/)"), (1260, "USED BY")]:
    box(x, 88, 250 if x > 1200 else 340, 24, t, HDR)
# A
box(15, 115, 1510, 470, "A. Sub-KHG level: climatic water balance (method of the 2021 Kahayan-Sebangau study)", BAND)
u = box(30, 145, 340, 52, "<b>Sub-KHG units</b> 02_delineation/subkhg_units.gpkg (repeat-delineation)<br>none yet: KHG boundary from batas_khg_indonesia.gpkg as one unit", INP)
ch = box(30, 205, 340, 62, "<b>Rain P: CHIRPS daily</b><br>UCSB-CHG/CHIRPS/DAILY, 0.05° (5.6 km), mm/day<br>1981 to 2026-09-30, public domain", INP)
wa = box(30, 275, 340, 62, "<b>ET (central): WaPOR v3 L1 AETI</b><br>FAO/WAPOR/3/L1_AETI_D, 326 m, dekadal mean mm/day ×0.1<br>2018 to 2026-10-11; includes interception", INP)
md = box(30, 345, 340, 62, "<b>ET (second source): MODIS MOD16A2GF</b><br>500 m, 8-day sum ×0.1, fill codes masked<br>2000 to 2025-12, no use restrictions", INP)
wc = box(30, 415, 340, 52, "<b>Land cover: ESA WorldCover v200</b><br>10 m, 2021, CC-BY-4.0", INP)
f1 = box(420, 205, 400, 132, "<b>1. repeat_common.fetch_gee_balance</b> (Earth Engine, EE_PROJECT)<br>• dekads 1-10, 11-20, 21-end<br>• period total = Σ images (daily rate × overlap days)<br>• mean per unit on each product's own grid, no resampling; valid pixels, time coverage<br>• WorldCover shares per unit, counted in 0.1° pieces<br>• one request per year, cached; provenance .json", PRO)
b2 = box(420, 355, 400, 122, "<b>2. repeat_neraca.balance</b><br>• dekads → months (fully covered months only)<br>• <b>WB = P (1 − I) (1 − C) − ET</b>, I = Σ share<sub>class</sub> × I<sub>class</sub><br>• complete years only (all 12 months)<br>• indicators per unit; Spearman between years and between ET sources → balance_stable_ok", PRO)
pa = box(420, 487, 400, 88, "<b>Parameters</b> (src/repeat_neraca/parameters.yaml; B.K. Cahyono, established)<br>C = 0.12 · I: tree, mangrove 0.164 · shrub 0.08 · herbaceous wetland 0.05 · grass, crop 0.03 · other 0<br>stability threshold Spearman 0.5 (provisional)", PAR)
o1 = box(900, 205, 330, 80, "<b>inputs/</b> (or inputs/khg_level/)<br>balance_&lt;product&gt;_dekad.csv: unit_id, start, end, days, mm, n_px, time_cov (+ .json provenance)<br>units_landcover.csv: area_km2, wc_&lt;class&gt;", OUT)
o2 = box(900, 355, 330, 132, "<b>runs/balance/</b> (or runs/balance_khg_level/)<br>neraca_balance_unit.csv: <b>u_wb_mean</b> (mm/month), <b>u_deficit_months</b> (per year), wb_year_sd_mm, p_minus_et_mean_mm, interception_share, n_px_*, balance_stable_ok<br>neraca_balance_monthly.csv · neraca_balance.md · registry_snapshot.json", OUT)
r1 = box(1260, 355, 250, 92, "<b>repeat-prioritisation</b><br>extra_indicators (C5): replaces its TerraClimate balance, fills the rank-sum water slots; empty where balance_stable_ok = 0; need-score weight 0", USE)
for a in (u, ch, wa, md, wc):
    edge(a, f1)
edge(f1, o1); edge(o1, b2, "read"); edge(b2, o2); edge(pa, b2, dashed=True); edge(o2, r1)
# B
box(15, 600, 1510, 250, "B. KHG level: supply deficit (mass balance on observed water tables)", BAND)
st = box(30, 630, 340, 62, "<b>Water table: SiTMAT stations</b><br>repeat-sitmat/sitmat_out/processed (SITMAT_PROCESSED)<br>concession stations, 2026-04-01 to 2026-10-22 only", INP)
er = box(30, 700, 340, 62, "<b>Rain and evaporation: ERA5 daily</b><br>repeat_common.forcing (cache) or forcing_daily.csv<br>KHG mean, local days (WIB)", INP)
kb = box(30, 770, 340, 40, "<b>KHG boundary</b> 00_inputs/khg.gpkg", INP)
s1 = box(420, 630, 400, 52, "<b>3. repeat_neraca.stations</b> (site config neraca.yaml)<br>stations inside the KHG, ≥ 50 % of window days", PRO)
d1 = box(420, 695, 400, 70, "<b>4. deficit.py</b> (scripts/run_neraca.py)<br><b>deficit = max(0, −Σ(P − E) − Sy · Δz<sub>obs</sub>)</b>, 1 June to last forcing day (≤ 31 Oct)", PRO)
pb = box(420, 775, 400, 52, "<b>Parameters</b>: Sy 0.15 (band 0.10-0.20) · ERA5 central, WaPOR bound · Δz from first and last 7 days", PAR)
o3 = box(900, 630, 330, 62, "<b>inputs/</b> stations.csv, stations_daily.csv (depth_cm, positive down)", OUT)
o4 = box(900, 705, 330, 70, "<b>runs/&lt;run&gt;/neraca_khg.csv</b>: deficit_mm (low, high), deficit_m3, deficit_months, n_stations", OUT)
r2 = box(1260, 705, 250, 70, "<b>repeat-pump</b> (subkhg_priority.csv deficit_mm), prioritisation report", USE)
edge(st, s1); edge(kb, s1); edge(s1, o3); edge(o3, d1, "read"); edge(er, d1); edge(d1, o4); edge(pb, d1, dashed=True); edge(o4, r2)
# C
box(15, 865, 1510, 95, "C. Diagnostic only (not on the ranking path)", BAND)
box(30, 895, 790, 55, "<b>Physical model</b>, tiers 1 and 2 (lumped.py, spatial.py): Sy(z) dz/dt = R − C(z)(z − z<sub>c</sub>) and 2D Boussinesq; DTM, peat depth, canals by class. Explains why observed water tables are held (supply from outside the rain balance); per-sub-KHG skill 0, frozen.", DIA)
box(900, 895, 610, 55, "Retired 2026-10-26: bucket model fitted to SiTMAT (failed spatial skill check); record in docs/bucket_reports/. Not used: TerraClimate (ends 2024-12; only to reproduce 2021), runoff C 0.25 / 0.35 of the 2021 scripts.", DIA)

xml = ('<mxfile host="repeat-neraca"><diagram id="neraca" name="Neraca air method"><mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" '
       'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1560" pageHeight="980" background="#ffffff" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>\n")
out = Path(__file__).with_name("neraca_method.drawio")
out.write_text(xml, encoding="utf-8")
print(f"wrote {out} ({len(cells)} cells)")
