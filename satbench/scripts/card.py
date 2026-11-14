import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))  # satbench/scripts
import sys; sys.path.insert(0, ROOT)
from common import *
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'share')
df = items()
s = satbench_series(df, start='2023-01-01')
fig = plt.figure(figsize=(12, 6.75), dpi=200)
fig.text(0.04, 0.95, 'SatBench: the benchmark of benchmarks', fontsize=29, fontweight='bold', color=INK, va='top')
fig.text(0.04, 0.865, 'Its 173 questions are the AI benchmarks labs cite most.\nA benchmark counts as solved once the best AI score reaches 85%.',
         fontsize=15, color=MUTED, va='top')
# left: big number + line
fig.text(0.04, 0.73, '63%', fontsize=72, fontweight='bold', color=BLUES[4], va='top')
fig.text(0.255, 0.695, 'solved', fontsize=22, color=INK, va='top', fontweight='bold')
fig.text(0.255, 0.632, '109 of 173 benchmarks,\nNov 2026', fontsize=15, color=MUTED, va='top', linespacing=1.3)
ax = fig.add_axes([0.065, 0.18, 0.37, 0.33])
ax.plot(s.date, s.score, color=BLUES[4], lw=3.2)
ax.axhline(85, color=MUTED, ls=(0, (4, 3)), lw=1.2)
ax.text(s.date.iloc[0], 87.5, 'saturated (85%)', fontsize=12.5, color=MUTED)
ax.set_ylim(0, 100); ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(['0', '25', '50', '75', '100%'], fontsize=13)
ax.set_xlim(s.date.iloc[0], s.date.iloc[-1] + pd.Timedelta(days=40))
ax.set_xticks(pd.to_datetime(['2023-01-01', '2024-01-01', '2025-01-01', '2026-01-01'])); ax.set_xticklabels(['2023', '2024', '2025', '2026'], fontsize=13)
ax.grid(axis='x', visible=False)
ax.annotate('flat near 30% for two years:\nnew tests arrived as fast\nas old ones fell', xy=(pd.Timestamp('2024-06-01'), 30), xytext=(pd.Timestamp('2023-06-01'), 48),
            fontsize=12, color=MUTED, arrowprops=dict(arrowstyle='-', color=FAINT, lw=1))
ax.plot([s.date.iloc[-1]], [s.score.iloc[-1]], 'o', color=BLUES[4], ms=8)
# right: stat rows
rows = [
    ('86%', 'The 2023 edition is saturated', 'Its 44 benchmarks passed 85% in Sep 2026'),
    ('14 mo', 'Median time to solve a 2025 test', '20 months for 2023 and 2024 tests'),
    ('2028', "Today's tests 85% solved, at 2026 pace", 'But new, harder tests keep arriving'),
    ('OpenAI', 'Has saturated the most tests (20)', 'Anthropic leads in 2026 (11)'),
    ('74%', "Humanity's Last Exam, top holdout", 'Also unsolved: MMMU-Pro, SciCode, IFBench'),
]
y0, dy = 0.71, 0.112
fig.add_artist(plt.Line2D([0.475, 0.475], [0.17, 0.73], color=GRID, lw=1.5, transform=fig.transFigure))
for i, (big, a, b) in enumerate(rows):
    y = y0 - i * dy
    fig.text(0.50, y, big, fontsize=25, fontweight='bold', color=BLUES[4] if i != 4 else ACCENT, va='top')
    fig.text(0.645, y - 0.002, a, fontsize=14.5, color=INK, va='top', fontweight='bold')
    fig.text(0.645, y - 0.044, b, fontsize=13.5, color=MUTED, va='top')
notes = ['SatBench: benchmarks named in 10+ AI lab launch posts, scored in %. Best score from any source, including labs\' own launch posts;',
         'counting only independent runs, 24% are solved. Leader = first model recorded at 85%+ on tests several labs report. 2028 is an extrapolation.', CREDIT]
for i, line in enumerate(reversed(notes)):
    fig.text(0.04, 0.025 + i * 0.033, line, fontsize=11.5, color=FAINT, va='bottom')
save(fig, f'{OUT}/satbench_summary_card.png')
