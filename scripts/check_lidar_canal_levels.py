"""How far below the land do mapped canals sit in a LiDAR DTM? A measured alternative to the canal levels per class the groundwater model
assumes (`--drawdown`, 1.2 m by default).

  python scripts/check_lidar_canal_levels.py --khg 14.10.01 --dtm $REPEAT_DATA/lidar_pulau_padang_2016/DTM_2mFloat.tif \
      --flown "November 2016" --out docs/reports/lidar_canal_levels_14.10.01.md                                  # needs REPEAT_KHG

Transects across canals of the KHG's `00_inputs/canals.gpkg` (class from KET_KANAL) at 4 points per segment, -150 to +150 m every DTM cell:
  at the line   lowest DTM value within --window m of the mapped line, minus the transect median (the land)
  control       the same at 100 m to either side, where there is no mapped canal
  found         share of transects whose lowest point lies within --window m of the line (chance: the window's share of the transect)
Over water a DTM holds a water-surface return or an interpolation from the banks, so the value at the line is the canal water level at the
flight date, or a shallower bound of it. Needs a DTM fine enough to resolve a canal (a few metres).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def main(argv=None):
    import geopandas as gpd
    import rasterio
    from shapely.geometry import box
    from repeat_common import khg as K
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True)
    ap.add_argument("--dtm", required=True)
    ap.add_argument("--flown", default="unknown", help="flight date, for the report")
    ap.add_argument("--window", type=float, default=10.0, help="half-width around the line, m")
    ap.add_argument("--per-class", type=int, default=600, help="segments sampled per class")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    r = rasterio.open(a.dtm)
    step = abs(r.res[0])
    offs = np.arange(-150, 150 + step / 2, step)
    near = np.abs(offs) <= a.window
    canals = gpd.read_file(K.folder(a.khg) / "00_inputs" / "canals.gpkg").to_crs(r.crs)
    canals = canals[canals.intersects(box(*r.bounds)) & (canals.length >= 60)]
    rows = []
    for cls, grp in canals.groupby("KET_KANAL"):
        Z = []
        for g in grp.sample(min(a.per_class, len(grp)), random_state=0).geometry:
            for f in (0.2, 0.4, 0.6, 0.8):
                p, q = g.interpolate(f, normalized=True), g.interpolate(f + 0.01, normalized=True)
                dx, dy = q.x - p.x, q.y - p.y
                n = np.hypot(dx, dy)
                if n == 0:
                    continue
                z = np.array([v[0] for v in r.sample([(p.x - o * dy / n, p.y + o * dx / n) for o in offs])], float)
                z[(z < -100) | (z == r.nodata)] = np.nan
                if np.isfinite(z).mean() > 0.9:
                    Z.append(z)
        Z = np.array(Z)
        land = np.nanmedian(Z, axis=1)
        wmin = lambda c: np.nanmin(Z[:, np.abs(offs - c) <= a.window], axis=1) - land
        line, ctl = wmin(0), np.r_[wmin(100), wmin(-100)]
        lowest = offs[np.nanargmin(Z, axis=1)]
        rows.append((cls, len(Z), np.nanquantile(line, [0.25, 0.5, 0.75]), np.nanmedian(ctl), np.mean(np.abs(lowest) <= a.window), near.mean()))
    L = [f"# Canal levels in the LiDAR DTM, KHG {a.khg}", "",
         f"Written by `scripts/check_lidar_canal_levels.py` from `{Path(a.dtm).name}` ({step:g} m, flown {a.flown}) and the KHG's mapped canals. "
         f"Depths are m below the land (transect median), window ±{a.window:g} m around the line.", "",
         "| class | transects | at the line: 25th / median / 75th percentile (m) | control at 100 m, median (m) | lowest point at the line | chance |",
         "|---|---|---|---|---|---|"]
    L += [f"| {c} | {n} | {-q[2]:.2f} / {-q[1]:.2f} / {-q[0]:.2f} | {-ct:.2f} | {fd:.0%} | {ch:.0%} |" for c, n, q, ct, fd, ch in rows]
    L += ["", "The value at the line is the canal water level on the flight date, or a shallower bound where the DTM interpolates over water. "
          "Transects where the mapped line misses the canal by more than the window dilute the median towards the control."]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
