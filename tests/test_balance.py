"""Climatic water balance per sub-KHG (repeat_neraca.balance) on synthetic Earth Engine tables."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from repeat_neraca import balance as B
from repeat_neraca.params import Registry


def _dekads(start: date, end: date):
    out, d = [], start
    while d < end:
        e = date(d.year + d.month // 12, d.month % 12 + 1, 1) if d.day == 21 else date(d.year, d.month, d.day + 10)
        out.append((d, e))
        d = e
    return out


def _write(path, units, rate_per_day, end=date(2021, 1, 1), cov=1.0):
    rows = [{"unit_id": u, "start": a, "end": b, "days": (b - a).days, "mm": rate_per_day(u, a) * (b - a).days, "n_px": 4, "time_cov": cov}
            for a, b in _dekads(date(2019, 1, 1), end) for u in units]
    pd.DataFrame(rows).to_csv(path, index=False)


@pytest.fixture
def inputs(tmp_path):
    units = [f"U{i}" for i in range(6)]
    # rain 8 mm/day; ET 4 mm/day + 0.5 per unit index, + 6 mm/day in Aug-Sep: deficits grow with the index, same every year
    _write(tmp_path / "balance_chirps_dekad.csv", units, lambda u, d: 8.0)
    _write(tmp_path / "balance_wapor_dekad.csv", units, lambda u, d: 4.0 + 0.5 * int(u[1]) + (6.0 if d.month in (8, 9) else 0.0))
    pd.DataFrame({"unit_id": units, "area_km2": 10.0, "wc_10": [1, 1, 0.5, 0.5, 0, 0], "wc_40": [0, 0, 0.5, 0.5, 1, 1]}).to_csv(
        tmp_path / "units_landcover.csv", index=False)
    return tmp_path


def test_balance_formula_years_and_indicators(inputs, tmp_path):
    reg = Registry.load()
    r = B.run(inputs, tmp_path / "out", "chirps", ["wapor"], reg)
    assert r["years"] == [2019, 2020]
    t = pd.read_csv(tmp_path / "out" / "neraca_balance_unit.csv").set_index("unit_id")
    c, it, ic = reg["runoff_coefficient"], reg["interception_tree"], reg["interception_crop"]
    i0 = it                                  # U0 is all tree cover
    days = 365 + 366
    p_eff = 8.0 * (1 - i0) * (1 - c) * days
    et = 4.0 * days + 6.0 * (31 + 30) * 2
    assert t.loc["U0", "u_wb_mean"] == pytest.approx((p_eff - et) / 24, abs=1e-3)     # csv keeps 3 decimals
    assert t.loc["U4", "interception_share"] == pytest.approx(ic)
    assert t.loc["U0", "u_deficit_months"] == 2.0                  # August and September
    assert (t["u_wb_mean"].diff().dropna() < 0).all()             # more ET, lower balance
    assert t["balance_stable_ok"].iloc[0] == 1                     # same order every year


def test_a_partly_covered_month_does_not_count(inputs, tmp_path):
    d = pd.read_csv(inputs / "balance_wapor_dekad.csv")
    d.loc[d["start"] == "2020-12-21", "time_cov"] = 0.5
    d.to_csv(inputs / "balance_wapor_dekad.csv", index=False)
    r = B.run(inputs, tmp_path / "out", "chirps", ["wapor"], Registry.load())
    assert r["years"] == [2019]
