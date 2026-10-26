"""Parameter registry: load, validate, override, snapshot and sample.

The registry in ``src/repeat_neraca/parameters.yaml`` is the single source of numbers. Every run stores
``Registry.snapshot()`` so that results reproduce exactly.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Literal

import numpy as np
import yaml
from pydantic import BaseModel, ConfigDict, model_validator

Scope = Literal["global", "khg", "compartment", "reach", "block", "gate", "pump", "relay"]
Sampling = Literal["fixed", "uniform", "log-uniform"]
Confidence = Literal["regulation", "high", "medium", "low", "assumption"]

DEFAULT_PATH = Path(__file__).resolve().with_name("parameters.yaml")      # package data, so an installed package finds it


class Param(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    default: float
    range: tuple[float, float]
    outer_range: tuple[float, float] | None = None
    unit: str
    scope: Scope
    sampling: Sampling
    source: str
    confidence: Confidence
    integer: bool = False
    note: str | None = None

    @model_validator(mode="after")
    def _check(self) -> "Param":
        lo, hi = self.range
        if lo > hi:
            raise ValueError(f"{self.name}: range lower bound exceeds upper bound")
        if not lo <= self.default <= hi:
            raise ValueError(f"{self.name}: default {self.default} outside range {self.range}")
        if self.outer_range is not None:
            olo, ohi = self.outer_range
            if not (olo <= lo and hi <= ohi):
                raise ValueError(f"{self.name}: range {self.range} not inside outer_range {self.outer_range}")
        if self.sampling == "log-uniform" and lo <= 0:
            raise ValueError(f"{self.name}: log-uniform sampling needs a positive range")
        if self.integer and not (float(self.default).is_integer() and float(lo).is_integer() and float(hi).is_integer()):
            raise ValueError(f"{self.name}: integer parameter with non-integer default or range")
        return self

    @property
    def bounds(self) -> tuple[float, float]:
        """Bounds an edit must respect: the outer range if there is one, else the range."""
        return self.outer_range or self.range


class Registry:
    """An ordered set of parameters with effective values (defaults plus overrides)."""

    def __init__(self, params: dict[str, Param], version: int = 1, values: dict[str, float] | None = None):
        self.params = params
        self.version = version
        self.values = {k: p.default for k, p in params.items()}
        for k, v in (values or {}).items():
            self.values[k] = v

    # -- loading ------------------------------------------------------------------------------
    @classmethod
    def load(cls, path: str | Path = DEFAULT_PATH) -> "Registry":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        params = {name: Param(name=name, **spec) for name, spec in raw["parameters"].items()}
        return cls(params, version=int(raw.get("version", 1)))

    # -- access -------------------------------------------------------------------------------
    def __getitem__(self, name: str) -> float:
        try:
            return self.values[name]
        except KeyError:
            raise KeyError(f"unknown parameter {name!r}") from None

    def __contains__(self, name: str) -> bool:
        return name in self.params

    def __iter__(self):
        return iter(self.params)

    def __len__(self) -> int:
        return len(self.params)

    # -- overrides ----------------------------------------------------------------------------
    def with_overrides(self, overrides: dict[str, float]) -> "Registry":
        """Return a new registry with edited values; unknown names and out-of-bounds values raise."""
        values = dict(self.values)
        for name, value in overrides.items():
            if name not in self.params:
                raise KeyError(f"unknown parameter {name!r}")
            p = self.params[name]
            lo, hi = p.bounds
            if not lo <= value <= hi:
                raise ValueError(f"{name}: {value} outside allowed bounds [{lo}, {hi}]")
            if p.integer and not float(value).is_integer():
                raise ValueError(f"{name}: must be an integer")
            values[name] = value
        return Registry(self.params, self.version, values)

    # -- reproducibility ----------------------------------------------------------------------
    def snapshot(self) -> dict:
        """Effective values plus a SHA-256 over the values and the registry version."""
        values = {k: self.values[k] for k in sorted(self.values)}
        payload = json.dumps({"version": self.version, "values": values}, sort_keys=True)
        return {"version": self.version, "values": values,
                "sha256": hashlib.sha256(payload.encode()).hexdigest()}

    # -- sampling -----------------------------------------------------------------------------
    def sample(self, name: str, n: int, rng: np.random.Generator, outer: bool = False) -> np.ndarray:
        """Draw n values for Monte Carlo: fixed returns the effective value, others sample the range."""
        p = self.params[name]
        if p.sampling == "fixed":
            return np.full(n, self.values[name], dtype=float)
        lo, hi = p.outer_range if (outer and p.outer_range) else p.range
        if p.sampling == "uniform":
            x = rng.uniform(lo, hi, n)
        else:
            if lo <= 0:
                raise ValueError(f"{name}: log-uniform needs a positive range (got {lo})")
            x = np.exp(rng.uniform(math.log(lo), math.log(hi), n))
        return np.rint(x) if p.integer else x

    # -- derived quantities -------------------------------------------------------------------
    @property
    def sy_decay(self) -> float:
        """s2 in Sy(z) = s1 exp(s2 z) with z negative below ground: ln(s1 / Sy(1.5 m)) / 1.5."""
        s1, s15 = self.values["sy_surface"], self.values["sy_at_1p5m"]
        if not 0 < s15 < s1:
            raise ValueError("sy_at_1p5m must be positive and smaller than sy_surface")
        return math.log(s1 / s15) / 1.5
