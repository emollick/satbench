# SatBench scripts

`run.sh` rebuilds every SatBench chart from scratch:

```sh
pip install -r ../../requirements.txt
./run.sh
```

It clones the [Benchmark Almanac](https://github.com/brianlzhou/benchmark-almanac) into `repo/` at commit
`90715d1` (Nov 14, 2026), dumps the site's own data layer to `dump/`, and draws the charts into `../share`,
`../index`, `../items` and `../labs`. Rerun at that commit, the output matches the published PNGs pixel for pixel.
To update to newer data, change `ALMANAC_COMMIT` in `run.sh`; the hardcoded "as of" date lives in `common.py`.

## Requirements

- Node 22.18 or later (on 22.6 to 22.17, add `--experimental-strip-types` to the `node` line). No `npm install` is needed.
- Python 3.11 or later with the packages in `../../requirements.txt`.
- The Inter font, optionally. Without it the charts fall back to the default font.

## Files

| File | What it does |
|---|---|
| `dump.mts`, `reg.mjs`, `hook.mjs` | Import the almanac's `src/lib/data.ts` and write `dump/*.json`: every benchmark's summary (`benchSummary()`), models, labs, launch posts, and independent-run scores. The hook lets plain Node import the site's JSON files. |
| `common.py` | **The SatBench definition**: which benchmarks are items, when an item counts as solved, the live and fixed-edition scores, and the shared chart style. |
| `index/run.py` | The live index, the fixed editions, the robustness variants, the working set, the projection and the by-area chart. Also writes `numbers.json`. |
| `index/explore.py`, `explore2.py`, `extra.py`, `ws.py` | Print the supporting numbers quoted in `../summary.md` (hazard rates, independent-only scores, working-set counts). No charts. |
| `items/analysis.py`, `items/charts.py` | Holdouts, time to 85% by release year (Kaplan-Meier), and items by area. `analysis.py` also reads the almanac's `data/audits.json`. |
| `labs/data.py`, `labs/headline.py`, `labs/charts.py` | Kills by lab, by source and normalized for reporting volume; how many already-saturated benchmarks each lab headlines. |
| `labs/contested.py` | Kills counted only on benchmarks that other frontier labs also report. This is the lab ranking the README uses. |
| `card.py`, `leaderboard.py`, `cohorts.py`, `runout.py` | The four share-ready images in `../share`. |
