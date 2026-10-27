"""Map layers of the neraca air for one KHG: the balance per sub-KHG and the SiTMAT stations, in one GeoPackage.

    repeat-neraca-map --khg <path to _khg/<code>_<name>>        (also written by repeat-neraca-batch after the balance)

Writes ``03_neraca/runs/balance/neraca_map.gpkg`` (``runs/balance_khg_level`` for a KHG without sub-KHG units):

* ``neraca_units``: the sub-KHG polygons with the balance of ``neraca_balance_unit.csv`` (u_wb_mean, u_deficit_months, P - ET, ...),
  the monthly climatology of the central ET source (``wb_m01`` .. ``wb_m12``, mm, mean over the years in the monthly table), the dry-season
  mean ``wb_dry_mm`` (July to October) and the KHG deficit of ``runs/deficit/neraca_khg.csv``. ``order_ok`` copies ``balance_stable_ok``:
  where it is 0 the order of the units is not trustworthy, so a map should grey the values out rather than rank them.
* ``neraca_stations``: SiTMAT stations with their water table in the deficit window (or the whole record when there is no deficit run):
  depth at the start and the end (cm, positive down), the change, the deepest value, the share of days deeper than 40 cm (the PP 57/2016
  limit) and the sub-KHG they lie in.
* ``neraca_monthly``: the monthly balance per unit and ET source (table, no geometry), for charts.

There is no water-table surface: the gridded physical model did not pass the station check (docs/physical-model.md).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

DRY_MONTHS = (7, 8, 9, 10)
TMA_LIMIT_CM = 40


def _units(kf: Path, n_rows: int):
    import geopandas as gpd
    sub = kf / "02_delineation" / "subkhg_units.gpkg"
    if sub.exists():
        return gpd.read_file(sub)[["unit_id", "geometry"]], "balance"
    khg = kf / "00_inputs" / "khg.gpkg"
    if khg.exists() and n_rows == 1:
        g = gpd.read_file(khg)
        return gpd.GeoDataFrame({"unit_id": [None]}, geometry=[g.union_all()], crs=g.crs), "balance_khg_level"
    raise SystemExit(f"{kf.name}: no sub-KHG units and no single KHG polygon to draw the balance on")


def station_summary(stations: pd.DataFrame, daily: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
    """Per station: depth at the start and end of the window, change, deepest value and share of days deeper than 40 cm."""
    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"])
    if start is not None:
        d = d[(d["date"] >= pd.Timestamp(start)) & (d["date"] <= pd.Timestamp(end))]
    rows = []
    for sid, g in d.dropna(subset=["depth_cm"]).sort_values("date").groupby("station_id"):
        rows.append(dict(station_id=sid, n_days=len(g), first_date=g["date"].iloc[0].date().isoformat(), last_date=g["date"].iloc[-1].date().isoformat(),
                         depth_start_cm=float(g["depth_cm"].iloc[0]), depth_end_cm=float(g["depth_cm"].iloc[-1]),
                         change_cm=float(g["depth_cm"].iloc[-1] - g["depth_cm"].iloc[0]), depth_max_cm=float(g["depth_cm"].max()),
                         share_deeper_40cm=float((g["depth_cm"] > TMA_LIMIT_CM).mean())))
    return stations.merge(pd.DataFrame(rows), on="station_id", how="inner")


def write_map(kf: Path) -> Path:
    import geopandas as gpd
    kf = Path(kf)
    unit_csv = next((p for p in (kf / "03_neraca" / "runs" / "balance" / "neraca_balance_unit.csv",
                                 kf / "03_neraca" / "runs" / "balance_khg_level" / "neraca_balance_unit.csv") if p.exists()), None)
    if unit_csv is None:
        raise SystemExit(f"{kf.name}: no neraca_balance_unit.csv; run repeat-neraca-balance first")
    t = pd.read_csv(unit_csv, dtype={"unit_id": str})
    units, run = _units(kf, len(t))
    if units["unit_id"].isna().all():
        units["unit_id"] = t["unit_id"].iloc[0]
    g = units.merge(t, on="unit_id", how="left")
    g["order_ok"] = g["balance_stable_ok"]
    mon_path = unit_csv.parent / "neraca_balance_monthly.csv"
    mon = pd.read_csv(mon_path, dtype={"unit_id": str}) if mon_path.exists() else pd.DataFrame(columns=["month", "unit_id", "WB_mm", "et_source"])
    if len(mon):
        central = mon["et_source"].iloc[0]                         # written in the order of the ET sources, the central one first
        m = mon[mon["et_source"] == central].copy()
        m["moy"] = pd.PeriodIndex(m["month"], freq="M").month
        clim = m.pivot_table(index="unit_id", columns="moy", values="WB_mm", aggfunc="mean")
        clim.columns = [f"wb_m{c:02d}" for c in clim.columns]
        g = g.merge(clim, left_on="unit_id", right_index=True, how="left")
        g["wb_dry_mm"] = g[[f"wb_m{c:02d}" for c in DRY_MONTHS if f"wb_m{c:02d}" in g]].mean(axis=1)
        g["et_source"] = central
    deficit = kf / "03_neraca" / "runs" / "deficit" / "neraca_khg.csv"
    window = (None, None)
    if deficit.exists():
        d = pd.read_csv(deficit).iloc[0]
        g["khg_deficit_mm"] = float(d["deficit_mm"])
        g["khg_deficit_window"] = f"{d['period_start']} to {d['period_end']}"
        window = (d["period_start"], d["period_end"])
    out = unit_csv.parent / "neraca_map.gpkg"
    if out.exists():
        out.unlink()
    gpd.GeoDataFrame(g, geometry="geometry", crs=units.crs).to_file(out, layer="neraca_units", driver="GPKG")
    st, daily = kf / "03_neraca" / "inputs" / "stations.csv", kf / "03_neraca" / "inputs" / "stations_daily.csv"
    if st.exists() and daily.exists():
        s = station_summary(pd.read_csv(st), pd.read_csv(daily), *window)
        if len(s):
            pts = gpd.GeoDataFrame(s, geometry=gpd.points_from_xy(s["lon"], s["lat"]), crs="EPSG:4326").to_crs(units.crs)
            pts = gpd.sjoin(pts, units[["unit_id", "geometry"]], how="left", predicate="within").drop(columns="index_right")
            pts = pts[~pts.index.duplicated()]
            pts.to_file(out, layer="neraca_stations", driver="GPKG")
    if len(mon):
        import pyogrio
        pyogrio.write_dataframe(mon, out, layer="neraca_monthly", driver="GPKG")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True, help="KHG work folder, e.g. _khg/16.02.01_sugihan_lumpur")
    a = ap.parse_args(argv)
    print(write_map(Path(a.khg)))


if __name__ == "__main__":
    main()
