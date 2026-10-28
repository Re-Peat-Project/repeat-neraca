"""Score a groundwater run against field water-table points (`fieldobs`), next to two simple predictions.

Points scored: on peat, with a depth, inside the KHG and not on a fixed (canal or edge) cell. The simulated depth of a point is the mean over
its window (date_from to date_to). Scores are given for all such points and for the unflagged ones.

Simple predictions, scored the same way:
  constant   the median observed depth everywhere
  distance   observed depth regressed on log(1 + distance to the nearest canal, m), fitted to the same points (in-sample, so it is favoured)

Gate (set 2026-10-28 before the first run; change it only with a reason in the report):
  the model's Spearman across points >= MIN_SPEARMAN, and above the Spearman of the distance prediction,
  and its RMSE below that of the constant prediction.
The gate decides whether the gridded water table can be used to say where the peat is dry. It is checked on the unflagged points.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

MIN_SPEARMAN = 0.3
DIST_BINS = [0, 100, 300, 1000, np.inf]


def _scores(obs, sim) -> dict:
    ok = np.isfinite(obs) & np.isfinite(sim)
    o, s = obs[ok], sim[ok]
    if ok.sum() < 8:
        return {"n": int(ok.sum())}
    sp = float(spearmanr(o, s).correlation) if np.std(s) > 0 else float("nan")
    return {"n": int(ok.sum()), "spearman": sp, "bias_cm": float(np.mean(s - o)), "rmse_cm": float(np.sqrt(np.mean((s - o) ** 2))),
            "mae_cm": float(np.mean(np.abs(s - o)))}


def canal_distance(points: pd.DataFrame, canals_path, crs) -> np.ndarray:
    """Distance (m) from each point to the nearest canal line of any class."""
    import geopandas as gpd
    c = gpd.read_file(canals_path).to_crs(crs)
    p = gpd.GeoSeries(gpd.points_from_xy(points.lon, points.lat), crs=4326).to_crs(crs)
    return p.distance(c.geometry.union_all()).values


def score(pts: pd.DataFrame) -> dict:
    """pts: obs_cm, sim_cm, dist_m, flag. Returns the scores of the model and the two predictions, and the gate."""
    out = {}
    for name, sel in (("all", np.ones(len(pts), bool)), ("unflagged", (pts["flag"] == "").values)):
        p = pts[sel]
        o, s, d = p.obs_cm.values, p.sim_cm.values, np.log1p(p.dist_m.values)
        const = np.full(len(o), np.median(o)) if len(o) else o
        b = np.polyfit(d, o, 1) if len(o) >= 8 else [0.0, np.nan]
        out[name] = {"model": _scores(o, s), "constant": _scores(o, const), "distance": _scores(o, np.polyval(b, d)),
                     "distance_fit": {"slope_cm_per_log_m": float(b[0]), "intercept_cm": float(b[1])}}
    u = out["unflagged"]
    p = pts[pts["flag"] == ""]
    if "group" in p and p["group"].nunique() > 1:          # how much of the observed spread is between field teams, not places
        mean = p.groupby("group").obs_cm.transform("mean")
        u["obs_variance_between_groups"] = float(1 - ((p.obs_cm - mean) ** 2).sum() / ((p.obs_cm - p.obs_cm.mean()) ** 2).sum())
        u["n_groups"] = int(p["group"].nunique())
    m, dist, const = u["model"], u["distance"], u["constant"]
    checks = {f"spearman >= {MIN_SPEARMAN}": m.get("spearman", np.nan) >= MIN_SPEARMAN,
              "spearman above the distance prediction": m.get("spearman", np.nan) > dist.get("spearman", np.nan),
              "rmse below the constant prediction": m.get("rmse_cm", np.inf) < const.get("rmse_cm", np.inf)}
    out["gate"] = {"checks": {k: bool(v) for k, v in checks.items()}, "pass": bool(all(checks.values()))}
    return out


def breakdown(pts: pd.DataFrame, by: str) -> pd.DataFrame:
    """Median observed and simulated depth, and n, per class of `by` (distance bins for dist_m)."""
    p = pts[pts["flag"] == ""].copy()
    key = pd.cut(p.dist_m, DIST_BINS, right=False) if by == "dist_m" else p[by]
    g = p.groupby(key, observed=True)
    t = pd.DataFrame({"n": g.size(), "obs_median_cm": g.obs_cm.median(), "sim_median_cm": g.sim_cm.median()})
    return t[t.n >= 5].round(1)


def day_sensitivity(obs_cm, sim_days_cm, dates) -> pd.DataFrame:
    """Spearman and bias of the model on each single day of the window (the survey dates are not known)."""
    rows = []
    for k, dte in enumerate(dates):
        s = _scores(obs_cm, sim_days_cm[k])
        rows.append({"date": str(dte.date()), "spearman": s.get("spearman"), "bias_cm": s.get("bias_cm"), "rmse_cm": s.get("rmse_cm")})
    return pd.DataFrame(rows)


MIN_TEMPORAL_R = 0.5         # station gate (set 2026-10-28 before the first station run): median per-station correlation of the daily series


def score_stations(obs: pd.DataFrame, sim: pd.DataFrame, info: pd.DataFrame, edge_days: int = 7) -> tuple[dict, pd.DataFrame]:
    """Score a run against water-table stations (daily depth, cm positive down).

    obs, sim: dates x stations. info: station_id, group (e.g. concession), dist_m, flag. A station counts with at least 30 days.
    Levels: each station's mean over its valid days, scored with `score` (model, constant and distance predictions; group share).
    Dynamics: per-station Pearson r of the daily series, the mean curve of the stations, and the drawdown (mean of the last minus the
    first `edge_days` valid days) across stations; all on the unflagged stations (a station on a fixed cell only shows the fixed level).
    Gate: the field gate on the levels, and the median per-station r >= MIN_TEMPORAL_R.
    """
    rows = []
    for sid in obs.columns:
        o, s = obs[sid].values, sim[sid].values
        ok = np.isfinite(o) & np.isfinite(s)
        if ok.sum() < 30:
            continue
        oo, ss = o[ok], s[ok]
        r = float(np.corrcoef(oo, ss)[0, 1]) if np.std(ss) > 0 and np.std(oo) > 0 else float("nan")
        rows.append({"station_id": sid, "days": int(ok.sum()), "obs_cm": float(oo.mean()), "sim_cm": float(ss.mean()), "r": r,
                     "obs_drawdown_cm": float(oo[-edge_days:].mean() - oo[:edge_days].mean()),
                     "sim_drawdown_cm": float(ss[-edge_days:].mean() - ss[:edge_days].mean())})
    t = pd.DataFrame(rows).merge(info, on="station_id", how="left")
    t["flag"] = t["flag"].fillna("")
    out = score(t)
    t_ok = t[t.flag == ""]
    cols = [c for c in obs.columns if c in set(t_ok.station_id)]
    obs, sim = obs[cols], sim[cols]
    ok = obs.notna() & sim.notna()
    om, sm = obs.where(ok).mean(axis=1), sim.where(ok).mean(axis=1)
    m = om.notna() & sm.notna()
    dyn = {"median_station_r": float(np.nanmedian(t_ok.r)), "n_stations": int(len(t)), "n_unflagged": int(len(t_ok)),
           "khg_mean_r": float(np.corrcoef(om[m], sm[m])[0, 1]) if m.sum() > 5 else float("nan"),
           "khg_mean_bias_cm": float((sm[m] - om[m]).mean()), "obs_khg_mean_cm": float(om[m].mean()), "sim_khg_mean_cm": float(sm[m].mean()),
           "drawdown_spearman": float(spearmanr(t_ok.obs_drawdown_cm, t_ok.sim_drawdown_cm).correlation) if len(t_ok) >= 8 else float("nan"),
           "obs_drawdown_median_cm": float(t_ok.obs_drawdown_cm.median()), "sim_drawdown_median_cm": float(t_ok.sim_drawdown_cm.median())}
    out["dynamics"] = dyn
    out["gate"]["checks"][f"median station r >= {MIN_TEMPORAL_R}"] = bool(dyn["median_station_r"] >= MIN_TEMPORAL_R)
    out["gate"]["pass"] = bool(all(out["gate"]["checks"].values()))
    return out, t
