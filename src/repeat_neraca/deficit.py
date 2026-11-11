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
  no TMAT  a KHG with no water-table reading in the window can still get a deficit, but only when its config asks for one: dz is
           then assumed, not observed. `dz_no_obs_cm` is null by default, and the KHG stops as before. A number is the assumed drop
           (cm); `observed` takes the drops measured at the KHG with stations (OBSERVED_DZ_CM: median 9.35 cm, band 2.8 to 22.2 cm),
           and `dz_no_obs_band_cm` [low, high] sets or overrides the band. deficit_mm uses the central dz; deficit_mm_low and
           deficit_mm_high run over the dz band and the Sy band together. Such a row has water_table_source "assumed", n_stations 0,
           dz_assumed_cm filled and the observed columns (obs_depth_*, obs_change_cm) empty. A KHG whose stations have readings in the
           window but too few for the change still stops (lower `min_station_coverage` instead): the assumption never replaces data
           silently. Read the source before using the deficit as a measured value (`is_assumed`).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULTS = {"start": "06-01", "end": "10-31", "sy": 0.15, "sy_band": [0.10, 0.20], "edge_days": 7, "min_station_coverage": 0.5,
            "wapor_bound": False, "dz_no_obs_cm": None, "dz_no_obs_band_cm": None}

# Water-table drop over the deficit window (cm, positive = deeper) at the KHG with SiTMAT stations, 2026 (runs/deficit/neraca_khg.csv,
# collected 2026-11-10). `dz_no_obs_cm: observed` takes their median and range for a KHG without stations.
OBSERVED_DZ_CM = {"Air Hitam Laut-Buntu Kecil": 2.8, "Mendahara-Batanghari": 22.2, "Sugihan-Lumpur": 11.0, "Pungurbesar-Kapuas": 20.5,
                  "Kapuas-Barito": 3.7, "Kahayan-Sebangau": 7.7}

COLUMNS = ["khg_id", "period_start", "period_end", "n_days", "valid_day_share", "n_stations", "area_km2", "sy", "net_balance_mm",
           "obs_depth_start_cm", "obs_depth_end_cm", "obs_change_cm", "storage_change_mm", "deficit_mm", "deficit_mm_low",
           "deficit_mm_high", "deficit_m3", "deficit_months", "evaporation_source", "e_wapor_covers_period", "water_table_source", "dz_assumed_cm",
           "method"]


def _deficit(net_mm: float, dz_cm: float, sy: float) -> float:
    return float(max(0.0, -net_mm - sy * dz_cm * 10.0))


def assumed_dz(c: dict) -> tuple[float, list[float]] | None:
    """(central dz, [low, high]) in cm for a KHG without readings, from the config; None when the config asks for stations."""
    v, band = c.get("dz_no_obs_cm"), c.get("dz_no_obs_band_cm")
    if v is None:
        return None
    if v == "observed":
        obs = list(OBSERVED_DZ_CM.values())
        if not obs:
            raise ValueError("dz_no_obs_cm is `observed` but OBSERVED_DZ_CM holds no measured drop")
        v, band = float(np.median(obs)), band or [min(obs), max(obs)]
    try:
        v = float(v)
    except (TypeError, ValueError):
        raise ValueError(f"dz_no_obs_cm must be a number of cm or `observed`, got {v!r}") from None
    if band is not None and (not isinstance(band, (list, tuple)) or len(band) != 2):
        raise ValueError(f"dz_no_obs_band_cm must be [low, high] in cm, got {band!r}")
    lo, hi = (float(x) for x in (band or [v, v]))
    if not lo <= v <= hi:
        raise ValueError(f"dz_no_obs_cm {v:g} lies outside dz_no_obs_band_cm [{lo:g}, {hi:g}]")
    return v, [lo, hi]


def is_assumed(row) -> bool:
    """True for a neraca_khg.csv row whose water-table change was assumed (files written before the column existed: observed)."""
    src = row.get("water_table_source") if hasattr(row, "get") else None
    return isinstance(src, str) and src.startswith("assumed")


def khg_deficit(forcing: pd.DataFrame, obs: pd.DataFrame, area_km2: float, khg_id: str, cfg: dict | None = None) -> dict:
    """One row of neraca_khg.csv (see COLUMNS).

    forcing: date, P_era5_mm, E_era5_mm, optionally E_wapor_mm. obs: stations in columns, dates in the index, depth in cm (positive down);
    None or an empty frame when the KHG has no TMAT station (then dz = dz_no_obs_cm, see the module notes).
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

    o = obs.reindex(w.index) if obs is not None else pd.DataFrame(index=w.index)
    readings = bool(o.notna().any().any()) if o.shape[1] else False
    cover = o.notna().mean()
    o = o.loc[:, cover >= float(c["min_station_coverage"])]
    mean_o = o.mean(axis=1).dropna()
    k = int(c["edge_days"])
    has_obs = len(mean_o) >= 2 * k
    dzs, band = None, None
    if has_obs:
        z0, z1 = float(mean_o.iloc[:k].mean()), float(mean_o.iloc[-k:].mean())
        dz = z1 - z0
    else:
        a = assumed_dz(c)
        if readings or a is None:
            raise ValueError("too few observed days to get the water table change over the window"
                             + ("" if readings else "; for a KHG without TMAT stations set deficit.dz_no_obs_cm (a drop in cm, or `observed`)"))
        z0 = z1 = float("nan")
        dz, band = a                        # no TMAT: an assumed drop, so the storage term Sy * dz is still subtracted
        dzs = sorted({dz, *band})

    sy = float(c["sy"])
    sys_ = {sy, *map(float, c["sy_band"])}
    variants = [_deficit(net, d, s) for s in sys_ for d in (dzs or [dz])]
    wapor_ok = "E_wapor_mm" in w and bool(w["E_wapor_mm"].notna().all()) and bool(valid.all())
    if wapor_ok and c["wapor_bound"]:
        net_w = float((w["P_era5_mm"] - w["E_wapor_mm"]).sum())
        variants += [_deficit(net_w, d, s) for s in sys_ for d in (dzs or [dz])]
    central = _deficit(net, dz, sy)
    month_net = (wv["P_era5_mm"] - wv["E_era5_mm"]).groupby(wv.index.month).sum()
    return {"khg_id": str(khg_id), "period_start": start.date().isoformat(), "period_end": last.date().isoformat(),
            "n_days": int(valid.sum()), "valid_day_share": float(valid.mean()), "n_stations": int(o.shape[1]) if has_obs else 0,
            "area_km2": float(area_km2), "sy": sy, "net_balance_mm": net, "obs_depth_start_cm": z0, "obs_depth_end_cm": z1,
            "obs_change_cm": dz if has_obs else float("nan"), "storage_change_mm": sy * dz * 10.0, "deficit_mm": central, "deficit_mm_low": float(min(variants)),
            "deficit_mm_high": float(max(variants)), "deficit_m3": central / 1000.0 * area_km2 * 1e6,
            "deficit_months": int((month_net < 0).sum()), "evaporation_source": "ERA5", "e_wapor_covers_period": wapor_ok,
            "water_table_source": "stations" if has_obs else "assumed", "dz_assumed_cm": float("nan") if has_obs else dz,
            "method": "max(0, -sum(P-E) - Sy*dz_obs); ERA5 P and E; Sy 0.15, band 0.10-0.20" + ("; WaPOR bound" if c["wapor_bound"] else "")
                      + ("" if has_obs else f"; no TMAT stations: dz assumed {dz:g} cm, band {band[0]:g}-{band[1]:g} cm")}
