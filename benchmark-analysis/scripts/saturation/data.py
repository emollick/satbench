"""Shared prep for the saturation / extinction analyses."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # benchmark-analysis/scripts
import sys, json
sys.path.insert(0, ROOT)
import common as c
import pandas as pd, numpy as np

AS_OF = pd.Timestamp('2026-11-14')
FRONTIER = ['anthropic', 'openai', 'google', 'moonshot', 'meta', 'deepseek', 'xai', 'qwen', 'zai']
OUTDIR = os.path.join(c.OUT, 'saturation') + os.sep
R = {b['id']: b for b in c.raw()['benches']}
B = c.benches()

def rel_date(s):
    if not s or pd.isna(s): return pd.NaT
    s = str(s)
    if len(s) == 4: s += '-07'          # year only -> mid-year
    if len(s) == 7: s += '-15'          # month only -> mid-month
    return pd.Timestamp(s)

def half(d):
    d = pd.Timestamp(d)
    if d.year <= 2024: return '2023-24'
    return f"{d.year} H{1 if d.month <= 6 else 2}"
PERIODS = ['2023-24', '2025 H1', '2025 H2', '2026 H1', '2026 H2']

def cards():
    cs = pd.DataFrame(json.load(open(f'{c.REPO}/data/cards.json')))
    cs['date'] = pd.to_datetime(cs['date'])
    cs['period'] = cs['date'].map(half)
    cs['frontier'] = cs['lab'].isin(FRONTIER)
    return cs

# HMMT Nov 2025 is another sitting of the HMMT contest; treat it as a version, like AIME years
FAMILY_OVERRIDE = {'hmmt-nov-2025': 'hmmt-february'}
def fam_of(k):
    if k in FAMILY_OVERRIDE: return FAMILY_OVERRIDE[k]
    f = B.at[k, 'family']
    return f if isinstance(f, str) else k

def cites():
    """One row per (launch post, benchmark) from the site's citeDates."""
    rows = []
    for b in R.values():
        for d, lab, model, score in b['citeDates']:
            rows.append((b['id'], d, lab, model, score))
    df = pd.DataFrame(rows, columns=['bench', 'date', 'lab', 'model', 'score'])
    df['date'] = pd.to_datetime(df['date'])
    df['period'] = df['date'].map(half)
    df['frontier'] = df['lab'].isin(FRONTIER)
    df['family'] = df['bench'].map(fam_of)
    return df

def frontier(bid):
    f = pd.DataFrame(R[bid]['frontier'], columns=['date', 'value', 'model', 'source'])
    f['date'] = pd.to_datetime(f['date'])
    return f

def best_at(bid, date):
    f = frontier(bid)
    f = f[f['date'] <= pd.Timestamp(date)]
    return f['value'].iloc[-1] if len(f) else np.nan
