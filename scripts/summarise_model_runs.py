"""One table over groundwater model runs scored against stations, for the report.

  python scripts/summarise_model_runs.py --runs "$REPEAT_KHG/*/03_neraca/*/runs/model/*" --out docs/reports/model_station_runs.md

Reads each run folder's `run_config.json` and `station_scores.json` (runs without stations are skipped).
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="glob of run folders")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for d in sorted(glob.glob(a.runs)):
        d = Path(d)
        if not (d / "station_scores.json").exists() or not (d / "station_sim_daily.csv").exists():
            continue                                     # runs scored before 2026-10-28 counted stations on canal cells in the dynamics
        c = json.loads((d / "run_config.json").read_text(encoding="utf-8"))
        s = json.loads((d / "station_scores.json").read_text(encoding="utf-8"))
        u, dyn = s["unflagged"], s["dynamics"]
        dd = c["drawdown"]
        canal = "/".join("open" if v is None else f"{v:g}" for v in dd.values())
        if c.get("drawdown_managed"):
            canal += " (managed " + "/".join("open" if v is None else f"{v:g}" for v in c["drawdown_managed"].values()) + ")"
        sup = s.get("supply_check", {})
        kinds = s.get("by_kind", {})
        rows.append([c["khg"], f"{c['res_m']:g} m", c["peat_table"], canal, c.get("et_stress") and "yes" or "no",
                     f"{dyn['n_unflagged']} of {dyn['n_stations']}",
                     f"{u['model'].get('spearman', float('nan')):.2f}", f"{u['distance'].get('spearman', float('nan')):.2f}",
                     f"{u['model'].get('bias_cm', float('nan')):.0f}", f"{u['model'].get('rmse_cm', float('nan')):.0f}",
                     f"{u['constant'].get('rmse_cm', float('nan')):.0f}", f"{dyn['median_station_r']:.2f}",
                     f"{dyn['obs_drawdown_median_cm']:.0f} / {dyn['sim_drawdown_median_cm']:.0f}",
                     f"{sup.get('station_deficit_mm', float('nan')):.0f} / {sup.get('model_canal_in_mm', float('nan')):.0f}" if sup else "",
                     "; ".join(f"{k} {v['n']}: {v['obs_level_cm']:.0f}/{v['sim_level_cm']:.0f} cm" for k, v in kinds.items()),
                     "pass" if s["gate"]["pass"] else "fail", d.name])
    head = ["KHG", "grid", "peat table", "canal level p/s/t (m)", "ET falls with depth", "stations scored", "Spearman model",
            "Spearman distance", "bias (cm)", "RMSE (cm)", "RMSE constant (cm)", "median station r", "drawdown obs / sim (cm)",
            "deficit / canal inflow (mm)", "level obs/sim by kind", "gate", "run"]
    L = ["# Groundwater model runs scored against SiTMAT stations", "", f"`python scripts/summarise_model_runs.py --runs \"{a.runs}\"`. "
         "Levels: each unflagged station's mean over its days. Dynamics on the unflagged stations (not on a canal or edge cell). Deficit: "
         "the station-based KHG deficit over June to early October 2026; canal inflow: water the model's canals put into the peat over the "
         "same days (negative: drainage).", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    L += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
