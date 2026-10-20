#!/usr/bin/env python3
"""Does giving each concession its own canal water level make the water table predictable? (the idea of Taufik et al. 2019, Ambio 48:363)

  python -m repeat_neraca.bucket.canal_level --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml

Model, per station, in cm below the surface (z, positive down), daily:

    Sy dz/dt = (E - P) + (zc - z) / gamma           (P and E in cm/day)

Rain minus evaporation moves the water table; a drain (canal) pulls it towards the canal level zc with a resistance gamma (days).
zc is **per concession** (a constant: the level the concession holds its canals at); Sy and gamma are shared by all stations.
The concession is read from the SiTMAT station id (`concession/<code>:<station>`). P and E are the ERA5 forcing of the calibration window.

Two ways of leaving stations out, both scored out of fold on the observed water table:
  within a concession   one station is left out; zc of its concession is fitted on the other stations of that concession
                        (a concession with a monitored neighbour; compared with copying the neighbours' mean curve)
  new concession        a whole concession is left out; zc is the median of the other concessions (no management information)
and the same global baseline as the calibration (every station follows the mean observed curve of the training stations).
The ranking metric is the Spearman correlation across held-out stations of the simulated and observed peak (95th percentile) depth.

Writes neraca_canal_level.md in the output folder.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from repeat_common import grid as G
from .config import load_config
from . import calibrate as CAL
from repeat_common import forcing as FO
from .run import PRESET

log = logging.getLogger("prioritas.neraca")
SKIP = 14                                   # spin-up days not scored
SY = [0.1, 0.2, 0.3, 0.5]
GAMMA = [25, 50, 100, 200, 400, 800]        # days
ZC = np.arange(0.0, 122.0, 2.0)             # candidate constant canal levels, cm
ZC_SEASONAL = np.arange(0.0, 124.0, 4.0)    # candidate wet-season and dry-season levels, cm


def canal_series(dates: pd.DatetimeIndex, mode: str, dry_from_month: int = 6) -> tuple[np.ndarray, np.ndarray]:
    """(zc_t (T, K), combos (K, 2) = wet and dry level): `constant` has wet = dry; `seasonal` every pair, the level changing on the first day of `dry_from_month`."""
    if mode == "constant":
        combos = np.array([(z, z) for z in ZC])
    else:
        combos = np.array([(w, d) for w in ZC_SEASONAL for d in ZC_SEASONAL])
    dry = (dates.month >= dry_from_month)[:, None]
    return np.where(dry, combos[None, :, 1], combos[None, :, 0]).astype("float64"), combos


def simulate(net_cm: np.ndarray, sy: float, gamma: float, zc_t: np.ndarray) -> np.ndarray:
    """Water table depth (T, S, K) for E - P in cm/day (T, S) and K canal-level series zc_t (T, K); starts at the canal level."""
    T, S = net_cm.shape
    z = np.repeat(zc_t[0][None, :], S, axis=0).astype("float64")             # (S, K)
    out = np.empty((T, S, zc_t.shape[1]), "float32")
    for t in range(T):
        z = z + (net_cm[t][:, None] + (zc_t[t][None, :] - z) / gamma) / sy
        z = np.maximum(z, 0.0)                                              # no standing water above the surface
        out[t] = z
    return out


def build_table(net_cm: np.ndarray, obs: np.ndarray, zc_t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """sse[i_sy, i_gamma, k, station] and n[station] over the scored days (after the spin-up); k indexes the canal-level series."""
    ok = np.isfinite(obs)
    ok[:SKIP] = False
    n = ok.sum(axis=0)
    sse = np.zeros((len(SY), len(GAMMA), zc_t.shape[1], obs.shape[1]))
    for i, sy in enumerate(SY):
        for j, g in enumerate(GAMMA):
            sim = simulate(net_cm, sy, g, zc_t)                              # (T, S, K)
            d = np.where(ok[:, :, None], sim - obs[:, :, None], 0.0)
            sse[i, j] = np.moveaxis((d ** 2).sum(axis=0), -1, 0)             # (K, S)
    return sse, n


def _best(sse, n, members):
    """Mean squared error of the best zc of one concession for every (sy, gamma): (nsy, ngamma) and the index of that zc."""
    m = np.asarray(members)
    tot = sse[:, :, :, m].sum(axis=-1) / max(n[m].sum(), 1)                  # (nsy, ng, nzc)
    k = tot.argmin(axis=-1)
    return np.take_along_axis(tot, k[..., None], axis=-1)[..., 0], k


def fit_global(sse, n, groups: dict, exclude: int | None = None, drop_group: str | None = None):
    """(sy, gamma) minimising the pooled error when every concession gets its best zc; returns indices and the zc index per concession."""
    tot = np.zeros((len(SY), len(GAMMA)))
    w = 0
    best = {}
    for g, members in groups.items():
        if g == drop_group:
            continue
        m = [s for s in members if s != exclude]
        if not m:
            continue
        e, k = _best(sse, n, m)
        tot += e * n[m].sum()
        w += n[m].sum()
        best[g] = k
    tot /= max(w, 1)
    i, j = np.unravel_index(tot.argmin(), tot.shape)
    return int(i), int(j), {g: int(k[i, j]) for g, k in best.items()}


def predict(net_cm, i, j, zi_per_station, zc_t):
    """Simulated depth (T, S) for each station with its own canal-level series index."""
    sy, g = SY[i], GAMMA[j]
    out = np.full(net_cm.shape, np.nan)
    for zi in sorted(set(zi_per_station)):
        sel = np.flatnonzero(np.asarray(zi_per_station) == zi)
        out[:, sel] = simulate(net_cm[:, sel], sy, g, zc_t[:, [zi]])[:, :, 0]
    return out


def _median_series(combos: np.ndarray, ks: list) -> int:
    """The canal-level series (index) closest to the median wet and dry levels of the given ones."""
    med = np.median(combos[ks], axis=0)
    return int(np.abs(combos - med[None, :]).sum(axis=1).argmin())


def _rmse(sim, obs):
    ok = np.isfinite(obs) & np.isfinite(sim)
    ok[:SKIP] = False
    return float(np.sqrt(np.mean((sim[ok] - obs[ok]) ** 2)))


def _rho(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[ok], b[ok]).correlation) if ok.sum() >= 8 else float("nan")


def evaluate(net_cm, obs, conc: np.ndarray, in_season: np.ndarray, zc_t: np.ndarray, combos: np.ndarray, min_group: int = 3) -> dict:
    sse, n = build_table(net_cm, obs, zc_t)
    groups = {c: list(np.flatnonzero(conc == c)) for c in sorted(set(conc))}
    big = [c for c, m in groups.items() if len(m) >= min_group]
    S = obs.shape[1]
    simA, mateA, baseA = np.full(obs.shape, np.nan), np.full(obs.shape, np.nan), np.full(obs.shape, np.nan)
    for s in range(S):                                                         # A: within a concession, one station left out
        c = conc[s]
        if c not in big:
            continue
        i, j, zi = fit_global(sse, n, groups, exclude=s)
        simA[:, s] = predict(net_cm[:, [s]], i, j, [zi[c]], zc_t)[:, 0]
        mates = [m for m in groups[c] if m != s]
        mateA[:, s] = np.nanmean(obs[:, mates], axis=1)
        others = [m for m in range(S) if m != s]
        baseA[:, s] = np.nanmean(obs[:, others], axis=1)
    simB, baseB = np.full(obs.shape, np.nan), np.full(obs.shape, np.nan)
    zc_fitted = {}
    for c in groups:                                                           # B: a new concession, zc unknown
        i, j, zi = fit_global(sse, n, groups, drop_group=c)
        zc_med = _median_series(combos, list(zi.values()))
        sel = groups[c]
        simB[:, sel] = predict(net_cm[:, sel], i, j, [zc_med] * len(sel), zc_t)
        baseB[:, sel] = np.nanmean(obs[:, [m for m in range(S) if m not in sel]], axis=1)[:, None]
    i, j, zi = fit_global(sse, n, groups)
    zc_fitted = {c: tuple(float(v) for v in combos[k]) for c, k in zi.items()}
    peak_obs, _ = CAL.season_stats(np.where(np.isfinite(obs), obs, np.nan), in_season)
    inA = np.isfinite(simA).any(axis=0)
    res = {"n_stations": S, "n_concessions": len(groups), "concessions_with_3plus": len(big), "stations_in_big": int(inA.sum()),
           "sy": SY[i], "gamma": GAMMA[j], "zc": zc_fitted}
    res["A"] = {"rmse_model": _rmse(simA[:, inA], obs[:, inA]), "rmse_mates": _rmse(mateA[:, inA], obs[:, inA]), "rmse_global": _rmse(baseA[:, inA], obs[:, inA]),
                "rho_peak": _rho(CAL.season_stats(simA[:, inA], in_season)[0], peak_obs[inA]),
                "rho_peak_mates": _rho(CAL.season_stats(mateA[:, inA], in_season)[0], peak_obs[inA])}
    res["B"] = {"rmse_model": _rmse(simB, obs), "rmse_global": _rmse(baseB, obs), "rho_peak": _rho(CAL.season_stats(simB, in_season)[0], peak_obs)}
    # the same schemes inside each concession: does the model rank stations of one concession?
    within = []
    for c in big:
        m = groups[c]
        within.append((c, len(m), _rho(CAL.season_stats(simA[:, m], in_season)[0], peak_obs[m])))
    res["within"] = within
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    for noisy in ("azure", "rasterio._env", "rasterio._err", "fsspec", "pyogrio._io"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    import geopandas as gpd
    cfg = load_config(a.config, PRESET, "neraca")
    nc = cfg["neraca"]
    out = Path(cfg["out"])
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    idf = cfg["khg_id_field"]
    kid = str(khg[idf].iloc[0]) if idf in khg.columns else "KHG01"
    geom = khg.geometry.union_all()
    grid = G.make_grid(geom, float(cfg["grid_res_m"]))
    cal = nc["calibration"]
    era5 = {**cfg["sources"]["era5"]}
    f = FO.forcing_for(grid, era5, cal["start"], cal["end"], Path(cfg["cache_dir"]) / kid / "neraca", nc["tz_hours"], int(era5.get("evap_stride", 3)), **nc["forcing"])
    end = FO.last_valid(f)
    keep = f["dates"] <= end
    dates = f["dates"][keep]
    P, E = f["P"][keep], f["E"][keep]
    Z, meta = CAL.load_stations(cfg, geom, dates[0], dates[-1])
    Z = Z.reindex(dates)
    r, c = FO.cell_of(meta.lon.values, meta.lat.values, f["transform"], P.shape[1:])
    net_cm = (E[:, r, c] - P[:, r, c]).astype("float64") / 10.0
    obs = Z.values.astype("float64")
    conc = pd.Series(meta.station_id).str.split(":").str[0].str.replace("concession/", "", regex=False).values
    in_season = np.isin(dates.month, nc["dry_months"])
    head = [f"# Canal level per concession, KHG {kid}", "",
            "Model: `Sy dz/dt = (E - P) + (zc - z)/gamma` per station, one canal level zc per concession (method and the two ways of leaving stations out in `repeat_neraca/bucket/canal_level.py`). "
            "`constant`: one level for the whole season. `seasonal`: one level for April-May and one for June-October (the structure of Taufik et al. 2019, who set the canal level by season). "
            "Scores are out of fold on the observed water table; the calibration baseline is the mean observed curve of the training stations.", ""]
    L = list(head)
    for mode in ("constant", "seasonal"):
        zc_t, combos = canal_series(dates, mode)
        res = evaluate(net_cm, obs, conc, in_season, zc_t, combos)
        A, B = res["A"], res["B"]
        fmt = (lambda v: f"{v[0]:.0f}") if mode == "constant" else (lambda v: f"{v[0]:.0f} / {v[1]:.0f}")
        L += [f"## {mode.capitalize()} canal level", "",
              f"{res['n_stations']} stations in {res['n_concessions']} concessions ({res['concessions_with_3plus']} with 3 or more stations, {res['stations_in_big']} stations); "
              f"{dates[0].date()} to {dates[-1].date()}. Fitted on all stations: Sy {res['sy']}, gamma {res['gamma']} days. Canal level per concession (cm" + ("" if mode == "constant" else ", April-May / June-October") + "): "
              + ", ".join(f"{k} {fmt(v)}" for k, v in res["zc"].items()) + ".", "",
              "**Within a concession** (one station left out; the canal level is fitted on the other stations of its concession)", "",
              "| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |", "|---|---|---|",
              f"| canal-level model | {A['rmse_model']:.1f} | {A['rho_peak']:.2f} |",
              f"| mean curve of the other stations of the same concession | {A['rmse_mates']:.1f} | {A['rho_peak_mates']:.2f} |",
              f"| mean curve of all other stations (the calibration baseline) | {A['rmse_global']:.1f} | n/a |", "",
              "**New concession** (whole concession left out; canal level = median of the others)", "",
              "| predictor | out-of-fold RMSE (cm) | Spearman of peak depth across stations |", "|---|---|---|",
              f"| canal-level model | {B['rmse_model']:.1f} | {B['rho_peak']:.2f} |",
              f"| mean curve of the stations outside the concession (the calibration baseline) | {B['rmse_global']:.1f} | n/a |", "",
              "**Ranking stations inside one concession** (Spearman of simulated and observed peak depth; needs 8 or more stations to mean anything)", "",
              "| concession | stations | rho |", "|---|---|---|"] + [f"| {c} | {k} | {v:.2f} |" for c, k, v in res["within"] if k >= 8] + [""]
    text = "\n".join(L) + "\n"
    (out / "neraca_canal_level.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
