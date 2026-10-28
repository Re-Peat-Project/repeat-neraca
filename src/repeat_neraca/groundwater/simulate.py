"""Daily run of the 2D groundwater solver over a KHG grid, with a canal level per canal class, the water the fixed cells put into the peat,
and the simulated depth at given points.

    Sy(z) dh/dt = div( T(z) grad h ) + R,   R = P - ET of the KHG (one daily series)

Fixed heads: the KHG edge ring at `edge_stage` m below the local surface (river or sea), and the canal cells of each class at that class's
drawdown below the local surface. A class without a drawdown is not fixed (its cells behave as peat). The flux from fixed into free cells,
sum over shared faces of T_face (h_fixed - h_free), is the supply the boundary implies (negative: drainage out of the peat).
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from .grid import RealKHG
from .solver import PeatTable, solve


@dataclass
class Boundary:
    drawdown: dict                 # canal class -> m below the local surface (absent or None: that class is not fixed)
    edge_stage: float              # m below the local surface on the KHG edge ring
    managed: np.ndarray | None = None          # bool raster: managed land (e.g. plantation licences)
    drawdown_managed: dict | None = None       # canal class -> m below the surface for canal cells in managed land

    def heads(self, khg: RealKHG):
        """(fixed mask, fixed head, label raster: 0 free, 1 edge, 2 canal)."""
        fixed = khg.boundary & khg.domain
        head = np.where(fixed, khg.surface - self.edge_stage, 0.0)
        label = np.where(fixed, 1, 0)
        for cls in self.drawdown:
            cells = khg.canal[cls] & khg.domain & ~fixed                  # a cell in two classes keeps the first class's level
            parts = [(cells, self.drawdown.get(cls))]
            if self.managed is not None and self.drawdown_managed is not None:
                parts = [(cells & ~self.managed, self.drawdown.get(cls)), (cells & self.managed, self.drawdown_managed.get(cls))]
            for m, dd in parts:
                if dd is None:
                    continue
                head = np.where(m, khg.surface - float(dd), head)
                label = np.where(m, 2, label)
                fixed |= m
        return fixed, np.where(fixed, head, 0.0), label


def _faces(shape, domain):
    ny, nx = shape
    idx = np.arange(ny * nx).reshape(ny, nx)
    fa = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel()])
    fb = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel()])
    d = domain.ravel()
    ok = d[fa] & d[fb]
    return fa[ok], fb[ok]


def et_share(z: np.ndarray, z_start: float, z_end: float) -> np.ndarray:
    """Share of the forcing ET realised at water table depth z (m, negative below ground): 1 above z_start, 0 below z_end, linear between
    (PEATCLSM-Trop thresholds, Apers et al. 2022; the same rule as `lumped.et_factor`, per cell)."""
    return np.clip((z - z_end) / (z_start - z_end), 0.0, 1.0)


def run(khg: RealKHG, net_m_day, table: PeatTable, boundary: Boundary, h0_below_surface: float = 0.0, points=None, keep_days=None,
        log=None, rain_m_day=None, et_m_day=None, et_stress: tuple | None = None) -> dict:
    """net_m_day: daily P - ET (m/day). points: (rows, cols) of cells to sample each day. keep_days: bool per day, the days whose mean
    depth map is accumulated (the scoring window). et_stress (z_start, z_end): ET of each cell is scaled by `et_share` of its water table
    on the previous day (needs rain_m_day and et_m_day). Returns daily KHG series, the point series and the maps."""
    net = np.asarray(net_m_day, float)
    if et_stress is not None:
        rain, et = np.asarray(rain_m_day, float), np.asarray(et_m_day, float)
    T = len(net)
    fixed, head_fixed, label = boundary.heads(khg)
    free = khg.domain & ~fixed
    n_free = int(free.sum())
    depth_flat = khg.peat_depth.ravel()
    sy_fn = table.sy
    tr_fn = lambda zeta, cells: table.trans(zeta, depth_flat[cells])
    h = np.where(fixed, head_fixed, khg.surface - h0_below_surface)
    fa, fb = _faces(khg.shape, khg.domain)
    lab, fr = label.ravel(), free.ravel()
    to_free = (fr[fa] & (lab[fb] > 0)) | (fr[fb] & (lab[fa] > 0))
    fa, fb = fa[to_free], fb[to_free]
    src_is_a = lab[fa] > 0                                  # the fixed side of each face
    src_lab = np.where(src_is_a, lab[fa], lab[fb])
    cells = np.flatnonzero(khg.domain.ravel())
    series = {k: np.full(T, np.nan) for k in ("mean_depth_m", "share_deeper_0_4", "canal_in_mm", "edge_in_mm", "et_share")}
    pts = None if points is None else np.full((T, len(points[0])), np.nan)
    keep = np.zeros(T, bool) if keep_days is None else np.asarray(keep_days, bool)
    acc, n_acc = np.zeros(khg.shape), 0
    t0 = time.time()
    for t in range(T):
        if not np.isfinite(net[t]):
            continue
        r_t = net[t]
        if et_stress is not None:                                   # ET falls where yesterday's water table is deep
            share = et_share(h - khg.surface, *et_stress)
            r_t = rain[t] - et[t] * share
            series["et_share"][t] = float(share[free].mean())
        h = solve(khg.surface, khg.domain, khg.dx, fixed, head_fixed, h, [r_t], sy_fn, tr_fn)
        z = h - khg.surface
        series["mean_depth_m"][t] = float(z[free].mean())
        series["share_deeper_0_4"][t] = float((z[free] < -0.4).mean())
        tr = np.zeros(h.size)
        hf, zf = h.ravel(), z.ravel()
        tr[cells] = tr_fn(zf[cells], cells)
        g = 0.5 * (tr[fa] + tr[fb])
        q = g * np.where(src_is_a, hf[fa] - hf[fb], hf[fb] - hf[fa])            # m3/day into the free cell
        mm = 1000.0 / (n_free * khg.dx ** 2)
        series["canal_in_mm"][t] = float(q[src_lab == 2].sum() * mm)
        series["edge_in_mm"][t] = float(q[src_lab == 1].sum() * mm)
        if pts is not None:
            pts[t] = z[points]
        if keep[t]:
            acc += z
            n_acc += 1
        if log and t % 30 == 0:
            log(f"  day {t + 1} of {T} ({time.time() - t0:.0f} s), mean depth {-100 * series['mean_depth_m'][t]:.0f} cm")
    return {"series": series, "points": pts, "window_mean_depth_m": np.where(khg.domain, acc / max(n_acc, 1), np.nan),
            "final_depth_m": np.where(khg.domain, h - khg.surface, np.nan), "fixed": fixed, "label": label, "free": free,
            "seconds": time.time() - t0}
