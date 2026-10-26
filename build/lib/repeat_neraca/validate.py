"""Compare a physical neraca air run with the observed water tables, without fitting anything.

Observed depths come from `stations_daily.csv` (cm below the surface, positive down); the model works in metres, negative below ground, so
simulated values are converted with depth_cm = -100 z. The first `SKIP` days are spin-up and are not scored.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SKIP = 14
MIN_SPATIAL_SKILL = 0.3     # Spearman of the dry-season peak depth across stations below which per-sub-KHG outputs are flagged unusable for ranking (skill_ok = 0)


def observed_wide(inputs_dir: str | Path, dates: pd.DatetimeIndex) -> pd.DataFrame:
    d = pd.read_csv(Path(inputs_dir) / "stations_daily.csv", parse_dates=["date"])
    return d.pivot(index="date", columns="station_id", values="depth_cm").reindex(dates)


def _rho(a, b):
    from scipy.stats import spearmanr
    ok = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[ok], b[ok]).correlation) if ok.sum() >= 8 else float("nan")


def khg_level(sim_depth_cm: np.ndarray, obs: pd.DataFrame) -> dict:
    """The KHG-mean simulated curve against the mean observed curve of the stations."""
    o = obs.mean(axis=1).values
    s = np.asarray(sim_depth_cm, float)
    ok = np.isfinite(o) & np.isfinite(s)
    ok[:SKIP] = False
    if ok.sum() < 5:
        return {}
    r = float(np.corrcoef(o[ok], s[ok])[0, 1]) if np.std(s[ok]) > 0 and np.std(o[ok]) > 0 else float("nan")
    return {"days": int(ok.sum()), "bias_cm": float(np.mean(s[ok] - o[ok])), "rmse_cm": float(np.sqrt(np.mean((s[ok] - o[ok]) ** 2))),
            "r": r, "obs_mean_cm": float(np.mean(o[ok])), "sim_mean_cm": float(np.mean(s[ok])),
            "rmse_after_removing_bias_cm": float(np.sqrt(np.mean((s[ok] - o[ok] - np.mean(s[ok] - o[ok])) ** 2)))}


def station_level(sim_depth_cm: np.ndarray, obs: pd.DataFrame, station_ids) -> dict:
    """Station by station: pooled error, error of the mean level, and the Spearman of the dry-season peak depth across stations."""
    o = obs.reindex(columns=list(station_ids)).values
    s = np.asarray(sim_depth_cm, float)
    ok = np.isfinite(o) & np.isfinite(s)
    ok[:SKIP] = False
    if ok.sum() < 20:
        return {}
    d = np.where(ok, s - o, np.nan)
    mean_o = np.array([np.nanmean(np.where(ok[:, j], o[:, j], np.nan)) for j in range(o.shape[1])])
    mean_s = np.array([np.nanmean(np.where(ok[:, j], s[:, j], np.nan)) for j in range(o.shape[1])])
    peak_o = np.array([np.nanpercentile(np.where(ok[:, j], o[:, j], np.nan), 95) if ok[:, j].sum() > 5 else np.nan for j in range(o.shape[1])])
    peak_s = np.array([np.nanpercentile(np.where(ok[:, j], s[:, j], np.nan), 95) if ok[:, j].sum() > 5 else np.nan for j in range(o.shape[1])])
    return {"n_stations": int(o.shape[1]), "pooled_bias_cm": float(np.nanmean(d)), "pooled_rmse_cm": float(np.sqrt(np.nanmean(d ** 2))),
            "spearman_mean_level": _rho(mean_s, mean_o), "spearman_peak_depth": _rho(peak_s, peak_o),
            "obs_mean_level_cm": float(np.nanmean(mean_o)), "sim_mean_level_cm": float(np.nanmean(mean_s)),
            "obs_peak_range_cm": [float(np.nanmin(peak_o)), float(np.nanmax(peak_o))]}
