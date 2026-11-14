import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys; sys.path.insert(0, ROOT)
import common as c, pandas as pd, numpy as np, collections
LAB_FIX = {'palm-2-l': 'google', 'minicpm-v-2-6': 'openbmb'}  # models.json lacks lab for these
def lab(m):
    return c.lab_of(m) or LAB_FIX.get(m) or 'unknown'
def kind(src):
    if src is None: return None
    if src in ('card', 'collected:lab'): return 'claim'
    if src in ('leaderboard', 'epoch', 'collected:board'): return 'indep'
    return 'paper'
def yr_bin(t):
    return 'pre-2023' if t.year < 2023 else str(t.year)

df = c.items()
for t in (85, 95):
    df[f'k{t}_lab'] = df[f'solver{t}'].map(lambda m: lab(m) if m else None)
    df[f'k{t}_kind'] = df[f'solver{t}_source'].map(kind)
df['born95'] = df['solved95'].notna() & (df['solved95'] < df['released'] + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1))
S = {x['id']: x for x in c.summaries()}
CARDS = pd.DataFrame(c.CARDS); CARDS['date'] = pd.to_datetime(CARDS['date'])
