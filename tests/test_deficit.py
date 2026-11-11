"""KHG deficit from the mass balance P - E and the observed storage change (repeat_neraca.deficit).

    python -m pytest tests/test_deficit.py
"""
import numpy as np
import pandas as pd
import pytest

from repeat_neraca.deficit import OBSERVED_DZ_CM, is_assumed, khg_deficit


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


def test_wapor_gives_the_other_bound_only_if_asked_and_it_covers_every_day():
    f, obs = _case(net=-1.0, wapor=-2.0)
    assert khg_deficit(f, obs, 10.0, "X")["deficit_mm_high"] < 200 - 10.0          # off by default
    r = khg_deficit(f, obs, 10.0, "X", {"wapor_bound": True})
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


def test_without_tmat_it_stops_unless_the_config_assumes_a_drop():
    f, obs = _case()
    for o in (None, obs.iloc[:, :0], obs * np.nan):                     # no frame, no station, stations without readings
        with pytest.raises(ValueError, match="dz_no_obs_cm"):
            khg_deficit(f, o, 100.0, "X")


def test_without_tmat_an_assumed_drop_is_subtracted_and_marked():
    f, obs = _case()                                                    # -100 mm; with stations (dz 10 cm) the deficit is 85 mm
    for o in (None, obs.iloc[:, :0], obs * np.nan):
        r = khg_deficit(f, o, 100.0, "X", {"dz_no_obs_cm": 10.0})       # 0.15 * 10 * 10 = 15 mm of storage
        assert r["deficit_mm"] == pytest.approx(85.0) and r["storage_change_mm"] == pytest.approx(15.0)
        assert r["deficit_mm_low"] == pytest.approx(80.0) and r["deficit_mm_high"] == pytest.approx(90.0)     # Sy band only
        assert r["n_stations"] == 0 and r["water_table_source"] == "assumed" and r["dz_assumed_cm"] == 10.0
        assert np.isnan(r["obs_change_cm"]) and np.isnan(r["obs_depth_start_cm"])
        assert is_assumed(r)
    r = khg_deficit(f, obs, 100.0, "X", {"dz_no_obs_cm": 10.0})         # stations win over the assumption
    assert r["water_table_source"] == "stations" and np.isnan(r["dz_assumed_cm"]) and not is_assumed(r)


def test_the_observed_band_runs_with_the_sy_band():
    f, _ = _case()
    obs = list(OBSERVED_DZ_CM.values())
    r = khg_deficit(f, None, 100.0, "X", {"dz_no_obs_cm": "observed"})
    assert r["dz_assumed_cm"] == pytest.approx(np.median(obs)) == pytest.approx(9.35)
    assert r["deficit_mm"] == pytest.approx(100 - 0.15 * 9.35 * 10)
    assert r["deficit_mm_low"] == pytest.approx(100 - 0.20 * max(obs) * 10)          # deepest drop, largest Sy
    assert r["deficit_mm_high"] == pytest.approx(100 - 0.10 * min(obs) * 10)         # shallowest drop, smallest Sy
    r = khg_deficit(f, None, 100.0, "X", {"dz_no_obs_cm": 5.0, "dz_no_obs_band_cm": [2.0, 20.0]})
    assert r["deficit_mm_low"] == pytest.approx(60.0) and r["deficit_mm_high"] == pytest.approx(98.0)
    with pytest.raises(ValueError, match="outside"):
        khg_deficit(f, None, 100.0, "X", {"dz_no_obs_cm": 30.0, "dz_no_obs_band_cm": [2.0, 20.0]})


def test_too_few_readings_still_stops_even_with_an_assumed_drop():
    f, obs = _case()
    sparse = obs.copy()
    sparse.loc[sparse.index.day != 1] = np.nan                          # readings exist, but under the coverage threshold
    with pytest.raises(ValueError, match="too few observed days"):
        khg_deficit(f, sparse, 100.0, "X", {"dz_no_obs_cm": "observed"})


def test_files_without_the_column_count_as_observed():
    assert not is_assumed(pd.Series({"deficit_mm": 100.0}))
    assert is_assumed(pd.Series({"water_table_source": "assumed"}))


def test_config_mistakes_give_a_clear_message():
    f, _ = _case()
    with pytest.raises(ValueError, match="number of cm or `observed`"):
        khg_deficit(f, None, 100.0, "X", {"dz_no_obs_cm": "observe"})          # typo
    with pytest.raises(ValueError, match=r"\[low, high\]"):
        khg_deficit(f, None, 100.0, "X", {"dz_no_obs_cm": 5.0, "dz_no_obs_band_cm": [2.0]})
