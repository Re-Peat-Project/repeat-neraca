"""Does a canal narrower than a cell need the whole cell fixed at the canal level? A numerical check of the leak term of `solver.solve`
against a fine grid that resolves the canal.

  python scripts/check_subcell_canal.py --out docs/reports/subcell_canal_check.md

Parallel canals `--spacing` m apart in flat peat (tropical-large table, peat 4 m), canal level `--level` m below the land, a dry spell of
`--days` days at `--et` mm/day from a saturated start. Reference: a 5 m grid with the canal cells (10 m) fixed. Each coarse grid (100 and
200 m; the canal through a cell centre at 100 m, 50 m off it at 200 m) is run with
  fixed      every cell the canal touches fixed at the canal level (the model up to now, `all_touched`)
  leak k     the canal cells free, exchanging q = k (L/dx) max(1, L/dx) T(zeta) (h_canal - h) with the canal (L: canal length in the cell)
Scored: each coarse cell's depth against the mean of the reference over the same land, day `--days`; and the mean over all land.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from repeat_neraca.groundwater.solver import PeatTable, solve


def strip(dx, width, canals, ny=3):
    nx = int(round(width / dx))
    xc = (np.arange(nx) + 0.5) * dx
    return nx, ny, xc


def run(dx, width, canals, level, days, et, table, depth, mode, k=None):
    nx, ny, xc = strip(dx, width, canals)
    surface = np.zeros((ny, nx))
    domain = np.ones((ny, nx), bool)
    fixed = np.zeros((ny, nx), bool)
    lf = np.zeros((ny, nx))
    for c in canals:
        if mode == "reference":
            fixed[:, np.abs(xc - c) < 5.0] = True
        else:
            col = int(np.floor(c / dx))
            touched = [col] if abs(c - col * dx) > 1e-9 else [col - 1, col]          # a line on a cell edge touches both cells
            for j in touched:
                if mode == "fixed":
                    fixed[:, j] = True
                else:
                    L = dx / len(touched)                                            # the line's length shared between the cells it lies on
                    lf[:, j] += k * (L / dx) * max(1.0, L / dx)
    head = np.full((ny, nx), -level)
    tr = lambda zeta, cells: table.trans(zeta, np.full(len(cells), depth))
    kw = {} if mode != "leak" else {"leak_factor": lf, "leak_head": np.full((ny, nx), -level)}
    h = solve(surface, domain, dx, fixed, head, np.where(fixed, -level, 0.0), [-et / 1000.0] * days, table.sy, tr, **kw)
    return xc, h[1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spacing", default="300,500", help="canal spacings, m")
    ap.add_argument("--level", type=float, default=0.8)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--et", type=float, default=4.0)
    ap.add_argument("--depth", type=float, default=4.0)
    ap.add_argument("--table", default="tropical-large")
    ap.add_argument("--k", default="4,8,12,24")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    table = PeatTable.named(a.table)
    rows = []
    for spacing in (float(v) for v in a.spacing.split(",")):
        width = 2 * spacing
        canals = [spacing / 2, 3 * spacing / 2]
        xr, hr = run(5.0, width, canals, a.level, a.days, a.et, table, a.depth, "reference")
        for dx in (100.0, 200.0):
            nx = int(round(width / dx))
            ref = np.array([hr[(xr >= j * dx) & (xr < (j + 1) * dx)].mean() for j in range(nx)])      # reference mean over each coarse cell
            for mode, k in [("fixed", None)] + [("leak", float(v)) for v in a.k.split(",")]:
                _, h = run(dx, width, canals, a.level, a.days, a.et, table, a.depth, mode, k)
                rows.append((spacing, -100 * hr.mean(), dx, "fixed cells" if mode == "fixed" else f"leak k = {k:g}",
                             100 * np.sqrt(np.mean((h - ref) ** 2)), 100 * (h.mean() - hr.mean()), -100 * h.mean()))
    L = ["# Canals narrower than a cell: leak term against a fine grid", "",
         f"Written by `scripts/check_subcell_canal.py`. Parallel canals {a.spacing.replace(",", " and ")} m apart, level {a.level:g} m below flat land, peat "
         f"{a.depth:g} m, `{a.table}`, {a.days} days at {a.et:g} mm/day from saturation. Reference: 5 m grid, canal 10 m wide. "
         "At 100 m the canal runs through a cell centre, at 200 m 50 m off it. Depths on the last day.", "",
         "| spacing (m) | reference land mean (cm) | grid (m) | canal | cell RMSE against the reference (cm) | bias of the land mean (cm) | land mean depth (cm) |",
         "|---|---|---|---|---|---|---|"]
    L += [f"| {sp:g} | {rm:.1f} | {dx:g} | {m} | {r:.1f} | {b:+.1f} | {d:.1f} |" for sp, rm, dx, m, r, b, d in rows]
    L += ["", "Bias: positive when the coarse grid is wetter than the reference. Fixed cells count at the canal level."]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
