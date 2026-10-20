"""KHG deficit from the mass balance P - E and the observed storage change (repeat_neraca.deficit).

    python -m pytest tests/test_deficit.py
"""
import numpy as np
import pandas as pd
import pytest

from repeat_neraca.deficit import khg_deficit


def _case(net=-1.0, n=100, z0=40.0, z1=50.0, wapor=None):
    dates = pd.date_range("2026-04-01", periods=61 + n)               # 1 April + 61 days = 1 June
    f = pd.DataFrame({"date": dates, "P_era5_mm": 2.0, "E_era5_mm": 2.0 - net, "E_wapor_mm": np.nan if wapor is None else 2.0 - wapor})
    zs = np.where(np.arange(len(dates)) < 61 + n // 2, z0, z1).astype(float)      # a step half way, so both ends of the window are flat
    obs = pd.DataFrame({"a": zs, "b": zs + 5}, index=dates)           # two stations, the same change
    return f, obs


def test_mass_balance_minus_storage_change():
    f, obs = _case()                                                    # -100 mm over 100 days; water table 10 cm deeper = 15 mm at Sy 0.15
    r = khg_deficit(f, obs, 100.0, "X")
    assert r["n_days"] == 100 and r["n_stations"] == 2
    assert r["net_balance_mm"] == pytest.approx(-100.0) and r["obs_change_cm"] == pytest.approx(10.0)
    assert r["deficit_mm"] == pytest.approx(85.0)
    assert r["deficit_mm_low"] == pytest.approx(100 - 20.0) and r["deficit_mm_high"] == pytest.approx(100 - 10.0)
    assert r["deficit_m3"] == pytest.approx(85.0 / 1000 * 100 * 1e6)


def test_no_deficit_when_rain_covers_the_loss_and_the_rise():
    f, obs = _case(net=+0.5)                                            # +50 mm of rain surplus and a deeper table: nothing to supply
    assert khg_deficit(f, obs, 10.0, "X")["deficit_mm"] == 0.0
    f, obs = _case(net=+0.5, z0=50.0, z1=30.0)                          # +50 mm; the water table rose 20 cm = 30 mm of storage: 20 mm left over
    assert khg_deficit(f, obs, 10.0, "X")["deficit_mm"] == 0.0


def test_a_rising_water_table_against_a_negative_balance_adds_to_the_deficit():
    f, obs = _case(net=-0.1, z0=50.0, z1=30.0)                          # -10 mm lost and 30 mm stored: 40 mm had to come from outside
    assert khg_deficit(f, obs, 10.0, "X")["deficit_mm"] == pytest.approx(40.0)


def test_wapor_gives_the_other_bound_only_if_it_covers_every_day():
    f, obs = _case(net=-1.0, wapor=-2.0)
    r = khg_deficit(f, obs, 10.0, "X")
    assert r["e_wapor_covers_period"] and r["deficit_mm_high"] == pytest.approx(200 - 10.0)
    f.loc[f.index[-3:], "E_wapor_mm"] = np.nan
    assert not khg_deficit(f, obs, 10.0, "X")["e_wapor_covers_period"]


def test_missing_forcing_days_lower_the_valid_share():
    f, obs = _case()
    f.loc[f.index[70:80], ["P_era5_mm", "E_era5_mm"]] = np.nan
    r = khg_deficit(f, obs, 10.0, "X")
    assert r["n_days"] == 90 and r["valid_day_share"] == pytest.approx(90 / 100)


def test_stops_without_forcing_in_the_window():
    f, obs = _case(n=1)
    f["P_era5_mm"] = np.nan
    with pytest.raises(ValueError):
        khg_deficit(f, obs, 10.0, "X")
