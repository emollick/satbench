#!/usr/bin/env bash
# Rebuild every SatBench chart from the Benchmark Almanac.
# Clones the almanac at the commit the published charts used, dumps its data layer, then draws the charts
# into ../share, ../index, ../items and ../labs.
set -euo pipefail
cd "$(dirname "$0")"
ALMANAC_COMMIT=90715d125ae15408329fc5203452726549f9c0e3   # Nov 14, 2026

[ -d repo ] || git clone https://github.com/brianlzhou/benchmark-almanac.git repo
git -C repo fetch -q origin 2>/dev/null || true
git -C repo checkout -q "$ALMANAC_COMMIT"

mkdir -p dump
node --import ./reg.mjs dump.mts          # writes dump/*.json from the site's own src/lib/data.ts

python3 index/run.py                      # ../index: live index, fixed editions, robustness, working set, projection, areas
python3 items/charts.py                   # ../items: scorecard, holdouts, half-life by cohort, areas
python3 labs/charts.py                    # ../labs: kills by lab, by source, normalized, at 95%, headline saturation
python3 labs/contested.py                 # ../labs: contested kills (the lab ranking the README uses)
python3 card.py                           # ../share: summary card
python3 leaderboard.py                    # ../share: lab leaderboard
python3 cohorts.py                        # ../share: each year's benchmarks get beaten faster
python3 runout.py                         # ../share: when will SatBench be saturated
