import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys, json, os; sys.path.insert(0,ROOT)
import common as c, pandas as pd, numpy as np
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT, '..', 'index')
os.makedirs(OUT,exist_ok=True)
R={}  # numbers for findings
df=c.items()
pct=FuncFormatter(lambda v,_: f'{v:.0f}%')
def yearaxis(ax, x0, x1):
    ax.set_xlim(pd.Timestamp(x0), pd.Timestamp(x1))
    ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(axis='x', visible=False)
def endlabel(ax, x, y, text, color, dy=0, **kw):
    ax.annotate(text, (x, y), xytext=(10, dy), textcoords='offset points', va='center', fontsize=15, color=c.INK, **kw)

# ---------------- core series
live=c.satbench_series(df)
R['live_now']=live.iloc[-1].to_dict()
first50=live[live.score>=50].iloc[0]; R['first50']=(str(first50.date.date()), first50.score)
prev=live[live.date==pd.Timestamp('2025-11-01')].iloc[0]
R['live_nov2025']=prev.to_dict()
for d in ['2023-01-01','2024-01-01','2025-01-01','2026-01-01']:
    R[f'live_{d}']=live[live.date==pd.Timestamp(d)].iloc[0].to_dict()
ed={}
for y in (2023,2024,2025):
    s=c.satbench_series(df, start=f'{y+1}-01-01', fixed_cutoff=pd.Timestamp(f'{y}-12-31'))
    ed[y]=s; R[f'ed{y}']=s.iloc[-1].to_dict(); R[f'ed{y}_start']=s.iloc[0].to_dict()
    R[f'ed{y}_cross85']=str(s[s.score>=85].date.min())

# ---------------- 1. HERO
fig,ax=c.figure("Even the benchmark of benchmarks is getting saturated",
    "SatBench: share of 173 widely used AI benchmarks where the best reported score has passed 85%.\n"
    "Live index adds benchmarks as they are released; fixed editions freeze the item set at year end.",
    notes=["Items: benchmarks named in 10+ AI lab launch posts, scored in %, higher is better. Best score from any source (leaderboards, Epoch AI, lab claims).",
           "Launch posts are sparse before 2025, so 2023-24 values are rough. Item selection uses citation counts as of today."],
    rect=[0.07,0.235,0.70,0.53])
ax.axhspan(85,100,color=c.GRID,alpha=0.55,lw=0,zorder=0)
ax.axhline(85,color=c.MUTED,lw=1.2,ls=(0,(4,3)),zorder=1)
ax.text(pd.Timestamp('2023-01-20'),87.5,'Saturated (85%)',fontsize=14,color=c.MUTED,va='bottom')
cols={2023:c.BLUES[1],2024:c.BLUES[2],2025:c.BLUES[3]}
end=c.AS_OF
for y,s in ed.items():
    ax.plot(s.date,s.score,color=cols[y],lw=2.6,zorder=3)
    ax.plot(s.date.iloc[0],s.score.iloc[0],'o',ms=6,color=cols[y],zorder=3)
ax.plot(live.date,live.score,color=c.INK,lw=3.4,zorder=4)
lab={2023:(ed[2023].score.iloc[-1],f"SatBench-2023  {ed[2023].score.iloc[-1]:.0f}%",4),
     2024:(ed[2024].score.iloc[-1],f"SatBench-2024  {ed[2024].score.iloc[-1]:.0f}%",2),
     2025:(ed[2025].score.iloc[-1],f"SatBench-2025  {ed[2025].score.iloc[-1]:.0f}%",1),
     'live':(live.score.iloc[-1],f"Live  {live.score.iloc[-1]:.0f}%",-6)}
for k,(y,t,dy) in lab.items():
    endlabel(ax,end,y,t,None,dy=dy,fontweight='bold' if k in ('live',2023) else 'normal')
# 2023 crossing
x23=ed[2023]; xc=x23[x23.score>=85].iloc[0]
ax.plot(xc.date,xc.score,'o',ms=11,mfc=c.ACCENT,mec=c.BG,mew=2,zorder=6)
ax.annotate(f"The 2023 edition (44 benchmarks)\ncrossed 85% in {xc.date:%b %Y}",(xc.date,xc.score),xytext=(pd.Timestamp('2025-01-15'),93),
            fontsize=14.5,color=c.INK,va='center',ha='left',arrowprops=dict(arrowstyle='-',color=c.MUTED,lw=1.2,connectionstyle='arc3,rad=-0.15'))
ax.annotate(f"Flat near 30% until early 2025",(pd.Timestamp('2024-03-01'),31),xytext=(pd.Timestamp('2023-06-01'),12),fontsize=14,color=c.MUTED,
            arrowprops=dict(arrowstyle='-',color=c.FAINT,lw=1))
ax.set_ylim(0,100); ax.yaxis.set_major_formatter(pct); ax.set_yticks([0,25,50,75,100])
yearaxis(ax,'2023-01-01','2026-12-01')
ax.text(pd.Timestamp('2024-01-10'),44,'2023 edition\nstarts', fontsize=12.5,color=c.FAINT,va='bottom')
c.save(fig,f'{OUT}/satbench_hero.png')

# ---------------- 2. ROBUSTNESS
rob={}
for t in (75,85,95): rob[f'thr{t}']=c.satbench_series(df,col=f'solved{t}')
rob['indep']=c.satbench_series(df,col='solved85_indep')
for k in (3,5,10,20):
    d=c.items(k); rob[f'mc{k}']=c.satbench_series(d); R[f'mc{k}_n']=len(d)
for k,s in rob.items():
    R[f'rob_{k}']={str(d.date()):round(v,1) for d,v in zip(s.date,s.score) if d in (pd.Timestamp('2024-01-01'),pd.Timestamp('2025-01-01'),pd.Timestamp('2026-01-01'),c.AS_OF)}
fig=plt.figure(figsize=(12,6.75),dpi=200)
fig.text(0.04,0.955,"The 2025-26 rise survives every definition we tried",fontsize=27,fontweight='bold',color=c.INK,va='top')
fig.text(0.04,0.885,"SatBench-live under alternative choices. Levels move; the post-2025 climb is in every version.",fontsize=15.5,color=c.MUTED,va='top')
notes=["Indep. = independent runs only (official leaderboards, Epoch AI), no lab self-reported scores; same 173 items, 44 of which have no independent runs.",
       "Dark line in each panel = default: 85% threshold, any source, named in 10+ launch posts. Dashed line: 85%.", c.CREDIT]
for i,l in enumerate(reversed(notes)): fig.text(0.04,0.025+i*0.033,l,fontsize=11.5,color=c.FAINT,va='bottom')
panels=[("Threshold for 'solved' (%)",[('thr75','75:',c.BLUES[1]),('thr85','85:',c.INK),('thr95','95:',c.BLUES[2])]),
        ("Source of scores",[('thr85','All:',c.INK),('indep','Indep.:',c.BLUES[2])]),
        ("Min. launch-post citations",[('mc3','3+:',c.BLUES[0]),('mc5','5+:',c.BLUES[1]),('mc10','10+:',c.INK),('mc20','20+:',c.BLUES[2])])]
W=0.21; gap=0.10
for i,(ttl,ser) in enumerate(panels):
    ax=fig.add_axes([0.065+i*(W+gap),0.23,W,0.54])
    if i>0: ax.tick_params(labelleft=False)
    ax.set_title(ttl,loc='left',fontsize=16.5,color=c.INK,fontweight='bold',pad=12)
    ends=[]
    for key,name,col in ser:
        s=rob[key]; s=s[s.date>='2023-07-01']
        ax.plot(s.date,s.score,color=col,lw=3 if col==c.INK else 2.4,zorder=4 if col==c.INK else 3)
        ends.append([s.score.iloc[-1],f"{name} {s.score.iloc[-1]:.0f}%"])
    # de-overlap labels (min 9 pts apart)
    ends.sort(key=lambda e:e[0])
    pos=[e[0] for e in ends]
    for j in range(1,len(pos)):
        if pos[j]-pos[j-1]<9: pos[j]=pos[j-1]+9
    for (v,t),p in zip(ends,pos):
        ax.annotate(t,(c.AS_OF,v),xytext=(c.AS_OF+pd.Timedelta(days=50),p),fontsize=13.5,color=c.INK,va='center',
                    annotation_clip=False, linespacing=1.0)
    ax.axhline(85,color=c.MUTED,lw=1,ls=(0,(4,3)))
    ax.set_ylim(0,100); ax.yaxis.set_major_formatter(pct); ax.set_yticks([0,25,50,75,100])
    ax.set_xlim(pd.Timestamp('2023-07-01'),c.AS_OF+pd.Timedelta(days=20))
    ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y')); ax.grid(axis='x',visible=False)
    ax.tick_params(labelsize=14)
c.save(fig,f'{OUT}/satbench_robustness.png')

# ---------------- 3. WORKING SET
S=[x for x in c.summaries() if (x['unit'] or '%')=='%' and x['better']!='lower']
cite_dates={x['id']:[(cc['card'],pd.Timestamp(cc['date'])) for cc in x['cites']] for x in S}
cross={x['id']:(pd.Timestamp(c.crossing(x['frontier'],85)['date']) if c.crossing(x['frontier'],85) else pd.NaT) for x in S}
def ws(t,k=2):
    lo=t-pd.DateOffset(months=6); n=sol=0; ids=[]
    for x in S:
        if len({cd for cd,d in cite_dates[x['id']] if lo<d<=t})>=k:
            n+=1; ids.append(x['id'])
            if pd.notna(cross[x['id']]) and cross[x['id']]<=t: sol+=1
    return n,sol,ids
wrows=[]
for t in list(pd.date_range('2024-01-01','2026-11-01',freq='MS'))+[c.AS_OF]:
    n,s,_=ws(t); n3,s3,_=ws(t,3)
    wrows.append(dict(date=t,n=n,sol=s,share=100*s/n if n else np.nan,n3=n3,share3=100*s3/n3 if n3 else np.nan))
W_=pd.DataFrame(wrows); W_=W_[W_.date>=W_[W_.n>=20].date.min()]
R['ws']=W_.round(1).to_dict('records')
wl=live[live.date>=W_.date.min()]
fig=plt.figure(figsize=(12,6.75),dpi=200)
fig.text(0.04,0.955,"Labs keep moving to tests AI hasn't solved yet",fontsize=27,fontweight='bold',color=c.INK,va='top')
fig.text(0.04,0.885,"Share past 85%: benchmarks labs are actively reporting (named in 2+ launch posts in the trailing 6 months)\nvs. SatBench-live, the stock of 173 widely used benchmarks (named in 10+ launch posts).",fontsize=15.5,color=c.MUTED,va='top',linespacing=1.45)
notes=["Working set: any benchmark in the almanac scored in %, higher is better; solved = best reported score from any source reached 85% by that date.",
       f"Starts {W_.date.min():%b %Y}, the first month with 20+ active benchmarks. Launch posts are sparse before 2025.", c.CREDIT]
for i,l in enumerate(reversed(notes)): fig.text(0.04,0.025+i*0.033,l,fontsize=11.5,color=c.FAINT,va='bottom')
ax=fig.add_axes([0.07,0.39,0.76,0.38]); axb=fig.add_axes([0.07,0.19,0.76,0.13],sharex=ax)
ax.plot(wl.date,wl.score,color=c.INK,lw=3.2)
ax.plot(W_.date,W_.share,color=c.ACCENT,lw=3.2)
ax.axhline(85,color=c.MUTED,lw=1,ls=(0,(4,3)))
endlabel(ax,c.AS_OF,wl.score.iloc[-1],f"SatBench-live  {wl.score.iloc[-1]:.0f}%",None,fontweight='bold')
endlabel(ax,c.AS_OF,W_.share.iloc[-1],f"Working set  {W_.share.iloc[-1]:.0f}%",None,fontweight='bold')
ax.set_ylim(0,100); ax.set_yticks([0,25,50,75,100]); ax.yaxis.set_major_formatter(pct)
ax.tick_params(labelbottom=False); ax.grid(axis='x',visible=False)
axb.bar(W_.date,W_.n,width=22,color=c.GREY,lw=0)
axb.set_ylim(0,300); axb.set_yticks([0,150,300]); axb.grid(axis='x',visible=False)
axb.set_title("Benchmarks in the working set",loc='left',fontsize=14,color=c.MUTED,pad=4)
axb.annotate(f"{W_.n.iloc[-1]}",(W_.date.iloc[-1],W_.n.iloc[-1]),xytext=(8,0),textcoords='offset points',fontsize=14,va='bottom',color=c.INK)
axb.annotate(f"{W_.n.iloc[0]}",(W_.date.iloc[0],W_.n.iloc[0]),xytext=(0,4),textcoords='offset points',fontsize=14,va='bottom',ha='center',color=c.INK)
axb.xaxis.set_major_locator(mdates.YearLocator()); axb.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axb.set_xlim(W_.date.min()-pd.Timedelta(days=20),c.AS_OF+pd.Timedelta(days=20))
c.save(fig,f'{OUT}/satbench_working_set.png')

# ---------------- 4. PROJECTION
rng=np.random.default_rng(7)
def risk_table(m0,m1):
    rows=[]
    for m in pd.date_range(m0,m1,freq='MS'):
        at=df[(df.released<m)&(df.solved85.isna()|(df.solved85>=m))]
        e=((at.solved85>=m)&(at.solved85<m+pd.offsets.MonthBegin(1)))
        rows+= [(i,int(v)) for i,v in zip(at.id,e)]
    return pd.DataFrame(rows,columns=['id','e'])
haz={}
for w,(a,b) in {'6m':('2026-05-01','2026-10-01'),'12m':('2025-11-01','2026-10-01'),'24m':('2024-11-01','2026-10-01'),'2025':('2025-01-01','2025-12-01')}.items():
    rt=risk_table(a,b); haz[w]=dict(events=int(rt.e.sum()),item_months=len(rt),h=rt.e.mean())
R['hazard']=haz
rt=risk_table('2025-11-01','2026-10-01'); g=rt.groupby('id').e.agg(['sum','size'])
boot=[]
for _ in range(4000):
    s=g.sample(len(g),replace=True,random_state=rng.integers(1e9)); boot.append(s['sum'].sum()/s['size'].sum())
boot=np.array(boot); R['h_boot_10_90']=list(np.percentile(boot,[10,50,90]))
# arrivals
y25=df[df.released.dt.year==2025]; A25=len(y25)/12
h1=df[(df.released>='2025-01-01')&(df.released<'2025-07-01')]; Ah1=len(h1)/6
y26=df[df.released.dt.year==2026]; A26=len(y26)/10.5
rec=df[df.released>='2025-01-01']; b=rec.born_solved.mean()
R['arrivals']=dict(A2025=A25,A2025H1=Ah1,A2026_obs=A26,n2025=len(y25),n2026=len(y26),born_share_2025_26=b,born_n=int(rec.born_solved.sum()),rec_n=len(rec))
N0=len(df); S0=int(df.solved85.notna().sum()); U0=N0-S0
need=int(np.ceil(0.85*N0)); R['fixed']=dict(N=N0,S=S0,U=U0,need=need)
H=12*14  # months ahead
months=pd.date_range('2026-12-01',periods=H,freq='MS')
def det_fixed(h): return 100*(N0-U0*(1-h)**np.arange(1,H+1))/N0
def cross_month(curve):
    i=np.argmax(curve>=85); return months[i] if curve[i]>=85 else None
for w in haz: R[f'fixed_cross_{w}']=str(cross_month(det_fixed(haz[w]['h'])))
# stochastic sims
nsim=4000; fx=np.zeros((nsim,H)); lv=np.zeros((nsim,H)); lv2=np.zeros((nsim,H))
for i in range(nsim):
    h=rng.choice(boot)
    U=U0
    for t in range(H):
        U-=rng.binomial(U,h); fx[i,t]=100*(N0-U)/N0
    for A,arr in ((A25,lv),(Ah1,lv2)):
        U=U0; N=N0
        for t in range(H):
            U-=rng.binomial(U,h); a=rng.poisson(A); bs=rng.binomial(a,b); U+=a-bs; N+=a
            arr[i,t]=100*(N-U)/N
def summ(arr):
    q=np.percentile(arr,[10,50,90],axis=0); return q
qf=summ(fx); ql=summ(lv); ql2=summ(lv2)
def cross_dist(arr):
    idx=[np.argmax(r>=85) if (r>=85).any() else None for r in arr]
    ds=[months[j] for j in idx if j is not None]; frac=len(ds)/len(arr)
    return frac, [str(pd.Series(ds).quantile(q).date()) for q in (0.1,0.5,0.9)] if ds else None
R['fixed_cross_sim']=cross_dist(fx); R['live_cross_sim_A2025']=cross_dist(lv); R['live_cross_sim_A2025H1']=cross_dist(lv2)
for yy in ('2027-12-01','2028-12-01','2030-12-01','2035-12-01','2040-11-01'):
    j=list(months).index(pd.Timestamp(yy))
    R[f'proj_{yy}']=dict(fixed=qf[:,j].round(1).tolist(),live=ql[:,j].round(1).tolist(),live_H1=ql2[:,j].round(1).tolist())
hm=haz['12m']['h']; R['live_steady_U']=A25*(1-b)/hm; R['live_steady_U_H1']=Ah1*(1-b)/hm
fixhist=c.satbench_series(df,fixed_cutoff=c.AS_OF)
fig,ax=c.figure("At 2026 rates, today's benchmarks are 85% solved by 2028",
    "Past and projected SatBench. Fixed: today's 173 benchmarks. Live: new benchmarks keep arriving.\n"
    "Projection: each unsolved benchmark has a 5% chance per month of being solved (rate over the last 12 months).",
    notes=[f"Hazard: {haz['12m']['events']} benchmarks crossed 85% in {haz['12m']['item_months']} unsolved benchmark-months (Nov 2025-Oct 2026). Bands: 10th-90th percentile of simulations.",
           f"Live: {A25:.1f} new benchmarks/month (2025 rate; 2026 releases are undercounted while they gather citations), {100*b:.0f}% already past 85% at release.",
           "A simple extrapolation, not a forecast: the remaining benchmarks may be harder, and new tests may be built to resist."],
    rect=[0.07,0.27,0.72,0.48])
x1=pd.Timestamp('2031-01-01'); mm=months<=x1
ax.axhline(85,color=c.MUTED,lw=1.2,ls=(0,(4,3)))
ax.text(pd.Timestamp('2023-02-01'),86.5,'Saturated (85%)',fontsize=14,color=c.MUTED,va='bottom')
ax.plot(fixhist.date,fixhist.score,color=c.BLUES[2],lw=2.6)
ax.plot(live.date,live.score,color=c.INK,lw=3.2)
ax.fill_between(months[mm],qf[0][mm],qf[2][mm],color=c.BLUES[1],alpha=0.35,lw=0)
ax.plot(months[mm],qf[1][mm],color=c.BLUES[2],lw=2.6,ls=(0,(5,2.5)))
ax.fill_between(months[mm],ql[0][mm],ql[2][mm],color=c.GREY,alpha=0.35,lw=0)
ax.plot(months[mm],ql[1][mm],color=c.INK,lw=2.6,ls=(0,(5,2.5)))
ax.axvline(c.AS_OF,color=c.FAINT,lw=1); ax.text(c.AS_OF-pd.Timedelta(days=25),5,'Today',ha='right',fontsize=14,color=c.MUTED)
fc=R['fixed_cross_sim'][1]
ax.plot(pd.Timestamp(fc[1]),85,'o',ms=11,mfc=c.ACCENT,mec=c.BG,mew=2,zorder=6)
ax.annotate(f"Today's 173 benchmarks pass 85%\naround {pd.Timestamp(fc[1]):%b %Y} (80% range {pd.Timestamp(fc[0]):%b %Y} to {pd.Timestamp(fc[2]):%b %Y})",
            (pd.Timestamp(fc[1]),85),xytext=(pd.Timestamp('2027-01-15'),34),fontsize=14,va='center',ha='left',color=c.INK,
            arrowprops=dict(arrowstyle='-',color=c.MUTED,lw=1.1,relpos=(0.15,1)))
j=list(months).index(pd.Timestamp('2030-12-01'))
endlabel(ax,months[j],qf[1][j],f"Fixed set  {qf[1][j]:.0f}%",None,dy=2,fontweight='bold')
endlabel(ax,months[j],ql[1][j],f"Live  {ql[1][j]:.0f}%",None,fontweight='bold')
ax.text(pd.Timestamp('2029-01-01'),ql[1][list(months).index(pd.Timestamp('2029-01-01'))]-9,
        "Live index keeps climbing but slowly:\nnew unsolved benchmarks keep arriving",fontsize=14,color=c.MUTED,va='top')
ax.set_ylim(0,100); ax.set_yticks([0,25,50,75,100]); ax.yaxis.set_major_formatter(pct)
yearaxis(ax,'2023-01-01',x1)
c.save(fig,f'{OUT}/satbench_projection.png')

# ---------------- 5. AREAS
ar=df.assign(sol=df.solved85.notna()).groupby('area').agg(n=('id','size'),sol=('sol','sum'))
ar['pct']=100*ar.sol/ar.n; R['areas']=ar.round(1).to_dict('index')
ar=ar[ar.n>=10].sort_values('pct')
names={'knowledge':'Knowledge','multimodal':'Multimodal','agents':'Agents','code':'Code','reasoning':'Reasoning','work':'Work tasks'}
fig,ax=c.figure("Most reasoning tests are beaten; most work tests are not",
    f"SatBench items past 85% today, by area. All areas: {100*S0/N0:.0f}% ({S0} of {N0}).",
    notes=["Areas as labelled by Benchmark Almanac. Two areas with one benchmark each (safety, other) are not shown.",
           "Best reported score from any source, incl. lab claims."],rect=[0.20,0.20,0.66,0.58])
yy=np.arange(len(ar))
ax.barh(yy,ar.pct,height=0.62,color=c.BLUES[3],lw=0)
ax.barh(yy,100-ar.pct,left=ar.pct,height=0.62,color=c.GRID,lw=0)
for i,(k,r) in enumerate(ar.iterrows()):
    ax.text(r.pct+1.5 if r.pct<90 else r.pct-1.5,i,f"{r.pct:.0f}%  ({int(r.sol)} of {int(r.n)})",va='center',ha='left',fontsize=15,color=c.INK)
ax.set_yticks(yy); ax.set_yticklabels([f"{names.get(k,k)}" for k in ar.index],fontsize=17,color=c.INK)
ax.set_xlim(0,100); ax.xaxis.set_major_formatter(pct); ax.set_xticks([0,25,50,75,100]); ax.grid(axis='y',visible=False)
ax.tick_params(axis='y',length=0)
c.save(fig,f'{OUT}/satbench_by_area.png')

json.dump(R,open(os.path.join(OUT, 'numbers.json'),'w'),indent=1,default=str)
print(json.dumps(R,indent=1,default=str)[:6000])
