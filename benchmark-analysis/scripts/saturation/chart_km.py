"""A2: cumulative share of benchmarks past 85% by months since release, by release-year cohort (Kaplan-Meier)."""
from km import *
import matplotlib.pyplot as plt

el = eligible()
ids = el[el.n_cites >= 10].index
T = sat_table(ids); T = T[T.first_pt.notna()]
C = cohort_table(T)
fig = c.new_figure(12, 6.75, top=0.78, bottom=0.21, left=0.08, right=0.86)
ax = fig.add_subplot(111)
cols = {'2022 or earlier': '#b5b4ae', '2023': '#86b6ef', '2024': '#2a78d6', '2025': '#104281', '2026': '#0d366b'}
lws = {'2022 or earlier': 2.4, '2023': 2.6, '2024': 2.6, '2025': 3.2, '2026': 2.6}
ends = []
for k, v in C.items():
    xs = np.append(v['xs'], v['maxage']); ys = np.append(v['ys'], v['ys'][-1])
    cum = (1 - ys) * 100
    ax.step(xs, cum, where='post', color=cols[k], lw=lws[k], zorder=3 if k == '2025' else 2,
            ls='-' if k != '2026' else (0, (3, 1.5)))
    ends.append((k, xs[-1], cum[-1], v))
ax.axvline(12, color=c.MUTED, lw=1, ls=':', zorder=1)
ax.text(12.4, 97, 'one year', color=c.INK2, fontsize=11.5, va='top')
ax.set_xlim(0, 60); ax.set_ylim(0, 100)
ax.set_xticks(range(0, 61, 12))
ax.set_xlabel('Months since the benchmark was released')
ax.set_ylabel('Share past 85%')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
# short labels at curve ends
endpos = {'2022 or earlier': (60.6, None, 'left', 'center', '2022 or\nearlier'), '2023': (45.3, 2.0, 'left', 'bottom', '2023'),
          '2024': (34.6, -1.5, 'left', 'top', '2024'), '2025': (22.6, 0.8, 'left', 'bottom', '2025'),
          '2026': (6.0, 1.5, 'center', 'bottom', '2026 (so far)')}
for k, x, y, v in ends:
    ex, dy, ha, va, txt = endpos[k]
    if x > 60: y = (1 - S_at(v['xs'], v['ys'], 60)) * 100
    ax.text(ex, y + (dy or 0), txt, ha=ha, va=va, fontsize=12, color=c.INK, fontweight='bold', clip_on=False)
# summary table, lower right
tx = [0.615, 0.80, 0.885, 0.965]
ty = 0.30
ax.text(tx[0], ty, 'Released', transform=ax.transAxes, fontsize=11.5, color=c.INK2, va='bottom')
ax.text(tx[1], ty, 'n', transform=ax.transAxes, fontsize=11.5, color=c.INK2, va='bottom', ha='right')
ax.text(tx[2], ty, 'by 6 mo', transform=ax.transAxes, fontsize=11.5, color=c.INK2, va='bottom', ha='right')
ax.text(tx[3], ty, 'by 1 yr', transform=ax.transAxes, fontsize=11.5, color=c.INK2, va='bottom', ha='right')
for i, (k, x, y, v) in enumerate(ends):
    yy = ty - 0.055 * (i + 1)
    s6 = (1 - S_at(v['xs'], v['ys'], 6)) * 100
    ax.plot([tx[0] - 0.035, tx[0] - 0.01], [yy + 0.012] * 2, transform=ax.transAxes, color=cols[k], lw=3,
            ls='-' if k != '2026' else (0, (3, 1.5)), clip_on=False)
    ax.text(tx[0], yy, k, transform=ax.transAxes, fontsize=11.5, color=c.INK, va='bottom')
    ax.text(tx[1], yy, str(v['n']), transform=ax.transAxes, fontsize=11.5, color=c.INK, va='bottom', ha='right')
    ax.text(tx[2], yy, f"{s6:.0f}%", transform=ax.transAxes, fontsize=11.5, color=c.INK, va='bottom', ha='right')
    ax.text(tx[3], yy, f"{v['sat12']*100:.0f}%" if v['maxage'] >= 12 else '–', transform=ax.transAxes, fontsize=11.5, color=c.INK, va='bottom', ha='right')
ax.patch.set_zorder(0)
c.header(fig, 'New benchmarks are getting beaten faster',
         'Share of benchmarks whose best reported score has passed 85%, by months since release, grouped by the year the\n'
         'benchmark came out. Covers the 172 benchmarks named in 10+ AI lab launch posts.')
c.footer(fig, 'Kaplan-Meier estimate: benchmarks not yet at 85% count until today. Benchmarks already at 85% when released (8 of 172) count as 0 months.\n'
              'Older cohorts are survivors: pre-2023 benchmarks that saturated fast were rarely named in 2023+ launch posts, so their curve is biased slow.')
c.save(fig, OUTDIR + 'time_to_saturation_by_cohort.png')
for k, v in C.items():
    print(k, v['n'], v['sat'], v['on_arrival'], round(v['median'], 1), round(v['sat12'], 2), v['maxage'], 1 - S_at(v['xs'], v['ys'], 6))
print(len(T), T.on_arrival.sum())
