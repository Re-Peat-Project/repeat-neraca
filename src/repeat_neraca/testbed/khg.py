"""Synthetic KHG generator: peat dome, canals, structures, peat depth, land cover, loggers, pumps.

``generate(KHGConfig(seed=1))`` returns a ``SyntheticKHG`` of in-memory arrays and records. The
same seed always gives identical output. File writers and the truth run come in later steps.
All lengths are metres, elevations metres above one datum, water table depth negative below the
surface.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage

from .canals import CanalCells
from .fields import distance_to, gaussian_field

# model land-cover classes (methodology: Fire and land-cover layers)
LANDCOVER = {1: "forest", 2: "drained_forest", 3: "shrub_fern", 4: "burnt",
             5: "plantation", 6: "agriculture", 7: "settlement", 8: "water"}
CANAL_CLASS = {1: "primary", 2: "secondary"}


@dataclass(frozen=True)
class KHGConfig:
    seed: int = 1
    size_m: float = 10_000.0
    dx: float = 20.0
    z_river: float = 2.0                  # surface elevation at the river edge
    dome_relief: float = 4.0              # height of the dome centre above the edge
    micro_sd: float = 0.05                # micro-topography standard deviation (m)
    micro_corr_m: float = 150.0
    rotation_deg: float = 12.0            # canal grid rotation
    primary_spacing: float = 2000.0
    secondary_spacing: float = 600.0
    secondary_margin_cells: int = 6       # secondaries stop this far from the river
    drawdown_primary: float = 1.5         # canal level below the surface without blocks
    drawdown_secondary: float = 1.0
    block_head: float = 0.4               # distance from the surface to the top of a block
    width_primary: float = 8.0
    width_secondary: float = 4.0
    depth_primary: float = 3.0
    depth_secondary: float = 1.5
    n_blocks: int = 14
    n_gates: int = 4
    n_loggers: int = 12
    n_villages: int = 3
    river_stage_below_edge: float = 0.3


@dataclass
class SyntheticKHG:
    config: KHGConfig
    x: np.ndarray                         # (nx,) cell-centre x
    y: np.ndarray                         # (ny,) cell-centre y
    domain: np.ndarray                    # bool, inside the KHG
    boundary: np.ndarray                  # bool, outer ring where the river sets the head
    river_head: np.ndarray                # head at boundary cells
    surface: np.ndarray
    peat_depth: np.ndarray
    function_zone: np.ndarray             # 1 lindung (>= 3 m peat), 2 budidaya, 0 outside
    canal_class: np.ndarray               # 0 none, 1 primary, 2 secondary
    canals: CanalCells
    canal_drawdown: np.ndarray            # per canal label
    polylines: list                       # dicts: id, class, width_m, depth_m, xy (N, 2)
    structures: list                      # dicts
    landcover: np.ndarray
    burn_count: np.ndarray                # number of past fires per cell
    villages: list                        # dicts: id, x, y
    roads: list                           # (N, 2) arrays
    loggers: list                         # dicts
    water_sources: list                   # dicts
    pumps: list                           # dicts
    dist_canal: np.ndarray = field(repr=False, default=None)

    @property
    def shape(self) -> tuple[int, int]:
        return self.surface.shape

    def cell_of(self, x: float, y: float) -> tuple[int, int]:
        dx = self.config.dx
        return int(round((y - self.y[0]) / dx)), int(round((x - self.x[0]) / dx))

    def block_levels(self, structures: list | None = None) -> dict[int, float]:
        """Canal label -> level held, for existing blocks and gates held closed (dry-season default)."""
        out: dict[int, float] = {}
        base = self.canals.base_levels(self.canal_drawdown)
        for s in (self.structures if structures is None else structures):
            if s["status"] != "existing":
                continue
            lab = self.canals.label[s["cell"]]
            eta = s["condition"]
            crest = self.canals.surface[lab] - self.config.block_head
            out[int(lab)] = float(base[lab] + eta * (crest - base[lab]))
        return out


def _rotate(u, v, theta):
    c, s = np.cos(theta), np.sin(theta)
    return u * c - v * s, u * s + v * c


def _runs(flags: np.ndarray, min_len: int):
    """Contiguous True runs of a 1D boolean array as (start, stop) slices."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        if (not f or i == len(flags) - 1) and start is not None:
            stop = i + 1 if f else i
            if stop - start >= min_len:
                out.append((start, stop))
            start = None
    return out


def generate(cfg: KHGConfig = KHGConfig()) -> SyntheticKHG:
    ss = np.random.SeedSequence(cfg.seed).spawn(8)
    rng_shape, rng_micro, rng_canal, rng_struct, rng_lc, rng_vill, rng_log, rng_pump = (np.random.default_rng(s) for s in ss)
    n = int(round(cfg.size_m / cfg.dx))
    dx = cfg.dx
    x = (np.arange(n) + 0.5) * dx - cfg.size_m / 2
    y = x.copy()
    X, Y = np.meshgrid(x, y)
    half = 0.45 * cfg.size_m

    # --- domain: a rounded square with a wavy edge -------------------------------------------
    r_n = (np.abs(X / half) ** 2.5 + np.abs(Y / half) ** 2.5) ** (1 / 2.5)
    edge_noise = np.clip(gaussian_field((n, n), dx, 1200.0, rng_shape), -2, 2)
    r_eff = r_n * (1 + 0.06 * edge_noise)
    domain = r_eff <= 1.0
    inner = ndimage.binary_erosion(domain, structure=np.ones((3, 3)))
    boundary = domain & ~inner
    # --- surface: parabolic dome plus micro-topography ---------------------------------------
    r_dome = np.clip(r_eff, 0, 1)
    micro = gaussian_field((n, n), dx, cfg.micro_corr_m, rng_micro) * cfg.micro_sd
    surface = cfg.z_river + cfg.dome_relief * (1 - r_dome**2) + micro
    surface = np.where(domain, surface, cfg.z_river)
    river_head = np.where(boundary, cfg.z_river - cfg.river_stage_below_edge, 0.0)
    # --- peat depth and function zone --------------------------------------------------------
    pnoise = gaussian_field((n, n), dx, 600.0, rng_micro)
    peat_depth = np.clip(0.5 + 1.0 * (surface - cfg.z_river) + 0.3 * pnoise, 0.3, 9.0)
    peat_depth = np.where(domain, peat_depth, 0.0)
    function_zone = np.where(domain, np.where(peat_depth >= 3.0, 1, 2), 0)

    # --- canals: N-S primaries to the river, E-W secondaries between them ------------------
    theta = np.deg2rad(cfg.rotation_deg)
    step = dx / 2
    s_axis = np.arange(-cfg.size_m, cfg.size_m + step, step)
    eroded = ndimage.binary_erosion(domain, iterations=cfg.secondary_margin_cells)

    def in_mask(mask, px, py):
        c = np.rint((px - x[0]) / dx).astype(int)
        r = np.rint((py - y[0]) / dx).astype(int)
        ok = (c >= 0) & (c < n) & (r >= 0) & (r < n)
        res = np.zeros(px.shape, bool)
        res[ok] = mask[r[ok], c[ok]]
        return res

    primaries_u = np.arange(-2, 3) * cfg.primary_spacing + rng_canal.uniform(-200, 200)
    primaries_u = primaries_u[np.abs(primaries_u) < 0.9 * half]
    secondaries_v = np.arange(-8, 9) * cfg.secondary_spacing + rng_canal.uniform(-100, 100)
    polylines = []
    canal_class = np.zeros((n, n), dtype=int)

    def add_line(u, v, cls, mask):
        px, py = _rotate(u, v, theta)
        for a, b in _runs(in_mask(mask, px, py), 5):
            xy = np.c_[px[a:b], py[a:b]]
            polylines.append({"id": f"C{len(polylines) + 1:03d}", "class": CANAL_CLASS[cls],
                              "width_m": cfg.width_primary if cls == 1 else cfg.width_secondary,
                              "depth_m": cfg.depth_primary if cls == 1 else cfg.depth_secondary, "xy": xy})
            cc = np.rint((xy[:, 0] - x[0]) / dx).astype(int)
            rr = np.rint((xy[:, 1] - y[0]) / dx).astype(int)
            for r, c in zip(rr, cc):
                if canal_class[r, c] == 0 or cls < canal_class[r, c]:
                    canal_class[r, c] = cls

    for u in primaries_u:
        add_line(np.full_like(s_axis, u), s_axis, 1, domain)
    edges = np.concatenate([[-np.inf], np.sort(primaries_u), [np.inf]])
    for v in secondaries_v:
        for lo, hi in zip(edges[:-1], edges[1:]):
            u = s_axis[(s_axis >= max(lo, -cfg.size_m)) & (s_axis <= min(hi, cfg.size_m))]
            if u.size > 5:
                add_line(u, np.full_like(u, v), 2, eroded)
    canal_class = np.where(domain, canal_class, 0)
    canal_class[boundary & (canal_class == 2)] = 0
    canal_mask = canal_class > 0
    canals = CanalCells.from_mask(canal_mask, surface)
    drawdown = np.full(canals.n + 1, np.nan)
    for k in range(1, canals.n + 1):
        drawdown[k] = cfg.drawdown_primary if canal_class[canals.cells[k]] == 1 else cfg.drawdown_secondary

    # --- structures: existing blocks on secondaries, gates where secondaries meet primaries ---
    structures = []
    sec_cells = [k for k in range(1, canals.n + 1) if canal_class[canals.cells[k]] == 2 and inner[canals.cells[k]]]
    chosen: list[int] = []
    for k in rng_struct.permutation(sec_cells):
        r, c = canals.cells[k]
        if all(np.hypot(r - canals.cells[j][0], c - canals.cells[j][1]) * dx > 400 for j in chosen):
            chosen.append(int(k))
        if len(chosen) >= cfg.n_blocks:
            break
    junction = []
    for k in range(1, canals.n + 1):
        r, c = canals.cells[k]
        if canal_class[r, c] == 2:
            win = canal_class[max(r - 1, 0):r + 2, max(c - 1, 0):c + 2]
            if (win == 1).any():
                junction.append(k)
    gates = [int(k) for k in rng_struct.permutation(junction)[: cfg.n_gates]] if junction else []
    for i, k in enumerate(chosen):
        r, c = canals.cells[k]
        structures.append({"id": f"B{i + 1:03d}", "type": "block", "status": "existing", "x": float(x[c]), "y": float(y[r]),
                           "cell": (r, c), "condition": float(np.clip(rng_struct.beta(3, 2), 0.1, 1.0)),
                           "year_built": int(rng_struct.integers(2016, 2023)),
                           "crest_elev_m": float(surface[r, c] - cfg.block_head)})
    for i, k in enumerate(gates):
        r, c = canals.cells[k]
        structures.append({"id": f"G{i + 1:03d}", "type": "gate", "status": "existing", "x": float(x[c]), "y": float(y[r]),
                           "cell": (r, c), "condition": float(np.clip(rng_struct.beta(4, 2), 0.2, 1.0)),
                           "year_built": int(rng_struct.integers(2016, 2023)),
                           "crest_elev_m": float(surface[r, c] - cfg.block_head)})

    # --- villages, roads, land cover ---------------------------------------------------------
    ring = domain & ~ndimage.binary_erosion(domain, iterations=25)
    ring_cells = np.argwhere(ring)
    pick = rng_vill.choice(len(ring_cells), cfg.n_villages, replace=False)
    villages = [{"id": f"V{i + 1}", "x": float(x[c]), "y": float(y[r])} for i, (r, c) in enumerate(ring_cells[pick])]
    roads = []
    for a, b in zip(villages[:-1], villages[1:]):
        t = np.linspace(0, 1, 60)
        roads.append(np.c_[a["x"] + t * (b["x"] - a["x"]), a["y"] + t * (b["y"] - a["y"])])
    dist_canal = distance_to(canal_mask, dx)
    pressure = np.exp(-dist_canal / 250.0)
    n1 = gaussian_field((n, n), dx, 700.0, rng_lc)
    n2 = gaussian_field((n, n), dx, 400.0, rng_lc)
    edge_access = 1 - np.clip((surface - cfg.z_river) / cfg.dome_relief, 0, 1)      # easier to reach near the river
    score = 0.35 * pressure + 0.35 * (n1 - n1.min()) / (np.ptp(n1) + 1e-9) + 0.30 * edge_access
    pct = np.zeros((n, n))
    order = np.argsort(score[domain])
    ranks = np.empty(order.size)
    ranks[order] = np.arange(order.size) / order.size
    pct[domain] = ranks                                                   # percentile of degradation pressure
    lc = np.ones((n, n), dtype=int)
    lc[pct >= 0.30] = 2
    lc[pct >= 0.55] = 3
    lc[(pct >= 0.80) & (n2 > 0)] = 4
    # plantation in one corner block, agriculture and settlement around villages
    corner = (X > 0.15 * cfg.size_m) & (Y < -0.1 * cfg.size_m) & (Y > -0.38 * cfg.size_m)
    lc[corner & (lc <= 3)] = 5
    for v in villages:
        d = np.hypot(X - v["x"], Y - v["y"])
        lc[(d < 1200) & (lc != 5)] = 6
        lc[d < 400] = 7
    lc = np.where(domain, lc, 8)
    burn_count = np.where(lc == 4, rng_lc.integers(1, 4, (n, n)), 0)

    # --- loggers across distance-to-canal classes --------------------------------------------
    loggers = []
    classes = [(5, 50), (50, 300), (300, 5000)]
    cand = domain & inner & ~canal_mask & ndimage.binary_erosion(domain, iterations=10)
    for i in range(cfg.n_loggers):
        lo, hi = classes[i % 3]
        ok = np.argwhere(cand & (dist_canal >= lo) & (dist_canal < hi))
        r, c = ok[rng_log.integers(len(ok))]
        loggers.append({"id": f"L{i + 1:02d}", "x": float(x[c]), "y": float(y[r]), "cell": (int(r), int(c)),
                        "ground_elev_m": float(surface[r, c]), "dist_canal_m": float(dist_canal[r, c])})

    # --- water sources (river intakes near primary outlets) and pumps ------------------------
    sources = []
    prim_boundary = [(r, c) for r, c in np.argwhere(boundary)
                     if (canal_class[max(r - 3, 0):r + 4, max(c - 3, 0):c + 4] == 1).any()]
    for i, idx in enumerate(rng_pump.permutation(len(prim_boundary))[:3]):
        r, c = prim_boundary[idx]
        sources.append({"id": f"S{i + 1}", "type": "river", "x": float(x[c]), "y": float(y[r]), "cell": (int(r), int(c)),
                        "dry_season_supply": True, "brackish": False})
    pumps = [{"id": "P1", "capacity_m3h": 22.0, "lift_m": 4.0, "fuel_l_per_h": 4.9, "units_available": 8},
             {"id": "P2", "capacity_m3h": 100.0, "lift_m": 6.0, "fuel_l_per_h": 20.0, "units_available": 2},
             {"id": "P3", "capacity_m3h": 22.0, "lift_m": 4.0, "fuel_l_per_h": 4.9, "units_available": 4}]

    return SyntheticKHG(cfg, x, y, domain, boundary, river_head, surface, peat_depth, function_zone, canal_class,
                        canals, drawdown, polylines, structures, lc, burn_count, villages, roads, loggers,
                        sources, pumps, dist_canal)
