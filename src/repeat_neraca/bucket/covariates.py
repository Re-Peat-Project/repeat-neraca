#!/usr/bin/env python3
"""Which simple covariates explain where the water table is deepest at the SiTMAT stations?

  python -m repeat_neraca.bucket.covariates --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml [--ndvi-year 2019]

Reads neraca_stations.csv (written by `repeat_neraca.bucket.run --calibrate-only` or the full run), adds covariates at each station
(peat depth, elevation and relief from the DTM, canal distance and density, distance to rivers, primary canals and the KHG
edge, and NDMI / NDVI of one year from the cache), and writes neraca_station_covariates.csv and neraca_covariates.md in the
output folder: Spearman of each covariate with the observed peak depth and with the share of days deeper than 40 cm.
It answers whether a spatially useful neraca air has a simple driver to build on. Needs rasters.dtm in the config.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from repeat_common import grid as G
from .config import load_config
from . import calibrate as CAL
from .run import PRESET

log = logging.getLogger("prioritas.neraca")


def _rho(s: pd.DataFrame, a: str, b: str):
    ok = s[a].notna() & s[b].notna()
    if ok.sum() < 8 or s.loc[ok, a].nunique() < 2 or s.loc[ok, b].nunique() < 2:
        return None
    return round(float(spearmanr(s.loc[ok, a], s.loc[ok, b]).correlation), 2)


def station_covariates(cfg: dict, s: pd.DataFrame, khg_geom_ll, ndvi_year=None) -> pd.DataFrame:
    import geopandas as gpd
    import rasterio
    from rasterio.windows import Window
    from shapely.geometry import Point
    grid = G.make_grid(khg_geom_ll, float(cfg["grid_res_m"]))
    s = s.copy()
    dtm = cfg["rasters"].get("dtm")
    if dtm:
        rows = []
        with rasterio.open(dtm) as src:
            nod = src.nodata
            half = int(round(2000 / (src.res[0] * 111320)))               # about 2 km either side, in pixels
            for lon, lat in zip(s.lon, s.lat):
                r, c = src.index(lon, lat)
                w = src.read(1, window=Window(c - half, r - half, 2 * half + 1, 2 * half + 1), boundless=True, fill_value=nod).astype(float)
                w[(w == nod) | (w < -1000) | (w > 1000)] = np.nan
                z0 = w[half, half]
                ok = np.isfinite(z0) and np.isfinite(w).any()
                rows.append({"elev_m": z0, "relief_2km_m": z0 - np.nanpercentile(w, 10) if ok else np.nan,
                             "elev_minus_min2km": z0 - np.nanmin(w) if ok else np.nan})
        for k, v in pd.DataFrame(rows).items():
            s[k] = v.values
    utm = grid.crs
    pts = gpd.GeoSeries([Point(x, y) for x, y in zip(s.lon, s.lat)], crs=4326).to_crs(utm)
    if cfg["vectors"].get("canals"):
        canals = gpd.read_file(cfg["vectors"]["canals"]).to_crs(utm)
        sidx = canals.sindex
        dens = []
        for p in pts:
            b = p.buffer(500)
            cand = canals.iloc[list(sidx.intersection(b.bounds))]
            dens.append(cand.intersection(b).length.sum() / (np.pi * 0.5 ** 2) / 1000.0 if len(cand) else 0.0)
        s["canal_density_500m"] = dens                                   # km of canal per km2
        f = (cfg["units"].get("subkhg") or {}).get("canal_class_field") or cfg["params"].get("ipg_canal_class_field")
        if f and f in canals.columns:
            prim = canals[canals[f].astype(str).str.lower().str.contains("primer|primary")]
            if len(prim):
                s["dist_primary_canal_m"] = [prim.distance(p).min() for p in pts]
    if cfg["vectors"].get("rivers"):
        rivers = gpd.read_file(cfg["vectors"]["rivers"]).to_crs(utm)
        if len(rivers):
            s["dist_river_m"] = [rivers.distance(p).min() for p in pts]
    edge = gpd.GeoSeries([khg_geom_ll], crs=4326).to_crs(utm).iloc[0].boundary
    s["dist_khg_edge_m"] = [edge.distance(p) for p in pts]
    if ndvi_year:
        import rasterio as rio
        for name in ("ndmi", "ndvi"):
            f = Path(cfg["cache_dir"]) / s.attrs.get("khg_id", "") / "annual" / f"{name}_{ndvi_year}.tif"
            if f.exists():
                with rio.open(f) as src:
                    s[f"{name}_{ndvi_year}"] = CAL.sample_grid(src.read(1), grid, s.lon.values, s.lat.values)
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--ndvi-year", type=int, help="year of the NDMI / NDVI layers to sample (default: first neraca year)")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    import geopandas as gpd
    cfg = load_config(a.config, PRESET, "neraca")
    out = Path(cfg["out"])
    st = pd.read_csv(out / "neraca_stations.csv")
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    idf = cfg["khg_id_field"]
    kid = str(khg[idf].iloc[0]) if idf in khg.columns else "KHG01"
    st.attrs["khg_id"] = kid
    year = a.ndvi_year or (cfg["neraca"]["years"][0] if cfg["neraca"]["years"] else None)
    s = station_covariates(cfg, st, khg.geometry.union_all(), year)
    s.to_csv(out / "neraca_station_covariates.csv", index=False)
    covs = [c for c in s.columns if c not in ("station_id", "lon", "lat", "obs_peak_cm", "sim_peak_cm", "obs_days_gt40", "sim_days_gt40", "block")]
    lines = [f"# Station covariates ({len(s)} stations)", "",
             "Spearman correlation of each covariate with the observed water-table depth over the dry season "
             "(peak = 95th percentile depth, days > 40 = share of days deeper than 40 cm).", "",
             "| covariate | rho with observed peak depth | rho with days deeper than 40 cm |", "|---|---|---|"]
    for c in covs:
        lines.append(f"| {c} | {_rho(s, c, 'obs_peak_cm')} | {_rho(s, c, 'obs_days_gt40')} |")
    p = s["obs_peak_cm"].dropna()
    lines += ["", f"Observed peak depth: 10th percentile {p.quantile(.1):.0f} cm, median {p.median():.0f} cm, 90th percentile {p.quantile(.9):.0f} cm."]
    if "peat_depth_cm" in s:
        lines.append(f"Stations whose peat depth is within 2 cm of the raster minimum ({s.peat_depth_cm.min():.0f} cm): "
                     f"{int((s.peat_depth_cm < s.peat_depth_cm.min() + 2).sum())} of {len(s)}.")
    text = "\n".join(lines)
    (out / "neraca_covariates.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
