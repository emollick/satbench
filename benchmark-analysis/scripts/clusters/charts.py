"""Charts for the benchmark-clusters analysis. Run analysis.py first (writes results.pkl)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # benchmark-analysis/scripts
import sys, pickle
sys.path.insert(0, ROOT)
import common as c
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from adjustText import adjust_text

OUT = f'{c.OUT}/clusters'
r = pickle.load(open(os.path.join(ROOT, 'clusters', 'results.pkl'), 'rb'))
p = r['pcs'].copy()
AREA_ORDER = ['knowledge', 'reasoning', 'code', 'agents', 'work', 'multimodal']
SHORT = {'knowledge': 'Knowledge', 'reasoning': 'Math & sci.', 'code': 'Coding', 'agents': 'Agents',
         'work': 'Prof. work', 'multimodal': 'Vision etc.'}
NOTE_CORE_2 = (f"Core: {len(r['cols'])} benchmarks x {len(r['rows'])} models, 40% filled (no safety, composites or duplicate versions); rank-normalized.")
NOTE_CORE = (f"Core: {len(r['cols'])} benchmarks x {len(r['rows'])} models (40% filled; safety, composite indices and duplicate versions removed). "
             "Scores rank-normalized per benchmark.")

# cluster names, keyed by a member that defines the cluster (robust to cluster numbering)
NAMES = {
    'designarena-website': 'Building apps & websites',
    'legal-research-bench': 'Professional agent tasks (Vals)',
    'gdpval-extended-mercor': 'Long agentic jobs & simulations',
    'browsecomp': 'Tool use, search & not making things up',
    'gpqa-diamond': 'Hard exams: math, science, contest code',
    'lmarena-elo': 'Human preference, writing & finance QA',
    'legalbench': 'Mixed: multilingual, legal & medical QA',
    'kaggle-game-arena-chess': 'Games, long context & recall',
}
cl_name = {}
for key, nm in NAMES.items():
    if key in p.index:
        cl_name[p.at[key, 'cluster']] = nm
for k in set(p.cluster):
    cl_name.setdefault(k, f'Cluster {k}')
p['cluster_name'] = p.cluster.map(cl_name)

SHORTNAME = {
    'Vectara Hallucination Leaderboard (HHEM)': 'Vectara HHEM', 'Harvey LAB (Legal Agent Benchmark)': 'Harvey LAB',
    'MathArena (Apex, IMO, USAMO)': 'MathArena Apex', 'Longform Creative Writing (EQ-Bench)': 'EQ-Bench Longform',
    'Wer wird Millionär? LLM Benchmark': 'Millionaire Bench', 'OTIS Mock AIME 2024-2025': 'OTIS Mock AIME',
    'DesignArena Frontend Web App': 'DesignArena Web App', 'DesignArena Android (Kotlin)': 'DesignArena Android',
    'EnterpriseBench: CoreCraft': 'EnterpriseBench', 'LLM Confabulation Leaderboard': 'Confabulations',
    'SWE-bench Verified Extended': 'SWE-bench Verified (Mercor)', 'Terminal-Bench 2.1 Extended': 'Terminal-Bench (Mercor)',
    'DesignArena Data Visualization': 'DesignArena Data Viz', 'Excel Modeling Benchmark': 'Excel Modeling',
    'Vals Finance Agent v2': 'Finance Agent', 'FrontierMath Tiers 1-3 v2': 'FrontierMath 1-3',
    'FrontierMath Tier 4 v2': 'FrontierMath T4', 'MedXpertQA MM Extended': 'MedXpertQA MM',
}
sn = lambda s: SHORTNAME.get(s, s)


def area_legend(ax, loc='upper left', **kw):
    ax.legend(handles=c.area_legend_handles(AREA_ORDER), loc=loc, ncol=kw.pop('ncol', 1), handletextpad=0.3,
              columnspacing=1.0, borderaxespad=0.2, **kw)


# ======================================================================= 1. hero map PC2 x PC3
fig = c.new_figure(10, 10, top=0.80, bottom=0.2, left=0.115, right=0.97)
ax = fig.add_subplot(111)
x, y = p.pc2.values, p.pc3.values
ax.axhline(0, color=c.MUTED, lw=0.8, zorder=1); ax.axvline(0, color=c.MUTED, lw=0.8, zorder=1)
for a in AREA_ORDER:
    s = p.area == a
    ax.scatter(p.pc2[s], p.pc3[s], s=70, color=c.AREA_COLORS[a], edgecolor='white', linewidth=1.2, zorder=3)
# label: extremes on each axis plus well-known benchmarks
pick = set()
for col in ('pc2', 'pc3'):
    pick |= set(p.sort_values(col).index[:7]) | set(p.sort_values(col).index[-7:])
WELL_KNOWN = ['gpqa-diamond', 'humanitys-last-exam', 'arc-agi-2', 'lmarena-elo', 'browsecomp', 'tau2-bench',
              'mmlu-pro', 'livecodebench-v6', 'swe-bench-multilingual', 'code-arena', 'simpleqa', 'mmmu-pro',
              'frontiermath-tiers-1-3-v2', 'vending-bench-2', 'gdpval-extended-mercor', 'toolathlon',
              'fiction-livebench', 'vals-ioi', 'vision-arena', 'designarena-website']
pick |= {w for w in WELL_KNOWN if w in p.index}
texts = []
for i in pick:
    texts.append(ax.text(p.at[i, 'pc2'], p.at[i, 'pc3'], sn(p.at[i, 'name']), fontsize=9.5, color=c.INK, zorder=4))
pad = 0.05
ax.set_xlim(x.min() - pad, x.max() + pad + 0.03); ax.set_ylim(y.min() - 0.03, y.max() + 0.12)
adjust_text(texts, x=x, y=y, ax=ax, expand=(1.2, 1.45), force_text=(0.3, 0.5), force_static=(0.25, 0.4),
            arrowprops=dict(arrowstyle='-', color=c.MUTED, lw=0.6), min_arrow_len=8)
ax.set_xlabel('← ranks models like app-building & agent work      ranks models like an exam →\n'
              '(second pattern, 5.6% of signal)', fontsize=12.5, color=c.INK2, linespacing=1.4)
ax.set_ylabel('← like human preference & writing      like games, long context & recall →\n'
              '(third pattern, 2.6% of signal)', fontsize=12.5, color=c.INK2, linespacing=1.4)
ax.tick_params(labelsize=10)
area_legend(ax, loc='upper left', ncol=3, fontsize=10.5)
c.header(fig, 'Beyond overall skill, benchmarks split\ninto "building" vs "exam" tests',
         'Each dot is a benchmark, placed by how it ranks 146 models once overall capability\n'
         'is removed. Nearby dots agree on which models are relatively strong. Color = area.')
fig.texts[0].set_linespacing(1.15)
fig.texts[1].set_y(0.872)
c.footer(fig, note=NOTE_CORE_2 + '\nAxes = components 2-3 of a low-rank model fit to observed scores (component 1 = overall capability, 82% of signal).'
                   '\nThe left-right split partly reflects benchmark age: "building" boards are newer and scored newer models.')
c.save(fig, f'{OUT}/benchmark_map.png')

# ======================================================================= 2. cluster list (4:5)
fig = c.new_figure(10, 12.5, top=0.80, bottom=0.115, left=0.04, right=0.98)
order = (p.groupby('cluster').pc2.mean().sort_values().index.tolist())   # app-building -> exam-ish
gs = fig.add_gridspec(4, 2, hspace=0.10, wspace=0.06)
MAXN = 8
for idx, k in enumerate(order):
    ax = fig.add_subplot(gs[idx // 2, idx % 2]); ax.axis('off')
    s = p[p.cluster == k].sort_values('stab', ascending=False)
    st = np.nanmean(s.stab)
    ax.text(0, 1.0, cl_name[k], fontsize=13.5, fontweight='bold', color=c.INK, va='top', transform=ax.transAxes)
    ax.text(0, 0.885, f'{len(s)} benchmarks · stays together in {st * 100:.0f}% of resamples',
            fontsize=10.5, color=c.INK2, va='top', transform=ax.transAxes)
    for j, (bid, row) in enumerate(s.head(MAXN).iterrows()):
        yy = 0.76 - j * 0.083
        ax.scatter([0.015], [yy - 0.03], s=45, color=c.AREA_COLORS[row.area], transform=ax.transAxes, clip_on=False)
        ax.text(0.045, yy, sn(row['name']), fontsize=11, color=c.INK if row.stab >= 0.4 else c.MUTED, va='top',
                transform=ax.transAxes)
    if len(s) > MAXN:
        ax.text(0.045, 0.76 - MAXN * 0.083, f'+ {len(s) - MAXN} more', fontsize=10.5, color=c.MUTED, va='top',
                transform=ax.transAxes)
legax = fig.add_axes([0.04, 0.815, 0.92, 0.03]); legax.axis('off')
legax.legend(handles=c.area_legend_handles(AREA_ORDER), loc='center left', ncol=3, fontsize=11, handletextpad=0.2,
             columnspacing=0.9, borderaxespad=0)
c.header(fig, 'Benchmarks form loose families, not tidy topics',
         'Groups of benchmarks that rank models alike once overall capability is removed.\n'
         'Most-stable members listed first; gray names move between groups when models are resampled.')
c.footer(fig, note='Ward clustering on residual correlation (after component 1). "Stays together" = share of 40 model-bootstrap refits\n'
                   'in which a member lands with its family-mates. Core: 125 benchmarks x 146 models, 40% filled, no safety benchmarks.')
c.save(fig, f'{OUT}/benchmark_families.png')

# ======================================================================= 3. how much is general capability (16:9)
fig = c.new_figure(12, 6.75, top=0.76, bottom=0.21, left=0.08, right=0.97)
ax = fig.add_subplot(111)
v = r['varA'][:10] * 100
cols_ = [c.SEQ_BLUE[5]] + [c.SEQ_BLUE[2]] * 9
ax.bar(range(1, 11), v, color=cols_, width=0.7, zorder=3)
for i, val in enumerate(v):
    ax.text(i + 1, val + 1.2, f'{val:.0f}%' if val >= 10 else f'{val:.1f}%', ha='center', fontsize=12, color=c.INK)
ax.set_xticks(range(1, 11)); ax.set_xticklabels(['Overall\ncapability'] + [str(i) for i in range(2, 11)])
ax.set_ylabel('Share of the patterned (non-noise) signal'); ax.set_ylim(0, 92); ax.grid(axis='x', visible=False)
ax.set_xlabel('Component', labelpad=2)
ax.text(3.2, 52, f'Overall capability alone predicts {(1 - min(v for (k, l), v in r["cv"].items() if k == 1) / r["base_mse"]) * 100:.0f}% of '
        f'held-out scores;\nall {r["K_RANK"]} components together predict {(1 - r["cv"][(r["K_RANK"], r["LAM"])] / r["base_mse"]) * 100:.0f}%.\n'
        f'A model\'s overall-capability score tracks its\nrelease date (Spearman {r["rho_time"]:.2f}).',
        fontsize=12.5, color=c.INK2, va='center', linespacing=1.5)
c.header(fig, 'One factor, overall capability, explains most of how models score',
         'Components of a low-rank model of benchmark scores. Everything after the first is small, which is why\n'
         'benchmark "clusters" are soft.')
c.footer(fig, note=NOTE_CORE_2 + ' Held-out = 5-fold cross-validation on observed cells.')
c.save(fig, f'{OUT}/variance_explained.png')

# ======================================================================= 4. areas vs families (16:9)
fig = c.new_figure(12, 6.75, top=0.68, bottom=0.13, left=0.2, right=0.97)
gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 1], wspace=0.25)
ax = fig.add_subplot(gs[0])
ct = pd.crosstab(p.area, p.cluster).reindex(index=AREA_ORDER, columns=order).fillna(0)
share = ct / ct.sum(axis=1).values[:, None]
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('seq', [c.SURFACE] + c.SEQ_BLUE[1:7])
ax.imshow(share.values, cmap=cmap, vmin=0, vmax=0.7, aspect='auto')
for i in range(ct.shape[0]):
    for j in range(ct.shape[1]):
        nv = int(ct.values[i, j])
        if nv:
            ax.text(j, i, nv, ha='center', va='center', fontsize=11.5, color='white' if share.values[i, j] > 0.4 else c.INK)
ax.set_yticks(range(len(AREA_ORDER))); ax.set_yticklabels([c.AREA_NAMES[a] for a in AREA_ORDER], fontsize=11.5)
short_cl = {'Building apps & websites': 'Apps &\nwebsites', 'Professional agent tasks (Vals)': 'Prof.\nagent',
            'Long agentic jobs & simulations': 'Long\nagentic', 'Tool use, search & not making things up': 'Tools &\nsearch',
            'Hard exams: math, science, contest code': 'Hard\nexams', 'Human preference, writing & finance QA': 'Prefer-\nence',
            'Mixed: multilingual, legal & medical QA': 'Mixed\nQA', 'Games, long context & recall': 'Games &\nrecall'}
ax.set_xticks(range(len(order))); ax.set_xticklabels([short_cl.get(cl_name[k], cl_name[k]) for k in order], fontsize=10, linespacing=1.1)
ax.xaxis.tick_top(); ax.tick_params(length=0); ax.grid(False)
for sp in ax.spines.values(): sp.set_visible(False)
# right: misfiled list
ax2 = fig.add_subplot(gs[1]); ax2.axis('off')
m = r['misfiled'].head(10)
ax2.text(0, 1.06, 'Most "misfiled": sits closer to another area', fontsize=12.5, fontweight='bold', color=c.INK,
         transform=ax2.transAxes, va='bottom')
for j, (_, row) in enumerate(m.iterrows()):
    yy = 0.97 - j * 0.098
    ax2.scatter([0.0], [yy - 0.025], s=50, color=c.AREA_COLORS[row.area], transform=ax2.transAxes, clip_on=False)
    ax2.text(0.035, yy, sn(row['name']), fontsize=11, color=c.INK, va='top', transform=ax2.transAxes)
    ax2.text(0.60, yy, '→', fontsize=11, color=c.MUTED, va='top', transform=ax2.transAxes)
    ax2.scatter([0.68], [yy - 0.025], s=50, color=c.AREA_COLORS[row.closest_area], transform=ax2.transAxes, clip_on=False)
    ax2.text(0.715, yy, SHORT[row.closest_area], fontsize=11, color=c.INK2, va='top', transform=ax2.transAxes)
hit = (p.area == r['mis'].set_index('bench').closest_area.reindex(p.index))
c.header(fig, 'The almanac\'s areas barely predict which benchmarks agree',
         f'Left: benchmarks per area (rows) in each family (columns). Agreement with areas: adjusted Rand index {r["ari_area"]:.2f}\n'
         f'(0 = chance, 1 = identical). Only {hit.mean() * 100:.0f}% of benchmarks sit closest to their own area (coding 74%, agents 28%, vision 17%).')
c.footer(fig, note='"Closest area" = highest mean residual correlation with that area\'s other benchmarks, after removing overall capability.\nCore: 125 benchmarks x 146 models.')
c.save(fig, f'{OUT}/areas_vs_families.png')

# ======================================================================= 5. labs on the two axes (16:9)
ms = r['ms']
vc = ms.lab.value_counts(); labs = vc[vc >= 8].index.tolist()
LABN = {'openai': 'OpenAI', 'anthropic': 'Anthropic', 'google': 'Google', 'qwen': 'Qwen', 'deepseek': 'DeepSeek',
        'xai': 'xAI', 'zai': 'Z.ai', 'meta': 'Meta', 'moonshot': 'Moonshot'}
fig = c.new_figure(12, 6.75, top=0.74, bottom=0.25, left=0.1, right=0.97)
gs = fig.add_gridspec(1, 2, wspace=0.08)
rng = np.random.default_rng(3)
for pi, (col, lt, rt) in enumerate([('pc2', 'better at app-building\n& agent work', 'better at\nexams'),
                                    ('pc3', 'better at preference\n& writing', 'better at games,\nlong context, recall')]):
    ax = fig.add_subplot(gs[pi])
    stats = ms[ms.lab.isin(labs)].groupby('lab')[col].agg(['mean', 'std', 'count'])
    srt = ms[ms.lab.isin(labs)].groupby('lab')['pc2'].mean().sort_values().index.tolist()
    for yi, lab in enumerate(srt):
        vals = ms.loc[ms.lab == lab, col].values
        ax.scatter(vals, yi + rng.uniform(-0.18, 0.18, len(vals)), s=14, color=c.MUTED, alpha=0.55, zorder=2, lw=0)
        mu, se = stats.at[lab, 'mean'], stats.at[lab, 'std'] / np.sqrt(stats.at[lab, 'count'])
        ax.plot([mu - 1.96 * se, mu + 1.96 * se], [yi, yi], color=c.INK, lw=2, zorder=3)
        ax.scatter([mu], [yi], s=70, color=c.INK, zorder=4, edgecolor='white', lw=1.2)
    ax.axvline(0, color=c.MUTED, lw=0.8)
    ax.set_yticks(range(len(srt)))
    ax.set_yticklabels([f'{LABN.get(l, l)} ({int(stats.at[l, "count"])})' for l in srt] if pi == 0 else [], fontsize=11.5)
    ax.set_xlim(-3.2, 3.2); ax.grid(axis='y', visible=False)
    ax.set_title(['Second pattern', 'Third pattern'][pi], fontsize=13, color=c.INK, loc='left', fontweight='bold')
    ax.text(-3.1, -1.25, '← ' + lt, fontsize=10.5, color=c.INK2, va='top', ha='left')
    ax.text(3.1, -1.25, rt + ' →', fontsize=10.5, color=c.INK2, va='top', ha='right')
    ax.set_ylim(len(srt) - 0.5, -0.6) if False else ax.set_ylim(-0.6, len(srt) - 0.5)
    ax.tick_params(axis='x', labelsize=10)
c.header(fig, 'Anthropic models lean toward "building" tests, Google\'s toward exams',
         'Each gray dot is a model; black = lab average with 95% interval. Scores are relative strengths after removing\n'
         'overall capability, so a lab can be strong overall and still lean one way. Labs with 8+ models in the core.')
c.footer(fig, note='Model scores on components 2 and 3 of the same low-rank fit (unit variance across models). Core: 125 benchmarks x 146 models.\n'
                   'The second pattern partly reflects benchmark age (newer "building" boards scored newer models), so read leanings as tentative.')
c.save(fig, f'{OUT}/labs_on_patterns.png')
print('done')
