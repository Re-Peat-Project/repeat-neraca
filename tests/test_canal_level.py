"""Checks of the canal-level model (repeat_neraca/bucket/canal_level.py) on made-up data.

    python -m tests.test_canal_level
"""
import numpy as np
import pandas as pd

from repeat_neraca.bucket.canal_level import canal_series, evaluate, simulate


def test_water_table_relaxes_to_the_canal_level_without_rain_or_evaporation():
    zc_t = np.full((200, 1), 55.0)
    z = simulate(np.zeros((200, 2)), sy=0.2, gamma=50, zc_t=np.array([[30.0]] * 200))[:, :, 0]
    assert abs(z[0, 0] - 30.0) < 1e-6                         # starts at the canal level and stays there
    z = simulate(np.zeros((200, 1)), sy=0.2, gamma=50, zc_t=np.vstack([np.full((1, 1), 20.0), np.full((199, 1), 55.0)]))[:, 0, 0]
    assert z[0] < 25 and abs(z[-1] - 55.0) < 1.0              # a canal level that drops pulls the water table down with a delay


def test_evaporation_deepens_the_water_table_below_the_canal_level():
    z = simulate(np.full((300, 1), 0.3), sy=0.2, gamma=100, zc_t=np.full((300, 1), 40.0))[:, 0, 0]
    assert abs(z[-1] - (40.0 + 100 * 0.3)) < 1.0              # equilibrium: zc + gamma (E - P)


def test_seasonal_levels_switch_in_june():
    dates = pd.date_range("2026-04-01", "2026-08-31", freq="D")
    zc_t, combos = canal_series(dates, "seasonal")
    k = int(np.flatnonzero((combos == [40.0, 80.0]).all(axis=1))[0])
    assert zc_t[0, k] == 40.0 and zc_t[-1, k] == 80.0


def test_known_canal_levels_beat_the_global_mean_curve():
    rng = np.random.default_rng(1)
    dates = pd.date_range("2026-04-01", periods=150, freq="D")
    net = np.tile(0.2 + 0.1 * np.sin(np.arange(150) / 15.0), (12, 1)).T                # E - P, cm/day, same for every station
    levels = {"a": 30.0, "b": 60.0, "c": 90.0}
    conc = np.array(sum(([c] * 4 for c in levels), []))
    zc_t, combos = canal_series(dates, "constant")
    obs = np.stack([simulate(net[:, [i]], 0.2, 50, np.full((150, 1), levels[conc[i]]))[:, 0, 0] for i in range(12)], axis=1) + rng.normal(0, 1.0, (150, 12))
    res = evaluate(net, obs, conc, np.ones(150, bool), zc_t, combos)
    assert res["A"]["rmse_model"] < 0.5 * res["A"]["rmse_global"], res["A"]
    assert res["A"]["rho_peak"] > 0.8


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
