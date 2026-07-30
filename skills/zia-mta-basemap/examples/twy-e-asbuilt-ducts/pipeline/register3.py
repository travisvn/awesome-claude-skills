"""LOC-02 / LOC-03 by axis-aligned search.

LOC-01 solved to sub-mm with rotation 0.0001 deg and a y-reflection, i.e. the sheets are
plotted axis-aligned to the ZIA local grid. So for the remaining sheets assume
    x_local =  s*x_emu + tx        y_local = -s*y_emu + ty
Each candidate (deck pair, fixture pair) then yields s twice -- once from dx, once from
dy -- and the two must agree. That is a hard filter no coincidence survives.
Every hit is then re-fitted with a FREE 4-parameter Helmert (scale and rotation both
unheld) so the assumption is tested, not baked in.
"""
import sys, json, math, itertools, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures
from register import helmert, apply, CORRIDOR

TOL_M=1.2; SREL=0.004          # scale-agreement tolerance between the dx- and dy-derived s
fx=load_fixtures(bbox=CORRIDOR, assets_only=True).reset_index(drop=True)
M=fx[['x','y']].to_numpy(float); mtype=fx['asset_type'].tolist(); tree=cKDTree(M)
pop=collections.Counter(mtype)

def solve(deck, name):
    D=np.array([[p['px'],p['py']] for p in deck],float); dt=[p['type'] for p in deck]
    tidx={t:np.array([i for i,v in enumerate(mtype) if v==t]) for t in set(dt) if t in pop}
    cand=[]
    for i,j in itertools.combinations(range(len(D)),2):
        if dt[i]!=dt[j] or dt[i] not in tidx: continue
        dx,dy=D[j]-D[i]
        if abs(dx)<200_000 or abs(dy)<200_000: continue     # need both axes to test s twice
        cand.append((pop[dt[i]], -(dx*dx+dy*dy), i, j))
    cand.sort(); cand=cand[:200]
    best=None; tried=0
    for _,_,i,j in cand:
        idx=tidx[dt[i]]; P=M[idx]
        dxe,dye=D[j]-D[i]
        for a,b in itertools.permutations(range(len(P)),2):
            dxm,dym=P[b]-P[a]
            s1=dxm/dxe; s2=-dym/dye
            if s1<=0 or abs(s1-s2)>SREL*s1: continue
            s=(s1+s2)/2
            if not (5e-6 < s < 2.5e-5): continue            # 40k..200k EMU/m
            T=dict(s=s,theta=0.0,reflect=True,
                   t=np.array([P[a][0]-s*D[i][0], P[a][1]+s*D[i][1]]))
            tried+=1
            dd,mi=tree.query(apply(T,D))
            ok=(dd<TOL_M)&np.array([mtype[m]==t for m,t in zip(mi,dt)])
            if best is None or ok.sum()>best[0]: best=(int(ok.sum()),T,ok.copy(),mi.copy())
    n,T,ok,mi=best
    for _ in range(8):                                      # FREE re-fit: s and theta unheld
        T=helmert(D[ok], M[mi[ok]], True)
        dd,mi=tree.query(apply(T,D))
        ok=(dd<TOL_M)&np.array([mtype[m]==t for m,t in zip(mi,dt)])
    dd,mi=tree.query(apply(T,D))
    ok=(dd<TOL_M)&np.array([mtype[m]==t for m,t in zip(mi,dt)])
    print(f'{name}: axis-aligned candidates tested={tried}')
    return T,ok,mi,dd,D

reg=json.load(open('registration.json')); deckall=json.load(open('deck_fittings.json'))
for loc in ('LOC-02','LOC-03'):
    T,ok,mi,dd,D=solve(deckall[loc],loc)
    ii=np.where(ok)[0]
    Tf=helmert(D[ii[0::2]], M[mi[ii[0::2]]], True)
    hv=np.linalg.norm(apply(Tf,D[ii[1::2]])-M[mi[ii[1::2]]],axis=1)
    q=apply(T,D)
    print(f'   matched {ok.sum()}/{len(D)}   free-refit scale={1/T["s"]:,.1f} EMU/m   rot={math.degrees(T["theta"]):+.5f} deg')
    print(f'   fit RMS={math.sqrt((dd[ok]**2).mean()):.4f} m  max={dd[ok].max():.4f} m   HOLD-OUT RMS={math.sqrt((hv**2).mean()):.4f} m on {len(hv)} pairs')
    print(f'   window x[{q[:,0].min():.1f},{q[:,0].max():.1f}] y[{q[:,1].min():.1f},{q[:,1].max():.1f}]')
    reg[loc]=dict(s=T['s'],theta=T['theta'],t=T['t'].tolist(),reflect=True,
                  matched=int(ok.sum()),n=len(D),rms=float(math.sqrt((dd[ok]**2).mean())),
                  maxres=float(dd[ok].max()),holdout_rms=float(math.sqrt((hv**2).mean())),
                  holdout_n=int(len(hv)),inliers=ok.tolist(),match=mi.tolist(),resid=dd.tolist(),
                  window=[float(q[:,0].min()),float(q[:,1].min()),float(q[:,0].max()),float(q[:,1].max())])
json.dump(reg, open('registration.json','w'), indent=1)
