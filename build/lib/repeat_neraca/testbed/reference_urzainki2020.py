"""Reference reproduction of the Siak benchmark of Urzainki et al. (2020).

Re-implements the data preparation, the canal water level rule and the evaluation used by
`LukeEcomod/blopti` (MIT) on top of the SI solver in `groundwater.py`, so the paper's stored block
configurations can be re-evaluated. Needs rasterio and the Siak rasters from that repository
(python3/data/Strat4). This module is a benchmark aid, not part of the decision model: the canal
water level rule (DEM minus a constant, raised upstream by neighbouring-pixel DEM comparison) is
exactly the terrain-sensitive step the water-sharing model replaces.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.signal

from .groundwater import PeatTable, solve

CROP = (slice(7, -7), slice(5, -15))                      # empty rows and columns of the clip
DEPTH_BY_TYPE = {1: 2.0, 2: 2.0, 3: 4.0, 4: 0.0, 5: 0.0, 6: 2.0, 7: 4.0, 8: 8.0}
K_FACTOR_BY_TYPE = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 0.0, 6: 0.5, 7: 0.5, 8: 0.5}
NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# configurations stored in the repository (python3/main.py and python3/output/results_ga_3.txt)
GA_5 = [9259, 7242, 135, 3230, 5842]
GA_10 = [6831, 9089, 1445, 7233, 1895, 7050, 783, 5841, 7289, 3173]
RULE_BASED_10 = [11170, 10237, 10514, 2932, 4794, 8921, 4785, 5837, 7300, 6868]
# results stored in python3/output/concise_output_opti.txt: dry peat volume as % of the no-block case
PAPER_PERCENT = {"GA_5": 99.41, "GA_10": 98.87}


def _peel(catchment: np.ndarray) -> np.ndarray:
    """Outermost ring of cells inside the catchment (where the fixed-head boundary is applied)."""
    kernel = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 0, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
    b = scipy.signal.convolve2d(catchment, kernel, boundary="fill", fillvalue=False)
    peel = np.ones(catchment.shape, bool)
    peel[b[2:-2, 2:-2] == 0] = False
    peel[b[2:-2, 2:-2] == 20] = False
    return (catchment * peel) > 0


@dataclass
class Siak:
    dem: np.ndarray
    ptype: np.ndarray
    depth: np.ndarray
    canal_cells: list           # (row, col) of canal pixel k; index 0 is a dummy
    neighbours: list            # upstream canal labels for each canal label
    domain: np.ndarray
    peel: np.ndarray
    inner: np.ndarray
    kfactor: np.ndarray
    table: PeatTable
    block_height: float = 0.4
    canal_depth: float = 1.2
    et_mm: float = 3.0
    k_adjust: float = 1.5
    dx: float = 100.0

    @classmethod
    def load(cls, folder: str | Path) -> "Siak":
        import rasterio

        folder = Path(folder)

        def read(name):
            with rasterio.open(folder / name) as r:
                return r.read(1)

        dem, can, pt = read("DTM_metres_clip.tif"), read("canals_clip.tif"), read("Peattypedepth_clip.tif")
        can = can.copy()
        can[can < 0.5] = 0
        can[abs(can) > 0.5] = 1
        can = can.astype(int)
        dem = dem.astype(float)
        dem[dem < -10] = -9999.0
        dem[np.isnan(dem)] = -9999.0
        dem[dem > 1e20] = -9999.0
        pt = pt.astype("int16")
        pt[pt < 0] = -1
        pt[pt < 0.1] = 1                                    # as the original (its `and` keeps the second condition)
        depth = np.ones(pt.shape)
        for t, d in DEPTH_BY_TYPE.items():
            depth[pt == t] = d
        depth[depth < 0.1] = 1.0
        dem, can, pt, depth = (a[CROP] for a in (dem, can, pt, depth))
        depth = np.maximum(depth, 2.0)

        label = np.zeros(can.shape, int)
        cells = [None]
        k = 0
        for (r, c), v in np.ndenumerate(can):
            if v > 0 and dem[r, c] > 0:
                k += 1
                label[r, c] = k
                cells.append((r, c))
        ny, nx = dem.shape
        up = [[] for _ in range(k + 1)]
        for lab in range(1, k + 1):
            r, c = cells[lab]
            for dr, dc in NEIGHBOURS:
                rr, cc = r + dr, c + dc
                if 0 <= rr < ny and 0 <= cc < nx and label[rr, cc] > 0 and dem[rr, cc] - dem[r, c] > 0:
                    up[lab].append(int(label[rr, cc]))

        catchment = dem >= -10
        peel = _peel(catchment)
        inner = catchment & ~peel
        kf = np.ones(pt.shape)
        for t, f in K_FACTOR_BY_TYPE.items():
            kf[pt == t] = f
        return cls(dem, pt, depth, cells, up, inner | peel, peel, inner, kf, PeatTable.urzainki2020())

    @property
    def n_canals(self) -> int:
        return len(self.canal_cells) - 1

    def canal_levels(self, blocks: list[int]) -> np.ndarray:
        """Canal water level per canal label after building blocks (the paper's rule)."""
        srf = np.array([np.nan] + [self.dem[c] for c in self.canal_cells[1:]])
        wt = srf - self.canal_depth
        for b in blocks:
            height = srf[b] - self.block_height
            queue = deque([b])
            while queue:
                c = queue.popleft()
                if wt[c] < height:
                    wt[c] = height
                    queue.extend(self.neighbours[c])
        return wt

    def run(self, blocks: list[int], days: int = 3) -> dict:
        wt = self.canal_levels(blocks)
        ny, nx = self.dem.shape
        canal_head = np.zeros((ny, nx))
        canal_mask = np.zeros((ny, nx), bool)
        for lab in range(1, self.n_canals + 1):
            canal_head[self.canal_cells[lab]] = wt[lab]
            canal_mask[self.canal_cells[lab]] = True
        canal_mask &= self.inner                           # boundary cells win over canals
        fixed = self.peel | canal_mask
        head = np.where(self.peel, self.dem, canal_head)
        surface = np.where(self.domain, self.dem, 0.0)
        depth, kf = self.depth.ravel(), (self.kfactor * self.k_adjust).ravel()
        table = self.table

        def trans(zeta, cells):
            return table.trans(zeta, depth[cells], kf[cells])

        h = solve(surface, self.domain, self.dx, fixed, head, np.where(self.domain, surface, 0.0),
                  [-self.et_mm * 1e-3] * days, table.sy, trans, dt=1.0)
        peat = self.inner & ~canal_mask & ~np.isin(self.ptype, (4, 5))
        dry = float(np.sum((surface - h)[peat]) * self.dx**2 / 1e4)       # ha m
        return {"dry_volume_ha_m": dry, "mean_wtd_m": float(np.mean((h - surface)[peat])),
                "canal_rise_m": float(np.nansum(wt[1:] - (np.array([self.dem[c] for c in self.canal_cells[1:]]) - self.canal_depth)))}
