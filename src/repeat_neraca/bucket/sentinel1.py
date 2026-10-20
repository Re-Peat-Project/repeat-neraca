#!/usr/bin/env python3
"""Does Sentinel-1 radar backscatter tell which SiTMAT stations have the deepest water table?

  python -m repeat_neraca.bucket.sentinel1 --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml [--refetch]

Why: ERA5 is too coarse to separate stations (neraca air has no spatial skill), and water tables are managed, so a
direct observation of wetness may carry what the weather cannot. Sentinel-1 C-band backscatter (RTC gamma0, 10 m,
Planetary Computer `sentinel-1-rtc`) has been related to peat water table depth in the literature; this tests it here.

Reads neraca_stations.csv (from `repeat_neraca.bucket.run`) and the SiTMAT daily series, reads VV and VH at each station
(mean of the 3 x 3 pixels around it at 60 m) for the calibration window, and writes in the output folder
  neraca_s1_series.csv     station, date, orbit, vv_db, vh_db (cached in cache_dir/<khg>/neraca; --refetch to redo)
  neraca_s1_stations.csv   per-station backscatter features next to the observed peak depth and days deeper than 40 cm
  neraca_sentinel1.md      the two questions and their answers:
    1. across stations: Spearman of each feature with observed peak depth / share of days deeper than 40 cm
       (the same threshold as the neraca air gate: |rho| >= 0.3)
    2. within a station: does a wetter-than-usual radar scene fall on a shallower-than-usual water table day
       (anomalies against the station's own mean and, for radar, its own orbit's mean)
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from repeat_common import grid as G
from .config import load_config
from . import calibrate as CAL
from .covariates import _rho
from .run import PRESET

log = logging.getLogger("prioritas.neraca")
RES_M = 60
LANDCOVER = {10: "tree", 20: "shrub", 30: "grass", 40: "crop"}      # ESA WorldCover classes seen at the stations
MIN_STATIONS = 12


def fetch(stations: pd.DataFrame, start: str, end: str, cache: Path) -> pd.DataFrame:
    """VV and VH in dB at each station for every Sentinel-1 RTC scene in [start, end] (cached as csv)."""
    f = cache / "s1_series.csv"
    if f.exists():
        log.info("Sentinel-1: reading %s", f)
        return pd.read_csv(f, parse_dates=["date"])
    import odc.stac
    import planetary_computer
    import pystac_client
    import xarray as xr
    from pyproj import Transformer
    cl = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
    pad = 0.02
    bbox = [stations.lon.min() - pad, stations.lat.min() - pad, stations.lon.max() + pad, stations.lat.max() + pad]
    items = list(cl.search(collections=["sentinel-1-rtc"], bbox=bbox, datetime=f"{start}/{end}").items())
    items.sort(key=lambda i: i.datetime)                            # odc.stac returns one time step per item, in time order
    log.info("Sentinel-1 RTC: %d scenes between %s and %s", len(items), start, end)
    if not items:
        raise SystemExit("no Sentinel-1 scenes found")
    zone = int((stations.lon.mean() + 180) // 6) + 1
    crs = f"EPSG:{(32600 if stations.lat.mean() >= 0 else 32700) + zone}"        # UTM zone of the stations
    ds = odc.stac.load(items, bands=["vv", "vh"], bbox=bbox, crs=crs, resolution=RES_M, chunks={"x": 512, "y": 512},
                       groupby=None, resampling="average")
    x, y = Transformer.from_crs(4326, crs, always_xy=True).transform(stations.lon.values, stations.lat.values)
    xs, ys = ds.x.values, ds.y.values
    ix = np.abs(xs[None, :] - np.asarray(x)[:, None]).argmin(axis=1)
    iy = np.abs(ys[None, :] - np.asarray(y)[:, None]).argmin(axis=1)
    acc = {b: [] for b in ("vv", "vh")}
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            sel = ds.isel(x=xr.DataArray(np.clip(ix + dx, 0, len(xs) - 1), dims="s"), y=xr.DataArray(np.clip(iy + dy, 0, len(ys) - 1), dims="s"))
            for b in acc:
                acc[b].append(sel[b])
    log.info("Sentinel-1: reading pixels (%d scenes x %d stations) ...", ds.sizes["time"], len(stations))
    out = {}
    for b in acc:
        lin = xr.concat(acc[b], dim="k").where(lambda a: a > 0).mean("k").compute()
        out[b] = 10 * np.log10(lin.values)                                # time x station, dB
    t = pd.DatetimeIndex(ds.time.values)
    meta = pd.DataFrame({"date": t.tz_localize("UTC").tz_convert("Asia/Jakarta").tz_localize(None).normalize(),
                         "orbit": [f"{i.properties.get('sat:orbit_state', '?')[:3]}{i.properties.get('sat:relative_orbit', '?')}" for i in items]
                         if len(items) == len(t) else "?"})
    rows = []
    for j, sid in enumerate(stations.station_id):
        d = meta.copy()
        d["station_id"], d["vv_db"], d["vh_db"] = sid, out["vv"][:, j], out["vh"][:, j]
        rows.append(d)
    s = pd.concat(rows, ignore_index=True)
    s = s[np.isfinite(s.vv_db) & np.isfinite(s.vh_db)]
    cache.mkdir(parents=True, exist_ok=True)
    s.to_csv(f, index=False)
    return s


def station_features(s1: pd.DataFrame) -> pd.DataFrame:
    """Per-station backscatter features. Anomalies are against the station's own orbit so viewing geometry drops out."""
    s1 = s1.copy()
    s1["vv_anom"] = s1.vv_db - s1.groupby(["station_id", "orbit"]).vv_db.transform("mean")
    g = s1.groupby("station_id")
    f = pd.DataFrame({"vv_mean_db": g.vv_db.mean(), "vh_mean_db": g.vh_db.mean(),
                      "vv_minus_vh_db": g.vv_db.mean() - g.vh_db.mean(),
                      "vv_anom_sd_db": g.vv_anom.std(),
                      "vv_p90_minus_p10_db": g.vv_db.quantile(.9) - g.vv_db.quantile(.1),
                      "n_scenes": g.size()})
    return f.reset_index()


def within_station(s1: pd.DataFrame, Z: pd.DataFrame) -> dict:
    """Spearman between radar anomaly and water-table depth anomaly on the same local day, per station."""
    s1 = s1.copy()
    s1["vv_anom"] = s1.vv_db - s1.groupby(["station_id", "orbit"]).vv_db.transform("mean")
    z = Z.stack().dropna().rename("z").reset_index()
    z.columns = ["date", "station_id", "z"]
    z["z_anom"] = z.z - z.groupby("station_id").z.transform("mean")
    m = s1.merge(z, on=["date", "station_id"])
    r = []
    for sid, d in m.groupby("station_id"):
        if len(d) >= 8 and d.vv_anom.nunique() > 1 and d.z_anom.nunique() > 1:
            r.append(float(spearmanr(d.vv_anom, d.z_anom).correlation))
    r = np.array(r)
    pooled = float(spearmanr(m.vv_anom, m.z_anom).correlation) if len(m) > 10 else None
    return {"n_pairs": int(len(m)), "n_stations": int(len(r)), "median_rho": float(np.median(r)) if len(r) else None,
            "share_negative": float((r < 0).mean()) if len(r) else None, "pooled_rho": pooled}


def block_cv(feats: pd.DataFrame, models: dict, target: str, group: str = "block") -> pd.DataFrame:
    """Leave-one-group-out (default: spatial block): out-of-fold RMSE and Spearman of linear models of `target`, against the training mean."""
    rows = []
    d = feats.dropna(subset=[target, group]).copy()
    y = d[target].values
    folds = [(d[group].values != b, d[group].values == b) for b in sorted(d[group].unique())]
    base = np.full(len(d), np.nan)
    for tr, te in folds:
        base[te] = y[tr].mean()
    rows.append({"model": "no skill (training mean)", "rmse": float(np.sqrt(np.mean((y - base) ** 2))), "oof_spearman": None})
    for name, cols in models.items():
        cols = [c for c in cols if c in d.columns and d[c].notna().all()]
        if not cols:
            continue
        X = d[cols].values.astype(float)
        pred = np.full(len(d), np.nan)
        for tr, te in folds:
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
            A = np.c_[np.ones(tr.sum()), (X[tr] - mu) / sd]
            beta = np.linalg.lstsq(A, y[tr], rcond=None)[0]
            pred[te] = np.c_[np.ones(te.sum()), (X[te] - mu) / sd] @ beta
        rows.append({"model": f"{name} ({', '.join(cols)})", "rmse": float(np.sqrt(np.mean((y - pred) ** 2))),
                     "oof_spearman": float(spearmanr(y, pred).correlation)})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--refetch", action="store_true", help="ignore the cached Sentinel-1 series")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    import geopandas as gpd
    cfg = load_config(a.config, PRESET, "neraca")
    out = Path(cfg["out"])
    st = pd.read_csv(out / "neraca_stations.csv")
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    idf = cfg["khg_id_field"]
    kid = str(khg[idf].iloc[0]) if idf in khg.columns else "KHG01"
    cal = cfg["neraca"]["calibration"]
    cache = Path(cfg["cache_dir"]) / kid / "neraca"
    if a.refetch and (cache / "s1_series.csv").exists():
        (cache / "s1_series.csv").unlink()
    s1 = fetch(st, str(cal["start"])[:10], str(cal["end"])[:10], cache)
    s1.to_csv(out / "neraca_s1_series.csv", index=False)
    Z, _ = CAL.load_stations(cfg, khg.geometry.union_all(), cal["start"], cal["end"])
    feats = station_features(s1).merge(st[["station_id", "obs_peak_cm", "obs_days_gt40", "block"]], on="station_id")
    cov = out / "neraca_station_covariates.csv"
    known = ["peat_depth_cm", "canal_dist_m", "dist_khg_edge_m", "elev_m", "dist_river_m"]
    if cov.exists():
        c = pd.read_csv(cov)
        feats = feats.merge(c[["station_id"] + [k for k in known if k in c.columns]], on="station_id", how="left")
    wc = Path(cfg["cache_dir"]) / kid / "static" / "worldcover.tif"
    if wc.exists():
        import rasterio
        grid = G.make_grid(khg.geometry.union_all(), float(cfg["grid_res_m"]))
        with rasterio.open(wc) as src:
            lc = CAL.sample_grid(src.read(1), grid, st.lon.values, st.lat.values)
        lcd = pd.DataFrame({"station_id": st.station_id, "landcover": lc})
        feats = feats.merge(lcd, on="station_id", how="left")
        for k, v in LANDCOVER.items():
            feats[f"lc_{v}"] = (feats.landcover == k).astype(float)
    feats["concession"] = feats.station_id.str.split(":").str[0].str.replace("concession/", "", regex=False)     # SiTMAT id = concession/<code>:<station>
    feats.to_csv(out / "neraca_s1_stations.csv", index=False)
    w = within_station(s1, Z)
    cols = ["vv_mean_db", "vh_mean_db", "vv_minus_vh_db", "vv_anom_sd_db", "vv_p90_minus_p10_db"]
    rho = {c: (_rho(feats, c, "obs_peak_cm"), _rho(feats, c, "obs_days_gt40")) for c in cols}
    best = max((abs(v) for pair in rho.values() for v in pair if v is not None), default=0)
    lines = [f"# Sentinel-1 against the SiTMAT stations ({len(feats)} stations, {int(feats.n_scenes.median())} scenes each)", "",
             f"Radar: Planetary Computer `sentinel-1-rtc` (gamma0, VV and VH), {cal['start']} to {cal['end']}, 3 x 3 pixels at {RES_M} m around each station.", "",
             "## 1. Across stations: does the radar say which stations are deepest?", "",
             "| feature | rho with observed peak depth | rho with days deeper than 40 cm |", "|---|---|---|"]
    lines += [f"| {c} | {v[0]} | {v[1]} |" for c, v in rho.items()]
    lines += ["", f"Strongest |rho|: {best:.2f}. The neraca air gate asks for 0.3. "
              + ("Reached by at least one feature (a screen over several features and two targets; section 3 is the test)." if best >= 0.3 else "**Not reached.**"), "",
              "## 2. Within a station: does a wetter scene fall on a shallower day?", "",
              f"Anomalies of VV (against the station's own orbit mean) and of observed depth (against the station mean), same local day: "
              f"{w['n_pairs']} pairs at {w['n_stations']} stations.",
              f"Median within-station Spearman {None if w['median_rho'] is None else round(w['median_rho'], 2)} "
              f"(negative = brighter radar on shallower water table, the expected sign), "
              f"{None if w['share_negative'] is None else round(100 * w['share_negative'])}% of stations negative, pooled {None if w['pooled_rho'] is None else round(w['pooled_rho'], 2)}."]
    ratio = ["vv_minus_vh_db"]
    s1_all = ["vv_minus_vh_db", "vv_mean_db", "vh_mean_db"]
    models = {"radar ratio": ratio, "radar VV, VH, ratio": s1_all, "known covariates": known,
              "known covariates + radar ratio": known + ratio, "known covariates + radar all": known + s1_all}
    lines += ["", "## 3. Out of fold: does the radar predict held-out stations, and does it add to what we already know?", "",
              f"Linear models fitted with whole spatial blocks left out ({feats.block.nunique()} blocks, the same blocks as the neraca air calibration). "
              "A model is useful only if its RMSE is below the no-skill line."]
    for tgt, lab in (("obs_peak_cm", "observed peak depth (cm)"), ("obs_days_gt40", "share of days deeper than 40 cm")):
        r = block_cv(feats, models, tgt)
        lines += ["", f"Target: {lab}", "", "| model | out-of-fold RMSE | out-of-fold Spearman |", "|---|---|---|"]
        lines += [f"| {x.model} | {x.rmse:.3g} | {'' if pd.isna(x.oof_spearman) else round(x.oof_spearman, 2)} |" for x in r.itertuples()]
    lines += ["", "## 4. One orbit at a time", "",
              "Features from a single relative orbit only, so viewing geometry is the same for every station of that orbit.", "",
              "| orbit | stations | scenes per station | rho(ratio, peak depth) | rho(ratio, days > 40) | rho(VV, peak depth) |", "|---|---|---|---|---|---|"]
    for orb, d in s1.groupby("orbit"):
        f = station_features(d.assign(orbit=orb)).merge(feats[["station_id", "obs_peak_cm", "obs_days_gt40"]], on="station_id")
        if len(f) >= MIN_STATIONS and f.n_scenes.median() >= 5:
            lines.append(f"| {orb} | {len(f)} | {int(f.n_scenes.median())} | {_rho(f, 'vv_minus_vh_db', 'obs_peak_cm')} | "
                         f"{_rho(f, 'vv_minus_vh_db', 'obs_days_gt40')} | {_rho(f, 'vv_mean_db', 'obs_peak_cm')} |")
    if "landcover" in feats:
        lines += ["", "## 5. Land cover (ESA WorldCover at the station)", "",
                  "If the radar ratio only tells land cover apart, it will not rank stations that share a class.", "",
                  "| class | stations | median peak depth (cm) | median ratio (dB) | rho(ratio, peak depth) inside the class |", "|---|---|---|---|---|"]
        for k, v in LANDCOVER.items():
            f = feats[feats.landcover == k]
            if len(f):
                inside = _rho(f, "vv_minus_vh_db", "obs_peak_cm") if len(f) >= MIN_STATIONS else "too few"
                lines.append(f"| {v} ({k}) | {len(f)} | {f.obs_peak_cm.median():.0f} | {f.vv_minus_vh_db.median():.2f} | {inside} |")
        lines.append("")
        lines.append(f"Spearman of the ratio with land cover itself (tree share): {_rho(feats, 'vv_minus_vh_db', 'lc_tree')}; of peak depth with tree share: {_rho(feats, 'obs_peak_cm', 'lc_tree')}.")
        lcs = [f"lc_{v}" for v in LANDCOVER.values() if f"lc_{v}" in feats and 0 < feats[f"lc_{v}"].sum() < len(feats)]
        r = block_cv(feats, {"land cover only": lcs, "land cover + radar ratio": lcs + ratio, "radar ratio": ratio}, "obs_peak_cm")
        lines += ["", "Out of fold, peak depth:", "", "| model | out-of-fold RMSE | out-of-fold Spearman |", "|---|---|---|"]
        lines += [f"| {x.model} | {x.rmse:.3g} | {'' if pd.isna(x.oof_spearman) else round(x.oof_spearman, 2)} |" for x in r.itertuples()]
    lines += ["", "## 6. Concession (from the SiTMAT station id)", "",
              "The id of every SiTMAT station starts with its concession code, which stands in for management (weirs, drainage targets); "
              "GFW concession polygons were not used (the wood-fibre layer is licensed view-only).", ""]
    cc = feats.groupby("concession").agg(stations=("station_id", "size"), peak_cm=("obs_peak_cm", "median"), ratio_db=("vv_minus_vh_db", "median")).sort_values("stations", ascending=False)
    lines += ["| concession | stations | median peak depth (cm) | median ratio (dB) |", "|---|---|---|---|"]
    lines += [f"| {i} | {int(r.stations)} | {r.peak_cm:.0f} | {r.ratio_db:.2f} |" for i, r in cc.iterrows()]
    big = cc[cc.stations >= 3].index
    f = feats[feats.concession.isin(big)].copy()
    ss_tot = ((f.obs_peak_cm - f.obs_peak_cm.mean()) ** 2).sum()
    ss_within = ((f.obs_peak_cm - f.groupby("concession").obs_peak_cm.transform("mean")) ** 2).sum()
    for c in ("obs_peak_cm", "vv_minus_vh_db"):
        f[c + "_w"] = f[c] - f.groupby("concession")[c].transform("mean")
    lines += ["", f"Concession explains {100 * (1 - ss_within / ss_tot):.0f}% of the variance of peak depth among the {len(big)} concessions with 3 or more stations ({len(f)} stations).",
              f"Inside concessions (both variables minus the concession mean): rho(ratio, peak depth) = {_rho(f, 'vv_minus_vh_db_w', 'obs_peak_cm_w')}; "
              f"between concession medians ({len(big)} concessions): rho = {_rho(cc.loc[big].reset_index().rename(columns={'ratio_db': 'a', 'peak_cm': 'b'}), 'a', 'b')}.",
              "", "Out of fold with whole concessions left out (a new concession is the hard case), peak depth:", "",
              "| model | out-of-fold RMSE | out-of-fold Spearman |", "|---|---|---|"]
    r = block_cv(f, {"radar ratio": ratio}, "obs_peak_cm", group="concession")
    lines += [f"| {x.model} | {x.rmse:.3g} | {'' if pd.isna(x.oof_spearman) else round(x.oof_spearman, 2)} |" for x in r.itertuples()]
    text = "\n".join(lines)
    (out / "neraca_sentinel1.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
