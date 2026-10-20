#!/usr/bin/env python3
"""Write the daily forcing and the water-table stations of a KHG as plain files, for the physical neraca air in the `re-peat` repository.

  python -m repeat_neraca.bucket.export_inputs --config ../re-peat/sites/sugihan_lumpur/neraca_experiments.yaml --out $REPEAT_WORK/neraca_inputs/sugihan_lumpur

the physical model (`repeat_neraca`) reads files only, so the cloud readers (ERA5, WaPOR, SiTMAT) stay here. Written into --out:

  forcing_daily.csv   date, window, P_era5_mm, E_era5_mm, E_wapor_mm
                      KHG-mean daily rain and evaporation on local days (UTC+tz_hours), mm/day, for the calibration window and every
                      baseline year window (April-October) that is cached. E_wapor_mm is empty where the WaPOR forcing was not read
                      (`python -m repeat_neraca.bucket.run --calibrate-only --rain era5 --evap wapor` caches it for the calibration window).
  stations.csv        station_id, lon, lat, concession
  stations_daily.csv  date, station_id, depth_cm   observed water table depth, cm below the surface (positive down), calibration window

Run `python -m repeat_neraca.bucket.run --config ... --forcing-only` first so the ERA5 windows are cached.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from repeat_common import grid as G
from .config import load_config
from . import calibrate as CAL
from repeat_common import forcing as FO
from .run import PRESET, year_window

log = logging.getLogger("prioritas.neraca")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    for noisy in ("azure", "rasterio._env", "rasterio._err", "fsspec", "pyogrio._io"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    import geopandas as gpd
    cfg = load_config(a.config, PRESET, "neraca")
    nc = cfg["neraca"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    idf = cfg["khg_id_field"]
    kid = str(khg[idf].iloc[0]) if idf in khg.columns else "KHG01"
    geom = khg.geometry.union_all()
    grid = G.make_grid(geom, float(cfg["grid_res_m"]))
    label = G.label_raster(khg.to_crs(grid.crs).reset_index(drop=True), grid)
    cache = Path(cfg["cache_dir"]) / kid / "neraca"
    era5 = {**cfg["sources"]["era5"]}
    stride = int(era5.get("evap_stride", 3))
    cal = nc["calibration"]
    windows = [("calibration", pd.Timestamp(cal["start"]), pd.Timestamp(cal["end"]))] + [(str(y), *year_window(y, nc)) for y in nc["years"]]
    rows = []
    for name, start, end in windows:
        rows.append(FO.khg_table(grid, label, era5, start, end, cache, nc["tz_hours"], stride, window=name))   # cached by `repeat_neraca.bucket.run --forcing-only`
        log.info("forcing window %s: %d days", name, len(rows[-1]))
    forcing = pd.concat(rows, ignore_index=True)
    forcing.to_csv(out / "forcing_daily.csv", index=False, float_format="%.3f")
    Z, meta = CAL.load_stations(cfg, geom, cal["start"], cal["end"])
    meta = meta[["station_id", "lon", "lat"]].copy()
    meta["concession"] = meta.station_id.str.split(":").str[0].str.replace("concession/", "", regex=False)
    meta.to_csv(out / "stations.csv", index=False)
    daily = Z.stack().dropna().rename("depth_cm").reset_index()
    daily.columns = ["date", "station_id", "depth_cm"]
    daily.to_csv(out / "stations_daily.csv", index=False, float_format="%.2f")
    print(f"wrote {out / 'forcing_daily.csv'} ({len(forcing)} days), stations.csv ({len(meta)} stations), stations_daily.csv ({len(daily)} readings)")


if __name__ == "__main__":
    main()
