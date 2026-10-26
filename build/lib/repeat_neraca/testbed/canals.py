"""Canal cells of a gridded canal network and the water level they hold, with and without blocks.

Canal water level follows the rule used in Urzainki et al. (2020): without blocks it sits a fixed
distance below the local surface; a block raises its own cell and every upstream canal cell
(neighbouring canal cells with a higher surface) up to the block level. In the testbed the surface
is the true one, so this rule defines the true canal levels of the synthetic world. The
water-sharing model does not use it; it carries its own canal storage model.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


@dataclass
class CanalCells:
    cells: list                 # (row, col) of canal cell k; index 0 is a dummy
    label: np.ndarray           # (ny, nx) int, 0 where no canal
    upstream: list              # upstream canal labels of each label
    surface: np.ndarray         # surface elevation at each label (nan at 0)

    @classmethod
    def from_mask(cls, mask: np.ndarray, surface: np.ndarray) -> "CanalCells":
        ny, nx = mask.shape
        label = np.zeros((ny, nx), dtype=int)
        cells: list = [None]
        for k, (r, c) in enumerate(zip(*np.nonzero(mask)), start=1):   # row-major order
            label[r, c] = k
            cells.append((int(r), int(c)))
        up: list = [[] for _ in range(len(cells))]
        for k in range(1, len(cells)):
            r, c = cells[k]
            for dr, dc in NEIGHBOURS:
                rr, cc = r + dr, c + dc
                if 0 <= rr < ny and 0 <= cc < nx and label[rr, cc] > 0 and surface[rr, cc] > surface[r, c]:
                    up[k].append(int(label[rr, cc]))
        srf = np.array([np.nan] + [surface[c] for c in cells[1:]])
        return cls(cells, label, up, srf)

    @property
    def n(self) -> int:
        return len(self.cells) - 1

    def base_levels(self, drawdown: np.ndarray | float) -> np.ndarray:
        """Canal level without blocks: surface minus drawdown (scalar or per label)."""
        return self.surface - drawdown

    def levels(self, base: np.ndarray, blocks: dict[int, float]) -> np.ndarray:
        """Levels after building blocks. blocks maps a label to the level its crest holds."""
        wt = base.copy()
        for lab, height in blocks.items():
            queue = deque([lab])
            while queue:
                k = queue.popleft()
                if wt[k] < height:
                    wt[k] = height
                    queue.extend(self.upstream[k])
        return wt

    def to_raster(self, values: np.ndarray, fill: float = 0.0) -> np.ndarray:
        out = np.full(self.label.shape, fill, dtype=float)
        for k in range(1, len(self.cells)):
            out[self.cells[k]] = values[k]
        return out
