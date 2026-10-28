import numpy as np
import pytest
from scipy import ndimage

from repeat_neraca.testbed.forcing import make_forcing
from repeat_neraca.groundwater import PeatTable, solve
from repeat_neraca.testbed.khg import KHGConfig, LANDCOVER, generate

SMALL = KHGConfig(seed=3, size_m=6000.0, dx=30.0, primary_spacing=1600.0, n_blocks=8, n_gates=3, n_loggers=9)


@pytest.fixture(scope="module")
def khg():
    return generate(SMALL)


def test_same_seed_identical_and_other_seed_differs(khg):
    again = generate(SMALL)
    for name in ("surface", "peat_depth", "canal_class", "landcover", "domain"):
        assert np.array_equal(getattr(khg, name), getattr(again, name)), name
    assert khg.structures == again.structures and khg.loggers == again.loggers
    other = generate(KHGConfig(**{**SMALL.__dict__, "seed": 4}))
    assert not np.array_equal(khg.surface, other.surface)


def test_dome_is_convex_and_drains_outward(khg):
    s, dom = khg.surface, khg.domain
    iy, ix = np.unravel_index(np.argmax(np.where(dom, s, -np.inf)), s.shape)
    n = s.shape[0]
    assert abs(iy - n / 2) < 0.15 * n and abs(ix - n / 2) < 0.15 * n          # highest near the centre
    yy, xx = np.indices(s.shape)
    rr = np.hypot(yy - n / 2, xx - n / 2)
    inner = s[dom & (rr < 0.15 * n)].mean()
    mid = s[dom & (rr > 0.25 * n) & (rr < 0.3 * n)].mean()
    edge = s[khg.boundary].mean()
    assert inner > mid > edge
    gy, gx = np.gradient(s, SMALL.dx)
    slope = np.hypot(gy, gx)[dom & ~khg.boundary]
    assert np.percentile(slope, 95) < 0.004                                    # a few metres per few km


def test_boundary_ring_and_river_head(khg):
    assert khg.boundary.sum() > 0
    assert not (khg.boundary & ~khg.domain).any()
    # boundary is a closed ring: eroding the domain removes exactly the ring
    assert (khg.domain & ~ndimage.binary_erosion(khg.domain, structure=np.ones((3, 3)))).sum() == khg.boundary.sum()
    assert (khg.river_head[khg.boundary] < khg.surface[khg.boundary]).all()


def test_peat_depth_and_function_zone(khg):
    d = khg.domain
    assert khg.peat_depth[d].min() >= 0.3 and khg.peat_depth[d].max() <= 9.0
    lind = khg.function_zone == 1
    assert lind.any() and (khg.peat_depth[lind] >= 3.0).all()
    assert (khg.function_zone[~d] == 0).all()


def test_canals_connected_inside_domain_and_reach_the_river(khg):
    cm = khg.canal_class > 0
    assert not (cm & ~khg.domain).any()
    _, ncomp = ndimage.label(cm, structure=np.ones((3, 3)))
    assert ncomp == 1
    assert {p["class"] for p in khg.polylines} == {"primary", "secondary"}
    near_river = ndimage.binary_dilation(khg.boundary, iterations=4)
    assert (cm & near_river & (khg.canal_class == 1)).any()                    # primaries drain to the river
    assert khg.canals.n == cm.sum()


def test_structures_sit_on_canals_with_valid_attributes(khg):
    assert len([s for s in khg.structures if s["type"] == "block"]) >= 4
    assert len([s for s in khg.structures if s["type"] == "gate"]) >= 1
    for s in khg.structures:
        assert khg.canal_class[s["cell"]] > 0
        assert 0.0 < s["condition"] <= 1.0
        assert 2016 <= s["year_built"] <= 2022
        assert s["crest_elev_m"] == pytest.approx(khg.surface[s["cell"]] - SMALL.block_head)


def test_blocks_raise_canal_levels_upstream_only(khg):
    base = khg.canals.base_levels(khg.canal_drawdown)
    lv = khg.canals.levels(base, khg.block_levels())
    assert (lv[1:] >= base[1:] - 1e-12).all() and (lv[1:] > base[1:] + 1e-9).any()
    # raised levels stay below the local surface minus the block head
    assert (lv[1:] <= khg.canals.surface[1:] - SMALL.block_head + 1e-9).all()
    # a block affects only itself and cells upstream of it (higher surface)
    lab = next(iter(khg.block_levels()))
    one = khg.canals.levels(base, {lab: khg.block_levels()[lab]})
    changed = np.flatnonzero(one[1:] > base[1:] + 1e-12) + 1
    assert lab in changed or one[lab] == base[lab]
    assert (khg.canals.surface[changed] >= khg.canals.surface[lab] - 1e-9).all()


def test_landcover_classes_and_burn_history(khg):
    d = khg.domain
    present = set(np.unique(khg.landcover[d]))
    assert {1, 2, 3, 4, 5, 6, 7} <= present and 8 not in present
    assert (khg.burn_count[(khg.landcover == 4) & d] >= 1).all()
    assert (khg.burn_count[(khg.landcover != 4)] == 0).all()
    assert set(LANDCOVER) == set(range(1, 9))


def test_loggers_cover_distance_classes(khg):
    dist = np.array([l["dist_canal_m"] for l in khg.loggers])
    assert (dist < 50).sum() >= 2 and ((dist >= 50) & (dist < 300)).sum() >= 2 and (dist >= 300).sum() >= 2
    for l in khg.loggers:
        assert l["ground_elev_m"] == pytest.approx(khg.surface[l["cell"]])


def test_forcing_scenarios_order_dry_spells_and_are_reproducible():
    runs = {s: np.mean([make_forcing(i, s).longest_dry_run() for i in range(20)])
            for s in ("normal", "moderate_el_nino", "strong_el_nino")}
    assert runs["normal"] < runs["moderate_el_nino"] < runs["strong_el_nino"]
    a, b = make_forcing(5, "strong_el_nino"), make_forcing(5, "strong_el_nino")
    assert np.array_equal(a.rain_mm, b.rain_mm) and np.array_equal(a.et_mm, b.et_mm)
    assert 3.0 < make_forcing(1).et_mm.mean() < 5.0
    with pytest.raises(ValueError):
        make_forcing(1, "nope")


def test_truth_solver_runs_on_the_synthetic_khg_and_blocks_help(khg):
    table = PeatTable.urzainki2020()
    depth = np.maximum(khg.peat_depth, 2.0).ravel()
    sy_fn = table.sy
    trans = lambda zeta, cells: table.trans(zeta, depth[cells], 150.0)
    canal_cells = khg.canal_class > 0
    interior = khg.domain & ~khg.boundary

    def run(blocks):
        base = khg.canals.base_levels(khg.canal_drawdown)
        lv = khg.canals.to_raster(khg.canals.levels(base, blocks))
        fixed = khg.boundary | (canal_cells & interior)
        head = np.where(khg.boundary, khg.river_head, lv)
        return solve(khg.surface, khg.domain, SMALL.dx, fixed, head, khg.surface, [-0.003] * 3, sy_fn, trans)

    h0 = run({})
    h1 = run(khg.block_levels())
    peat = interior & ~canal_cells
    wtd0, wtd1 = (khg.surface - h0)[peat].mean(), (khg.surface - h1)[peat].mean()
    assert 0.0 < wtd0 < 0.5                       # centimetres to decimetres below the surface after 3 dry days
    assert wtd1 < wtd0                            # existing blocks keep the water table higher
