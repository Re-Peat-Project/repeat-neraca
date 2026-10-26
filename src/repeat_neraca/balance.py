"""Climatic water balance per sub-KHG: the method of the 2021 Kahayan-Sebangau study on Earth Engine rain and evapotranspiration.

  python -m repeat_neraca.balance --inputs $REPEAT_KHG/<khg>/03_neraca/inputs --out $REPEAT_KHG/<khg>/03_neraca/runs/balance
  python -m repeat_neraca.balance --inputs ... --out ... --rain chirps --et wapor,mod16      # the first ET product is the central one

Monthly, per sub-KHG u:

    WB = P (1 - I_u) (1 - C) - ET        C = registry runoff_coefficient; I_u = sum over WorldCover classes of (share of u x interception_<class>)

Inputs (from `python -m repeat_common.fetch_gee_balance`): balance_<product>_dekad.csv (or _month.csv) per product and units_landcover.csv.
A month counts when all its dekads are fully covered for both P and ET; a year counts when all 12 months do. Indicators over
the complete years, defined as in repeat-prioritisation `common/indicators.py` so they can replace its columns through
`extra_indicators`:

    u_wb_mean          mean monthly WB, mm/month
    u_deficit_months   months with WB < 0, per year

Questions the report answers, as in the earlier `balance_compare` (docs/bucket_reports/*_balance_compare.md):
  1. how much the sub-KHG differ against how much the ET sources differ,
  2. whether the sources rank the sub-KHG alike (Spearman of u_wb_mean),
  3. whether the order is stable from year to year (Spearman of yearly mean WB between all pairs of years).
`balance_stable_ok` (docs/reports/balance_design.md for the evidence) is 1 when, across units,
  - the ET sources agree on the order of ET itself (Spearman of the unit means of ET; rain is left out because the sources share
    it, which made balances look consistent when the ET products were not), and
  - the yearly balance keeps its order (median Spearman over all pairs of complete years),
each above the 99th percentile of the same statistic for a random order of the same number of units (`null_quantiles`, p < 0.01).
With one ET source only the year test applies. Fewer than 5 units: left empty.

Writes into --out: neraca_balance_unit.csv, neraca_balance_monthly.csv, neraca_balance.md, registry_snapshot.json
(the parameter values used, with a hash).
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .params import Registry

NULL_Q = 0.99          # stability tests against a random order of units at p < 0.01
WC_INTERCEPTION = {10: "interception_tree", 95: "interception_mangrove", 20: "interception_shrub",
                   90: "interception_wetland", 30: "interception_grass", 40: "interception_crop"}


def interception(landcover: pd.DataFrame, reg: Registry) -> pd.Series:
    """Interception share per unit from the WorldCover class shares."""
    s = sum(landcover.get(f"wc_{c}", 0.0) * reg[k] for c, k in WC_INTERCEPTION.items())
    return pd.Series(np.asarray(s, dtype=float), index=landcover["unit_id"].astype(str))


def product_file(inputs: Path, product: str) -> Path:
    """balance_<product>_dekad.csv, or the monthly file when there is no dekadal one (TerraClimate)."""
    f = inputs / f"balance_{product}_dekad.csv"
    return f if f.exists() else inputs / f"balance_{product}_month.csv"


def monthly(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """(months x units) totals in mm, NaN where a month is not fully covered; and the mean valid pixel count per unit."""
    d = pd.read_csv(path, dtype={"unit_id": str}, parse_dates=["start"])
    d["month"] = d["start"].dt.to_period("M")
    full = d["time_cov"] >= 0.999
    d["mm"] = d["mm"].where(full)
    g = d.groupby(["month", "unit_id"])
    whole = g["days"].sum() == g["month"].first().map(lambda p: p.days_in_month)       # not cut by the fetch end date
    m = g["mm"].sum(min_count=1).where((g["mm"].count() == g["mm"].size()) & whole).unstack()
    return m, d.groupby("unit_id")["n_px"].mean()


def wb_monthly(P: pd.DataFrame, E: pd.DataFrame, icpt: pd.Series, c: float) -> pd.DataFrame:
    idx = P.index.intersection(E.index)
    cols = [u for u in P.columns if u in E.columns]
    i = icpt.reindex(cols).fillna(0.0).values
    return P.loc[idx, cols] * (1 - i)[None, :] * (1 - c) - E.loc[idx, cols]


def complete_years(wb: pd.DataFrame) -> list[int]:
    y = wb.index.year
    return [yr for yr in sorted(set(y)) if (y == yr).sum() == 12 and wb[y == yr].notna().all().all()]


def indicators(wb: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    w = wb[wb.index.year.isin(years)]
    yearly = w.groupby(w.index.year).mean()
    deficit = (w < 0).groupby(w.index.year).sum()
    return pd.DataFrame({"u_wb_mean": w.mean(), "u_deficit_months": deficit.mean(), "wb_year_sd_mm": yearly.std(ddof=0),
                         "n_years": len(years)})


def _rho(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return float("nan")
    return float(spearmanr(a[ok], b[ok]).correlation)


def null_quantiles(n: int, years: int = 8, draws: int = 10000, q: float = NULL_Q, seed: int = 0) -> tuple[float, float]:
    """q-quantiles, for n units in a random order, of one Spearman between two orders and of the median Spearman over all
    pairs of `years` yearly orders (simulation, fixed seed)."""
    rng = np.random.default_rng(seed)
    iu = np.triu_indices(years, 1)
    one, med = np.empty(draws), np.empty(draws)
    for i in range(draws):
        c = np.corrcoef(rng.random((years, n)).argsort(axis=1).argsort(axis=1).astype(float))[iu]
        one[i], med[i] = c[0], np.median(c)
    return float(np.quantile(one, q)), float(np.quantile(med, q))


def year_stability(wb: pd.DataFrame, years: list[int]) -> list[float]:
    yearly = wb[wb.index.year.isin(years)].groupby(lambda p: p.year).mean()
    return [_rho(yearly.loc[a], yearly.loc[b]) for a, b in combinations(years, 2)]


def run(inputs: Path, out: Path, rain: str, ets: list[str], reg: Registry, rain_mode: str = "khg") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    lc = pd.read_csv(inputs / "units_landcover.csv", dtype={"unit_id": str})
    icpt = interception(lc, reg)
    c = float(reg["runoff_coefficient"])
    P, npx_p = monthly(product_file(inputs, rain))
    Es = {}
    if rain_mode == "khg":           # one rain series for every unit: the area-weighted KHG mean of the month
        w = lc.set_index("unit_id")["area_km2"].reindex(P.columns)
        P = pd.DataFrame(np.repeat(((P * w).sum(axis=1, min_count=1) / P.notna().mul(w).sum(axis=1)).values[:, None], P.shape[1], axis=1),
                         index=P.index, columns=P.columns).where(P.notna().all(axis=1), axis=0)
    elif rain_mode != "unit":
        raise ValueError(f"rain_mode must be unit or khg (got {rain_mode})")
    wbs, npx, pme = {}, {}, {}
    for et in ets:
        E, npx[et] = monthly(product_file(inputs, et))
        Es[et] = E
        wbs[et] = wb_monthly(P, E, icpt, c)
        pme[et] = wb_monthly(P, E, icpt * 0, 0.0)
    # years complete for every source, so the sources are compared on the same months
    years = sorted(set.intersection(*[set(complete_years(w)) for w in wbs.values()]))
    if not years:
        raise SystemExit("no complete year common to the rain and evapotranspiration products")
    ind = {et: indicators(wbs[et], years) for et in ets}
    central = ets[0]
    stab = {et: year_stability(wbs[et], years) for et in ets}
    src_rho = {(a, b): _rho(ind[a]["u_wb_mean"], ind[b]["u_wb_mean"].reindex(ind[a].index)) for a, b in combinations(ets, 2)}
    med = float(np.nanmedian(stab[central])) if stab[central] else float("nan")
    et_mean = {et: Es[et][Es[et].index.year.isin(years)].mean() for et in ets}
    et_rho = {(a, b): _rho(et_mean[a], et_mean[b].reindex(et_mean[a].index)) for a, b in combinations(ets, 2)}
    n_units = len(ind[central])
    q_one, q_med = null_quantiles(n_units, len(years)) if n_units >= 5 and len(years) >= 2 else (np.nan, np.nan)
    ok = np.isfinite(med) and med >= q_med and all(np.isfinite(r) and r >= q_one for r in et_rho.values())

    t = ind[central].copy()
    w = wbs[central][wbs[central].index.year.isin(years)]
    t["p_minus_et_mean_mm"] = pme[central][pme[central].index.year.isin(years)].mean()
    t["interception_share"] = icpt.reindex(t.index).values
    t[f"n_px_{rain}"] = npx_p.reindex(t.index).values
    for et in ets:
        t[f"n_px_{et}"] = npx[et].reindex(t.index).values
        if et != central:
            t[f"wb_mean_{et}"] = ind[et]["u_wb_mean"]
            t[f"deficit_months_{et}"] = ind[et]["u_deficit_months"]
    t["balance_stable_ok"] = int(ok) if len(t) >= 5 else np.nan        # fewer than 5 units: no order to check
    t.index.name = "unit_id"
    t.reset_index().to_csv(out / "neraca_balance_unit.csv", index=False, float_format="%.3f")
    snap = reg.snapshot()
    (out / "registry_snapshot.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
    rows = []
    for et in ets:
        m = wbs[et].stack(future_stack=True).rename("WB_mm").reset_index()
        m.columns = ["month", "unit_id", "WB_mm"]
        m["et_source"] = et
        rows.append(m)
    mon = pd.concat(rows)
    mon["month"] = mon["month"].astype(str)
    mon.to_csv(out / "neraca_balance_monthly.csv", index=False, float_format="%.2f")

    khg = next((p.parent.name for p in [inputs, *inputs.parents] if p.name == "03_neraca"), inputs.name)   # _khg/<khg>/03_neraca/inputs[/..]
    L = [f"# Climatic water balance per sub-KHG, {khg}" + ("" if inputs.name == "inputs" else f" ({inputs.name})"), "",
         f"`WB = P (1 - I) (1 - C) - ET`, monthly; C = {c:g}, I from ESA WorldCover v200 shares and the registry interception values "
         f"(Bambang Kun Cahyono, taken as established; registry snapshot {snap['sha256'][:12]}). Rain: {rain}; evapotranspiration: {', '.join(ets)} (central: {central}). "
         f"Complete years common to all sources: {', '.join(map(str, years))}. {len(t)} sub-KHG. Method: `repeat_neraca/balance.py`.", "",
         "WaPOR AETI and MOD16 ET include evaporation of intercepted rain, so with them the interception term counts it a second time; "
         "`p_minus_et_mean_mm` in the unit table gives the balance without C and I.", "",
         "## 1. Sub-KHG against sources", "",
         "| ET source | KHG mean WB (mm/month) | sub-KHG min | median | max | std across sub-KHG | deficit months per year: min / max |",
         "|---|---|---|---|---|---|---|"]
    for et in ets:
        v, dm = ind[et]["u_wb_mean"], ind[et]["u_deficit_months"]
        L.append(f"| {et} | {v.mean():.1f} | {v.min():.1f} | {v.median():.1f} | {v.max():.1f} | {v.std(ddof=0):.2f} | {dm.min():.1f} / {dm.max():.1f} |")
    L += ["", "## 2. Do the sources rank the sub-KHG alike?", ""]
    L += (["| pair | Spearman of u_wb_mean |", "|---|---|"] + [f"| {a} vs {b} | {r:.2f} |" for (a, b), r in src_rho.items()]) if src_rho else ["One ET source only."]
    L += ["", "## 3. Is the order stable from year to year?", "",
          "| ET source | pairs of years | Spearman min | median |", "|---|---|---|---|"]
    for et in ets:
        s = stab[et]
        L.append(f"| {et} | {len(s)} | {np.nanmin(s) if s else float('nan'):.2f} | {np.nanmedian(s) if s else float('nan'):.2f} |")
    forest = (lc.set_index("unit_id").get("wc_10", 0) + lc.set_index("unit_id").get("wc_95", 0)).reindex(t.index)
    L += ["", (f"`balance_stable_ok` = {int(ok)}: ET order, " + "; ".join(f"{x} vs {y} {r:.2f}" for (x, y), r in et_rho.items())
                + f" (needs {q_one:.2f}); median year-to-year Spearman of {central} {med:.2f} (needs {q_med:.2f}); thresholds are the "
                f"99th percentiles for a random order of {n_units} units."
                + f" Spearman with the forest share (WorldCover tree cover + mangroves): u_wb_mean {_rho(t['u_wb_mean'], forest):.2f}, "
                f"P - ET {_rho(t['p_minus_et_mean_mm'], forest):.2f}; the interception term is fixed by land cover, so a large first value "
                "with a small second one means the order of units comes from land cover, not from water."
               if len(t) >= 5 else f"{len(t)} unit(s): no order between units to check, `balance_stable_ok` left empty."), "",
          "## 4. Calendar: KHG-mean WB by month (mm), central source", "",
          "| year | " + " | ".join(f"{m:02d}" for m in range(1, 13)) + " | deficit months |", "|---" * 14 + "|"]
    k = wbs[central].mean(axis=1)
    for y in sorted(set(k.index.year)):
        vals = [k.get(pd.Period(f"{y}-{m:02d}", "M"), np.nan) for m in range(1, 13)]
        L.append(f"| {y} | " + " | ".join("" if not np.isfinite(v) else f"{v:.0f}" for v in vals) + f" | {sum(v < 0 for v in vals if np.isfinite(v))} |")
    L += ["", "Pixels per sub-KHG (mean valid count, own grid): " + "; ".join(
        f"{p} {t[f'n_px_{p}'].min():.0f}-{t[f'n_px_{p}'].max():.0f}" for p in [rain, *ets]) + "."]
    text = "\n".join(L) + "\n"
    (out / "neraca_balance.md").write_text(text, encoding="utf-8")
    return {"years": years, "stable_ok": int(ok) if len(t) >= 5 else None, "et_rho": et_rho, "thresholds": (q_one, q_med), "median_year_rho": med, "source_rho": src_rho, "text": text}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rain", default="chirps")
    ap.add_argument("--et", default="mod16,wapor", help="ET products, the first is central (MOD16: its level is within the eddy-covariance range, docs/reports/forcing_products.md)")
    ap.add_argument("--rain-mode", choices=["unit", "khg"], default="khg", help="KHG-mean rain for every unit (default: CHIRPS and IMERG disagree on the order of units, docs/reports/forcing_products.md), or rain per unit")
    ap.add_argument("--registry", default=None)
    a = ap.parse_args(argv)
    reg = Registry.load(a.registry) if a.registry else Registry.load()
    r = run(Path(a.inputs), Path(a.out), a.rain, [s for s in a.et.split(",") if s], reg, a.rain_mode)
    print(r["text"])


if __name__ == "__main__":
    main()
