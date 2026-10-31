"""Audit the canal layer of a KHG for what the groundwater model assumes about it: lines that connect, classes that are consistent along a canal.

  python scripts/check_canal_topology.py --khg 15.05-07-10.01 --out docs/reports/canal_topology_15.05-07-10.01.md      # tolerances: --snap 15 --gap 150

Reads `00_inputs/canals.gpkg` (class field `KET_KANAL`), `rivers.gpkg` and `khg.gpkg` of the KHG folder, in the UTM zone of the KHG. Per class:
  segments, length (km)
  dangles      end points with no other canal within `snap` m, and not within `snap` m of a river or the KHG edge (a free end)
  gap pairs    two dangles of different segments within `gap` m of each other: a likely break in a canal that continues
  isolated     segments with no canal within `snap` m at either end (a stub not connected to anything)
Network: connected components (ends within `snap` m), the share of canal length in components that reach a river, the KHG edge or a primary canal,
and class flips: a segment whose class differs from every neighbour at both ends (for example a tertiary piece between two primary ones), which is
the pattern of a mis-classed line. These counts show where the layer is open or inconsistent; they do not say which class is right.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.strtree import STRtree

from repeat_common import khg as K

CLASSES = {"Kanal Primer": "primary", "Kanal Sekunder": "secondary", "Kanal Tersier": "tertiary"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--snap", type=float, default=15.0, help="m within which two ends count as connected")
    ap.add_argument("--gap", type=float, default=150.0, help="m within which two dangles count as a likely break")
    a = ap.parse_args(argv)
    folder = Path(K.folder(a.khg)) / "00_inputs"
    khg = gpd.read_file(folder / "khg.gpkg")
    crs = khg.estimate_utm_crs()
    khg = khg.to_crs(crs)
    c = gpd.read_file(folder / "canals.gpkg").to_crs(crs).explode(index_parts=False).reset_index(drop=True)
    c = c[c.geometry.type == "LineString"].reset_index(drop=True)
    c["cls"] = c.KET_KANAL.map(CLASSES)
    c["len_km"] = c.length / 1000
    edge = khg.geometry.union_all().boundary
    rv = folder / "rivers.gpkg"
    rivers = gpd.read_file(rv).to_crs(crs).geometry.union_all() if rv.exists() else None
    outlet = edge if rivers is None else edge.union(rivers)

    tree = STRtree(list(c.geometry))
    ends = [(i, Point(g.coords[0])) for i, g in enumerate(c.geometry)] + [(i, Point(g.coords[-1])) for i, g in enumerate(c.geometry)]
    nbrs = {i: set() for i in range(len(c))}
    dangle, near_outlet = [], []
    for i, p in ends:
        hit = {j for j in tree.query(p.buffer(a.snap), predicate="intersects") if j != i}
        nbrs[i] |= hit
        at_outlet = p.distance(outlet) <= a.snap
        dangle.append(not hit and not at_outlet)
        near_outlet.append(at_outlet)
    n = len(c)
    c["dangles"] = [dangle[k] + dangle[k + n] for k in range(n)]
    c["at_outlet"] = [near_outlet[k] or near_outlet[k + n] for k in range(n)]
    c["isolated"] = [(not nbrs[k]) and not c.at_outlet[k] for k in range(n)]

    dpts = [(i, p) for (i, p), d in zip(ends, dangle) if d]
    dtree = STRtree([p for _, p in dpts])
    gap_pairs = set()
    for k, (i, p) in enumerate(dpts):
        for m in dtree.query(p.buffer(a.gap), predicate="intersects"):
            if dpts[m][0] != i:
                gap_pairs.add(tuple(sorted((i, dpts[m][0]))))
    gap_segs = {s for pr in gap_pairs for s in pr}
    c["gap"] = [k in gap_segs for k in range(n)]

    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, js in nbrs.items():
        for j in js:
            parent[find(i)] = find(j)
    c["comp"] = [find(i) for i in range(n)]
    comp = c.groupby("comp").agg(len_km=("len_km", "sum"), n=("comp", "size"), reach=("at_outlet", "any"), has_primary=("cls", lambda s: (s == "primary").any()))
    c["comp_reaches"] = c.comp.map(comp.reach | comp.has_primary)
    flip = []
    for k in range(n):
        ns = nbrs[k]
        flip.append(bool(ns) and all(c.cls[j] != c.cls[k] for j in ns))
    c["flip"] = flip

    rows = []
    for cl in ("primary", "secondary", "tertiary"):
        s = c[c.cls == cl]
        rows.append({"class": cl, "segments": len(s), "length km": s.len_km.sum(), "dangle ends": int(s.dangles.sum()),
                     "segments with a likely gap": int(s.gap.sum()), "isolated stubs": int(s.isolated.sum()),
                     "length in components that reach a river, edge or primary (%)": 100 * s.len_km[s.comp_reaches].sum() / max(s.len_km.sum(), 1e-9),
                     "class flips": int(s.flip.sum())})
    t = pd.DataFrame(rows)
    big = comp.sort_values("len_km", ascending=False)
    L = [f"# Canal layer audit, {a.khg}", "",
         f"Written by `scripts/check_canal_topology.py` from `00_inputs/canals.gpkg` (class `KET_KANAL`), snap {a.snap:g} m, gap {a.gap:g} m. "
         "Counts show where the layer is open or inconsistent; they do not say which class is right.", "",
         t.round(1).to_markdown(index=False), "",
         f"Components: {len(comp)}; the largest holds {100 * big.len_km.iloc[0] / comp.len_km.sum():.0f}% of the length; "
         f"{100 * comp.len_km[comp.reach | comp.has_primary].sum() / comp.len_km.sum():.0f}% of the length is in components that reach a river, "
         f"the KHG edge or a primary canal; {int((comp.n == 1).sum())} components are a single segment.", ""]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    c[["cls", "len_km", "dangles", "gap", "isolated", "flip", "comp_reaches", "geometry"]].to_file(Path(a.out).with_suffix(".gpkg"), driver="GPKG")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
