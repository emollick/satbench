import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys
from headline import *
import matplotlib.pyplot as plt
from common import BLUES, ACCENT, GREY, INK, MUTED, FAINT, figure, save
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'labs')
NAME = lambda L: {'other': 'Other labs'}.get(L, c.lab_name(L))

k = df[df.solved85.notna()].copy(); k['yr'] = k.solved85.map(yr_bin)
kk = k[~k.born_solved]
born = k[k.born_solved]
YRS = ['pre-2023', '2023', '2024', '2025', '2026']
top = kk.k85_lab.value_counts()
TOP = list(top.index[:9])
kk = kk.assign(L=kk.k85_lab.where(kk.k85_lab.isin(TOP), 'other'))
born = born.assign(L=born.k85_lab.where(born.k85_lab.isin(TOP), 'other'))
order = TOP + ['other']

# ---------- 1. kills by lab, stacked by year
fig, ax = figure('Who first pushed each benchmark past 85%',
                 'SatBench items whose best reported score first crossed 85% with this lab\'s model, by year crossed.\n'
                 f'{len(kk)} kills; grey = born-solved items (already past 85% at release), not counted as kills',
                 notes=['Raw counts reward reporting niche tests: 13 of Qwen\'s 17 are benchmarks other frontier labs rarely report. 75 of 100 kills are the lab\'s own claim.',
                        f'Born solved ({len(born)}): e.g. AIME 2026, HMMT 2026, where leaderboards ran older models on the new test and date them by model release.'],
                 rect=[0.17, 0.24, 0.77, 0.43])
ct = pd.crosstab(kk.L, kk.yr).reindex(index=order, columns=YRS, fill_value=0)
bc = born.L.value_counts().reindex(order, fill_value=0)
y = np.arange(len(order))[::-1]
left = np.zeros(len(order))
for i, yr in enumerate(YRS):
    v = ct[yr].values
    ax.barh(y, v, left=left, color=BLUES[i], height=0.72, edgecolor=c.BG, linewidth=1.5)
    left += v
ax.barh(y, bc.values, left=left, color=GREY, height=0.72, edgecolor=c.BG, linewidth=1.5, alpha=0.6)
for yi, L, tot, b in zip(y, order, ct.sum(axis=1).values, bc.values):
    ax.text(tot + b + 0.4, yi, f'{tot}' + (f'  (+{b} born)' if b else ''), va='center', fontsize=15, color=INK)
ax.set_yticks(y); ax.set_yticklabels([NAME(L) for L in order], fontsize=16)
ax.set_xlim(0, 32); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.set_xlabel('items first taken past 85%')
# inline legend
xs = 0.17
for i, yr in enumerate(YRS + ['born solved']):
    col = BLUES[i] if i < 5 else GREY
    fig.patches.append(plt.Rectangle((xs, 0.705), 0.016, 0.028, transform=fig.transFigure, color=col, alpha=1 if i < 5 else 0.6))
    fig.text(xs + 0.021, 0.719, yr, fontsize=14.5, color=MUTED, va='center')
    xs += 0.105 if i < 5 else 0
save(fig, f'{OUT}/labs_kills_by_lab.png')

# ---------- 2. claim vs independent
fig, ax = figure('Three in four "kills" are a lab grading its own model',
                 'Who first took each SatBench item past 85%, by where the record score came from. Dark: the lab\'s\n'
                 'own launch post. Light: independent run (official leaderboard, Epoch AI). Grey: pre-2023 paper',
                 notes=[f'{len(kk)} kills; born-solved items excluded (all 9 are leaderboard runs). Only 10 of the 75 claimed kills were later matched by an independent run >=85%:',
                        '31 have no independent data at all; on 34 the independent runs top out below 85% (often because that source stopped tracking the test).'],
                 rect=[0.17, 0.24, 0.79, 0.49])
kind_ct = pd.crosstab(kk.L, kk.k85_kind).reindex(index=order, columns=['claim', 'indep', 'paper'], fill_value=0)
left = np.zeros(len(order))
for col, colr in zip(['claim', 'indep', 'paper'], [BLUES[3], BLUES[1], GREY]):
    v = kind_ct[col].values
    ax.barh(y, v, left=left, color=colr, height=0.72, edgecolor=c.BG, linewidth=1.5)
    left += v
for yi, L in zip(y, order):
    r = kind_ct.loc[L]; tot = r.sum()
    ax.text(tot + 0.4, yi, f'{r.claim} of {tot} self-reported ({100*r.claim/tot:.0f}%)', va='center', fontsize=14.5, color=INK)
ax.set_yticks(y); ax.set_yticklabels([NAME(L) for L in order], fontsize=16)
ax.set_xlim(0, 36); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.set_xlabel('items first taken past 85%')
save(fig, f'{OUT}/labs_kills_source.png')

# ---------- 3. top models
mc = kk.groupby('solver85').agg(n=('id', 'size'), claim=('k85_kind', lambda s: (s == 'claim').sum()),
                                 date=('solved85', 'min'), ids=('id', lambda s: ', '.join(sorted(s)))).sort_values(['n', 'date'], ascending=[False, True])
mc = mc[mc.n >= 2]
fig, ax = figure('One long launch post can rack up kills',
                 f'Models that first took >=2 SatBench items past 85% ({len(mc)} models, {mc.n.sum()} of {len(kk)} kills).\n'
                 'Dark = from the lab\'s own launch post, light = independent leaderboard / Epoch run',
                 notes=['Born-solved items excluded. Each leader\'s kills all come from a single long launch post (PaLM 2: May 2023; Qwen3.5: Feb 2026).'],
                 rect=[0.33, 0.20, 0.64, 0.53])
yy = np.arange(len(mc))[::-1]
ax.barh(yy, mc.claim, color=BLUES[3], height=0.72, edgecolor=c.BG, linewidth=1.5)
ax.barh(yy, mc.n - mc.claim, left=mc.claim, color=BLUES[1], height=0.72, edgecolor=c.BG, linewidth=1.5)
for yi, (m, r) in zip(yy, mc.iterrows()):
    short = r.ids.replace('berkeley-function-calling-leaderboard-bfcl', 'bfcl')
    if len(short) > 62: short = short[:60] + '...'
    ax.text(r.n + 0.1, yi, short, va='center', fontsize=11.5, color=MUTED)
ax.set_yticks(yy); ax.set_yticklabels([f'{c.model_name(m)}  ({NAME(lab(m)).replace(" DeepMind","").replace(" Seed","")}, {r.date.year})' for m, r in mc.iterrows()], fontsize=13)
ax.set_xlim(0, 9.5); ax.set_xticks([0, 1, 2, 3, 4, 5]); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
save(fig, f'{OUT}/labs_top_models.png')

# ---------- 4. normalized
rec = collections.defaultdict(set); cited = collections.defaultdict(set)
for _, r in df.iterrows():
    for ci in S[r.id]['cites']: cited[ci['lab']].add(r.id)
posts = CARDS.lab.value_counts()
labs_n = [L for L in posts.index if posts[L] >= 10]
N = pd.DataFrame([dict(lab=L, kills=int((kk.k85_lab == L).sum()), posts=posts[L], cited=len(cited[L])) for L in labs_n])
N['per10'] = 10 * N.kills / N.posts; N['per100'] = 100 * N.kills / N.cited
N = N.sort_values(['kills', 'per10'], ascending=True)
fig = plt.figure(figsize=(12, 6.75), dpi=200)
fig.text(0.04, 0.955, 'Per chance taken, Anthropic and OpenAI lead; Qwen drops', fontsize=27, fontweight='bold', color=INK, va='top')
fig.text(0.04, 0.885, 'Kills (items first taken past 85%) for labs with >=10 launch posts: raw, per 10 launch posts,\nand per 100 SatBench items the lab ever cited in its posts (its "chances")',
         fontsize=15.5, color=MUTED, va='top', linespacing=1.45)
notes = ['Born-solved items excluded. Kills include independent leaderboard runs of a lab\'s model; posts = launch posts in the almanac (all years).', c.CREDIT]
for i, line in enumerate(reversed(notes)):
    fig.text(0.04, 0.025 + i * 0.033, line, fontsize=11.5, color=FAINT, va='bottom')
yy = np.arange(len(N))
panels = [('kills', 'Kills (rank)', '{:.0f}'), ('per10', 'Per 10 launch posts', '{:.1f}'), ('per100', 'Per 100 items cited', '{:.0f}')]
for j, (col, ttl, fmt) in enumerate(panels):
    ax = fig.add_axes([0.17 + j * 0.275, 0.12, 0.22, 0.56])
    cols = [BLUES[3] if L in ('qwen',) else BLUES[2] for L in N.lab]
    cols = [BLUES[3]] * len(N)
    ax.barh(yy, N[col], color=cols, height=0.7)
    mx = N[col].max()
    for yi, v in zip(yy, N[col]):
        ax.text(v + mx * 0.03, yi, fmt.format(v), va='center', fontsize=13, color=INK)
    rank = N[col].rank(ascending=False, method='min').astype(int)
    ax.set_xlim(0, mx * 1.3); ax.set_xticks([]); ax.grid(False)
    ax.set_title(ttl, fontsize=16, color=INK, loc='left', pad=8)
    ax.set_yticks(yy); ax.tick_params(axis='y', length=0)
    ax.set_yticklabels([f'{NAME(L).replace(" DeepMind", "")}  #{r}' for L, r in zip(N.lab, rank)] if j == 0 else [f'#{r}' for r in rank], fontsize=14 if j == 0 else 12.5, color=INK if j == 0 else FAINT)
save(fig, f'{OUT}/labs_kills_normalized.png')

# ---------- 5. 95%
k9 = df[df.solved95.notna() & ~df.born95].copy()
c9 = pd.crosstab(k9.k95_lab, k9.k95_kind).reindex(columns=['claim', 'indep'], fill_value=0)
c9['tot'] = c9.sum(axis=1); c9 = c9.sort_values('tot', ascending=False)
t9 = list(c9.index[:6]); oth = c9.loc[~c9.index.isin(t9)].sum()
c9 = pd.concat([c9.loc[t9], pd.DataFrame([oth], index=['other'])])
fig, ax = figure('At 95%, OpenAI leads, half on independent runs',
                 f'SatBench items whose best reported score first crossed 95%, by lab ({len(k9)} items).\n'
                 'Dark = from the lab\'s own launch post, light = independent leaderboard / Epoch run',
                 notes=[f'{int(df.born95.sum())} born-solved items excluded (AIME 2026, HMMT 2026: GPT-5.2 leaderboard runs dated before the contests).', '95% is close to the label-noise ceiling of many benchmarks.'],
                 rect=[0.17, 0.17+0.08, 0.79, 0.47])
y9 = np.arange(len(c9))[::-1]
ax.barh(y9, c9.claim, color=BLUES[3], height=0.72, edgecolor=c.BG, linewidth=1.5)
ax.barh(y9, c9.indep, left=c9.claim, color=BLUES[1], height=0.72, edgecolor=c.BG, linewidth=1.5)
for yi, (L, r) in zip(y9, c9.iterrows()):
    ax.text(r.tot + 0.15, yi, f'{r.tot}  ({r.claim} self-reported)', va='center', fontsize=15, color=INK)
ax.set_yticks(y9); ax.set_yticklabels([NAME(L) for L in c9.index], fontsize=16)
ax.set_xlim(0, 16); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.set_xlabel('items first taken past 95%')
save(fig, f'{OUT}/labs_kills95.png')

# ---------- 6. headline saturation by lab, 2026
Q = P[P.n >= 3]
q26 = Q[Q.year == 2026]
g = q26.groupby('lab').agg(posts=('card', 'size'), share=('share', 'mean'), n=('n', 'mean'), k=('k', 'mean'))
g = g[g.posts >= 5].sort_values('share')
allmean = q26.share.mean()
fig, ax = figure('OpenAI headlines the fewest already-saturated tests in 2026',
                 'Share of % benchmarks in each 2026 launch post whose best reported score was already >=85%\n'
                 'before the post. Mean over the lab\'s posts; labs with >=5 posts in 2026. Blue = frontier lab',
                 notes=[f'{len(q26)} 2026 posts with >=3 eligible benchmarks (% scored, higher better; any benchmark, not only SatBench items). "Before" = strictly before post date.',
                        'A low share can also mean a lab reports new tests of its own. Leaderboard points are dated by model release (a few new tests look saturated early).'],
                 rect=[0.17, 0.22, 0.79, 0.50])
yg = np.arange(len(g))
ax.barh(yg, 100 * g.share, color=[BLUES[3] if L in c.FRONTIER_LABS else GREY for L in g.index], height=0.72)
for yi, (L, r) in zip(yg, g.iterrows()):
    ax.text(100 * r.share + 0.8, yi, f'{100*r.share:.0f}%   ({r.k:.1f} of {r.n:.0f} per post, {int(r.posts)} posts)', va='center', fontsize=13.5, color=INK, bbox=dict(fc=c.BG, ec='none', pad=0.5))
ax.axvline(100 * allmean, color=MUTED, lw=1.5, ls=(0, (3, 3)), zorder=0.5)
ax.text(100 * allmean + 0.8, -1.0, f'all 2026 posts: {100*allmean:.0f}%', fontsize=13.5, color=MUTED, va='center')
ax.set_yticks(yg); ax.set_yticklabels([NAME(L) for L in g.index], fontsize=15)
ax.set_xlim(0, 100); ax.set_ylim(-1.5, len(g) - 0.4); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.xaxis.set_major_formatter(lambda v, p: f'{v:.0f}%')
save(fig, f'{OUT}/labs_headline_saturation_2026.png')

# ---------- 7. quarterly frontier vs other
Q2 = Q.assign(q=Q.date.dt.to_period('Q'))
Q2 = Q2[Q2.q >= pd.Period('2025Q1')]
t = Q2.groupby(['q', 'frontier']).share.agg(['mean', 'size']).unstack()
fig, ax = figure('Frontier labs headline fewer saturated tests',
                 'Mean share of % benchmarks in a launch post whose best score was already >=85% before the post.\n'
                 'Frontier labs = Anthropic, OpenAI, Google, Moonshot, Meta, DeepSeek, xAI, Qwen, Z.ai',
                 notes=[f'Posts with >=3 eligible benchmarks; {int(t["size"].sum().sum())} posts, 13-37 per series per quarter. 2026 Q4 runs to Nov 14 only.',
                        'Too few posts before 2025 to plot by quarter (42). Per year, all labs: 2023 48%, 2024 50%, 2025 48%, 2026 39%.'],
                 rect=[0.08, 0.24, 0.84, 0.48])
xq = np.arange(len(t))
for fr, col, lbl in [(True, BLUES[3], 'Frontier labs'), (False, GREY, 'Other labs')]:
    v = 100 * t['mean'][fr].values
    ax.plot(xq, v, color=col, lw=3, marker='o', ms=8)
    ax.text(xq[-1] + 0.15, v[-1], f'{lbl}\n{v[-1]:.0f}%', color=INK, fontsize=15, va='center')
    ax.text(xq[0] - 0.1, v[0] + (3 if fr is False else -6), f'{v[0]:.0f}%', color=MUTED, fontsize=14, ha='center')
ax.set_xticks(xq); ax.set_xticklabels([f'{p.year}\nQ{p.quarter}' if p.quarter == 1 else f'Q{p.quarter}' for p in t.index], fontsize=14)
ax.set_ylim(0, 75); ax.set_xlim(-0.5, len(t) + 0.9)
ax.yaxis.set_major_formatter(lambda v, p: f'{v:.0f}%')
ax.grid(axis='x', visible=False)
save(fig, f'{OUT}/labs_headline_saturation_quarterly.png')
print(N.to_string()); print(c9); print(g); print(t)
