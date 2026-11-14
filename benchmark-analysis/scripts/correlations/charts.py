import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # benchmark-analysis/scripts
import sys, os
sys.path.insert(0, ROOT)
import common as c
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from scipy.cluster.hierarchy import linkage, leaves_list, optimal_leaf_ordering
from scipy.spatial.distance import squareform
from analysis import BENCHES, MIN_N, B, M, eci, epoch_hub

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f'{c.OUT}/correlations'
P = pd.read_csv(f'{HERE}/out/pairs.csv')
PER = pd.read_csv(f'{HERE}/out/per_bench.csv').set_index('bench')

SHORT = {
    'lmarena-elo': 'LMArena (text)', 'mmlu-pro': 'MMLU-Pro', 'humanitys-last-exam': "Humanity's Last Exam",
    'simpleqa-verified': 'SimpleQA Verified', 'ifeval': 'IFEval', 'creative-writing-v3': 'Creative Writing v3',
    'nyt-connections-extended': 'NYT Connections', 'bullshitbench-2': 'BullshitBench V2',
    'vectara-hallucination-leaderboard-hhem': 'Vectara Hallucination', 'gpqa-diamond': 'GPQA Diamond',
    'otis-mock-aime-2024-2025': 'OTIS Mock AIME', 'aime-2025': 'AIME 2025',
    'frontiermath-tiers-1-3-v2': 'FrontierMath T1-3', 'arc-agi-2': 'ARC-AGI-2', 'simplebench': 'SimpleBench',
    'math-level-5': 'MATH Level 5', 'forecastbench': 'ForecastBench', 'swe-bench-verified': 'SWE-bench Verified',
    'livecodebench-v6': 'LiveCodeBench v6', 'designarena-website': 'DesignArena Website',
    'code-arena': 'Code Arena', 'weirdml': 'WeirdML', 'ale-bench': 'ALE-Bench', 'vibe-code-bench': 'Vibe Code Bench',
    'tau2-bench': 'tau2-bench', 'browsecomp': 'BrowseComp', 'terminal-bench-2-0': 'Terminal-Bench 2.0',
    'gaia': 'GAIA', 'llm-chess': 'LLM Chess', 'snakebench': 'SnakeBench', 'chess-puzzles': 'Chess Puzzles',
    'legalbench': 'LegalBench', 'vals-taxeval-v2': 'TaxEval v2', 'corpfin-v2': 'CorpFin v2',
    'vals-medcode': 'MedCode', 'vending-bench-2': 'Vending-Bench 2', 'vals-finance-agent-v2': 'Finance Agent v2',
    'profbench': 'ProfBench', 'mmmu': 'MMMU', 'mmmu-pro': 'MMMU-Pro', 'vision-arena': 'Vision Arena (LMArena)',
    'zerobench': 'ZeroBench', 'charxiv': 'CharXiv',
}
CMAP = LinearSegmentedColormap.from_list('div', [c.DIVERGING[0], c.DIVERGING[1], c.DIVERGING[2]])
AREA_ORDER = ['knowledge', 'reasoning', 'code', 'agents', 'work', 'multimodal']


def square(col):
    R = pd.DataFrame(np.nan, index=BENCHES, columns=BENCHES)
    for _, r in P.iterrows():
        R.loc[r.a, r.b] = R.loc[r.b, r.a] = r[col]
    return R


def order():
    R = square('rho')
    fill = np.nanmean(R.values)
    D = 1 - R.fillna(fill).values
    np.fill_diagonal(D, 0)
    D = (D + D.T) / 2
    Z = linkage(squareform(D, checks=False), 'average')
    Z = optimal_leaf_ordering(Z, squareform(D, checks=False))
    return [BENCHES[i] for i in leaves_list(Z)]


ORDER = order()


def heatmap(col, path, title, subtitle, note, cbar_label):
    R = square(col).loc[ORDER, ORDER]
    n = len(ORDER)
    fig = c.new_figure(10, 12.5)
    c.header(fig, title, subtitle)
    # legend of areas
    hs = c.area_legend_handles(AREA_ORDER)
    fig.legend(handles=hs, loc='upper left', bbox_to_anchor=(0.03, 0.865), ncol=6, fontsize=10,
               handletextpad=0.1, columnspacing=0.55)
    ax = fig.add_axes([0.235, 0.222, 0.735, 0.588])  # square-ish: 7.35in x 7.35in
    ax.set_xlim(0, n); ax.set_ylim(n, 0)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    for i in range(n):
        for j in range(i):
            v = R.iat[i, j]
            if np.isnan(v):
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor='white', edgecolor=c.GRID, hatch='////', lw=0))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=CMAP((v + 1) / 2), edgecolor=c.SURFACE, lw=0.6))
    names = [SHORT[b] for b in ORDER]
    ax.set_yticks(np.arange(n) + 0.5); ax.set_yticklabels(names, fontsize=9.6, color=c.INK)
    ax.set_xticks(np.arange(n) + 0.5); ax.set_xticklabels(names, fontsize=9.6, color=c.INK, rotation=90)
    ax.tick_params(length=0, pad=14)
    for k, b in enumerate(ORDER):
        col_ = c.AREA_COLORS[B.loc[b, 'area']]
        ax.add_patch(Rectangle((-0.85, k + 0.15), 0.7, 0.7, facecolor=col_, lw=0, clip_on=False))
        ax.add_patch(Rectangle((k + 0.15, n + 0.15), 0.7, 0.7, facecolor=col_, lw=0, clip_on=False))
    # colorbar in the empty upper-right triangle
    cax = fig.add_axes([0.66, 0.752, 0.27, 0.014])
    grad = np.linspace(-1, 1, 256)[None, :]
    cax.imshow(grad, aspect='auto', cmap=CMAP, extent=(-1, 1, 0, 1))
    cax.set_yticks([]); cax.set_xticks([-1, -0.5, 0, 0.5, 1])
    cax.set_xticklabels(['-1', '-0.5', '0', '0.5', '1'], fontsize=10)
    cax.tick_params(length=0, pad=3); cax.grid(False)
    for s in cax.spines.values():
        s.set_visible(False)
    cax.set_title(cbar_label, fontsize=10.5, color=c.INK2, loc='left', pad=5)
    hx = fig.add_axes([0.66, 0.702, 0.03, 0.015]); hx.axis('off')
    hx.add_patch(Rectangle((0, 0), 1, 1, facecolor='white', edgecolor=c.GRID, hatch='////', lw=0.6,
                           transform=hx.transAxes))
    fig.text(0.70, 0.709, f'fewer than {MIN_N} models scored on both', fontsize=10, color=c.INK2, va='center')
    c.footer(fig, note)
    c.save(fig, path)


if __name__ == '__main__':
    what = sys.argv[1:] or ['raw', 'eci']
    nraw = P.rho.notna().sum(); neci = P.partial_eci.notna().sum()
    if 'raw' in what:
        heatmap('rho', f'{OUT}/1_heatmap_raw.png',
                'Almost every AI benchmark ranks models the same way',
                f'Spearman rank correlation between {len(BENCHES)} widely used benchmarks, across the models scored on both.\n'
                f'Red = models that do well on one do well on the other. Median correlation: {P.rho.median():.2f}.',
                f'Method: {nraw} of {len(P)} pairs have {MIN_N}+ shared models (median {int(P.n.median())}). Each benchmark\'s lead board (one source);\n'
                'rows ordered by hierarchical clustering. Safety tests excluded.',
                'Rank correlation (Spearman)')
    if 'eci' in what:
        heatmap('partial_eci', f'{OUT}/2_heatmap_beyond_capability.png',
                'Control for general capability and most links vanish',
                'Same benchmarks and order, now controlling for each model\'s Epoch Capabilities Index (ECI).\n'
                f'What is left is what two benchmarks share beyond "this is a stronger model". Median: {P.partial_eci.median():.2f}.',
                f'Method: partial Spearman correlation given ECI, on models scored on both benchmarks and rated by Epoch ({neci} pairs with {MIN_N}+ models).\n'
                'ECI is fit from many of these benchmarks, so pairs of ECI inputs are pushed toward or below zero.',
                'Partial rank correlation, controlling for ECI')
