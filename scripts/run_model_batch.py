#!/usr/bin/env python3
"""Run the groundwater model (repeat-neraca-model) over a list of KHG with one set-up; resumable.

  python scripts/run_model_batch.py --dem deltadtm [--khg 14.03.02 ...] [--workers 2] [--run d22_climate_2026] [--dry-run]

Set-up: the recommended one of the groundwater report (D21 with the canal classes of D24): canals inside cells, managed land held at
0.4 m with the supply capped at the KHG's own climatic shortfall (`--supply-cap climate`, D22), stations screened, tropical-large peat set, ET from mod16nrt, depth fallback bbsdlp, forcing fetched from Earth Engine.
Grid: 100 m for KHG up to 250,000 ha (registry area), 200 m above. Window 2025-11-01 to 2026-10-01 (report 6.14).
Without --khg, every KHG folder in $REPEAT_KHG is run. A KHG whose run folder already holds model_report.md is skipped
(--force reruns). Logs: <KHG folder>/logs/model_<dem>_<run>.log. Summary: $REPEAT_KHG/model_batch_<dem>_<run>.csv.
Output: <KHG folder>/03_neraca/<dem>/runs/model/<run>/. A KHG without field stations runs, and its station gates are not testable.
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import repeat_common.khg as K

ROOT = Path(os.environ["REPEAT_KHG"]) if os.environ.get("REPEAT_KHG") else Path(K.WORKSPACE if hasattr(K, "WORKSPACE") else ".")
AREA_100M_MAX = 250_000
SETUP = ["--peat-table", "tropical-large", "--drawdown", "primary=0.8,secondary=0.32,tertiary=0.24", "--managed-target", "0.4",
         "--peat-base", "--depth-fallback", "bbsdlp", "--et", "mod16nrt", "--canal-cells", "leak", "--screen-stations", "--supply-cap", "climate", "--fetch"]


def exe():
    p = Path(sys.executable).parent / "repeat-neraca-model.exe"
    return [str(p)] if p.exists() else [shutil.which("repeat-neraca-model") or "repeat-neraca-model"]


def area_ha(code: str):
    for r in K.registry():
        if r["khg_code"] == "KHG." + code:
            return float(r["area_ha_kepmen"])
    return None


def one(job):
    folder, code, dem, run, start, end, force = job
    out = folder / "03_neraca" / dem / "runs" / "model" / run
    if (out / "model_report.md").exists() and not force:
        return folder.name, "", "skipped (done)", 0.0
    a = area_ha(code)
    res = 100 if a is not None and a <= AREA_100M_MAX else 200
    log = folder / "logs" / f"model_{dem}_{run}.log"
    log.parent.mkdir(exist_ok=True)
    cmd = [*exe(), "--khg", code, "--dem", dem, "--start", start, "--end", end, "--res", str(res), "--run", run, *SETUP]
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as f:
        f.write(" ".join(cmd) + "\n")
        f.flush()
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONIOENCODING": "utf-8"}).returncode
    ok = rc == 0 and (out / "model_report.md").exists()
    return folder.name, res, "done" if ok else f"failed (exit {rc}, see {log.name})", (time.time() - t0) / 60


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dem", default="deltadtm", choices=["lidar", "deltadtm", "demnas"])
    ap.add_argument("--khg", nargs="*")
    ap.add_argument("--start", default="2025-11-01")
    ap.add_argument("--end", default="2026-10-01")
    ap.add_argument("--run", default="d22_climate_2026")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    folders = sorted(d for d in ROOT.iterdir() if d.is_dir() and d.name[:1].isdigit())
    if a.khg:
        folders = [d for d in folders if any(d.name.startswith(c.replace("KHG.", "") + "_") for c in a.khg)]
    jobs = []
    for d in folders:
        code = d.name.split("_", 1)[0]
        jobs.append((d, code, a.dem, a.run, a.start, a.end, a.force))
        print(f"{d.name:45s} {'100' if (area_ha(code) or 1e9) <= AREA_100M_MAX else '200'} m  {area_ha(code)} ha")
    if a.dry_run:
        return
    rows = []
    with ThreadPoolExecutor(a.workers) as ex:
        for name, res, status, mins in ex.map(one, jobs):
            print(f"{name:45s} {status} {mins:.1f} min", flush=True)
            rows.append([name, res, status, round(mins, 1)])
    with open(ROOT / f"model_batch_{a.dem}_{a.run}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["khg_folder", "res_m", "status", "minutes"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
