"""Are SiTMAT concession water levels a measurement the groundwater model can take its managed-land target from, or do they follow the
PP 57/2016 compliance limit (0.4 m)?

  python scripts/check_concession_levels.py --out docs/reports/concession_levels.md          # needs SITMAT_PROCESSED
  python scripts/check_concession_levels.py --screen --out docs/reports/concession_levels_screened.md   # records screened as the gates are (D20)

From `$SITMAT_PROCESSED/daily_long.csv`, unflagged daily values between -300 and +50 cm (SiTMAT: negative below the surface):
  bins          readings per 1 cm bin from -60 to -20 cm, concession and community stations; a step at -40/-41 cm in one group and not the
                other marks the compliance limit
  stations      per station: median level, standard deviation, share of days equal to the day before
  dry season    per station: median level in September minus median in June (cm, negative = deeper)
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

LIMIT_CM = -40


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screen", action="store_true", help="drop restarts after gaps, settling days and stuck runs per station (fieldcheck.screen)")
    a = ap.parse_args(argv)
    sp = Path(os.environ["SITMAT_PROCESSED"])
    d = pd.read_csv(sp / "daily_long.csv", usecols=["kind", "station_id", "date", "water_level_cm", "flag"], parse_dates=["date"])
    d = d[d.flag.isna() & d.water_level_cm.between(-300, 50)].sort_values(["station_id", "date"])
    if a.screen:
        from repeat_neraca.groundwater.fieldcheck import screen
        n0 = len(d)
        kept = [screen(g.set_index("date").water_level_cm)[0].dropna().reset_index().assign(kind=g.kind.iloc[0], station_id=sid)
                for sid, g in d.groupby("station_id")]
        d = pd.concat(kept, ignore_index=True)[["kind", "station_id", "date", "water_level_cm"]]
        print(f"screened: {len(d):,} of {n0:,} readings kept")
    d["bin"] = np.floor(d.water_level_cm).astype(int)

    bins = d[d.bin.between(-60, -20)].groupby(["bin", "kind"]).size().unstack(fill_value=0)
    bins["community"] = bins.get("community", 0)
    share = bins / d.groupby("kind").size()                        # share of all readings of the group, so the two groups compare
    step = {k: float(bins.loc[LIMIT_CM, k] / max(bins.loc[LIMIT_CM - 1, k], 1)) for k in ("concession", "community")}

    g = d.groupby(["kind", "station_id"])
    per = pd.DataFrame({"median_cm": g.water_level_cm.median(), "sd_cm": g.water_level_cm.std(),
                        "same_as_day_before": g.water_level_cm.apply(lambda s: float((s.diff() == 0).iloc[1:].mean()) if len(s) > 1 else np.nan),
                        "days": g.size()}).reset_index()
    jun = d[d.date.dt.month == 6].groupby("station_id").water_level_cm.median()
    sep = d[d.date.dt.month == 9].groupby("station_id").water_level_cm.median()
    per["jun_to_sep_cm"] = per.station_id.map(sep - jun)
    c = per[per.kind == "concession"]

    q = lambda s: " / ".join(f"{v:.0f}" for v in s.quantile([0.1, 0.25, 0.5, 0.75, 0.9]))
    L = ["# SiTMAT concession water levels and the 40 cm compliance limit", "",
         f"Written by `scripts/check_concession_levels.py` from `$SITMAT_PROCESSED/daily_long.csv` ({d.date.min():%Y-%m-%d} to {d.date.max():%Y-%m-%d}), "
         "unflagged daily values between -300 and +50 cm" + (", screened per station as the gates are (`fieldcheck.screen`, D20)" if a.screen else "") + ". Levels are cm, negative below the surface.", "",
         f"- Readings: {int((d.kind == 'concession').sum()):,} from {c.station_id.nunique():,} concession stations; "
         f"{int((d.kind == 'community').sum()):,} from {per[per.kind == 'community'].station_id.nunique()} community stations.",
         f"- Readings at -40 cm against -41 cm: {step['concession']:.1f} times as many at concession stations, {step['community']:.1f} at community stations.",
         f"- Concession station medians: {(c.median_cm.between(-40, -30)).mean():.0%} between -40 and -30 cm, {(c.median_cm < -40).mean():.0%} deeper than -40 cm, "
         f"{(c.median_cm > -30).mean():.0%} shallower than -30 cm.",
         f"- Concession days equal to the day before (median station): {c.same_as_day_before.median():.0%}; stations with a standard deviation under 2 cm: "
         f"{(c.sd_cm < 2).mean():.0%}.",
         f"- Change from June to September, concession stations with both months ({c.jun_to_sep_cm.notna().sum()}), 10/25/50/75/90th percentile (cm): "
         f"{q(c.jun_to_sep_cm.dropna())}.", "",
         "Share of each group's readings per 1 cm bin (per mille):", "",
         "| level (cm) | concession | community |", "|---|---|---|"]
    L += [f"| {b} | {1000 * share.loc[b, 'concession']:.1f} | {1000 * share.loc[b, 'community']:.1f} |" for b in sorted(share.index, reverse=True)]
    L += ["", "Reading: concession readings pile up just inside the limit and fall off below it; community readings do not. Whether operators hold "
          "water at the limit or report it there, these readings are not independent evidence of the managed water table: a target taken from "
          "them is the 0.4 m compliance level under another name."]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    out = Path(a.out)
    pd.DataFrame({"level_cm": share.index, "concession_permille": 1000 * share["concession"].to_numpy(),
                  "community_permille": 1000 * share["community"].to_numpy()}).to_csv(out.with_suffix(".csv"), index=False)
    pd.Series({"readings_concession": int((d.kind == "concession").sum()), "stations_concession": int(c.station_id.nunique()),
               "readings_community": int((d.kind == "community").sum()), "stations_community": int(per[per.kind == "community"].station_id.nunique()),
               "step_40_concession": step["concession"], "step_40_community": step["community"],
               "first_date": f"{d.date.min():%Y-%m-%d}", "last_date": f"{d.date.max():%Y-%m-%d}"}, name="value").rename_axis("metric").reset_index().to_csv(
        out.with_name(out.stem + "_stats.csv"), index=False)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
