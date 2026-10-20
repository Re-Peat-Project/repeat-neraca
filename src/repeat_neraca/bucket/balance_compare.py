#!/usr/bin/env python3
"""The team's neraca air (a rain minus evaporation balance) per sub-KHG from different rain and evaporation sources: does it separate sub-KHG?

  python -m repeat_neraca.bucket.balance_compare --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml [--sources terraclimate,era5,wapor]

The balance is the one of the Kahayan-Sebangau study and of `common/indicators.py` (`u_wb_mean`, `u_deficit_months`), monthly:
    WB = P x (1 - interception of the land cover) x (1 - runoff coefficient) - ET
with the interception per WorldCover class and the runoff coefficient from the config parameters. A month is in deficit when WB < 0.
It is computed for the months of `neraca.window_months` (April to October) of every year in `neraca.years`, per sub-KHG, from:

  terraclimate   TerraClimate rain (ppt) and actual evapotranspiration (aet), monthly, about 4 km (cache_dir/<khg>/climate; ends 2021-12)
  era5           ERA5 rain and evaporation, 0.25 degrees, the daily forcing of the neraca air module
  wapor          ERA5 rain with WaPOR v3 evapotranspiration, 300 m, dekadal (reads about 20 files per year the first time)
  chirps         CHIRPS v3 rain with ERA5 evaporation, 5 km (only if the CHIRPS server lets us read; see scripts/README.md)

There is no observation of this balance to score it against (station water tables reflect management as well), so the questions are
about whether it can be used to rank sub-KHG at all:
  1. How much do sub-KHG differ (spread across sub-KHG) compared with how much the sources differ (offset of the KHG mean)?
  2. Do the sources rank the sub-KHG the same way (Spearman across sub-KHG)?
  3. Is the spatial pattern stable from year to year (Spearman of the sub-KHG means between years)?
A balance that varies little between sub-KHG, ranks them differently with every source and reshuffles them every year cannot separate them.

Writes neraca_balance_compare.md and neraca_balance_units.csv in the output folder.
"""
from __future__ import annotations

import argparse
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from repeat_common import grid as G
from .config import load_config
from repeat_common import forcing as FO
from .run import PRESET, year_window

log = logging.getLogger("prioritas.neraca")


def zonal_mean(label: np.ndarray, n: int, arr: np.ndarray) -> np.ndarray:
    ok = (label >= 0) & np.isfinite(arr)
    s = np.bincount(label[ok], weights=arr[ok].astype("float64"), minlength=n)
    c = np.bincount(label[ok], minlength=n)
    return np.divide(s, c, out=np.full(n, np.nan), where=c > 0)


def interception(label: np.ndarray, n: int, worldcover: Path | None, by_class: dict) -> np.ndarray:
    """Interception share per sub-KHG: sum over WorldCover classes of (class value x share of the sub-KHG in that class)."""
    icpt = np.zeros(n)
    if worldcover is None or not Path(worldcover).exists():
        return icpt
    import rasterio
    with rasterio.open(worldcover) as src:
        wc = src.read(1)
    for cls, v in (by_class or {}).items():
        icpt += float(v) * zonal_mean(label, n, (wc == int(cls)).astype("float32")) if wc.shape == label.shape else 0.0
    return icpt


def monthly_from_daily(dates: pd.DatetimeIndex, P: np.ndarray, E: np.ndarray, label, n, grid, transform, months) -> tuple[np.ndarray, np.ndarray]:
    """(months x units) monthly rain and evaporation in mm from a daily forcing on its own grid (only complete months count)."""
    w = FO.unit_weights(label, n, grid, transform, P.shape[1:])
    T = len(dates)
    Pu = P.reshape(T, -1).astype("float64") @ w.T
    Eu = E.reshape(T, -1).astype("float64") @ w.T
    mo = dates.month.values
    out_p, out_e = [], []
    for m in months:
        sel = mo == m
        full = sel.sum() >= 27
        out_p.append(Pu[sel].sum(axis=0) if full else np.full(n, np.nan))
        out_e.append(Eu[sel].sum(axis=0) if full else np.full(n, np.nan))
    return np.array(out_p), np.array(out_e)


def monthly_terraclimate(cache: Path, year: int, label, n, grid, months):
    fp, fe = cache / "climate" / f"ppt_{year}.tif", cache / "climate" / f"aet_{year}.tif"
    if not (fp.exists() and fe.exists()):
        return None
    P = np.array([zonal_mean(label, n, G.warp_to_grid(str(fp), grid, band=m)) for m in months])
    E = np.array([zonal_mean(label, n, G.warp_to_grid(str(fe), grid, band=m)) for m in months])
    return P, E


def balances(cfg: dict, kid: str, up, grid, sources: list[str]) -> dict:
    """{source: {year: (months x units) balance in mm/month}}"""
    nc = cfg["neraca"]
    cache = Path(cfg["cache_dir"]) / kid
    label = G.label_raster(up, grid)
    n = len(up)
    params = load_config(None, {}, "neraca")["params"]
    icpt = interception(label, n, cache / "static" / "worldcover.tif", params["interception_by_class"])
    c = float(params["runoff_coefficient"])
    m0, m1 = nc["window_months"]
    months = list(range(m0, m1 + 1))
    era5 = {**cfg["sources"]["era5"]}
    stride = int(era5.get("evap_stride", 3))
    out: dict = {s: {} for s in sources}
    for y in nc["years"]:
        start, end = year_window(y, nc)
        for s in sources:
            if s == "terraclimate":
                pe = monthly_terraclimate(cache, y, label, n, grid, months)
            else:
                rain, evap = {"era5": ("era5", "era5"), "wapor": ("era5", "wapor"), "chirps": ("chirps", "era5")}[s]
                f = FO.forcing_for(grid, era5, start, end, cache / "neraca", nc["tz_hours"], stride, rain=rain, evap=evap)
                pe = monthly_from_daily(f["dates"], f["P"], f["E"], label, n, grid, f["transform"], months)
            if pe is None:
                log.warning("%s %s: no data", s, y)
                continue
            P, E = pe
            out[s][y] = P * (1 - icpt)[None, :] * (1 - c) - E
    return out


def _rho(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[ok], b[ok]).correlation) if ok.sum() >= 5 and np.nanstd(a[ok]) > 0 and np.nanstd(b[ok]) > 0 else float("nan")


def summarise(bal: dict, unit_ids) -> tuple[str, pd.DataFrame]:
    srcs = [s for s in bal if bal[s]]
    mean_wb, deficit = {}, {}
    for s in srcs:
        arr = np.stack(list(bal[s].values()))                          # years x months x units
        mean_wb[s] = np.nanmean(arr, axis=(0, 1))
        deficit[s] = np.nanmean((arr < 0).sum(axis=1).astype(float), axis=0)
    df = pd.DataFrame({"unit_id": unit_ids, **{f"wb_{s}": mean_wb[s] for s in srcs}, **{f"deficit_{s}": deficit[s] for s in srcs}})
    L = ["| source | KHG mean balance (mm/month) | sub-KHG min | median | max | std across sub-KHG | share of sub-KHG in deficit | deficit months per year: min / max |", "|---|---|---|---|---|---|---|---|"]
    for s in srcs:
        v = mean_wb[s]
        L.append(f"| {s} | {np.nanmean(v):.1f} | {np.nanmin(v):.1f} | {np.nanmedian(v):.1f} | {np.nanmax(v):.1f} | {np.nanstd(v):.2f} | {100 * np.nanmean(v < 0):.0f}% | {np.nanmin(deficit[s]):.1f} / {np.nanmax(deficit[s]):.1f} |")
    lines = ["## 1. How much sub-KHG differ, and how much the sources differ", "", *L, ""]
    if len(srcs) > 1:
        base = srcs[0]
        lines += [f"Offset of the KHG mean from `{base}`: " + "; ".join(f"{s} {np.nanmean(mean_wb[s]) - np.nanmean(mean_wb[base]):+.1f} mm/month" for s in srcs[1:]) + ".", ""]
    lines += ["## 2. Do the sources rank the sub-KHG the same way?", "", "| pair | rho of mean balance | rho of deficit months |", "|---|---|---|"]
    for a, b in combinations(srcs, 2):
        lines.append(f"| {a} vs {b} | {_rho(mean_wb[a], mean_wb[b]):.2f} | {_rho(deficit[a], deficit[b]):.2f} |")
    lines += ["", "## 3. Is the pattern stable from year to year?", "", "| source | years | rho of the sub-KHG means between years (min over pairs) | median | std of the KHG mean between years (mm/month) | std across sub-KHG (mm/month) |", "|---|---|---|---|---|---|"]
    for s in srcs:
        yrs = sorted(bal[s])
        per = {y: np.nanmean(bal[s][y], axis=0) for y in yrs}
        rr = [_rho(per[a], per[b]) for a, b in combinations(yrs, 2)]
        inter = np.nanstd([np.nanmean(per[y]) for y in yrs])
        lines.append(f"| {s} | {', '.join(map(str, yrs))} | {np.nanmin(rr) if rr else float('nan'):.2f} | {np.nanmedian(rr) if rr else float('nan'):.2f} | {inter:.1f} | {np.nanstd(mean_wb[s]):.2f} |")
    return "\n".join(lines), df


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--sources", default="terraclimate,era5,wapor")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    for noisy in ("azure", "rasterio._env", "rasterio._err", "fsspec", "pyogrio._io"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    import geopandas as gpd
    cfg = load_config(a.config, PRESET, "neraca")
    out = Path(cfg["out"])
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    idf = cfg["khg_id_field"]
    kid = str(khg[idf].iloc[0]) if idf in khg.columns else "KHG01"
    grid = G.make_grid(khg.geometry.union_all(), float(cfg["grid_res_m"]))
    units = G.load_units(cfg, khg)
    up = units.to_crs(grid.crs).reset_index(drop=True)
    sources = [s.strip() for s in a.sources.split(",") if s.strip()]
    bal = balances(cfg, kid, up, grid, sources)
    body, df = summarise(bal, up["unit_id"].values)
    nc = cfg["neraca"]
    head = [f"# Neraca air as a rain minus evaporation balance, KHG {kid}: {len(up)} sub-KHG", "",
            f"Monthly balance `P x (1 - interception) x (1 - runoff coefficient) - ET` for months {nc['window_months'][0]} to {nc['window_months'][1]} of {', '.join(map(str, nc['years']))} "
            "(method and sources in `repeat_neraca/bucket/balance_compare.py`). Sources: " + ", ".join(sources) + ".", ""]
    text = "\n".join(head) + body + "\n"
    (out / "neraca_balance_compare.md").write_text(text, encoding="utf-8")
    df.to_csv(out / "neraca_balance_units.csv", index=False)
    print(text)


if __name__ == "__main__":
    main()
