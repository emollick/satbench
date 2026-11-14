from data import *
PEAK_MIN = 10
cs = cards(); ci = cites()
W0 = AS_OF - pd.DateOffset(months=6)
den = cs.groupby('period').size(); denF = cs[cs.frontier].groupby('period').size()
fam = ci.drop_duplicates(['family', 'date', 'lab', 'model'])
cnt = fam.groupby(['family', 'period']).size().unstack().reindex(columns=PERIODS).fillna(0)
cntF = fam[fam.frontier].groupby(['family', 'period']).size().unstack().reindex(columns=PERIODS).fillna(0)
cntNF = fam[~fam.frontier].groupby(['family', 'period']).size().unstack().reindex(columns=PERIODS).fillna(0)
sh = cnt / den[PERIODS] * 100
shF = (cntF / denF[PERIODS] * 100).reindex(sh.index).fillna(0)
denNF = den - denF
shNF = (cntNF / denNF[PERIODS] * 100).reindex(sh.index).fillna(0)
nF6 = cs[cs.frontier & (cs.date > W0)].shape[0]; nNF6 = cs[~cs.frontier & (cs.date > W0)].shape[0]
rec = fam[fam.date > W0]
recF = rec[rec.frontier].groupby('family').size().reindex(sh.index).fillna(0)
recNF = rec[~rec.frontier].groupby('family').size().reindex(sh.index).fillna(0)
peak = sh.max(axis=1); peak_period = sh.idxmax(axis=1)
peak_n = pd.Series([cnt.at[f, p] for f, p in peak_period.items()], index=sh.index)

def members(f):
    return [k for k in B.index if fam_of(k) == f]

def main_member(f):
    m = members(f)
    return max(m, key=lambda k: B.at[k, 'n_cites'])

rows = []
for f in sh.index:
    if not (peak[f] >= PEAK_MIN and peak_n[f] >= 5): continue
    g = fam[fam.family == f]
    gF = g[g.frontier]
    m = main_member(f)
    lastF = gF.date.max() if len(gF) else pd.NaT
    lastFrow = gF.sort_values('date').iloc[-1] if len(gF) else None
    vals = [best_at(k, lastF) for k in members(f) if B.at[k, 'unit'] == '%'] if pd.notna(lastF) else []
    best_end = np.nanmax(vals) if len(vals) and np.isfinite(vals).any() else np.nan
    succ = B.at[m, 'successor'] if isinstance(B.at[m, 'successor'], str) else None
    succ_fam = None; succ_first = pd.NaT
    if succ and succ in B.index:
        sf = fam_of(succ)
        if sf == f: succ = None
        else:
            succ_fam = sf
            sg = fam[(fam.family == sf) & fam.frontier]
            succ_first = sg.date.min() if len(sg) else pd.NaT
    rows.append(dict(family=f, main=m, name=B.at[m, 'name'], area=B.at[m, 'area'], released=B.at[m, 'released'],
                     peak=peak[f], peak_period=peak_period[f], peak_n=peak_n[f], peakF=shF.loc[f].max(),
                     lastF=lastF, lastF_who=(f"{lastFrow.lab}/{lastFrow.model}" if lastFrow is not None else ''),
                     last=g.date.max(), recF=recF[f], recNF=recNF[f], status=B.at[m, 'status'], why=B.at[m, 'why'],
                     best_end=best_end, sat_at=B.at[m, 'saturated_at'], successor=succ,
                     succ_name=(B.at[succ, 'name'] if succ else None), succ_first=succ_first,
                     **{f'sh {p}': sh.at[f, p] for p in PERIODS}, **{f'shF {p}': shF.at[f, p] for p in PERIODS},
                     **{f'shNF {p}': shNF.at[f, p] for p in PERIODS}))
T = pd.DataFrame(rows).set_index('family')
T['extinct'] = (T.recF <= 1) & (T.peakF >= 10)
def cause(r):
    sat = pd.notna(r.best_end) and r.best_end >= 85
    rep = r.successor is not None and pd.notna(r.succ_first)
    if sat and rep: return 'saturated + replaced'
    if sat: return 'saturated'
    if rep: return 'replaced'
    return 'other'
T['cause'] = T.apply(cause, axis=1)
META = dict(nF6=nF6, nNF6=nNF6, W0=W0, den=den, denF=denF)
if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
    print(META)
    print(T.sort_values('peak', ascending=False)[['name','peak','peak_period','peakF','lastF','lastF_who','recF','recNF','status','why','best_end','successor','succ_first','cause','extinct']].round(1).to_string())
