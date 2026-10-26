#!/usr/bin/env python3
"""Checks of `repeat_common.fetch_gee_balance` against Earth Engine, for one KHG's sub-KHG units.

  python scripts/check_gee_balance.py --khg "Kampar - Gaung"

1. Identity: a period that is exactly one source image (WaPOR dekad 2024-02-01..10, TerraClimate month 2019-08) must give the
   image's own value x scale (x 10 days for WaPOR), reduced directly on the image's grid.
2. MOD16 fill codes: how many pixels in the KHG are above 32700 (water, urban, barren fill) in one composite; the fetcher masks them.
Prints the largest absolute difference per check; run with the root .venv (needs earthengine-api, EE_PROJECT).
"""
import argparse
from datetime import date

import geopandas as gpd

from repeat_common import fetch_gee_balance as B
from repeat_common import gee, khg as K


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True)
    a = ap.parse_args()
    ee = gee.init()
    units = gpd.read_file(K.folder(a.khg) / "02_delineation" / "subkhg_units.gpkg")
    fc = B._units_fc(ee, units, "unit_id")
    for name, t0, t1, idx, factor in [("wapor", date(2024, 2, 1), date(2024, 2, 11), "WAPOR-3_L1-AETI-D_2024-02-D1", 0.1 * 10),
                                      ("terraclimate_aet", date(2019, 8, 1), date(2019, 9, 1), "201908", 0.1)]:
        p = B.PRODUCTS[name]
        got = B.fetch_year(ee, fc, name, t0.year, t0, t1, "dekad" if name == "wapor" else "month").set_index("unit_id")["mm"]
        coll = ee.ImageCollection(p["collection"])
        crs, tr = B._grid(ee, coll, p["band"])
        im = coll.filter(ee.Filter.eq("system:index", idx)).first().select(p["band"]).multiply(factor)
        ref = im.reduceRegions(collection=fc, reducer=ee.Reducer.mean(), crs=crs, crsTransform=tr).getInfo()
        ref = {f["properties"]["unit_id"]: f["properties"].get("mean") for f in ref["features"]}
        diff = max(abs(got[u] - v) for u, v in ref.items() if v is not None)
        print(f"identity {name} {t0}: {len(ref)} units, mean {sum(ref.values()) / len(ref):.2f} mm, max |fetch - direct| = {diff:.2e} mm")
    m = ee.ImageCollection(B.PRODUCTS["mod16"]["collection"]).filterDate("2023-08-01", "2023-08-10").first().select("ET")
    region = fc.geometry()
    n = m.gt(32700).reduceRegion(ee.Reducer.sum(), region, 500, maxPixels=1e9).getInfo()
    tot = m.mask().reduceRegion(ee.Reducer.sum(), region, 500, maxPixels=1e9).getInfo()
    print(f"MOD16 2023-08 composite: {n['ET']:.0f} of {tot['ET']:.0f} unmasked pixels in the KHG carry fill codes above 32700")


if __name__ == "__main__":
    main()
