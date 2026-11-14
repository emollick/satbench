#!/usr/bin/env bash
# Rebuild the correlations, saturation and clusters charts from the Benchmark Almanac.
# Clones the almanac at the commit the published charts used, dumps its data layer, then draws the charts
# into ../correlations, ../saturation and ../clusters.
set -euo pipefail
cd "$(dirname "$0")"
ALMANAC_COMMIT=1737c28606322adcbc1c154d5e3d066e10751fd4   # Nov 14, 2026

[ -d repo ] || git clone https://github.com/brianlzhou/benchmark-almanac.git repo
git -C repo fetch -q origin 2>/dev/null || true
git -C repo checkout -q "$ALMANAC_COMMIT"

node --import ./reg.mjs dump.ts           # writes summaries.json from the site's own src/lib/data.ts

(cd correlations && python3 analysis.py && python3 charts.py && python3 charts2.py)
(cd saturation && for f in chart_*.py; do python3 "$f"; done)
(cd clusters && python3 analysis.py && python3 charts.py)   # the cluster fit takes a few minutes
