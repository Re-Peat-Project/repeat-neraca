"""Climatic water balance for many KHG in one command: Earth Engine fetch, then `balance`, per KHG.

  python -m repeat_neraca.batch --selected                    # the KHG of re-peat/sites/selected_khg.csv
  python -m repeat_neraca.batch --khg 16.02.01 14.10.01       # codes or names from re-peat/sites/khg_registry.csv
  python -m repeat_neraca.batch --all                         # every KHG in the registry

Per KHG (work folder from `repeat_common.khg.folder`, created if missing):
  - with `02_delineation/subkhg_units.gpkg`: per sub-KHG, inputs in `03_neraca/inputs/`, results in `03_neraca/runs/balance/`;
  - without: the whole KHG as one unit (`fetch_gee_balance --whole-khg`), inputs in `inputs/khg_level/`, results in
    `runs/balance_khg_level/` (a calendar and KHG indicators, no ranking between sub-KHG).
Fetches are cached per year in the KHG's `cache/`, so a rerun or an interrupted batch only fetches what is missing. A KHG that
fails (e.g. not in the boundary file) is reported and the batch goes on. Summary: `<_khg>/neraca_balance_summary.csv` (one row per KHG; a run replaces the rows of its own KHG only).
Runs in the workspace .venv (earthengine-api, repeat-common, repeat-neraca); needs EE_PROJECT and REPEAT_KHG.
"""
from __future__ import annotations

import argparse
import csv
import traceback
from pathlib import Path

import pandas as pd

from . import balance as BAL
from .params import Registry


def khg_list(a) -> list[str]:
    from repeat_common import khg as K
    if a.all:
        return [r["khg_code"] for r in K.registry()]
    if a.selected:
        hub = Path(K.REGISTRY).parent
        rows = list(csv.DictReader(open(hub / "selected_khg.csv", encoding="utf-8")))
        return [r["khg_name_in_gpkg"] for r in rows if r["match_status"].startswith("confirmed") and r["khg_name_in_gpkg"]]
    return a.khg


def run_one(khg: str, a, reg: Registry) -> dict:
    from repeat_common import fetch_gee_balance as F, khg as K
    r = K.lookup(khg)
    kf = K.folder(khg, create=True)
    whole = not (kf / "02_delineation" / "subkhg_units.gpkg").exists()
    args = ["--khg", r["khg_code"], "--products", ",".join([a.rain, *a.et]), "--start", a.start, "--end", a.end, "--workers", str(a.workers)]
    F.main(args + (["--whole-khg"] if whole else []))
    inputs = kf / "03_neraca" / "inputs" / ("khg_level" if whole else "")
    out = kf / "03_neraca" / "runs" / ("balance_khg_level" if whole else "balance")
    res = BAL.run(inputs, out, a.rain, a.et, reg)
    t = pd.read_csv(out / "neraca_balance_unit.csv")
    return {"khg_code": r["khg_code"], "name": r["name"], "units": "khg" if whole else "sub-KHG", "n_units": len(t),
            "years": f"{res['years'][0]}-{res['years'][-1]}", "u_wb_mean_khg": round(float(t["u_wb_mean"].mean()), 1),
            "u_deficit_months_khg": round(float(t["u_deficit_months"].mean()), 2), "median_year_rho": round(res["median_year_rho"], 2),
            "balance_stable_ok": res["stable_ok"], "status": "ok", "folder": str(out)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--khg", nargs="+")
    g.add_argument("--selected", action="store_true")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--rain", default="chirps")
    ap.add_argument("--et", default="mod16,wapor")
    ap.add_argument("--start", default="2018-01-01")
    ap.add_argument("--end", required=True, help="exclusive; the first day after the last complete dekad of every product used")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    a.et = [s for s in a.et.split(",") if s]
    from repeat_common import khg as K
    reg = Registry.load()
    summary = K.root() / "neraca_balance_summary.csv"
    done = [K.lookup(k)["khg_code"] if not k.startswith("KHG.") else k for k in khg_list(a)]
    old = pd.read_csv(summary) if summary.exists() else pd.DataFrame(columns=["khg_code"])
    def code(k):
        try:
            return K.lookup(k)["khg_code"]
        except KeyError:
            return k
    old = old[~old["khg_code"].map(code).isin(done)]            # rows of other KHG are kept
    rows = []
    for khg in khg_list(a):
        print(f"=== {khg}", flush=True)
        try:
            rows.append(run_one(khg, a, reg))
        except (Exception, SystemExit) as e:          # fetch_gee_balance stops with SystemExit on a missing boundary
            traceback.print_exc()
            rows.append({"khg_code": K.lookup(khg)["khg_code"], "name": khg, "status": f"failed: {e}"})
        pd.concat([old, pd.DataFrame(rows)], ignore_index=True).to_csv(summary, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
