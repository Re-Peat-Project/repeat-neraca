"""Field water-table points of a KHG: one generic table that the groundwater model is scored against.

    python -m repeat_neraca.groundwater.fieldobs --khg 14.10.03 --source "$REPEAT_DATA/Peat depth and DTM/Tebingtinggi.csv" --format tebingtinggi2015

Writes `_khg/<folder>/00_inputs/field_wtd.csv` and lists it in `00_inputs/local_manifest.csv`. Columns:

    point_id, lon, lat, depth_cm      water table depth below the surface, positive down; empty where not measured
    date_from, date_to                window the reading falls in (the survey date when known)
    on_peat                           1 peat, 0 mineral soil (as recorded in the field)
    peat_thickness_m, peat_type, drainage, land_use, status, group      attributes for breakdowns; group = survey team or transect
    flag                              empty, or why the reading should be left out of a score

A KHG with other field data gets its own `--format` reader that returns the same columns.

Format `tebingtinggi2015`: the 2015 survey of Pulau Tebing Tinggi (`Tebingtinggi.csv`, 1,385 points). The survey date is not recorded;
`HujanAkhir` holds the date of the last rain before the visit, from 24 October to 1 December 2015, so each reading is taken as falling between
that date and 10 December 2015 (24 October where it is missing). `Air_Tanah` = 0 is read as not measured: the zeros cluster by surveyor (up
to 91% of one surveyor's points) and in mangrove (91%; scripts/check_field_inputs.py), and the survey has no ponding record (`Genangan` is 0 everywhere) to tell a dry
reading from a flooded one. Flags: `deeper_than_peat` (water table below the recorded peat base), `deeper_than_2m`.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ["point_id", "lon", "lat", "depth_cm", "date_from", "date_to", "on_peat", "peat_thickness_m", "peat_type", "drainage", "land_use",
           "status", "group", "flag"]
MONTHS_ID = {"januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "agustus": 8, "september": 9,
             "oktober": 10, "nopember": 11, "november": 11, "desember": 12}


def _date_id(s) -> pd.Timestamp:
    """'27 Oktober 2015' -> Timestamp, NaT when not a date."""
    p = str(s).strip().lower().split()
    if len(p) == 3 and p[1] in MONTHS_ID and p[0].isdigit() and p[2].isdigit():
        return pd.Timestamp(int(p[2]), MONTHS_ID[p[1]], int(p[0]))
    return pd.NaT


def tebingtinggi2015(path: str | Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    last_rain = d["HujanAkhir"].map(_date_id)
    start, end = pd.Timestamp("2015-10-24"), pd.Timestamp("2015-12-10")
    last_rain = last_rain.where((last_rain >= start) & (last_rain <= end))         # one entry reads 2005, a typo
    depth = d["Air_Tanah"].astype(float).where(d["Air_Tanah"] > 0)
    thick = d["TebalGmbt1"].astype(float)
    flag = np.where((thick > 0) & (depth / 100 > thick), "deeper_than_peat", np.where(depth > 200, "deeper_than_2m", ""))
    low = lambda c: d[c].astype(str).str.strip().str.lower()
    return pd.DataFrame({
        "point_id": d["FID"].astype(int), "lon": d["POINT_X"], "lat": d["POINT_Y"], "depth_cm": depth,
        "date_from": last_rain.fillna(start).dt.date.astype(str), "date_to": end.date().isoformat(),
        "on_peat": (thick > 0).astype(int), "peat_thickness_m": thick, "peat_type": low("Jns_Gmbt"),
        "drainage": low("Drainase_B").replace({"saluran tebuka": "saluran terbuka", "sauran terkontrol": "saluran terkontrol"}),
        "land_use": low("TupLah"), "status": low("Status"), "group": low("Surveyor").replace("", "(none)"),
        "flag": np.where(depth.isna(), "", flag)})[COLUMNS]


FORMATS = {"tebingtinggi2015": tebingtinggi2015}


def read(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"flag": str, "group": str}, keep_default_na=True).fillna({"flag": "", "group": "(none)"})


def write_manifest_row(kf: Path, rel: str, source: str, what: str, count: int) -> None:
    """Add or replace the row of 00_inputs/<rel> in 00_inputs/local_manifest.csv."""
    f = kf / "00_inputs" / rel
    man = kf / "00_inputs" / "local_manifest.csv"
    row = {"file": rel, "source": source, "what": what, "count": count, "bytes": f.stat().st_size,
           "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    m = pd.read_csv(man) if man.exists() else pd.DataFrame(columns=list(row))
    m = pd.concat([m[m["file"] != row["file"]], pd.DataFrame([row])], ignore_index=True)
    m.to_csv(man, index=False)


def write(table: pd.DataFrame, kf: Path, source: Path) -> Path:
    """field_wtd.csv in 00_inputs of the KHG folder, and its row in local_manifest.csv."""
    out = kf / "00_inputs" / "field_wtd.csv"
    table.to_csv(out, index=False)
    write_manifest_row(kf, "field_wtd.csv", source.name, "field water table points (repeat_neraca.groundwater.fieldobs)", len(table))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", required=True, help="KHG name or code")
    ap.add_argument("--source", required=True)
    ap.add_argument("--format", required=True, choices=sorted(FORMATS))
    a = ap.parse_args(argv)
    from repeat_common import khg as K
    t = FORMATS[a.format](a.source)
    out = write(t, K.folder(a.khg), Path(a.source))
    n = t["depth_cm"].notna()
    print(f"{out}: {len(t)} points, {int(n.sum())} with a depth ({int((n & (t.on_peat == 1)).sum())} on peat), "
          f"flagged {int((t.flag != '').sum())}")


if __name__ == "__main__":
    main()
