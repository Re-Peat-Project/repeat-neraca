import numpy as np
import pandas as pd

from repeat_neraca.groundwater import PeatTable
from repeat_neraca.groundwater import fieldcheck as FC
from repeat_neraca.groundwater import fieldobs as FO
from repeat_neraca.groundwater import simulate as SIM
from repeat_neraca.groundwater.grid import RealKHG
from repeat_neraca.model import parse_drawdown


def small_khg(n=9, canal_col=4):
    domain = np.ones((n, n), bool)
    boundary = np.zeros((n, n), bool)
    canal = np.zeros((n, n), bool)
    canal[1:-1, canal_col] = True
    return RealKHG(name="t", crs="EPSG:32648", dx=50.0, transform=None, domain=domain, boundary=boundary, surface=np.full((n, n), 5.0),
                   peat_depth=np.full((n, n), 4.0), canal={"primary": canal, "secondary": np.zeros_like(canal), "tertiary": np.zeros_like(canal)},
                   canal_length_km={}, area_km2=0.2)


def test_canal_below_the_water_table_drains_the_peat():
    k = small_khg()
    r = SIM.run(k, [0.0] * 5, PeatTable.named("tropical-large"), SIM.Boundary({"primary": 0.8}, 0.3))
    assert (r["series"]["canal_in_mm"] < 0).all()                  # the canal takes water out of a saturated peat
    assert r["series"]["edge_in_mm"][0] == 0                         # no edge ring in this domain
    assert r["series"]["mean_depth_m"][-1] < 0                       # and the water table falls


def test_a_class_without_drawdown_is_not_fixed():
    k = small_khg()
    fixed, _, label = SIM.Boundary({"primary": None}, 0.3).heads(k)
    assert not fixed.any() and not label.any()


def test_parse_drawdown():
    assert parse_drawdown("0.6", 1.2) == {"primary": 0.6, "secondary": 0.6, "tertiary": 0.6}
    assert parse_drawdown("primary=1.0,tertiary=none", 1.2) == {"primary": 1.0, "secondary": 1.2, "tertiary": None}


def test_gate_passes_a_perfect_model_and_fails_noise():
    rng = np.random.default_rng(0)
    dist = rng.uniform(10, 3000, 200)
    obs = 40 + 10 * np.log1p(dist) + rng.normal(0, 30, 200)
    base = pd.DataFrame({"obs_cm": obs, "dist_m": dist, "flag": "", "group": "a"})
    assert FC.score(base.assign(sim_cm=obs))["gate"]["pass"]
    assert not FC.score(base.assign(sim_cm=rng.normal(70, 30, 200)))["gate"]["pass"]


def test_tebingtinggi_reader_treats_zero_as_missing_and_flags(tmp_path):
    cols = {"FID": [0, 1, 2], "POINT_X": [102.5] * 3, "POINT_Y": [1.0] * 3, "Air_Tanah": [0, 80, 300], "TebalGmbt1": [3.0, 3.0, 2.0],
            "HujanAkhir": ["27 Oktober 2015", "Tidak ada data", "17 Nopember 2005"], "Jns_Gmbt": ["hemik"] * 3,
            "Drainase_B": ["saluran tebuka"] * 3, "TupLah": ["hutan"] * 3, "Status": ["masyarakat"] * 3, "Surveyor": ["A", "B", "C"]}
    f = tmp_path / "s.csv"
    pd.DataFrame(cols).to_csv(f, index=False)
    t = FO.tebingtinggi2015(f)
    assert np.isnan(t.depth_cm[0]) and t.depth_cm[1] == 80
    assert list(t.flag) == ["", "", "deeper_than_peat"]
    assert list(t.date_from) == ["2015-10-27", "2015-10-24", "2015-10-24"]           # a 2005 typo falls back to the window start
    assert t.drainage[0] == "saluran terbuka"


def test_dekad_start_snaps_to_the_1st_11th_21st():
    from repeat_neraca.model import dekad_start
    T = pd.Timestamp
    assert dekad_start(T("2025-10-22")) == T("2025-10-21")
    assert dekad_start(T("2026-10-01"), up=True) == T("2026-10-01")
    assert dekad_start(T("2026-10-05"), up=True) == T("2026-10-11")
    assert dekad_start(T("2026-10-25"), up=True) == T("2026-11-01")
    assert dekad_start(T("2026-10-15"), up=True) == T("2026-10-21")


def test_et_stress_keeps_a_deep_water_table_up():
    k = small_khg(canal_col=0)
    k.canal["primary"][:] = False
    b = SIM.Boundary({"primary": None}, 0.3)
    n = 60
    P, ET = np.zeros(n), np.full(n, 0.006)
    base = SIM.run(k, P - ET, PeatTable.named("tropical-small"), b)
    held = SIM.run(k, P - ET, PeatTable.named("tropical-small"), b, rain_m_day=P, et_m_day=ET, et_stress=(-0.2, -0.6))
    assert held["series"]["mean_depth_m"][-1] > base["series"]["mean_depth_m"][-1]      # less ET once the water table is below -0.2 m
    assert held["series"]["et_share"][-1] < 1


def test_managed_land_gets_its_own_canal_level():
    k = small_khg()
    managed = np.zeros(k.shape, bool)
    managed[:4] = True
    fixed, head, _ = SIM.Boundary({"primary": 1.2}, 0.3, managed, {"primary": 0.4}).heads(k)
    canal = k.canal["primary"]
    assert np.allclose(head[canal & managed], 5.0 - 0.4) and np.allclose(head[canal & ~managed], 5.0 - 1.2)
    f2, h2, _ = SIM.Boundary({"primary": 1.2}, 0.3).heads(k)
    assert (f2 == fixed).all() and np.allclose(h2[canal], 5.0 - 1.2)


def test_drained_ismail_sy_matches_the_reported_values():
    t = PeatTable.named("drained-ismail-large")
    assert abs(t.sy(np.array([-0.01]))[0] - 0.3) < 0.01
    assert abs(t.sy(np.array([-1.5]))[0] - 0.1) < 0.01


def test_managed_land_is_held_at_its_target_and_the_supply_is_the_storage_it_took():
    k = small_khg()
    k.canal["primary"][:] = False
    target = np.full(k.shape, np.nan)
    target[:, :4] = 0.4
    table = PeatTable.named("tropical-small")
    n = 40
    r = SIM.run(k, np.full(n, -0.006), table, SIM.Boundary({"primary": None}, 0.3, managed_target=target))
    z = r["final_depth_m"]
    held = r["held"]
    assert np.allclose(z[held], -0.4, atol=1e-9)                         # never deeper than the target
    assert (z[~held & k.domain] < -0.4).all()                            # unmanaged land keeps drying
    assert np.nansum(r["series"]["managed_supply_m3"]) > 0
    one = np.interp(-0.4, table.zeta, table.storage) - np.interp(-0.41, table.zeta, table.storage)
    assert one > 0                                                       # storage rises towards the surface, so topping up costs water


def test_peat_base_stops_et_below_the_peat():
    k = small_khg()
    k.canal["primary"][:] = False
    k.peat_depth[:] = 0.3
    P, ET = np.zeros(60), np.full(60, 0.006)
    b = SIM.Boundary({"primary": None}, 0.3)
    free = SIM.run(k, P - ET, PeatTable.named("drained-ismail-large"), b, rain_m_day=P, et_m_day=ET)
    based = SIM.run(k, P - ET, PeatTable.named("drained-ismail-large"), b, rain_m_day=P, et_m_day=ET, peat_base=True)
    assert based["series"]["mean_depth_m"][-1] > free["series"]["mean_depth_m"][-1]
    assert based["series"]["mean_depth_m"][-1] > -0.6                    # stops close to the 0.3 m peat base


def test_supply_check_passes_within_a_ratio_or_a_small_absolute_difference():
    assert FC.supply_ok(244, 290) and FC.supply_ok(41, 7)          # ratio; wet year, 34 mm apart
    assert not FC.supply_ok(104, 7) and not FC.supply_ok(500, 200)


def test_unit_table_counts_open_and_managed_land_per_unit():
    from repeat_neraca.model import unit_table
    k = small_khg()
    k.canal["primary"][:] = False
    target = np.full(k.shape, np.nan)
    target[:, :4] = 0.4
    n = 120                                                               # long enough for the water table to reach the 0.4 m target
    r = SIM.run(k, np.full(n, -0.006), PeatTable.named("tropical-small"), SIM.Boundary({"primary": None}, 0.3, managed_target=target),
                season_days=np.ones(n, bool))
    open_cells = k.domain & ~r["fixed"] & ~r["held"]
    t = unit_table(k, r, open_cells, n)
    assert len(t) == 1 and t.unit_id[0] == "KHG"
    assert t.managed_km2[0] > 0 and t.open_km2[0] > 0 and t.managed_supply_mm[0] > 0
    assert 0 <= t.open_days_deeper_40cm[0] <= n


def test_a_block_reach_raises_the_canal_level_and_keeps_the_higher_one():
    k = small_khg()
    reach = np.full(k.shape, np.nan)
    reach[2:5, 4] = 0.3                                                   # block reach on the canal: water 0.3 m below the land
    fixed, head, _ = SIM.Boundary({"primary": 1.2}, 0.3, canal_override=reach).heads(k)
    assert np.allclose(head[2:5, 4], 5.0 - 0.3) and np.allclose(head[6:8, 4], 5.0 - 1.2)
    target = np.full(k.shape, np.nan)
    target[2:5, :] = 0.1
    _, head2, _ = SIM.Boundary({"primary": 1.2}, 0.3, managed_target=target, canal_override=reach).heads(k)
    assert np.allclose(head2[2:5, 4], 5.0 - 0.1)                         # a managed level above the block level is kept
