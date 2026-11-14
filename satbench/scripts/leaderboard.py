import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))  # satbench/scripts
import sys; sys.path.insert(0, os.path.join(ROOT, 'labs')); sys.path.insert(0, ROOT)
from data import *
import matplotlib.pyplot as plt
from common import BLUES, INK, MUTED, FAINT, save, BG, CREDIT
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'share')
k = df[df.solved85.notna() & ~df.born_solved].copy()
k['ofc'] = k.apply(lambda r: sum(1 for q in S[r.id]['cites'] if q['lab'] in c.FRONTIER_LABS and q['lab'] != r.k85_lab), axis=1)
kc = k[k.ofc >= 5]
labs = ['openai', 'google', 'anthropic', 'meta', 'bytedance', 'qwen']
names = ['OpenAI', 'Google', 'Anthropic', 'Meta', 'ByteDance', 'Qwen', 'All other labs']
pre = [int(((kc.k85_lab == l) & (kc.solved85.dt.year < 2026)).sum()) for l in labs]
now = [int(((kc.k85_lab == l) & (kc.solved85.dt.year >= 2026)).sum()) for l in labs]
oth = kc[~kc.k85_lab.isin(labs)]
pre.append(int((oth.solved85.dt.year < 2026).sum())); now.append(int((oth.solved85.dt.year >= 2026).sum()))
short = {'Berkeley Function Calling Leaderboard (BFCL)': 'BFCL', 'SWE-bench Multilingual': 'SWE-bench Multilingual'}
ex = []
for l in labs:
    d = kc[kc.k85_lab == l].sort_values('n_cites', ascending=False)
    ex.append(', '.join(short.get(n, n) for n in d.name.head(2)))
ex.append('')

fig = plt.figure(figsize=(12, 6.75), dpi=200)
fig.text(0.04, 0.95, 'OpenAI has saturated the most AI benchmarks.', fontsize=28, fontweight='bold', color=INK, va='top')
fig.text(0.04, 0.875, 'Anthropic is saturating the most in 2026.', fontsize=28, fontweight='bold', color=BLUES[4], va='top')
fig.text(0.04, 0.79, 'SatBench leaderboard: widely used benchmarks where each lab\'s model was the first to score 85%+',
         fontsize=16, color=MUTED, va='top')
ax = fig.add_axes([0.20, 0.16, 0.40, 0.52])
y = np.arange(len(names))[::-1]
ax.barh(y, pre, height=0.66, color=BLUES[1])
ax.barh(y, now, left=pre, height=0.66, color=BLUES[4])
for yi, p, n in zip(y, pre, now):
    ax.text(p + n + 0.3, yi, f'{p+n}', va='center', fontsize=22, fontweight='bold', color=INK)
ax.set_yticks(y); ax.set_yticklabels(names, fontsize=20, color=INK)
ax.set_xlim(0, 22); ax.set_ylim(-0.6, len(names) - 0.4); ax.set_xticks([]); ax.grid(False)
ax.tick_params(axis='y', length=0)
for s in ax.spines.values(): s.set_visible(False)
fig.canvas.draw()
for yi, e in zip(y, ex):
    fy = fig.transFigure.inverted().transform(ax.transData.transform((0, yi)))[1]
    fig.text(0.665, fy, e, fontsize=14, color=MUTED, va='center')
fig.text(0.665, 0.70, 'e.g.', fontsize=14, color=FAINT, va='center')
for x0, col, lab in [(0.20, BLUES[1]), (0.335, BLUES[4])] and [(0.20, BLUES[1], 'before 2026'), (0.335, BLUES[4], 'in 2026')]:
    fig.patches.append(plt.Rectangle((x0, 0.686), 0.016, 0.028, transform=fig.transFigure, color=col))
    fig.text(x0 + 0.022, 0.70, lab, fontsize=15, color=MUTED, va='center')
notes = [f'Counts the {len(kc)} SatBench benchmarks (named in 10+ AI lab launch posts) where a lab\'s model was the first recorded to reach 85%,',
         'among benchmarks several frontier labs report. Best scores include labs\' own launch-post results.', CREDIT]
for i, line in enumerate(reversed(notes)):
    fig.text(0.04, 0.025 + i * 0.033, line, fontsize=11.5, color=FAINT, va='bottom')
save(fig, f'{OUT}/satbench_leaderboard.png')
