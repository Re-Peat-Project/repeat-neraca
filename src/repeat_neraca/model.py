"""Neraca air groundwater model of one KHG: daily water table on a grid, scored against field water-table points.

  repeat-neraca-model --khg 14.10.03 --dem deltadtm --start 2014-10-01 --end 2015-12-11 --peat-table tropical-small --drawdown 0.6
  repeat-neraca-model --khg 14.10.03 --dem deltadtm --start 2014-10-01 --end 2015-12-11 --drawdown primary=1.0,secondary=0.6,tertiary=none

Everything comes from the KHG work folder (`repeat_common.khg.folder`), so any KHG with the inputs runs the same way:
  00_inputs/khg.gpkg, canals.gpkg, peat_depth.tif         boundary, canals by class (KET_KANAL), peat depth (cm, scale from the hub's khg.yaml)
  DTM of the variant                                      lidar: the clip in khg.yaml; deltadtm, demnas: 01_dem/processed/<dem>/dtm_smooth.tif;
                                                          deltadtm without it: the raw clip 01_dem/inputs/deltadtm.tif (DeltaDTM is a
                                                          bare-earth product; the report says it was not corrected by repeat-dem)
  03_neraca/inputs/model/balance_<product>_dekad.csv      KHG-mean rain and ET per dekad (fetched from Earth Engine when missing or short)
  00_inputs/field_wtd.csv                                 optional: field water-table points (`repeat_neraca.groundwater.fieldobs`)

Rain and ET are dekad totals spread evenly over their days. The run starts saturated (`--h0`, m below the surface) on --start; use a wet
season start and a few months of spin-up before the window that is scored. Writes into 03_neraca/<dem>/runs/model/<run>/:
  model_series.csv      date, P_mm, ET_mm, mean_depth_cm, share_deeper_40cm, canal_in_mm, edge_in_mm (water the fixed cells put into the
                        peat per day, mm over the free cells; negative: drainage)
  model_depth_window.tif   mean water table depth (cm, positive down) over the field window; model_depth_end.tif: on the last day
  field_points.csv, field_scores.json, model_report.md, registry_snapshot.json, run_config.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from repeat_neraca.groundwater import PEAT_TABLES, PeatTable
from repeat_neraca.groundwater import fieldcheck as FC
from repeat_neraca.groundwater import fieldobs as FO
from repeat_neraca.groundwater import grid as G
from repeat_neraca.groundwater import simulate as SIM
from repeat_neraca.params import Registry

CLASSES = ("primary", "secondary", "tertiary")
LICENCES = "landstatus/ALL_Updade__IZIN_USAHA__PBPH_Perkebunan_HTRKM_Tambang__2025.gpkg"   # under REPEAT_DATA
MANAGED_LICENCES = ("PBPH", "Perkebunan Kelapa Sawit")
REGULATORY_TARGET_M = 0.40     # PP 57/2016: the water table of cultivated peat at most 0.4 m below the surface at the compliance points
BBSDLP_DEPTH_M = {"D1": 0.75, "D2": 1.5, "D3": 2.5, "D4": 4.0, "D5": 6.0, "D6": 8.0}   # class midpoints (D6, >700 cm: 8 m assumed)
# Canal store (D19), a priori per class. Widths: primary 8 m (plantation canals "5 to 8 m wide", Hooijer et al. 2012; branch canals 5-8 m,
# Evans et al. 2019); secondary 3 m (the narrowest canals LiDAR maps, "always over 3 m", Vernimmen et al. 2020); tertiary 1 m (Pulau Padang
# tertiary drains, Ismail et al. 2021). Beds below the land: primary 3 m ("3 m depth", Evans 2019; "over 3 m deep", Hooijer 2012); secondary
# 1.5 m (every canal in Urzainki et al. 2023); tertiary 1 m (field drains "1 m deep", Evans 2019). research_notes/canal_levels_evidence.md
CANAL_WIDTH_M = {"primary": 8.0, "secondary": 3.0, "tertiary": 1.0}
CANAL_BED_M = {"primary": 3.0, "secondary": 1.5, "tertiary": 1.0}
CANAL_NAMES = {"primary": ["Kanal Primer"], "secondary": ["Kanal Sekunder"], "tertiary": ["Kanal Tersier"]}


def hub_khg_yaml(kf: Path) -> dict:
    hub = Path(os.environ.get("REPEAT_HUB", kf.parents[1] / "re-peat"))
    p = hub / "sites" / kf.name / "khg.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def dtm_path(kf: Path, dem: str, kc: dict) -> tuple[Path, str]:
    """The DTM of a variant and a note on where it came from."""
    if dem == "lidar":
        clip = ((kc.get("dems") or {}).get("lidar") or {}).get("clip")
        p = Path(G.expand(clip)) if clip else None
        if p and p.is_file():
            return p, "LiDAR clip"
        raise SystemExit("no LiDAR clip for this KHG (khg.yaml dems.lidar.clip)")
    for p in (kf / "01_dem" / "processed" / dem / "dtm_smooth.tif", kf / "01_dem" / "benchmark" / "04_processed" / dem / "dtm_smooth.tif"):
        if p.is_file():
            return p, f"{dem} corrected by repeat-dem ({p.relative_to(kf)})"
    raw = kf / "01_dem" / "inputs" / f"{dem}.tif"
    if dem == "deltadtm" and raw.is_file():
        return raw, "DeltaDTM clip, not corrected by repeat-dem (DeltaDTM is itself a bare-earth product)"
    raise SystemExit(f"no DTM for variant {dem}: run repeat-dem first (01_dem/processed/{dem}/dtm_smooth.tif)")


def khg_config(kf: Path, dem: str) -> tuple[dict, dict]:
    kc = hub_khg_yaml(kf)
    inp = kf / "00_inputs"
    dtm, dtm_note = dtm_path(kf, dem, kc)
    field = (kc.get("canals") or {}).get("class_field", "KET_KANAL")
    units = next((p for p in (kf / "02_delineation" / dem / "subkhg_units.gpkg", kf / "02_delineation" / "subkhg_units.gpkg") if p.is_file()), None)
    cfg = {"name": kf.name, "khg": str(inp / "khg.gpkg"), "dtm": str(dtm),
           "peat_depth": {"path": str(inp / "peat_depth.tif"), "scale": float((kc.get("peat_depth") or {}).get("scale", 0.01))},
           "canals": {"path": str(inp / "canals.gpkg"), "class_field": field, "classes": CANAL_NAMES},
           "units": str(units) if units else None, "inputs_dir": str(kf / "03_neraca" / "inputs" / "none")}
    return cfg, {"dtm": dtm_note, "units": str(units.relative_to(kf)) if units else "none (KHG without sub-KHG units)"}


def forcing(kf: Path, start: str, end: str, rain: str, et: str, fetch: bool) -> pd.DataFrame:
    """Daily P and ET (mm) of the KHG from the dekad tables; fetched from Earth Engine (cached) when missing or not covering the period."""
    d = kf / "03_neraca" / "inputs" / "model"
    days = pd.date_range(start, pd.Timestamp(end) - pd.Timedelta(days=1))

    def daily(product):
        f = d / f"balance_{product}_dekad.csv"
        if not f.exists():
            return None
        t = pd.read_csv(f, parse_dates=["start", "end"])
        s = pd.Series(np.nan, index=days)
        for r in t.itertuples():
            if r.time_cov >= 0.999:
                s[(s.index >= r.start) & (s.index < r.end)] = r.mm / r.days
        return s

    out = {p: daily(p) for p in (rain, et)}
    if any(s is None or s.isna().any() for s in out.values()):
        if not fetch:
            raise SystemExit(f"forcing in {d} does not cover {start} to {end}; rerun with --fetch")
        from repeat_common import fetch_gee_balance as FG
        fs, fe = dekad_start(pd.Timestamp(start)).date().isoformat(), dekad_start(pd.Timestamp(end), up=True).date().isoformat()
        FG.main(["--khg", str(kf.name.split("_")[0]), "--whole-khg", "--products", f"{rain},{et}", "--start", fs, "--end", fe,
                 "--no-landcover", "--out", str(d), "--cache", str(kf / "cache" / "gee_balance_model")])
        out = {p: daily(p) for p in (rain, et)}
    return pd.DataFrame({"P_mm": out[rain], "ET_mm": out[et]})


def dekad_start(d: pd.Timestamp, up: bool = False) -> pd.Timestamp:
    """First day of the dekad (1st, 11th, 21st) holding d; with up, the first dekad start on or after d."""
    s = d.replace(day=21 if d.day >= 21 else 11 if d.day >= 11 else 1)
    if up and s < d:
        s = (s + pd.Timedelta(days=10)).replace(day=21) if s.day == 11 else (s + pd.Timedelta(days=10)).replace(day=11) if s.day == 1             else (s + pd.offsets.MonthBegin(1))
    return s


def parse_drawdown(text: str, default: float) -> dict:
    """'0.6' (every class), or 'primary=1.0,secondary=0.6,tertiary=none' (a class not named keeps `default`; none: not fixed)."""
    if "=" not in text:
        v = None if text.lower() == "none" else float(text)
        return {c: v for c in CLASSES}
    dd = {c: default for c in CLASSES}
    for part in text.split(","):
        k, v = part.split("=")
        dd[k.strip()] = None if v.strip().lower() == "none" else float(v)
    return dd


def licences(kf: Path):
    """The 2025 business-licence polygons of the KHG: `00_inputs/national/izin_usaha_2025.gpkg`, clipped from REPEAT_DATA on first use and
    listed in `00_inputs/local_manifest.csv`."""
    import geopandas as gpd
    from repeat_neraca.groundwater.fieldobs import write_manifest_row
    out = kf / "00_inputs" / "national" / "izin_usaha_2025.gpkg"
    if not out.exists():
        src = Path(os.environ["REPEAT_DATA"]) / LICENCES
        k = gpd.read_file(kf / "00_inputs" / "khg.gpkg").to_crs(4326)
        g = gpd.read_file(src, bbox=tuple(k.total_bounds))
        g = g[g.intersects(k.union_all())].clip(k)
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(f"izin_usaha_2025.{os.getpid()}.tmp.gpkg")          # runs started together must not write the same file
        g.to_file(tmp, driver="GPKG")
        try:
            os.rename(tmp, out)
            write_manifest_row(kf, "national/izin_usaha_2025.gpkg", LICENCES, "business licences 2025 (IZIN_USAHA), clipped (repeat_neraca.model)", len(g))
        except FileExistsError:
            tmp.unlink()                                           # another run wrote it first: use theirs
    return gpd.read_file(out)


def depth_fallback(kf: Path, khg) -> dict:
    """Fill the cells the peat-depth raster leaves empty from the BBSDLP depth classes (class midpoints); returns the share per source."""
    from rasterio import features
    f = kf / "00_inputs" / "national" / "kedalaman_gambut_bbsdlp.gpkg"
    if f.exists():
        import geopandas as gpd
        g = gpd.read_file(f).to_crs(khg.crs)
        g = g[g["KODE_GBT"].isin(BBSDLP_DEPTH_M)]
        v = features.rasterize([(x, BBSDLP_DEPTH_M[k]) for x, k in zip(g.geometry, g["KODE_GBT"])], out_shape=khg.shape,
                               transform=khg.transform, fill=0.0, dtype="float32") if len(g) else np.zeros(khg.shape, "float32")
        use = (khg.peat_depth_source == 0) & (v > 0)
        khg.peat_depth = np.where(use, v, khg.peat_depth)
        khg.peat_depth_source = np.where(use, 2, khg.peat_depth_source).astype("int8")
    d = khg.domain
    return {"peat_depth_raster": float((khg.peat_depth_source[d] == 1).mean()), "peat_depth_bbsdlp": float((khg.peat_depth_source[d] == 2).mean()),
            "peat_depth_median_fill": float((khg.peat_depth_source[d] == 0).mean())}


def managed_targets(kf: Path, khg, kinds, mode: str, stn, levels: pd.Series | None) -> tuple[np.ndarray, dict, pd.DataFrame]:
    """Target water table (m below the surface) per cell of managed land (licences of `kinds`), NaN elsewhere.

    mode: a number (metres, the same for every licence), or 'stations-loo': each licence gets the median level of the concession stations
    outside it (leave one concession out), else the regulatory 0.4 m."""
    from rasterio import features
    g = licences(kf)
    g = g[g["IZIN_USAHA"].isin(kinds)].to_crs(khg.crs).reset_index(drop=True)
    ids = features.rasterize([(x, i) for i, x in enumerate(g.geometry) if x is not None and not x.is_empty], out_shape=khg.shape,
                             transform=khg.transform, fill=-1, dtype="int32") if len(g) else np.full(khg.shape, -1, "int32")
    ids = np.where(khg.domain, ids, -1)
    rows = []
    if mode == "stations-loo":
        s = stn.assign(level_m=stn.station_id.map(levels) / 100.0, lic=ids[stn.row, stn.col])
        s = s[s.level_m.notna() & ~stn.station_id.str.startswith("community/")]
        for i in range(len(g)):
            others = s[s.lic != i].level_m
            rows.append({"licence": i, "holder": g.loc[i, "PERUSAHAAN"], "type": g.loc[i, "IZIN_USAHA"], "own_stations": int((s.lic == i).sum()),
                         "target_m": float(others.median()) if len(others) else REGULATORY_TARGET_M,
                         "source": f"median of {len(others)} concession stations outside it" if len(others) else "regulatory 0.4 m (no other stations)"})
        unplaced = int((s.lic < 0).sum())
    else:
        for i in range(len(g)):
            rows.append({"licence": i, "holder": g.loc[i, "PERUSAHAAN"], "type": g.loc[i, "IZIN_USAHA"], "own_stations": 0,
                         "target_m": float(mode), "source": "fixed target"})
        unplaced = 0
    t = pd.DataFrame(rows, columns=["licence", "holder", "type", "own_stations", "target_m", "source"])
    lut = np.full(len(g) + 1, np.nan)
    if len(t):
        lut[t.licence.values] = t.target_m.values
    target = np.where(ids >= 0, lut[np.clip(ids, 0, None)], np.nan)
    return target, {"managed_licences": list(kinds), "managed_share_of_khg": float(np.isfinite(target)[khg.domain].mean()),
                    "managed_target_mode": str(mode), "concession_stations_outside_licences": unplaced}, t


def pump_gpkg(kf: Path, dem: str, layer: str) -> tuple[Path, str]:
    """repeat-pump's GeoPackage holding `layer`: the variant's own run first, then any variant (block reaches are relative to the land)."""
    import pyogrio
    for d in [kf / "05_pump" / dem, kf / "05_pump", *sorted((kf / "05_pump").glob("*/"))]:
        for f in sorted(d.glob("*.gpkg")) if d.is_dir() else []:
            if layer in [x[0] for x in pyogrio.list_layers(f)]:
                return f, str(f.relative_to(kf))
    raise SystemExit(f"no repeat-pump GeoPackage with layer {layer} in {kf / '05_pump'}: run repeat-pump first")


def source(arg: str, kf: Path, dem: str, layer: str):
    """('pump' -> repeat-pump's layer) or 'path[:layer]' -> (GeoDataFrame, description)."""
    import geopandas as gpd
    if arg == "pump":
        f, rel = pump_gpkg(kf, dem, layer)
        return gpd.read_file(f, layer=layer), f"{rel}, layer {layer}"
    path, _, lyr = arg.partition(":")
    return gpd.read_file(path, layer=lyr or None), arg


def block_levels(kf: Path, dem: str, khg, arg: str) -> tuple[np.ndarray, dict]:
    """Canal water depth below the land (m) along each block's reach, NaN elsewhere."""
    from rasterio import features
    g, src = source(arg, kf, dem, "sekat_reach")
    g = g[g["depth_m"].notna()].to_crs(khg.crs)
    g = g.sort_values("depth_m", ascending=False)                    # where reaches overlap, the shallower level is written last and wins
    v = features.rasterize([(x, float(d)) for x, d in zip(g.geometry, g["depth_m"])], out_shape=khg.shape, transform=khg.transform,
                           fill=np.nan, dtype="float32", all_touched=True) if len(g) else np.full(khg.shape, np.nan, "float32")
    v = np.where(khg.domain, v, np.nan)
    return v, {"blocks": src, "block_reaches": int(len(g)), "block_reach_cells": int(np.isfinite(v).sum())}


def existing_block_levels(kf: Path, khg, level: float, radius: float) -> tuple[np.ndarray | None, dict]:
    """Canal water depth below the land (m) on the canal cells within `radius` m of an existing canal block (D23), NaN elsewhere.
    The blocks are the BRGM/PPEG `Sekat Kanal` points clipped to the KHG (`00_inputs/blocks.gpkg`): points only, no crest level and no flow
    direction, so a block holds the canal at `level` for a radius around it (field reports: rewetting 100 to 400 m along the canal)."""
    import geopandas as gpd
    from rasterio import features
    f = kf / "00_inputs" / "blocks.gpkg"
    if not f.exists():
        return None, {"existing_blocks": "none: no 00_inputs/blocks.gpkg"}
    g = gpd.read_file(f)
    g = g[g.geometry.notna()]
    if "Jenis" in g:
        g = g[g.Jenis.astype(str).str.strip().str.lower() == "sekat kanal"]
    g = g.to_crs(khg.crs)
    if g.empty:
        return None, {"existing_blocks": "none: no Sekat Kanal points in 00_inputs/blocks.gpkg"}
    near = features.rasterize([(x.buffer(radius), 1) for x in g.geometry], out_shape=khg.shape, transform=khg.transform, fill=0, dtype="uint8") > 0
    canal = np.zeros(khg.shape, bool)
    for cls in khg.canal:
        canal |= khg.canal[cls]
    v = np.where(near & canal & khg.domain, float(level), np.nan).astype("float32")
    return v, {"existing_blocks": f"00_inputs/blocks.gpkg, {len(g)} Sekat Kanal points, canal cells within {radius:g} m held at {level:g} m below the land",
               "existing_block_points": int(len(g)), "existing_block_canal_cells": int(np.isfinite(v).sum())}


def supply_areas(kf: Path, dem: str, khg, arg: str, target: float) -> tuple[np.ndarray, dict]:
    """Target water table (m below the surface) on the land a scenario supplies with water, NaN elsewhere."""
    from rasterio import features
    g, src = source(arg, kf, dem, "interventions")
    if arg == "pump":
        g = g[g["intervention"].astype(str).str.contains("water")]
    g = g.to_crs(khg.crs)
    m = features.rasterize([(x, 1) for x in g.geometry if x is not None and not x.is_empty], out_shape=khg.shape, transform=khg.transform,
                           fill=0, dtype="uint8").astype(bool) if len(g) else np.zeros(khg.shape, bool)
    m &= khg.domain
    return np.where(m, target, np.nan), {"supply": src, "supply_polygons": int(len(g)), "supply_share_of_khg": float(m[khg.domain].mean()),
                                         "supply_target_m": target}


def managed_raster(kf: Path, khg, kinds) -> tuple[np.ndarray, dict]:
    from rasterio import features
    g = licences(kf)
    g = g[g["IZIN_USAHA"].isin(kinds)].to_crs(khg.crs)
    m = features.rasterize([(x, 1) for x in g.geometry if x is not None and not x.is_empty], out_shape=khg.shape, transform=khg.transform,
                           fill=0, dtype="uint8").astype(bool) if len(g) else np.zeros(khg.shape, bool)
    m &= khg.domain
    return m, {"managed_licences": list(kinds), "managed_share_of_khg": float(m[khg.domain].mean())}


def write_tif(path: Path, a: np.ndarray, khg) -> None:
    import rasterio
    with rasterio.open(path, "w", driver="GTiff", height=a.shape[0], width=a.shape[1], count=1, dtype="float32", crs=khg.crs,
                       transform=khg.transform, nodata=-9999.0, compress="deflate") as dst:
        dst.write(np.where(np.isfinite(a), a, -9999.0).astype("float32"), 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True, help="KHG name or code")
    ap.add_argument("--dem", default="deltadtm", choices=["lidar", "deltadtm", "demnas"])
    ap.add_argument("--start", required=True, help="first day (start saturated, in a wet season)")
    ap.add_argument("--end", required=True, help="exclusive")
    ap.add_argument("--res", type=float, default=100.0, help="grid cell, m")
    ap.add_argument("--peat-table", default="tropical-small", choices=list(PEAT_TABLES))
    ap.add_argument("--drawdown", default=None, help="canal level below the surface, m: one value, or per class (default: registry canal_drawdown)")
    ap.add_argument("--edge-stage", type=float, default=None, help="edge ring level below the surface, m (default: registry river_stage_below_edge)")
    ap.add_argument("--h0", type=float, default=0.0, help="initial water table below the surface, m")
    ap.add_argument("--rain", default="chirps")
    ap.add_argument("--et", default="mod16")
    ap.add_argument("--fetch", action="store_true", help="fetch missing forcing from Earth Engine")
    ap.add_argument("--drawdown-managed", default=None,
                    help="canal level below the surface (m) for canal cells in managed land (one value or per class); default: as --drawdown")
    ap.add_argument("--managed-target", default=None,
                    help="hold managed land at a target water table: metres below the surface (e.g. 0.4, PP 57/2016), or 'stations-loo' (each "
                         "licence's target = median level of the concession stations outside it; calibrated, leave-one-concession-out)")
    ap.add_argument("--peat-base", action="store_true", help="no ET from a cell whose water table is below the peat base")
    ap.add_argument("--season", default=None, help="season of the per-cell maps and the unit table (month-day,month-day), in the last year of the run "
                    "(default 06-01,09-30; with --supply-cap climate, the KHG's dry window, so the supply and the days deeper than 40 cm are reported "
                    "over the period the cap acts in)")
    ap.add_argument("--depth-fallback", choices=["none", "bbsdlp"], default="none",
                    help="fill peat-depth raster gaps cell by cell from the BBSDLP 1:50k depth classes (00_inputs/national), then the median")
    ap.add_argument("--blocks", default="none",
                    help="canal blocks of a scenario: 'pump' (repeat-pump's sekat_reach: each block's reach and its water depth below the land), "
                         "or a GeoPackage path[:layer] with lines and a depth_m field; 'none' (default)")
    ap.add_argument("--existing-blocks", choices=["brgm", "none"], default="brgm",
                    help="existing canal blocks (BRGM/PPEG Sekat Kanal points, 00_inputs/blocks.gpkg): canal cells within --block-radius m of a block are held "
                         "at --block-level m below the land, or at the class level where that is shallower (D23); `none` reproduces runs made before D23")
    ap.add_argument("--block-level", type=float, default=0.4, help="canal level behind an existing block, m below the land (assumed: the PP 57/2016 limit; the layer has no crest level)")
    ap.add_argument("--block-radius", type=float, default=200.0, help="m of canal around an existing block held at the block level (assumed: field reports 100 to 400 m)")
    ap.add_argument("--supply", default="none",
                    help="pumping of a scenario: 'pump' (the sub-KHG of repeat-pump's interventions layer that receive water), or a GeoPackage "
                         "path[:layer] of polygons; the land is held at --supply-target like managed land, and the water it takes is the pumping need")
    ap.add_argument("--supply-target", type=float, default=REGULATORY_TARGET_M, help="water table held where water is supplied, m below the surface")
    ap.add_argument("--managed-licences", default=",".join(MANAGED_LICENCES),
                    help="IZIN_USAHA values of the licence layer that count as managed land (plantations with water management)")
    ap.add_argument("--et-stress", choices=["none", "drained", "natural"], default="none",
                    help="ET falls where the water table is deep (PEATCLSM-Trop): drained = registry et_stress_start/end, natural = -0.70/-1.82 m")
    ap.add_argument("--canal-cells", choices=["fixed", "leak"], default="fixed",
                    help="fixed: every cell a canal touches is held at the canal level; leak: canals narrower than a cell exchange water with it (D18)")
    ap.add_argument("--canal-store", action="store_true",
                    help="canal level from a water balance per sub-KHG (D19), moving around the --drawdown levels as the sill; implies --canal-cells leak")
    ap.add_argument("--canal-tau", type=float, default=1.0, help="canal store: days for water above the sill to leave through the outlet")
    ap.add_argument("--screen-stations", action="store_true",
                    help="score stations on the screened record (fieldcheck.screen: restarts after gaps, settling days, stuck loggers left out; D21)")
    ap.add_argument("--log-ponding", action="store_true", help="also write model_ponded.csv: water the solver removes above the surface, per day (diagnostic)")
    ap.add_argument("--supply-cap", default=None, help="water management adds at most this much to each managed cell (mm), so a cell that has used it falls "
                    "with the water table (D22): a number (over --season), or `deficit` (the station-based deficit and its period from runs/deficit/neraca_khg.csv; "
                    "the supply check of the gate is then not testable, since the cap is taken from it), or `climate` (the shortfall of the run over the KHG's own dry window, "
                    "from its 2018-2025 rain and ET; needs no stations, so the supply check still tests it)")
    ap.add_argument("--run", default=None, help="run folder name (default from the options)")
    a = ap.parse_args(argv)

    from repeat_common import khg as K
    kf = K.folder(a.khg)
    reg = Registry.load()
    dd = parse_drawdown(a.drawdown, float(reg["canal_drawdown"])) if a.drawdown else {c: float(reg["canal_drawdown"]) for c in CLASSES}
    edge = float(reg["river_stage_below_edge"]) if a.edge_stage is None else a.edge_stage
    tag = "_".join(f"{c[0]}{'x' if v is None else f'{v:g}'}" for c, v in dd.items())
    ddm = parse_drawdown(a.drawdown_managed, float(reg["canal_drawdown"])) if a.drawdown_managed else None
    if ddm and a.managed_target:
        raise SystemExit("--drawdown-managed and --managed-target are alternatives: give one")
    if ddm:
        tag += "_m" + "_".join(f"{c[0]}{'x' if v is None else f'{v:g}'}" for c, v in ddm.items())
    if a.managed_target:
        tag += "_mt" + ("loo" if a.managed_target == "stations-loo" else f"{float(a.managed_target):g}")
    if a.blocks != "none":
        tag += "_blk"
    if a.existing_blocks == "brgm" and (kf / "00_inputs" / "blocks.gpkg").exists():
        tag += "_eb" + ("" if (a.block_level, a.block_radius) == (0.4, 200.0) else f"{a.block_level:g}r{a.block_radius:g}")
    if a.supply != "none":
        tag += f"_sup{a.supply_target:g}"
    leak = a.canal_cells == "leak" or a.canal_store
    if leak and ddm:
        raise SystemExit("--canal-cells leak and --canal-store need --managed-target, not --drawdown-managed")
    if leak:
        tag += "_lk"
    if a.canal_store:
        tag += f"_cs{a.canal_tau:g}"
    if a.screen_stations:
        tag += "_scr"
    if a.supply_cap:
        tag += f"_cap{a.supply_cap}"
    run_name = a.run or (f"{a.peat_table}_{tag}_e{edge:g}_{a.res:g}m" + ("" if a.et_stress == "none" else f"_et{a.et_stress}")
                         + ("_pb" if a.peat_base else "") + ("" if a.depth_fallback == "none" else f"_d{a.depth_fallback}"))
    out = kf / "03_neraca" / a.dem / "runs" / "model" / run_name
    out.mkdir(parents=True, exist_ok=True)
    log = lambda m: print(m, flush=True)

    cfg, notes = khg_config(kf, a.dem)
    khg = G.load(cfg, a.res)
    depth_sources = depth_fallback(kf, khg) if a.depth_fallback == "bbsdlp" else None
    f = forcing(kf, a.start, a.end, a.rain, a.et, a.fetch)
    net = (f.P_mm - f.ET_mm).values / 1000.0
    dates = f.index

    fp = kf / "00_inputs" / "field_wtd.csv"
    pts = None
    if fp.exists():
        p = FO.read(fp)
        pts = on_grid(p[(p.on_peat == 1) & p.depth_cm.notna()], khg)
    sd = next((d for d in (kf / "03_neraca" / "inputs" / "model", kf / "03_neraca" / "inputs") if (d / "stations_daily.csv").exists()),
              kf / "03_neraca" / "inputs")             # the model's own station export (may include community stations), else the deficit's
    sp, sdp = sd / "stations.csv", sd / "stations_daily.csv"
    stn = on_grid(pd.read_csv(sp), khg) if sp.exists() and sdp.exists() else None
    if stn is not None:                                          # stations whose record does not overlap the run cannot score it
        sd_dates = pd.to_datetime(pd.read_csv(sdp, usecols=["date"]).date)
        if ((sd_dates >= dates[0]) & (sd_dates <= dates[-1])).sum() == 0:
            log(f"stations in {sd} do not overlap the run ({sd_dates.min().date()} to {sd_dates.max().date()}): not scored")
            stn = None
    window = np.zeros(len(dates), bool)
    if pts is not None and len(pts):
        window = (dates >= pd.Timestamp(pts.date_from.min())) & (dates <= pd.Timestamp(pts.date_to.max()))

    managed, mnotes, target, targets = (None, {}, None, None)
    kinds = [s.strip() for s in a.managed_licences.split(",")]
    if ddm:
        managed, mnotes = managed_raster(kf, khg, kinds)
    if a.managed_target:
        levels = pd.read_csv(sdp).groupby("station_id").depth_cm.mean() if stn is not None else None
        if a.managed_target == "stations-loo" and levels is None:
            raise SystemExit("--managed-target stations-loo needs station files")
        target, mnotes, targets = managed_targets(kf, khg, kinds, a.managed_target, stn, levels)
        managed = np.isfinite(target)
        targets.to_csv(out / "managed_targets.csv", index=False, float_format="%.3f")
    blocks, snotes = None, {}
    if a.blocks != "none":
        blocks, n1 = block_levels(kf, a.dem, khg, a.blocks)
        snotes.update(n1)
    if a.existing_blocks == "brgm":
        eb, n0 = existing_block_levels(kf, khg, a.block_level, a.block_radius)
        snotes.update(n0)
        if eb is not None:                                       # with a scenario's blocks, the shallower level of the two
            blocks = eb if blocks is None else np.fmin(blocks, eb)
            snotes["existing_blocks_on"] = True
    if a.supply != "none":                                       # pumped land is held like managed land; where both, the shallower target
        sup, n2 = supply_areas(kf, a.dem, khg, a.supply, a.supply_target)
        snotes.update(n2)
        target = sup if target is None else np.where(np.isfinite(target) & np.isfinite(sup), np.fmin(target, sup), np.where(np.isfinite(target), target, sup))
        managed = np.isfinite(target)
    mnotes.update(snotes)
    b = SIM.Boundary(dd, edge, managed if ddm else None, ddm, target, blocks)
    if leak:
        b.leak_length = G.canal_length(cfg, khg)
        b.store = SIM.CanalStore(CANAL_WIDTH_M, CANAL_BED_M, a.canal_tau) if a.canal_store else None
    table = PeatTable.named(a.peat_table)
    log(f"{kf.name} {a.dem} {a.res:g} m, {khg.shape}, {len(dates)} days, peat table {a.peat_table}, drawdown {dd}, edge {edge:g} m")
    n_pts = 0 if pts is None else len(pts)
    rows = np.concatenate([[] if pts is None else pts.row.values, [] if stn is None else stn.row.values]).astype(int)
    cols = np.concatenate([[] if pts is None else pts.col.values, [] if stn is None else stn.col.values]).astype(int)
    stress = None if a.et_stress == "none" else ((-0.70, -1.82) if a.et_stress == "natural" else (float(reg["et_stress_start"]), float(reg["et_stress_end"])))
    season_default = a.season is None
    s0, s1 = (pd.Timestamp(f"{dates[-1].year}-{x}") for x in (a.season or "06-01,09-30").split(","))
    season = (dates >= s0) & (dates <= s1)
    cap_mm, cap_days = None, None
    if a.supply_cap:
        if a.supply_cap == "deficit":
            dfile0 = kf / "03_neraca" / "runs" / "deficit" / "neraca_khg.csv"
            if not dfile0.exists():
                raise SystemExit(f"--supply-cap deficit needs {dfile0} (repeat-neraca-run)")
            dk0 = pd.read_csv(dfile0).iloc[0]
            cap_mm, cap_days = float(dk0.deficit_mm), np.asarray((dates >= pd.Timestamp(dk0.period_start)) & (dates <= pd.Timestamp(dk0.period_end)))
        elif a.supply_cap == "climate":
            from repeat_neraca.supply_rule import climate_cap
            cap_mm, cap_days, w0, wmean = climate_cap(kf, dates, f.P_mm.values, f.ET_mm.values, a.dem)
            log(f"dry window from the 2018-2025 record: 14 dekads from dekad {w0 + 1} of 36, mean shortfall {wmean:.0f} mm")
            if season_default:                                       # report over the days the cap acts in (D25)
                season = np.asarray(cap_days, bool)
        else:
            cap_mm, cap_days = float(a.supply_cap), season
        if not np.asarray(cap_days).any():
            raise SystemExit("--supply-cap: the cap window has no days inside the run")
        log(f"supply cap {cap_mm:.0f} mm per managed cell over {int(np.asarray(cap_days).sum())} days")
    if season_default:
        if a.supply_cap == "climate" and season.any():
            d_in = dates[season]
            a.season = f"{d_in.min():%Y-%m-%d} to {d_in.max():%Y-%m-%d} (dry window of the cap)"
            log(f"season of the maps and the unit table: {a.season}")
        else:
            a.season = "06-01,09-30"
    r = SIM.run(khg, net, table, b, a.h0, points=(rows, cols) if len(rows) else None, keep_days=window, log=log, season_days=season,
                rain_m_day=f.P_mm.values / 1000.0, et_m_day=f.ET_mm.values / 1000.0, et_stress=stress, peat_base=a.peat_base,
                log_ponding=a.log_ponding, supply_cap_mm=cap_mm, supply_cap_days=cap_days)
    sampled = None if r["points"] is None else -100 * r["points"]          # days x samples, cm positive down

    s = r["series"]
    series = pd.DataFrame({"date": dates.date, "P_mm": f.P_mm.values, "ET_mm": f.ET_mm.values, "mean_depth_cm": -100 * s["mean_depth_m"],
                           "share_deeper_40cm": s["share_deeper_0_4"], "canal_in_mm": s["canal_in_mm"], "edge_in_mm": s["edge_in_mm"],
                           "et_share": s["et_share"], "unmanaged_mean_depth_cm": -100 * s["unmanaged_mean_depth_m"],
                           "unmanaged_share_deeper_40cm": s["unmanaged_share_deeper_0_4"], "managed_supply_mm": s["managed_supply_mm"],
                           "managed_supply_m3": s["managed_supply_m3"]})
    series.to_csv(out / "model_series.csv", index=False, float_format="%.4f")
    if r["ponded"] is not None:
        pd.DataFrame({"date": dates.date, "ponded_mm": r["ponded"][:, 0], "share_cells_ponded": r["ponded"][:, 1]}).to_csv(
            out / "model_ponded.csv", index=False, float_format="%.4f")
    write_tif(out / "model_depth_window.tif", -100 * r["window_mean_depth_m"], khg)
    write_tif(out / "model_depth_end.tif", -100 * r["final_depth_m"], khg)
    open_cells = khg.domain & ~r["fixed"] & (~r["held"] if r["held"] is not None else True)
    write_tif(out / "model_season_days_deeper_40cm.tif", np.where(open_cells, r["season_days_deeper_0_4"], np.nan), khg)   # managed and canal cells left out
    write_tif(out / "model_season_mean_depth.tif", -100 * r["season_mean_depth_m"], khg)
    if r["held"] is not None:
        write_tif(out / "model_season_managed_supply.tif", np.where(r["held"], r["season_supply_mm"], np.nan), khg)
    units = unit_table(khg, r, open_cells, int(r["season_n_days"]))
    units.to_csv(out / "model_units.csv", index=False, float_format="%.2f")
    cstore = None
    if r["leak"] is not None:
        mnotes["leaky_canal_cell_share_of_khg"] = float(r["leak"]["cells"][khg.domain].mean())
        write_tif(out / "model_canal_length.tif", np.where(r["leak"]["cells"], sum(b.leak_length.values()), np.nan), khg)
    if r["canal_stage"] is not None:                             # the canal store: level and water depth per store, mass closure, gate
        cs = r["canal_stage"]
        uid = [khg.unit_ids[k] if 0 <= k < len(khg.unit_ids) else "outside units" for k in cs["store_ids"]]
        pd.concat([pd.DataFrame({"date": dates.date, "unit_id": u, "y_m": cs["y_m"][:, k], "canal_depth_m": cs["depth_m"][:, k]})
                   for k, u in enumerate(uid)]).to_csv(out / "canal_stage.csv", index=False, float_format="%.4f")
        khg_depth = (cs["depth_m"] * cs["cells"]).sum(axis=1) / cs["cells"].sum()
        exch_m3 = np.abs(series.canal_in_mm.values) * int(r["free"].sum()) * khg.dx ** 2 / 1000.0
        med = float(np.nanmedian(khg_depth[season])) if season.any() else float("nan")
        cstore = {"stores": len(uid), "canal_area_km2": float(cs["area_m2"].sum() / 1e6), "tau_days": a.canal_tau, "width_m": CANAL_WIDTH_M,
                  "bed_m": CANAL_BED_M, "season_median_canal_depth_m": med,
                  "season_min_max_canal_depth_m": [float(np.nanmin(khg_depth[season])), float(np.nanmax(khg_depth[season]))] if season.any() else None,
                  "closure_share_of_exchange": float(np.nansum(np.abs(cs["closure_m3"])) / max(np.nansum(exch_m3), 1e-9)),
                  "gate": {f"season median canal depth in {FC.CANAL_DEPTH_RANGE_M[0]:g}-{FC.CANAL_DEPTH_RANGE_M[1]:g} m": FC.canal_depth_ok(med)}}
        (out / "canal_store.json").write_text(json.dumps(cstore, indent=2, default=float), encoding="utf-8")
    if r["held"] is not None:                                   # held cells are imposed: a "still needs rewetting" map must leave them out
        write_tif(out / "model_managed_target.tif", np.where(khg.domain, 100 * target, np.nan), khg)
    inputs = [("DTM", notes["dtm"], 1.0), ("KHG boundary", "00_inputs/khg.gpkg", 1.0), ("canals", "00_inputs/canals.gpkg (KET_KANAL)", 1.0),
              ("rain", f"{a.rain}, KHG mean", 1.0), ("ET", f"{a.et}, KHG mean", 1.0)]
    ds = depth_sources or {"peat_depth_raster": khg.notes["peat_depth_valid_in_domain"], "peat_depth_median_fill": 1 - khg.notes["peat_depth_valid_in_domain"]}
    inputs += [("peat depth", "00_inputs/peat_depth.tif", ds["peat_depth_raster"])]
    if "peat_depth_bbsdlp" in ds:
        inputs += [("peat depth", "BBSDLP 1:50k depth classes (fallback)", ds["peat_depth_bbsdlp"])]
    inputs += [("peat depth", f"KHG median {khg.notes['peat_depth_median_m']:.1f} m (fallback)", ds["peat_depth_median_fill"])]
    if managed is not None:
        inputs += [("managed land", "2025 licences " + ", ".join(kinds), float(managed[khg.domain].mean()))]
    if a.managed_target:
        inputs += [("managed target", mnotes["managed_target_mode"], float(managed[khg.domain].mean()))]
    if blocks is not None:
        inputs += [("canal blocks" + (" (scenario)" if "blocks" in mnotes else " (existing, BRGM)"), mnotes.get("blocks", mnotes.get("existing_blocks")), float(np.isfinite(blocks)[khg.domain].mean()))]
    if a.supply != "none":
        inputs += [("water supply (scenario)", mnotes["supply"], mnotes["supply_share_of_khg"])]
    inputs += [("stations", str(sp.relative_to(kf)) if stn is not None else "none", float("nan")),
               ("field points", "00_inputs/field_wtd.csv" if pts is not None else "none", float("nan"))]
    pd.DataFrame(inputs, columns=["input", "source", "share_of_khg"]).to_csv(out / "inputs.csv", index=False, float_format="%.3f")
    fixed_share = {lab: float((r["label"][khg.domain] == v).mean()) for lab, v in (("edge", 1), ("canal", 2))}
    if managed is not None:
        canal = r["label"] == 2
        mnotes["managed_share_of_canal_cells"] = float((canal & managed).sum() / max(canal.sum(), 1))

    scores, sens, brk = None, None, {}
    if pts is not None and len(pts):
        on_fixed = r["fixed"][pts.row, pts.col]
        sim_days = sampled[:, :n_pts]
        sim = np.array([np.nanmean(sim_days[(dates >= pd.Timestamp(a0)) & (dates <= pd.Timestamp(a1)), j])
                        for j, (a0, a1) in enumerate(zip(pts.date_from, pts.date_to))])
        pts = pts.assign(sim_cm=sim, obs_cm=pts.depth_cm, on_fixed=on_fixed, dist_m=FC.canal_distance(pts, cfg["canals"]["path"], khg.crs))
        pts.to_csv(out / "field_points.csv", index=False, float_format="%.2f")
        scored = pts[~pts.on_fixed].reset_index(drop=True)
        scores = FC.score(scored)
        scores["excluded"] = {"on_fixed_cell": int(pts.on_fixed.sum()), "outside_or_not_peat_or_no_depth": int(len(FO.read(fp)) - len(pts))}
        wd = dates[window]
        sens = FC.day_sensitivity(scored.obs_cm.values, sim_days[window][:, ~pts.on_fixed.values], wd)
        for by in ("dist_m", "drainage", "land_use", "status"):
            brk[by] = FC.breakdown(scored, by)
        (out / "field_scores.json").write_text(json.dumps(scores, indent=2, default=float), encoding="utf-8")
        sens.to_csv(out / "field_day_sensitivity.csv", index=False, float_format="%.3f")

    st_scores = None
    if stn is not None and len(stn):
        obs = pd.read_csv(sdp, parse_dates=["date"]).pivot(index="date", columns="station_id", values="depth_cm").reindex(dates)
        if a.screen_stations:
            obs = obs.apply(lambda col: FC.screen(col)[0].reindex(obs.index))
        sim_st = pd.DataFrame(sampled[:, n_pts:], index=dates, columns=stn.station_id.values)
        on_fixed = r["fixed"][stn.row, stn.col]
        group = stn["concession"].fillna("(none)") if "concession" in stn else pd.Series("(none)", index=stn.index)
        info = stn.assign(group=group, dist_m=FC.canal_distance(stn, cfg["canals"]["path"], khg.crs),
                          flag=np.where(on_fixed, "on_fixed_cell", np.where((r["held"] is not None) & (r["held"][stn.row, stn.col]
                                                                                    if r["held"] is not None else False), "in_managed_land", "")),
                          managed=managed[stn.row, stn.col] if managed is not None else False)
        keep = [c for c in obs.columns if c in set(info.station_id)]
        st_scores, st_table = FC.score_stations(obs[keep], sim_st[keep], info[["station_id", "group", "dist_m", "flag", "managed"]])
        g2 = st_table.assign(kind=np.where(st_table.group == "community", "community", "concession"))
        n_fixed = g2[g2.flag != ""].groupby("kind").size()
        g2 = g2[g2.flag == ""]                                  # a station on a canal or edge cell only shows the fixed canal level
        st_scores["by_kind"] = {k: {"n": int(len(v)), "on_fixed_cell": int(n_fixed.get(k, 0)), "obs_level_cm": float(v.obs_cm.median()),
                                    "sim_level_cm": float(v.sim_cm.median()),
                                    "obs_drawdown_cm": float(v.obs_drawdown_cm.median()), "sim_drawdown_cm": float(v.sim_drawdown_cm.median()),
                                    "in_managed_land": int(v.managed.sum())}
                                for k, v in g2.groupby("kind")}
        st_scores["excluded"] = {"on_fixed_cell": int(on_fixed.sum()), "outside_khg": int(len(pd.read_csv(sp)) - len(stn))}
        if r["leak"] is not None:                               # canal runs: community level and fall together; the canal store's depth
            st_scores["on_leaky_canal_cell"] = int(r["leak"]["cells"][stn.row, stn.col].sum())
            st_scores["gate"]["checks"][f"community level and drawdown within {FC.COMMUNITY_TOL_CM:g} cm"] = \
                FC.community_ok(st_scores["by_kind"].get("community"))
            if cstore is not None:
                st_scores["gate"]["checks"].update(cstore["gate"])
            st_scores["gate"]["pass"] = FC.gate_pass(st_scores["gate"]["checks"])
        dfile = kf / "03_neraca" / "runs" / "deficit" / "neraca_khg.csv"
        if dfile.exists():
            dk = pd.read_csv(dfile).iloc[0]
            sel = (dates >= pd.Timestamp(dk.period_start)) & (dates <= pd.Timestamp(dk.period_end))
            if sel.sum() == 0:
                dk = None
        if dfile.exists() and dk is not None:
            st_scores["supply_check"] = {"period": f"{dk.period_start} to {dk.period_end}", "station_deficit_mm": float(dk.deficit_mm),
                                         "model_canal_in_mm": float(series.canal_in_mm[sel].sum()),
                                         "model_edge_in_mm": float(series.edge_in_mm[sel].sum())}
            if r["held"] is not None:
                sup = float(series.managed_supply_mm[sel].sum())
                lo, hi = FC.SUPPLY_RATIO
                st_scores["supply_check"].update({"model_managed_supply_mm": sup,
                                                  "model_managed_supply_m3": float(series.managed_supply_m3[sel].sum())})
                if a.supply_cap == "deficit":
                    st_scores["supply_check"]["cap_from_deficit"] = True       # the check would pass by construction (D22): left out
                else:
                    st_scores["gate"]["checks"][f"managed supply within x{hi:g} or {FC.SUPPLY_ABS_MM:g} mm of the station deficit"] = \
                        FC.supply_ok(sup, float(dk.deficit_mm))
                st_scores["gate"]["pass"] = FC.gate_pass(st_scores["gate"]["checks"])
        st_table.to_csv(out / "station_scores.csv", index=False, float_format="%.2f")
        sim_st[keep].rename_axis("date").to_csv(out / "station_sim_daily.csv", float_format="%.1f")      # cm, positive down; rescoring needs no rerun
        (out / "station_scores.json").write_text(json.dumps(st_scores, indent=2, default=float), encoding="utf-8")

    snap = reg.snapshot()
    (out / "registry_snapshot.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
    run_cfg = {"khg": kf.name, "dem": a.dem, "res_m": a.res, "start": a.start, "end": a.end, "peat_table": a.peat_table, "drawdown": dd,
               "edge_stage": edge, "drawdown_managed": ddm, "managed_target": a.managed_target, "peat_base": a.peat_base,
               "depth_fallback": a.depth_fallback, "blocks": a.blocks, **({"existing_blocks": {"source": "brgm", "level_m": a.block_level, "radius_m": a.block_radius}} if snotes.get("existing_blocks_on") else {}),
               **({"canal_cells": "leak", "canal_store": cstore} if leak else {}), **({"screen_stations": True} if a.screen_stations else {}), **({"supply_cap": a.supply_cap, "supply_cap_mm": cap_mm} if a.supply_cap else {}), "supply": a.supply, "season": a.season, "h0": a.h0, "rain": a.rain, "et": a.et, "et_stress": stress, "inputs": cfg, "notes": {**notes, **khg.notes, **mnotes}}
    (out / "run_config.json").write_text(json.dumps(run_cfg, indent=2, default=str), encoding="utf-8")
    text = report(kf.name, a, run_cfg, series, window, fixed_share, scores, sens, brk, r["seconds"], snap["sha256"], st_scores, units)
    if leak:
        text += (f"\nCanals inside cells (D18): {mnotes['leaky_canal_cell_share_of_khg']:.0%} of the KHG's cells hold a canal and stay free; "
                 f"canal cells fixed: {fixed_share['canal']:.0%} (managed land, block reaches).\n")
    if cstore is not None:
        text += (f"\nCanal store (D19): {cstore['stores']} stores, canal water surface {cstore['canal_area_km2']:.2f} km2, outlet time constant "
                 f"{a.canal_tau:g} days. Season canal water depth below the land, KHG mean: median {cstore['season_median_canal_depth_m']:.2f} m "
                 f"(range {cstore['season_min_max_canal_depth_m'][0]:.2f} to {cstore['season_min_max_canal_depth_m'][1]:.2f} m). "
                 f"Mass closure of the coupling: {cstore['closure_share_of_exchange']:.1%} of the canal exchange. `canal_stage.csv` per store.\n")
    (out / "model_report.md").write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out}")


def unit_table(khg, r, open_cells, n_days: int) -> pd.DataFrame:
    """One row per sub-KHG (or one for the KHG without units): season summaries of the cells of that unit.

    open land = free cells not held by water management; managed = held cells. Depths in cm, positive down."""
    if khg.units is not None and len(khg.unit_ids):
        parts = [(uid, khg.units == k) for k, uid in enumerate(khg.unit_ids)]
    else:
        parts = [("KHG", khg.domain)]
    held = r["held"] if r["held"] is not None else np.zeros(khg.shape, bool)
    cell_km2 = khg.dx ** 2 / 1e6
    rows = []
    for uid, m in parts:
        m = m & khg.domain
        o, h = m & open_cells, m & held
        days = r["season_days_deeper_0_4"][o]
        rows.append({"unit_id": uid, "area_km2": m.sum() * cell_km2, "open_km2": o.sum() * cell_km2, "managed_km2": h.sum() * cell_km2,
                     "season_days": n_days,
                     "open_mean_depth_cm": float(-100 * r["season_mean_depth_m"][o].mean()) if o.any() else np.nan,
                     "open_days_deeper_40cm": float(days.mean()) if o.any() else np.nan,
                     "open_share_deeper_40cm_half_season": float((days > n_days / 2).mean()) if o.any() else np.nan,
                     "managed_supply_mm": float(r["season_supply_mm"][h].mean()) if h.any() else np.nan})
    return pd.DataFrame(rows)


def on_grid(p: pd.DataFrame, khg) -> pd.DataFrame:
    """Points (lon, lat) with their grid row and col, kept when inside the KHG."""
    from pyproj import Transformer
    x, y = Transformer.from_crs(4326, khg.crs, always_xy=True).transform(p.lon.values, p.lat.values)
    p = p.assign(col=np.floor((x - khg.transform.c) / khg.dx).astype(int), row=np.floor((khg.transform.f - y) / khg.dx).astype(int))
    p = p[(p.row >= 0) & (p.row < khg.shape[0]) & (p.col >= 0) & (p.col < khg.shape[1])]
    return p[khg.domain[p.row, p.col]].reset_index(drop=True)


def verdict(p) -> str:
    return "not testable" if p is None else ("pass" if p else "fail")


def yes_no(v) -> str:
    return "not testable" if v is None else ("yes" if v else "no")


def md_table(t: pd.DataFrame) -> list[str]:
    cols = [t.index.name or ""] + list(t.columns)
    return ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)] + [
        "| " + " | ".join(map(str, [i, *r])) + " |" for i, r in zip(t.index, t.itertuples(index=False))]


def report(name, a, rc, series, window, fixed_share, scores, sens, brk, seconds, sha, st=None, units=None) -> str:
    w = series[window]
    L = [f"# Groundwater model, {name}, {a.dem}", "",
         f"Grid {a.res:g} m; peat table `{a.peat_table}`; canal level below the surface (m): "
         + ", ".join(f"{c} {'not fixed' if v is None else f'{v:g}'}" for c, v in rc["drawdown"].items())
         + ("" if not rc.get("drawdown_managed") else "; in managed land (" + ", ".join(rc["notes"]["managed_licences"]) + f", {rc['notes']['managed_share_of_khg']:.0%} of the KHG, "
            f"{rc['notes'].get('managed_share_of_canal_cells', 0):.0%} of the canal cells): "
            + ", ".join(f"{c} {'not fixed' if v is None else f'{v:g}'}" for c, v in rc["drawdown_managed"].items()))
         + f"; edge ring {rc['edge_stage']:g} m below the surface; start {a.start} saturated ({a.h0:g} m), end {a.end}. "
         f"Rain {a.rain}, ET {a.et}, KHG mean, dekad totals spread evenly over their days; ET reduction with depth: "
         + ("none" if not rc.get("et_stress") else f"{a.et_stress}, full ET above {rc['et_stress'][0]:g} m, none below {rc['et_stress'][1]:g} m") + ". "
         f"DTM: {rc['notes']['dtm']}. "
         f"Sub-KHG units: {rc['notes']['units']}. Peat depth valid on {rc['notes']['peat_depth_valid_in_domain']:.0%} of the KHG "
         f"(gaps: median {rc['notes']['peat_depth_median_m']:.1f} m). Fixed cells: edge {fixed_share['edge']:.1%}, canals "
         f"{fixed_share['canal']:.1%} of the KHG. Run time {seconds / 60:.1f} min. Registry snapshot {sha[:12]}. Method: `repeat_neraca/model.py`.", ""]
    s = series.assign(month=pd.to_datetime(series.date).dt.to_period("M"))
    g = s.groupby("month")
    mon = pd.DataFrame({"P (mm)": g.P_mm.sum().round(0), "ET (mm)": g.ET_mm.sum().round(0), "P - ET (mm)": (g.P_mm.sum() - g.ET_mm.sum()).round(0),
                        "depth at month end (cm)": g.mean_depth_cm.last().round(0), "share deeper than 40 cm": g.share_deeper_40cm.last().round(2),
                        "canal inflow (mm)": g.canal_in_mm.sum().round(1), "edge inflow (mm)": g.edge_in_mm.sum().round(1),
                        "ET realised (share)": g.et_share.mean().round(2)})
    mon.index.name = "month"
    L += ["## By month (KHG mean over the free cells)", "", *md_table(mon), ""]
    if units is not None and len(units):
        u = units.set_index("unit_id")[["area_km2", "open_km2", "managed_km2", "open_mean_depth_cm", "open_days_deeper_40cm",
                                        "open_share_deeper_40cm_half_season", "managed_supply_mm"]].round(2)
        L += [f"## Season {a.season} per {'sub-KHG' if len(u) > 1 or u.index[0] != 'KHG' else 'KHG'} (`model_units.csv`)", "",
              f"Open land: free cells not held by water management. Days deeper than 40 cm out of {int(units.season_days.iloc[0])}; share of the open "
              "land deeper than 40 cm for more than half the season; water supplied to managed land (mm). Maps: `model_season_days_deeper_40cm.tif` "
              "(open land only), `model_season_mean_depth.tif`, `model_season_managed_supply.tif`.", "", *md_table(u), ""]
    if len(w):
        L += [f"## Window {w.date.iloc[0]} to {w.date.iloc[-1]}", "",
              f"KHG-mean depth {w.mean_depth_cm.min():.0f} to {w.mean_depth_cm.max():.0f} cm; share of the KHG deeper than 40 cm "
              f"{w.share_deeper_40cm.min():.0%} to {w.share_deeper_40cm.max():.0%}. Water put into the peat over the window: canals "
              f"{w.canal_in_mm.sum():.0f} mm, edge {w.edge_in_mm.sum():.0f} mm; rain {w.P_mm.sum():.0f} mm, ET {w.ET_mm.sum():.0f} mm.", ""]
    if scores:
        L += ["## Field points", "",
              f"Excluded: {scores['excluded']['outside_or_not_peat_or_no_depth']} points not on peat, without a depth or outside the KHG; "
              f"{scores['excluded']['on_fixed_cell']} on a canal or edge cell.", "",
              "| points | prediction | n | Spearman | bias (cm) | RMSE (cm) | MAE (cm) |", "|---|---|---|---|---|---|---|"]
        for sub in ("unflagged", "all"):
            for k in ("model", "distance", "constant"):
                v = scores[sub][k]
                L.append(f"| {sub} | {k} | {v.get('n')} | {v.get('spearman', float('nan')):.2f} | {v.get('bias_cm', float('nan')):.0f} | "
                         f"{v.get('rmse_cm', float('nan')):.0f} | {v.get('mae_cm', float('nan')):.0f} |")
        g = scores["gate"]
        L += ["", f"**Gate: {verdict(g['pass'])}** (" + "; ".join(f"{k}: {yes_no(v)}" for k, v in g["checks"].items())
              + "). Distance prediction: depth = "
              f"{scores['unflagged']['distance_fit']['intercept_cm']:.0f} + {scores['unflagged']['distance_fit']['slope_cm_per_log_m']:.1f} ln(1 + d) cm, fitted to the same points.", ""]
        if "obs_variance_between_groups" in scores["unflagged"]:
            L += [f"Share of the observed variance between the {scores['unflagged']['n_groups']} field teams (`group`): "
                  f"{scores['unflagged']['obs_variance_between_groups']:.0%}. A large share means the readings differ by who took them more "
                  "than by place: a difference in method or in visit date, which the survey cannot tell apart. A model can follow neither "
                  "without the dates.", ""]
        if sens is not None and len(sens):
            L += [f"Single-day scores across the window: Spearman {sens.spearman.min():.2f} to {sens.spearman.max():.2f}, bias "
                  f"{sens.bias_cm.min():.0f} to {sens.bias_cm.max():.0f} cm (`field_day_sensitivity.csv`).", ""]
        for by, t in brk.items():
            L += [f"### By {'distance to the nearest canal (m)' if by == 'dist_m' else by}", "", *md_table(t), ""]
    if st:
        d = st["dynamics"]
        L += ["## Water-table stations", "",
              f"{d['n_stations']} stations with at least 30 days ({st['excluded']['on_fixed_cell']} on a canal or edge cell, scored but "
              f"flagged; {st['excluded']['outside_khg']} outside the KHG).", "",
              "| points | prediction | n | Spearman | bias (cm) | RMSE (cm) | MAE (cm) |", "|---|---|---|---|---|---|---|"]
        for part in ("unflagged", "all"):
            for k in ("model", "distance", "constant"):
                v = st[part][k]
                L.append(f"| {part} | {k} | {v.get('n')} | {v.get('spearman', float('nan')):.2f} | {v.get('bias_cm', float('nan')):.0f} | "
                         f"{v.get('rmse_cm', float('nan')):.0f} | {v.get('mae_cm', float('nan')):.0f} |")
        g = st["gate"]
        L += ["", f"Levels are each station's mean over its days. Dynamics, on the {d['n_unflagged']} unflagged stations: median per-station r {d['median_station_r']:.2f}; mean curve "
              f"r {d['khg_mean_r']:.2f} (mean curve of these stations), bias {d['khg_mean_bias_cm']:.0f} cm (observed {d['obs_khg_mean_cm']:.0f}, simulated "
              f"{d['sim_khg_mean_cm']:.0f} cm); drawdown over the record, median observed {d['obs_drawdown_median_cm']:.0f} cm, simulated "
              f"{d['sim_drawdown_median_cm']:.0f} cm, Spearman across stations {d['drawdown_spearman']:.2f}.", ""]
        if "obs_variance_between_groups" in st["unflagged"]:
            L += [f"Share of the variance of station levels between the {st['unflagged']['n_groups']} groups (concessions): "
                  f"{st['unflagged']['obs_variance_between_groups']:.0%}.", ""]
        if "by_kind" in st:
            L += ["| stations | n (and on a canal or edge cell, left out) | in managed land | level observed (cm) | level simulated (cm) | drawdown observed (cm) | drawdown simulated (cm) |",
                  "|---|---|---|---|---|---|---|"]
            L += [f"| {k} | {v['n']} ({v['on_fixed_cell']}) | {v['in_managed_land']} | {v['obs_level_cm']:.0f} | {v['sim_level_cm']:.0f} | {v['obs_drawdown_cm']:.0f} | "
                  f"{v['sim_drawdown_cm']:.0f} |" for k, v in st["by_kind"].items()]
            L += ["", "Medians over the unflagged stations of each kind.", ""]
        if "supply_check" in st and "model_managed_supply_mm" in st["supply_check"]:
            c = st["supply_check"]
            L += [f"Managed land held at its target: water management supplied {c['model_managed_supply_mm']:.0f} mm over the managed land "
                  f"({c['model_managed_supply_m3'] / 1e6:.1f} million m3) in {c['period']}; the station-based deficit is {c['station_deficit_mm']:.0f} mm "
                  "(the stations stand in managed land). Stations in managed land are flagged `in_managed_land`: their level is imposed.", ""]
        if "supply_check" in st:
            c = st["supply_check"]
            L += [f"Supply check, {c['period']}: deficit from the stations (repeat-neraca-run) {c['station_deficit_mm']:.0f} mm; water the "
                  f"model's canals put into the peat {c['model_canal_in_mm']:.0f} mm, edge {c['model_edge_in_mm']:.0f} mm.", ""]
        L += [f"**Station gate: {verdict(g['pass'])}** ("
              + "; ".join(f"{k}: {yes_no(v)}" for k, v in g["checks"].items()) + ").", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
