#!/usr/bin/env python3
"""Neraca air per sub-KHG: a daily water-table bucket driven by ERA5, fitted to SiTMAT stations.
Definition, outputs and checks: repeat_neraca/bucket/README.md.

  python -m repeat_neraca.bucket.run --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml --forcing-only    # slow, once: ERA5 for every window
  python -m repeat_neraca.bucket.run --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml --calibrate-only  # skill on SiTMAT stations only
  python -m repeat_neraca.bucket.run --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml                   # everything
  python -m repeat_neraca.bucket.run --print-default-config

Needs: units.path (sub-KHG polygons with khg_id and unit_id, e.g. from repeat_delineation), khg, rasters.peat_depth
(with params.peat_depth_scale), tma.path (SiTMAT folder), vectors.canals (optional). It writes, in `out`:
  neraca_unit.csv        one row per sub-KHG, averaged over neraca.years (merge with extra_indicators)
  neraca_unit_by_year.csv  the same per year
  neraca_report.json     fitted parameters, skill on held-out stations, spread of each output
  neraca_stations.csv    per station: observed and simulated peak depth, covariates
  neraca_calibration.png diagnostics
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
from scipy.stats import spearmanr

from repeat_common import grid as G
from .config import load_config
from . import calibrate as CAL
from repeat_common import forcing as FO
from .model import simulate, unit_indicators

log = logging.getLogger("prioritas.neraca")

NERACA_DEFAULTS = {
    "tz_hours": 7,                         # local day: WIB = 7, WITA = 8, WIT = 9
    "window_months": [4, 10],              # first and last month simulated (April start = end of wet season assumed)
    "dry_months": [6, 7, 8, 9, 10],        # the indicators are taken over these months; earlier months are spin-up
    "years": [2019, 2021],                 # baseline years for the indicators
    "calibration": {"start": "2026-04-01", "end": "2026-10-15", "blocks": 4, "min_stations": 12},
    "sy_grid": [0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0],   # above ~0.5 is not physical: it flags a model that over-predicts the drawdown
    "k_grid": [0.0, 0.5, 1.0, 2.0, 4.0],   # drainage coefficient, mm/day at full canal proximity
    "z0_grid": [0.0, 10.0, 20.0, 30.0, 40.0],
    "canal_scale_m": 300,                  # proximity = exp(-distance / scale)
    "min_spatial_skill": 0.3,              # the outputs are flagged unusable for ranking below this Spearman across held-out stations
    "drainage_gain": 0.02,                 # drainage is kept only if out-of-fold RMSE improves by this share AND spatial skill does not drop
    "params": None,                        # {"sy": .., "k": .., "z0": ..} skips the fit
    "forcing": {"rain": "era5", "evap": "era5"},   # rain: era5 | chirps (5 km); evap: era5 | wapor (300 m); see repeat_common/forcing.py (repeat-common repo)
}
PRESET = {"units": {"mode": "vector"}, "grid_res_m": 30, "neraca": NERACA_DEFAULTS}


def _spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4 or np.nanstd(a[ok]) == 0 or np.nanstd(b[ok]) == 0:
        return None
    r = spearmanr(a[ok], b[ok]).correlation
    return None if not np.isfinite(r) else float(r)


def _plots(out: Path, Z, dates, sim_mean, stn, cv, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
    ax[0].plot(Z.index, Z.values, color="#9aa", lw=0.4, alpha=0.5)
    ax[0].plot(Z.index, np.nanmean(Z.values, axis=1), color="k", lw=2, label="observed, mean of stations")
    ax[0].plot(dates, sim_mean, color="#B8321F", lw=2, label="simulated, mean of stations (out of fold)")
    ax[0].axhline(40, color="#555", ls=":", lw=1)
    ax[0].invert_yaxis()
    ax[0].set_ylabel("water table depth, cm")
    ax[0].set_title("Seasonal drawdown")
    ax[0].legend(fontsize=8)
    ax[1].scatter(stn["obs_peak_cm"], stn["sim_peak_cm"], s=16, c=stn["block"], cmap="tab10")
    lim = [0, float(np.nanmax(stn[["obs_peak_cm", "sim_peak_cm"]].values)) * 1.05]
    ax[1].plot(lim, lim, color="#999", lw=1)
    ax[1].set_xlabel("observed peak depth (p95), cm")
    ax[1].set_ylabel("simulated, held-out stations, cm")
    ax[1].set_title("Which stations dry out more: Spearman %s" % ("n/a" if cv["spatial_spearman_peak"] is None else "%.2f" % cv["spatial_spearman_peak"]))
    ax[2].scatter(stn["peat_depth_cm"], stn["obs_peak_cm"], s=16, c="#2a6", label="vs peat depth")
    ax2 = ax[2].twiny()
    ax2.scatter(stn["canal_dist_m"], stn["obs_peak_cm"], s=16, c="#c70", marker="s", label="vs canal distance")
    ax[2].set_xlabel("peat depth, cm (green)")
    ax2.set_xlabel("distance to canal, m (orange)")
    ax[2].set_ylabel("observed peak depth, cm")
    ax[2].set_title("Covariates on their own")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out / "neraca_calibration.png", dpi=130)
    plt.close(fig)


def year_window(year: int, nc: dict) -> tuple[pd.Timestamp, pd.Timestamp]:
    """First and last local day simulated in a baseline year (neraca.window_months)."""
    m0, m1 = nc["window_months"]
    return pd.Timestamp(year=year, month=m0, day=1), pd.Timestamp(year=year, month=m1, day=1) + pd.offsets.MonthEnd(0)


def fetch_forcing(cfg: dict, kid: str, geom_ll) -> None:
    """Read and cache the ERA5 daily forcing of every window a run needs (calibration and baseline years).
    About 11 minutes per window; run it once, then every later run reads the cache."""
    nc = cfg["neraca"]
    cache = Path(cfg["cache_dir"]) / kid / "neraca"
    era5 = {**cfg["sources"]["era5"]}
    grid = G.make_grid(geom_ll, float(cfg["grid_res_m"]))
    stride = int(era5.get("evap_stride", 3))
    cal = nc["calibration"]
    windows = [(cal["start"], cal["end"])] + [year_window(y, nc) for y in nc["years"]]
    for start, end in windows:
        f = FO.forcing_for(grid, era5, start, end, cache, nc["tz_hours"], stride, **nc["forcing"])
        log.info("forcing %s..%s ready: %d of %d days valid, last valid day %s", pd.Timestamp(start).date(),
                 pd.Timestamp(end).date(), int(f["valid"].sum()), len(f["dates"]), FO.last_valid(f))


def run_khg(cfg: dict, kid: str, geom_ll, units_k, out: Path):
    nc = cfg["neraca"]
    cache = Path(cfg["cache_dir"]) / kid / "neraca"
    era5 = {**cfg["sources"]["era5"]}
    grid = G.make_grid(geom_ll, float(cfg["grid_res_m"]))
    up = units_k.to_crs(grid.crs).reset_index(drop=True)
    n_units = len(up)
    label = G.label_raster(up, grid)
    log.info("KHG %s: %d sub-KHG on a %d x %d grid", kid, n_units, grid.height, grid.width)

    # peat depth in cm and canal proximity on the grid
    pdp = cfg["rasters"].get("peat_depth")
    if not pdp:
        raise SystemExit("rasters.peat_depth is needed (and params.peat_depth_scale)")
    scale = float(cfg["params"].get("peat_depth_scale", 1.0))
    depth = G.warp_to_grid(pdp, grid) * scale * 100.0                       # raster x scale = m; x 100 = cm
    log.info("peat depth: median %.0f cm, p5-p95 %.0f-%.0f cm, valid %.0f%%", np.nanmedian(depth),
             *np.nanpercentile(depth, [5, 95]), 100 * np.isfinite(depth).mean())
    ell = float(nc["canal_scale_m"])
    if cfg["vectors"].get("canals"):
        cm = G.vector_to_grid_mask(cfg["vectors"]["canals"], grid)
        dist = ndimage.distance_transform_edt(~cm, sampling=grid.res).astype("float32") if cm.any() else np.full(grid.shape, 1e5, "float32")
    else:
        dist = np.full(grid.shape, 1e5, "float32")
    cprox = np.exp(-dist / ell).astype("float32")

    # ---- calibration on SiTMAT (forcing of the calibration window) ----
    cal = nc["calibration"]
    params, cv_report, stn = nc["params"], None, None
    Zst = None
    if params is None:
        f = FO.forcing_for(grid, era5, cal["start"], cal["end"], cache, nc["tz_hours"], int(era5.get("evap_stride", 3)), **nc["forcing"])
        end = FO.last_valid(f)
        if end is None:
            raise SystemExit("ERA5 has no data in the calibration window")
        keep = f["dates"] <= end
        dates = f["dates"][keep]
        P, E = f["P"][keep], f["E"][keep]
        log.info("calibration window %s .. %s (last valid ERA5 day)", dates[0].date(), dates[-1].date())
        Z, meta = CAL.load_stations(cfg, geom_ll, dates[0], dates[-1])
        Z = Z.reindex(dates)
        if Z.shape[1] < int(cal["min_stations"]):
            raise SystemExit(f"only {Z.shape[1]} stations in the KHG; need at least {cal['min_stations']} or set neraca.params")
        r, c = FO.cell_of(meta.lon.values, meta.lat.values, f["transform"], P.shape[1:])
        net = (P[:, r, c] - E[:, r, c]).astype("float64")
        dep = CAL.sample_grid(depth, grid, meta.lon.values, meta.lat.values)
        n_nan = int(np.isnan(dep).sum())
        dep = np.where(np.isfinite(dep) & (dep > 0), dep, np.nanmedian(depth))
        cd = CAL.sample_grid(dist, grid, meta.lon.values, meta.lat.values)
        cd = np.where(np.isfinite(cd), cd, 1e5)
        cst = np.exp(-cd / ell)
        obs = Z.values.astype("float64")
        in_season = np.isin(dates.month, nc["dry_months"])
        lonlat = meta[["lon", "lat"]].values
        nocap = np.full(len(dep), np.inf)         # the water table can fall below the peat, into the mineral soil
        grids_full = {"sy": nc["sy_grid"], "k": nc["k_grid"], "z0": nc["z0_grid"]}
        grids_k0 = {**grids_full, "k": [0.0]}
        cvf = CAL.cross_validate(net, obs, nocap, cst, lonlat, in_season, grids_full, int(cal["blocks"]))
        cv0 = CAL.cross_validate(net, obs, nocap, cst, lonlat, in_season, grids_k0, int(cal["blocks"]))
        gain = (cv0["rmse_cm"] - cvf["rmse_cm"]) / cv0["rmse_cm"]
        sp_f, sp_0 = cvf["spatial_spearman_peak"], cv0["spatial_spearman_peak"]
        spatial_ok = (sp_f or 0.0) >= (sp_0 or 0.0) - 0.02          # a constant offset can cut RMSE without telling places apart
        use_k = gain >= float(nc["drainage_gain"]) and spatial_ok
        cv = cvf if use_k else cv0
        params = CAL.fit(net, obs, nocap, cst, grids_full if use_k else grids_k0)
        log.info("drainage term %s (out-of-fold RMSE %.1f cm with it, %.1f cm without, gain %.1f%%; spatial Spearman of peak depth %s with, %s without)",
                 "kept" if use_k else "dropped", cvf["rmse_cm"], cv0["rmse_cm"], 100 * gain,
                 "n/a" if sp_f is None else "%.2f" % sp_f, "n/a" if sp_0 is None else "%.2f" % sp_0)
        log.info("fitted on all stations: Sy %.3f, k %.1f mm/day, z0 %.0f cm", params["sy"], params["k"], params["z0"])
        stn = pd.DataFrame({"station_id": meta.station_id, "lon": meta.lon, "lat": meta.lat, "peat_depth_cm": dep,
                            "canal_dist_m": cd, "obs_peak_cm": cv["_obs_peak"], "sim_peak_cm": cv["_sim_peak"],
                            "obs_days_gt40": cv["_obs_days"], "sim_days_gt40": cv["_sim_days"], "block": cv["_block"]})
        cov = CAL.covariate_skill(stn.obs_peak_cm, stn.obs_days_gt40, dep, cd)
        sim_mean = sim_mean_series = np.nanmean(np.where(np.isfinite(obs), cv["_sim_oof"], np.nan), axis=1)
        sp = [cv["spatial_spearman_peak"], cv["spatial_spearman_days_gt40"]]
        spatial_ok = any(v is not None and v >= float(nc["min_spatial_skill"]) for v in sp)
        beats = cv["rmse_cm"] < cv["rmse_baseline_cm"]
        verdict = {"usable_for_ranking": bool(spatial_ok and beats), "min_spatial_skill": float(nc["min_spatial_skill"]),
                   "spatial_spearman_peak": sp[0], "spatial_spearman_days_gt40": sp[1], "beats_no_skill_baseline_rmse": bool(beats),
                   "reason": "" if (spatial_ok and beats) else
                   "; ".join(m for ok, m in ((spatial_ok, "no spatial skill across held-out stations"),
                                             (beats, "does not beat the no-skill baseline")) if not ok)}
        if not verdict["usable_for_ranking"]:
            log.warning("neraca air is NOT usable for ranking: %s (spatial Spearman peak %s, days>40 %s; RMSE %.1f vs baseline %.1f cm)",
                        verdict["reason"], sp[0], sp[1], cv["rmse_cm"], cv["rmse_baseline_cm"])
        cv_report = {"verdict": verdict, "n_stations": cv["n_stations"], "n_stations_peat_depth_filled": n_nan, "period": [str(dates[0].date()), str(dates[-1].date())],
                     "drainage_kept": bool(use_k), "drainage_gain_share": float(gain),
                     "with_drainage": {k: v for k, v in cvf.items() if not k.startswith("_")},
                     "without_drainage": {k: v for k, v in cv0.items() if not k.startswith("_")},
                     "covariates_alone": cov, "fitted": params}
        stn.to_csv(out / "neraca_stations.csv", index=False)
        pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "n_stations_observed": np.isfinite(obs).sum(axis=1),
                      "obs_mean_cm": np.nanmean(obs, axis=1), "obs_p10_cm": np.nanpercentile(obs, 10, axis=1),
                      "obs_p90_cm": np.nanpercentile(obs, 90, axis=1), "sim_mean_cm": sim_mean_series,
                      "net_mm": np.nanmean(net, axis=1)}).to_csv(out / "neraca_series.csv", index=False)
        try:
            _plots(out, Z, dates, sim_mean, stn, cv, f"KHG {kid}: neraca air, held-out stations (Sy {params['sy']:.2f}, k {params['k']:.1f}, z0 {params['z0']:.0f})")
        except Exception as e:
            log.warning("plot failed: %s", e)
    log.info("parameters: %s", {k: params[k] for k in ("sy", "k", "z0")})

    if not nc["years"]:                                  # --calibrate-only
        return None, None, {"khg_id": kid, "n_units": n_units, "parameters": {k: params[k] for k in ("sy", "k", "z0")},
                            "calibration": cv_report}

    # ---- indicators per sub-KHG and baseline year ----
    rows = []
    c_u = np.array([cprox[label == u].mean() if (label == u).any() else 0.0 for u in range(n_units)])
    depth_u = [depth[label == u] for u in range(n_units)]
    w = None
    for y in nc["years"]:
        start, end = year_window(y, nc)
        f = FO.forcing_for(grid, era5, start, end, cache, nc["tz_hours"], int(era5.get("evap_stride", 3)), **nc["forcing"])
        if w is None:
            w = FO.unit_weights(label, n_units, grid, f["transform"], f["P"].shape[1:])
        T = len(f["dates"])
        Pu = f["P"].reshape(T, -1).astype("float64") @ w.T
        Eu = f["E"].reshape(T, -1).astype("float64") @ w.T
        for u in range(n_units):
            r = unit_indicators(f["dates"], Pu[:, u], Eu[:, u], depth_u[u], c_u[u], params["sy"], params["k"],
                                params["z0"], nc["dry_months"])
            rows.append({"unit_id": up["unit_id"].iloc[u], "khg_id": kid, "year": y, **r})
    by_year = pd.DataFrame(rows)
    num = [c for c in by_year.columns if c not in ("unit_id", "khg_id", "year")]
    unit = by_year.groupby(["khg_id", "unit_id"], sort=False)[num].mean().reset_index()
    unit["neraca_skill_ok"] = int(bool(cv_report and cv_report["verdict"]["usable_for_ranking"])) if cv_report else -1
    unit["u_mean_peat_depth_cm"] = [float(np.nanmean(d)) if d.size else np.nan for d in depth_u]
    unit["canal_proximity"] = c_u
    spread = {}
    for c in [c for c in num if c != "neraca_skill_ok"]:
        v = unit[c].values
        spread[c] = {"min": float(np.nanmin(v)), "median": float(np.nanmedian(v)), "max": float(np.nanmax(v)),
                     "spearman_with_peat_depth": _spearman(v, unit["u_mean_peat_depth_cm"]),
                     "spearman_with_canal_proximity": _spearman(v, c_u)}
    return unit, by_year, {"khg_id": kid, "n_units": n_units, "years": nc["years"], "parameters": {k: params[k] for k in ("sy", "k", "z0")},
                           "calibration": cv_report, "spread_across_sub_khg": spread}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config")
    ap.add_argument("--out")
    ap.add_argument("--calibrate-only", action="store_true", help="fit and score on SiTMAT stations, skip the indicators")
    ap.add_argument("--forcing-only", action="store_true", help="only read and cache the ERA5 forcing of every window (slow, once)")
    ap.add_argument("--rain", choices=["era5", "chirps"], help="rain source (overrides neraca.forcing.rain); chirps = CHIRPS v3, 5 km")
    ap.add_argument("--evap", choices=["era5", "wapor"], help="evaporation source (overrides neraca.forcing.evap); wapor = WaPOR v3, 300 m")
    ap.add_argument("--print-default-config", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    for noisy in ("azure", "rasterio._env", "rasterio._err", "fsspec", "pyogrio._io"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    if a.print_default_config:
        import yaml
        print(yaml.safe_dump(load_config(None, PRESET, "neraca"), sort_keys=False, allow_unicode=True))
        return
    cfg = load_config(a.config, PRESET, "neraca", None, a.out)
    cfg["neraca"]["forcing"] = {**cfg["neraca"]["forcing"], **{k: v for k, v in (("rain", a.rain), ("evap", a.evap)) if v}}
    if a.calibrate_only:
        cfg["neraca"]["years"] = []
    import geopandas as gpd
    t0 = time.time()
    if not cfg["khg"] or (not a.forcing_only and not cfg["units"].get("path")):
        raise SystemExit("set khg (boundary) and units.path (sub-KHG polygons)")
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    idf = cfg["khg_id_field"]
    if idf not in khg.columns:
        khg[idf] = [f"KHG{i + 1:02d}" for i in range(len(khg))]
    khg[idf] = khg[idf].astype(str)
    if a.forcing_only:
        for _, r in khg.iterrows():
            fetch_forcing(cfg, r[idf], r.geometry)
        return
    units = G.load_units(cfg, khg)
    out = Path(cfg["out"])
    out.mkdir(parents=True, exist_ok=True)
    units_all, by_year_all, reports = [], [], []
    for _, r in khg.iterrows():
        uk = units[units["khg_id"] == r[idf]]
        if not len(uk):
            continue
        u, by, rep = run_khg(cfg, r[idf], r.geometry, uk, out)
        if u is not None:
            units_all.append(u)
            by_year_all.append(by)
        reports.append(rep)
    if not reports:
        raise SystemExit("no sub-KHG matched a KHG")
    if units_all:
        pd.concat(units_all, ignore_index=True).to_csv(out / "neraca_unit.csv", index=False)
        pd.concat(by_year_all, ignore_index=True).to_csv(out / "neraca_unit_by_year.csv", index=False)
    with open(out / "neraca_report.json", "w", encoding="utf-8") as fh:
        json.dump({"runtime_s": round(time.time() - t0, 1), "khg": reports, "config": cfg["neraca"]}, fh, indent=2, default=str)
    log.info("done in %.0f s: %s", time.time() - t0, out / ("neraca_report.json" if a.calibrate_only else "neraca_unit.csv"))


if __name__ == "__main__":
    main()
