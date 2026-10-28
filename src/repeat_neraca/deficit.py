"""KHG-level deficit: the water the managed system has to supply to hold the water table, from a mass balance (no model, nothing fitted).

    deficit_mm = max(0, -sum(P - E) - Sy * dz_obs * 10)

over a dry-season window. P - E is the KHG-mean daily rain minus evaporation (mm/day); dz_obs is the change of the station-mean water table
depth over the window (cm, positive = deeper), so Sy * dz_obs * 10 is the storage the water table itself gave up (mm). What the rain
balance lost beyond that was supplied from outside the rain balance (canal and river inflow, tides, gates, pumping). Where the water table
rose or the balance is positive the deficit is 0.

Choices (agreed 2026-10-20):
  window   1 June to the last day with forcing (at most 31 October), of the forcing window's year. Station data only cover 2026, so one
           dry season is all there is; baseline years can be added when stations or other water table data cover them.
  Sy       a constant 0.15, band 0.10 to 0.20. The Urzainki et al. (2020) peat tables are not used here: they are built from boreal
           retention curves (Paivanen 1973; see groundwater/data/NOTICE-urzainki2020.md), so they are only an option once tropical peat
           has adopted them or tropical curves replace them.
  E        ERA5 is the central value (kept 2026-10-26: its evaporation totals are within -6 to +2 % of MOD16, whose level lies in the
           eddy-covariance range for tropical peat, and its rain is as close to IMERG as CHIRPS; docs/reports/forcing_products.md).
           WaPOR is no longer a bound by default (`wapor_bound`): it runs 20-30 % below the eddy-covariance range, and the cached
           2026 values were superseded upstream for six dekads.
  band     deficit_mm_low and deficit_mm_high are the smallest and largest deficit over Sy 0.10, 0.15, 0.20 (and WaPOR if wapor_bound).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULTS = {"start": "06-01", "end": "10-31", "sy": 0.15, "sy_band": [0.10, 0.20], "edge_days": 7, "min_station_coverage": 0.5,
            "wapor_bound": False}

COLUMNS = ["khg_id", "period_start", "period_end", "n_days", "valid_day_share", "n_stations", "area_km2", "sy", "net_balance_mm",
           "obs_depth_start_cm", "obs_depth_end_cm", "obs_change_cm", "storage_change_mm", "deficit_mm", "deficit_mm_low",
           "deficit_mm_high", "deficit_m3", "deficit_months", "evaporation_source", "e_wapor_covers_period", "method"]


def _deficit(net_mm: float, dz_cm: float, sy: float) -> float:
    return float(max(0.0, -net_mm - sy * dz_cm * 10.0))


def khg_deficit(forcing: pd.DataFrame, obs: pd.DataFrame, area_km2: float, khg_id: str, cfg: dict | None = None) -> dict:
    """One row of neraca_khg.csv (see COLUMNS).

    forcing: date, P_era5_mm, E_era5_mm, optionally E_wapor_mm. obs: stations in columns, dates in the index, depth in cm (positive down).
    """
    c = {**DEFAULTS, **(cfg or {})}
    f = forcing.copy()
    f["date"] = pd.DatetimeIndex(f["date"])
    f = f.set_index("date").sort_index()
    year = int(f.index[0].year)
    start = pd.Timestamp(f"{year}-{c['start']}")
    ok = f["P_era5_mm"].notna() & f["E_era5_mm"].notna()
    last = f.index[ok & (f.index <= pd.Timestamp(f"{year}-{c['end']}"))].max() if (ok & (f.index >= start)).any() else pd.NaT
    if pd.isna(last) or last <= start:
        raise ValueError(f"no forcing between {start.date()} and {c['end']}: the deficit cannot be computed")
    w = f.loc[start:last]
    valid = w["P_era5_mm"].notna() & w["E_era5_mm"].notna()
    wv = w[valid]
    net = float((wv["P_era5_mm"] - wv["E_era5_mm"]).sum())

    o = obs.reindex(w.index)
    cover = o.notna().mean()
    o = o.loc[:, cover >= float(c["min_station_coverage"])]
    mean_o = o.mean(axis=1).dropna()
    if len(mean_o) < 2 * int(c["edge_days"]):
        raise ValueError("too few observed days to get the water table change over the window")
    k = int(c["edge_days"])
    z0, z1 = float(mean_o.iloc[:k].mean()), float(mean_o.iloc[-k:].mean())
    dz = z1 - z0

    sy = float(c["sy"])
    variants = [_deficit(net, dz, s) for s in {sy, *map(float, c["sy_band"])}]
    wapor_ok = "E_wapor_mm" in w and bool(w["E_wapor_mm"].notna().all()) and bool(valid.all())
    if wapor_ok and c["wapor_bound"]:
        net_w = float((w["P_era5_mm"] - w["E_wapor_mm"]).sum())
        variants += [_deficit(net_w, dz, s) for s in {sy, *map(float, c["sy_band"])}]
    central = _deficit(net, dz, sy)
    month_net = (wv["P_era5_mm"] - wv["E_era5_mm"]).groupby(wv.index.month).sum()
    return {"khg_id": str(khg_id), "period_start": start.date().isoformat(), "period_end": last.date().isoformat(),
            "n_days": int(valid.sum()), "valid_day_share": float(valid.mean()), "n_stations": int(o.shape[1]),
            "area_km2": float(area_km2), "sy": sy, "net_balance_mm": net, "obs_depth_start_cm": z0, "obs_depth_end_cm": z1,
            "obs_change_cm": dz, "storage_change_mm": sy * dz * 10.0, "deficit_mm": central, "deficit_mm_low": float(min(variants)),
            "deficit_mm_high": float(max(variants)), "deficit_m3": central / 1000.0 * area_km2 * 1e6,
            "deficit_months": int((month_net < 0).sum()), "evaporation_source": "ERA5", "e_wapor_covers_period": wapor_ok,
            "method": "max(0, -sum(P-E) - Sy*dz_obs); ERA5 P and E; Sy 0.15, band 0.10-0.20" + ("; WaPOR bound" if c["wapor_bound"] else "")}
