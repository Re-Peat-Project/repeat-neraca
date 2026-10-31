"""Daily run of the 2D groundwater solver over a KHG grid, with a canal level per canal class, the water the fixed cells put into the peat,
and the simulated depth at given points.

    Sy(z) dh/dt = div( T(z) grad h ) + R,   R = P - ET of the KHG (one daily series)

Fixed heads: the KHG edge ring at `edge_stage` m below the local surface (river or sea), and the canal cells of each class at that class's
drawdown below the local surface. A class without a drawdown is not fixed (its cells behave as peat). The flux from fixed into free cells,
sum over shared faces of T_face (h_fixed - h_free), is the supply the boundary implies (negative: drainage out of the peat).

Managed land held at a target (`managed_target`, m below the surface per cell, NaN outside managed land): canal cells there are fixed at the
target, and each day a free managed cell whose water table fell below its target is brought back to it. The water this takes, the storage
of the peat table at the target minus that at the water table, is the supply of water management (mm over the managed free cells, and m3).
Peat base (`peat_base`): no ET is taken from a cell whose water table is below the peat (depth > peat depth).

Canals narrower than a cell (`leak_length`, D18): the canal cells of the unmanaged land stay free and exchange
q = LEAK_K (L/dx) max(1, L/dx) T(z) (h_canal - h) with a canal of length L inside the cell, at the class's level below the local surface.
Canal store (`store`, D19): that level moves. One store per sub-KHG (one for the KHG without units) holds the canal water; each day
    A dy = sum q_exchange + (P - E) A - A max(0, y) / tau
with A the canal water surface (length x width per class), y the store's level relative to the class levels (the outlet sill), solved
implicitly and iterated with the groundwater step. A canal whose level reaches its bed is dry and only drains the cell.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from .grid import CLASSES, RealKHG
from . import solver
from .solver import PeatTable, solve

LEAK_K = 12.0       # D18: the mean head of a strip drained by a canal through it, under uniform recharge q and spacing s, lies q s^2 / (12 T)
                    # above the canal (Hooghoudt parabola, mean = 2/3 of the midpoint rise), so a canal crossing a cell has C = 12 T.
                    # Checked against a 5 m grid: scripts/check_subcell_canal.py, docs/reports/subcell_canal_check.md


@dataclass
class CanalStore:
    width: dict                    # canal class -> water surface width, m
    bed: dict                      # canal class -> bed below the local surface, m (a class level deeper than its bed moves the bed down)
    tau_days: float = 1.0          # water above the sill (y > 0) leaves through the outlet with this time constant
    iterations: int = 8            # coupling iterations of store and groundwater per day (secant per store)
    tol_m: float = 1e-4


@dataclass
class Boundary:
    drawdown: dict                 # canal class -> m below the local surface (absent or None: that class is not fixed)
    edge_stage: float              # m below the local surface on the KHG edge ring
    managed: np.ndarray | None = None          # bool raster: managed land (e.g. plantation licences)
    drawdown_managed: dict | None = None       # canal class -> m below the surface for canal cells in managed land
    managed_target: np.ndarray | None = None   # m below the surface per cell, held by water management (NaN outside managed land)
    canal_override: np.ndarray | None = None   # m below the surface per cell: canal water level set by a scenario (block reaches), NaN elsewhere
    leak_length: dict | None = None            # canal class -> m of canal per cell: canals narrower than a cell (D18) instead of fixed cells
    store: CanalStore | None = None            # canal water balance per sub-KHG (D19); needs leak_length

    def heads(self, khg: RealKHG):
        """(fixed mask, fixed head, label raster: 0 free, 1 edge, 2 canal)."""
        fixed = khg.boundary & khg.domain
        head = np.where(fixed, khg.surface - self.edge_stage, 0.0)
        label = np.where(fixed, 1, 0)
        for cls in (self.drawdown if self.leak_length is None else ()):  # leaky canals stay free (`leak`)
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
        if self.managed_target is not None:                                # canals in managed land are held at the target
            canal = np.zeros(khg.shape, bool)
            for cls in self.drawdown:
                canal |= khg.canal[cls]
            m = canal & khg.domain & ~(khg.boundary & khg.domain) & np.isfinite(self.managed_target)
            head = np.where(m, khg.surface - np.nan_to_num(self.managed_target), head)
            label = np.where(m, 2, label)
            fixed |= m
        if self.canal_override is not None:                                # a block holds the canal water of its reach at the reach's level
            m = np.isfinite(self.canal_override) & khg.domain & ~(khg.boundary & khg.domain)
            level = khg.surface - np.nan_to_num(self.canal_override)
            head = np.where(m & fixed & (label == 2), np.maximum(head, level), np.where(m, level, head))   # keep the higher of two levels
            label = np.where(m, 2, label)
            fixed |= m
        return fixed, np.where(fixed, head, 0.0), label

    def leak(self, khg: RealKHG, fixed: np.ndarray) -> dict:
        """Canals narrower than a cell, on cells not fixed (D18): per cell the factor of the exchange, the canal level below the surface
        (the first class present: primary, secondary, tertiary), and for the store the bed below the surface and the water surface (m2)."""
        L, depth = np.zeros(khg.shape), np.full(khg.shape, np.nan)
        bed, area = np.full(khg.shape, np.nan), np.zeros(khg.shape)
        for cls in CLASSES:
            dd = self.drawdown.get(cls)
            if dd is None:
                continue
            ln = self.leak_length[cls]
            first = np.isnan(depth) & (ln > 0)
            L += ln
            depth = np.where(first, float(dd), depth)
            if self.store is not None:
                bed = np.where(first, max(float(self.store.bed[cls]), float(dd)), bed)
                area += ln * float(self.store.width[cls])
        cells = (L > 0) & khg.domain & ~fixed
        r = L / khg.dx
        return {"cells": cells, "factor": np.where(cells, LEAK_K * r * np.maximum(1.0, r), 0.0), "depth": np.where(cells, depth, np.nan),
                "bed": np.where(cells, bed, np.nan), "area": np.where(cells, area, 0.0)}


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
        log=None, rain_m_day=None, et_m_day=None, et_stress: tuple | None = None, peat_base: bool = False, season_days=None,
        log_ponding: bool = False, supply_cap_mm: float | None = None, supply_cap_days=None) -> dict:
    """net_m_day: daily P - ET (m/day). points: (rows, cols) of cells to sample each day. keep_days: bool per day, the days whose mean
    depth map is accumulated (the scoring window). et_stress (z_start, z_end): ET of each cell is scaled by `et_share` of its water table
    on the previous day (needs rain_m_day and et_m_day). supply_cap_mm: water management adds at most this much (mm, per managed cell) over
    the days flagged in supply_cap_days; a cell that has used its budget is no longer topped up and falls with the water table (the last
    top-up is exact: storage rises by the remaining budget only). Returns daily KHG series, the point series and the maps."""
    net = np.asarray(net_m_day, float)
    if et_stress is not None or peat_base or boundary.store is not None:
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
    lk = None if boundary.leak_length is None else boundary.leak(khg, fixed)
    st = None
    if lk is not None:
        lc = lk["cells"]
        base = khg.surface - np.nan_to_num(lk["depth"])                 # canal level at the sill (y = 0)
        bedl = khg.surface - np.nan_to_num(lk["bed"])
        st = boundary.store
        if st is not None:                                              # one store per sub-KHG; cells outside the units, or no units: one more
            sid = (khg.units if khg.units is not None else np.zeros(khg.shape, int))[lc]
            store_ids, si = np.unique(sid, return_inverse=True)
            ns = len(store_ids)
            A = np.bincount(si, weights=lk["area"][lc], minlength=ns)
            n_cells = np.bincount(si, minlength=ns)
            y = np.zeros(ns)
            y_floor = np.array([np.min((bedl - base)[lc][si == k]) for k in range(ns)])   # every canal of the store at its bed
            stage = np.full((T, ns), np.nan)
            cdepth = np.full((T, ns), np.nan)                           # mean canal water depth below the land per store, m
            d_c, b_c = lk["depth"][lc], lk["bed"][lc]
            closure = np.full(T, np.nan)
    series = {k: np.full(T, np.nan) for k in ("mean_depth_m", "share_deeper_0_4", "canal_in_mm", "edge_in_mm", "et_share",
                                               "unmanaged_mean_depth_m", "unmanaged_share_deeper_0_4", "managed_supply_mm", "managed_supply_m3")}
    target = boundary.managed_target
    held = None if target is None else (free & np.isfinite(target))         # free cells kept at the target by water management
    open_ = free if held is None else (free & ~held)
    zt = None if target is None else -np.nan_to_num(target)
    pts = None if points is None else np.full((T, len(points[0])), np.nan)
    keep = np.zeros(T, bool) if keep_days is None else np.asarray(keep_days, bool)
    acc, n_acc = np.zeros(khg.shape), 0
    season = np.zeros(T, bool) if season_days is None else np.asarray(season_days, bool)   # e.g. the dry season: per-cell totals
    s_deep, s_depth, s_supply, n_season = np.zeros(khg.shape), np.zeros(khg.shape), np.zeros(khg.shape), 0
    capd = None if supply_cap_mm is None else np.asarray(supply_cap_days, bool)
    used = np.zeros(khg.shape)                                     # supply cap: mm already supplied per cell in the window
    ponded = np.full((T, 2), np.nan) if log_ponding else None      # mm removed as ponding, share of free cells that ponded (last solve of the day)
    t0 = time.time()
    for t in range(T):
        if not np.isfinite(net[t]):
            continue
        if log_ponding:
            solver.PONDED_LOG = []
        r_t = net[t]
        if et_stress is not None or peat_base:                      # ET falls where yesterday's water table is deep, none below the peat
            zp = h - khg.surface
            share = et_share(zp, *et_stress) if et_stress is not None else np.ones(khg.shape)
            if peat_base:
                share = np.where(zp < -khg.peat_depth, 0.0, share)
            r_t = rain[t] - et[t] * share
            series["et_share"][t] = float(share[free].mean())
        if lk is None:
            h = solve(khg.surface, khg.domain, khg.dx, fixed, head_fixed, h, [r_t], sy_fn, tr_fn)
        else:
            h, hc, lf, cf = _leak_day(khg, h, r_t, fixed, head_fixed, sy_fn, tr_fn, lk, base, bedl,
                                  None if st is None else (st, y, si, A, y_floor, rain[t], et[t]))
            if st is not None:
                y, closure[t] = cf
                stage[t] = y
                cdepth[t] = np.bincount(si, weights=np.clip(d_c - y[si], 0.0, b_c), minlength=ns) / n_cells
        if log_ponding:
            ponded[t] = solver.PONDED_LOG[-1]
            solver.PONDED_LOG = None
        z = h - khg.surface
        if held is not None:                                        # water management tops the managed cells up to their target
            low = held & (z < zt)
            if capd is not None and capd[t]:
                low &= used < supply_cap_mm
                s_now = np.interp(z[low], table.zeta, table.storage)
                add = np.minimum(np.interp(zt[low], table.zeta, table.storage) - s_now, (supply_cap_mm - used[low]) / 1000.0)
                full = np.zeros(khg.shape)
                full[low] = np.interp(s_now + add, table.storage, table.zeta)      # new level of the topped-up cells
                h = np.where(low, khg.surface + full, h)
                used[low] += add * 1000.0
            else:
                add = np.interp(zt[low], table.zeta, table.storage) - np.interp(z[low], table.zeta, table.storage)
                h = np.where(low, khg.surface + zt, h)
            z = h - khg.surface
            series["managed_supply_m3"][t] = float(add.sum() * khg.dx ** 2)
            if season[t]:
                s_supply[low] += add * 1000.0                            # mm
            series["managed_supply_mm"][t] = float(add.sum() * 1000.0 / max(held.sum(), 1))
            series["unmanaged_mean_depth_m"][t] = float(z[open_].mean()) if open_.any() else np.nan
            series["unmanaged_share_deeper_0_4"][t] = float((z[open_] < -0.4).mean()) if open_.any() else np.nan
        series["mean_depth_m"][t] = float(z[free].mean())
        series["share_deeper_0_4"][t] = float((z[free] < -0.4).mean())
        tr = np.zeros(h.size)
        hf, zf = h.ravel(), z.ravel()
        tr[cells] = tr_fn(zf[cells], cells)
        g = 0.5 * (tr[fa] + tr[fb])
        q = g * np.where(src_is_a, hf[fa] - hf[fb], hf[fb] - hf[fa])            # m3/day into the free cell
        mm = 1000.0 / (n_free * khg.dx ** 2)
        series["canal_in_mm"][t] = float(q[src_lab == 2].sum() * mm)
        if lk is not None:                                          # exchange with the canals inside free cells, at the level of the step
            series["canal_in_mm"][t] += float((lf[lc] * tr.reshape(khg.shape)[lc] * (hc[lc] - h[lc])).sum() * mm)
        series["edge_in_mm"][t] = float(q[src_lab == 1].sum() * mm)
        if pts is not None:
            pts[t] = z[points]
        if keep[t]:
            acc += z
            n_acc += 1
        if season[t]:
            s_deep += z < -0.4
            s_depth += z
            n_season += 1
        if log and t % 30 == 0:
            log(f"  day {t + 1} of {T} ({time.time() - t0:.0f} s), mean depth {-100 * series['mean_depth_m'][t]:.0f} cm")
    return {"series": series, "points": pts, "window_mean_depth_m": np.where(khg.domain, acc / max(n_acc, 1), np.nan),
            "final_depth_m": np.where(khg.domain, h - khg.surface, np.nan), "fixed": fixed, "label": label, "free": free, "held": held,
            "season_days_deeper_0_4": np.where(khg.domain, s_deep, np.nan), "season_mean_depth_m": np.where(khg.domain, s_depth / max(n_season, 1), np.nan),
            "season_supply_mm": np.where(khg.domain, s_supply, np.nan), "season_n_days": n_season,
            "seconds": time.time() - t0, "leak": lk, "ponded": ponded,
            "canal_stage": None if st is None else {"store_ids": store_ids, "y_m": stage, "closure_m3": closure, "area_m2": A, "cells": n_cells,
                                               "depth_m": cdepth}}


def _canal_head(y_cells, base, bedl, surface):
    """Canal water level per cell: the sill level plus the store's y, not below the bed, not above the land; and whether it is wet."""
    hc = base + y_cells
    return np.clip(hc, bedl, surface), hc > bedl


def _leak_day(khg, h, r_t, fixed, head_fixed, sy_fn, tr_fn, lk, base, bedl, store):
    """One day with canals inside free cells. Without a store the canal level is the class level. With a store, the store's level and the
    groundwater are iterated: groundwater with the canal at the level of the guess, then the store's level solved implicitly with those
    heads (linear in y for wet canals; a dry canal drains the cell at its bed, independent of y); the next guess is a secant step per store
    on guess minus result. Returns h, the canal level used, the exchange factor used, and
    (y, closure m3: the exchange the groundwater saw minus the exchange the store booked)."""
    lc = lk["cells"]
    if store is None:
        hc = np.where(lc, base, 0.0)
        return solve(khg.surface, khg.domain, khg.dx, fixed, head_fixed, h, [r_t], sy_fn, tr_fn, leak_factor=lk["factor"], leak_head=hc, linear="cg"), hc, lk["factor"], None
    st, y0, si, A, y_floor, p, e = store
    ns = len(A)
    cells = np.flatnonzero(lc.ravel())
    y = y0.copy()
    prev = None
    for _ in range(st.iterations):
        hc_c, wet = _canal_head(y[si], base[lc], bedl[lc], khg.surface[lc])
        f = lk["factor"].copy()
        f[lc] = np.where(~wet & (h[lc] <= bedl[lc]), 0.0, f[lc])         # a dry canal cannot feed the peat: no exchange
        hc = np.zeros(khg.shape)
        hc[lc] = hc_c
        h_new = solve(khg.surface, khg.domain, khg.dx, fixed, head_fixed, h, [r_t], sy_fn, tr_fn, leak_factor=f, leak_head=hc, linear="cg")
        hn = h_new[lc]
        c = f[lc] * tr_fn(hn - khg.surface[lc], cells)
        G = np.bincount(si, weights=np.where(wet, c, 0.0), minlength=ns)
        X = np.bincount(si, weights=np.where(wet, c * (hn - base[lc]), c * np.maximum(hn - bedl[lc], 0.0)), minlength=ns)
        num = A * y0 + X + (p - e) * A
        y_new = num / np.maximum(A + G, 1e-9)
        y_new = np.where(y_new > 0, num / np.maximum(A + G + A / st.tau_days, 1e-9), y_new)
        y_new = np.maximum(y_new, y_floor)
        done = np.max(np.abs(y_new - y)) < st.tol_m
        hb, _ = _canal_head(y_new[si], base[lc], bedl[lc], khg.surface[lc])
        closure = float((c * (hc_c - hn)).sum() - (c * (hb - hn)).sum())   # into the peat at the level used, minus what the store booked
        if done:
            break
        g = y_new - y                                                  # secant on g(y) = F(y) - y, per store; a plain step where it stalls
        nxt = y_new
        if prev is not None:
            dg = g - prev[1]
            ok = np.abs(dg) > 1e-12
            nxt = np.where(ok, y - g * (y - prev[0]) / np.where(ok, dg, 1.0), y_new)
        prev = (y, g)
        y = np.maximum(nxt, y_floor)
    y = y_new
    return h_new, hc, f, (y, closure)
