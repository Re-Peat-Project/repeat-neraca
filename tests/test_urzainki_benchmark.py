"""Siak benchmark of Urzainki et al. (2020). Needs the Siak rasters from LukeEcomod/blopti:
set WATERSHARE_SIAK_DATA to .../python3/data/Strat4 (skipped otherwise)."""
import os

import numpy as np
import pytest

pytest.importorskip("rasterio")
DATA = os.environ.get("WATERSHARE_SIAK_DATA")
pytestmark = pytest.mark.skipif(not DATA, reason="WATERSHARE_SIAK_DATA not set")

from repeat_neraca.testbed import reference_urzainki2020 as ref  # noqa: E402


@pytest.fixture(scope="module")
def siak():
    s = ref.Siak.load(DATA)
    s.k_adjust = 150.0          # x100 the original 1.5: realistic transmissivity, see the benchmark script
    return s


def test_canal_rule_reproduces_stored_canal_rise(siak):
    # concise_output_opti.txt in the blopti repository: CWL change 100.17 m (5 blocks), 206.57 m (10 blocks)
    assert siak.n_canals == 11311
    assert siak.run(ref.GA_5)["canal_rise_m"] == pytest.approx(100.17, abs=0.1)
    assert siak.run(ref.GA_10)["canal_rise_m"] == pytest.approx(206.57, abs=0.1)


def test_optimised_blocks_beat_rule_based_and_random(siak):
    base = siak.run([])["dry_volume_ha_m"]
    gain = lambda blocks: base - siak.run(blocks)["dry_volume_ha_m"]
    rng = np.random.default_rng(1)
    random10 = np.mean([gain(rng.integers(1, siak.n_canals, 10).tolist()) for _ in range(4)])
    assert gain(ref.GA_10) > 4 * random10             # paper: about 3 to 7 times the random improvement
    assert gain(ref.GA_10) > 3 * gain(ref.RULE_BASED_10)
    assert gain(ref.GA_10) > gain(ref.GA_5) > 0       # more blocks, more rewetting
