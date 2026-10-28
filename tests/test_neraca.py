"""Tests of the physical neraca air (repeat_neraca): lumped model against the 2D solver, and the real-KHG loader on made-up rasters."""
import numpy as np
import pytest

from repeat_neraca.groundwater import lumped
from repeat_neraca.params import Registry
from repeat_neraca.groundwater import solve


def const(sy, T):
    return (lambda z: sy), (lambda z: T)


def test_lumped_steady_state_is_the_strip_between_two_drains():
    # uniform recharge R on a strip of width L between drains at the canal level: mean depth R L^2 / (12 T)
    sy, T, L, R = 0.2, 100.0, 200.0, -0.003
    sy_fn, t_fn = const(sy, T)
    z = lumped.simulate(np.full(600, R), sy_fn, t_fn, L, 0.0, 0.0)
    assert z[-1] == pytest.approx(R * L**2 / (12 * T), abs=1e-4)


def test_lumped_matches_the_2d_solver_on_the_same_strip():
    nx, dx, T, sy, R = 21, 10.0, 100.0, 0.2, -0.003
    L = (nx - 1) * dx
    ny = 3
    fixed = np.zeros((ny, nx), bool)
    fixed[:, 0] = fixed[:, -1] = True
    h = solve(np.zeros((ny, nx)), np.ones((ny, nx), bool), dx, fixed, np.zeros((ny, nx)), np.zeros((ny, nx)), [R] * 300,
              lambda zeta: np.full_like(zeta, sy), lambda zeta, cells: np.full_like(zeta, T))
    trapezoid = getattr(np, "trapezoid", None) or np.trapz                             # numpy 2 renamed trapz
    mean_2d = trapezoid(h[1], dx=dx) / L
    sy_fn, t_fn = const(sy, T)
    z = lumped.simulate(np.full(300, R), sy_fn, t_fn, L, 0.0, 0.0)
    assert z[-1] == pytest.approx(mean_2d, abs=3e-3)


def test_lumped_stays_at_the_canal_level_without_forcing_and_never_rises_above_the_surface():
    sy_fn, t_fn = const(0.2, 50.0)
    z = lumped.simulate(np.zeros(50), sy_fn, t_fn, 300.0, 0.8, -0.8)
    assert np.allclose(z, -0.8)
    z = lumped.simulate(np.full(20, 0.05), sy_fn, t_fn, 300.0, 0.8, -0.1)             # 5 cm of rain a day, 20 days
    assert z.max() <= 0.0


def test_lumped_is_stable_with_very_close_drains_and_skips_days_without_forcing():
    sy_fn, t_fn = const(0.1, 500.0)
    net = np.full(40, -0.004)
    net[10:13] = np.nan
    z = lumped.simulate(net, sy_fn, t_fn, 40.0, 0.5, -0.5)                              # coupling rate about 37 per day
    assert np.isfinite(z[np.isfinite(net)]).all() and np.isnan(z[10:13]).all()
    assert (z[np.isfinite(z)] > -0.52).all()                                             # held close to the canal level


def test_drain_spacing_from_canal_length():
    assert lumped.drain_spacing_m(100.0, 200.0) == pytest.approx(500.0)               # 100 km2 with 200 km of canal
    assert lumped.drain_spacing_m(100.0, 0.0) == float("inf")


def test_registry_has_the_neraca_parameters_inside_their_ranges():
    r = Registry.load()
    for k in ("canal_drawdown", "river_stage_below_edge", "neraca_grid_res_m", "initial_wtd"):
        lo, hi = r.params[k].range
        assert lo <= r[k] <= hi
    with pytest.raises(ValueError):
        r.with_overrides({"canal_drawdown": 5.0})


def test_loader_reads_a_made_up_khg(tmp_path):
    rasterio = pytest.importorskip("rasterio")
    gpd = pytest.importorskip("geopandas")
    from rasterio.transform import from_origin
    from shapely.geometry import LineString, box

    from repeat_neraca.groundwater import grid as IN
    crs = "EPSG:32748"                                                # UTM 48S, around 105.5 E, 3 S
    x0, y1 = 500000.0, 9668000.0
    khg = gpd.GeoDataFrame({"id": [1]}, geometry=[box(x0 + 1000, y1 - 7000, x0 + 7000, y1 - 1000)], crs=crs)
    khg.to_file(tmp_path / "khg.gpkg", driver="GPKG")
    tr = from_origin(x0, y1, 100.0, 100.0)
    shape = (80, 80)
    for name, value in (("dtm.tif", 3.0), ("peat.tif", 200.0)):
        with rasterio.open(tmp_path / name, "w", driver="GTiff", height=shape[0], width=shape[1], count=1, dtype="float32", crs=crs,
                           transform=tr, nodata=-9999.0) as dst:
            dst.write(np.full(shape, value, "float32"), 1)
    lines = [LineString([(x0 + 1500, y1 - 4000), (x0 + 6500, y1 - 4000)]), LineString([(x0 + 4000, y1 - 1500), (x0 + 4000, y1 - 6500)])]
    gpd.GeoDataFrame({"KET_KANAL": ["Kanal Primer", "Kanal Sekunder"]}, geometry=lines, crs=crs).to_file(tmp_path / "canals.gpkg", driver="GPKG")
    cfg = {"name": "t", "khg": str(tmp_path / "khg.gpkg"), "dtm": str(tmp_path / "dtm.tif"), "peat_depth": {"path": str(tmp_path / "peat.tif"), "scale": 0.01},
           "canals": {"path": str(tmp_path / "canals.gpkg"), "class_field": "KET_KANAL",
                      "classes": {"primary": ["Kanal Primer"], "secondary": ["Kanal Sekunder"], "tertiary": ["Kanal Tersier"]}},
           "inputs_dir": str(tmp_path)}
    k = IN.load(cfg, 500.0)
    assert k.crs == "EPSG:32748"
    assert k.area_km2 == pytest.approx(36.0, rel=0.1)
    assert np.allclose(k.surface[k.domain], 3.0, atol=1e-3) and np.allclose(k.peat_depth[k.domain], 2.0, atol=1e-3)
    assert k.canal_length_km["primary"] == pytest.approx(5.0, rel=0.02) and k.canal_length_km["tertiary"] == 0.0
    fixed, head = IN.fixed_head(k, canal_drawdown=1.2, river_stage_below_edge=0.3)
    assert fixed[k.boundary].all() and fixed[k.canal["primary"]].all()
    assert np.allclose(head[k.boundary], 3.0 - 0.3) and np.allclose(head[k.canal["secondary"]], 3.0 - 1.2)


def test_et_factor_is_one_above_the_start_zero_below_the_end_and_linear_between():
    f = lumped.et_factor(-0.7, -1.82)
    assert f(0.0) == 1.0 and f(-0.7) == 1.0 and f(-1.82) == 0.0 and f(-3.0) == 0.0
    assert f(-1.26) == pytest.approx(0.5)


def test_evaporation_stress_stops_the_fall_of_the_water_table():
    sy_fn, t_fn = const(0.2, 0.0)                                                      # no drain: only rain and evaporation
    rain, et = np.zeros(400), np.full(400, 0.004)
    free = lumped.simulate_rain_et(rain, et, sy_fn, t_fn, float("inf"), 1.0, 0.0)
    stressed = lumped.simulate_rain_et(rain, et, sy_fn, t_fn, float("inf"), 1.0, 0.0, lumped.et_factor(-0.7, -1.82))
    assert free[-1] < -5.0                                                              # 400 days at 4 mm/day on Sy 0.2
    assert stressed[-1] > -1.83 and stressed[-1] < -1.5                                 # the fall slows and stops where ET reaches zero
    assert (np.diff(stressed) <= 1e-12).all()


def test_solver_takes_a_recharge_field_per_step():
    z = np.zeros((6, 6))
    domain = np.ones((6, 6), bool)
    fixed = np.zeros((6, 6), bool)
    field = np.zeros((6, 6))
    field[:, 3:] = -0.004
    h = solve(z, domain, 10.0, fixed, np.zeros((6, 6)), np.zeros((6, 6)), [field],
              lambda zeta: np.full_like(zeta, 0.2), lambda zeta, cells: np.full_like(zeta, 1e-9))     # isolated cells: no lateral flow
    assert np.allclose(h[:, :3], 0.0) and np.allclose(h[:, 3:], -0.004 / 0.2)
