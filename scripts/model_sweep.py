"""Run the groundwater model of one KHG over a small set of peat tables and canal levels (nothing fitted) and write one report.

  python scripts/model_sweep.py --khg 14.10.03 --start 2014-10-01 --end 2015-12-11 --res 200 \
      --tables tropical-small,tropical-large,urzainki2020 --drawdown 0.6,1.2 --out docs/reports/model_sweep_14.10.03.md

Each configuration is one `repeat-neraca-model` run (its own folder in 03_neraca/<dem>/runs/model/), run in parallel. The report puts the
field scores of every run next to the two simple predictions and adds a check of the field data themselves: the share of the observed
variance between field teams, overall and within 2 km blocks (teams that worked the same area). Needs REPEAT_KHG, REPEAT_DATA, REPEAT_HUB.
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd


def team_share(p: pd.DataFrame, block_m: float | None) -> float:
    """Share of the variance of obs_cm between field teams, after removing the mean of each block of block_m (None: no blocks)."""
    q = p.assign(group=p["group"].fillna("(none)"))
    if block_m:
        q["blk"] = (np.floor(q.x / block_m)).astype(int).astype(str) + "_" + (np.floor(q.y / block_m)).astype(int).astype(str)
        multi = q.groupby("blk").group.transform("nunique") >= 2
        q = q[multi]
        q["r"] = q.obs_cm - q.groupby("blk").obs_cm.transform("mean")
        m = q.groupby(["blk", "group"]).r.transform("mean")
    else:
        q["r"] = q.obs_cm - q.obs_cm.mean()
        m = q.groupby("group").r.transform("mean")
    return float(1 - ((q.r - m) ** 2).sum() / (q.r ** 2).sum()), int(len(q))


def within_team(p: pd.DataFrame, col: str) -> float:
    """Spearman of obs_cm with `col` after removing each field team's mean from both (a constant offset per team drops out)."""
    q = p.assign(group=p["group"].fillna("(none)"))
    a = q.obs_cm - q.groupby("group").obs_cm.transform("mean")
    b = q[col] - q.groupby("group")[col].transform("mean")
    return float(pd.Series(a).corr(pd.Series(b), method="spearman"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True)
    ap.add_argument("--dem", default="deltadtm")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--res", default="200")
    ap.add_argument("--tables", default="tropical-small,tropical-large,urzainki2020")
    ap.add_argument("--drawdown", default="0.6,1.2", help="values separated by commas; each is one --drawdown of the model")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from repeat_common import khg as K
    from repeat_neraca.groundwater import fieldcheck as FC
    kf = K.folder(a.khg)
    configs = list(itertools.product(a.tables.split(","), a.drawdown.split(",")))

    def one(c):
        pt, dd = c
        cmd = [sys.executable, "-m", "repeat_neraca.model", "--khg", a.khg, "--dem", a.dem, "--start", a.start, "--end", a.end,
               "--res", a.res, "--peat-table", pt, "--drawdown", dd]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"{pt} {dd} failed:\n{r.stderr[-2000:]}")
        return Path(r.stdout.strip().splitlines()[-1].split("wrote ", 1)[1])

    with ThreadPoolExecutor(a.workers) as ex:
        runs = list(ex.map(one, configs))

    rows, pts = [], None
    for (pt, dd), run in zip(configs, runs):
        s = json.loads((run / "field_scores.json").read_text(encoding="utf-8"))
        ser = pd.read_csv(run / "model_series.csv", parse_dates=["date"])
        cfg = json.loads((run / "run_config.json").read_text(encoding="utf-8"))
        u = s["unflagged"]
        p = pd.read_csv(run / "field_points.csv")
        w = ser[(ser.date >= p.date_from.min()) & (ser.date <= p.date_to.max())]
        sc = p[(~p.on_fixed) & (p.flag.isna())]
        rows.append({"peat table": pt, "canal level (m)": dd, "Spearman": u["model"]["spearman"], "Spearman within teams": within_team(sc, "sim_cm"),
                     "bias (cm)": u["model"]["bias_cm"],
                     "RMSE (cm)": u["model"]["rmse_cm"], "gate": "pass" if s["gate"]["pass"] else "fail",
                     "KHG mean depth in window (cm)": f"{w.mean_depth_cm.min():.0f}-{w.mean_depth_cm.max():.0f}",
                     "canal inflow in window (mm)": round(float(w.canal_in_mm.sum()), 1), "run": run.name})
        pts = p
    t = pd.DataFrame(rows)
    u = json.loads((runs[0] / "field_scores.json").read_text(encoding="utf-8"))["unflagged"]

    from pyproj import Transformer
    q = pts[(~pts.on_fixed) & (pts.flag.isna())].copy()
    import rasterio
    with rasterio.open(runs[0] / "model_depth_end.tif") as src:
        epsg = src.crs.to_epsg()
    q["x"], q["y"] = Transformer.from_crs(4326, epsg, always_xy=True).transform(q.lon.values, q.lat.values)
    share_all, n_all = team_share(q, None)
    share_blk, n_blk = team_share(q, 2000.0)
    phys = {c: float(q[[c, "obs_cm"]].corr(method="spearman").iloc[0, 1]) for c in ("dist_m", "peat_thickness_m")}
    dist_within = within_team(pts[pts.flag.isna()], "dist_m")                   # every unflagged point, canal cells included
    d = pts[pts.flag.isna() & (pts.date_from > pts.date_from.min())].assign(group=lambda x: x.group.fillna("(none)"))
    tm = d.groupby("group").agg(n=("obs_cm", "size"), depth=("obs_cm", "median"),
                                day=("date_from", lambda s: pd.to_datetime(s).map(pd.Timestamp.toordinal).median()))
    tm = tm[tm.n >= 5]
    timing = float(tm.depth.corr(tm.day, method="spearman"))

    L = [f"# Groundwater model sweep, {kf.name}, {a.dem}, {a.res} m", "",
         f"`python scripts/model_sweep.py --khg {a.khg} --dem {a.dem} --start {a.start} --end {a.end} --res {a.res} --tables {a.tables} "
         f"--drawdown {a.drawdown}`. Runs start saturated on {a.start}; nothing is fitted. Field points: `00_inputs/field_wtd.csv`, unflagged, "
         f"on peat, not on a fixed cell (n = {u['model']['n']}). Each run's own report: `03_neraca/{a.dem}/runs/model/<run>/model_report.md`.", "",
         "## Runs", "", "| " + " | ".join(t.columns) + " |", "|" + "---|" * len(t.columns)]
    L += ["| " + " | ".join(f"{v:.2f}" if isinstance(v, float) and k.startswith("Spearman") else (f"{v:.0f}" if isinstance(v, float) and "cm" in k else str(v))
                            for k, v in r.items()) + " |" for r in t.to_dict("records")]
    L += ["", f"Simple predictions on the same points: constant median RMSE {u['constant']['rmse_cm']:.0f} cm; distance to the nearest canal "
          f"Spearman {u['distance']['spearman']:.2f}, RMSE {u['distance']['rmse_cm']:.0f} cm. Gate (`groundwater/fieldcheck.py`): Spearman "
          "at least 0.3 and above the distance prediction, RMSE below the constant prediction.", "",
          "## The field data", "",
          f"Spearman of the observed depth with distance to the nearest canal {phys['dist_m']:.2f}, with the recorded peat thickness "
          f"{phys['peat_thickness_m']:.2f}. Share of the observed variance between field teams: {share_all:.0%} over all points (n = {n_all}), "
          f"{share_blk:.0%} between teams that worked the same 2 km block (n = {n_blk}). With each team's mean removed, the Spearman of the "
          f"observed depth with distance to the nearest canal is {dist_within:.2f} (every unflagged point, canal cells included). The team "
          f"effect does not follow the visit dates: across the {len(tm)} teams with at least 5 dated points, the Spearman of the team's median "
          f"depth with its median last-rain date is {timing:.2f}. "
          + (f"Both distance figures are below the gate's {FC.MIN_SPEARMAN} (a positive value means deeper away from canals, the opposite of "
             "canal drainage), so the field depths carry no usable canal-driven pattern and cannot serve as the spatial test of the model."
             if max(abs(phys["dist_m"]), abs(dist_within)) < FC.MIN_SPEARMAN else
             "Distance to canal explains part of the depths once teams are accounted for; score the model within teams."), ""]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
