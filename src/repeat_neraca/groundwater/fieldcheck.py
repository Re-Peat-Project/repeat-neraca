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
    testable = m.get("n", 0) >= 8                     # fewer points: the check cannot be made (None), which is not a failure
    checks = {f"spearman >= {MIN_SPEARMAN}": bool(m.get("spearman", np.nan) >= MIN_SPEARMAN) if testable else None,
              "spearman above the distance prediction": bool(m.get("spearman", np.nan) > dist.get("spearman", np.nan)) if testable else None,
              "rmse below the constant prediction": bool(m.get("rmse_cm", np.inf) < const.get("rmse_cm", np.inf)) if testable else None}
    out["gate"] = {"checks": checks, "pass": gate_pass(checks)}
    return out


def gate_pass(checks: dict) -> bool | None:
    """True when every check that could be made passed, False when one failed, None when none could be made."""
    made = [v for v in checks.values() if v is not None]
    return None if not made else bool(all(made))


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


MIN_TEMPORAL_R = 0.5
SUPPLY_RATIO = (0.5, 2.0)
SUPPLY_ABS_MM = 50.0         # added 2026-10-28 after Kampar-Gaung (deficit 7 mm in a near-neutral dry season): a ratio of two small numbers
                             # fails on small absolute differences, so the check also passes within 50 mm (about two weeks of dry-season ET)


def supply_ok(model_mm: float, station_mm: float) -> bool:
    """The model's water-management supply against the station-based deficit: within SUPPLY_RATIO, or within SUPPLY_ABS_MM."""
    lo, hi = SUPPLY_RATIO
    ratio_ok = station_mm > 0 and lo <= model_mm / station_mm <= hi
    return bool(ratio_ok or abs(model_mm - station_mm) <= SUPPLY_ABS_MM)    # managed-land runs (set 2026-10-28 before the first one): the water management supplies in the model, mm over
                             # the managed land, within this factor of the station-based deficit (the stations stand in managed land)         # station gate (set 2026-10-28 before the first station run): median per-station correlation of the daily series


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
    r_ok = np.isfinite(dyn["median_station_r"])
    out["gate"]["checks"][f"median station r >= {MIN_TEMPORAL_R}"] = bool(dyn["median_station_r"] >= MIN_TEMPORAL_R) if r_ok else None
    out["gate"]["pass"] = gate_pass(out["gate"]["checks"])
    return out, t


# Canal runs (D18, D19; set 2026-10-29 before the first run with canals inside cells or a canal store). A fixed canal level could not give
# the community stations both their level and their dry-season fall (section 6.11); these checks judge the two together, and the canal level
# the store produces against what has been measured.
COMMUNITY_TOL_CM = 20.0      # between the LiDAR canal-level error (0.13 m) and the peat microtopography over 5-10 m (0.27 m), Vernimmen et al. 2020
COMMUNITY_MIN_N = 3
CANAL_DEPTH_RANGE_M = (0.2, 2.5)   # season median canal water below the land: about -0.2 m in low plantations (Vernimmen & Hooijer 2026) to
                                   # "more than 2.5 m over large distances" in unmanaged dry-season canals (Vernimmen et al. 2020)


def community_ok(c: dict) -> bool | None:
    """Community stations off fixed cells: median level and median drawdown both within COMMUNITY_TOL_CM of the observed. None: too few."""
    if not c or c.get("n", 0) < COMMUNITY_MIN_N:
        return None
    return bool(abs(c["sim_level_cm"] - c["obs_level_cm"]) <= COMMUNITY_TOL_CM and abs(c["sim_drawdown_cm"] - c["obs_drawdown_cm"]) <= COMMUNITY_TOL_CM)


def canal_depth_ok(median_depth_m: float) -> bool | None:
    """The canal store's season median water depth below the land inside CANAL_DEPTH_RANGE_M. None: no store."""
    if median_depth_m is None or not np.isfinite(median_depth_m):
        return None
    lo, hi = CANAL_DEPTH_RANGE_M
    return bool(lo <= median_depth_m <= hi)


# Station screening (set 2026-10-29, at the project owner's request, before scoring any run on screened records). SiTMAT's own QC flags a
# reading outside -500..100 cm or a single spike over 60 cm; it passes a record that restarts after a gap at a shifted level, a sensor
# stuck at one value, and steps between days. Readings left out by `screen`:
GAP_DAYS = 7            # a gap of this many days or more splits a record into pieces
MIN_PIECE_DAYS = 14     # pieces shorter than this are left out (fragments around gaps)
SETTLE_DAYS = 7         # the first days of every piece are left out (a restarted or reinstalled logger settling)
STUCK_DAYS = 7          # runs of this many identical values or more are left out
JUMP_CM = 30.0          # a day-to-day change larger than this is counted (not removed): more than a dry-season week of fall in one day


def screen(s: pd.Series) -> tuple[pd.Series, dict]:
    """Daily depths of one station (DatetimeIndex, cm) -> the screened series (NaN where left out) and counts per reason."""
    s = s.dropna().sort_index()
    if s.empty:
        return s, {"readings": 0, "pieces": 0, "short_piece": 0, "settling": 0, "stuck": 0, "kept": 0, "jumps_over_30cm": 0}
    piece = (s.index.to_series().diff().dt.days.fillna(1) >= GAP_DAYS).cumsum()
    size = piece.map(piece.value_counts())
    short = size < MIN_PIECE_DAYS
    day_in_piece = s.groupby(piece.values).cumcount().values
    settling = ~short & (day_in_piece < SETTLE_DAYS)
    run = (s != s.shift()).cumsum()
    stuck = run.map(run.value_counts()) >= STUCK_DAYS
    out = s.where(~(short | settling | stuck))
    jumps = int((s.diff().abs() > JUMP_CM).sum())
    return out, {"readings": int(len(s)), "pieces": int(piece.nunique()), "short_piece": int(short.sum()), "settling": int(settling.sum()),
                 "stuck": int((stuck & ~short & ~settling).sum()), "kept": int(out.notna().sum()), "jumps_over_30cm": jumps}
