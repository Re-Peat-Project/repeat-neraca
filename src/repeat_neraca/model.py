"""Neraca air groundwater model of one KHG: daily water table on a grid, scored against field water-table points.

  repeat-neraca-model --khg 14.10.03 --dem deltadtm --start 2014-10-01 --end 2015-12-11 --peat-table tropical-small --drawdown 0.6
  repeat-neraca-model --khg 14.10.03 --dem deltadtm --start 2014-10-01 --end 2015-12-11 --drawdown primary=1.0,secondary=0.6,tertiary=none

Everything comes from the KHG work folder (`repeat_common.khg.folder`), so any KHG with the inputs runs the same way:
  00_inputs/khg.gpkg, canals.gpkg, peat_depth.tif         boundary, canals by class (KET_KANAL), peat depth (cm, scale from the hub's khg.yaml)
  DTM of the variant                                      lidar: the clip in khg.yaml; deltadtm, demnas: 01_dem/processed/<dem>/dtm_smooth.tif;
                                                          deltadtm without it: the raw clip 01_dem/inputs/deltadtm.tif (DeltaDTM is a
                                                          bare-earth product; the report says it was not corrected by repeat-dem)
  03_neraca/inputs/model/balance_<product>_dekad.csv      KHG-mean rain and ET per dekad (fetched from Earth Engine when missing or short)
  00_inputs/field_wtd.csv                                 optional: field water-table points (`repeat_neraca.groundwater.fieldobs`)

Rain and ET are dekad totals spread evenly over their days. The run starts saturated (`--h0`, m below the surface) on --start; use a wet
season start and a few months of spin-up before the window that is scored. Writes into 03_neraca/<dem>/runs/model/<run>/:
  model_series.csv      date, P_mm, ET_mm, mean_depth_cm, share_deeper_40cm, canal_in_mm, edge_in_mm (water the fixed cells put into the
                        peat per day, mm over the free cells; negative: drainage)
  model_depth_window.tif   mean water table depth (cm, positive down) over the field window; model_depth_end.tif: on the last day
  field_points.csv, field_scores.json, model_report.md, registry_snapshot.json, run_config.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from repeat_neraca.groundwater import PEAT_TABLES, PeatTable
from repeat_neraca.groundwater import fieldcheck as FC
from repeat_neraca.groundwater import fieldobs as FO
from repeat_neraca.groundwater import grid as G
from repeat_neraca.groundwater import simulate as SIM
from repeat_neraca.params import Registry

CLASSES = ("primary", "secondary", "tertiary")
LICENCES = "landstatus/ALL_Updade__IZIN_USAHA__PBPH_Perkebunan_HTRKM_Tambang__2025.gpkg"   # under REPEAT_DATA
MANAGED_LICENCES = ("PBPH", "Perkebunan Kelapa Sawit")
CANAL_NAMES = {"primary": ["Kanal Primer"], "secondary": ["Kanal Sekunder"], "tertiary": ["Kanal Tersier"]}


def hub_khg_yaml(kf: Path) -> dict:
    hub = Path(os.environ.get("REPEAT_HUB", kf.parents[1] / "re-peat"))
    p = hub / "sites" / kf.name / "khg.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def dtm_path(kf: Path, dem: str, kc: dict) -> tuple[Path, str]:
    """The DTM of a variant and a note on where it came from."""
    if dem == "lidar":
        clip = ((kc.get("dems") or {}).get("lidar") or {}).get("clip")
        p = Path(G.expand(clip)) if clip else None
        if p and p.is_file():
            return p, "LiDAR clip"
        raise SystemExit("no LiDAR clip for this KHG (khg.yaml dems.lidar.clip)")
    for p in (kf / "01_dem" / "processed" / dem / "dtm_smooth.tif", kf / "01_dem" / "benchmark" / "04_processed" / dem / "dtm_smooth.tif"):
        if p.is_file():
            return p, f"{dem} corrected by repeat-dem ({p.relative_to(kf)})"
    raw = kf / "01_dem" / "inputs" / f"{dem}.tif"
    if dem == "deltadtm" and raw.is_file():
        return raw, "DeltaDTM clip, not corrected by repeat-dem (DeltaDTM is itself a bare-earth product)"
    raise SystemExit(f"no DTM for variant {dem}: run repeat-dem first (01_dem/processed/{dem}/dtm_smooth.tif)")


def khg_config(kf: Path, dem: str) -> tuple[dict, dict]:
    kc = hub_khg_yaml(kf)
    inp = kf / "00_inputs"
    dtm, dtm_note = dtm_path(kf, dem, kc)
    field = (kc.get("canals") or {}).get("class_field", "KET_KANAL")
    units = next((p for p in (kf / "02_delineation" / dem / "subkhg_units.gpkg", kf / "02_delineation" / "subkhg_units.gpkg") if p.is_file()), None)
    cfg = {"name": kf.name, "khg": str(inp / "khg.gpkg"), "dtm": str(dtm),
           "peat_depth": {"path": str(inp / "peat_depth.tif"), "scale": float((kc.get("peat_depth") or {}).get("scale", 0.01))},
           "canals": {"path": str(inp / "canals.gpkg"), "class_field": field, "classes": CANAL_NAMES},
           "units": str(units) if units else None, "inputs_dir": str(kf / "03_neraca" / "inputs" / "none")}
    return cfg, {"dtm": dtm_note, "units": str(units.relative_to(kf)) if units else "none (KHG without sub-KHG units)"}


def forcing(kf: Path, start: str, end: str, rain: str, et: str, fetch: bool) -> pd.DataFrame:
    """Daily P and ET (mm) of the KHG from the dekad tables; fetched from Earth Engine (cached) when missing or not covering the period."""
    d = kf / "03_neraca" / "inputs" / "model"
    days = pd.date_range(start, pd.Timestamp(end) - pd.Timedelta(days=1))

    def daily(product):
        f = d / f"balance_{product}_dekad.csv"
        if not f.exists():
            return None
        t = pd.read_csv(f, parse_dates=["start", "end"])
        s = pd.Series(np.nan, index=days)
        for r in t.itertuples():
            if r.time_cov >= 0.999:
                s[(s.index >= r.start) & (s.index < r.end)] = r.mm / r.days
        return s

    out = {p: daily(p) for p in (rain, et)}
    if any(s is None or s.isna().any() for s in out.values()):
        if not fetch:
            raise SystemExit(f"forcing in {d} does not cover {start} to {end}; rerun with --fetch")
        from repeat_common import fetch_gee_balance as FG
        fs, fe = dekad_start(pd.Timestamp(start)).date().isoformat(), dekad_start(pd.Timestamp(end), up=True).date().isoformat()
        FG.main(["--khg", str(kf.name.split("_")[0]), "--whole-khg", "--products", f"{rain},{et}", "--start", fs, "--end", fe,
                 "--no-landcover", "--out", str(d), "--cache", str(kf / "cache" / "gee_balance_model")])
        out = {p: daily(p) for p in (rain, et)}
    return pd.DataFrame({"P_mm": out[rain], "ET_mm": out[et]})


def dekad_start(d: pd.Timestamp, up: bool = False) -> pd.Timestamp:
    """First day of the dekad (1st, 11th, 21st) holding d; with up, the first dekad start on or after d."""
    s = d.replace(day=21 if d.day >= 21 else 11 if d.day >= 11 else 1)
    if up and s < d:
        s = (s + pd.Timedelta(days=10)).replace(day=21) if s.day == 11 else (s + pd.Timedelta(days=10)).replace(day=11) if s.day == 1             else (s + pd.offsets.MonthBegin(1))
    return s


def parse_drawdown(text: str, default: float) -> dict:
    """'0.6' (every class), or 'primary=1.0,secondary=0.6,tertiary=none' (a class not named keeps `default`; none: not fixed)."""
    if "=" not in text:
        v = None if text.lower() == "none" else float(text)
        return {c: v for c in CLASSES}
    dd = {c: default for c in CLASSES}
    for part in text.split(","):
        k, v = part.split("=")
        dd[k.strip()] = None if v.strip().lower() == "none" else float(v)
    return dd


def licences(kf: Path):
    """The 2025 business-licence polygons of the KHG: `00_inputs/national/izin_usaha_2025.gpkg`, clipped from REPEAT_DATA on first use and
    listed in `00_inputs/local_manifest.csv`."""
    import geopandas as gpd
    from repeat_neraca.groundwater.fieldobs import write_manifest_row
    out = kf / "00_inputs" / "national" / "izin_usaha_2025.gpkg"
    if not out.exists():
        src = Path(os.environ["REPEAT_DATA"]) / LICENCES
        k = gpd.read_file(kf / "00_inputs" / "khg.gpkg").to_crs(4326)
        g = gpd.read_file(src, bbox=tuple(k.total_bounds))
        g = g[g.intersects(k.union_all())].clip(k)
        out.parent.mkdir(parents=True, exist_ok=True)
        g.to_file(out, driver="GPKG")
        write_manifest_row(kf, "national/izin_usaha_2025.gpkg", LICENCES, "business licences 2025 (IZIN_USAHA), clipped (repeat_neraca.model)", len(g))
    return gpd.read_file(out)


def managed_raster(kf: Path, khg, kinds) -> tuple[np.ndarray, dict]:
    from rasterio import features
    g = licences(kf)
    g = g[g["IZIN_USAHA"].isin(kinds)].to_crs(khg.crs)
    m = features.rasterize([(x, 1) for x in g.geometry if x is not None and not x.is_empty], out_shape=khg.shape, transform=khg.transform,
                           fill=0, dtype="uint8").astype(bool) if len(g) else np.zeros(khg.shape, bool)
    m &= khg.domain
    return m, {"managed_licences": list(kinds), "managed_share_of_khg": float(m[khg.domain].mean())}


def write_tif(path: Path, a: np.ndarray, khg) -> None:
    import rasterio
    with rasterio.open(path, "w", driver="GTiff", height=a.shape[0], width=a.shape[1], count=1, dtype="float32", crs=khg.crs,
                       transform=khg.transform, nodata=-9999.0, compress="deflate") as dst:
        dst.write(np.where(np.isfinite(a), a, -9999.0).astype("float32"), 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True, help="KHG name or code")
    ap.add_argument("--dem", default="deltadtm", choices=["lidar", "deltadtm", "demnas"])
    ap.add_argument("--start", required=True, help="first day (start saturated, in a wet season)")
    ap.add_argument("--end", required=True, help="exclusive")
    ap.add_argument("--res", type=float, default=100.0, help="grid cell, m")
    ap.add_argument("--peat-table", default="tropical-small", choices=list(PEAT_TABLES))
    ap.add_argument("--drawdown", default=None, help="canal level below the surface, m: one value, or per class (default: registry canal_drawdown)")
    ap.add_argument("--edge-stage", type=float, default=None, help="edge ring level below the surface, m (default: registry river_stage_below_edge)")
    ap.add_argument("--h0", type=float, default=0.0, help="initial water table below the surface, m")
    ap.add_argument("--rain", default="chirps")
    ap.add_argument("--et", default="mod16")
    ap.add_argument("--fetch", action="store_true", help="fetch missing forcing from Earth Engine")
    ap.add_argument("--drawdown-managed", default=None,
                    help="canal level below the surface (m) for canal cells in managed land (one value or per class); default: as --drawdown")
    ap.add_argument("--managed-licences", default=",".join(MANAGED_LICENCES),
                    help="IZIN_USAHA values of the licence layer that count as managed land (plantations with water management)")
    ap.add_argument("--et-stress", choices=["none", "drained", "natural"], default="none",
                    help="ET falls where the water table is deep (PEATCLSM-Trop): drained = registry et_stress_start/end, natural = -0.70/-1.82 m")
    ap.add_argument("--run", default=None, help="run folder name (default from the options)")
    a = ap.parse_args(argv)

    from repeat_common import khg as K
    kf = K.folder(a.khg)
    reg = Registry.load()
    dd = parse_drawdown(a.drawdown, float(reg["canal_drawdown"])) if a.drawdown else {c: float(reg["canal_drawdown"]) for c in CLASSES}
    edge = float(reg["river_stage_below_edge"]) if a.edge_stage is None else a.edge_stage
    tag = "_".join(f"{c[0]}{'x' if v is None else f'{v:g}'}" for c, v in dd.items())
    ddm = parse_drawdown(a.drawdown_managed, float(reg["canal_drawdown"])) if a.drawdown_managed else None
    if ddm:
        tag += "_m" + "_".join(f"{c[0]}{'x' if v is None else f'{v:g}'}" for c, v in ddm.items())
    run_name = a.run or f"{a.peat_table}_{tag}_e{edge:g}_{a.res:g}m" + ("" if a.et_stress == "none" else f"_et{a.et_stress}")
    out = kf / "03_neraca" / a.dem / "runs" / "model" / run_name
    out.mkdir(parents=True, exist_ok=True)
    log = lambda m: print(m, flush=True)

    cfg, notes = khg_config(kf, a.dem)
    khg = G.load(cfg, a.res)
    f = forcing(kf, a.start, a.end, a.rain, a.et, a.fetch)
    net = (f.P_mm - f.ET_mm).values / 1000.0
    dates = f.index

    fp = kf / "00_inputs" / "field_wtd.csv"
    pts = None
    if fp.exists():
        p = FO.read(fp)
        pts = on_grid(p[(p.on_peat == 1) & p.depth_cm.notna()], khg)
    sd = next((d for d in (kf / "03_neraca" / "inputs" / "model", kf / "03_neraca" / "inputs") if (d / "stations_daily.csv").exists()),
              kf / "03_neraca" / "inputs")             # the model's own station export (may include community stations), else the deficit's
    sp, sdp = sd / "stations.csv", sd / "stations_daily.csv"
    stn = on_grid(pd.read_csv(sp), khg) if sp.exists() and sdp.exists() else None
    window = np.zeros(len(dates), bool)
    if pts is not None and len(pts):
        window = (dates >= pd.Timestamp(pts.date_from.min())) & (dates <= pd.Timestamp(pts.date_to.max()))

    managed, mnotes = (None, {})
    if ddm:
        managed, mnotes = managed_raster(kf, khg, [s.strip() for s in a.managed_licences.split(",")])
    b = SIM.Boundary(dd, edge, managed, ddm)
    table = PeatTable.named(a.peat_table)
    log(f"{kf.name} {a.dem} {a.res:g} m, {khg.shape}, {len(dates)} days, peat table {a.peat_table}, drawdown {dd}, edge {edge:g} m")
    n_pts = 0 if pts is None else len(pts)
    rows = np.concatenate([[] if pts is None else pts.row.values, [] if stn is None else stn.row.values]).astype(int)
    cols = np.concatenate([[] if pts is None else pts.col.values, [] if stn is None else stn.col.values]).astype(int)
    stress = None if a.et_stress == "none" else ((-0.70, -1.82) if a.et_stress == "natural" else (float(reg["et_stress_start"]), float(reg["et_stress_end"])))
    r = SIM.run(khg, net, table, b, a.h0, points=(rows, cols) if len(rows) else None, keep_days=window, log=log,
                rain_m_day=f.P_mm.values / 1000.0, et_m_day=f.ET_mm.values / 1000.0, et_stress=stress)
    sampled = None if r["points"] is None else -100 * r["points"]          # days x samples, cm positive down

    s = r["series"]
    series = pd.DataFrame({"date": dates.date, "P_mm": f.P_mm.values, "ET_mm": f.ET_mm.values, "mean_depth_cm": -100 * s["mean_depth_m"],
                           "share_deeper_40cm": s["share_deeper_0_4"], "canal_in_mm": s["canal_in_mm"], "edge_in_mm": s["edge_in_mm"],
                           "et_share": s["et_share"]})
    series.to_csv(out / "model_series.csv", index=False, float_format="%.4f")
    write_tif(out / "model_depth_window.tif", -100 * r["window_mean_depth_m"], khg)
    write_tif(out / "model_depth_end.tif", -100 * r["final_depth_m"], khg)
    fixed_share = {lab: float((r["label"][khg.domain] == v).mean()) for lab, v in (("edge", 1), ("canal", 2))}
    if managed is not None:
        canal = r["label"] == 2
        mnotes["managed_share_of_canal_cells"] = float((canal & managed).sum() / max(canal.sum(), 1))

    scores, sens, brk = None, None, {}
    if pts is not None and len(pts):
        on_fixed = r["fixed"][pts.row, pts.col]
        sim_days = sampled[:, :n_pts]
        sim = np.array([np.nanmean(sim_days[(dates >= pd.Timestamp(a0)) & (dates <= pd.Timestamp(a1)), j])
                        for j, (a0, a1) in enumerate(zip(pts.date_from, pts.date_to))])
        pts = pts.assign(sim_cm=sim, obs_cm=pts.depth_cm, on_fixed=on_fixed, dist_m=FC.canal_distance(pts, cfg["canals"]["path"], khg.crs))
        pts.to_csv(out / "field_points.csv", index=False, float_format="%.2f")
        scored = pts[~pts.on_fixed].reset_index(drop=True)
        scores = FC.score(scored)
        scores["excluded"] = {"on_fixed_cell": int(pts.on_fixed.sum()), "outside_or_not_peat_or_no_depth": int(len(FO.read(fp)) - len(pts))}
        wd = dates[window]
        sens = FC.day_sensitivity(scored.obs_cm.values, sim_days[window][:, ~pts.on_fixed.values], wd)
        for by in ("dist_m", "drainage", "land_use", "status"):
            brk[by] = FC.breakdown(scored, by)
        (out / "field_scores.json").write_text(json.dumps(scores, indent=2, default=float), encoding="utf-8")
        sens.to_csv(out / "field_day_sensitivity.csv", index=False, float_format="%.3f")

    st_scores = None
    if stn is not None and len(stn):
        obs = pd.read_csv(sdp, parse_dates=["date"]).pivot(index="date", columns="station_id", values="depth_cm").reindex(dates)
        sim_st = pd.DataFrame(sampled[:, n_pts:], index=dates, columns=stn.station_id.values)
        on_fixed = r["fixed"][stn.row, stn.col]
        group = stn["concession"].fillna("(none)") if "concession" in stn else pd.Series("(none)", index=stn.index)
        info = stn.assign(group=group, dist_m=FC.canal_distance(stn, cfg["canals"]["path"], khg.crs),
                          flag=np.where(on_fixed, "on_fixed_cell", ""),
                          managed=managed[stn.row, stn.col] if managed is not None else False)
        keep = [c for c in obs.columns if c in set(info.station_id)]
        st_scores, st_table = FC.score_stations(obs[keep], sim_st[keep], info[["station_id", "group", "dist_m", "flag", "managed"]])
        g2 = st_table.assign(kind=np.where(st_table.group == "community", "community", "concession"))
        n_fixed = g2[g2.flag != ""].groupby("kind").size()
        g2 = g2[g2.flag == ""]                                  # a station on a canal or edge cell only shows the fixed canal level
        st_scores["by_kind"] = {k: {"n": int(len(v)), "on_fixed_cell": int(n_fixed.get(k, 0)), "obs_level_cm": float(v.obs_cm.median()),
                                    "sim_level_cm": float(v.sim_cm.median()),
                                    "obs_drawdown_cm": float(v.obs_drawdown_cm.median()), "sim_drawdown_cm": float(v.sim_drawdown_cm.median()),
                                    "in_managed_land": int(v.managed.sum())}
                                for k, v in g2.groupby("kind")}
        st_scores["excluded"] = {"on_fixed_cell": int(on_fixed.sum()), "outside_khg": int(len(pd.read_csv(sp)) - len(stn))}
        dfile = kf / "03_neraca" / "runs" / "deficit" / "neraca_khg.csv"
        if dfile.exists():
            dk = pd.read_csv(dfile).iloc[0]
            sel = (dates >= pd.Timestamp(dk.period_start)) & (dates <= pd.Timestamp(dk.period_end))
            st_scores["supply_check"] = {"period": f"{dk.period_start} to {dk.period_end}", "station_deficit_mm": float(dk.deficit_mm),
                                         "model_canal_in_mm": float(series.canal_in_mm[sel].sum()),
                                         "model_edge_in_mm": float(series.edge_in_mm[sel].sum())}
        st_table.to_csv(out / "station_scores.csv", index=False, float_format="%.2f")
        sim_st[keep].rename_axis("date").to_csv(out / "station_sim_daily.csv", float_format="%.1f")      # cm, positive down; rescoring needs no rerun
        (out / "station_scores.json").write_text(json.dumps(st_scores, indent=2, default=float), encoding="utf-8")

    snap = reg.snapshot()
    (out / "registry_snapshot.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
    run_cfg = {"khg": kf.name, "dem": a.dem, "res_m": a.res, "start": a.start, "end": a.end, "peat_table": a.peat_table, "drawdown": dd,
               "edge_stage": edge, "drawdown_managed": ddm, "h0": a.h0, "rain": a.rain, "et": a.et, "et_stress": stress, "inputs": cfg, "notes": {**notes, **khg.notes, **mnotes}}
    (out / "run_config.json").write_text(json.dumps(run_cfg, indent=2, default=str), encoding="utf-8")
    text = report(kf.name, a, run_cfg, series, window, fixed_share, scores, sens, brk, r["seconds"], snap["sha256"], st_scores)
    (out / "model_report.md").write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out}")


def on_grid(p: pd.DataFrame, khg) -> pd.DataFrame:
    """Points (lon, lat) with their grid row and col, kept when inside the KHG."""
    from pyproj import Transformer
    x, y = Transformer.from_crs(4326, khg.crs, always_xy=True).transform(p.lon.values, p.lat.values)
    p = p.assign(col=np.floor((x - khg.transform.c) / khg.dx).astype(int), row=np.floor((khg.transform.f - y) / khg.dx).astype(int))
    p = p[(p.row >= 0) & (p.row < khg.shape[0]) & (p.col >= 0) & (p.col < khg.shape[1])]
    return p[khg.domain[p.row, p.col]].reset_index(drop=True)


def md_table(t: pd.DataFrame) -> list[str]:
    cols = [t.index.name or ""] + list(t.columns)
    return ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)] + [
        "| " + " | ".join(map(str, [i, *r])) + " |" for i, r in zip(t.index, t.itertuples(index=False))]


def report(name, a, rc, series, window, fixed_share, scores, sens, brk, seconds, sha, st=None) -> str:
    w = series[window]
    L = [f"# Groundwater model, {name}, {a.dem}", "",
         f"Grid {a.res:g} m; peat table `{a.peat_table}`; canal level below the surface (m): "
         + ", ".join(f"{c} {'not fixed' if v is None else f'{v:g}'}" for c, v in rc["drawdown"].items())
         + ("" if not rc.get("drawdown_managed") else "; in managed land (" + ", ".join(rc["notes"]["managed_licences"]) + f", {rc['notes']['managed_share_of_khg']:.0%} of the KHG, "
            f"{rc['notes'].get('managed_share_of_canal_cells', 0):.0%} of the canal cells): "
            + ", ".join(f"{c} {'not fixed' if v is None else f'{v:g}'}" for c, v in rc["drawdown_managed"].items()))
         + f"; edge ring {rc['edge_stage']:g} m below the surface; start {a.start} saturated ({a.h0:g} m), end {a.end}. "
         f"Rain {a.rain}, ET {a.et}, KHG mean, dekad totals spread evenly over their days; ET reduction with depth: "
         + ("none" if not rc.get("et_stress") else f"{a.et_stress}, full ET above {rc['et_stress'][0]:g} m, none below {rc['et_stress'][1]:g} m") + ". "
         f"DTM: {rc['notes']['dtm']}. "
         f"Sub-KHG units: {rc['notes']['units']}. Peat depth valid on {rc['notes']['peat_depth_valid_in_domain']:.0%} of the KHG "
         f"(gaps: median {rc['notes']['peat_depth_median_m']:.1f} m). Fixed cells: edge {fixed_share['edge']:.1%}, canals "
         f"{fixed_share['canal']:.1%} of the KHG. Run time {seconds / 60:.1f} min. Registry snapshot {sha[:12]}. Method: `repeat_neraca/model.py`.", ""]
    s = series.assign(month=pd.to_datetime(series.date).dt.to_period("M"))
    g = s.groupby("month")
    mon = pd.DataFrame({"P (mm)": g.P_mm.sum().round(0), "ET (mm)": g.ET_mm.sum().round(0), "P - ET (mm)": (g.P_mm.sum() - g.ET_mm.sum()).round(0),
                        "depth at month end (cm)": g.mean_depth_cm.last().round(0), "share deeper than 40 cm": g.share_deeper_40cm.last().round(2),
                        "canal inflow (mm)": g.canal_in_mm.sum().round(1), "edge inflow (mm)": g.edge_in_mm.sum().round(1),
                        "ET realised (share)": g.et_share.mean().round(2)})
    mon.index.name = "month"
    L += ["## By month (KHG mean over the free cells)", "", *md_table(mon), ""]
    if len(w):
        L += [f"## Window {w.date.iloc[0]} to {w.date.iloc[-1]}", "",
              f"KHG-mean depth {w.mean_depth_cm.min():.0f} to {w.mean_depth_cm.max():.0f} cm; share of the KHG deeper than 40 cm "
              f"{w.share_deeper_40cm.min():.0%} to {w.share_deeper_40cm.max():.0%}. Water put into the peat over the window: canals "
              f"{w.canal_in_mm.sum():.0f} mm, edge {w.edge_in_mm.sum():.0f} mm; rain {w.P_mm.sum():.0f} mm, ET {w.ET_mm.sum():.0f} mm.", ""]
    if scores:
        L += ["## Field points", "",
              f"Excluded: {scores['excluded']['outside_or_not_peat_or_no_depth']} points not on peat, without a depth or outside the KHG; "
              f"{scores['excluded']['on_fixed_cell']} on a canal or edge cell.", "",
              "| points | prediction | n | Spearman | bias (cm) | RMSE (cm) | MAE (cm) |", "|---|---|---|---|---|---|---|"]
        for sub in ("unflagged", "all"):
            for k in ("model", "distance", "constant"):
                v = scores[sub][k]
                L.append(f"| {sub} | {k} | {v.get('n')} | {v.get('spearman', float('nan')):.2f} | {v.get('bias_cm', float('nan')):.0f} | "
                         f"{v.get('rmse_cm', float('nan')):.0f} | {v.get('mae_cm', float('nan')):.0f} |")
        g = scores["gate"]
        L += ["", f"**Gate: {'pass' if g['pass'] else 'fail'}** (" + "; ".join(f"{k}: {'yes' if v else 'no'}" for k, v in g["checks"].items())
              + "). Distance prediction: depth = "
              f"{scores['unflagged']['distance_fit']['intercept_cm']:.0f} + {scores['unflagged']['distance_fit']['slope_cm_per_log_m']:.1f} ln(1 + d) cm, fitted to the same points.", ""]
        if "obs_variance_between_groups" in scores["unflagged"]:
            L += [f"Share of the observed variance between the {scores['unflagged']['n_groups']} field teams (`group`): "
                  f"{scores['unflagged']['obs_variance_between_groups']:.0%}. A large share means the readings differ by who took them more "
                  "than by place: a difference in method or in visit date, which the survey cannot tell apart. A model can follow neither "
                  "without the dates.", ""]
        if sens is not None and len(sens):
            L += [f"Single-day scores across the window: Spearman {sens.spearman.min():.2f} to {sens.spearman.max():.2f}, bias "
                  f"{sens.bias_cm.min():.0f} to {sens.bias_cm.max():.0f} cm (`field_day_sensitivity.csv`).", ""]
        for by, t in brk.items():
            L += [f"### By {'distance to the nearest canal (m)' if by == 'dist_m' else by}", "", *md_table(t), ""]
    if st:
        d = st["dynamics"]
        L += ["## Water-table stations", "",
              f"{d['n_stations']} stations with at least 30 days ({st['excluded']['on_fixed_cell']} on a canal or edge cell, scored but "
              f"flagged; {st['excluded']['outside_khg']} outside the KHG).", "",
              "| points | prediction | n | Spearman | bias (cm) | RMSE (cm) | MAE (cm) |", "|---|---|---|---|---|---|---|"]
        for part in ("unflagged", "all"):
            for k in ("model", "distance", "constant"):
                v = st[part][k]
                L.append(f"| {part} | {k} | {v.get('n')} | {v.get('spearman', float('nan')):.2f} | {v.get('bias_cm', float('nan')):.0f} | "
                         f"{v.get('rmse_cm', float('nan')):.0f} | {v.get('mae_cm', float('nan')):.0f} |")
        g = st["gate"]
        L += ["", f"Levels are each station's mean over its days. Dynamics, on the {d['n_unflagged']} unflagged stations: median per-station r {d['median_station_r']:.2f}; mean curve "
              f"r {d['khg_mean_r']:.2f} (mean curve of these stations), bias {d['khg_mean_bias_cm']:.0f} cm (observed {d['obs_khg_mean_cm']:.0f}, simulated "
              f"{d['sim_khg_mean_cm']:.0f} cm); drawdown over the record, median observed {d['obs_drawdown_median_cm']:.0f} cm, simulated "
              f"{d['sim_drawdown_median_cm']:.0f} cm, Spearman across stations {d['drawdown_spearman']:.2f}.", ""]
        if "obs_variance_between_groups" in st["unflagged"]:
            L += [f"Share of the variance of station levels between the {st['unflagged']['n_groups']} groups (concessions): "
                  f"{st['unflagged']['obs_variance_between_groups']:.0%}.", ""]
        if "by_kind" in st:
            L += ["| stations | n (and on a canal or edge cell, left out) | in managed land | level observed (cm) | level simulated (cm) | drawdown observed (cm) | drawdown simulated (cm) |",
                  "|---|---|---|---|---|---|---|"]
            L += [f"| {k} | {v['n']} ({v['on_fixed_cell']}) | {v['in_managed_land']} | {v['obs_level_cm']:.0f} | {v['sim_level_cm']:.0f} | {v['obs_drawdown_cm']:.0f} | "
                  f"{v['sim_drawdown_cm']:.0f} |" for k, v in st["by_kind"].items()]
            L += ["", "Medians over the unflagged stations of each kind.", ""]
        if "supply_check" in st:
            c = st["supply_check"]
            L += [f"Supply check, {c['period']}: deficit from the stations (repeat-neraca-run) {c['station_deficit_mm']:.0f} mm; water the "
                  f"model's canals put into the peat {c['model_canal_in_mm']:.0f} mm, edge {c['model_edge_in_mm']:.0f} mm.", ""]
        L += [f"**Station gate: {'pass' if g['pass'] else 'fail'}** ("
              + "; ".join(f"{k}: {'yes' if v else 'no'}" for k, v in g["checks"].items()) + ").", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
