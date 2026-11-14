import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'items'))
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import common as c
from analysis import df, holdouts, months_to_solve, km_median, AS_OF, MO

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'items')
SHORT = {'aa-lcr-artificial-analysis-long-context-reasoning': 'AA-LCR (long context)'}
FLAG = {'humanitys-last-exam': 'audit: ~29% of chem/bio answers disputed',
        'automationbench': 'audit: broken grader; fixed fork 92%'}


def fmt_month(t):
    return t.strftime('%b %Y')


# ------------------------------------------------------------------ 1. holdouts
def chart_holdouts(n_min=28):
    h = holdouts()
    h = h[h.n_cites >= n_min].reset_index(drop=True)
    n = len(h)
    fig, ax = c.figure('The last holdouts: most still moving, a few stalled',
                       f'The {n} most-cited SatBench items still below 85%: best score a year ago (grey) and now (orange;\n'
                       'hollow = lab self-report). Naive date = the past year\'s straight-line pace, extended to 85%.',
                       notes=['* since release (item released after Nov 2025). Orange month = no new best in 6+ months. Scores dated by model release.',
                              'Best scores mix harnesses, tool use and lab claims. Naive dates are not forecasts.',
                              '\u2020 published audit: HLE (FutureHouse: ~29% of chem/bio answers disputed); AutomationBench (Prime Intellect: grader/task bugs).'],
                       rect=[0.215, 0.235, 0.40, 0.515])
    y = np.arange(n)[::-1]
    ax.axvline(85, color=c.INK, lw=1.4, ls=(0, (4, 3)), zorder=1)
    ax.text(85, n - 0.45, '85%', ha='center', va='bottom', fontsize=14, color=c.INK, fontweight='bold')
    T = ax.get_yaxis_transform()
    X_NOW, X_GAIN, X_LAST, X_ETA = 1.12, 1.30, 1.38, 1.66
    for yi, r in zip(y, h.itertuples()):
        ax.plot([r.start_v, r.best], [yi, yi], color=c.BLUES[1], lw=3, solid_capstyle='round', zorder=2)
        ax.scatter([r.start_v], [yi], s=70, color=c.GREY, zorder=3, lw=0)
        card = r.best_source == 'card'
        ax.scatter([r.best], [yi], s=120, zorder=4, facecolor=c.BG if card else c.ACCENT, edgecolor=c.ACCENT, lw=2.4)
        name = SHORT.get(r.id, r.name) + (' \u2020' if r.id in FLAG else '')
        ax.text(-0.02, yi, name, transform=T, ha='right', va='center', fontsize=15, color=c.INK)
        ax.text(X_NOW, yi, f'{r.best:.1f}', transform=T, ha='right', va='center', fontsize=15, color=c.INK, fontweight='bold')
        stalled = (AS_OF - r.best_date).days > 183
        if r.gain <= 0:
            g, eta = 'none', 'no progress'
        else:
            g = (f'+{r.gain:.0f}' if r.gain >= 1 else f'+{r.gain:.1f}') + ('*' if r.base == 'release' else '')
            eta = 'after 2030' if r.eta85.year > 2030 else r.eta85.strftime('%b %Y')
        hot = r.gain <= 0
        ax.text(X_GAIN, yi, g, transform=T, ha='right', va='center', fontsize=15, color=c.ACCENT if hot else c.INK)
        ax.text(X_LAST, yi, r.best_date.strftime('%b %y'), transform=T, ha='left', va='center', fontsize=15,
                color=c.ACCENT if stalled else c.MUTED)
        ax.text(X_ETA, yi, eta, transform=T, ha='left', va='center', fontsize=15, color=c.ACCENT if hot else c.INK,
                fontweight='bold' if hot else 'normal')
    for x, lab, ha in [(X_NOW, 'now', 'right'), (X_GAIN, 'gain', 'right'), (X_LAST, 'last best', 'left'), (X_ETA, 'naive 85%', 'left')]:
        ax.text(x, n - 0.45, lab, transform=T, ha=ha, va='bottom', fontsize=13, color=c.MUTED, linespacing=1.05)
    ax.set_ylim(-0.6, n - 0.4); ax.set_yticks([])
    ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(['0', '25', '50', '75', '100%'])
    ax.grid(axis='y', visible=False)
    c.save(fig, f'{OUT}/holdouts.png')
    return h


# ------------------------------------------------------------------ 2. half-life
def cohort_stats():
    rows = []
    for y in [2023, 2024, 2025, 2026]:
        d = df[df.rel_year == y]
        t, e = months_to_solve(d)
        m, lo, hi, k = km_median(t, e)
        s12 = k[k.t <= 12].S.iloc[-1]
        s6 = k[k.t <= 6].S.iloc[-1]
        rows.append(dict(year=y, n=len(d), solved=int(e.sum()), born=int(d.born_solved.sum()), median=m, lo=lo, hi=hi,
                         follow=t.max(), within12=1 - s12, within6=1 - s6, S_end=k.S.iloc[-1]))
    return pd.DataFrame(rows)


def chart_halflife():
    cs = cohort_stats()
    fig, ax = c.figure('Benchmark half-life: 20 months in 2023-24, 14 in 2025',
                       'Median months from a benchmark\'s release until its best reported score passes 85%, by release year.\n'
                       'Kaplan-Meier, unsolved items censored at Nov 14, 2026. Bars = 95% CI; arrow = upper limit not reached yet.',
                       notes=['Born solved = an existing model already scored 85%+ in the release month (scores are dated by model release).',
                              'Few launch posts before 2025 (12 in 2023, 31 in 2024), so early solve dates may be late. Best scores mix harnesses and lab claims.'],
                       rect=[0.13, 0.25, 0.47, 0.48])
    y = np.arange(len(cs))[::-1]
    xmax = 36
    T = ax.get_yaxis_transform()
    arrow = lambda yi, col, a=1: ax.annotate('', xy=(xmax + 0.6, yi), xytext=(xmax - 2, yi),
                                             arrowprops=dict(arrowstyle='-|>', color=col, alpha=a, lw=0, mutation_scale=24))
    for yi, r in zip(y, cs.itertuples()):
        ax.text(-0.03, yi, str(r.year), transform=T, ha='right', va='center', fontsize=20, fontweight='bold', color=c.INK)
        if np.isfinite(r.median):
            hi = r.hi if np.isfinite(r.hi) else xmax - 1
            ax.plot([r.lo, hi], [yi, yi], color=c.BLUES[1], lw=6, solid_capstyle='round', zorder=2)
            if not np.isfinite(r.hi): arrow(yi, c.BLUES[1])
            ax.scatter([r.median], [yi], s=260, color=c.BLUES[3], zorder=3, edgecolor=c.BG, lw=2)
            ax.text(r.median, yi + 0.28, f'{r.median:.0f} mo', ha='center', va='bottom', fontsize=17, fontweight='bold', color=c.INK)
        else:
            ax.plot([r.follow, xmax - 1], [yi, yi], color=c.ACCENT, lw=6, alpha=0.35, solid_capstyle='butt', zorder=2)
            arrow(yi, c.ACCENT, 0.6)
            ax.scatter([r.follow], [yi], s=120, marker='|', color=c.ACCENT, lw=3, zorder=3)
            ax.text(r.follow, yi + 0.28, f'not reached: >{r.follow:.0f} mo ({r.solved} of {r.n} solved so far)',
                    ha='left', va='bottom', fontsize=16, color=c.INK)
        w6 = f'{100*r.within6:.0f}%'
        w12 = f'{100*r.within12:.0f}%' if r.follow >= 12 else '\u2013'
        for x, v in [(1.13, r.n), (1.29, r.born), (1.46, w6), (1.62, w12)]:
            ax.text(x, yi, str(v), transform=T, ha='right', va='center', fontsize=17, color=c.INK)
    for x, lab in [(1.13, 'items'), (1.29, 'born\nsolved'), (1.46, 'solved\nby 6 mo'), (1.62, 'solved\nby 12 mo')]:
        ax.text(x, len(cs) - 0.4, lab, transform=T, ha='right', va='bottom', fontsize=13, color=c.MUTED, linespacing=1.1)
    ax.set_ylim(-0.5, len(cs) - 0.3); ax.set_yticks([])
    ax.set_xlim(0, xmax + 1); ax.set_xticks([0, 6, 12, 18, 24, 30, 36])
    ax.set_xlabel('months from release to 85%', labelpad=4)
    ax.grid(axis='y', visible=False)
    c.save(fig, f'{OUT}/half_life_by_cohort.png')
    return cs


# ------------------------------------------------------------------ 3. areas
def area_stats():
    rows = []
    for a, d in df.groupby('area'):
        t, e = months_to_solve(d)
        m, lo, hi, _ = km_median(t, e)
        rows.append(dict(area=a, n=len(d), solved=int(e.sum()), share=e.mean(), median=m, lo=lo, hi=hi,
                         rel_med=d.released.median(), unsolved=int((~e).sum())))
    return pd.DataFrame(rows).sort_values('share')


def chart_areas():
    a = area_stats()
    a = a[a.n >= 5].reset_index(drop=True)
    fig, ax = c.figure('Agent and work tests are the least-solved areas',
                       'SatBench items by area: solved (best score 85%+) vs. still unsolved, Nov 14, 2026.\nRight: median release month of the area\'s items.',
                       notes=['Newer areas have had less time: agent and work items are mostly 2025-26 releases. Two single-item areas (safety, other) not shown.'],
                       rect=[0.15, 0.15, 0.55, 0.60])
    y = np.arange(len(a))
    for yi, r in zip(y, a.itertuples()):
        ax.barh(yi, r.solved, color=c.BLUES[3], height=0.62, edgecolor=c.BG, lw=2)
        ax.barh(yi, r.unsolved, left=r.solved, color=c.ACCENT, height=0.62, edgecolor=c.BG, lw=2)
        ax.text(-0.5, yi, r.area.capitalize(), ha='right', va='center', fontsize=18, color=c.INK)
        ax.text(r.n + 0.8, yi, f'{r.solved}/{r.n}  ({100*r.share:.0f}%)', ha='left', va='center', fontsize=16, color=c.INK)
        ax.text(1.40, yi, r.rel_med.strftime('%b %Y'), transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=16, color=c.MUTED)
    ax.text(1.40, len(a) - 0.45, 'median release', transform=ax.get_yaxis_transform(), ha='right', va='bottom', fontsize=13, color=c.MUTED)
    first = a.iloc[-1]
    ax.text(first.solved / 2, len(a) - 0.5, 'solved', ha='center', va='bottom', fontsize=14, color=c.BLUES[3], fontweight='bold')
    ax.text(first.solved + first.unsolved / 2, len(a) - 0.5, 'unsolved', ha='center', va='bottom', fontsize=14, color=c.ACCENT, fontweight='bold')
    ax.set_axisbelow(True)
    ax.set_xlim(0, 50); ax.set_ylim(-0.5, len(a) - 0.1); ax.set_yticks([])
    ax.set_xticks([0, 10, 20, 30, 40, 50]); ax.grid(axis='y', visible=False)
    c.save(fig, f'{OUT}/areas.png')
    return a


# ------------------------------------------------------------------ 4. scorecard
STATES = [('born', 'Born solved', c.GREY), ('s95', 'Solved, 95%+', c.BLUES[4]),
          ('s85', 'Solved, 85-95%', c.BLUES[2]), ('un', 'Unsolved', c.ACCENT)]


def state(r):
    if pd.isna(r.solved85): return 'un'
    if r.born_solved: return 'born'
    if pd.notna(r.solved95): return 's95'
    return 's85'


def chart_scorecard():
    d = df.copy()
    d['state'] = d.apply(state, axis=1)
    d['grp'] = d.rel_year.where(d.rel_year >= 2023, 2022)
    order = {k: i for i, (k, _, _) in enumerate(STATES)}
    total = len(d); solved = int(d.solved85.notna().sum())
    fig = plt.figure(figsize=(12, 6.75), dpi=200)
    fig.text(0.04, 0.955, 'SatBench', fontsize=27, fontweight='bold', color=c.INK, va='top')
    fig.text(0.04, 0.885, 'The benchmark of benchmarks: each square is one of 173 AI benchmarks named in 10+ lab launch posts.\n'
             'Solved = best reported score 85%+. Grouped by the year the benchmark was released.', fontsize=15.5, color=c.MUTED, va='top', linespacing=1.45)
    fig.text(0.04, 0.60, f'{solved}', fontsize=110, fontweight='bold', color=c.BLUES[4], va='baseline')
    fig.text(0.04, 0.53, f'/ {total} solved', fontsize=34, fontweight='bold', color=c.INK, va='baseline')
    fig.text(0.04, 0.475, f'{100*solved/total:.0f}% as of Nov 14, 2026', fontsize=18, color=c.MUTED, va='baseline')
    counts = d.state.value_counts()
    for i, (k, lab, col) in enumerate(STATES):
        yy = 0.39 - i * 0.055
        fig.patches.append(Rectangle((0.04, yy - 0.016), 0.018, 0.032, transform=fig.transFigure, color=col))
        fig.text(0.066, yy, f'{lab}', fontsize=16, color=c.INK, va='center')
        fig.text(0.255, yy, f'{counts.get(k, 0)}', fontsize=16, color=c.INK, va='center', ha='right', fontweight='bold')
    notes = ['Born solved: an existing model already scored 85%+ when the test came out. Best scores mix leaderboards, Epoch AI and lab self-reports.', c.CREDIT]
    for i, line in enumerate(reversed(notes)):
        fig.text(0.04, 0.025 + i * 0.033, line, fontsize=11.5, color=c.FAINT, va='bottom')
    ax = fig.add_axes([0.33, 0.13, 0.64, 0.68]); ax.axis('off')
    groups = [2022, 2023, 2024, 2025, 2026]
    cols = 5; cell = 1.0; gap = 0.16; ggap = 1.3
    x0 = 0
    rows_max = max(int(np.ceil((d.grp == g).sum() / cols)) for g in groups)
    for g in groups:
        sub = d[d.grp == g].copy()
        sub['o'] = sub.state.map(order)
        sub = sub.sort_values(['o', 'best'], ascending=[True, False])
        for i, r in enumerate(sub.itertuples()):
            cx = x0 + (i % cols) * cell; cy = rows_max - 1 - (i // cols) * cell
            col = dict((k, cc) for k, _, cc in STATES)[r.state]
            ax.add_patch(Rectangle((cx + gap / 2, cy + gap / 2), cell - gap, cell - gap, color=col, lw=0))
        lab = '2022 &\nearlier' if g == 2022 else str(g)
        k = int(sub.solved85.notna().sum())
        ax.text(x0 + cols * cell / 2, rows_max + 1.55, lab if g != 2022 else 'pre-2023', ha='center', va='bottom', fontsize=17,
                fontweight='bold', color=c.INK)
        ax.text(x0 + cols * cell / 2, rows_max + 0.25, f'{k}/{len(sub)}', ha='center', va='bottom', fontsize=16, color=c.MUTED)
        x0 += cols * cell + ggap
    ax.set_xlim(-0.2, x0 - ggap + 0.2); ax.set_ylim(-0.2, rows_max + 2.8); ax.set_aspect('equal')
    c.save(fig, f'{OUT}/scorecard.png')
    return d


if __name__ == '__main__':
    h = chart_holdouts(); cs = chart_halflife(); a = chart_areas(); d = chart_scorecard()
    print(cs.to_string()); print(a.to_string()); print(d.groupby(['grp', 'state']).size().unstack(fill_value=0))
