#!/usr/bin/env python3
"""Side by side: the neraca air calibration with ERA5, CHIRPS rain and WaPOR evaporation (written by scripts/forcing_test.sh).

  python -m repeat_neraca.bucket.forcing_compare --khg sugihan_lumpur --baseline data_local/out_neraca_sl --out docs/reports/sugihan_lumpur_forcing_test.md

Reads neraca_report.json of the baseline run (ERA5 rain and evaporation) and of every data_local/out_neraca_<khg>_<rain>_<evap>/ folder.
Every number is out-of-fold: the stations of the scored block were not used to fit the parameters. Compare RMSE with the baseline
column (every station follows the mean observed curve of the training stations); a model is useful only if it is below it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _row(label: str, report: Path) -> list[str] | None:
    if not report.exists():
        return None
    c = json.loads(report.read_text(encoding="utf-8"))["khg"][0]["calibration"]
    w, wo = c["with_drainage"], c["without_drainage"]
    v = c["verdict"]
    f = lambda x: "" if x is None else f"{x:.2f}"
    return [label, f"{c['period'][0]} to {c['period'][1]}", str(c["n_stations"]), f"{w['rmse_cm']:.1f}", f"{wo['rmse_cm']:.1f}", f"{wo['rmse_baseline_cm']:.1f}",
            f(w["temporal_r_median"]), f(wo["temporal_r_median"]), f(wo["spatial_spearman_peak"]), "kept" if c["drainage_kept"] else "dropped",
            "usable" if v["usable_for_ranking"] else "not usable"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True, help="config folder name, e.g. sugihan_lumpur")
    ap.add_argument("--baseline", required=True, help="output folder of the ERA5 run (neraca.yaml out)")
    ap.add_argument("--out", help="write the table here as markdown")
    a = ap.parse_args(argv)
    rows = [_row("ERA5 rain + ERA5 evaporation", Path(a.baseline) / "neraca_report.json")]
    for d in sorted(Path("data_local").glob(f"out_neraca_{a.khg}_*")):
        rain, evap = d.name.replace(f"out_neraca_{a.khg}_", "").split("_", 1)
        rows.append(_row(f"{rain} rain + {evap} evaporation", d / "neraca_report.json"))
    rows = [r for r in rows if r]
    head = ["forcing", "period scored", "stations", "RMSE with drainage (cm)", "RMSE without (cm)", "baseline RMSE (cm)",
            "temporal r with", "temporal r without", "spatial rho peak (without)", "drainage term", "verdict"]
    text = [f"# Forcing test: {a.khg}", "", "Out-of-fold, block cross-validation (see `repeat_neraca/bucket/README.md`). Periods differ where a source stops earlier (CHIRPS final data ends 2026-09-30).", "",
            "| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]
    out = "\n".join(text) + "\n"
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
