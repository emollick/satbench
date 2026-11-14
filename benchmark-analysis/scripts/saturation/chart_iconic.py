"""A3: small multiples of best-score-over-time for eight landmark benchmarks."""
from sat_calc import *
import matplotlib.pyplot as plt, matplotlib.dates as mdates

IDS = ['mmlu', 'gsm8k', 'humaneval', 'math', 'gpqa-diamond', 'swe-bench-verified', 'humanitys-last-exam', 'arc-agi-2']
T = sat_table(IDS)
fig = c.new_figure(12, 6.75, top=0.755, bottom=0.175, left=0.06, right=0.985)
gs = fig.add_gridspec(2, 4, hspace=0.45, wspace=0.14)
x0, x1 = pd.Timestamp('2020-01-01'), pd.Timestamp('2027-01-01')
for i, k in enumerate(IDS):
    ax = fig.add_subplot(gs[i // 4, i % 4])
    r = T.loc[k]; col = c.AREA_COLORS[r.area]
    f = frontier(k)
    f = pd.concat([f, pd.DataFrame([{'date': AS_OF, 'value': f.value.iloc[-1]}])], ignore_index=True)
    rel = r.released
    pre = f[f.date <= rel]; post = f[f.date >= rel]
    # stitch: post starts at release with the pre-release best
    if len(pre):
        post = pd.concat([pd.DataFrame([{'date': rel, 'value': pre.value.iloc[-1]}]), post], ignore_index=True)
        ax.step(pd.concat([pre.date, pd.Series([rel])]), list(pre.value) + [pre.value.iloc[-1]], where='post', color=col, lw=1.6, alpha=0.35, ls=(0, (2, 1.5)))
    ax.step(post.date, post.value, where='post', color=col, lw=2.4)
    ax.axhline(85, color=c.INK2, lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.axhline(95, color=c.INK2, lw=0.8, ls=(0, (1, 2)), zorder=1)
    ax.axvline(rel, color=c.MUTED, lw=1.0, zorder=1)
    if pd.notna(r.eff85):
        ax.scatter([r.eff85], [f[f.date >= r.sat85].value.iloc[0]], s=36, color=col, edgecolor='white', lw=1.2, zorder=5)
        note = 'past 85% at release' if r.on_arrival else f'85% after {r.m85:.0f} mo'
    else:
        note = f'best {r.best:.0f}% so far'
    ax.set_title(r['name'], loc='left', fontsize=13.5, fontweight='bold', color=c.INK, pad=4)
    ax.text(0.0, 1.0, '', transform=ax.transAxes)
    if rel.year < 2023:
        ax.text(0.98, 0.04, note, transform=ax.transAxes, ha='right', va='bottom', fontsize=11, color=c.INK)
    else:
        ax.text(0.03, 0.58, note, transform=ax.transAxes, ha='left', va='center', fontsize=11, color=c.INK)
    ax.set_xlim(x0, x1); ax.set_ylim(0, 102)
    ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_yticks([0, 25, 50, 85, 100]); ax.yaxis.grid(False)
    for yv in (25, 50): ax.axhline(yv, color=c.GRID, lw=0.7, zorder=0)
    if i % 4: ax.set_yticklabels([])
    else: ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.tick_params(labelsize=10.5)
    ax.grid(False); ax.grid(axis='y', color=c.GRID, lw=0.6)
    for yv in (25, 50):
        pass
c.header(fig, 'One by one, the "hard" benchmarks hit the ceiling',
         'Best reported score over time on eight landmark AI benchmarks. Dashed: 85%; dotted: 95%; gray vertical\n'
         'line: benchmark release. Faded line: models older than the benchmark, tested later. Only Humanity\'s Last Exam is below 85%.')
c.footer(fig, 'Best score from any source (official leaderboards, Epoch AI, lab launch-post claims), dated by model release. Settings vary across sources\n'
              '(tools, sampling, test subsets). ARC-AGI-2: ARC Prize leaderboard plus lab claims. MATH: no scores before 2023 in the data.')
c.save(fig, OUTDIR + 'iconic_benchmarks_best_score.png')
print(T[['released', 'sat85', 'm85', 'm95', 'best', 'pre_best']])
