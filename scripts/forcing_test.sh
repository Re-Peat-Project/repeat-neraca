#!/usr/bin/env bash
# Question: does finer rain (CHIRPS v3, 5 km) and/or evaporation (WaPOR v3, 300 m) than ERA5 (25 km) improve the neraca air
# calibration on the SiTMAT stations? Runs the station calibration (no sub-KHG indicators) for every combination.
#
#   bash scripts/forcing_test.sh sugihan_lumpur      # or kampar_gaung; run in repeat-neraca; needs REPEAT_DATA, REPEAT_WORK and SITMAT_PROCESSED
#
# Reads the cached ERA5 calibration window (run `repeat_neraca.bucket.run --forcing-only` first for the baseline), reads CHIRPS and WaPOR
# for the same days (about 10-20 minutes the first time, cached afterwards) and writes one report per combination to
# $REPEAT_WORK/out_neraca_<khg>_<rain>_<evap>/neraca_report.json. `python -m repeat_neraca.bucket.forcing_compare` puts them side by side.
set -euo pipefail
khg="${1:?usage: forcing_test.sh <config folder name, e.g. sugihan_lumpur>}"
cfg="../re-peat/sites/${khg}/neraca_experiments.yaml"
for combo in "chirps era5" "era5 wapor" "chirps wapor"; do
  set -- $combo
  python -m repeat_neraca.bucket.run --config "$cfg" --calibrate-only --rain "$1" --evap "$2" --out "${REPEAT_WORK:?set REPEAT_WORK}/out_neraca_${khg}_$1_$2"
done
