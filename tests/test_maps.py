"""Map layers of the neraca air: units with the balance and its climatology, stations with their dry-season water table."""
import pandas as pd
import pytest

gpd = pytest.importorskip("geopandas")
from shapely.geometry import box  # noqa: E402

from repeat_neraca.maps import station_summary, write_map  # noqa: E402


def test_station_summary_uses_the_window_and_the_40_cm_limit():
    st = pd.DataFrame({"station_id": ["a"], "lon": [105.0], "lat": [-3.0]})
    d = pd.DataFrame({"date": ["2026-05-30", "2026-06-01", "2026-06-02", "2026-06-03"], "station_id": ["a"] * 4,
                      "depth_cm": [10.0, 30.0, 50.0, 45.0]})
    s = station_summary(st, d, "2026-06-01", "2026-06-30").iloc[0]
    assert s["depth_start_cm"] == 30 and s["depth_end_cm"] == 45 and s["change_cm"] == 15 and s["depth_max_cm"] == 50
    assert s["share_deeper_40cm"] == pytest.approx(2 / 3) and s["n_days"] == 3


def test_write_map_joins_balance_climatology_deficit_and_stations(tmp_path):
    kf = tmp_path / "16.02.01_test"
    (kf / "02_delineation").mkdir(parents=True)
    gpd.GeoDataFrame({"unit_id": ["U1", "U2"]}, geometry=[box(105, -3.1, 105.1, -3), box(105.1, -3.1, 105.2, -3)], crs="EPSG:4326") \
        .to_file(kf / "02_delineation" / "subkhg_units.gpkg", driver="GPKG")
    run = kf / "03_neraca" / "runs" / "balance"
    run.mkdir(parents=True)
    pd.DataFrame({"unit_id": ["U1", "U2"], "u_wb_mean": [50.0, 60.0], "u_deficit_months": [2.0, 1.5], "balance_stable_ok": [1, 1]}) \
        .to_csv(run / "neraca_balance_unit.csv", index=False)
    months = [f"2024-{m:02d}" for m in range(1, 13)]
    mon = pd.DataFrame([(m, u, float(i) - 5, "mod16") for u in ("U1", "U2") for i, m in enumerate(months)] +
                       [(m, "U1", 99.0, "wapor") for m in months], columns=["month", "unit_id", "WB_mm", "et_source"])
    mon.to_csv(run / "neraca_balance_monthly.csv", index=False)
    (kf / "03_neraca" / "runs" / "deficit").mkdir(parents=True)
    pd.DataFrame({"period_start": ["2024-06-01"], "period_end": ["2024-10-31"], "deficit_mm": [120.0]}) \
        .to_csv(kf / "03_neraca" / "runs" / "deficit" / "neraca_khg.csv", index=False)
    inp = kf / "03_neraca" / "inputs"
    inp.mkdir(parents=True)
    pd.DataFrame({"station_id": ["s1"], "lon": [105.05], "lat": [-3.05]}).to_csv(inp / "stations.csv", index=False)
    pd.DataFrame({"date": ["2024-06-01", "2024-07-01"], "station_id": ["s1", "s1"], "depth_cm": [20.0, 60.0]}).to_csv(inp / "stations_daily.csv", index=False)
    out = write_map(kf)
    u = gpd.read_file(out, layer="neraca_units").set_index("unit_id")
    assert u.loc["U1", "wb_m01"] == -5 and u.loc["U1", "wb_m12"] == 6                  # the central source (mod16), not wapor
    assert u.loc["U1", "wb_dry_mm"] == pytest.approx((1 + 2 + 3 + 4) / 4)            # July to October
    assert u.loc["U2", "khg_deficit_mm"] == 120 and u.loc["U1", "order_ok"] == 1
    s = gpd.read_file(out, layer="neraca_stations")
    assert list(s["unit_id"]) == ["U1"] and s["change_cm"].iloc[0] == 40
