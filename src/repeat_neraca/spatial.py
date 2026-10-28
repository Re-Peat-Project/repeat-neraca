"""Tier 2 neraca air: the 2D groundwater solver run daily over a real KHG.

    Sy(z) dh/dt = div( T(z) grad h ) + R

on the grid of `RealKHG` with the peat table of `repeat_neraca.groundwater` (storage and transmissivity as functions of water table depth),
fixed heads on the KHG edge ring (river or sea) and on the canal cells (local surface minus `canal_drawdown`), and the daily net recharge
R = P - ET of the whole KHG (one series; spatial forcing is a later step), with ET multiplied by `et_fn(z)` cell by cell when given. The initial water table is `initial_wtd` below the surface.

`k_multiplier` scales the transmissivity of the peat table (1 = the Urzainki et al. 2020 table, about 0.5 m2/day at the surface).
Returns the daily water table depth (m, negative below ground) averaged over the free cells (not canal, not edge), per sub-KHG, at the
stations, and the final map. No parameter is fitted.
"""
from __future__ import annotations

import time

import numpy as np

from .groundwater import PeatTable, solve
from .inputs import RealKHG, fixed_head


def run(khg: RealKHG, rain_m, et_m, table: PeatTable, canal_drawdown: float, river_stage_below_edge: float, initial_wtd: float,
        classes=("primary", "secondary"), k_multiplier: float = 1.0, et_fn=None, log=None) -> dict:
    rain = np.asarray(rain_m, float)
    et = np.asarray(et_m, float)
    net = rain - et
    fixed, head_fixed = fixed_head(khg, canal_drawdown, river_stage_below_edge, classes)
    free = khg.domain & ~fixed
    depth_flat = khg.peat_depth.ravel()
    h = np.where(khg.domain, khg.surface + initial_wtd, khg.surface)
    h = np.where(fixed, head_fixed, h)
    sy_fn = lambda zeta: table.sy(zeta)
    tr_fn = lambda zeta, cells: table.trans(zeta, depth_flat[cells], k_multiplier)
    T = len(net)
    stress = np.vectorize(et_fn) if et_fn else None
    mean = np.full(T, np.nan)
    share_deeper = np.full(T, np.nan)
    unit_series = None
    if khg.units is not None:
        unit_series = np.full((T, len(khg.unit_ids)), np.nan)
    st = khg.stations
    st_series = np.full((T, 0 if st is None else len(st)), np.nan)
    t0 = time.time()
    for t in range(T):
        if np.isfinite(net[t]):
            r_t = net[t]
            if stress is not None:                              # evaporation falls where the water table is deep
                r_t = rain[t] - et[t] * stress(h - khg.surface)
            h = solve(khg.surface, khg.domain, khg.dx, fixed, head_fixed, h, [r_t], sy_fn, tr_fn)
            z = h - khg.surface
            mean[t] = float(z[free].mean())
            share_deeper[t] = float((z[free] < -0.4).mean())
            if unit_series is not None:
                for k in range(len(khg.unit_ids)):
                    m = free & (khg.units == k)
                    if m.any():
                        unit_series[t, k] = float(z[m].mean())
            if st is not None and len(st):
                st_series[t] = z[st.row.values, st.col.values]
        if log and (t % 30 == 0):
            log(f"  day {t + 1} of {T}  ({time.time() - t0:.0f} s)")
    return {"mean": mean, "share_deeper_than_0.4": share_deeper, "units": unit_series, "stations": st_series, "final_depth": h - khg.surface,
            "free": free, "fixed": fixed}
