"""One table over groundwater model runs scored against stations, for the report.

  python scripts/summarise_model_runs.py --runs "$REPEAT_KHG/*/03_neraca/*/runs/model/*" --out docs/reports/model_station_runs.md

Reads each run folder's `run_config.json` and `station_scores.json` (runs without stations are skipped).
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def gate(g: dict, n_unflagged: int, supply: dict | None = None) -> str:
    """pass / fail / not testable. Rescored from the stored numbers, so runs made before a rule changed follow the current rules:
    checks without stations to use are not testable (the canal-depth check of canal-store runs needs none), and the supply check is
    `fieldcheck.supply_ok` (ratio or absolute floor)."""
    from repeat_neraca.groundwater import fieldcheck as FC
    spatial = ("spearman", "rmse")          # the checks on levels need 8 stations; the dynamics and supply checks are made with fewer
    checks = {k: (None if n_unflagged < 8 and k.startswith(spatial) else v) for k, v in g["checks"].items()}
    if n_unflagged == 0:
        checks = {k: (None if "supply" not in k and "canal depth" not in k else v) for k, v in checks.items()}
    if supply and "model_managed_supply_mm" in supply:
        checks = {k: v for k, v in checks.items() if "supply" not in k}
        checks["supply"] = FC.supply_ok(supply["model_managed_supply_mm"], supply["station_deficit_mm"])
    made = [v for v in checks.values() if v is not None]
    return "not testable" if not made else ("pass" if all(made) else "fail")


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
        mt = c.get("managed_target") or ""
        extra = "; ".join(x for x in ([f"peat base"] if c.get("peat_base") else []) + ([f"depth {c['depth_fallback']}"] if c.get("depth_fallback", "none") != "none" else [])
                         + (["canals inside cells"] if c.get("canal_cells") == "leak" else [])
                         + ([f"canal store, tau {c['canal_store']['tau_days']:g} d"] if c.get("canal_store") else []))
        supply = f"{sup['model_managed_supply_mm']:.0f}" if sup and "model_managed_supply_mm" in sup else ""
        rows.append([c["khg"], f"{c['res_m']:g} m", c["peat_table"], canal, mt, extra, c.get("et_stress") and "yes" or "no",
                     f"{dyn['n_unflagged']} of {dyn['n_stations']}",
                     f"{u['model'].get('spearman', float('nan')):.2f}", f"{u['distance'].get('spearman', float('nan')):.2f}",
                     f"{u['model'].get('bias_cm', float('nan')):.0f}", f"{u['model'].get('rmse_cm', float('nan')):.0f}",
                     f"{u['constant'].get('rmse_cm', float('nan')):.0f}", f"{dyn['median_station_r']:.2f}",
                     f"{dyn['obs_drawdown_median_cm']:.0f} / {dyn['sim_drawdown_median_cm']:.0f}",
                     f"{sup.get('station_deficit_mm', float('nan')):.0f} / {sup.get('model_canal_in_mm', float('nan')):.0f}" if sup else "", supply,
                     "; ".join(f"{k} {v['n']}: {v['obs_level_cm']:.0f}/{v['sim_level_cm']:.0f} cm" for k, v in kinds.items()),
                     gate(s["gate"], dyn.get("n_unflagged", dyn["n_stations"]), sup), d.name])
    head = ["KHG", "grid", "peat table", "canal level p/s/t (m)", "managed target", "options", "ET falls with depth", "stations scored", "Spearman model",
            "Spearman distance", "bias (cm)", "RMSE (cm)", "RMSE constant (cm)", "median station r", "drawdown obs / sim (cm)",
            "deficit / canal inflow (mm)", "managed supply (mm)", "level obs/sim by kind", "gate", "run"]
    L = ["# Groundwater model runs scored against SiTMAT stations", "", f"`python scripts/summarise_model_runs.py --runs \"{a.runs}\"`. "
         "Levels: each unflagged station's mean over its days. Dynamics on the unflagged stations (not on a canal or edge cell). Deficit: "
         "the station-based KHG deficit over June to early October 2026; canal inflow: water the model's canals put into the peat over the "
         "same days (negative: drainage). Managed target: the water table held in plantation licences (m, or `stations-loo`); managed "
         "supply: the water management supplies to hold it, mm over the managed land, over the deficit's days. In runs with a managed target, "
         "stations in managed land are left out of the level and dynamics scores (their level is imposed).", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    L += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
