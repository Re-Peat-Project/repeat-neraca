"""Managed land outside the licences, from ForTy 2020: area per KHG and the surroundings of the water-table stations.
Config and reading rules: config/forest_type_managed_check.yaml (written before any result).

  python scripts/check_forest_type_managed.py config/forest_type_managed_check.yaml       # needs REPEAT_DATA, REPEAT_KHG

Per KHG: ForTy argmax class (Other land = 250 - sum of the five probability bands) inside the KHG boundary
(00_inputs/khg.gpkg), split by licence (00_inputs/national/izin_usaha_2025.gpkg; managed = repeat_neraca.model.MANAGED_LICENCES).
Per station of the given model run: class shares within each buffer, with the run's observed and simulated mean depth
and dry-season drawdown (station_scores.csv). Writes docs/reports/forest_type_managed.md and .csv.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import yaml
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds

from repeat_neraca.model import MANAGED_LICENCES

CLASSES = ["primary", "nat_regen", "planted", "plantation", "tree_crop", "other"]
HERE = Path(__file__).resolve().parents[1]


def argmax_class(F, window=None):
    p = F.read(window=window).astype("int16")
    nod = (p == 255).any(axis=0)
    other = (250 - p.sum(axis=0, dtype="int16")).astype("int16")
    cls = np.argmax(np.concatenate([p, other[None]], axis=0), axis=0).astype("int8")
    cls[nod] = -1
    return cls


def strip_counts(F, w, geoms_by_zone, strip=1500):
    """Cell counts per zone and class over window w, read in row strips (a 10 m KHG grid does not fit in memory)."""
    from rasterio.windows import Window
    counts = {z: np.zeros(len(CLASSES), np.int64) for z in geoms_by_zone}
    for r0 in range(0, int(w.height), strip):
        sw = Window(w.col_off, w.row_off + r0, w.width, min(strip, int(w.height) - r0))
        cls = argmax_class(F, sw)
        tf = F.window_transform(sw)
        masks = {}
        for z, (inc, exc) in geoms_by_zone.items():
            m = geometry_mask(inc, cls.shape, tf, invert=True) if inc else np.zeros(cls.shape, bool)
            for e in exc:
                m &= ~(geometry_mask(e, cls.shape, tf, invert=True) if e else np.zeros(cls.shape, bool))
            counts[z] += np.bincount(cls[m & (cls >= 0)], minlength=len(CLASSES))[:len(CLASSES)]
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(open(a.config, encoding="utf-8"))
    data, kroot = Path(os.environ["REPEAT_DATA"]), Path(os.environ["REPEAT_KHG"])
    area_rows, st_rows = [], []
    for k in cfg["khg"]:
        kf = kroot / k["folder"]
        slug = "_".join(w.capitalize() for w in k["folder"].split("_", 1)[1].split("_"))
        fp = data / cfg["forty"].format(slug=slug)
        with rasterio.open(fp) as F:
            khg = gpd.read_file(kf / "00_inputs" / "khg.gpkg").to_crs(F.crs).union_all()
            lic = gpd.read_file(kf / "00_inputs" / "national" / "izin_usaha_2025.gpkg").to_crs(F.crs)
            w = from_bounds(*khg.bounds, F.transform).round_offsets().round_lengths()
            man = lic[lic["IZIN_USAHA"].isin(MANAGED_LICENCES)]
            # clip licences to the KHG first, so each strip rasterises only small polygons
            man_g = [g for g in man.geometry.intersection(khg) if not g.is_empty]
            lic_g = [g for g in lic.geometry.intersection(khg) if not g.is_empty]
            cell_ha = abs(F.res[0] * F.res[1]) / 1e4
            zdef = {"managed licence": (man_g, []), "other licence": (lic_g, [man_g]), "no licence": ([khg], [lic_g])}
            counts = strip_counts(F, w, zdef)
            tot = float(sum(c.sum() for c in counts.values())) * cell_ha
            for zn, cnt in counts.items():
                for i, c in enumerate(CLASSES):
                    ha = float(cnt[i]) * cell_ha
                    area_rows.append({"khg": k["name"], "zone": zn, "class": c, "ha": round(ha), "pct_of_khg": round(100 * ha / tot, 2)})
            # stations
            if k.get("run"):
                run = kf / "03_neraca" / k["run"]
                sc = pd.read_csv(run / "station_scores.csv")
                xy = pd.read_csv(kf / "03_neraca" / "inputs" / "model" / "stations.csv")
                sc = sc.merge(xy, on="station_id", how="left")
                g = gpd.GeoDataFrame(sc, geometry=gpd.points_from_xy(sc.lon, sc.lat), crs=4326).to_crs(F.crs)
                for _, s in g.iterrows():
                    row = {"khg": k["name"], "station_id": s.station_id, "group": s.group, "managed_in_model": s.managed,
                           "flag": "" if pd.isna(s.flag) else s.flag, "obs_cm": s.obs_cm, "sim_cm": s.sim_cm,
                           "sim_minus_obs_cm": round(s.sim_cm - s.obs_cm, 2), "obs_drawdown_cm": s.obs_drawdown_cm,
                           "sim_drawdown_cm": s.sim_drawdown_cm}
                    for b in cfg["station_buffer_m"]:
                        buf = s.geometry.buffer(b)
                        bw = from_bounds(*buf.bounds, F.transform).round_offsets().round_lengths()
                        c2 = argmax_class(F, bw)
                        mm = geometry_mask([buf], c2.shape, F.window_transform(bw), invert=True) & (c2 >= 0)
                        for i, c in enumerate(CLASSES):
                            row[f"{c}_{b}m"] = round(float((c2[mm] == i).mean()), 2) if mm.any() else np.nan
                        row[f"managed_share_{b}m"] = round(sum(row[f"{c}_{b}m"] for c in cfg["managed_classes"]), 2)
                    st_rows.append(row)
    A, S = pd.DataFrame(area_rows), pd.DataFrame(st_rows)
    rep = HERE / "docs" / "reports"
    A.to_csv(rep / "forest_type_managed_area.csv", index=False)
    S.to_csv(rep / "forest_type_managed_stations.csv", index=False)

    L = ["# Managed land outside the licences (ForTy 2020)", "",
         "Generated by `scripts/check_forest_type_managed.py config/forest_type_managed_check.yaml`; do not edit. "
         "ForTy 2020 v1 argmax class at 10 m; managed licences = " + ", ".join(MANAGED_LICENCES) + ". Share of the KHG area (%).", ""]
    mc = cfg["managed_classes"]
    for kn in A.khg.unique():
        x = A[A.khg == kn].pivot_table(index="class", columns="zone", values="pct_of_khg", aggfunc="sum").reindex(CLASSES)
        x = x[[c for c in ["managed licence", "other licence", "no licence"] if c in x.columns]]
        L += [f"## {kn}", "", "| ForTy class | " + " | ".join(x.columns) + " |", "|---|" + "---|" * len(x.columns)]
        L += [f"| {c} | " + " | ".join(f"{v:.1f}" for v in r.values) + " |" for c, r in x.iterrows()]
        un = float(x.loc[mc, "no licence"].sum() + (x.loc[mc, "other licence"].sum() if "other licence" in x else 0))
        L += ["", f"Tree crops and plantation outside managed licences: **{un:.1f}% of the KHG** "
                  f"({'above' if un > 10 else 'not above'} the 10% reading threshold).", ""]
    if len(S):
        b = 250
        L += [f"## Stations: ForTy surroundings within {b} m and the model run", "",
              "| station | group | in model as managed | flag | tree crops + plantation | primary + regenerating | obs depth (cm) | sim - obs (cm) | obs / sim drawdown (cm) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for _, r in S.sort_values(["group", f"managed_share_{b}m"]).iterrows():
            L.append(f"| {r.station_id.split('/')[-1]} | {r.group} | {'yes' if r.managed_in_model else 'no'} | {r.flag} | "
                     f"{r[f'managed_share_{b}m']:.2f} | {r[f'primary_{b}m'] + r[f'nat_regen_{b}m']:.2f} | {r.obs_cm:.1f} | "
                     f"{r.sim_minus_obs_cm:+.1f} | {r.obs_drawdown_cm:.1f} / {r.sim_drawdown_cm:.1f} |")
        c = S[S.group == "community"]
        hi, lo = c[c[f"managed_share_{b}m"] >= 0.5], c[c[f"managed_share_{b}m"] < 0.5]
        L += ["", f"Community stations with at least half tree crops or plantation within {b} m: {len(hi)}, median sim - obs "
              f"{hi.sim_minus_obs_cm.median():+.1f} cm; the others: {len(lo)}, median {lo.sim_minus_obs_cm.median():+.1f} cm."]
        if len(hi) and len(lo):
            d = hi.sim_minus_obs_cm.median() - lo.sim_minus_obs_cm.median()
            L.append(f"Difference {d:+.1f} cm: {'supports' if d > 10 else 'does not support'} the reading rule (more than 10 cm). "
                     "Descriptive only; too few stations for a test.")
        L.append("")
    (rep / "forest_type_managed.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", rep / "forest_type_managed.md")


if __name__ == "__main__":
    main()
