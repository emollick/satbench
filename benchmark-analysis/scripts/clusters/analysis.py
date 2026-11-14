"""Benchmark clusters: which benchmarks rank models the same way?

Pipeline (all numbers saved to results.pkl for the chart script; printed log in analysis_log.txt):
 1. Lead-board matrix (c.matrix), benchmarks with >= 40 models, no safety, no 'other' (meta-leaderboards and
    composite indices), drop composite indices inside areas, keep one benchmark per version family.
 2. Iteratively prune the sparsest row/column until fill >= 40% (dense core).
 3. Per benchmark: rank-based inverse-normal transform over the core models scored (unit-free).
 4. Method A (main): low-rank factor model fit only on observed cells, z_ij = a_j + u_i . v_j + noise, with a
    free intercept per benchmark (so it does not matter which models a benchmark happened to score), ridge
    penalty; rank and penalty chosen by 5-fold held-out-cell CV. The fitted low-rank part is rotated to
    principal components by SVD (PC1 = general capability).
    Method B (check, no imputation): regress each benchmark on the model's PC1 score using only the models it
    scored, then correlate the residuals pairwise over shared models (min 20).
    Method C (check): soft-impute (nuclear-norm completion) then ordinary PCA.
 5. Residual correlation after removing PC1, hierarchical clustering (Ward, distance sqrt(2(1 - r))), k = 8;
    silhouette for every k printed (all low); bootstrap over models for per-benchmark stability.
 6. Agreement with almanac areas and with board publisher (adjusted Rand index), misfiled benchmarks.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # benchmark-analysis/scripts
import sys, json, pickle, re
from urllib.parse import urlparse
sys.path.insert(0, ROOT)
import common as c
import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr, rankdata
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score, silhouette_score

RNG = np.random.default_rng(7)
MIN_SHARED = 20
TARGET_FILL = 0.40

b = c.benches()
meta = {x['id']: x for x in json.load(open(f'{c.REPO}/data/benchmarks.json'))}

# ------------------------------------------------------------------ 1. candidate set
M = c.matrix(min_models=40, exclude_areas=('safety', 'other'))
COMPOSITES = {'vals-index-v2', 'vals-index-v2-1', 'vals-finance-index', 'tuesday-work-index', 'kaggle-game-arena',
              'designarena', 'designarena-agentic-overall', 'cais-text-capabilities-index'}
M = M[[x for x in M.columns if x not in COMPOSITES]]


def fam(x):
    f = b.at[x, 'family']
    if isinstance(f, str):
        return f
    base = re.sub(r'-extended-mercor$', '', x)
    base = re.sub(r'-(v?\d+(-\d+)*)$', '', base)  # strip trailing version numbers
    return base


# manual families the metadata leaves unlinked
MANUAL = {'terminal-bench-2-1-extended-mercor': 'terminal-bench', 'browsecomp-extended-mercor': 'browsecomp',
          'swe-bench-verified-extended-mercor': 'swe-bench-verified', 'mmbench-cn-v1-1': 'mmbench',
          'gpqa-main': 'gpqa', 'gpqa-diamond': 'gpqa', 'lmarena-elo': 'lmarena-text', 'studyarena-text': 'studyarena',
          'math-level-5': 'math', 'math': 'math', 'math-500': 'math', 'vals-caselaw-v2': 'vals-caselaw',
          'vals-taxeval-v2': 'vals-taxeval', 'corpfin-v2': 'corpfin', 'apex-agents-1-1': 'apex-agents',
          'proofbench-1-1': 'proofbench', 'eq-bench-2': 'eq-bench', 'eq-bench-3': 'eq-bench'}
family = {x: MANUAL.get(x, fam(x)) for x in M.columns}

# ------------------------------------------------------------------ 2. dense core
def prune(X, target):
    rows, cols = list(X.index), list(X.columns)
    N = X.notna()
    while True:
        Y = N.loc[rows, cols]
        if Y.values.mean() >= target:
            return rows, cols
        rf, cf = Y.mean(axis=1), Y.mean(axis=0)
        r, k = rf.idxmin(), cf.idxmin()
        if rf[r] <= cf[k]:
            rows.remove(r)
        else:
            cols.remove(k)

# dedupe families first: keep the member with the most scores
counts = M.notna().sum()
keep = (pd.DataFrame({'fam': pd.Series(family), 'n': counts}).sort_values('n', ascending=False)
        .groupby('fam').head(1).index)
dropped_versions = sorted(set(M.columns) - set(keep))
M = M[list(keep)]
M = M.loc[M.notna().sum(axis=1) >= 5]
rows, cols = prune(M, TARGET_FILL)
X = M.loc[rows, cols]
print('core', X.shape, 'fill', round(X.notna().values.mean(), 3), 'min/bench', X.notna().sum().min(),
      'median/bench', X.notna().sum().median(), 'min/model', X.notna().sum(axis=1).min())
print('dropped as versions:', len(dropped_versions))

# ------------------------------------------------------------------ 3. rank -> normal scores
def rank_normal(col):
    v = col.dropna()
    r = rankdata(v.values)  # average ties
    z = norm.ppf((r - 0.5) / len(v))
    return pd.Series(z, index=v.index).reindex(col.index)

Z = X.apply(rank_normal)
mask = Z.notna().values
Zv = Z.values

# ------------------------------------------------------------------ 4A. factor model with per-benchmark intercepts
def als(Zv, M, k, lam, iters=80, seed=0):
    rng = np.random.default_rng(seed)
    nr, p = Zv.shape
    U = rng.normal(0, .1, (nr, k)); V = rng.normal(0, .1, (p, k)); a = np.zeros(p)
    Zf = np.nan_to_num(Zv)
    for _ in range(iters):
        for i in range(nr):
            o = M[i]; Vo = V[o]
            U[i] = np.linalg.solve(Vo.T @ Vo + lam * np.eye(k), Vo.T @ (Zf[i, o] - a[o]))
        for j in range(p):
            o = M[:, j]; D = np.hstack([np.ones((o.sum(), 1)), U[o]])
            P = lam * np.eye(k + 1); P[0, 0] = 1e-6
            w = np.linalg.solve(D.T @ D + P, D.T @ Zf[o, j]); a[j] = w[0]; V[j] = w[1:]
    return U, V, a

def cv_als(Zv, M, k, lam, nfold=5, seed=1):
    rng = np.random.default_rng(seed)
    obs = np.argwhere(M); f = rng.integers(0, nfold, len(obs)); errs = []
    for fo in range(nfold):
        tr = M.copy(); te = obs[f == fo]; tr[te[:, 0], te[:, 1]] = False
        U, V, a = als(Zv, tr, k, lam, iters=40)
        errs.append(np.mean(((U @ V.T + a)[te[:, 0], te[:, 1]] - Zv[te[:, 0], te[:, 1]]) ** 2))
    return float(np.mean(errs))

base_mse = float(np.mean((Zv[mask] - np.array([np.nanmean(Zv[:, j]) for j in range(Zv.shape[1])])[np.where(mask)[1]]) ** 2))
cv = {}
for lam in (1.0, 3.0, 5.0):
    for k in (1, 2, 3, 4, 6, 8, 10):
        cv[(k, lam)] = cv_als(Zv, mask, k, lam)
print('held-out MSE (baseline: benchmark mean only = %.3f)' % base_mse)
print({f'k={k},lam={l}': round(v, 3) for (k, l), v in cv.items()})
K_RANK, LAM = min(cv, key=cv.get)
# prefer the smallest rank within 0.005 of best
best = cv[(K_RANK, LAM)]
K_RANK, LAM = min([kl for kl, v in cv.items() if v <= best + 0.005], key=lambda kl: kl[0])
print('chosen rank', K_RANK, 'lambda', LAM, 'cv', round(cv[(K_RANK, LAM)], 3))
cv1 = min(v for (k, l), v in cv.items() if k == 1)
print('held-out variance explained: 1 factor %.3f, chosen %.3f' % (1 - cv1 / base_mse, 1 - cv[(K_RANK, LAM)] / base_mse))

def fit_pcs(Zv, M, k=None, lam=None, iters=100, seed=0):
    k = k or K_RANK; lam = lam or LAM
    U, V, a = als(Zv, M, k, lam, iters=iters, seed=seed)
    Lr = U @ V.T
    mu = Lr.mean(0)
    u, s, vt = np.linalg.svd(Lr - mu, full_matrices=False)
    load = vt.T * s / np.sqrt(Zv.shape[0])        # benchmark loadings (sd units of the fitted signal)
    score = u * np.sqrt(Zv.shape[0])               # model scores, unit variance
    if load[:, 0].mean() < 0:
        load[:, 0] *= -1; score[:, 0] *= -1
    fitted = Lr + a
    psi = np.array([np.mean((fitted[M[:, j], j] - Zv[M[:, j], j]) ** 2) for j in range(Zv.shape[1])])
    return dict(load=load, score=score, s=s, a=a, mu=mu, psi=psi, fitted=fitted)

FA = fit_pcs(Zv, mask)
loadA, scoreA, sA = FA['load'], FA['score'], FA['s']
varA = sA ** 2 / np.sum(sA ** 2)
r2 = {}
for k in range(1, 6):
    Lk = (scoreA[:, :k] / np.sqrt(len(Zv))) @ (loadA[:, :k] * np.sqrt(len(Zv))).T + FA['mu'] + FA['a']
    r2[k] = float(1 - np.mean((Lk[mask] - Zv[mask]) ** 2) / base_mse)
print('share of fitted signal variance PC1..6', np.round(varA[:6], 3))
print('in-sample R2 of observed scores using PCs 1..k', {k: round(v, 3) for k, v in r2.items()})
model_pc1 = scoreA[:, 0]

def implied_resid_corr(load, psi, drop=1):
    W = load[:, drop:]
    C = W @ W.T + np.diag(psi)
    d = np.sqrt(np.diag(C))
    return C / np.outer(d, d)

RrA = implied_resid_corr(loadA, FA['psi'])

# ------------------------------------------------------------------ 4B. pairwise residual correlation, no imputation
n = X.shape[1]
Res = np.full_like(Zv, np.nan)
for j in range(n):
    o = mask[:, j]
    D = np.column_stack([np.ones(o.sum()), model_pc1[o]])
    w = np.linalg.lstsq(D, Zv[o, j], rcond=None)[0]
    Res[o, j] = Zv[o, j] - D @ w
RrB = np.full((n, n), np.nan); NB = np.zeros((n, n), int)
for i in range(n):
    RrB[i, i] = 1
    for j in range(i + 1, n):
        m = mask[:, i] & mask[:, j]
        NB[i, j] = NB[j, i] = m.sum()
        if m.sum() >= MIN_SHARED:
            RrB[i, j] = RrB[j, i] = np.corrcoef(Res[m, i], Res[m, j])[0, 1]
iu = np.triu_indices(n, 1)
pair_cov = float(np.isfinite(RrB[iu]).mean())
print('pairs with >= %d shared models: %.3f; median shared %d' % (MIN_SHARED, pair_cov, np.median(NB[iu])))
okp = np.isfinite(RrB[iu])
print('A vs B residual correlations (pairs with data): r = %.3f' % np.corrcoef(RrA[iu][okp], RrB[iu][okp])[0, 1])

# ------------------------------------------------------------------ 4C. soft-impute + PCA
def soft_impute(A, obs, lam, iters=300, tol=1e-5):
    Zf = np.where(obs, A, 0.0); prev = None
    for _ in range(iters):
        U, s, Vt = np.linalg.svd(Zf, full_matrices=False)
        s = np.maximum(s - lam, 0); L = (U * s) @ Vt
        Zf = np.where(obs, A, L)
        if prev is not None and np.linalg.norm(L - prev) / max(np.linalg.norm(prev), 1e-9) < tol:
            break
        prev = L
    return L
Lsi = soft_impute(np.nan_to_num(Zv), mask, 3.0)
Zc = np.where(mask, Zv, Lsi)
Rc = np.corrcoef((Zc - Zc.mean(0)) / Zc.std(0), rowvar=False)
wC, VC = np.linalg.eigh(Rc); o = np.argsort(wC)[::-1]; wC, VC = wC[o], VC[:, o]
loadC = VC * np.sqrt(wC); varC = wC / wC.sum()
agree = {}
for k in range(4):
    rr = np.corrcoef(loadA[:, k], loadC[:, k])[0, 1]
    if rr < 0: loadC[:, k] *= -1
    agree[k + 1] = abs(float(rr))
print('soft-impute PCA variance explained PC1..4', np.round(varC[:4], 3))
print('loading agreement factor model vs soft-impute PCA, PC1..4', {k: round(v, 3) for k, v in agree.items()})

# ------------------------------------------------------------------ 5. clusters
def cluster(Rr, k):
    """Ward linkage on the correlation distance sqrt(2(1 - r)) (Euclidean for a valid correlation matrix)."""
    D = np.sqrt(np.clip(2 * (1 - Rr), 0, 4)); np.fill_diagonal(D, 0)
    Zl = linkage(squareform(D, checks=False), 'ward')
    return fcluster(Zl, k, 'maxclust'), Zl, D

sil = {}
for k in range(3, 15):
    lab, _, D = cluster(RrA, k)
    sil[k] = float(silhouette_score(D, lab, metric='precomputed'))
print('silhouette by k', {k: round(v, 3) for k, v in sil.items()})
K = int(sys.argv[1]) if len(sys.argv) > 1 else 8  # silhouette is flat and low for every k (printed); 8 is chosen for readability
labA, linkA, DA = cluster(RrA, K)
RrB0 = np.where(np.isfinite(RrB), RrB, 0.0)   # no shared data -> no evidence of similarity
labB, _, _ = cluster(RrB0, K)
ari_AB = adjusted_rand_score(labA, labB)
print('K =', K, 'sizes', np.bincount(labA)[1:].tolist(), '| ARI factor-model clusters vs pairwise-residual clusters', round(ari_AB, 3))

# bootstrap over models
B_N = 40
co = np.zeros((n, n)); aris = []
for bi in range(B_N):
    idx = RNG.integers(0, X.shape[0], X.shape[0])
    Zb = X.iloc[idx].reset_index(drop=True).apply(rank_normal)
    mb = Zb.notna().values
    Fb = fit_pcs(Zb.values, mb, iters=60, seed=bi)
    lb, _, _ = cluster(implied_resid_corr(Fb['load'], Fb['psi']), K)
    co += (lb[:, None] == lb[None, :]); aris.append(adjusted_rand_score(labA, lb))
co /= B_N
print('bootstrap ARI vs full-data clusters: median %.3f, IQR %s' % (np.median(aris), np.round(np.percentile(aris, [25, 75]), 3)))
stab = np.array([np.mean([co[i, j] for j in np.where(labA == labA[i])[0] if j != i]) if (labA == labA[i]).sum() > 1 else np.nan
                 for i in range(n)])

# robustness: recent models only
recent = c.models()['released'].reindex(X.index) >= '2025-07-01'
Xr = X.loc[recent.values]
Xr = Xr.loc[:, Xr.notna().sum() >= 15]
Zr = Xr.apply(rank_normal)
Fr = fit_pcs(Zr.values, Zr.notna().values)
ix = [cols.index(x) for x in Xr.columns]
rec_agree = {}
for k in range(1, 4):
    rr = np.corrcoef(loadA[ix, k], Fr['load'][:, k])[0, 1]
    rec_agree[k + 1] = float(rr)
print('recent-only (models >= 2025-07, %d models, %d benches) loading r with full fit, PC2..4' % Xr.shape, {k: round(v, 3) for k, v in rec_agree.items()})
# best-matching component (rotation may reorder small PCs)
cm = np.corrcoef(np.column_stack([loadA[ix, 1:5], Fr['load'][:, 1:5]]).T)[:4, 4:]
print('cross-corr PC2-5 full (rows) vs recent (cols)\n', np.round(cm, 2))

# ------------------------------------------------------------------ 6. agreement with areas and publishers
areas = b.loc[cols, 'area'].values

def publisher(x):
    if b.at[x, 'board_source'] == 'card':
        return 'lab launch posts'
    if b.at[x, 'board_source'] == 'epoch':
        return 'epoch.ai'
    lk = (meta[x].get('links') or {}).get('leaderboard', '')
    u = urlparse(lk); host = u.netloc.replace('www.', '')
    if host in ('github.com', 'huggingface.co') and u.path:
        host += '/' + u.path.strip('/').split('/')[0]
    return host or x

pubs = np.array([publisher(x) for x in cols])
ari_area = adjusted_rand_score(areas, labA)
ari_pub = adjusted_rand_score(pubs, labA)
null = np.array([adjusted_rand_score(RNG.permutation(areas), labA) for _ in range(2000)])
nullp = np.array([adjusted_rand_score(RNG.permutation(pubs), labA) for _ in range(2000)])
print('ARI clusters vs area %.3f (perm 95th pct %.3f, p=%.4f) | vs board publisher %.3f (perm 95th %.3f)' % (
    ari_area, np.percentile(null, 95), np.mean(null >= ari_area), ari_pub, np.percentile(nullp, 95)))
labRaw, _, _ = cluster(np.corrcoef(np.where(mask, Zv, FA['fitted']), rowvar=False), K)
print('ARI vs area for clusters on raw correlation (PC1 kept): %.3f' % adjusted_rand_score(areas, labRaw))
# silhouette of area labels on residual distance
print('silhouette of almanac areas on residual distance: %.3f' % silhouette_score(DA, areas, metric='precomputed'))

# misfiled: mean residual correlation with each area's other members
Rr = RrA.copy(); np.fill_diagonal(Rr, np.nan)
area_aff = pd.DataFrame({a: np.nanmean(Rr[:, areas == a], axis=1) for a in np.unique(areas)}, index=cols)
mis = pd.DataFrame({'bench': cols, 'name': b.loc[cols, 'name'].values, 'area': areas,
                    'closest_area': area_aff.idxmax(axis=1).values,
                    'own_aff': [area_aff.loc[x, areas[i]] for i, x in enumerate(cols)],
                    'best_aff': area_aff.max(axis=1).values, 'cluster': labA, 'pub': pubs})
mis['gap'] = mis.best_aff - mis.own_aff
misfiled = mis[mis.area != mis.closest_area].sort_values('gap', ascending=False)
print('closest area (mean residual r) is not own area: %d of %d' % (len(misfiled), n))
print(misfiled.head(25).to_string())
print('\nown-area hit rate by area', (mis.area == mis.closest_area).groupby(mis.area).mean().round(2).to_dict())

for k in sorted(set(labA)):
    ids = [x for x, l in zip(cols, labA) if l == k]
    a = pd.Series(areas[labA == k]).value_counts(); p = pd.Series(pubs[labA == k]).value_counts()
    print(f'\n=== cluster {k} (n={len(ids)}) areas {a.to_dict()} pubs {p.head(4).to_dict()} stab {np.nanmean(stab[labA == k]):.2f}')
    print('   ', ', '.join(b.loc[ids, 'name'].tolist()))

pcs = pd.DataFrame({f'pc{k + 1}': loadA[:, k] for k in range(6)}, index=cols)
for k in range(1, 4):
    pcs[f'pc{k + 1}C'] = loadC[:, k]
pcs['name'] = b.loc[cols, 'name']; pcs['area'] = areas; pcs['pub'] = pubs; pcs['cluster'] = labA; pcs['stab'] = stab
rel = c.models()['released'].reindex(X.index)
pcs['med_model_release'] = [rel[X[x].notna()].median() for x in cols]
pcs['n_models'] = X.notna().sum().values
for k in ('pc2', 'pc3', 'pc4'):
    s = pcs.sort_values(k)
    print(f'\n{k} low:', s.head(12)[['name', 'area']].values.tolist())
    print(f'{k} high:', s.tail(12)[['name', 'area']].values.tolist())
    print(f'{k} vs median release of models scored: rho=%.2f' % spearmanr(pcs[k], pcs.med_model_release.astype('int64')).statistic)
print('\nmean loading by area\n', pcs.groupby('area')[['pc1', 'pc2', 'pc3', 'pc4']].mean().round(3))

ok = rel.notna().values
rho_time = spearmanr(model_pc1[ok], rel[ok].values.astype('int64')).statistic
print('Spearman(model PC1 score, release date) %.3f (n=%d)' % (rho_time, ok.sum()))
print('core model release range', rel.min().date(), rel.max().date(), 'median', rel.median().date())
ms = pd.DataFrame({f'pc{k + 1}': scoreA[:, k] for k in range(4)}, index=X.index)
ms['lab'] = c.models()['lab'].reindex(X.index); ms['released'] = rel; ms['n_obs'] = mask.sum(1)
vc = ms.lab.value_counts()
print('model scores by lab (labs with >=5 core models)\n', ms.groupby('lab')[['pc1', 'pc2', 'pc3', 'pc4']].mean().loc[vc[vc >= 5].index].round(2).join(vc))

pickle.dump(dict(cols=cols, rows=rows, X=X, Z=Z, varA=varA, varC=varC, r2=r2, cv=cv, base_mse=base_mse,
                 K_RANK=K_RANK, LAM=LAM, loadA=loadA, loadC=loadC, scoreA=scoreA, RrA=RrA, RrB=RrB,
                 labA=labA, labB=labB, linkA=linkA, DA=DA, stab=stab, co=co, areas=areas, pubs=pubs, sil=sil,
                 ari_area=ari_area, ari_pub=ari_pub, ari_AB=ari_AB, aris=aris, agree=agree, rec_agree=rec_agree,
                 misfiled=misfiled, mis=mis, pcs=pcs, ms=ms, rho_time=rho_time, pair_cov=pair_cov,
                 dropped_versions=dropped_versions, K=K, null=null, area_aff=area_aff),
            open(os.path.join(ROOT, 'clusters', 'results.pkl'), 'wb'))
