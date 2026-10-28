"""Check the field survey and the gridded inputs of a KHG against each other before the groundwater model is scored on them.

  python scripts/check_field_inputs.py --khg 14.10.03 --source "$REPEAT_DATA/Peat depth and DTM/Tebingtinggi.csv" \
      --out docs/reports/field_inputs_14.10.03.md

Reads the raw survey (format of `repeat_neraca.groundwater.fieldobs.tebingtinggi2015`) and the KHG's own copies in 00_inputs and 01_dem/inputs.
Reports: where zero water tables fall (by field team and land use), whether the peat masks agree with the field record of peat and mineral
soil, how the peat-depth raster compares with the measured thickness, and the DTMs against the survey elevation.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def sample(path, lon, lat):
    import rasterio
    from pyproj import Transformer
    with rasterio.open(path) as s:
        x, y = Transformer.from_crs(4326, s.crs, always_xy=True).transform(lon, lat)
        v = np.array([a[0] for a in s.sample(zip(x, y))], float)
        if s.nodata is not None:
            v[v == s.nodata] = np.nan
        v[np.abs(v) > 1e30] = np.nan
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from repeat_common import khg as K
    kf = K.folder(a.khg)
    d = pd.read_csv(a.source)
    peat = (d.TebalGmbt1 > 0).values
    zero = (d.Air_Tanah <= 0).values
    team = d.Surveyor.astype(str).str.strip().str.lower().replace("", "(none)")
    L = [f"# Field survey and gridded inputs, {kf.name}", "", f"`python scripts/check_field_inputs.py --khg {a.khg} --source <survey>`. "
         f"Survey: {Path(a.source).name}, {len(d)} points, {int(peat.sum())} on peat, {int((~peat).sum())} on mineral soil.", "",
         "## Zero water tables", "",
         f"{int((zero & peat).sum())} of {int(peat.sum())} peat points have a water table of 0. The ponding column is "
         f"{'0 everywhere' if (d.Genangan == 0).all() else 'not always 0'}.", ""]
    for by, key in (("field team", team), ("land use", d.TupLah.astype(str).str.strip().str.lower())):
        t = pd.DataFrame({"key": key[peat], "zero": zero[peat]}).groupby("key").zero.agg(["size", "mean"])
        t = t[t["size"] >= 30].sort_values("mean", ascending=False)
        L += [f"Share of zeros by {by} (groups with at least 30 peat points): "
              + "; ".join(f"{k} {r['mean']:.0%} of {int(r['size'])}" for k, r in t.iterrows()) + ".", ""]

    inp = kf / "00_inputs"
    import geopandas as gpd
    khg = gpd.read_file(inp / "khg.gpkg")
    crs = khg.estimate_utm_crs()
    area = float(khg.to_crs(crs).area.sum() / 1e6)
    c = gpd.read_file(inp / "canals.gpkg").to_crs(crs)
    c = c.assign(km=c.geometry.intersection(khg.to_crs(crs).union_all()).length / 1000)
    km = c.groupby("KET_KANAL").km.sum() if "KET_KANAL" in c else c.km.sum()
    L += ["## KHG and canals", "", f"KHG area {area:,.0f} km2 ({crs}). Canal length inside the KHG: "
          + "; ".join(f"{k} {v:,.0f} km" for k, v in km.items()) + f" ({len(c)} lines).", ""]
    if (inp / "blocks.gpkg").exists():
        b = gpd.read_file(inp / "blocks.gpkg")
        L += [f"Canal blocks in 00_inputs/blocks.gpkg: {len(b)}; columns {', '.join(c for c in b.columns if c != 'geometry')}.", ""]
    L += ["## Peat masks against the field record", "", "| layer | marks peat at field peat points | at field mineral points |", "|---|---|---|"]
    masks = {"GFW peat extent (00_inputs/national)": sample(inp / "national" / "peat_extent_gfw_v20230315_z11.tif", d.POINT_X, d.POINT_Y) == 1,
             "peat-depth raster > 0 (00_inputs/peat_depth.tif)": sample(inp / "peat_depth.tif", d.POINT_X, d.POINT_Y) > 0}
    for k, m in masks.items():
        L.append(f"| {k} | {m[peat].mean():.0%} | {m[~peat].mean():.0%} |")
    dep = sample(inp / "peat_depth.tif", d.POINT_X, d.POINT_Y)
    ok = peat & np.isfinite(dep) & (dep > 0)
    L += ["", f"Peat-depth raster (cm) against the measured thickness at {int(ok.sum())} peat points: Pearson r "
          f"{np.corrcoef(dep[ok], d.TebalGmbt1[ok] * 100)[0, 1]:.2f}, median ratio {np.median(dep[ok] / (d.TebalGmbt1[ok] * 100)):.2f}.", "",
          "## DTMs against the survey elevation", "", "| DTM | n | median DTM (m) | median survey (m) | Pearson r | median difference (m) |",
          "|---|---|---|---|---|---|"]
    for dem in ("deltadtm", "demnas"):
        f = kf / "01_dem" / "inputs" / f"{dem}.tif"
        if f.exists():
            z = sample(f, d.POINT_X, d.POINT_Y)
            ok = np.isfinite(z) & (d.Elevasi > 0)
            L.append(f"| {dem} | {int(ok.sum())} | {np.median(z[ok]):.2f} | {np.median(d.Elevasi[ok]):.2f} | "
                     f"{np.corrcoef(z[ok], d.Elevasi[ok])[0, 1]:.2f} | {np.median(z[ok] - d.Elevasi[ok]):.2f} |")
    st = inp / "sitmat" / "daily_long.csv"
    if st.exists():
        s = pd.read_csv(st)
        s = s[s.flag.isna()]
        g = s.groupby(["kind", "station_id"]).water_level_cm.agg(days="count", median="median", min="min", max="max").reset_index()
        L += ["", "## SiTMAT stations (00_inputs/sitmat/daily_long.csv, unflagged days)", "",
              "| kind | station | days | median (cm) | min (cm) | max (cm) |", "|---|---|---|---|---|---|"]
        L += [f"| {r.kind} | {r.station_id} | {r.days} | {r.median:.1f} | {r.min:.0f} | {r.max:.0f} |" for r in g.itertuples()]
    L += ["", "The survey does not say how its elevations were measured, so agreement with a DTM is not evidence of DTM quality on its own.", ""]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
