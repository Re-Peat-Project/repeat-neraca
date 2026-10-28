"""Tier 1 neraca air at KHG level: one daily water table for the whole KHG, from physical parameters only.

    Sy(z) dz/dt = R - C(z) (z - z_c),     C(z) = 12 T(z) / L^2

z is the water table depth relative to the surface (m, negative below ground), R = P - ET (m/day), z_c = -canal_drawdown is the canal level
below the surface, T(z) the transmissivity above the peat bottom at that water table, and L the spacing of the drains.

The exchange coefficient 12 T / L^2 is the one that reproduces the steady state of a strip of width L between two drains with uniform
recharge: the mean head above the drain is R L^2 / (12 T) (tested against the 2D solver in tests/test_neraca.py). L = 1 / (canal length
per unit area). No parameter is fitted; Sy and T come from the peat table (`PeatTable`), the drawdown and the canal classes from the registry
and the config.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np


def drain_spacing_m(area_km2: float, canal_length_km: float) -> float:
    """Spacing of parallel drains that has the same length per area: L = 1 / D."""
    if canal_length_km <= 0:
        return float("inf")
    return area_km2 * 1e6 / (canal_length_km * 1e3)


def et_factor(z_start: float, z_end: float) -> Callable:
    """Share of the forcing evaporation that is realised at water table depth z (m, negative below ground): 1 above z_start, 0 below z_end, linear between."""
    return lambda z: float(min(1.0, max(0.0, (z - z_end) / (z_start - z_end))))


def simulate(net_m, sy_fn: Callable, t_fn: Callable, spacing_m: float, canal_drawdown: float, z0: float, max_substep_rate: float = 0.5) -> np.ndarray:
    """As `simulate_rain_et` with the net recharge given directly (no evaporation stress)."""
    net = np.asarray(net_m, float)
    return simulate_rain_et(np.where(np.isfinite(net), net, np.nan), np.zeros_like(net), sy_fn, t_fn, spacing_m, canal_drawdown, z0, None, max_substep_rate)


def simulate_rain_et(rain_m, et_m, sy_fn: Callable, t_fn: Callable, spacing_m: float, canal_drawdown: float, z0: float,
                     et_fn: Callable | None = None, max_substep_rate: float = 0.5) -> np.ndarray:
    """Daily water table depth (m, negative down) for daily rain and evaporation (m/day; NaN in either = no forcing that day: the state is kept, output NaN).

    Evaporation is multiplied by `et_fn(z)` (see `et_factor`) when given. sy_fn(z) and t_fn(z) take and return floats; sub-steps keep the explicit
    scheme stable when C/Sy is large.
    """
    rain = np.asarray(rain_m, float)
    et = np.asarray(et_m, float)
    net = rain - et
    z = float(min(z0, 0.0))
    zc = -float(canal_drawdown)
    out = np.full(net.shape, np.nan)
    for i in range(len(net)):
        if not np.isfinite(net[i]):
            continue
        rate = 12.0 * t_fn(z) / spacing_m ** 2 / max(sy_fn(z), 1e-6) if np.isfinite(spacing_m) else 0.0
        n = max(1, int(math.ceil(rate / max_substep_rate)))
        h = 1.0 / n
        for _ in range(n):
            sy = max(sy_fn(z), 1e-6)
            c = 12.0 * t_fn(z) / spacing_m ** 2 if np.isfinite(spacing_m) else 0.0
            r = rain[i] - et[i] * (et_fn(z) if et_fn else 1.0)
            z = min(z + h * (r - c * (z - zc)) / sy, 0.0)         # ponded water leaves
        out[i] = z
    return out
