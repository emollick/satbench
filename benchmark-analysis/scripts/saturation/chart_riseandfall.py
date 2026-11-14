"""B1: rise and fall of the most-cited benchmarks that went extinct at the frontier."""
import warnings; warnings.filterwarnings('ignore')
from extinct_calc import *
import matplotlib.pyplot as plt

FAMS = ['mmlu', 'humaneval', 'gsm8k', 'math', 'big-bench-hard', 'hellaswag', 'drop', 'arc-challenge',
        'mmmu', 'math-500', 'simpleqa', 'aider']
assert all(T.loc[f, 'extinct'] for f in FAMS)
NAMES = {'simpleqa': 'SimpleQA (+ Verified)', 'aider': 'Aider Polyglot', 'big-bench-hard': 'BIG-Bench Hard'}
xl = ['2023–24', "'25 H1", "'25 H2", "'26 H1", "'26 H2"]
fig = c.new_figure(12, 6.75, top=0.775, bottom=0.165, left=0.06, right=0.985)
gs = fig.add_gridspec(3, 4, hspace=0.62, wspace=0.12)
x = np.arange(5)
for i, f in enumerate(FAMS):
    ax = fig.add_subplot(gs[i // 4, i % 4])
    r = T.loc[f]; col = c.AREA_COLORS[r.area]
    yF = [r[f'shF {p}'] for p in PERIODS]; yN = [r[f'shNF {p}'] for p in PERIODS]
    ax.plot(x, yN, color=c.INK2, lw=1.4, ls=(0, (3, 2)), marker='o', ms=3.5, zorder=2)
    ax.plot(x, yF, color=col, lw=2.6, marker='o', ms=5, markeredgecolor='white', mew=1, zorder=3)
    ax.set_ylim(0, 100); ax.set_xlim(-0.25, 4.25)
    ax.set_yticks([0, 50, 100])
    if i % 4: ax.set_yticklabels([])
    else: ax.set_yticklabels(['0', '50%', '100%'])
    ax.set_xticks(x)
    ax.set_xticklabels(xl if i >= 8 else [''] * 5, fontsize=9.5)
    ax.tick_params(axis='y', labelsize=10)
    ax.grid(axis='x', visible=False)
    ax.set_title(NAMES.get(f, r['name']), loc='left', fontsize=12.5, fontweight='bold', color=c.INK, pad=3)
    ax.text(4.2, 97, f"last frontier post: {r.lastF:%b %Y}", fontsize=9.5, color=c.INK2, ha='right', va='top')
dF = META['denF']; d = META['den']
c.header(fig, 'The 2023 benchmark canon is extinct at the frontier',
         'Share of AI lab launch posts naming each benchmark, by half-year. Colored: posts by the 9 frontier labs; dashed gray: all other\n'
         'labs. "Extinct" here: named in 10%+ of posts at its peak, then in at most 1 frontier-lab post in the last 6 months.')
pl = {'2023-24': '2023-24', '2025 H1': "'25 H1", '2025 H2': "'25 H2", '2026 H1': "'26 H1", '2026 H2': "'26 H2"}
c.footer(fig, "Launch posts per period (frontier / other labs): " + ', '.join(f"{pl[p]} {dF[p]}/{d[p]-dF[p]}" for p in PERIODS) +
         " ('26 H2 to Nov 14). 2023-24 pooled: few posts recorded.\n"
         "Frontier labs: Anthropic, OpenAI, Google, Moonshot, Meta, DeepSeek, xAI, Qwen, Z.ai. Most 2026 frontier-lab citations of the old canon are DeepSeek base-model tables.")
c.save(fig, OUTDIR + 'extinct_rise_and_fall.png')
