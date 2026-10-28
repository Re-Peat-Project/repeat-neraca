"""Rank KHG as test sites for the groundwater model by what their SiTMAT water-table stations can show.

  python scripts/rank_station_sites.py --out docs/reports/station_sites.md          # needs SITMAT_PROCESSED, REPEAT_HUB, REPEAT_KHG

Per KHG, from `$SITMAT_PROCESSED/stations_geo.csv` (station -> KHG) and `daily_long.csv` (unflagged days only):
  good stations      concession stations with at least --min-days-concession days, community stations with at least --min-days-community
  level spread       standard deviation of the good stations' mean levels (cm): the spatial signal a model can be scored on
  dry drawdown       per station, mean level of the last 14 days of --dry minus the first 14 (cm, positive = deeper), median and spread
  groups             concessions (company codes) among the good stations; community stations count as one group
LiDAR, sub-KHG units and selection come from the hub (`sites/<folder>/khg.yaml`, `selected_khg.csv`) and the KHG work folders, where they
exist. Water levels in SiTMAT are negative below the surface; depths here are cm, positive down.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-days-concession", type=int, default=120)
    ap.add_argument("--min-days-community", type=int, default=45)
    ap.add_argument("--dry", default="2026-06-01,2026-09-30", help="dry-season window for the drawdown")
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args(argv)
    from repeat_common import khg as K
    sp = Path(os.environ["SITMAT_PROCESSED"])
    hub = Path(os.environ["REPEAT_HUB"])
    geo = pd.read_csv(sp / "stations_geo.csv")
    st = pd.read_csv(sp / "stations.csv")[["station_id", "company_code"]]
    d = pd.read_csv(sp / "daily_long.csv", usecols=["kind", "station_id", "date", "water_level_cm", "flag"], parse_dates=["date"])
    d = d[d.flag.isna() & d.water_level_cm.notna()].assign(depth_cm=lambda x: -x.water_level_cm)

    per = d.groupby(["kind", "station_id"]).agg(days=("date", "nunique"), level_cm=("depth_cm", "mean")).reset_index()
    d0, d1 = (pd.Timestamp(x) for x in a.dry.split(","))
    dry = d[(d.date >= d0) & (d.date <= d1)]
    first = dry[dry.date < d0 + pd.Timedelta(days=14)].groupby("station_id").depth_cm.mean()
    last = dry[dry.date > d1 - pd.Timedelta(days=14)].groupby("station_id").depth_cm.mean()
    per["drawdown_cm"] = per.station_id.map(last - first)
    per = per.merge(geo[["station_id", "khg_name", "khg_dist_km"]], on="station_id", how="left").merge(st, on="station_id", how="left")
    per = per[per.khg_name.notna() & (per.khg_dist_km == 0)]
    per["good"] = np.where(per.kind == "concession", per.days >= a.min_days_concession, per.days >= a.min_days_community)

    sel = pd.read_csv(hub / "sites" / "selected_khg.csv")
    selected = set(sel.khg_name_in_gpkg)
    rows = []
    for name, g in per.groupby("khg_name"):
        try:
            info = K.lookup(name)
        except Exception:
            info = {"khg_code": "?", "name": name}
        code = str(info.get("khg_code", "?")).replace("KHG.", "")
        gg = g[g.good]
        folder = K.folder_name(code) if code != "?" else None
        ky = hub / "sites" / folder / "khg.yaml" if folder else None
        lidar = "?"
        if ky and ky.exists():
            lv = (yaml.safe_load(ky.read_text(encoding="utf-8")).get("dems") or {}).get("lidar") or {}
            lidar = "no" if lv.get("skip") else "yes"
        kf = Path(os.environ["REPEAT_KHG"]) / folder if folder else None
        units = "yes" if kf and any(kf.glob("02_delineation/**/subkhg_units.gpkg")) else ("no" if kf and kf.exists() else "?")
        groups = gg[gg.kind == "concession"].company_code.nunique() + int((gg.kind == "community").any())
        rows.append({"KHG": name, "code": code, "selected": "yes" if f"KHG {name}" in selected or name in selected else "",
                     "good concession": int((gg.kind == "concession").sum()), "good community": int((gg.kind == "community").sum()),
                     "groups": int(groups), "level mean (cm)": round(float(gg.level_cm.mean()), 0) if len(gg) else np.nan,
                     "level spread (cm)": round(float(gg.level_cm.std()), 1) if len(gg) > 1 else np.nan,
                     "dry drawdown median (cm)": round(float(gg.drawdown_cm.median()), 0) if gg.drawdown_cm.notna().any() else np.nan,
                     "dry drawdown spread (cm)": round(float(gg.drawdown_cm.std()), 1) if gg.drawdown_cm.notna().sum() > 1 else np.nan,
                     "LiDAR": lidar, "sub-KHG units": units})
    t = pd.DataFrame(rows)
    t["good"] = t["good concession"] + t["good community"]
    t = t.sort_values(["good", "level spread (cm)"], ascending=False)
    t.to_csv(Path(a.out).with_suffix(".csv"), index=False)
    top = t.head(a.top).drop(columns="good")
    L = [f"# KHG as test sites for the groundwater model, by their SiTMAT stations", "",
         f"`python scripts/rank_station_sites.py --out {a.out}`. {len(per)} stations inside {per.khg_name.nunique()} KHG; good stations: "
         f"concession with at least {a.min_days_concession} unflagged days, community with at least {a.min_days_community} "
         f"(community records start later). Dry window {a.dry}. Full table: `{Path(a.out).with_suffix('.csv').name}`. "
         "LiDAR and sub-KHG units are known only for KHG with a hub site folder or a work folder ('?' otherwise).", "",
         f"## Top {a.top} by number of good stations", "",
         "| " + " | ".join(top.columns) + " |", "|" + "---|" * len(top.columns)]
    L += ["| " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else str(v) for v in r) + " |" for r in top.itertuples(index=False)]
    both = t[(t["good concession"] >= 5) & (t["good community"] >= 3)]
    L += ["", f"KHG with at least 5 good concession and 3 good community stations: {len(both)}"
          + (": " + ", ".join(f"{r.KHG} ({r.code})" for r in both.itertuples()) if len(both) else "") + ".", ""]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
