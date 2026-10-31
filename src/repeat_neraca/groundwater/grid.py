"""Read a real KHG (boundary, DTM, peat depth, canals, stations) onto a metric grid for the physical neraca air.

Everything is read from files named in a small YAML config (paths may use ${ENV_VAR}); nothing is downloaded. The DTM and the peat
depth raster are averaged onto the grid, canals are rasterised by class, the KHG edge ring is the fixed-head boundary where a river or
the sea sets the level. Needs rasterio, geopandas, pandas, pyproj and shapely (`pip install -e .[neraca]`).

Conventions as in the rest of the package: metres, water table depth negative below the surface, daily steps.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml
from scipy import ndimage

CLASSES = ("primary", "secondary", "tertiary")


def expand(value):
    """Replace ${NAME} by the environment variable; a missing variable stops with a message."""
    if isinstance(value, dict):
        return {k: expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand(v) for v in value]
    if isinstance(value, str):
        def sub(m):
            if m.group(1) not in os.environ:
                raise SystemExit(f"environment variable {m.group(1)} is not set (needed by the config)")
            return os.environ[m.group(1)]
        return re.sub(r"\$\{(\w+)\}", sub, value)
    return value


def load_config(path: str | Path) -> dict:
    cfg = expand(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
    cfg["_dir"] = str(Path(path).resolve().parent)
    return cfg


@dataclass
class RealKHG:
    name: str
    crs: str
    dx: float
    transform: object
    domain: np.ndarray                    # bool, inside the KHG
    boundary: np.ndarray                  # bool, edge ring of the domain
    surface: np.ndarray                   # m, DTM averaged onto the grid, gaps filled from the nearest cell
    peat_depth: np.ndarray                # m, gaps filled with the median
    canal: dict                           # class -> bool raster (primary, secondary, tertiary)
    canal_length_km: dict                 # class -> km inside the KHG
    area_km2: float
    stations: object = None               # DataFrame: station_id, lon, lat, concession, row, col
    units: np.ndarray | None = None       # int raster of sub-KHG index (-1 outside) and their ids
    unit_ids: list = field(default_factory=list)
    notes: dict = field(default_factory=dict)
    peat_depth_source: np.ndarray | None = None     # int8 per cell: 1 the peat-depth raster, 0 filled with the median (2: a fallback layer)

    @property
    def shape(self):
        return self.surface.shape


def _utm(lon: float, lat: float) -> str:
    zone = int((lon + 180) // 6) + 1
    return f"EPSG:{(32600 if lat >= 0 else 32700) + zone}"


def _fill_nearest(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    idx = ndimage.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return a[tuple(idx)]


def _to_grid(path, transform, shape, crs, scale=1.0):
    """Average a raster onto the grid (NaN where there is no data)."""
    import rasterio
    from rasterio.warp import Resampling, reproject
    out = np.full(shape, np.nan, "float32")
    with rasterio.open(path) as src:
        nod = src.nodata
        reproject(rasterio.band(src, 1), out, src_nodata=nod, dst_transform=transform, dst_crs=crs, dst_nodata=np.nan,
                  resampling=Resampling.average)
    out[(out < -1e6) | (out > 1e6)] = np.nan
    return out * scale


def load(cfg: dict, res_m: float) -> RealKHG:
    import geopandas as gpd
    import pandas as pd
    from rasterio import features
    from rasterio.transform import from_origin

    khg_ll = gpd.read_file(cfg["khg"]).to_crs(4326)
    c = khg_ll.geometry.union_all().centroid
    crs = _utm(c.x, c.y)
    khg = khg_ll.to_crs(crs)
    x0, y0, x1, y1 = khg.total_bounds
    nx = int(np.ceil((x1 - x0) / res_m)) + 2
    ny = int(np.ceil((y1 - y0) / res_m)) + 2
    transform = from_origin(x0 - res_m, y1 + res_m, res_m, res_m)
    shape = (ny, nx)
    domain = features.rasterize([(g, 1) for g in khg.geometry], out_shape=shape, transform=transform, fill=0, dtype="uint8").astype(bool)
    boundary = domain & ~ndimage.binary_erosion(domain, structure=np.ones((3, 3)))
    notes = {}

    dtm = _to_grid(cfg["dtm"], transform, shape, crs)
    ok = np.isfinite(dtm)
    notes["dtm_valid_in_domain"] = float(ok[domain].mean())
    surface = _fill_nearest(np.where(ok, dtm, 0.0), ok) if ok.any() else np.zeros(shape, "float32")

    pd_cfg = cfg.get("peat_depth")
    if pd_cfg:
        depth = _to_grid(pd_cfg["path"], transform, shape, crs, float(pd_cfg.get("scale", 1.0)))
    else:                          # no peat-depth layer for this KHG: every cell takes the 3.0 m fallback below, valid share 0
        depth = np.full(shape, np.nan)
    okd = np.isfinite(depth) & (depth > 0)
    notes["peat_depth_valid_in_domain"] = float(okd[domain].mean())
    med = float(np.nanmedian(depth[okd & domain])) if (okd & domain).any() else 3.0
    depth = np.where(okd, depth, med)
    depth_source = okd.astype("int8")
    notes["peat_depth_median_m"] = med

    cg = gpd.read_file(cfg["canals"]["path"]).to_crs(crs)
    field_name = cfg["canals"]["class_field"]
    canal, length = {}, {}
    for cls in CLASSES:
        names = [str(v).lower() for v in cfg["canals"]["classes"].get(cls, [])]
        sel = cg[cg[field_name].astype(str).str.lower().isin(names)] if names else cg.iloc[0:0]
        sel = sel[~sel.geometry.is_empty]
        if len(sel):
            m = features.rasterize([(g, 1) for g in sel.geometry], out_shape=shape, transform=transform, fill=0, dtype="uint8", all_touched=True).astype(bool)
            inside = sel.geometry.intersection(khg.geometry.union_all())
            km = float(inside.length.sum() / 1000.0)
        else:
            m, km = np.zeros(shape, bool), 0.0
        canal[cls] = m & domain & ~boundary
        length[cls] = km

    stations, units, unit_ids = None, None, []
    inputs_dir = Path(cfg.get("inputs_dir", "."))
    sp = inputs_dir / "stations.csv"
    if sp.exists():
        from pyproj import Transformer
        st = pd.read_csv(sp)
        xx, yy = Transformer.from_crs(4326, crs, always_xy=True).transform(st.lon.values, st.lat.values)
        st["col"] = np.floor((xx - transform.c) / res_m).astype(int)
        st["row"] = np.floor((transform.f - yy) / res_m).astype(int)
        inside = (st.row >= 0) & (st.row < ny) & (st.col >= 0) & (st.col < nx)
        stations = st[inside].reset_index(drop=True)
    if cfg.get("units"):
        ug = gpd.read_file(cfg["units"]).to_crs(crs).reset_index(drop=True)
        units = features.rasterize([(g, i) for i, g in enumerate(ug.geometry)], out_shape=shape, transform=transform, fill=-1, dtype="int32")
        unit_ids = list(ug["unit_id"].astype(str)) if "unit_id" in ug.columns else [str(i) for i in range(len(ug))]
    return RealKHG(name=cfg.get("name", "khg"), crs=crs, dx=float(res_m), transform=transform, domain=domain, boundary=boundary,
                   surface=surface.astype("float64"), peat_depth=depth.astype("float64"), canal=canal, canal_length_km=length,
                   area_km2=float(domain.sum() * res_m ** 2 / 1e6), stations=stations, units=units, unit_ids=unit_ids, notes=notes,
                   peat_depth_source=depth_source)


def fixed_head(khg: RealKHG, canal_drawdown: float, river_stage_below_edge: float, classes=("primary", "secondary")):
    """Fixed-head mask and heads: the KHG edge ring (river or sea) and the canal cells of the given classes, each below the local surface."""
    canal = np.zeros(khg.shape, bool)
    for cls in classes:
        canal |= khg.canal[cls]
    fixed = (khg.boundary | canal) & khg.domain
    head = np.where(khg.boundary, khg.surface - river_stage_below_edge, khg.surface - canal_drawdown)
    return fixed, np.where(fixed, head, 0.0)


def canal_length(cfg: dict, khg: RealKHG) -> dict:
    """Canal length per cell (m) by class: the lines of `cfg['canals']` cut into pieces of a tenth of a cell, each piece's length added to
    the cell holding its midpoint. Cells outside the domain or on the edge ring get 0. For canals narrower than a cell (`simulate.Boundary.leak`)."""
    import geopandas as gpd
    import shapely
    cg = gpd.read_file(cfg["canals"]["path"]).to_crs(khg.crs)
    field_name = cfg["canals"]["class_field"]
    ny, nx = khg.shape
    out = {}
    for cls in CLASSES:
        names = [str(v).lower() for v in cfg["canals"]["classes"].get(cls, [])]
        sel = cg[cg[field_name].astype(str).str.lower().isin(names)] if names else cg.iloc[0:0]
        acc = np.zeros(ny * nx)
        lines = sel.geometry[~sel.geometry.is_empty].explode(index_parts=False)
        lines = lines[lines.geom_type == "LineString"]
        if len(lines):
            xy, part = shapely.get_coordinates(shapely.segmentize(lines.values, khg.dx / 10), return_index=True)
            same = part[1:] == part[:-1]
            a, b = xy[:-1][same], xy[1:][same]
            mid, ln = (a + b) / 2, np.hypot(*(b - a).T)
            col = np.floor((mid[:, 0] - khg.transform.c) / khg.dx).astype(int)
            row = np.floor((khg.transform.f - mid[:, 1]) / khg.dx).astype(int)
            ok = (row >= 0) & (row < ny) & (col >= 0) & (col < nx)
            acc = np.bincount(row[ok] * nx + col[ok], weights=ln[ok], minlength=ny * nx).astype(float)
        out[cls] = np.where(khg.domain & ~khg.boundary, acc.reshape(ny, nx), 0.0)
    return out
