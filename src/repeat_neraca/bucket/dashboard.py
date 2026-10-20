#!/usr/bin/env python3
"""Build the HTML page that explains neraca air and shows how it did against the SiTMAT stations.

  python -m repeat_neraca.bucket.dashboard --neraca-config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml --out docs/neraca_air_process.html

One self-contained file: the mechanism of the water-table bucket, the process with its skill check (coloured by the verdict
of the run), the seasonal curve of observed and simulated water table, skill on stations that were left out of the fit
against the no-skill baseline, which covariates explain the stations, and a map of the stations next to the sub-KHG outputs.
Every number comes from the output folder of `repeat_neraca.bucket.run` (and `repeat_neraca.bucket.covariates`).
"""
from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from repeat_common import htmlkit as K
from .config import load_config
from repeat_neraca.bucket.run import PRESET as NERACA_PRESET

OUTPUTS = [
    ("u_wb_daily_mean", "P - E, mean over the dry months (mm/day)"),
    ("u_deficit_months_dry", "Dry months with a negative balance (0-5)"),
    ("u_dry_days_mean", "Mean length of dry runs (days)"),
    ("u_storage_decline_pct", "Storage decline (% of the peat column)"),
    ("u_wt_peak_cm", "Simulated deepest water table (cm)"),
    ("u_wt_days_gt40", "Share of days deeper than 40 cm"),
    ("u_mean_peat_depth_cm", "Mean peat depth (cm)"),
    ("canal_proximity", "Canal proximity (0-1)"),
]
ST_VARS = [("obs_peak_cm", "Observed peak depth (cm)"), ("sim_peak_cm", "Simulated peak depth, held out (cm)"),
           ("resid_cm", "Simulated minus observed (cm)"), ("peat_depth_cm", "Peat depth at the station (cm)"),
           ("canal_dist_m", "Distance to a canal (m)"), ("obs_days_gt40", "Observed share of days deeper than 40 cm"),
           ("dist_khg_edge_m", "Distance to the KHG edge (m)"), ("elev_m", "Elevation (m)")]


def _rho(a, b):
    a, b = pd.Series(a, dtype=float), pd.Series(b, dtype=float)
    ok = a.notna() & b.notna()
    if ok.sum() < 8 or a[ok].nunique() < 2 or b[ok].nunique() < 2:
        return None
    return round(float(spearmanr(a[ok], b[ok]).correlation), 2)


def build(neraca_config: str, out: str) -> None:
    nc = load_config(neraca_config, NERACA_PRESET, "neraca")
    od = Path(nc["out"])
    rep = json.load(open(od / "neraca_report.json", encoding="utf-8"))
    k = rep["khg"][0]
    cal = k["calibration"]
    v = cal["verdict"]
    cfg_n = rep["config"]
    kid = k["khg_id"]
    chosen = cal["with_drainage"] if cal["drainage_kept"] else cal["without_drainage"]
    fit = cal["fitted"]

    units = gpd.read_file(nc["units"]["path"]).to_crs(4326)
    nu = pd.read_csv(od / "neraca_unit.csv")
    units = units.merge(nu, on=["unit_id"], how="left", suffixes=("", "_n"))
    ucols = ["unit_id"] + [c for c, _ in OUTPUTS if c in units.columns] + ["neraca_skill_ok"]
    U = K.pack_polygons(units, [c for c in ucols if c in units.columns])
    outs = [{"key": c, "label": l} for c, l in OUTPUTS if c in units.columns and units[c].nunique() > 1]

    khg = gpd.read_file(nc["khg"]).to_crs(4326)
    geo = {"khg": K._rings(khg.geometry.union_all(), 0.0008)}
    if nc["vectors"].get("canals"):
        cn = gpd.read_file(nc["vectors"]["canals"]).to_crs(4326)
        f = nc["params"].get("ipg_canal_class_field")
        geo["canals"] = K.pack_lines(cn, f, {"Kanal Tersier": 3, "Kanal Sekunder": 2, "Kanal Primer": 1})
    cov_path = od / "neraca_station_covariates.csv"
    st = pd.read_csv(cov_path if cov_path.exists() else od / "neraca_stations.csv")
    st["resid_cm"] = st["sim_peak_cm"] - st["obs_peak_cm"]
    sv = [(c, l) for c, l in ST_VARS if c in st.columns]
    stations = []
    for r in st.itertuples():
        p = {c: (None if pd.isna(getattr(r, c)) else round(float(getattr(r, c)), 3)) for c, _ in sv}
        p["block"] = int(r.block)
        stations.append({"x": round(r.lon, 4), "y": round(r.lat, 4), "id": r.station_id, "p": p})
    series = pd.read_csv(od / "neraca_series.csv")
    series["i"] = np.arange(len(series))
    ser = {"i": series["i"].tolist(), "date": series["date"].tolist(), "obs": series["obs_mean_cm"].round(1).tolist(),
           "p10": series["obs_p10_cm"].round(1).tolist(), "p90": series["obs_p90_cm"].round(1).tolist(), "sim": series["sim_mean_cm"].round(1).tolist(),
           "n": series["n_stations_observed"].tolist()}
    covs = []
    if cov_path.exists():
        for c in [c for c in st.columns if c not in ("station_id", "lon", "lat", "obs_peak_cm", "sim_peak_cm", "obs_days_gt40", "sim_days_gt40", "block", "resid_cm")]:
            covs.append({"label": c, "peak": _rho(st[c], st["obs_peak_cm"]), "days": _rho(st[c], st["obs_days_gt40"])})
    model_rho = {"peak": _rho(st["sim_peak_cm"], st["obs_peak_cm"]), "days": _rho(st["sim_days_gt40"], st["obs_days_gt40"])}
    b = khg.total_bounds
    sy_max, k_max, z_max = max(cfg_n["sy_grid"]), max(cfg_n["k_grid"]), max(cfg_n["z0_grid"])
    params = [("Sy (mm of deficit per 10 cm of fall)", fit["sy"], max(cfg_n["sy_grid"]), min(cfg_n["sy_grid"]), "physical values are below about 0.5"),
              ("k (drainage, mm/day at full canal proximity)", fit["k"], k_max, min(cfg_n["k_grid"]), ""),
              ("z0 (starting depth, cm)", fit["z0"], z_max, min(cfg_n["z0_grid"]), "")]
    n_st = cal["n_stations"]
    ok = bool(v["usable_for_ranking"])

    # ---- diagrams
    mech_nodes = {
        "P": dict(x=20, y=20, w=200, h=64, title="Rain P", lines=["ERA5, mm per local day", "all 24 hours summed"], kind="cloud"),
        "E": dict(x=20, y=110, w=200, h=64, title="Evaporation E", lines=["ERA5, mm per local day", "every 3rd hour, scaled"], kind="cloud"),
        "D": dict(x=20, y=200, w=200, h=64, title="Drainage loss k x c", lines=["k fitted, mm/day", "c = exp(-distance to canal / 300 m)"], kind="input"),
        "Z": dict(x=330, y=80, w=270, h=110, title="Water table depth z (cm below surface)", lines=["z = max( z - (P - E - k c) / (10 Sy), 0 )", "starts at z0 on 1 April; no peat-depth cap", "Sy: fitted, effective, absorbs drainage"], kind="proc"),
        "O": dict(x=710, y=80, w=220, h=110, title="Six outputs per sub-KHG", lines=["Jun-Oct: P - E, deficit months,", "dry days, storage decline,", "peak depth, days deeper than 40 cm"], kind="out"),
    }
    mech_edges = [("P", "Z", "adds water", {"dyt": -22}), ("E", "Z", "removes water"), ("D", "Z", "removes water", {"dyt": 22}), ("Z", "O", "dry months only")]
    mech = K.flow_svg(mech_nodes, mech_edges, 950, 290, "A water-table bucket: rain adds water, evaporation and drainage remove it, and the water table depth follows; six outputs are taken over the dry months")

    gk = "gatefail" if not ok else "gate"
    nodes = {
        "i_era5": dict(x=20, y=150, w=205, h=64, title="ERA5 hourly", lines=["rain, evaporation, 0.25 deg", "ARCO Zarr, read in windows"], kind="cloud"),
        "i_units": dict(x=20, y=40, w=205, h=60, title="Sub-KHG polygons", lines=[f"{len(units)} units", "from the delineation"], kind="input"),
        "i_peat": dict(x=20, y=250, w=205, h=64, title="Peat depth, canals", lines=["raster in cm (floor 50 cm)", "canal distance -> proximity"], kind="input"),
        "i_sit": dict(x=20, y=340, w=205, h=64, title="SiTMAT stations", lines=[f"{n_st} inside the KHG", "daily water table, 2026"], kind="input"),
        "p_force": dict(x=315, y=150, w=215, h=80, title="Forcing", lines=["hourly to local days (WIB)", "cached per window", "last valid ERA5 day checked"], kind="proc"),
        "p_w": dict(x=605, y=40, w=215, h=80, title="Cell weights", lines=["ERA5 cell to sub-KHG,", "weighted by pixel count"], kind="proc"),
        "p_cal": dict(x=605, y=340, w=215, h=92, title="Calibrate", lines=["grid search of Sy, k, z0", f"leave one of {cal['with_drainage']['blocks']} blocks out", "drainage kept only if it helps"], kind="proc"),
        "p_run": dict(x=895, y=190, w=215, h=92, title="Run the bucket", lines=["per sub-KHG and year", f"years {', '.join(str(y) for y in cfg_n['years'])}", "Apr-Oct; indicators Jun-Oct"], kind="proc"),
        "gate": dict(x=895, y=340, w=215, h=92, title="Skill check" + ("" if ok else ": FAILED"), lines=[f"spatial rho >= {cfg_n['min_spatial_skill']} and", "RMSE below the baseline", "on held-out stations"], kind=gk),
        "o_csv": dict(x=1185, y=100, w=195, h=64, title="neraca_unit.csv", lines=["6 outputs per sub-KHG", "+ neraca_skill_ok"], kind="out"),
        "o_rep": dict(x=1185, y=210, w=195, h=64, title="neraca_report.json", lines=["parameters, skill, verdict", "spread across sub-KHG"], kind="out"),
        "o_st": dict(x=1185, y=320, w=195, h=64, title="neraca_stations.csv", lines=["observed vs simulated", "peak depth per station"], kind="out"),
        "c_rank": dict(x=1185, y=430, w=195, h=70, title="Sub-KHG ranking", lines=["via extra_indicators", "no weight in the need score" if not ok else "may be given a weight"], kind="proc"),
    }
    edges = [
        ("i_era5", "p_force", "hourly P, E"),
        ("i_units", "p_w", "polygons", {"ly": -6}),
        ("p_force", "p_w", "daily P, E per cell", {"from": "t", "to": "l", "dyt": 0}),
        ("p_force", "p_cal", "P - E at stations", {"dyt": -20, "lx": -34, "ly": 44}),
        ("p_w", "p_run", "P, E per sub-KHG", {"dyt": -22}),
        ("i_peat", "p_run", "depth, proximity", {"dyt": 22}),
        ("i_sit", "p_cal", "observed depth"),
        ("p_cal", "p_run", "Sy, k, z0", {"dyf": -20, "dyt": 20}),
        ("p_cal", "gate", "held-out skill", {"dyf": 10, "dyt": 10}),
        ("p_run", "o_csv", "6 outputs", {"dyt": 10}),
        ("gate", "o_rep", "verdict", {"dyf": -22}),
        ("gate", "o_st", "per station", {"dyf": -8}),
        ("gate", "c_rank", "pass: weight allowed" if ok else "fail: no weight", {"dyf": 14}),
    ]
    lanes = [(10, 225, "Inputs"), (300, 245, "Forcing"), (590, 245, "Weights, calibration"), (880, 245, "Run, check"), (1170, 225, "Outputs")]
    flow = K.flow_svg(nodes, edges, 1400, 480,
                      "ERA5 forcing and sub-KHG polygons feed the bucket run; stations feed the calibration; the skill check on held-out stations decides whether the outputs may be used in the ranking", lanes)

    details = {
        "i_era5": {"title": "ERA5 hourly rain and evaporation", "body": ["Google ARCO-ERA5 (public Zarr, no account). One hour of the whole globe is one chunk, so an hour costs about 0.3 s whatever the window; a year of April to October takes 11 to 33 minutes.", "Coarse: 0.25 degrees, about 25 km. The KHG spans a handful of cells, so P - E barely differs between sub-KHG."]},
        "i_units": {"title": "Sub-KHG polygons", "body": ["The units from <code>repeat_delineation</code>; weights between ERA5 cells and each sub-KHG come from pixel counts on the 30 m grid."]},
        "i_peat": {"title": "Peat depth and canals", "body": ["Peat depth enters only the storage decline (the share of the peat column the water table has left); the raster has a floor at 50 cm, so thin peat is not resolved.", "Distance to the nearest canal gives the proximity <code>c = exp(-d / 300 m)</code> used by the drainage term."]},
        "i_sit": {"title": "SiTMAT stations", "body": [f"{n_st} concession stations inside the KHG with at least 50% coverage, 2026-04-01 to {cal['period'][1]}. Flagged readings dropped.", "One season only, and mostly inside concessions: where weirs hold the water table near the 40 cm limit."]},
        "p_force": {"title": "Forcing (repeat_common/forcing.py)", "body": ["Hourly accumulations are summed to local days (WIB, UTC+7). A day with any missing hour is empty. ERA5 is complete only to about 5 days before today, so the calibration window ends at the last valid day.", "Cached per window under <code>cache/&lt;khg&gt;/neraca/</code>: <code>repeat_neraca.bucket.run --forcing-only</code> reads them once."]},
        "p_w": {"title": "Cell weights", "body": ["Each 30 m pixel is assigned to the ERA5 cell it lies in; a sub-KHG's P and E are the pixel-count weighted mean of its cells."]},
        "p_cal": {"title": "Calibrate (repeat_neraca/bucket/calibrate.py)", "body": [f"Grid search of Sy, k and z0 minimising the pooled RMSE on the stations. Scored with leave-one-spatial-block-out ({cal['with_drainage']['blocks']} blocks of stations): fit on three blocks, score on the fourth.",
                                                                               f"Fitted on all stations: Sy {fit['sy']}, k {fit['k']} mm/day, z0 {fit['z0']} cm (see the table below: a value at the edge of its grid means the fit wanted more).",
                                                                               "Drainage is kept only if the out-of-fold RMSE improves by 2% and spatial skill does not drop." + (" Kept here." if cal["drainage_kept"] else " Dropped here.")]},
        "p_run": {"title": "Run the bucket (repeat_neraca/bucket/model.py)", "body": ["For each sub-KHG and each baseline year the bucket is run from 1 April; the six outputs are taken over June to October and averaged over the years.", "No forest or interception term: such terms made forested units look drier in this program and cancelled the forest indicator."]},
        "gate": {"title": "Skill check", "body": [f"Usable only if the spatial Spearman across held-out stations is at least {cfg_n['min_spatial_skill']} (peak depth or days deeper than 40 cm) and the out-of-fold RMSE is below the no-skill baseline.",
                                               f"This run: spatial rho {v['spatial_spearman_peak']:.2f} (peak) and {v['spatial_spearman_days_gt40']:.2f} (days > 40 cm); RMSE {chosen['rmse_cm']:.1f} cm against a baseline of {chosen['rmse_baseline_cm']:.1f} cm. " + ("Passed." if ok else "<b>Failed: " + v["reason"] + ".</b>")]},
        "o_csv": {"title": "neraca_unit.csv", "body": ["One row per sub-KHG: the six outputs, mean peat depth, canal proximity and <code>neraca_skill_ok</code> (0 = failed, 1 = passed). Merged into a ranking run through <code>extra_indicators</code>."]},
        "o_rep": {"title": "neraca_report.json", "body": ["Fitted parameters, skill with and without drainage, the verdict, covariates alone, and the spread of each output across the sub-KHG with its Spearman against peat depth and canal proximity."]},
        "o_st": {"title": "neraca_stations.csv", "body": ["Per station: location, peat depth, canal distance, observed and simulated peak depth, days deeper than 40 cm, and the block it was held out in."]},
        "c_rank": {"title": "Sub-KHG ranking", "body": ["The columns are merged by unit id. They only count in the need score if given a weight; the rank-sum method can read them through <code>scoring.ranksum_columns</code>.", "Here they have no weight because of the skill check."]},
    }

    spread = k["spread_across_sub_khg"]
    sections = f"""
<section id="mechanism"><h2>The mechanism</h2>
<p class="lede">Neraca air here is a daily water-table bucket per sub-KHG: rain adds water, evaporation and drainage remove it, and the depth of the water table follows. It is a definition we made from the data we can get, not a copy of an earlier method.</p>
<div class="card"><figure>{mech}<figcaption>The bucket. Dashed boxes come from ERA5. Sy is not looked up: it is fitted to the stations, so it is an effective value that absorbs drainage and local effects.</figcaption></figure></div></section>

<section id="process"><h2>The process</h2>
<p class="lede">From ERA5 and the stations to six outputs per sub-KHG, with a skill check before anyone may use them. Click a box for details.</p>
<div class="card"><figure>{flow}<figcaption>The red (or green) box is the gate: its colour is the verdict of this run. The outputs are written either way, flagged by <code>neraca_skill_ok</code>.</figcaption></figure>
<div id="node-detail"><p>Click a box.</p></div>
<div class="legend-row"><span><i class="sw"></i>local file</span><span><i class="sw d"></i>read from the cloud</span><span><i class="sw p"></i>processing step</span><span><i class="sw o"></i>output</span><span><i class="sw {'g' if ok else 'f'}"></i>skill check</span></div></div></section>

<section id="skill"><h2>How it did against the stations</h2>
<p class="lede">{n_st} SiTMAT stations, {cal['period'][0]} to {cal['period'][1]}, scored on stations in spatial blocks that were left out of the fit. <span class="badge {'good' if ok else 'bad'}">{'usable for ranking' if ok else 'not usable for ranking'}</span></p>
<div class="card chart" id="ch-series"></div>
<div class="grid2" style="margin-top:14px"><div class="card chart" id="ch-skill"></div><div class="card chart" id="ch-peak"></div></div>
<div class="grid2" style="margin-top:14px"><div class="card chart" id="ch-cov"></div><div class="card"><h3 style="margin:0 0 6px;font-size:15px">Fitted parameters against their search grids</h3><div id="params"></div>
<p style="color:var(--muted);font-size:13px">A fitted value at the top of its grid means the best bucket wanted even more. Sy of {fit['sy']} would mean 10 mm of deficit lowers the table by {10 / fit['sy']:.1f} mm: a nearly flat line, not a physical peat.</p></div></div></section>

<section id="map"><h2>Stations and sub-KHG on a map</h2>
<p class="lede">Colour the stations by what was observed or simulated, and the sub-KHG by a neraca air output. Scroll to zoom, drag to pan, double-click to reset.</p>
<div class="controls"><label>Stations <select id="svar"></select></label><label>Sub-KHG <select id="uvar"></select></label>
<label><input type="checkbox" id="ov-canals"> canals</label><label><input type="checkbox" id="ov-st" checked> stations</label><button type="button" id="reset">Reset view</button></div>
<div class="maprow"><div class="mapbox"><canvas class="map" id="map-canvas" role="img" aria-label="Map of the water-table stations and the sub-KHG coloured by a neraca air output"></canvas>
<div class="legend" id="legend"></div><div class="legend" id="legend2" style="left:auto;right:12px;bottom:12px"></div></div>
<aside class="card side" id="panel"><h3>Station</h3><p style="color:var(--muted);margin:0">Click a station or a sub-KHG.</p></aside></div></section>

<section id="outputs"><h2>The six outputs across the sub-KHG</h2>
<p class="lede">An output is only useful for ranking if it differs between sub-KHG for a hydrological reason. Two of these are close to rescaled covariates.</p>
<div class="card"><div class="tablewrap" id="spread"></div></div></section>
"""
    data = {"units": U, "outs": outs, "geo": geo, "stations": stations, "stvars": [{"key": c, "label": l} for c, l in sv], "bounds": [float(b[0]), float(b[1]), float(b[2]), float(b[3])],
            "series": ser, "covs": covs, "model_rho": model_rho, "details": details, "ok": ok, "threshold": cfg_n["min_spatial_skill"],
            "skill": {"rmse": chosen["rmse_cm"], "base": chosen["rmse_baseline_cm"], "rho_peak": chosen["spatial_spearman_peak"], "rho_days": chosen["spatial_spearman_days_gt40"],
                      "peak_rmse": chosen["peak_rmse_cm"], "peak_base": chosen["peak_rmse_baseline_cm"], "r_med": chosen["temporal_r_median"]},
            "params": [{"name": a, "value": b_, "max": c, "min": d, "note": e} for a, b_, c, d, e in params],
            "spread": [{"key": c, "label": dict(OUTPUTS).get(c, c), **s} for c, s in spread.items()]}
    facts = [("KHG", kid), ("Stations", str(n_st)), ("Sub-KHG", str(len(units))), ("Baseline years", ", ".join(str(y) for y in cfg_n["years"])),
             ("Verdict", "not usable" if not ok else "usable"), ("Generated", str(datetime.date.today()))]
    foot = (f"Generated by <code>python -m repeat_neraca.bucket.dashboard --neraca-config {neraca_config}</code> on {datetime.date.today()} from <code>{od}</code>. "
            f"Definition: <code>docs/bucket_experiments_README.md</code>. Steps and decisions: <code>re-peat/sites/{Path(neraca_config).parent.name}/README.md</code>.")
    html_ = K.page("Neraca air", "A daily water-table bucket per sub-KHG, fitted to water-table stations, with a skill check on stations it was not fitted on.", facts,
                   [("mechanism", "Mechanism"), ("process", "Process"), ("skill", "Skill"), ("map", "Map"), ("outputs", "Outputs")], sections, data, SCRIPT, foot)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(html_, encoding="utf-8")
    print(f"written {out} ({len(html_) / 1e6:.1f} MB)")


SCRIPT = r"""
wireFlow(DATA.details);
const U=DATA.units,ST=DATA.stations,GEO=DATA.geo,SK=DATA.skill;
// ---- seasonal curve
(function(){const s=DATA.series,mon=['Apr','May','Jun','Jul','Aug','Sep','Oct'];const xt=[];s.date.forEach((d,i)=>{if(d.slice(8)==='01')xt.push([i,mon[+d.slice(5,7)-4]||d.slice(5,7)])});
  chartSeries($('#ch-series'),[{name:'observed: mean of stations (band: 10th to 90th percentile)',pts:s.i.map((i,k)=>[i,s.obs[k]]),band:s.i.map((i,k)=>[i,s.p10[k],s.p90[k]]),color:'var(--fg)'},
    {name:'simulated, held-out stations',pts:s.i.map((i,k)=>[i,s.sim[k]]),color:'var(--orange)'}],
    {title:'Water table depth through the season (deeper is lower on the chart)',yl:'depth below surface, cm',xticks:xt,refs:[{v:40,label:'40 cm limit'}],xlabel:i=>s.date[i],h:340});
  const t=document.createElement('div');tableView(t,['date','stations observed','observed mean cm','p10','p90','simulated mean cm'],s.i.filter(i=>i%7===0).map(i=>[s.date[i],s.n[i],s.obs[i],s.p10[i],s.p90[i],s.sim[i]]));$('#ch-series').appendChild(t)})();
// ---- skill bars
(function(){const rows=[{label:'model, held out',value:SK.rmse,fill:'var(--orange)',tip:'model RMSE '+fmt(SK.rmse,1)+' cm'},{label:'no-skill baseline',value:SK.base,fill:'var(--blue)',tip:'baseline RMSE '+fmt(SK.base,1)+' cm'}];
  chartBars($('#ch-skill'),rows,{title:'Error of the daily series, cm (lower is better)',ml:120,lo:0,w:520});
  const r2=[{label:'peak depth',value:SK.rho_peak??0,fill:'var(--orange)',tip:'Spearman '+fmt(SK.rho_peak,2)},{label:'days deeper than 40 cm',value:SK.rho_days??0,fill:'var(--orange)',tip:'Spearman '+fmt(SK.rho_days,2)}];
  const d=document.createElement('div');d.innerHTML='<div id="b2" style="margin-top:8px"></div>';$('#ch-skill').appendChild(d);
  chartBars($('#b2'),r2,{title:'Spatial skill across held-out stations (Spearman; the line is the threshold)',ml:150,lo:-.5,hi:1,refs:[{v:DATA.threshold,label:'needs '+DATA.threshold}],w:520});
  const t=document.createElement('div');tableView(t,['measure','value'],[['model RMSE, cm',fmt(SK.rmse,1)],['baseline RMSE, cm',fmt(SK.base,1)],['spatial Spearman, peak depth',fmt(SK.rho_peak,2)],['spatial Spearman, days > 40 cm',fmt(SK.rho_days,2)],['temporal r, median over stations',fmt(SK.r_med,2)]]);$('#ch-skill').appendChild(t)})();
// ---- peak depth scatter
(function(){const pts=ST.filter(s=>s.p.obs_peak_cm!=null&&s.p.sim_peak_cm!=null).map(s=>({x:s.p.obs_peak_cm,y:s.p.sim_peak_cm,tip:'<b>'+esc(s.id)+'</b><br>observed '+fmt(s.p.obs_peak_cm,0)+' cm<br>simulated '+fmt(s.p.sim_peak_cm,0)+' cm<br>block '+s.p.block}));
  const hi=Math.max(...pts.map(p=>Math.max(p.x,p.y)))*1.05;
  chartScatter($('#ch-peak'),pts,{title:'Which stations are deepest (each dot a station; dashed = perfect)',xl:'observed peak depth (95th percentile), cm',yl:'simulated, held-out, cm',x0:0,x1:hi,y0:0,y1:hi,lines:[[0,0,hi,hi]],h:380});
  const t=document.createElement('div');tableView(t,['station','observed peak cm','simulated peak cm','block'],ST.map(s=>[s.id,s.p.obs_peak_cm,s.p.sim_peak_cm,s.p.block]));$('#ch-peak').appendChild(t)})();
// ---- covariates
(function(){if(!DATA.covs.length){$('#ch-cov').innerHTML='<p style="color:var(--muted)">Run <code>repeat_neraca.bucket.covariates</code> to add this chart.</p>';return}
  const rows=DATA.covs.map(c=>({label:c.label,value:c.peak??0,fill:'var(--blue)',tip:'<b>'+esc(c.label)+'</b><br>Spearman with observed peak depth '+fmt(c.peak,2)+'<br>with days deeper than 40 cm '+fmt(c.days,2)}));
  rows.push({label:'the model (held out)',value:DATA.model_rho.peak??0,fill:'var(--orange)',tip:'Spearman of the simulated with the observed peak '+fmt(DATA.model_rho.peak,2)});
  chartBars($('#ch-cov'),rows,{title:'What explains the observed peak depth? (Spearman, one bar per covariate)',ml:150,lo:-1,hi:1,rh:22,w:520});
  const t=document.createElement('div');tableView(t,['covariate','Spearman, peak depth','Spearman, days > 40 cm'],DATA.covs.map(c=>[c.label,c.peak,c.days]));$('#ch-cov').appendChild(t)})();
(function(){$('#params').innerHTML='<table class="data"><thead><tr><th>parameter</th><th>fitted</th><th>grid</th><th></th></tr></thead><tbody>'+DATA.params.map(p=>{const edge=p.value>=p.max;return'<tr><td style="text-align:left">'+esc(p.name)+'</td><td>'+fmt(p.value,2)+'</td><td>'+fmt(p.min,2)+' to '+fmt(p.max,2)+'</td><td>'+(edge?'<span class="badge bad">at the edge</span>':'<span class="badge good">inside</span>')+'</td></tr>'}).join('')+'</tbody></table>'})();
// ---- spread table
(function(){const rows=DATA.spread.map(s=>'<tr><td style="text-align:left">'+esc(s.label)+'</td><td>'+fmt(s.min,2)+'</td><td>'+fmt(s.median,2)+'</td><td>'+fmt(s.max,2)+'</td><td>'+fmt(s.spearman_with_peat_depth,2)+'</td><td>'+fmt(s.spearman_with_canal_proximity,2)+'</td></tr>').join('');
  $('#spread').innerHTML='<table class="data"><thead><tr><th>output</th><th>min</th><th>median</th><th>max</th><th>Spearman with mean peat depth</th><th>Spearman with canal proximity</th></tr></thead><tbody>'+rows+'</tbody></table><p style="color:var(--muted);font-size:13px">Close to -1 or 1 means the output is mostly the covariate rescaled.</p>'})();
// ---- map
const cv=$('#map-canvas'),map=new MapView(cv,DATA.bounds),L1=$('#legend'),L2=$('#legend2');
const uvar=$('#uvar'),svar=$('#svar');
const none=document.createElement('option');none.value='';none.textContent='none';uvar.appendChild(none);
DATA.outs.forEach(o=>{const e=document.createElement('option');e.value=o.key;e.textContent=o.label;uvar.appendChild(e)});uvar.value=DATA.outs.length?DATA.outs.find(o=>o.key==='u_storage_decline_pct')?'u_storage_decline_pct':DATA.outs[0].key:'';
DATA.stvars.forEach(o=>{const e=document.createElement('option');e.value=o.key;e.textContent=o.label;svar.appendChild(e)});svar.value='obs_peak_cm';
const rg=(arr)=>{const a=arr.filter(v=>v!=null);return[Math.min(...a),Math.max(...a)]};
let ur=null,sr=null;
const ufill=it=>{const k=uvar.value;if(!k)return css('--surface');const v=it.p[k];if(v==null)return css('--grid');const t=(v-ur[0])/((ur[1]-ur[0])||1);return ramp(t)};
const sfill=it=>{const k=svar.value,v=it.p[k];if(v==null)return css('--grid');if(k==='resid_cm'){const m=Math.max(Math.abs(sr[0]),Math.abs(sr[1]));return div(v/m)}return rampO((v-sr[0])/((sr[1]-sr[0])||1))};
map.addLayer({id:'units',type:'poly',items:U,pickable:true,selectable:true,style:it=>({fill:ufill(it),stroke:css('--axis'),lw:1})});
const canalL=GEO.canals?map.addLayer({id:'canals',type:'line',visible:false,items:GEO.canals.map(c=>({pts:c[1],k:c[0]})),style:it=>({lw:it.k===1?1.6:it.k===2?.9:.4,stroke:it.k===3?css('--axis'):css('--faint')})}):null;
map.addLayer({id:'khg',type:'poly',items:[{polys:GEO.khg,p:{}}],style:()=>({fill:null,stroke:css('--fg'),lw:1.2})});
const stL=map.addLayer({id:'stations',type:'point',pickable:true,selectable:true,items:ST.map(s=>({x:s.x,y:s.y,id:s.id,p:s.p})),style:it=>({r:5.5,fill:sfill(it),stroke:css('--fg'),ring:1})});
function refresh(){ur=uvar.value?rg(U.map(u=>u.p[uvar.value])):[0,1];sr=rg(ST.map(s=>s.p[svar.value]));
  const uo=DATA.outs.find(o=>o.key===uvar.value);
  if(uvar.value){legendCont(L1,'Sub-KHG: '+uo.label+(DATA.ok?'':' (failed skill check)'),ur[0],ur[1],v=>fmt(v,2),false)}else L1.innerHTML='<div>Sub-KHG: none</div>';
  const so=DATA.stvars.find(o=>o.key===svar.value);
  if(svar.value==='resid_cm'){const m=Math.max(Math.abs(sr[0]),Math.abs(sr[1]));legendCont(L2,'Stations: '+so.label,-m,m,v=>fmt(v,0),false,true)}else legendCont(L2,'Stations: '+so.label,sr[0],sr[1],v=>fmt(v,1),false,false,rampO);
  map.draw()}
[uvar,svar].forEach(e=>e.addEventListener('change',refresh));
$('#ov-canals').addEventListener('change',e=>{if(canalL){canalL.visible=e.target.checked;map.draw()}});if(!canalL)$('#ov-canals').parentElement.style.display='none';
$('#ov-st').addEventListener('change',e=>{stL.visible=e.target.checked;map.draw()});
$('#reset').addEventListener('click',()=>{map.view={k:1,x:0,y:0};map.draw()});
window.addEventListener('themechange',refresh);matchMedia('(prefers-color-scheme:dark)').addEventListener('change',refresh);
map.onhover=h=>{if(h.layer.id==='stations'){const p=h.item.p;return '<b>'+esc(h.item.id)+'</b><br>observed peak '+fmt(p.obs_peak_cm,0)+' cm<br>simulated '+fmt(p.sim_peak_cm,0)+' cm'}
  if(h.layer.id==='units'){const k=uvar.value;return '<b>'+esc(h.item.p.unit_id)+'</b>'+(k?'<br>'+esc(DATA.outs.find(o=>o.key===k).label)+': <b>'+fmt(h.item.p[k],2)+'</b>':'')}return null};
const panel=$('#panel');
map.onclick=h=>{if(!h){panel.innerHTML='<h3>Station</h3><p style="color:var(--muted);margin:0">Click a station or a sub-KHG.</p>';return}
  if(h.layer.id==='stations'){let r='';DATA.stvars.forEach(v=>{r+='<tr><td>'+esc(v.label)+'</td><td>'+fmt(h.item.p[v.key],1)+'</td></tr>'});r+='<tr><td>held-out block</td><td>'+h.item.p.block+'</td></tr>';panel.innerHTML='<h3>'+esc(h.item.id)+'</h3><table>'+r+'</table>'}
  else if(h.layer.id==='units'){let r='';DATA.outs.forEach(o=>{r+='<tr><td>'+esc(o.label)+'</td><td>'+fmt(h.item.p[o.key],2)+'</td></tr>'});panel.innerHTML='<h3>'+esc(h.item.p.unit_id)+'</h3><table>'+r+'</table><p style="color:var(--muted);font-size:12.5px">'+(h.item.p.neraca_skill_ok===0?'Failed the skill check: shown for reference.':'')+'</p>'}};
refresh();
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--neraca-config", required=True)
    ap.add_argument("--out", default="docs/neraca_air_process.html")
    a = ap.parse_args(argv)
    build(a.neraca_config, a.out)


if __name__ == "__main__":
    main()
