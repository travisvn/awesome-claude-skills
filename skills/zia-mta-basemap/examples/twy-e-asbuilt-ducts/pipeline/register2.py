"""LOC-02 / LOC-03: seed scale+rotation from the LOC-01 solution (all three sheets were
plotted by one script at one scale), search translation only, then re-fit a FREE
4-param Helmert on the inliers to confirm scale and rotation come back independently."""
import sys, json, math, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures
from register import helmert, apply, CORRIDOR, TOL_M

fx=load_fixtures(bbox=CORRIDOR, assets_only=True)
M=fx[['x','y']].to_numpy(float); mtype=fx['asset_type'].tolist(); tree=cKDTree(M)
deckall=json.load(open('deck_fittings.json'))
reg=json.load(open('registration.json'))
S=reg['LOC-01']['s']; TH=reg['LOC-01']['theta']; RF=reg['LOC-01']['reflect']

def solve(deck):
    D=np.array([[p['px'],p['py']] for p in deck],float); dt=[p['type'] for p in deck]
    base=dict(s=S,theta=TH,reflect=RF,t=np.zeros(2))
    B=apply(base,D)                              # correctly scaled/rotated, wrong origin
    best=None
    for i in range(len(D)):
        cand=[k for k,t in enumerate(mtype) if t==dt[i]]
        for k in cand:
            T=dict(base); T['t']=M[k]-B[i]
            dd,mi=tree.query(B+T['t'])
            ok=(dd<TOL_M)&np.array([mtype[m]==t for m,t in zip(mi,dt)])
            if best is None or ok.sum()>best[0]: best=(int(ok.sum()),T,ok.copy(),mi.copy())
    n,T,ok,mi=best
    # now free re-fit: scale + rotation are NOT held
    for _ in range(6):
        T=helmert(D[ok], M[mi[ok]], RF)
        dd,mi=tree.query(apply(T,D))
        ok=(dd<TOL_M)&np.array([mtype[m]==t for m,t in zip(mi,dt)])
    dd,mi=tree.query(apply(T,D))
    ok=(dd<TOL_M)&np.array([mtype[m]==t for m,t in zip(mi,dt)])
    return T,ok,mi,dd,D

for loc in ('LOC-02','LOC-03'):
    T,ok,mi,dd,D=solve(deckall[loc])
    ii=np.where(ok)[0]
    Tf=helmert(D[ii[0::2]], M[mi[ii[0::2]]], RF)
    hv=np.linalg.norm(apply(Tf,D[ii[1::2]])-M[mi[ii[1::2]]],axis=1)
    q=apply(T,D)
    print(f'{loc}: matched {ok.sum()}/{len(D)}  free-refit scale={1/T["s"]:,.1f} EMU/m  '
          f'rot={math.degrees(T["theta"]):+.5f} deg')
    print(f'   fit RMS={math.sqrt((dd[ok]**2).mean()):.4f} m  max={dd[ok].max():.4f} m  '
          f'HOLD-OUT RMS={math.sqrt((hv**2).mean()):.4f} m on {len(hv)} pairs')
    print(f'   window x[{q[:,0].min():.1f},{q[:,0].max():.1f}] y[{q[:,1].min():.1f},{q[:,1].max():.1f}]')
    reg[loc]=dict(s=T['s'],theta=T['theta'],t=T['t'].tolist(),reflect=bool(RF),
                  matched=int(ok.sum()),n=len(D),rms=float(math.sqrt((dd[ok]**2).mean())),
                  maxres=float(dd[ok].max()),holdout_rms=float(math.sqrt((hv**2).mean())),
                  holdout_n=int(len(hv)),inliers=ok.tolist(),match=mi.tolist(),resid=dd.tolist(),
                  window=[float(q[:,0].min()),float(q[:,1].min()),float(q[:,0].max()),float(q[:,1].max())])
json.dump(reg, open('registration.json','w'), indent=1)
print('\nsaved registration.json')
