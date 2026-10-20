"""Checks of the neraca air bucket against cases that can be worked out by hand.

    python -m tests.test_neraca_model
"""
import numpy as np
import pandas as pd

from repeat_neraca.bucket.model import simulate, unit_indicators


def test_constant_deficit_is_linear():
    # 3 mm/day deficit, Sy 0.3: 3 / (10 * 0.3) = 1 cm/day, from z0 = 0
    z = simulate(np.full(30, -3.0), sy=0.3)[:, 0]
    assert np.allclose(np.diff(z), 1.0), np.diff(z)[:3]
    assert np.isclose(z[-1], 30.0)


def test_floor_at_surface():
    # a long surplus cannot lift the water table above the surface
    z = simulate(np.full(20, 8.0), sy=0.3, z0=5.0)[:, 0]
    assert z.min() == 0.0 and z[-1] == 0.0


def test_cap_at_peat_depth():
    z = simulate(np.full(100, -5.0), sy=0.2, depth=25.0)[:, 0]
    assert z.max() == 25.0 and z[-1] == 25.0


def test_sy_scales_the_drawdown():
    a = simulate(np.full(10, -2.0), sy=0.2)[-1, 0]
    b = simulate(np.full(10, -2.0), sy=0.4)[-1, 0]
    assert np.isclose(a, 2 * b)


def test_drainage_deepens_the_water_table():
    # no net rain-evaporation balance; the drain alone (k = 2 mm/day at full proximity) removes 2 mm/day
    z = simulate(np.zeros(10), sy=0.5, k=2.0, c=1.0)[:, 0]
    assert np.isclose(z[-1], 10 * 2.0 / (10 * 0.5))
    assert simulate(np.zeros(10), sy=0.5, k=2.0, c=0.0)[-1, 0] == 0.0


def test_many_series_at_once():
    net = np.column_stack([np.full(10, -3.0), np.full(10, -3.0)])
    z = simulate(net, sy=0.3, depth=np.array([100.0, 4.0]))
    assert np.isclose(z[-1, 0], 10.0) and np.isclose(z[-1, 1], 4.0)


def test_rise_after_rain():
    net = np.r_[np.full(10, -3.0), np.full(5, 6.0)]            # 10 cm down, then 2 cm/day up
    z = simulate(net, sy=0.3)[:, 0]
    assert np.isclose(z[9], 10.0) and np.isclose(z[-1], 0.0)


def test_nan_days_hold_the_state():
    net = np.array([-3.0, np.nan, -3.0])
    z = simulate(net, sy=0.3)[:, 0]
    assert np.isclose(z[0], 1.0) and np.isnan(z[1]) and np.isclose(z[2], 2.0)


def test_indicators():
    dates = pd.date_range("2021-04-01", "2021-10-31")
    P = np.zeros(len(dates))
    E = np.full(len(dates), 3.0)                                  # constant 3 mm/day deficit
    P[(dates.month == 7) & (dates.day == 10)] = 40.0              # one rainy day splits the dry run
    depth = np.array([100.0, 200.0, np.nan, -5.0])               # invalid pixels are ignored
    r = unit_indicators(dates, P, E, depth, c_u=0.0, sy=0.3, k=0.0, z0=0.0)
    assert r["u_deficit_months_dry"] == 5                         # every dry month is in deficit
    assert r["u_wt_days_gt40"] > 0.5                              # deeper than 40 cm for most of the season
    # peak is the uncapped depth; decline averages min(peak, depth)/depth over the valid pixels
    exp = np.mean(np.minimum(r["u_wt_peak_cm"], [100.0, 200.0]) / [100.0, 200.0]) * 100
    assert np.isclose(r["u_storage_decline_pct"], exp)
    assert r["u_wb_daily_mean"] < 0
    # dry runs: Jun 1 to Jul 9 (39 days), then Jul 11 to Oct 31 (113 days) -> mean 76
    assert np.isclose(r["u_dry_days_mean"], 76.0), r["u_dry_days_mean"]


if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            n += 1
            print("ok", name)
    print(n, "checks passed")
