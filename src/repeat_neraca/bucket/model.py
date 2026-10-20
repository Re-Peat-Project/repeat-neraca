"""
The water-table bucket of the neraca air module (definition in repeat_neraca/bucket/README.md).

    N(d) = P(d) - E(d)                                        mm/day
    z(d) = clip( z(d-1) - (N(d) - k*c) / (10*Sy), 0, D )      cm below the peat surface

Everything here is plain numpy so it can be tested without data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def simulate(net, sy, k=0.0, c=0.0, z0=0.0, depth=np.inf):
    """Water-table depth z (cm, positive down) for one or many series.

    net    daily P - E in mm; shape (T,) or (T, N)
    sy     effective storage coefficient (scalar)
    k      drainage coefficient, mm/day
    c      canal proximity, 0..1; scalar or (N,)
    z0     starting depth, cm (scalar or (N,))
    depth  peat depth cap, cm (scalar or (N,))
    Returns an array (T, N) (N = 1 for a single series). NaN days keep the previous state and give NaN.
    """
    net = np.asarray(net, dtype="float64")
    if net.ndim == 1:
        net = net[:, None]
    T, N = net.shape
    c = np.broadcast_to(np.asarray(c, dtype="float64"), (N,))
    depth = np.broadcast_to(np.asarray(depth, dtype="float64"), (N,))
    z = np.broadcast_to(np.asarray(z0, dtype="float64"), (N,)).copy()
    z = np.clip(z, 0, depth)
    out = np.empty((T, N))
    loss = k * c
    for t in range(T):
        n = net[t]
        step = (n - loss) / (10.0 * sy)
        z = np.where(np.isfinite(n), np.clip(z - step, 0, depth), z)
        out[t] = np.where(np.isfinite(n), z, np.nan)
    return out


def _runs(dry: np.ndarray) -> list[int]:
    """Lengths of the runs of True in a boolean array."""
    out, n = [], 0
    for d in dry:
        if d:
            n += 1
        elif n:
            out.append(n)
            n = 0
    if n:
        out.append(n)
    return out


def unit_indicators(dates, P, E, depth_px_cm, c_u, sy, k, z0, dry_months=(6, 7, 8, 9, 10),
                    dry_mm=1.0, z_thr_cm=40.0) -> dict:
    """The neraca air indicators of one sub-KHG for one year.

    dates       local days (DatetimeIndex), spin-up months included
    P, E        daily rain and evaporation of the sub-KHG, mm (T,)
    depth_px_cm peat depth of the pixels of the sub-KHG, cm
    c_u         canal proximity of the sub-KHG, 0..1
    """
    dates = pd.DatetimeIndex(dates)
    P, E = np.asarray(P, "float64"), np.asarray(E, "float64")
    net = P - E
    z = simulate(net, sy, k, c_u, z0)[:, 0]                       # uncapped: the cap is applied per pixel below
    dry = np.isin(dates.month, list(dry_months)) & np.isfinite(net)
    if not dry.any():
        return {}
    zd, nd = z[dry], net[dry]
    peak = float(np.nanmax(zd))
    depth = np.asarray(depth_px_cm, "float64")
    depth = depth[np.isfinite(depth) & (depth > 0)]
    decline = float(np.mean(np.minimum(peak, depth) / depth) * 100) if depth.size else np.nan
    monthly = pd.Series(nd, index=dates[dry]).groupby(dates[dry].month).sum()
    runs = _runs(P[dry] < dry_mm)
    return {"u_wb_daily_mean": float(np.mean(nd)),
            "u_deficit_months_dry": int((monthly < 0).sum()),
            "u_dry_days_mean": float(np.mean(runs)) if runs else 0.0,
            "u_storage_decline_pct": decline,
            "u_wt_peak_cm": peak,
            "u_wt_days_gt40": float(np.mean(zd > z_thr_cm))}
