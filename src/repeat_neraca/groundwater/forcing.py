"""Daily rain and evaporation of a KHG for the physical neraca air: from forcing_daily.csv, or read directly through repeat-common.

`file`    reads `<inputs_dir>/forcing_daily.csv` (written by the retired bucket experiments; the files on disk still serve), the offline route.
`direct`  reads ERA5 (and WaPOR where cached) with `repeat_common.forcing`, using the cache folder of the window first, and returns the
          same table. Needs repeat-common and the `forcing_direct:` block of the config. A cache miss reads the cloud (about 11 minutes).
`auto`    direct if the config has a `forcing_direct:` block, otherwise file.

Config block:

    forcing_direct:
      cache_dir: <folder with era5_daily_<start>_<end>_tz<h>_s<stride>.npz>
      start: 2026-04-01          # the window named by `forcing_window`
      end: 2026-10-15
      tz_hours: 7                # local day: WIB = 7
      era5: {}                   # optional overrides of the repeat-common ERA5 settings

Both routes give the columns date, window, P_era5_mm, E_era5_mm, E_wapor_mm for the window `forcing_window`.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_forcing(cfg: dict, inputs_dir: str | Path, mode: str = "auto") -> tuple[pd.DataFrame, str]:
    """(table of the window `cfg['forcing_window']`, 'file' or 'direct')."""
    if mode not in ("auto", "file", "direct"):
        raise ValueError(f"forcing mode must be auto, file or direct (got {mode})")
    block = cfg.get("forcing_direct")
    if mode == "auto":
        mode = "direct" if block else "file"
    if mode == "file":
        f = pd.read_csv(Path(inputs_dir) / "forcing_daily.csv", parse_dates=["date"])
        return f[f["window"] == cfg["forcing_window"]].reset_index(drop=True), "file"
    if not block:
        raise SystemExit("forcing direct needs a `forcing_direct:` block (cache_dir, start, end) in the config")
    import geopandas as gpd
    from repeat_common import forcing as FO
    from repeat_common import grid as G
    from repeat_common import sources as SRC
    khg = gpd.read_file(cfg["khg"]).to_crs(4326)
    grid = G.make_grid(khg.geometry.union_all(), float(block.get("grid_res_m", 30)))
    label = G.label_raster(khg.to_crs(grid.crs).reset_index(drop=True), grid)
    era5 = {**SRC.SOURCE_DEFAULTS["era5"], **(block.get("era5") or {})}
    f = FO.khg_table(grid, label, era5, block["start"], block["end"], Path(block["cache_dir"]), int(block.get("tz_hours", 7)),
                     int(era5.get("evap_stride", 3)), window=cfg["forcing_window"])
    return f.reset_index(drop=True), "direct"
