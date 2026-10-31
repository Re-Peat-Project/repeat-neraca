"""Candidate supply rules for the supply cap (D22), from the model's own rain and ET, compared with the station-based deficit.

  python scripts/supply_rule.py --khg 15.05-07-10.01 14.02-04-05.01 16.02.01 --start 2025-11-01 --end 2026-10-01 --out docs/reports/supply_rule.md

Reads `03_neraca/inputs/model/balance_chirps_dekad.csv` (rain) and `balance_<--et>_dekad.csv` (ET, mm per dekad, KHG mean) and, where it exists,
`03_neraca/runs/deficit/neraca_khg.csv` (the station-based deficit, repeat-neraca-run). Per KHG:
  window   climatic shortfall sum(E - P), floored at 0, over the station deficit's own period (June to October); the same window as the station figure
  trough   the largest rise of the cumulative (E - P) from any earlier dekad to a later one inside [--start, --end]: the dry-season shortfall with no
           window chosen by hand and no station needed, so it runs for any KHG that has the two forcing files
  dry      the dry window from the KHG's own record: the 14 consecutive dekads (circular over the year, 14 = the length of the station windows) with the largest
           mean sum(E - P) over the complete years 2018-2025 of `03_neraca/inputs/balance_{chirps,mod16}_dekad.csv` (pixel-weighted KHG mean of the sub-KHG units,
           gap-filled MOD16); the cap is sum(E - P) of the target year over that window, floored at 0
  station  deficit_mm of the station-based file (net shortfall minus the storage released by the observed fall of the water table)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from repeat_common import khg as K
from repeat_neraca.supply_rule import dekad_index, dry_window, history, window_days


def forcing(kf: Path, et: str):
    d = kf / "03_neraca" / "inputs" / "model"
    p = pd.read_csv(d / "balance_chirps_dekad.csv", parse_dates=["start", "end"])
    e = pd.read_csv(d / f"balance_{et}_dekad.csv", parse_dates=["start", "end"])
    m = p.merge(e, on="start", suffixes=("_p", "_e")).sort_values("start")
    return pd.DataFrame({"start": m.start, "end": m.end_p, "p": m.mm_p, "e": m.mm_e})


def trough(short: np.ndarray):
    """Largest rise of the cumulative shortfall: max over i<=j of c[j] - c[i-1] (c = cumsum), and its dekad range."""
    c = np.concatenate([[0.0], np.cumsum(short)])
    best, bi, bj, lo, lo_i = 0.0, 0, 0, c[0], 0
    for j in range(1, len(c)):
        if c[j] - lo > best:
            best, bi, bj = c[j] - lo, lo_i, j - 1
        if c[j] < lo:
            lo, lo_i = c[j], j
    return best, bi, bj


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", nargs="+", required=True)
    ap.add_argument("--start", default="2025-11-01")
    ap.add_argument("--end", default="2026-10-01")
    ap.add_argument("--et", default="mod16nrt")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for code in a.khg:
        kf = Path(K.folder(code))
        f = forcing(kf, a.et)
        s = f[(f.start >= a.start) & (f.end <= pd.Timestamp(a.end) + pd.Timedelta(days=1))].reset_index(drop=True)
        short = (s.e - s.p).to_numpy()
        t, i, j = trough(short)
        row = {"khg": kf.name, "dekads": len(s), "rain_mm": s.p.sum(), "et_mm": s.e.sum(), "trough_mm": t,
               "trough_from": s.start[i].date() if t > 0 else None, "trough_to": s.end[j].date() if t > 0 else None}
        h = history(kf)
        w0, wmean = dry_window(h)
        yr = s
        inw = yr[window_days(yr.start, w0)]
        row.update({"dry_window": f"dekad {w0 + 1} of 36 + 14", "dry_clim_mm": wmean, "dry_year_mm": max(0.0, (inw.e - inw.p).sum()), "dry_dekads_in_year": len(inw)})
        dfile = kf / "03_neraca" / "runs" / "deficit" / "neraca_khg.csv"
        if dfile.exists():
            dk = pd.read_csv(dfile).iloc[0]
            w = f[(f.start >= dk.period_start) & (f.end <= pd.Timestamp(dk.period_end) + pd.Timedelta(days=10))]
            row.update({"window": f"{dk.period_start} to {dk.period_end}", "window_mm": max(0.0, (w.e - w.p).sum()), "station_mm": dk.deficit_mm,
                        "station_net_balance_mm (ERA5)": -dk.net_balance_mm, "stations": int(dk.n_stations)})
        rows.append(row)
    t = pd.DataFrame(rows)
    L = [f"# Supply rule candidates, {a.start} to {a.end}", "",
         f"Written by `scripts/supply_rule.py` from the model's rain (CHIRPS) and ET ({a.et}), KHG mean, mm per dekad. `trough` is the largest rise of the cumulative (ET - rain) "
         "inside the period; `window` is sum(ET - rain), floored at 0, over the period of the station deficit; `station` is the station-based deficit.", "",
         t.round(1).to_markdown(index=False), ""]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(t.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
