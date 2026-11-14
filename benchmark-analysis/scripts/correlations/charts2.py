import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # benchmark-analysis/scripts
import sys, os
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from charts import SHORT, P, PER, B, M, OUT, MIN_N, AREA_ORDER
from analysis import epoch_hub, eci

def tag(ax, x, y, area, size=0.32, trans=None):
    pass


# ------------------------------------------------------------ 3. pairs that move together beyond ECI
def pairs_chart():
    T = P[P.n_eci >= 30].sort_values('partial_eci', ascending=False).head(12).reset_index(drop=True)
    why = {
        ('lmarena-elo', 'vision-arena'): 'same platform and voters',
        ('otis-mock-aime-2024-2025', 'math-level-5'): 'both competition math',
        ('designarena-website', 'code-arena'): 'both web-dev vote arenas',
        ('llm-chess', 'chess-puzzles'): 'both chess',
        ('legalbench', 'vals-medcode'): 'same evaluator (Vals AI)',
        ('code-arena', 'vibe-code-bench'): 'both build web apps',
    }
    fig = c.new_figure(12, 6.75)
    c.header(fig, 'Beyond general capability, a few benchmark pairs still move together',
             'Gray ring = raw rank correlation. Dark dot = what is left after controlling for Epoch Capabilities Index.\n'
             'Top 12 pairs by the controlled correlation, among pairs with 30+ shared models that Epoch has rated.')
    ax = fig.add_axes([0.335, 0.215, 0.44, 0.555])
    n = len(T)
    for i, r in T.iterrows():
        y = i
        ax.plot([r.partial_eci, r.rho], [y, y], color=c.GRID, lw=3, solid_capstyle='round', zorder=1)
        ax.scatter([r.rho], [y], s=70, facecolor=c.SURFACE, edgecolor=c.MUTED, lw=1.8, zorder=3)
        ax.scatter([r.partial_eci], [y], s=80, color=c.INK, zorder=4)
        ax.text(r.partial_eci - 0.03, y, f'{r.partial_eci:.2f}', ha='right', va='center', fontsize=11, color=c.INK)
        # labels at left with area tags
        la, lb = [SHORT[x].replace(' (LMArena)', '') for x in (r.a, r.b)]
        fig_y = y
        ax.text(-0.13, y, f'{la}  +  {lb}', ha='right', va='center', fontsize=12, color=c.INK,
                transform=ax.get_yaxis_transform())
        ax.text(0.012, y, f'n={int(r.n_eci)}', ha='left', va='center', fontsize=10, color=c.MUTED)
        for k, bb in enumerate((r.a, r.b)):
            ax.add_patch(Rectangle((-0.105 + k * 0.045, y - 0.22), 0.035, 0.44, facecolor=c.AREA_COLORS[B.loc[bb, 'area']],
                                   lw=0, clip_on=False, transform=ax.get_yaxis_transform()))
        # order: a then b -> draw a first
        key = (r.a, r.b) if (r.a, r.b) in why else (r.b, r.a)
        if key in why:
            ax.text(1.03, y, why[key], ha='left', va='center', fontsize=11, color=c.INK2,
                    transform=ax.get_yaxis_transform())
        flag = (r.a in epoch_hub) and (r.b in epoch_hub)
    ax.set_ylim(n - 0.4, -0.7); ax.set_yticks([])
    ax.set_xlim(0, 1.0); ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.grid(axis='y', visible=False)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Spearman rank correlation', fontsize=12)
    hs = [Line2D([0], [0], marker='o', lw=0, markersize=9, markerfacecolor=c.SURFACE, markeredgecolor=c.MUTED, markeredgewidth=1.8, label='raw'),
          Line2D([0], [0], marker='o', lw=0, markersize=9, color=c.INK, label='controlling for ECI')]
    ax.legend(handles=hs, loc='upper left', bbox_to_anchor=(1.0, 0.05), ncol=1, fontsize=11, handletextpad=0.2)
    fig.legend(handles=c.area_legend_handles(AREA_ORDER), loc='upper left', bbox_to_anchor=(0.03, 0.83), ncol=6, fontsize=10.5,
               handletextpad=0.1, columnspacing=0.8)
    c.footer(fig, 'Method: partial Spearman correlation given ECI on the models scored on both benchmarks and rated by Epoch. With n of 30-90, a value of 0.5 is uncertain by\n'
                  'roughly +/-0.2. Controlling for release date instead removes far less (median pair 0.52 vs 0.06). Notes on the right are descriptive, not tested causes.')
    c.save(fig, f'{OUT}/3_pairs_beyond_capability.png')


# ------------------------------------------------------------ 4. how predictable each benchmark is from ECI
def predictability():
    D = PER.sort_values('rho_eci', ascending=False).reset_index()
    fig = c.new_figure(10, 12.5)
    c.header(fig, 'General capability predicts most benchmarks.\nA few march to their own beat.', None)
    fig.text(0.04, 0.888, 'Rank correlation between each benchmark and the Epoch Capabilities Index (ECI), across models scored on both.\n'
             'Gray tick = its median correlation with the other 42 benchmarks here.', fontsize=12.5, color=c.INK2, va='top', linespacing=1.35)
    ax = fig.add_axes([0.33, 0.1, 0.6, 0.69])
    n = len(D)
    for i, r in D.iterrows():
        col = c.AREA_COLORS[r.area]
        ax.plot([r.median_rho] * 2, [i - 0.32, i + 0.32], color=c.MUTED, lw=2, zorder=2)
        if r.in_epoch_hub:
            ax.scatter([r.rho_eci], [i], s=70, facecolor=c.SURFACE, edgecolor=col, lw=2.2, zorder=4)
        else:
            ax.scatter([r.rho_eci], [i], s=70, color=col, edgecolor=c.SURFACE, lw=1, zorder=4)
        ax.text(-0.02, i, SHORT[r.bench], transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=11, color=c.INK)
        ax.text(r.rho_eci + 0.025, i, f'{r.rho_eci:.2f}', ha='left', va='center', fontsize=9.5, color=c.INK2)
    ax.set_ylim(n - 0.4, -0.6); ax.set_yticks([])
    ax.set_xlim(-0.05, 1.05); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.grid(axis='y', visible=False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.tick_top(); ax.xaxis.set_label_position('top')
    ax.set_xlabel('Spearman rank correlation', fontsize=12)
    hs = c.area_legend_handles(AREA_ORDER) + [
        Line2D([0], [0], marker='o', lw=0, markersize=10, markerfacecolor=c.SURFACE, markeredgecolor=c.INK2, markeredgewidth=2,
               label='Run or collected by Epoch AI\n(likely an ECI input)'),
        Line2D([0], [0], color=c.MUTED, lw=2, label='Median correlation with\nthe other benchmarks')]
    ax.legend(handles=hs, loc='center left', bbox_to_anchor=(0.0, 0.5), fontsize=10.5, handletextpad=0.3, labelspacing=0.55,
              frameon=True, facecolor=c.SURFACE, edgecolor=c.GRID)
    c.footer(fig, f'Method: Spearman correlation of each lead board with ECI (n = 24 to 176 models; Epoch rates 256 models).\nHollow dots partly define ECI, so their fit is flattered.')
    c.save(fig, f'{OUT}/4_predictability.png')


# ------------------------------------------------------------ 5. two scatterplots
def scatters():
    from adjustText import adjust_text
    names = c.models()['name']
    fig = c.new_figure(12, 6.75, top=0.76, bottom=0.2, left=0.07, right=0.97)
    
    c.header(fig, 'GPQA predicts a model\'s math score, not its BullshitBench score',
             'Each dot is a model scored on both benchmarks (lead-board scores, %). Spearman rank correlation and model count shown.')
    pairs = [('otis-mock-aime-2024-2025', 'Strong link'), ('bullshitbench-2', 'Weak link')]
    for k, (yb, lab) in enumerate(pairs):
        ax = fig.add_axes([0.07 + k * 0.49, 0.235, 0.41, 0.525])
        d = M[['gpqa-diamond', yb]].dropna()
        r = P[((P.a == 'gpqa-diamond') & (P.b == yb)) | ((P.b == 'gpqa-diamond') & (P.a == yb))].iloc[0]
        ax.scatter(d['gpqa-diamond'], d[yb], s=34, color=c.AREA_COLORS['knowledge'] if False else '#3987e5',
                   edgecolor=c.SURFACE, lw=0.8, alpha=0.85, zorder=3)
        ax.set_xlabel('GPQA Diamond (%)'); ax.set_ylabel(f'{SHORT[yb]} (%)')
        ax.set_xlim(20, 100)
        ax.set_title(f'{lab}: rank correlation {r.rho:.2f}  (n = {int(r.n)})', loc='left', fontsize=13.5,
                     fontweight='bold', color=c.INK, pad=8)
        ax.set_ylim(-4, 104)
        # label a few models
        if yb == 'bullshitbench-2':
            pick = list(d[yb].nlargest(2).index) + list(d[d['gpqa-diamond'] > 85][yb].nsmallest(2).index)
        else:
            pick = []
        if yb == 'bullshitbench-2':
            hi = d[yb].nlargest(2)
            lo = d[d['gpqa-diamond'] > 85][yb].nsmallest(2)
            for m in list(hi.index) + list(lo.index):
                ax.scatter([d.loc[m, 'gpqa-diamond']], [d.loc[m, yb]], s=46, facecolor='none', edgecolor=c.INK, lw=1.3, zorder=4)
            ax.text(22, 78, 'Among models above 85% on GPQA,\nBullshitBench runs from 10%\n(Gemini 3 Flash) to 95%\n(Claude Opus 4.8, Qwen 3.8 Max)', fontsize=11.5, color=c.INK2, va='center')
    c.footer(fig, 'GPQA Diamond and OTIS Mock AIME from Epoch AI runs; BullshitBench V2 from its own leaderboard (share of 100 nonsense questions where\nthe model clearly pushes back, judged by a model panel).')
    c.save(fig, f'{OUT}/5_scatter_strong_vs_weak.png')


if __name__ == '__main__':
    what = sys.argv[1:] or ['pairs', 'pred', 'scatter']
    if 'pairs' in what: pairs_chart()
    if 'pred' in what: predictability()
    if 'scatter' in what: scatters()
