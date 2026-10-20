"""Synthetic dry-season daily forcing: rainfall (two-state Markov chain) and reference ET."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# probability a dry day is followed by a wet day, and mean wet-day depth (mm), by climate year
SCENARIOS = {
    "normal": (0.35, 12.0),
    "moderate_el_nino": (0.20, 9.0),
    "strong_el_nino": (0.10, 7.0),
}


@dataclass(frozen=True)
class Forcing:
    start: str                  # ISO date of day 0
    rain_mm: np.ndarray         # (days,)
    et_mm: np.ndarray           # (days,)

    @property
    def net_m(self) -> np.ndarray:
        """Net recharge, precipitation minus ET, in m/day."""
        return (self.rain_mm - self.et_mm) * 1e-3

    def longest_dry_run(self, threshold_mm: float = 1.0) -> int:
        best = run = 0
        for r in self.rain_mm:
            run = run + 1 if r < threshold_mm else 0
            best = max(best, run)
        return best


def make_forcing(seed: int, scenario: str = "normal", days: int = 180, start: str = "2015-06-01",
                 et0: float = 4.17) -> Forcing:
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario {scenario!r}; choose from {sorted(SCENARIOS)}")
    p_dw, mean_depth = SCENARIOS[scenario]
    p_ww = 0.55                                         # a wet day is followed by another wet day
    rng = np.random.default_rng(np.random.SeedSequence([seed, 7919]))
    wet = False
    rain = np.zeros(days)
    for d in range(days):
        wet = rng.random() < (p_ww if wet else p_dw)
        if wet:
            rain[d] = rng.exponential(mean_depth)
    t = np.arange(days)
    et = et0 + 0.3 * np.sin(2 * np.pi * t / 365.0) + rng.normal(0.0, 0.2, days)
    return Forcing(start, rain, np.clip(et, 2.5, 6.0))
