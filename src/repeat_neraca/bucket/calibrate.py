"""
Fit the neraca air bucket to SiTMAT stations and measure how well it does on stations it was not fitted on.

Two kinds of skill, kept apart:
  temporal  per-station correlation of the daily series: is the seasonal drawdown and its timing right?
  spatial   Spearman across stations of simulated against observed peak depth and days deeper than 40 cm:
            does the model say which places dry out more? This is what the sub-KHG ranking needs.
Both are scored on stations in spatial blocks that were left out of the fit, and compared with a no-skill baseline
(every station follows the mean observed curve of the stations that were used for the fit).
"""
from __future__ import annotations

import copy
import logging

import numpy as np
import pandas as pd
from scipy.cluster.vq import kmeans2
from scipy.stats import spearmanr

from repeat_common import tma as TMA
from .model import simulate

log = logging.getLogger("prioritas.neraca")


def load_stations(cfg: dict, polygon_ll, start, end) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily water-table depth in cm (positive down), days x stations, for the stations inside polygon_ll."""
    import geopandas as gpd
    c = copy.deepcopy(cfg)
    c.setdefault("tma", {})["period"] = [str(pd.Timestamp(start).date()), str(pd.Timestamp(end).date())]
    t = TMA.load(c, [])
    if t is None or not len(t):
        raise RuntimeError("no water-table readings: set tma.path to the SiTMAT folder")
    meta = t.groupby("station_id").agg(lon=("lon", "first"), lat=("lat", "first")).reset_index()
    pts = gpd.GeoDataFrame(meta, geometry=gpd.points_from_xy(meta.lon, meta.lat), crs=4326)
    keep = pts[pts.within(polygon_ll)]["station_id"]
    t = t[t["station_id"].isin(keep)]
    Z = t.pivot(index="date", columns="station_id", values="depth_m") * 100.0
    Z.index = pd.DatetimeIndex(Z.index).normalize()
    meta = meta[meta["station_id"].isin(Z.columns)].set_index("station_id").loc[Z.columns].reset_index()
    log.info("stations inside the KHG: %d with at least %.0f%% coverage", Z.shape[1],
             100 * float(cfg.get("tma", {}).get("min_coverage", 0.5)))
    return Z, meta


def sample_grid(arr: np.ndarray, grid, lon, lat) -> np.ndarray:
    """Values of a raster on the analysis grid at the given longitudes and latitudes (NaN outside)."""
    from pyproj import Transformer
    from rasterio.transform import rowcol
    x, y = Transformer.from_crs(4326, grid.crs, always_xy=True).transform(np.asarray(lon), np.asarray(lat))
    r, c = rowcol(grid.transform, x, y)
    r, c = np.asarray(r), np.asarray(c)
    ok = (r >= 0) & (r < arr.shape[0]) & (c >= 0) & (c < arr.shape[1])
    out = np.full(len(r), np.nan)
    out[ok] = arr[r[ok], c[ok]]
    return out


def season_stats(z: np.ndarray, in_season: np.ndarray, thr_cm: float = 40.0) -> tuple[np.ndarray, np.ndarray]:
    """Peak (95th percentile) depth and share of days deeper than thr_cm, per column, over the season days."""
    zz = z[in_season]
    n = np.isfinite(zz).sum(axis=0)
    with np.errstate(all="ignore"):
        peak = np.nanpercentile(zz, 95, axis=0)
        days = np.where(n > 0, ((zz > thr_cm) & np.isfinite(zz)).sum(axis=0) / np.maximum(n, 1), np.nan)
    return np.where(n > 0, peak, np.nan), days


def fit(net, obs, depth, c, grids: dict, skip: int = 14) -> dict:
    """Grid search of (sy, k, z0) minimising the pooled RMSE between simulated and observed depth."""
    best = None
    for sy in grids["sy"]:
        for k in grids["k"]:
            for z0 in grids["z0"]:
                sim = simulate(net, sy, k, c, z0, depth)
                err = (sim - obs)[skip:]
                m = np.isfinite(err)
                if m.sum() < 50:
                    continue
                rmse = float(np.sqrt(np.mean(err[m] ** 2)))
                if best is None or rmse < best["rmse"]:
                    best = {"sy": float(sy), "k": float(k), "z0": float(z0), "rmse": rmse}
    if best is None:
        raise RuntimeError("calibration found no usable station data")
    return best


def _rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.nanstd(a[ok]) == 0 or np.nanstd(b[ok]) == 0:
        return None
    r = spearmanr(a[ok], b[ok]).correlation
    return None if not np.isfinite(r) else float(r)


def cross_validate(net, obs, depth, c, lonlat, in_season, grids, blocks: int = 4, skip: int = 14, seed: int = 0) -> dict:
    """Leave-one-spatial-block-out fit and score. Returns metrics plus the out-of-fold simulation."""
    n = obs.shape[1]
    cent, lab = kmeans2(lonlat.astype(float), min(blocks, n), minit="++", seed=seed)
    sim_oof = np.full_like(obs, np.nan)
    base_oof = np.full_like(obs, np.nan)
    fits = []
    for b in np.unique(lab):
        te, tr = lab == b, lab != b
        f = fit(net[:, tr], obs[:, tr], depth[tr], c[tr], grids, skip)
        fits.append({"block": int(b), "n_test": int(te.sum()), **f})
        sim_oof[:, te] = simulate(net[:, te], f["sy"], f["k"], c[te], f["z0"], depth[te])
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                base_oof[:, te] = np.nanmean(obs[:, tr], axis=1, keepdims=True)
    m = np.isfinite(obs) & np.isfinite(sim_oof) & np.isfinite(base_oof)
    m[:skip] = False
    rmse = float(np.sqrt(np.mean((sim_oof[m] - obs[m]) ** 2)))
    rmse_base = float(np.sqrt(np.mean((base_oof[m] - obs[m]) ** 2)))
    r_t = []
    for j in range(n):
        ok = m[:, j]
        if ok.sum() >= 30 and np.std(sim_oof[ok, j]) > 0 and np.std(obs[ok, j]) > 0:
            r_t.append(np.corrcoef(sim_oof[ok, j], obs[ok, j])[0, 1])
    sim_s = np.where(np.isfinite(obs), sim_oof, np.nan)                  # score the model on the days observed
    op, od = season_stats(obs, in_season)
    sp, sd = season_stats(sim_s, in_season)
    bp, _ = season_stats(np.where(np.isfinite(obs), base_oof, np.nan), in_season)
    return {"fits": fits, "n_stations": int(n), "blocks": int(len(np.unique(lab))),
            "rmse_cm": rmse, "rmse_baseline_cm": rmse_base,
            "temporal_r_median": float(np.median(r_t)) if r_t else None,
            "temporal_r_q25_q75": [float(np.percentile(r_t, 25)), float(np.percentile(r_t, 75))] if r_t else None,
            "spatial_spearman_peak": _rho(op, sp), "spatial_spearman_days_gt40": _rho(od, sd),
            "peak_rmse_cm": float(np.sqrt(np.nanmean((sp - op) ** 2))),
            "peak_rmse_baseline_cm": float(np.sqrt(np.nanmean((bp - op) ** 2))),
            "_sim_oof": sim_oof, "_obs_peak": op, "_sim_peak": sp, "_obs_days": od, "_sim_days": sd, "_block": lab}


def covariate_skill(obs_peak, obs_days, depth, canal_dist) -> dict:
    """What single covariates explain: Spearman of the observed peak depth (and days > 40 cm) with each."""
    return {"peak_vs_peat_depth": _rho(obs_peak, depth), "peak_vs_canal_distance": _rho(obs_peak, canal_dist),
            "days_gt40_vs_peat_depth": _rho(obs_days, depth), "days_gt40_vs_canal_distance": _rho(obs_days, canal_dist)}
