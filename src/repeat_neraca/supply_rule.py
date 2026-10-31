"""Supply cap from the KHG's own climate (`--supply-cap climate`, D22).

The dry window is the DEKADS stretch of the year (dekads are the 1st, 11th and 21st of each month, 36 a year, circular) with the largest mean shortfall
(ET minus rain) over the complete years 2018-2025 of the KHG's sub-KHG balance files (pixel-weighted mean). The cap is the shortfall of the run
over that window, floored at 0: it is the water that managed land would need in the year being simulated, so a wet year gives a cap near 0.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DEKADS = 14          # the length of the station deficit windows (June to October)


def dekad_index(d) -> np.ndarray:
    d = pd.DatetimeIndex(d)
    return (d.month.to_numpy() - 1) * 3 + np.minimum((d.day.to_numpy() - 1) // 10, 2)


def history(kf: Path, last_year: int = 2025, dem: str | None = None) -> pd.DataFrame:
    """Pixel-weighted KHG mean rain `p` and ET `e` (mm per dekad), with the dekad of the year `d`."""
    d = Path(kf) / "03_neraca" / "inputs"
    if not (d / "balance_chirps_dekad.csv").exists():
        d = Path(kf) / "03_neraca" / "lidar" / "inputs"
    if not (d / "balance_chirps_dekad.csv").exists() and dem:
        d = Path(kf) / "03_neraca" / dem / "inputs"      # KHG without LiDAR: the variant's own sub-KHG balance
    out = {}
    for k, name in (("p", "chirps"), ("e", "mod16")):
        f = d / f"balance_{name}_dekad.csv"
        if not f.exists():
            raise SystemExit(f"the dry window needs {f} (repeat_common.fetch_gee_balance, 2018 onwards)")
        x = pd.read_csv(f, parse_dates=["start"])
        x = x[(x.n_px > 0) & x.mm.notna()]
        out[k] = x.groupby("start").apply(lambda g: np.average(g.mm, weights=g.n_px), include_groups=False)
    h = pd.DataFrame(out).dropna()
    h = h[h.index.year <= last_year]
    h["d"] = dekad_index(h.index)
    return h


def dry_window(h: pd.DataFrame, k: int = DEKADS):
    """First dekad (0..35) of the k circular dekads with the largest mean sum(E - P), and that mean (mm)."""
    c = (h.e - h.p).groupby(h.d).mean().reindex(range(36)).fillna(0).to_numpy()
    tot = [sum(c[(i + n) % 36] for n in range(k)) for i in range(36)]
    i = int(np.argmax(tot))
    return i, float(tot[i])


def window_days(dates, first: int, k: int = DEKADS) -> np.ndarray:
    """True for the days of `dates` that fall in the window."""
    return ((dekad_index(dates) - first) % 36) < k


def climate_cap(kf: Path, dates, p_mm, et_mm, dem: str | None = None):
    """(cap mm, window days, first dekad, mean shortfall of the window over the record) for a run with daily rain and ET in mm."""
    first, mean = dry_window(history(kf, dem=dem))
    days = window_days(dates, first)
    cap = max(0.0, float((np.asarray(et_mm) - np.asarray(p_mm))[days].sum()))
    return cap, days, first, mean
