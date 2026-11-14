import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys; sys.path.insert(0, os.path.join(ROOT, 'labs'))
from data import *
import matplotlib.pyplot as plt
from common import BLUES, GREY, INK, MUTED, figure, save
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'labs')
k = df[df.solved85.notna() & ~df.born_solved].copy()
k['ofc'] = k.apply(lambda r: sum(1 for q in S[r.id]['cites'] if q['lab'] in c.FRONTIER_LABS and q['lab'] != r.k85_lab), axis=1)
k['own'] = k.apply(lambda r: sum(1 for q in S[r.id]['cites'] if q['lab'] == r.k85_lab) / len(S[r.id]['cites']), axis=1)
allc = k.k85_lab.value_counts(); con = k[k.ofc >= 5].k85_lab.value_counts()
labs = ['openai', 'google', 'anthropic', 'qwen', 'bytedance', 'meta']
rest_all = allc.drop(labs, errors='ignore').sum(); rest_con = con.drop(labs, errors='ignore').sum()
A = [allc.get(l, 0) for l in labs] + [rest_all]; C_ = [con.get(l, 0) for l in labs] + [rest_con]
own = [k[k.k85_lab == l].own.median() for l in labs]
names = [c.lab_name(l).replace(' DeepMind', '').replace(' Seed', '') for l in labs] + ['Other labs']
fig, ax = figure('Most of Qwen\'s "kills" are on tests only Qwen reports',
                 'Benchmarks each lab\'s model first took past 85%. Grey: all. Blue: only benchmarks that other frontier labs\n'
                 'also report (named in 5+ of their launch posts). Right: share of the benchmark\'s mentions from the lab itself',
                 notes=['"First past 85%" means first recorded. On a test frontier labs never run, any model that reports it gets the credit, even if others could score higher.',
                        f'Born-solved items excluded. {len(k)} kills in all, {int((k.ofc>=5).sum())} on contested benchmarks. Using 3+ or 10+ mentions instead: Qwen 7 or 0; top three unchanged.'],
                 rect=[0.17, 0.25, 0.58, 0.43])
y = np.arange(len(names))[::-1]
ax.barh(y + 0.19, A, height=0.36, color=GREY, alpha=0.7)
ax.barh(y - 0.19, C_, height=0.36, color=BLUES[3])
for yi, a, b in zip(y, A, C_):
    ax.text(a + 0.3, yi + 0.19, f'{a}', va='center', fontsize=14, color=MUTED)
    ax.text(b + 0.3, yi - 0.19, f'{b}', va='center', fontsize=15, color=INK, fontweight='bold')
ax.set_yticks(y); ax.set_yticklabels(names, fontsize=16)
ax.set_xlim(0, 27); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.set_xlabel('benchmarks first taken past 85%')
fig.text(0.81, 0.69, 'own share\nof mentions', fontsize=13.5, color=MUTED, ha='center', va='bottom')
for yi, o in zip(y[:-1], own):
    xf, yf = ax.transData.transform((0, yi))
    fy = fig.transFigure.inverted().transform((xf, yf))[1]
    fig.text(0.81, fy, f'{100*o:.0f}%', fontsize=16, color=INK if o < 0.4 else '#D9542B', ha='center', va='center', fontweight='bold' if o >= 0.4 else 'normal')
save(fig, f'{OUT}/labs_kills_contested.png')
print(dict(zip(names, zip(A, C_, own))))
