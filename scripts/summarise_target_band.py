"""Compare groundwater model runs across managed-land targets, canal levels and canal modes: what changes on the open land, what the
supply is, and how the community stations compare. Two tables: open land and supply per run; community stations per run that has them.

  python scripts/summarise_target_band.py --runs "$REPEAT_KHG/*/03_neraca/lidar/runs/model/tropical-large_*_mt0.[468]_e0.3_*_pb_dbbsdlp" \
      --out docs/reports/managed_target_band.md

Per run, from `model_units.csv` (season, area-weighted over the sub-KHG) and `station_scores.json` (community stations, off canal cells):
  open land       free cells not held by water management: mean depth and days deeper than 40 cm in the season
  same cells      plain cell means over the open cells of a fixed-cell run of the same KHG and grid (`model_season_mean_depth.tif`,
                  `model_season_days_deeper_40cm.tif`): runs with canals inside cells count canal cells as open land, so their open-land
                  figures above mix a change of area with the physics
  supply          water supplied to the managed land in the season (mm over the managed land)
  community       the same set of community stations in every run of a KHG and grid (those a fixed-cell run scores, so runs with
                  canals inside cells compare like with like): median level and drawdown (`station_scores.csv`), and median of the first
                  and last 7 days of each station's record, observed and simulated (the station inputs and `station_sim_daily.csv`).
                  Observed depths can be negative (water above the ground); the model removes ponded water, so it cannot go above 0.
                  The same on the screened record (`fieldcheck.screen`: restarts after gaps, settling days, stuck loggers left out):
                  level (mean over kept days) and drawdown (last minus first 7 kept days). Also the number of community stations the
                  run's own gate scores.
  canal store     season median canal water depth below the land, KHG mean (`canal_store.json`, runs with `--canal-store`)
Canal levels, the target and the canal mode are read from the run folder name (`p<primary>_s<secondary>_t<tertiary>_mt<target>`, then
`_lk` for canals inside cells, `_cs<tau>` for the canal store).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from repeat_neraca.groundwater import fieldcheck as FC


def tif(path: Path) -> np.ndarray:
    import rasterio
    with rasterio.open(path) as r:
        a = r.read(1).astype(float)
        if r.nodata is not None:
            a[a == r.nodata] = np.nan
    return a


def same_cells(d: Path, mask) -> dict:
    """Plain cell means of season depth (cm) and days deeper than 40 cm over `mask`."""
    if mask is None:
        return {"same cells: mean depth (cm)": "", "same cells: days > 40 cm": ""}
    return {"same cells: mean depth (cm)": round(float(np.nanmean(tif(d / "model_season_mean_depth.tif")[mask]))),
            "same cells: days > 40 cm": round(float(np.nanmean(tif(d / "model_season_days_deeper_40cm.tif")[mask])))}


def edge_weeks(d: Path, ids: list, days: int = 7, screened: bool = False) -> tuple:
    """Median over stations of the mean of the first and of the last `days` valid days, observed and simulated (cm); with `screened`, the
    observed record passed through `fieldcheck.screen` first, and also the median level over the kept days."""
    kf = d.parents[4]
    sd = next((x for x in (kf / "03_neraca" / "inputs" / "model", kf / "03_neraca" / "inputs") if (x / "stations_daily.csv").exists()), None)
    if sd is None or not (d / "station_sim_daily.csv").exists():
        return None
    sim = pd.read_csv(d / "station_sim_daily.csv", parse_dates=["date"]).set_index("date")
    obs = pd.read_csv(sd / "stations_daily.csv", parse_dates=["date"]).pivot(index="date", columns="station_id", values="depth_cm").reindex(sim.index)
    first, last, level = [], [], []
    for i in ids:
        if i not in sim or i not in obs:
            continue
        oi = FC.screen(obs[i])[0].reindex(sim.index) if screened else obs[i]
        ok = oi.notna() & sim[i].notna()
        if ok.sum() < 2 * days:
            continue
        o, m = oi[ok], sim[i][ok]
        first.append((o.iloc[:days].mean(), m.iloc[:days].mean()))
        last.append((o.iloc[-days:].mean(), m.iloc[-days:].mean()))
        level.append((o.mean(), m.mean()))
    if not first:
        return None
    return np.median(first, axis=0), np.median(last, axis=0), np.median(level, axis=0), np.median(np.subtract(last, first), axis=0), len(first)


def same_set(d: Path, ids: set) -> dict:
    """The community stations in `ids`: median level and drawdown, first and last week (cm), observed / simulated."""
    if not ids or not (d / "station_scores.csv").exists():
        return {}
    t = pd.read_csv(d / "station_scores.csv")
    t = t[t.station_id.isin(ids)]
    e = edge_weeks(d, sorted(ids))
    q = edge_weeks(d, sorted(ids), screened=True)
    f = lambda pair: f"{pair[0]:.0f} / {pair[1]:.0f}"
    return {"stations": len(t), "level obs / sim (cm)": f((t.obs_cm.median(), t.sim_cm.median())),
            "drawdown obs / sim (cm)": f((t.obs_drawdown_cm.median(), t.sim_drawdown_cm.median())),
            "first week obs / sim (cm)": f(e[0]) if e else "", "last week obs / sim (cm)": f(e[1]) if e else "",
            "screened: stations": q[4] if q else 0, "screened: level obs / sim (cm)": f(q[2]) if q else "",
            "screened: drawdown obs / sim (cm)": f(q[3]) if q else ""}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, nargs="+", help="run folders or glob patterns")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    runs = sorted({Path(p) for pat in a.runs for p in glob.glob(pat)})
    ref, cells = {}, {}                                        # (KHG, grid) -> community stations scored / open cells of a fixed-cell run
    for d in runs:
        g = re.search(r"_(\d+)m_", d.name)
        if g and "_lk_" not in d.name and (d / "station_scores.csv").exists():
            t = pd.read_csv(d / "station_scores.csv", keep_default_na=False)
            ref.setdefault((d.parents[4].name, g.group(1)), set(t[(t.group == "community") & (t.flag == "")].station_id))
        if g and "_lk_" not in d.name and (d / "model_season_days_deeper_40cm.tif").exists():
            cells.setdefault((d.parents[4].name, g.group(1)), np.isfinite(tif(d / "model_season_days_deeper_40cm.tif")))
    rows, crows = [], []
    for d in runs:
        m = re.search(r"_p([\d.]+)_s([\d.]+)_t([\d.]+)_mt([\d.]+)_", d.name)
        if not m or not (d / "model_units.csv").exists():
            continue
        u = pd.read_csv(d / "model_units.csv")
        w = lambda col, area: float(np.nansum(u[col] * u[area]) / u.loc[u[col].notna(), area].sum()) if u[area].sum() else np.nan
        tau = re.search(r"_cs([\d.]+)_", d.name)
        mode = f"store, tau {tau.group(1)} d" if tau else ("leak" if "_lk_" in d.name else "fixed")
        cs = json.loads((d / "canal_store.json").read_text()) if (d / "canal_store.json").exists() else {}
        c = json.loads((d / "station_scores.json").read_text()).get("by_kind", {}).get("community", {}) if (d / "station_scores.json").exists() else {}
        key = (d.parents[4].name, re.search(r"_(\d+)m_", d.name).group(1))
        run = {"KHG": key[0], "grid (m)": key[1], "canals p/s/t (m)": "/".join(m.groups()[:3]), "canal cells": mode, "target (m)": m.group(4)}
        rows.append({**run, "managed (km2)": round(u.managed_km2.sum()), "open (km2)": round(u.open_km2.sum()),
                     "open: mean depth (cm)": round(w("open_mean_depth_cm", "open_km2")),
                     "open: days > 40 cm": round(w("open_days_deeper_40cm", "open_km2")),
                     **same_cells(d, cells.get(key)),
                     "supply (mm)": round(w("managed_supply_mm", "managed_km2")),
                     "canal depth, season median (m)": f"{cs['season_median_canal_depth_m']:.2f}" if cs else ""})
        same = same_set(d, ref.get(key, set()))
        if same:
            crows.append({**run, **same, "stations the run's gate scores": c.get("n", 0)})
    order = ["KHG", "grid (m)", "canals p/s/t (m)", "canal cells", "target (m)"]
    L = ["# Managed-land targets and canal modes", "",
         "Written by `scripts/summarise_target_band.py`. Season June to September 2026. Open land and supply are area-weighted over the sub-KHG "
         "(`model_units.csv`); runs with canals inside cells count canal cells as open land, so compare modes on the same cells (plain cell "
         "means over the open cells of the fixed-cell run). Days out of the season's length.", ""]
    for name, rr in (("Open land and supply", rows), ("Community stations (the same stations in every run of a KHG and grid)", crows)):
        if not rr:
            continue
        t = pd.DataFrame(rr).sort_values(order)
        L += [f"## {name}", "", "| " + " | ".join(t.columns) + " |", "|" + "---|" * len(t.columns)]
        L += ["| " + " | ".join(map(str, r)) + " |" for r in t.itertuples(index=False)] + [""]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
