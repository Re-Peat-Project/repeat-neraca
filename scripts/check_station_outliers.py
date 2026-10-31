"""How much of the SiTMAT water-table (TMAT) record would `fieldcheck.screen` leave out? Restarts after gaps, settling days, stuck loggers
and day-to-day jumps that pass SiTMAT's own QC (range -500..100 cm, single spikes over 60 cm).

  python scripts/check_station_outliers.py --khg 16.02.01 14.02-04-05.01 15.05-07-10.01 --out docs/reports/station_outliers.md
      # needs SITMAT_PROCESSED and REPEAT_KHG

National: `$SITMAT_PROCESSED/daily_long.csv`, readings without a SiTMAT flag. Per KHG: the station file the groundwater model scores against
(`03_neraca/inputs/model/stations_daily.csv`, else `03_neraca/inputs/`). Depths in the model files are cm positive down; below 0 is water
above the ground.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from repeat_neraca.groundwater import fieldcheck as FC

REASONS = ["short_piece", "settling", "stuck"]


def counts(d: pd.DataFrame, value: str) -> pd.DataFrame:
    """d: kind, station_id, date, <value>. One row per kind: readings, left out per reason, kept, stations touched, jumps."""
    rows = []
    for (kind, sid), g in d.groupby(["kind", "station_id"]):
        _, n = FC.screen(g.set_index("date")[value])
        rows.append({"kind": kind, **n, "restarts": int(n["pieces"] > 1)})
    t = pd.DataFrame(rows).groupby("kind").agg(stations=("readings", "size"), readings=("readings", "sum"),
                                               **{r: (r, "sum") for r in REASONS}, kept=("kept", "sum"),
                                               stations_restarting=("restarts", "sum"), jumps_over_30cm=("jumps_over_30cm", "sum"))
    return t.reset_index()


def table(t: pd.DataFrame, label: str) -> list[str]:
    L = [f"| {label} | stations | readings | short pieces | settling days | stuck runs | left out | stations with a gap of 7+ days | day-to-day jumps > {FC.JUMP_CM:g} cm |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples(index=False):
        out = r.readings - r.kept
        L.append(f"| {r.kind} | {r.stations:,} | {r.readings:,} | {r.short_piece:,} | {r.settling:,} | {r.stuck:,} | {out:,} ({out / r.readings:.0%}) "
                 f"| {r.stations_restarting:,} ({r.stations_restarting / r.stations:.0%}) | {r.jumps_over_30cm:,} |")
    return L


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--khg", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from repeat_common import khg as K
    d = pd.read_csv(Path(os.environ["SITMAT_PROCESSED"]) / "daily_long.csv", usecols=["kind", "station_id", "date", "water_level_cm", "flag"],
                    parse_dates=["date"])
    d = d[d.flag.isna() & d.water_level_cm.notna()]
    L = ["# Outliers in the SiTMAT water-table record", "",
         f"Written by `scripts/check_station_outliers.py` with the screening rule of `groundwater/fieldcheck.py` (set 2026-10-29): a record is "
         f"split at gaps of {FC.GAP_DAYS} days or more; pieces shorter than {FC.MIN_PIECE_DAYS} days are left out; so are the first "
         f"{FC.SETTLE_DAYS} days of each piece and runs of {FC.STUCK_DAYS} or more identical values. Day-to-day jumps over {FC.JUMP_CM:g} cm "
         "are counted, not removed. Readings are what passed SiTMAT's own QC.", "",
         f"National, `daily_long.csv` ({d.date.min():%Y-%m-%d} to {d.date.max():%Y-%m-%d}):", ""]
    L += table(counts(d, "water_level_cm"), "kind")
    for code in a.khg:
        kf = K.folder(code)
        sd = next((x for x in (kf / "03_neraca" / "inputs" / "model", kf / "03_neraca" / "inputs") if (x / "stations_daily.csv").exists()), None)
        if sd is None:
            continue
        s = pd.read_csv(sd / "stations_daily.csv", parse_dates=["date"])
        s["kind"] = s.station_id.str.split("/").str[0].where(s.station_id.str.contains("/"), "concession")
        above = s.groupby("kind").depth_cm.apply(lambda v: f"{(v < 0).mean():.1%}")
        L += ["", f"{kf.name}, `{sd.relative_to(kf).as_posix()}/stations_daily.csv` (readings above the ground: "
              + ", ".join(f"{k} {v}" for k, v in above.items()) + "):", ""]
        L += table(counts(s, "depth_cm"), "kind")
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
