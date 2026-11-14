import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))  # satbench/scripts
import sys; sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'items'))
from common import *
import analysis as A
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'share')
df = items(); df['rel_year'] = df.released.dt.year
fig = plt.figure(figsize=(12, 6.75), dpi=200)
fig.text(0.04, 0.95, 'Each year\'s new AI benchmarks get beaten faster', fontsize=28, fontweight='bold', color=INK, va='top')
fig.text(0.04, 0.865, 'Share of benchmarks solved (best AI score reaches 85%), by months since the benchmark came out,\ngrouped by the year it was released',
         fontsize=15.5, color=MUTED, va='top', linespacing=1.4)
ax = fig.add_axes([0.08, 0.245, 0.60, 0.47])
cols = {2023: BLUES[0], 2024: BLUES[1], 2025: BLUES[3], 2026: BLUES[4]}
cols[2023] = '#A9A6A0'
at12 = {}; at6 = {}
for y in [2023, 2024, 2025, 2026]:
    d = df[df.rel_year == y]
    t, e = A.months_to_solve(d)
    k = A.km(t, e)
    fu = t.max()
    xs = list(k.t) + [fu]; ys = [100 * (1 - s) for s in k.S] + [100 * (1 - k.S.iloc[-1])]
    xs = [x for x in xs if x <= 40]; ys = ys[:len(xs)]
    if xs[-1] < min(fu, 40): xs.append(min(fu, 40)); ys.append(ys[-1])
    ax.step(xs, ys, where='post', color=cols[y], lw=4 if y >= 2025 else 3.2, ls=(0, (3, 1.5)) if y == 2026 else '-', solid_capstyle='round')
    lab = f'{y}' + (' (so far)' if y == 2026 else '')
    dy = {2023: 4, 2024: -5, 2026: 6}.get(y, 0)
    tx, ty = (0.6, 44) if y == 2026 else (xs[-1] + 0.6, ys[-1] + dy)
    ax.text(tx, ty, lab, fontsize=17, fontweight='bold', color=cols[y] if y != 2023 else '#8F8C86', va='center')
    at12[y] = 100 * (1 - k[k.t <= 12].S.iloc[-1]) if fu >= 12 else None
    at6[y] = 100 * (1 - k[k.t <= 6].S.iloc[-1])
    print(y, len(d), round(fu, 1), at6[y], at12[y])
ax.axvline(12, color=FAINT, lw=1.2, ls=':')
ax.text(12.4, 96, 'one year', fontsize=14, color=MUTED, va='top')
ax.set_xlim(0, 44); ax.set_xticks([0, 6, 12, 18, 24, 30, 36]); ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(['0', '25', '50', '75', '100%'])
ax.set_xlabel('months since the benchmark was released'); ax.grid(axis='x', visible=False)
# right panel: within one year
fig.text(0.775, 0.73, 'Solved within\na year of release', fontsize=16, fontweight='bold', color=INK, va='top', linespacing=1.3)
for i, y in enumerate([2023, 2024, 2025, 2026]):
    yy = 0.58 - i * 0.095
    v = at12[y]
    fig.text(0.775, yy, f'{y}', fontsize=18, color=MUTED, va='center')
    fig.text(0.955, yy, f'{v:.0f}%' if v is not None else f'{at6[y]:.0f}%*', fontsize=26, fontweight='bold',
             color=cols[y] if y != 2023 else '#8F8C86', va='center', ha='right')
fig.text(0.775, 0.235, '* 2026: within 6 months\n(vs 0%, 18%, 21% before)', fontsize=12.5, color=FAINT, va='top', linespacing=1.3)
notes = ['Benchmarks named in 10+ AI lab launch posts (2023: 18, 2024: 44, 2025: 56, 2026: 29). Kaplan-Meier: unsolved benchmarks count until today.',
         'Best score from any source, including labs\' own launch posts. Benchmarks already past 85% when released count as solved at month 0.', CREDIT]
for i, line in enumerate(reversed(notes)):
    fig.text(0.04, 0.025 + i * 0.033, line, fontsize=11.5, color=FAINT, va='bottom')
save(fig, f'{OUT}/satbench_by_year.png')
