#!/usr/bin/env python3
"""Does a Sentinel-1 anomaly predict how a station's water table moves in time, for stations left out of the fit?

  python -m repeat_neraca.bucket.radar_temporal --config ../re-peat/sites/kampar_gaung/neraca_experiments.yaml

Needs neraca_s1_series.csv and neraca_stations.csv in the output folder (written by `repeat_neraca.bucket.sentinel1` and
`repeat_neraca.bucket.run`). The question is about timing, not level: every station's own mean is removed from the observed depth, so
what is predicted is how much deeper or shallower than usual the water table is on a radar date.

  baseline   the mean anomaly of the training stations on that date (what the neraca air baseline uses)
  radar      baseline + b * (VV anomaly of the station on that date), b fitted on the training stations
  radar only b * (VV anomaly), without the date mean

Stations are left out in groups, by spatial block (as the neraca air calibration) and by concession (a new concession is
the hard case). Writes neraca_radar_temporal.md in the output folder.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .config import load_config
from . import calibrate as CAL
from .run import PRESET

log = logging.getLogger("prioritas.neraca")


def pairs(s1: pd.DataFrame, Z: pd.DataFrame, st: pd.DataFrame) -> pd.DataFrame:
    """One row per station and radar date with the observed depth anomaly (cm, positive = deeper) and the VV / VH anomalies (dB)."""
    s1 = s1.copy()
    for c in ("vv_db", "vh_db"):
        s1[c.replace("_db", "_anom")] = s1[c] - s1.groupby(["station_id", "orbit"])[c].transform("mean")
    z = Z.stack().dropna().rename("z").reset_index()
    z.columns = ["date", "station_id", "z"]
    m = s1.merge(z, on=["date", "station_id"])
    m["z_anom"] = m.z - m.groupby("station_id").z.transform("mean")
    m = m.merge(st[["station_id", "block"]], on="station_id", how="left")
    m["concession"] = m.station_id.str.split(":").str[0].str.replace("concession/", "", regex=False)
    return m


def _fit_b(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    A = np.c_[x]
    return np.linalg.lstsq(A, y, rcond=None)[0]


def cross_validate(m: pd.DataFrame, group: str) -> pd.DataFrame:
    """Leave-one-group-out predictions of z_anom: baseline, baseline + radar, radar only."""
    m = m.dropna(subset=[group]).reset_index(drop=True)
    pred = {k: np.full(len(m), np.nan) for k in ("baseline", "baseline + radar VV", "baseline + radar VV, VH", "radar VV only")}
    for g in sorted(m[group].unique()):
        te = (m[group] == g).values
        tr = ~te
        curve = m[tr].groupby("date").z_anom.mean()                       # mean anomaly curve of the training stations
        base_tr = m.loc[tr, "date"].map(curve).values
        base_te = m.loc[te, "date"].map(curve).fillna(curve.mean()).values
        pred["baseline"][te] = base_te
        ytr = m.loc[tr, "z_anom"].values
        b = _fit_b(m.loc[tr, ["vv_anom"]].values, ytr - base_tr)
        pred["baseline + radar VV"][te] = base_te + m.loc[te, ["vv_anom"]].values @ b
        b2 = _fit_b(m.loc[tr, ["vv_anom", "vh_anom"]].values, ytr - base_tr)
        pred["baseline + radar VV, VH"][te] = base_te + m.loc[te, ["vv_anom", "vh_anom"]].values @ b2
        b3 = _fit_b(m.loc[tr, ["vv_anom"]].values, ytr)
        pred["radar VV only"][te] = m.loc[te, ["vv_anom"]].values @ b3
    rows = []
    y = m.z_anom.values
    for k, p in pred.items():
        ok = np.isfinite(p)
        per = [float(spearmanr(d.z_anom, p[d.index]).correlation) for _, d in m[ok].groupby("station_id") if len(d) >= 8 and np.nanstd(p[d.index]) > 0]
        rows.append({"model": k, "rmse_cm": float(np.sqrt(np.mean((y[ok] - p[ok]) ** 2))),
                     "pooled_r": float(np.corrcoef(y[ok], p[ok])[0, 1]) if np.nanstd(p[ok]) > 0 else float("nan"),
                     "median_station_r": float(np.median(per)) if per else float("nan")})
    out = pd.DataFrame(rows)
    out["no_change_rmse_cm"] = float(np.sqrt(np.mean(y ** 2)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    import geopandas as gpd
    cfg = load_config(a.config, PRESET, "neraca")
    out = Path(cfg["out"])
    st = pd.read_csv(out / "neraca_stations.csv")
    s1 = pd.read_csv(out / "neraca_s1_series.csv", parse_dates=["date"])
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    cal = cfg["neraca"]["calibration"]
    Z, _ = CAL.load_stations(cfg, khg.geometry.union_all(), cal["start"], cal["end"])
    m = pairs(s1, Z, st)
    lines = [f"# Radar as a timing predictor ({m.station_id.nunique()} stations, {len(m)} station-dates)", "",
             "Target: the observed depth anomaly (cm; the station's own mean removed; positive = deeper than usual) on each Sentinel-1 date. "
             "Stations are left out in whole groups. `no change` is the error of predicting 0 (the station's usual level).", ""]
    for group, label in (("block", "spatial block"), ("concession", "concession")):
        r = cross_validate(m, group)
        lines += [f"## Left out by {label}", "", f"No-change RMSE {r.no_change_rmse_cm.iloc[0]:.1f} cm.", "",
                  "| model | out-of-fold RMSE (cm) | pooled r | median per-station r |", "|---|---|---|---|"]
        lines += [f"| {x.model} | {x.rmse_cm:.2f} | {x.pooled_r:.2f} | {x.median_station_r:.2f} |" for x in r.itertuples()]
        lines.append("")
    text = "\n".join(lines)
    (out / "neraca_radar_temporal.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
