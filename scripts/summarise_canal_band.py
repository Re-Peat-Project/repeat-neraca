"""Compare groundwater model runs that differ only in the canal levels: how much the unmeasured canal level moves the open land.

  python scripts/summarise_canal_band.py --khg 15.05-07-10.01 --dem lidar --runs band_canal_shallow imp_a_baseline_screened band_canal_deep \
      --labels "shallow (0.5/0.15)" "middle (0.8/0.3)" "deep (1.2/0.6)" --out docs/reports/canal_band_15.05-07-10.01.md

Run folders are read from `$REPEAT_KHG/<khg folder>/03_neraca/<dem>/runs/model/`. Per run, from `model_units.csv` (season, area-weighted over the
sub-KHG) and `station_scores.json`: open land mean depth and days deeper than 40 cm, supply to managed land, and the station scores on the
stations outside held land. Then per sub-KHG, the open-land season mean depth in each run and its range.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from repeat_common import khg as K


def wavg(v, w):
    ok = v.notna() & w.notna() & (w > 0)
    return float(np.average(v[ok], weights=w[ok])) if ok.any() else np.nan


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True)
    ap.add_argument("--dem", default="lidar")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    labels = a.labels or a.runs
    base = Path(K.folder(a.khg)) / "03_neraca" / a.dem / "runs" / "model"
    rows, units = [], {}
    for lab, run in zip(labels, a.runs):
        u = pd.read_csv(base / run / "model_units.csv")
        sc = json.loads((base / run / "station_scores.json").read_text())["unflagged"]
        units[lab] = u.set_index("unit_id").open_mean_depth_cm
        rows.append({"run": lab, "open land mean depth (cm)": wavg(u.open_mean_depth_cm, u.open_km2),
                     "open land days deeper than 40 cm": wavg(u.open_days_deeper_40cm, u.open_km2),
                     "supply to managed land (mm)": wavg(u.managed_supply_mm, u.managed_km2),
                     "stations (n)": sc["model"]["n"], "Spearman": sc["model"]["spearman"], "bias (cm)": sc["model"]["bias_cm"],
                     "RMSE (cm)": sc["model"]["rmse_cm"], "RMSE constant (cm)": sc["constant"]["rmse_cm"]})
    t = pd.DataFrame(rows)
    U = pd.DataFrame(units)
    U["range (cm)"] = U.max(axis=1) - U.min(axis=1)
    L = [f"# Canal levels band, {a.khg}, {a.dem}", "",
         f"Written by `scripts/summarise_canal_band.py`. Runs: {', '.join(a.runs)}. Season mean over the sub-KHG, area-weighted; stations outside held managed land.", "",
         t.round(2).to_markdown(index=False), "",
         f"Open-land season mean depth (cm) per sub-KHG; the range over the band is {U['range (cm)'].median():.1f} cm at the median sub-KHG, "
         f"{U['range (cm)'].max():.1f} cm at most.", "", U.round(1).to_markdown()]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
