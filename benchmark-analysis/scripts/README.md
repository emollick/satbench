# Scripts: correlations, saturation and clusters

These scripts made the charts in `../correlations`, `../saturation` and `../clusters`. `run.sh` rebuilds them all:

```sh
pip install -r ../../requirements.txt
./run.sh
```

It clones https://github.com/brianlzhou/benchmark-almanac into `repo/` at commit `1737c28` (Nov 14, 2026), the commit the published charts used, and runs the steps below in order. Rerun at that commit, every chart matches the published PNG pixel for pixel except `benchmark_map.png`, whose label placement (from `adjustText`) can shift slightly between package versions.

## Requirements

- **Node 22.18 or later** (add `--experimental-strip-types` on 22.6 to 22.17). It runs the almanac's own TypeScript directly, with no `npm install`.
- **Python 3.11 or later**, with `numpy pandas scipy scikit-learn matplotlib adjustText`.
- **Inter font (optional).** The charts fall back to the default font without it.

## Run order

### 1. Dump the almanac's data layer

```sh
node --import ./reg.mjs dump.ts
```

- `reg.mjs` and `hooks.mjs` add a loader hook so plain Node can import the site's `.json` files.
- `dump.ts` imports `src/lib/data.ts` from the clone and calls `allSummaries()`.
- That reads everything `data.ts` loads: `data/labs.json`, `models.json`, `benchmarks.json`, `resources.json`, `cards.json`, `system-cards.json`, `scores/epoch.json` and `scores/leaderboards.json`.
- It writes `summaries.json` (about 6 MB, not included; `run.sh` regenerates it). For each benchmark this has its status, its launch-post citations, its best-score-over-time and its lead board.

### 2. Shared module

`common.py` holds the data helpers (`benches()`, `scores()`, `matrix()`, `models()`) and the chart style.

- It reads `summaries.json` and `data/models.json`.
- It is imported by every script below.

### 3. Correlations (`correlations/`)

1. `python analysis.py` reads `summaries.json` (through `common.py`) and `data/scores/epoch.json` (ECI and the list of Epoch hub benchmarks). It writes `out/pairs.csv`, `out/per_bench.csv` and `out/matrix.csv`.
2. `python charts.py` makes the two heatmaps. It reads `out/*.csv` and imports `analysis`.
3. `python charts2.py` makes the pairs, predictability and scatter charts. It imports `charts` and `analysis`.

### 4. Saturation and extinct benchmarks (`saturation/`)

The data modules build on each other: `data.py` → `sat_calc.py` → `km.py`, and `data.py` → `extinct_calc.py`.

- `data.py` reads `summaries.json` (through `common.py`) and `data/cards.json`, for launch posts by lab and date.
- Each chart script imports what it needs, so they can run in any order:

| Script | Imports | Output |
|---|---|---|
| `chart_lanes.py` | `sat_calc` | `saturation_timeline_top30.png` |
| `chart_km.py` | `km` | `time_to_saturation_by_cohort.png` |
| `chart_iconic.py` | `sat_calc` | `iconic_benchmarks_best_score.png` |
| `chart_riseandfall.py` | `extinct_calc` | `extinct_rise_and_fall.png` |
| `chart_extinct_table.py` | `extinct_calc` | `extinct_benchmarks_table.png` |

### 5. Clusters (`clusters/`)

1. `python analysis.py` reads `summaries.json` (through `common.py`) and `data/benchmarks.json`. It fits the low-rank model, runs the cross-checks and bootstrap, and writes `results.pkl`. This takes a few minutes.
2. `python charts.py` reads `results.pkl` and makes all five cluster charts.

## Data terms

The almanac's data does not have a single license.

- Epoch AI data is CC BY 4.0.
- Some leaderboards are non-commercial, for example SWE-bench (CC BY-NC 4.0) and MathArena (CC BY-NC-SA 4.0).
- See the almanac README's License section before redistributing any derived data.
