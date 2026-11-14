"""B2: table-chart of every benchmark family that went extinct at the frontier."""
import warnings; warnings.filterwarnings('ignore')
from extinct_calc import *
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm, ListedColormap

E = T[T.extinct].sort_values(['peak'], ascending=False).copy()
NAMES = {'simpleqa': 'SimpleQA (+ Verified)', 'aider': 'Aider Polyglot', 'arena-hard': 'Arena-Hard (Auto, v2)',
         'mmlu': 'MMLU', 'chartqa': 'ChartQA'}
n = len(E)
fig = c.new_figure(10, 12.5, top=0.865, bottom=0.085, left=0.03, right=0.985)
ax = fig.add_axes([0.03, 0.085, 0.955, 0.73])
ax.set_xlim(0, 100); ax.set_ylim(n + 0.2, -2.7)
ax.axis('off')
X = dict(name=0.6, bar=21.5, bar_w=10, heat=37, last=64.5, best=70.5, tail=77, cause=79)
cell_w = 3.6
# sequential bins for share heat cells
bins = [0, 0.001, 5, 15, 30, 50, 101]
cols_bins = ['#f0efec', c.SEQ_BLUE[0], c.SEQ_BLUE[1], c.SEQ_BLUE[3], c.SEQ_BLUE[5], c.SEQ_BLUE[7]]
def cell_color(v):
    for lo, hi, col in zip(bins[:-1], bins[1:], cols_bins):
        if lo <= v < hi: return col
    return cols_bins[-1]
hdr = dict(fontsize=10.5, color=c.INK2, va='bottom', fontweight='bold')
ax.text(X['name'] + 1.6, -0.75, 'Benchmark', ha='left', **hdr)
ax.text(X['bar'], -0.75, 'Peak share of\nall launch posts', ha='left', **hdr)
ax.text(X['heat'], -1.35, 'Share of frontier-lab posts', ha='left', **hdr)
for j, lab in enumerate(['23-24', '25H1', '25H2', '26H1', '26H2']):
    ax.text(X['heat'] + j * (cell_w + 0.35) + cell_w / 2, -0.75, lab, ha='center', fontsize=9.5, color=c.INK2, va='bottom')
ax.text(X['last'], -0.75, 'Last\nfrontier\npost', ha='right', **hdr)
ax.text(X['best'], -0.75, 'Best\nscore\nthen', ha='right', **hdr)
ax.text(X['cause'], -0.75, 'Why it went\n(→ successor)', ha='left', **hdr)
ax.text(X['tail'], -0.75, 'Others,\nlast\n6 mo', ha='right', **hdr)
for i, (f, r) in enumerate(E.iterrows()):
    y = i
    if i % 2 == 0:
        ax.add_patch(Rectangle((0, y - 0.5), 100, 1, color='#f3f2ee', zorder=0, lw=0))
    ax.scatter([X['name']], [y], s=55, color=c.AREA_COLORS[r.area], zorder=3, edgecolor='white', lw=0.8)
    ax.text(X['name'] + 1.6, y, NAMES.get(f, r['name']), va='center', ha='left', fontsize=11.5, color=c.INK)
    w = r.peak / 100 * X['bar_w']
    ax.add_patch(Rectangle((X['bar'], y - 0.28), w, 0.56, color=c.INK2, lw=0, zorder=2))
    ax.text(X['bar'] + w + 0.6, y, f"{r.peak:.0f}%", va='center', ha='left', fontsize=10.5, color=c.INK)
    for j, p in enumerate(PERIODS):
        v = r[f'shF {p}']
        ax.add_patch(Rectangle((X['heat'] + j * (cell_w + 0.35), y - 0.36), cell_w, 0.72, color=cell_color(v), lw=0, zorder=2))
    ax.text(X['last'], y, f"{r.lastF:%b '%y}", va='center', ha='right', fontsize=10.5, color=c.INK)
    ax.text(X['best'], y, f"{r.best_end:.0f}%" if pd.notna(r.best_end) else 'n/a', va='center', ha='right', fontsize=10.5, color=c.INK)
    sat = pd.notna(r.best_end) and r.best_end >= 85
    why = 'Saturated' if sat else ('No % score' if pd.isna(r.best_end) else 'Not saturated')
    t = ax.text(X['cause'], y, why, va='center', ha='left', fontsize=10.5, color=c.INK if sat else '#b4372f')
    if isinstance(r.succ_name, str):
        ax.annotate(f" → {r.succ_name.replace('BIG-Bench Extra Hard', 'BBEH')}", xycoords=t, xy=(1, 0.5), va='center', ha='left', fontsize=9.5, color=c.INK2)
    ax.text(X['tail'], y, f"{int(r.recNF)}" if r.recNF else '–', va='center', ha='right', fontsize=10.5, color=c.INK)
# legend for heat cells
lx, ly = X['heat'], n + 0.15
labels = ['0', '<5%', '5-15%', '15-30%', '30-50%', '50%+']
for k, (col, lab) in enumerate(zip(cols_bins, labels)):
    ax.add_patch(Rectangle((lx + k * 8.5, ly - 0.25), 1.6, 0.5, color=col, lw=0, clip_on=False))
    ax.text(lx + k * 8.5 + 2.0, ly, lab, va='center', ha='left', fontsize=9.5, color=c.INK2)
nsat = int(((E.best_end >= 85)).sum())
c.header(fig, f'{nsat} of {n} benchmarks that went extinct were saturated first',
         'Benchmarks once named in 10%+ of AI lab launch posts (in some half-year) that now appear in at most one\n'
         'frontier-lab launch post in the last 6 months. Versions of a test are merged: AIME 2024 to AIME 2025\n'
         'is a version change, not an extinction. Sorted by peak share.')
c.footer(fig, f"Best score then = best reported score by the date of the last frontier-lab post; saturated = 85%+. Arrow: successor the Almanac names.\n"
              f"Other labs, last 6 mo = launch posts by non-frontier labs naming it since May 14, 2026 (of {META['nNF6']}). 2023-24 shares rest on 34 frontier-lab posts.")
c.save(fig, OUTDIR + 'extinct_benchmarks_table.png')
print(E[['name', 'peak', 'lastF', 'best_end', 'succ_name', 'recNF']].round(1).to_string())
