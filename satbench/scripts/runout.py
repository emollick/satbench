import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))  # satbench/scripts
import sys; sys.path.insert(0, ROOT)
from common import *
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'share')
rng = np.random.default_rng(7)
df = items()
s = satbench_series(df, start='2023-01-01')
s['unsolved'] = s.n_items - s.solved
U0 = int(s.unsolved.iloc[-1])
# hazard over last 12 months from item-months at risk (not born solved)
t0 = AS_OF - pd.DateOffset(months=12)
risk = ev = 0
for _, r in df.iterrows():
    if r.born_solved: continue
    start = max(r.released, t0); end = min(r.solved85, AS_OF) if pd.notna(r.solved85) else AS_OF
    if end <= start: continue
    risk += (end - start).days / 30.44
    if pd.notna(r.solved85) and t0 < r.solved85 <= AS_OF: ev += 1
h = ev / risk
rel25 = df[df.released.dt.year == 2025]; arr = len(rel25) / 12
p0 = df[df.released.dt.year >= 2025].born_solved.mean()
print('hazard', ev, round(risk), h, 'arrivals', arr, 'born', p0, 'U0', U0)
M = 12 * 14; months = pd.date_range(AS_OF, periods=M + 1, freq='30D')
N = 2000
def sim(arrivals, hz_fn):
    out = np.zeros((N, M + 1))
    for n in range(N):
        hb = rng.gamma(ev, 1 / risk) / h  # parameter uncertainty multiplier
        u = U0; out[n, 0] = u
        for m in range(1, M + 1):
            hm = min(hz_fn(m) * hb, 0.95)
            u -= rng.binomial(u, hm)
            if arrivals: u += rng.binomial(rng.poisson(arrivals), 1 - p0)
            out[n, m] = u
    return out
A = sim(0, lambda m: h)
B = sim(arr, lambda m: h)
C = sim(arr, lambda m: h + 0.01 * m / 12)   # solve rate +1 point per year, as 2024->2025->2026
zero = np.array([np.argmax(r == 0) if (r == 0).any() else np.nan for r in A])
q = lambda x, p: np.nanpercentile(x, p)
zd = [AS_OF + pd.Timedelta(days=30.44 * q(zero, p)) for p in (10, 50, 90)]
print('A zero dates', [d.strftime('%b %Y') for d in zd], 'never', np.isnan(zero).mean())
for nm, X in [('A', A), ('B', B), ('C', C)]:
    for yrs in [2, 4, 8, 14]:
        print(nm, yrs, np.median(X[:, 12 * yrs]))
fig = plt.figure(figsize=(12, 6.75), dpi=200)
fig.text(0.04, 0.955, 'When will SatBench be Saturated?', fontsize=28, fontweight='bold', color=INK, va='top')
fig.text(0.04, 0.88, 'Today\'s set: 2028. With new benchmarks and faster solving: ~2030.', fontsize=24, fontweight='bold', color=BLUES[4], va='top')
fig.text(0.04, 0.80, 'Saturated = 85% of its benchmarks solved. Lines show widely used AI benchmarks still unsolved.',
         fontsize=15.5, color=MUTED, va='top', linespacing=1.4)
ax = fig.add_axes([0.075, 0.225, 0.66, 0.50])
ax.plot(s.date, s.unsolved, color=INK, lw=3.2)
ent = [((df.released.dt.year == 2026) & (df.released <= t)).sum() for t in s.date]
miss = np.array([max(0.0, arr * ((t - pd.Timestamp('2026-01-01')).days / 30.44 + 1) - e) if t >= pd.Timestamp('2026-01-01') else 0.0 for t, e in zip(s.date, ent)])
adj = s.unsolved + miss * (1 - p0) * 0.85
m26 = s.date >= pd.Timestamp('2025-12-01')
ax.plot(s.date[m26], adj[m26], color=MUTED, lw=2.2, ls=(0, (1.5, 1.5)))
ax.text(pd.Timestamp('2023-03-01'), 86, f'Dotted: ~{adj.iloc[-1]:.0f} if this\nyear\'s new benchmarks\nwere all counted', fontsize=11.5, color=MUTED, ha='left')
print('adjusted now', adj.iloc[-1])
specs = [(C, BLUES[3], 'If AI benchmark solving\nrates continue to\nspeed up'), (A, ACCENT, 'If no new benchmarks\nare made after today')]
tot = 173 + arr * np.arange(M + 1)
for X, col, lab in specs:
    med = np.median(X, axis=0); lo = np.percentile(X, 10, axis=0); hi = np.percentile(X, 90, axis=0)
    ax.fill_between(months, lo, hi, color=col, alpha=0.18, lw=0)
    ax.plot(months, med, color=col, lw=3, ls=(0, (4, 2)))
    T = tot if X is C else np.full(M + 1, 173)
    i = int(np.argmax(1 - med / T >= 0.85))
    ax.plot([months[i]], [med[i]], 'o', color=col, ms=11, mec=BG, mew=2, zorder=5)
    print('sat', lab[:10], months[i].date(), med[i])
    if X is C:
        ax.text(months[i], med[i] + 7, f'SatBench saturated\n~{months[i].year}', ha='center', va='bottom', fontsize=13.5, color=col, fontweight='bold')
    else:
        ax.text(months[i] + pd.Timedelta(days=90), med[i] + 2, f'SatBench saturated ~{months[i].year}', ha='left', va='bottom', fontsize=13.5, color=col, fontweight='bold')
    ax.text(months[-1] + pd.Timedelta(days=60), med[-1] + (14 if col == BLUES[3] else 0), lab, color=col, fontsize=14.5, fontweight='bold', va='center', linespacing=1.2)
ax.axvline(AS_OF, color=FAINT, lw=1)
ax.text(AS_OF - pd.Timedelta(days=40), 112, 'today', ha='right', fontsize=13.5, color=MUTED)
ax.text(s.date.iloc[-1] - pd.Timedelta(days=30), 20, f'{U0} unsolved\ntoday', va='top', ha='right', fontsize=14, color=INK, fontweight='bold')
zm = zd[1]
ax.annotate(f'Last one falls around {zm.year}\n(80% range {zd[0].year}-{zd[2].year})', xy=(zm, 0), xytext=(pd.Timestamp('2035-03-01'), 5), va='bottom',
            fontsize=14, color=ACCENT, arrowprops=dict(arrowstyle='-', color=ACCENT, lw=1.2))
ax.plot([zm], [0], 'o', color=ACCENT, ms=9)
ax.set_ylim(0, 120); ax.set_xlim(pd.Timestamp('2023-01-01'), months[-1])
ax.set_xticks(pd.to_datetime([f'{y}-01-01' for y in range(2024, 2041, 2)])); ax.set_xticklabels([str(y) for y in range(2024, 2041, 2)])
ax.grid(axis='x', visible=False); ax.set_ylabel('unsolved benchmarks')
notes = [f'Benchmarks named in 10+ AI lab launch posts. Each unsolved benchmark falls with a {100*h:.0f}% chance per month (the last 12 months\' rate); new ones arrive at',
         f'{arr:.1f}/month, {100*p0:.0f}% already solved at release. Speed-up: solve rate +1 point a year, as from 2024 to 2026. Bands: 80% of simulations.',
         'Not a forecast. Dotted: 2026 benchmarks enter the count only after 10+ launch posts, so this year is undercounted (estimate at the 2025 pace).', CREDIT]
for i, line in enumerate(reversed(notes)):
    fig.text(0.04, 0.02 + i * 0.031, line, fontsize=11, color=FAINT, va='bottom')
save(fig, f'{OUT}/satbench_run_out.png')
