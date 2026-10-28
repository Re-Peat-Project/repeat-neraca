"""Compare rewetting scenarios with a baseline run of the groundwater model, per sub-KHG.

  python scripts/compare_scenarios.py --baseline <run folder> --scenario <run folder> [<run folder> ...] --out docs/reports/scenarios_<khg>.md

Each folder is a `repeat-neraca-model` run of the same KHG, grid and season (`model_units.csv`, `model_season_days_deeper_40cm.tif`,
`model_series.csv`, `run_config.json`). Per sub-KHG: the change in the open land's days deeper than 40 cm and mean depth, and the water the
scenario supplies. Writes `days_deeper_40cm_change.tif` (scenario minus baseline, days) into each scenario folder. "Still needs rewetting":
open land deeper than 40 cm for more than half the season in more than half of the unit after the scenario (`open_share_deeper_40cm_half_season`
above 0.5). Open land is land not held by water management; land a scenario supplies is held, so it leaves the open land of that run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

STILL_DRY_SHARE = 0.5
BANDS_M = [(0, 150), (150, 350), (350, 1000), (1000, None)]


def by_distance(scen: Path, kf: Path, blocks_src: str) -> list[str]:
    """Change in days deeper than 40 cm by distance from the scenario's block reaches (block effects are local)."""
    import geopandas as gpd
    import rasterio
    from rasterio import features
    from scipy import ndimage
    path, _, layer = blocks_src.partition(", layer ")
    with rasterio.open(scen / "days_deeper_40cm_change.tif") as s:
        d, tr, crs = s.read(1), s.transform, s.crs
    g = gpd.read_file(kf / path, layer=layer or "sekat_reach").to_crs(crs)
    reach = features.rasterize([(x, 1) for x in g.geometry], out_shape=d.shape, transform=tr, fill=0, all_touched=True).astype(bool)
    dist = ndimage.distance_transform_edt(~reach) * abs(tr.a)
    L = ["| distance from a block reach | cells | mean change (days) | cells at least 10 days better |", "|---|---|---|---|"]
    for lo, hi in BANDS_M:
        m = (dist >= lo) & (dist < (hi or np.inf)) & np.isfinite(d)
        L.append(f"| {lo}–{hi} m | {int(m.sum())} | {np.nanmean(d[m]):.1f} | {np.mean(d[m] <= -10):.0%} |" if hi else
                 f"| beyond {lo} m | {int(m.sum())} | {np.nanmean(d[m]):.1f} | {np.mean(d[m] <= -10):.0%} |")
    return L


def season_supply(run: Path) -> float:
    s = pd.read_csv(run / "model_series.csv", parse_dates=["date"])
    c = json.loads((run / "run_config.json").read_text(encoding="utf-8"))
    end = pd.Timestamp(c["end"]) - pd.Timedelta(days=1)
    s0, s1 = (pd.Timestamp(f"{end.year}-{x}") for x in c.get("season", "06-01,09-30").split(","))
    d = s[(s.date >= s0) & (s.date <= s1)]
    return float(d.managed_supply_m3.sum()) if "managed_supply_m3" in d else float("nan")


def diff_map(base: Path, scen: Path) -> tuple[float, float]:
    import rasterio
    with rasterio.open(base / "model_season_days_deeper_40cm.tif") as a, rasterio.open(scen / "model_season_days_deeper_40cm.tif") as b:
        x, y = a.read(1, masked=True), b.read(1, masked=True)
        d = (y - x).filled(np.nan).astype("float32")
        prof = a.profile
    with rasterio.open(scen / "days_deeper_40cm_change.tif", "w", **{**prof, "nodata": np.nan}) as out:
        out.write(d, 1)
    return float(np.nanmean(d)), float(np.nanmean(d < -10))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--scenario", required=True, nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    base = Path(a.baseline)
    ub = pd.read_csv(base / "model_units.csv").set_index("unit_id")
    cb = json.loads((base / "run_config.json").read_text(encoding="utf-8"))
    L = [f"# Rewetting scenarios, {cb['khg']}", "", f"`python scripts/compare_scenarios.py --baseline {base.name} --scenario "
         + " ".join(Path(s).name for s in a.scenario) + "`. Baseline run: `" + base.name + "`. Season: days deeper than 40 cm out of "
         f"{int(ub.season_days.iloc[0])}. Open land: land not held by water management in that run. Still needs rewetting: more than "
         f"{STILL_DRY_SHARE:.0%} of the unit's open land deeper than 40 cm for more than half the season.", ""]
    rows = []
    for s in a.scenario:
        s = Path(s)
        us = pd.read_csv(s / "model_units.csv").set_index("unit_id")
        cs = json.loads((s / "run_config.json").read_text(encoding="utf-8"))
        mean_change, share_better = diff_map(base, s)
        t = pd.DataFrame({
            "open km2": us.open_km2.round(1),
            "days deeper 40 cm, baseline": ub.open_days_deeper_40cm.round(0),
            "days deeper 40 cm, scenario": us.open_days_deeper_40cm.round(0),
            "mean depth baseline / scenario (cm)": ub.open_mean_depth_cm.round(0).astype("Int64").astype(str) + " / "
                                                 + us.open_mean_depth_cm.round(0).astype("Int64").astype(str),
            "still needs rewetting": np.where(us.open_share_deeper_40cm_half_season > STILL_DRY_SHARE, "yes", ""),
            "supply mm, scenario": us.managed_supply_mm.round(0)})
        sup_b, sup_s = season_supply(base), season_supply(s)
        what = "; ".join(x for x in ([f"blocks: {cs['notes'].get('blocks')} ({cs['notes'].get('block_reaches')} reaches)"] if cs.get("blocks", "none") != "none" else [])
                         + ([f"water supply: {cs['notes'].get('supply')} ({cs['notes'].get('supply_share_of_khg', 0):.0%} of the KHG held at "
                             f"{cs['notes'].get('supply_target_m')} m)"] if cs.get("supply", "none") != "none" else []))
        L += [f"## {s.name}", "", f"{what}. Mean change in days deeper than 40 cm over cells open in both runs: {mean_change:.1f} days; share of those "
              f"cells with at least 10 days fewer: {share_better:.0%}. Water supplied in the season, all held land: baseline "
              f"{sup_b / 1e6:.1f} million m3, scenario {sup_s / 1e6:.1f} million m3. Units still needing rewetting: "
              f"{int((t['still needs rewetting'] == 'yes').sum())} of {len(t)} (baseline "
              f"{int((ub.open_share_deeper_40cm_half_season > STILL_DRY_SHARE).sum())}). Map: `{s.name}/days_deeper_40cm_change.tif`.", "",
              ]
        if cs.get("blocks", "none") != "none":
            kf = s.parents[5] / cs["khg"]
            L += ["By distance from the block reaches:", "", *by_distance(s, kf, cs["notes"]["blocks"]), ""]
        L += ["| unit | " + " | ".join(t.columns) + " |", "|" + "---|" * (len(t.columns) + 1)]
        L += [f"| {i} | " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else str(v) for v in r) + " |" for i, r in zip(t.index, t.itertuples(index=False))]
        L.append("")
        rows.append(s.name)
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
