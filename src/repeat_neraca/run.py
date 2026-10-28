#!/usr/bin/env python3
"""Physical neraca air of one KHG, with no fitted parameter, compared with the observed water tables.

  repeat-neraca-run --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 1
  repeat-neraca-run --config ../re-peat/sites/16.02.01_sugihan_lumpur/neraca.yaml --tier 2 --res 500
  repeat-neraca-run --config ../re-peat/sites/14.02-04-05.01_kampar_gaung/neraca.yaml --tier 1 --tier 2 --drawdown 0.5,0.8,1.2,1.6,2.0

Question answered: with Sy, transmissivity, drain spacing, rain and evaporation taken from the registry and the data, and a canal level a
given distance below the surface, how close is the simulated water table to what the SiTMAT stations record?

  --tier 1   one KHG-level curve (`repeat_neraca.lumped`), run for every --drawdown; compared with the mean observed curve
  --tier 2   the 2D groundwater solver (`repeat_neraca.spatial`) at --res metres, run for the first --drawdown only (about a minute per
             run at 500 m); compared with the stations and summarised per sub-KHG

Needs the files named in the config (see config/neraca/*.yaml) and the extras: pip install -e .[neraca].
Writes into --out (default _out/<name>): neraca_report.md, tier1_series.csv, tier2_series.csv, neraca_unit.csv, registry_snapshot.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from repeat_neraca import deficit as DEF                  # noqa: E402
from repeat_neraca import forcing_read as FR              # noqa: E402
from repeat_neraca import inputs as IN                    # noqa: E402
from repeat_neraca import lumped, spatial, validate as V  # noqa: E402
from repeat_neraca.params import Registry                        # noqa: E402
from repeat_neraca.groundwater import TROPICAL_SETS, PeatTable          # noqa: E402


def _fmt(d: dict, keys) -> str:
    return " | ".join(f"{d.get(k, float('nan')):.2f}" if isinstance(d.get(k), (int, float)) else str(d.get(k, "")) for k in keys)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--tier", type=int, action="append", choices=[1, 2], help="1 and/or 2 (default 1)")
    ap.add_argument("--drawdown", default=None, help="canal drawdown(s) in m, comma separated (default: the registry value)")
    ap.add_argument("--classes", default="primary,secondary", help="canal classes that hold the canal level")
    ap.add_argument("--k-multiplier", default="1", help="scale of the peat table transmissivity, comma separated for tier 1 (tier 2 uses the first); 1 = Urzainki 2020 table")
    ap.add_argument("--et-stress", choices=["none", "drained", "natural"], default="none",
                    help="evaporation falls when the water table is deep (PEATCLSM-Trop thresholds): drained = registry et_stress_start/end, natural = -0.70/-1.82 m")
    ap.add_argument("--res", type=float, default=None, help="grid resolution in m for tier 2 (default: registry neraca_grid_res_m)")
    ap.add_argument("--forcing", choices=["auto", "file", "direct"], default="auto",
                    help="rain and evaporation from forcing_daily.csv (file), read through repeat-common (direct), or direct when the config has a forcing_direct block (auto)")
    ap.add_argument("--peat-table", default="urzainki2020", choices=["urzainki2020", "tropical-small", "tropical-large"],
                    help="storage and transmissivity of the peat: the boreal-curve table of this repository (default) or the tropical exponential set of Urzainki et al. 2023 (small or large conductivity)")
    ap.add_argument("--registry", default=None, help="registry file (default: the registry in the package, repeat_neraca/parameters.yaml)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    tiers = a.tier or [1]
    reg = Registry.load(a.registry) if a.registry else Registry.load()
    cfg = IN.load_config(a.config)
    inputs_dir = (Path(cfg["_dir"]).parents[1] / cfg["inputs_dir"]) if not Path(cfg["inputs_dir"]).is_absolute() else Path(cfg["inputs_dir"])
    cfg["inputs_dir"] = str(inputs_dir)
    out = Path(a.out) if a.out else Path("_out") / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    classes = tuple(c for c in a.classes.split(",") if c)
    drawdowns = [float(x) for x in a.drawdown.split(",")] if a.drawdown else [reg["canal_drawdown"]]
    res = a.res or reg["neraca_grid_res_m"]
    kmults = [float(x) for x in a.k_multiplier.split(",")]

    f, forcing_route = FR.read_forcing(cfg, inputs_dir, a.forcing)
    print(f"forcing: {forcing_route}")
    dates = pd.DatetimeIndex(f["date"])
    rain_m = (f["P_era5_mm"] / 1000.0).values
    et_m = (f[cfg.get("evaporation", "E_era5_mm")] / 1000.0).values
    net_m = rain_m - et_m
    et_fn = None if a.et_stress == "none" else lumped.et_factor(*((-0.70, -1.82) if a.et_stress == "natural" else (reg["et_stress_start"], reg["et_stress_end"])))
    obs = V.observed_wide(inputs_dir, dates)
    khg = IN.load(cfg, res)
    dr = DEF.khg_deficit(f, obs, khg.area_km2, cfg.get("khg_id", cfg["name"]), cfg.get("deficit"))
    pd.DataFrame([dr], columns=DEF.COLUMNS).to_csv(out / "neraca_khg.csv", index=False, float_format="%.3f")
    print(f"deficit {dr['period_start']}..{dr['period_end']}: {dr['deficit_mm']:.0f} mm ({dr['deficit_mm_low']:.0f}-{dr['deficit_mm_high']:.0f}), "
          f"{dr['deficit_m3'] / 1e6:,.0f} million m3 -> neraca_khg.csv")
    table = PeatTable.named(a.peat_table)
    (out / "registry_snapshot.json").write_text(json.dumps(reg.snapshot(), indent=2), encoding="utf-8")

    L = [f"# Physical neraca air, {cfg['name']}", "",
         f"Forcing window `{cfg['forcing_window']}`: {dates[0].date()} to {dates[-1].date()}, {int(np.isfinite(net_m).sum())} days with forcing; mean P - E {np.nanmean(net_m) * 1000:.2f} mm/day "
         f"(evaporation column `{cfg.get('evaporation', 'E_era5_mm')}`; evaporation stress: {a.et_stress}). Registry snapshot {reg.snapshot()['sha256'][:12]}. No parameter is fitted." + (f" Peat table: {a.peat_table} ({TROPICAL_SETS[a.peat_table]['source']})." if a.peat_table != "urzainki2020" else ""), "",
         f"KHG {khg.area_km2:,.0f} km2 on a {res:.0f} m grid ({int(khg.domain.sum()):,} cells); DTM valid on {100 * khg.notes['dtm_valid_in_domain']:.0f}% of it, "
         f"peat depth on {100 * khg.notes['peat_depth_valid_in_domain']:.0f}% (gaps filled with the median, {khg.notes['peat_depth_median_m']:.1f} m). "
         f"Canal length inside the KHG (km): " + ", ".join(f"{k} {v:,.0f}" for k, v in khg.canal_length_km.items()) + ". "
         f"Canal classes holding the canal level: {', '.join(classes)}. Observed: {obs.shape[1]} stations.", ""]
    z0 = reg["initial_wtd"]
    if 1 in tiers:
        length = sum(khg.canal_length_km[c] for c in classes)
        spacing = lumped.drain_spacing_m(khg.area_km2, length)
        depth_m = float(np.median(khg.peat_depth[khg.domain]))
        sy_fn = lambda z: float(table.sy(np.array([z]))[0])
        L += [f"## Tier 1: KHG-level curve", "", f"Drain spacing L = {spacing:,.0f} m from the canal length of the chosen classes; median peat depth {depth_m:.1f} m; initial water table {z0:.2f} m.", "",
              "| transmissivity x | canal drawdown (m) | mean simulated depth (cm) | mean observed depth (cm) | bias (cm) | RMSE (cm) | RMSE after removing bias (cm) | r |", "|---|---|---|---|---|---|---|---|"]
        series = {"date": dates}
        for km in kmults:
          t_fn = lambda z, km=km: float(table.trans(np.array([z]), np.array([depth_m]), km)[0])
          for dd in drawdowns:
            z = lumped.simulate_rain_et(rain_m, et_m, sy_fn, t_fn, spacing, dd, z0, et_fn)
            sim_cm = -100.0 * z
            series[f"depth_cm_k{km:g}_dd{dd:g}"] = sim_cm
            m = V.khg_level(sim_cm, obs)
            if m:
                L.append(f"| {km:g} | {dd:g} | {m['sim_mean_cm']:.1f} | {m['obs_mean_cm']:.1f} | {m['bias_cm']:+.1f} | {m['rmse_cm']:.1f} | {m['rmse_after_removing_bias_cm']:.1f} | {m['r']:.2f} |")
        series["obs_mean_cm"] = obs.mean(axis=1).values
        pd.DataFrame(series).to_csv(out / "tier1_series.csv", index=False, float_format="%.2f")
        L.append("")
    if 2 in tiers:
        dd = drawdowns[0]
        print(f"tier 2: {int(khg.domain.sum()):,} cells, {len(dates)} days, drawdown {dd:g} m, transmissivity x{kmults[0]:g}", flush=True)
        r = spatial.run(khg, rain_m, et_m, table, dd, reg["river_stage_below_edge"], z0, classes, kmults[0], et_fn, log=print)
        mean_cm = -100.0 * r["mean"]
        m = V.khg_level(mean_cm, obs)
        L += ["## Tier 2: 2D groundwater", "", f"Canal drawdown {dd:g} m, transmissivity x{kmults[0]:g}; canal and edge cells fixed ({int(r['fixed'].sum()):,} of {int(khg.domain.sum()):,} cells, {100 * r['fixed'].sum() / khg.domain.sum():.0f}%).", "",
              "| scale | bias (cm) | RMSE (cm) | r | notes |", "|---|---|---|---|---|"]
        if m:
            L.append(f"| KHG mean of free cells | {m['bias_cm']:+.1f} | {m['rmse_cm']:.1f} | {m['r']:.2f} | simulated mean {m['sim_mean_cm']:.1f} cm, observed {m['obs_mean_cm']:.1f} cm |")
        sdf = pd.DataFrame({"date": dates, "mean_depth_cm": mean_cm, "share_deeper_than_0.4": r["share_deeper_than_0.4"]})
        sl = {}
        if khg.stations is not None and len(khg.stations):
            sl = V.station_level(-100.0 * r["stations"], obs, khg.stations.station_id)
            if sl:
                L.append(f"| stations (cell of each station) | {sl['pooled_bias_cm']:+.1f} | {sl['pooled_rmse_cm']:.1f} | | Spearman across stations: mean level {sl['spearman_mean_level']:.2f}, peak depth {sl['spearman_peak_depth']:.2f}; "
                         f"observed mean level {sl['obs_mean_level_cm']:.0f} cm, simulated {sl['sim_mean_level_cm']:.0f} cm; observed peak depth {sl['obs_peak_range_cm'][0]:.0f}-{sl['obs_peak_range_cm'][1]:.0f} cm |")
            for j, sid in enumerate(khg.stations.station_id):
                sdf[f"st_{sid}"] = -100.0 * r["stations"][:, j]
        sdf.to_csv(out / "tier2_series.csv", index=False, float_format="%.2f")
        if r["units"] is not None:
            u = -100.0 * r["units"]
            sc = slice(V.SKIP, None)
            units = pd.DataFrame({"unit_id": khg.unit_ids, "u_wt_mean_cm": np.nanmean(u[sc], axis=0), "u_wt_peak_cm": np.nanpercentile(u[sc], 95, axis=0),
                                  "u_wt_days_gt40": np.nanmean(np.where(np.isfinite(u[sc]), u[sc] > 40.0, np.nan), axis=0)})
            rho = sl.get("spearman_peak_depth", float("nan"))
            units["neraca_skill_ok"] = int(np.isfinite(rho) and rho >= V.MIN_SPATIAL_SKILL)
            units.to_csv(out / "neraca_unit.csv", index=False, float_format="%.3f")
            L += ["", f"Per sub-KHG (mean water table depth over the window): min {units.u_wt_mean_cm.min():.0f}, median {units.u_wt_mean_cm.median():.0f}, max {units.u_wt_mean_cm.max():.0f} cm "
                  f"({len(units)} sub-KHG; table in `neraca_unit.csv`)."]
        L.append("")
    text = "\n".join(L) + "\n"
    (out / "neraca_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
