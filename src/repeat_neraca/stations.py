"""Write the SiTMAT water-table stations inside a KHG as the station files the physical neraca air and the deficit read.

  python -m repeat_neraca.stations --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml

Reads the `repeat-sitmat` extract through `repeat_common.tma` (config block `stations:`, below) and writes into `inputs_dir`:

  stations.csv        station_id, lon, lat, concession
  stations_daily.csv  date, station_id, depth_cm   observed water table depth, cm below the surface (positive down)

Config block:

    stations:
      tma: {path: ${SITMAT_PROCESSED}}   # repeat_common.tma settings: kinds, drop_flags, min_coverage (0.5)
      start: 2026-04-01                  # window; min_coverage is the share of its days a station must have
      end: 2026-10-15

Stations with readings on fewer than `min_coverage` of the window days are dropped, so a longer window can drop stations.
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path

import pandas as pd

from .groundwater import grid as IN


def load(cfg: dict, polygon_ll) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(days x stations depth in cm, positive down; station table) for the stations inside polygon_ll."""
    import geopandas as gpd
    from repeat_common import tma as TMA
    s = cfg["stations"]
    c = {"tma": copy.deepcopy(s.get("tma") or {})}
    c["tma"]["period"] = [str(pd.Timestamp(s["start"]).date()), str(pd.Timestamp(s["end"]).date())]
    t = TMA.load(c, [])
    if t is None or not len(t):
        raise SystemExit("no water-table readings: set stations.tma.path to the SiTMAT folder")
    meta = t.groupby("station_id").agg(lon=("lon", "first"), lat=("lat", "first")).reset_index()
    pts = gpd.GeoDataFrame(meta, geometry=gpd.points_from_xy(meta.lon, meta.lat), crs=4326)
    t = t[t["station_id"].isin(pts[pts.within(polygon_ll)]["station_id"])]
    Z = t.pivot(index="date", columns="station_id", values="depth_m") * 100.0
    Z.index = pd.DatetimeIndex(Z.index).normalize()
    meta = meta[meta["station_id"].isin(Z.columns)].set_index("station_id").loc[Z.columns].reset_index()
    meta = meta[["station_id", "lon", "lat"]].copy()
    meta["concession"] = meta.station_id.str.split(":").str[0].str.replace("concession/", "", regex=False)
    return Z, meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None, help="folder (default: inputs_dir of the config)")
    a = ap.parse_args(argv)
    import geopandas as gpd
    cfg = IN.load_config(a.config)
    out = Path(a.out or cfg["inputs_dir"])
    out.mkdir(parents=True, exist_ok=True)
    geom = gpd.read_file(cfg["khg"]).to_crs(4326).geometry.union_all()
    Z, meta = load(cfg, geom)
    meta.to_csv(out / "stations.csv", index=False)
    daily = Z.stack().dropna().rename("depth_cm").reset_index()
    daily.columns = ["date", "station_id", "depth_cm"]
    daily.to_csv(out / "stations_daily.csv", index=False, float_format="%.2f")
    print(f"wrote {out / 'stations.csv'} ({len(meta)} stations), stations_daily.csv ({len(daily)} readings)")


if __name__ == "__main__":
    main()
