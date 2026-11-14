"""Pairwise rank correlations between widely used capability benchmarks, raw and controlling for
general capability (Epoch Capabilities Index) and for model release date. Writes results to ./out/."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # benchmark-analysis/scripts
import sys, json, itertools, os
sys.path.insert(0, ROOT)
import common as c
import numpy as np, pandas as pd
from scipy.stats import rankdata

MIN_N = 15  # minimum shared models for a pair to be reported
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f'{HERE}/out', exist_ok=True)

# Widely used capability benchmarks with large lead boards (or heavy launch-post use); one per family;
# safety area, composite indexes and near-duplicate boards (e.g. the many DesignArena / Kaggle Game Arena
# sub-boards) excluded.
BENCHES = [
    # knowledge & language
    'lmarena-elo', 'mmlu-pro', 'humanitys-last-exam', 'simpleqa-verified', 'ifeval', 'creative-writing-v3',
    'nyt-connections-extended', 'bullshitbench-2', 'vectara-hallucination-leaderboard-hhem',
    # math & science
    'gpqa-diamond', 'otis-mock-aime-2024-2025', 'aime-2025', 'frontiermath-tiers-1-3-v2', 'arc-agi-2',
    'simplebench', 'math-level-5', 'forecastbench',
    # coding
    'swe-bench-verified', 'livecodebench-v6', 'designarena-website', 'code-arena', 'weirdml', 'ale-bench',
    'vibe-code-bench',
    # agents
    'tau2-bench', 'browsecomp', 'terminal-bench-2-0', 'gaia', 'llm-chess', 'snakebench', 'chess-puzzles',
    # professional work
    'legalbench', 'vals-taxeval-v2', 'corpfin-v2', 'vals-medcode', 'vending-bench-2', 'vals-finance-agent-v2',
    'profbench',
    # vision
    'mmmu', 'mmmu-pro', 'vision-arena', 'zerobench', 'charxiv',
]

B = c.benches().loc[BENCHES]
S = c.scores()
S = S[S.bench.isin(BENCHES)]
M = S.pivot_table(index='model', columns='bench', values='value', aggfunc='max')[BENCHES]

eci = pd.Series({r['model']: r['eci'] for r in json.load(open(f'{c.REPO}/data/scores/epoch.json'))['eci']})
rel = c.models()['released']
reln = pd.Series(rel.map(lambda d: d.toordinal() if pd.notna(d) else np.nan), index=rel.index)
epoch_hub = {r[0] for r in json.load(open(f'{c.REPO}/data/scores/epoch.json'))['rows']}


def rho(x, y):
    rx, ry = rankdata(x), rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return np.nan
    return np.corrcoef(rx, ry)[0, 1]


def partial(x, y, z):
    rxy, rxz, ryz = rho(x, y), rho(x, z), rho(y, z)
    d = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    return (rxy - rxz * ryz) / d if d > 1e-9 else np.nan


rows = []
for a, b in itertools.combinations(BENCHES, 2):
    both = M[[a, b]].dropna()
    r = dict(a=a, b=b, n=len(both), rho=np.nan)
    if len(both) >= MIN_N:
        r['rho'] = rho(both[a], both[b])
    for name, z in (('eci', eci), ('date', reln)):
        t = both.join(z.rename('z'), how='inner').dropna()
        r[f'n_{name}'] = len(t)
        r[f'rho_{name}_subset'] = rho(t[a], t[b]) if len(t) >= MIN_N else np.nan
        r[f'partial_{name}'] = partial(t[a], t[b], t['z']) if len(t) >= MIN_N else np.nan
    rows.append(r)
P = pd.DataFrame(rows)
P['area_a'] = P.a.map(B.area); P['area_b'] = P.b.map(B.area)
P['same_area'] = P.area_a == P.area_b
P.to_csv(f'{HERE}/out/pairs.csv', index=False)

# per-benchmark: correlation with ECI and with release date, typical correlation with others
per = []
for bn in BENCHES:
    col = M[bn].dropna()
    te = pd.concat([col, eci], axis=1, join='inner').dropna()
    td = pd.concat([col, reln], axis=1, join='inner').dropna()
    sub = P[(P.a == bn) | (P.b == bn)]
    per.append(dict(bench=bn, name=B.loc[bn, 'name'], area=B.loc[bn, 'area'], n_board=len(col),
                    n_eci=len(te), rho_eci=rho(te.iloc[:, 0], te.iloc[:, 1]) if len(te) >= MIN_N else np.nan,
                    n_date=len(td), rho_date=rho(td.iloc[:, 0], td.iloc[:, 1]) if len(td) >= MIN_N else np.nan,
                    n_pairs=sub.rho.notna().sum(), median_rho=sub.rho.median(), median_partial_eci=sub.partial_eci.median(),
                    max_partial_eci=sub.partial_eci.max(), in_epoch_hub=bn in epoch_hub,
                    board_source=B.loc[bn, 'board_source']))
PER = pd.DataFrame(per)
PER.to_csv(f'{HERE}/out/per_bench.csv', index=False)
M.to_csv(f'{HERE}/out/matrix.csv')

if __name__ == '__main__':
  pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
  print(PER.sort_values('rho_eci').round(2).to_string())
  print('pairs total', len(P), 'reported raw', P.rho.notna().sum(), 'partial eci', P.partial_eci.notna().sum(),
      'partial date', P.partial_date.notna().sum())
  for col in ['rho', 'partial_eci', 'partial_date']:
    g = P.dropna(subset=[col]).groupby('same_area')[col].agg(['mean', 'median', 'count'])
    print(col); print(g.round(3))
