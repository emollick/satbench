"""Shared data + definitions for SATURATION-BENCH (the benchmark of benchmarks).

Definition (do not change without telling the lead):
  * ITEMS: every benchmark in the almanac named in >= 10 lab launch posts, scored in percent, higher is better.
    Versions count as separate items (AIME 2024 and AIME 2025 are two items), as in the earlier saturation work.
  * An item is SOLVED at date t when the best reported score from any source (the site's own `frontier`:
    official leaderboards, Epoch AI runs, lab launch posts, collected claims) is >= THRESH (85) on or before t.
  * Item release month = benchmark `released` (YYYY-MM -> first of month). An item enters the test on release.
  * SatBench score at t = solved items / items released by t  ("live" exam: new benchmarks join as they come out).
  * Fixed exams: SatBench-<year> = items released by Dec 31 of <year>; denominator fixed.
Data as of AS_OF (Nov 14, 2026).
"""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))  # satbench/scripts
import json, os, datetime as dt
from collections import defaultdict
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, 'dump')
AS_OF = pd.Timestamp('2026-11-14')
THRESH = 85.0
MIN_CITES = 10
FRONTIER_LABS = ['anthropic', 'openai', 'google', 'moonshot', 'meta', 'deepseek', 'xai', 'qwen', 'zai']

_S = json.load(open(os.path.join(DUMP, 'summaries.json')))
MODELS = {m['id']: m for m in json.load(open(os.path.join(DUMP, 'models.json')))}
LABS = {l['id']: l for l in json.load(open(os.path.join(DUMP, 'labs.json')))}
CARDS = json.load(open(os.path.join(DUMP, 'cards.json')))   # launch posts: id, date, lab, model, n results
_INDEP = json.load(open(os.path.join(DUMP, 'indep_points.json')))


def summaries():
    """All 3,327 benchmark summaries from the site's own benchSummary()."""
    return _S


def lab_of(model_id):
    return (MODELS.get(model_id) or {}).get('lab')


def lab_name(lab_id):
    return (LABS.get(lab_id) or {}).get('name', lab_id or 'unknown')


def model_name(model_id):
    return (MODELS.get(model_id) or {}).get('name', model_id)


def _month(s):
    return pd.Timestamp(s + '-01') if len(s) == 7 else pd.Timestamp(s[:10])


def crossing(points, thresh):
    """First (date, model, source, value) where a running-best frontier reaches thresh. points sorted by date."""
    for p in points:
        if p['value'] >= thresh:
            return p
    return None


def indep_frontier(bench_id):
    """Running best from independent runs only (official leaderboard, Epoch AI, boards Epoch copied); no lab claims."""
    pts = sorted(_INDEP.get(bench_id, []), key=lambda p: (p['date'], -p['value']))
    out = []
    for p in pts:
        if not out or p['value'] > out[-1]['value']:
            out.append(p)
    return out


def items(min_cites=MIN_CITES):
    """DataFrame of SatBench items with solve dates at 75/85/95 and independent-only 85."""
    rows = []
    for x in _S:
        if len(x['cites']) < min_cites or (x['unit'] or '%') != '%' or x['better'] == 'lower':
            continue
        fr = x['frontier']
        rel = _month(x['released']) if x['released'] else _month(x['first'])
        r = dict(id=x['id'], name=x['name'], family=x['family'] or x['id'], area=x['area'], released=rel,
                 n_cites=len(x['cites']), n_scores=x['nScores'], first_cite=pd.Timestamp(x['first']),
                 last_cite=pd.Timestamp(x['last']), status=x['status'],
                 best=fr[-1]['value'] if fr else np.nan, best_model=fr[-1]['model'] if fr else None,
                 best_source=fr[-1]['source'] if fr else None, best_date=pd.Timestamp(fr[-1]['date']) if fr else pd.NaT,
                 epoch_ceiling=(x['epoch'] or {}).get('ceiling'))
        for t in (75, 85, 95):
            c = crossing(fr, t)
            r[f'solved{t}'] = pd.Timestamp(c['date']) if c else pd.NaT
            r[f'solver{t}'] = c['model'] if c else None
            r[f'solver{t}_source'] = (c['source'] + (':' + c['via'] if c.get('via') else '')) if c else None
            r[f'solver{t}_value'] = c['value'] if c else np.nan
        ci = crossing(indep_frontier(x['id']), THRESH)
        r['solved85_indep'] = pd.Timestamp(ci['date']) if ci else pd.NaT
        r['frontier'] = fr
        rows.append(r)
    df = pd.DataFrame(rows)
    df['solver85_lab'] = df['solver85'].map(lab_of)
    df['solver95_lab'] = df['solver95'].map(lab_of)
    # "born solved": already past 85% on or before its release month ended
    df['born_solved'] = df['solved85'].notna() & (df['solved85'] < df['released'] + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1))
    return df


def satbench_series(df, col='solved85', start='2023-01-01', end=AS_OF, freq='MS', fixed_cutoff=None):
    """Monthly SatBench score. Live by default; fixed_cutoff (Timestamp) freezes the item set to items released by then."""
    dates = list(pd.date_range(start, end, freq=freq))
    if dates[-1] < pd.Timestamp(end):
        dates.append(pd.Timestamp(end))
    out = []
    for t in dates:
        pool = df[df['released'] <= (fixed_cutoff if fixed_cutoff is not None else t)]
        if fixed_cutoff is not None and t < fixed_cutoff:
            pool = df[df['released'] <= fixed_cutoff]
        n = len(pool)
        k = int((pool[col].notna() & (pool[col] <= t)).sum())
        out.append(dict(date=t, n_items=n, solved=k, score=100 * k / n if n else np.nan))
    return pd.DataFrame(out)


# ---------------------------------------------------------------- chart style
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

BG = '#FBFAF7'
INK = '#141414'
MUTED = '#5C5C5C'
FAINT = '#8A8A8A'
GRID = '#E6E4DF'
BLUES = ['#BBD3F2', '#86B4EA', '#3F84D8', '#1F5FAE', '#0E3A75']
ACCENT = '#D9542B'   # warm accent for highlights (resisting / unsolved)
GREY = '#B5B3AE'
CREDIT = 'Data: Benchmark Almanac (benchmarkalmanac.com), incl. Epoch AI Benchmarking Hub (CC BY 4.0). Data as of Nov 14, 2026.'

plt.rcParams.update({
    'font.family': 'Inter', 'font.size': 15, 'axes.facecolor': BG, 'figure.facecolor': BG,
    'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 1, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.spines.left': False, 'xtick.labelsize': 15, 'ytick.labelsize': 15,
    'axes.labelsize': 16, 'savefig.facecolor': BG,
})


def figure(title, subtitle, notes=(), size=(12, 6.75), rect=None):
    """Social-card figure: 2400x1350 at dpi 200. Returns (fig, ax). rect = axes [l, b, w, h] in figure coords."""
    fig = plt.figure(figsize=size, dpi=200)
    fig.text(0.04, 0.955, title, fontsize=27, fontweight='bold', color=INK, va='top')
    fig.text(0.04, 0.885, subtitle, fontsize=15.5, color=MUTED, va='top', linespacing=1.45, wrap=True)
    lines = list(notes) + [CREDIT]
    for i, line in enumerate(reversed(lines)):
        fig.text(0.04, 0.025 + i * 0.033, line, fontsize=11.5, color=FAINT, va='bottom')
    if rect is None:
        nsub = subtitle.count('\n') + 1
        top = 0.86 - 0.05 * nsub
        bottom = 0.11 + 0.033 * len(lines)
        rect = [0.08, bottom, 0.86, top - bottom]
    ax = fig.add_axes(rect)
    return fig, ax


def save(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
