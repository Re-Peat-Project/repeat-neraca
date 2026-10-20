"""Checks of the Sentinel-1 station test (repeat_neraca/bucket/sentinel1.py) on made-up data.

    python -m tests.test_sentinel1
"""
import numpy as np
import pandas as pd

from repeat_neraca.bucket.sentinel1 import block_cv, station_features, within_station


def _feats(n=60, seed=0):
    rng = np.random.default_rng(seed)
    f = pd.DataFrame({"block": np.arange(n) % 4, "signal": rng.normal(size=n), "noise": rng.normal(size=n)})
    f["y"] = 50 + 10 * f.signal + rng.normal(scale=1.0, size=n)
    return f


def test_block_cv_rewards_a_real_signal_and_not_noise():
    r = block_cv(_feats(), {"signal": ["signal"], "noise": ["noise"]}, "y").set_index("model")
    base = r.loc["no skill (training mean)", "rmse"]
    assert r.loc["signal (signal)", "rmse"] < 0.3 * base
    assert r.loc["noise (noise)", "rmse"] > 0.9 * base
    assert r.loc["signal (signal)", "oof_spearman"] > 0.9


def test_anomalies_use_the_stations_own_orbit():
    # orbit B is 3 dB brighter everywhere; station anomalies must not see that offset
    d = pd.DataFrame({"station_id": ["a"] * 8, "orbit": ["A", "B"] * 4, "vv_db": [-8, -5, -9, -6, -7, -4, -8.5, -5.5],
                      "vh_db": -14.0, "date": pd.date_range("2026-04-01", periods=8, freq="6D")})
    z = pd.DataFrame({"a": [30, 31, 40, 41, 35, 36, 38, 39]}, index=pd.date_range("2026-04-01", periods=8, freq="6D"))
    w = within_station(d, z)
    assert w["n_stations"] == 1 and w["n_pairs"] == 8


def test_features_have_one_row_per_station():
    d = pd.DataFrame({"station_id": ["a", "a", "b", "b"], "orbit": "A", "vv_db": [-8, -9, -7, -6.5], "vh_db": [-14, -15, -13, -13.5],
                      "date": pd.to_datetime(["2026-04-01", "2026-04-13"] * 2)})
    f = station_features(d)
    assert list(f.station_id) == ["a", "b"] and abs(f.vv_minus_vh_db[0] - 6.0) < 1e-9


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
