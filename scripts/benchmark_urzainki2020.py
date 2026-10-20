"""Re-evaluate the stored block configurations of Urzainki et al. (2020) on the Siak data.

  python scripts/benchmark_urzainki2020.py --data path/to/blopti/python3/data/Strat4 [--random 10]

Prints the dry peat volume after 3 dry days as a percentage of the no-block case, next to the
values stored in the blopti repository (concise_output_opti.txt). The stored percentages come from
an older, unit-inconsistent version of the hydrology and are not reproduced in absolute terms;
the checks that hold are the canal rise (exact) and the ratios of improvement over random siting.
"""
import argparse
import time

import numpy as np

from repeat_neraca.testbed import reference_urzainki2020 as ref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="folder with DTM_metres_clip.tif, canals_clip.tif, Peattypedepth_clip.tif")
    ap.add_argument("--random", type=int, default=0, help="number of random 10-block draws to add")
    ap.add_argument("--k-adjust", type=float, default=150.0,
                    help="multiplier on the Paivanen-based transmissivity (original code: 1.5). 1.5 gives almost no block effect in 3 days; "
                         "150 (x100) is a realistic tropical regime and reproduces the paper's ratios")
    a = ap.parse_args()
    siak = ref.Siak.load(a.data)
    siak.k_adjust = a.k_adjust
    print(f"canal pixels: {siak.n_canals}, grid {siak.dem.shape}")
    t0 = time.time()
    base = siak.run([])
    print(f"no blocks: dry volume {base['dry_volume_ha_m']:.1f} ha m, mean WTD {base['mean_wtd_m']*100:.1f} cm "
          f"({time.time()-t0:.0f} s; stored original value 8255.1 ha m)")
    cases = {"GA_5": ref.GA_5, "GA_10": ref.GA_10, "rule-based_10": ref.RULE_BASED_10}
    rng = np.random.default_rng(0)
    for i in range(a.random):
        cases[f"random_10_{i}"] = rng.integers(1, siak.n_canals, 10).tolist()
    for name, blocks in cases.items():
        r = siak.run(blocks)
        pct = 100 * r["dry_volume_ha_m"] / base["dry_volume_ha_m"]
        paper = ref.PAPER_PERCENT.get(name)
        print(f"{name:>14}: {pct:6.2f} %  canal rise {r['canal_rise_m']:7.1f} m"
              + (f"   (stored original: {paper} %)" if paper else ""))


if __name__ == "__main__":
    main()
