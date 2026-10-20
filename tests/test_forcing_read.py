"""forcing_read: the file route filters the window; bad modes and a missing direct block stop with a message.

    python -m pytest tests/test_forcing_read.py
"""
import pandas as pd
import pytest

from repeat_neraca.forcing_read import read_forcing


def _write(tmp_path):
    pd.DataFrame({"date": ["2026-04-01", "2026-04-02", "2026-04-01"], "window": ["calibration", "calibration", "2019"],
                  "P_era5_mm": [1.0, 2.0, 3.0], "E_era5_mm": [0.5, 0.5, 0.5], "E_wapor_mm": [None, None, None]}).to_csv(tmp_path / "forcing_daily.csv", index=False)


def test_file_route_keeps_only_the_window(tmp_path):
    _write(tmp_path)
    f, route = read_forcing({"forcing_window": "calibration"}, tmp_path, "auto")
    assert route == "file" and list(f["P_era5_mm"]) == [1.0, 2.0]


def test_auto_without_block_is_file_and_direct_without_block_stops(tmp_path):
    _write(tmp_path)
    with pytest.raises(SystemExit):
        read_forcing({"forcing_window": "calibration"}, tmp_path, "direct")
    with pytest.raises(ValueError):
        read_forcing({"forcing_window": "calibration"}, tmp_path, "nope")
