import math

import numpy as np
import pytest
from pydantic import ValidationError

from repeat_neraca.params import Param, Registry


@pytest.fixture(scope="module")
def reg():
    return Registry.load()


def test_loads_and_defaults_in_range(reg):
    assert len(reg) >= 40
    for name, p in reg.params.items():
        lo, hi = p.range
        assert lo <= reg[name] <= hi, name


def test_depth_convention_is_negative(reg):
    for name in ("target_wtd", "hazard_moderate", "hazard_high", "hazard_extreme", "gate_band_upper", "gate_band_lower"):
        assert reg[name] < 0, name
    assert reg["hazard_moderate"] > reg["hazard_high"] > reg["hazard_extreme"]
    assert reg["gate_band_lower"] < reg["gate_band_upper"]


def test_resolved_drift_values(reg):
    assert reg["l_inf_burnt"] == 60 and reg["l_inf_intact"] == 200
    assert reg["k_forest"] == 30 and reg["k_drained"] == 5
    assert reg["et0"] == 4.17
    assert reg.params["k_forest"].outer_range == (1, 1300)


def test_sy_decay_matches_methodology(reg):
    assert reg.sy_decay == pytest.approx(math.log(3) / 1.5, rel=1e-12)
    assert reg.sy_decay == pytest.approx(0.7324, abs=1e-3)


def test_param_validation_rejects_bad_specs():
    base = dict(name="x", unit="m", scope="global", sampling="uniform", source="s", confidence="low")
    with pytest.raises(ValidationError):
        Param(default=5, range=(0, 1), **base)                       # default outside range
    with pytest.raises(ValidationError):
        Param(default=0.5, range=(1, 0), **base)                     # inverted range
    with pytest.raises(ValidationError):
        Param(default=0.5, range=(0, 1), outer_range=(0.2, 2), **base)  # range not inside outer
    with pytest.raises(ValidationError):
        Param(default=0.5, range=(0, 1), **{**base, "sampling": "log-uniform"})  # log needs positive
    with pytest.raises(ValidationError):
        Param(default=2.5, range=(1, 4), integer=True, **base)       # non-integer default


def test_overrides_are_range_checked(reg):
    r2 = reg.with_overrides({"target_wtd": -0.3})
    assert r2["target_wtd"] == -0.3 and reg["target_wtd"] == -0.4   # original untouched
    with pytest.raises(ValueError):
        reg.with_overrides({"target_wtd": -0.9})
    with pytest.raises(KeyError):
        reg.with_overrides({"nope": 1})
    with pytest.raises(ValueError):
        reg.with_overrides({"decision_interval_days": 7.5})
    # an outer_range lets an edit go beyond the plausible range
    assert reg.with_overrides({"k_forest": 500})["k_forest"] == 500


def test_snapshot_is_stable_and_sensitive(reg):
    a, b = reg.snapshot(), Registry.load().snapshot()
    assert a == b
    assert a["sha256"] != reg.with_overrides({"et0": 4.0}).snapshot()["sha256"]
    assert list(a["values"]) == sorted(a["values"])


def test_sampling(reg):
    rng = np.random.default_rng(0)
    x = reg.sample("k_forest", 20000, rng)
    lo, hi = reg.params["k_forest"].range
    assert x.min() >= lo and x.max() <= hi
    # log-uniform: the median is near the geometric mean, far below the arithmetic mean
    assert np.median(x) == pytest.approx(math.sqrt(lo * hi), rel=0.1)
    xo = reg.sample("k_forest", 20000, np.random.default_rng(0), outer=True)
    assert xo.max() > hi
    assert (reg.sample("decision_interval_days", 5, rng) == 7).all()      # fixed
    ints = reg.sample("alloc_horizon", 5, rng)
    assert (ints == 3).all()
    # reproducible for a given seed
    assert np.array_equal(reg.sample("et0", 10, np.random.default_rng(1)), reg.sample("et0", 10, np.random.default_rng(1)))
