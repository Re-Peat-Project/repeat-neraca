"""Map of the modelled water table from one groundwater-model run.

python scripts/plot_watertable_map.py --run <run folder> [--out <png>]

Reads the run's rasters (depth in cm below the surface), the KHG boundary and canals from
the KHG's 00_inputs, and writes watertable_map.png into the run folder. Managed land is
shown grey: its level is imposed (the managed target), not simulated.
"""
import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import Normalize
from rasterio.plot import plotting_extent


def read(run, name):
    with rasterio.open(run / f"{name}.tif") as r:
        return r.read(1, masked=True), plotting_extent(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--note", type=Path, help="text file: known limitations, printed under the maps")
    a = ap.parse_args()
    run = a.run
    cfg = json.loads((run / "run_config.json").read_text())
    inputs = Path(cfg["inputs"]["khg"]).parent
    khg = gpd.read_file(inputs / "khg.gpkg")
    canals = gpd.read_file(inputs / "canals.gpkg")

    st = None
    sc_path, st_path = run / "station_scores.csv", Path(cfg["inputs"]["inputs_dir"]).parent / "model" / "stations.csv"
    if sc_path.exists() and st_path.exists():
        sc, xy = pd.read_csv(sc_path), pd.read_csv(st_path)
        st = sc.merge(xy[["station_id", "lon", "lat"]], on="station_id")
        st = gpd.GeoDataFrame(st, geometry=gpd.points_from_xy(st.lon, st.lat), crs=4326)

    cap = cfg.get("supply_cap")
    if cap:                                                 # a number, `deficit` or `climate`: the value used is in the run config
        cap = f"{cfg['supply_cap_mm']:.0f}"
    season = cfg["season"]
    mean, ext = read(run, "model_season_mean_depth")
    with rasterio.open(run / "model_season_mean_depth.tif") as r:
        crs = r.crs
    khg = khg.to_crs(crs)
    end, _ = read(run, "model_depth_end")
    days, _ = read(run, "model_season_days_deeper_40cm")
    managed, _ = read(run, "model_managed_target")
    n_days = int(np.nanmax(days)) if days.count() else 0
    # days raster counts open land only; its season length is in the report
    panels = [
        (mean, "Season mean depth (cm)", "viridis_r", Normalize(0, 80)),
        (end, f"Depth on {cfg['end']} (cm)", "viridis_r", Normalize(0, 80)),
        (days, "Days deeper than 40 cm (open land only)", "magma_r", Normalize(0, max(n_days, 1))),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5), constrained_layout=True)
    fig.get_layout_engine().set(rect=(0, 0.14, 1, 0.86)) if a.note else None
    for ax, (arr, title, cmap, norm) in zip(axes, panels):
        im = ax.imshow(arr, extent=ext, cmap=cmap, norm=norm, interpolation="nearest")
        mm = ~np.ma.getmaskarray(managed)
        ax.contour(mm.astype(float), levels=[0.5], extent=ext, origin="upper", colors="black", linewidths=0.5, linestyles="--")   # managed land: outline only
        canals.to_crs(crs).plot(ax=ax, color="white", linewidth=0.25, alpha=0.6)
        khg.boundary.plot(ax=ax, color="black", linewidth=0.8)
        if st is not None and ax is axes[0]:                 # observed mean level over each station's record, same colour scale as the model
            pts = st.to_crs(crs)
            for kind, mk in (("community", "o"), ("concession", "^")):
                q = pts[(pts.group == "community") == (kind == "community")]
                ax.scatter(q.geometry.x, q.geometry.y, c=q.obs_cm, cmap=cmap, norm=norm, marker=mk, s=38,
                           edgecolor="black", linewidth=0.8, zorder=5, label=f"{kind} station, observed (mean of record)")
            ax.legend(loc="lower left", bbox_to_anchor=(-0.05, -0.08), fontsize=8, frameon=False)
        ax.set_title(title, loc="left")
        ax.set_axis_off()
        fig.colorbar(im, ax=ax, shrink=0.6, pad=0.01)
    fig.suptitle(
        f"{cfg['khg']}, {cfg['dem']} DTM, {cfg['res_m']:.0f} m, {cfg['start']} to {cfg['end']}; " +
        (f"season {season}. Dashed line: managed land, topped up to {cfg['managed_target']} m with at most {cap} mm of supply" if cfg.get("supply_cap")
         else f"season {season}. Dashed line: managed land, held at {cfg['managed_target']} m or shallower by water management (no supply limit)"),
        x=0.01, ha="left", fontsize=10)
    if a.note:
        fig.text(0.01, 0.01, a.note.read_text(encoding="utf-8").strip(), ha="left", va="bottom", fontsize=9)
    out = a.out or run / "watertable_map.png"
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == "__main__":
    main()
