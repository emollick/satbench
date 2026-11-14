"""A1: lane chart: release -> 85% -> 95% for the 30 most-cited percent benchmarks."""
from sat_calc import *
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.lines import Line2D

top = eligible().sort_values('n_cites', ascending=False).head(30).index
T = sat_table(top).sort_values('released', ascending=False)  # oldest at top after invert
fig = c.new_figure(10, 12.5, top=0.825, bottom=0.10, left=0.235, right=0.875)
ax = fig.add_subplot(111)
y = np.arange(len(T))
x0, x1 = pd.Timestamp('2020-06-01'), pd.Timestamp('2027-01-01')
for yi, (k, r) in zip(y, T.iterrows()):
    col = c.AREA_COLORS[r.area]
    rel = r.released
    ax.plot([max(rel, x0), AS_OF], [yi, yi], color=c.GRID, lw=1.2, zorder=1)
    if pd.notna(r.eff85):
        ax.plot([rel, r.eff85], [yi, yi], color=col, lw=4, solid_capstyle='round', zorder=3)
        if pd.notna(r.eff95):
            ax.plot([r.eff85, r.eff95], [yi, yi], color=col, lw=4, alpha=0.35, solid_capstyle='round', zorder=2)
        ax.scatter([r.eff85], [yi], s=70, color=col, edgecolor='white', lw=1.5, zorder=5)
        if pd.notna(r.eff95):
            ax.scatter([r.eff95], [yi], s=80, marker='D', color='white', edgecolor=col, lw=2, zorder=5)
        m = r.m85
        lab = 'at release' if r.on_arrival or m < 0.5 else f'{m:.0f} mo'
        if pd.notna(r.eff95): lab += f'  (95%: {r.m95:.0f} mo)'
        end = r.eff95 if pd.notna(r.eff95) else r.eff85
        if end > pd.Timestamp('2026-04-01'):
            ax.text(rel - pd.Timedelta(days=40), yi, lab, va='center', ha='right', fontsize=10.5, color=c.INK2)
        else:
            ax.text(end + pd.Timedelta(days=45), yi, lab, va='center', ha='left', fontsize=10.5, color=c.INK2)
    else:
        ax.plot([rel, AS_OF], [yi, yi], color=col, lw=1.6, ls=(0, (2, 2)), zorder=3)
        ax.annotate('', xy=(AS_OF + pd.Timedelta(days=40), yi), xytext=(AS_OF, yi),
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=1.6, mutation_scale=12))
        ax.text(AS_OF + pd.Timedelta(days=70), yi, f'best {r.best:.1f}%', va='center', ha='left', fontsize=10.5, color=c.INK)
    ax.scatter([rel], [yi], s=34, marker='|', color=c.INK2, lw=1.8, zorder=4)
ax.set_yticks(y)
ax.set_yticklabels([n.replace(' (MathVision)', '') for n in T.name], fontsize=11.5, color=c.INK)
for t, a in zip(ax.get_yticklabels(), T.area):
    pass
ax.set_ylim(-0.7, len(T) - 0.3)
ax.set_xlim(x0, x1)
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.grid(axis='y', visible=False)
ax.tick_params(axis='y', length=0)
ax.axvline(AS_OF, color=c.MUTED, lw=0.8, ls=':', zorder=0)
ax.text(AS_OF - pd.Timedelta(days=20), len(T) - 1, 'today', ha='right', va='center', fontsize=10.5, color=c.MUTED)
# area dots before names
for yi, a in zip(y, T.area):
    ax.scatter([-0.012], [yi], transform=ax.get_yaxis_transform(), s=0)
n_sat = T.sat85.notna().sum(); n95 = T.sat95.notna().sum()
c.header(fig, f'{n_sat} of the 30 top AI benchmarks are already past 85%',
         'The 30 benchmarks AI labs name most in launch posts. Each row runs from release (tick) to the\n'
         f'date the best reported score first passed 85% (dot) and 95% (diamond); {n95} have passed 95%.\n'
         'Dashed: not there yet. Labels give months from release.')
handles = [Line2D([0], [0], marker='|', lw=0, color=c.INK2, markersize=10, mew=1.8, label='released'),
           Line2D([0], [0], marker='o', lw=4, color=c.MUTED, markeredgecolor='white', markersize=9, label='passed 85%'),
           Line2D([0], [0], marker='D', lw=4, color=c.MUTED, alpha=0.5, markerfacecolor='white', markersize=8, label='passed 95%')]
areas = [a for a in c.AREA_COLORS if a in set(T.area)]
leg1 = ax.legend(handles=handles + c.area_legend_handles(areas), loc='lower left', fontsize=10.5, ncol=1,
                 bbox_to_anchor=(0.0, 0.0), handlelength=1.8, borderaxespad=0.3)
c.footer(fig, 'Percent benchmarks, higher is better, ranked by number of lab launch posts naming them. Best score = best reported by any source\n'
              '(leaderboards, Epoch AI, lab claims), dated by model release; scores from models older than the benchmark count from its release date.')
c.save(fig, OUTDIR + 'saturation_timeline_top30.png')
print(T[['name', 'm85', 'm95', 'on_arrival', 'best']].round(1).to_string())
