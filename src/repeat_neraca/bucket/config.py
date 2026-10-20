"""Config of the bucket-model experiments: the part of the old prioritisation defaults these modules read.

Kept key for key so the site configs (configs/<site>/neraca.yaml) work unchanged. `load_config(path, preset, level)` merges
defaults, the module preset (e.g. repeat_neraca.bucket.run.PRESET) and the user's YAML, and expands ${NAME}.
"""
from __future__ import annotations

import copy

from repeat_common import sources as SRC
from repeat_common import tma as TMA
from repeat_common.config import deep_update, expand_env

DEFAULTS = {
    "khg": None,
    "khg_id_field": "khg_id",
    "khg_filter": [],
    "units": {"mode": "khg", "hex_area_km2": 1.0, "min_fraction": 0.2, "path": None, "id_field": "unit_id", "subkhg": {}},
    "grid_res_m": 30,
    "years": {"baseline": [2016, 2022], "validation": [2023], "elnino": [2015, 2019, 2023]},
    "dry_months": [6, 7, 8, 9, 10],
    "ndmi_months": [8, 9, 10],
    "cache_dir": "cache",
    "out": "out_prioritas",
    "sources": copy.deepcopy(SRC.SOURCE_DEFAULTS),
    "vectors": {"canals": None, "rivers": None, "lakes": None, "roads": None, "settlements": None,
                "protected": {"path": None, "field": None, "values": ["lindung"]},
                "blocks": None, "tidal": None,
                "concessions": {"path": None, "type_field": None, "exclude_types": ["IUP"]},
                "tma_csv": None},
    "tma": copy.deepcopy(TMA.TMA_DEFAULTS),
    "rasters": {"peat_depth": None, "dtm": None},
    "params": {"peat_depth_scale": 1.0,
               "l_inf_m": 200, "l_inf_burnt_m": 60, "water_min_months": 10, "exposure_m": 2000,
               "forest_classes": [10, 95], "tma_threshold_m": 0.4, "tma_depth_positive": None,
               "tma_max_gap_days": 10,
               # water balance (Kahayan-Sebangau study, 2021): interception 0 % open land to 16.4 % forest;
               # runoff coefficient 0.07-0.18 measured on Pulau Padang (Aditya & Cahyono 2018)
               "runoff_coefficient": 0.12,
               "interception_by_class": {"10": 0.164, "95": 0.164, "20": 0.08, "90": 0.05, "30": 0.03, "40": 0.03},
               "water_content_natural": 0.8, "water_content_canalised": 0.7,
               "ipg_dA_m": 0.4, "ipg_category": "A", "ipg_js_min_m": 50, "ipg_js_max_m": 2000,
               "ipg_canal_class_field": None, "ipg_canal_classes": ["primer", "sekunder", "primary", "secondary"]},
}


def load_config(config_path, preset, level, khg=None, out=None) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    user = {}
    if config_path:
        import yaml
        with open(config_path, encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
    deep_update(cfg, copy.deepcopy(preset))
    deep_update(cfg, expand_env(user))
    cfg["level"] = level
    if khg:
        cfg["khg"] = khg
    if out:
        cfg["out"] = out
    y = cfg["years"]
    y["all"] = sorted(set(range(y["baseline"][0], y["baseline"][1] + 1)) | set(y["validation"]) | set(y["elnino"]))
    return cfg
