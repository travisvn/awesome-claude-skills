"""LOC-02 / LOC-03, anchored on the fitting classes that matched LOC-01 to sub-mm
(taxiway centreline lights, stop bar lights, sign foundations).

In LOC-01 the handhole / pit / RRM symbols sat a consistent ~2.4 m off the nearest DXF
fixture, so they are drawn symbols, not surveyed positions -- anchoring on them is what
pulled the earlier LOC-02/03 attempts into local optima.

Search: rotation is ~0 and y is reflected (established on LOC-01), so a deck pair fixes
the direction a fixture pair must run in. Walk each fixture along that ray only.
"""
import sys, json, math, itertools, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures
from register import helmert, apply, CORRIDOR

TOL_M=1.2; PERP=0.6; SLO,SHI=5e-6,2.5e-5
GOOD={'Taxiway centreline light','Stop bar light','Sign foundation'}
fx=load_fixtures(bbox=CORRIDOR, assets_only=True).reset_index(drop=True)
M=fx[['x','y']].to_numpy(float); mtype=fx['asset_type'].tolist(); tree=cKDTree(M)

def solve(deck,name,ndeckpairs=60):
    D=np.array([[p['px'],p['py']] for p in deck],float); dt=[p['type'] for p in deck]
    tidx={t:np.array([i for i,v in enumerate(mtype) if v==t]) for t in set(dt)&GOOD}
    pairs=[]
    for i,j in itertools.combinations(range(len(D)),2):
        if dt[i]!=dt[j] or dt[i] not in tidx: continue
        d=math.dist(D[i],D[j])
        if d<800_000: continue
        pairs.append((-d,i,j))
    pairs.sort(); pairs=pairs[:ndeckpairs]
    best=None; tried=0
    for _,i,j in pairs:
        idx=tidx[dt[i]]; P=M[idx]; sub=cKDTree(P)
        de=D[j]-D[i]; L=math.hypot(*de)
        u=np.array([de[0],-de[1]])/L                 # mirrored direction the fixture pair must run
        rmin,rmax=L*SLO, L*SHI
        for a in range(len(P)):
            nb=sub.query_ball_point(P[a], rmax)
            if not nb: continue
            V=P[nb]-P[a]; r=np.linalg.norm(V,axis=1)
            along=V@u; perp=np.abs(V[:,0]*u[1]-V[:,1]*u[0])
            sel=(r>=rmin)&(perp<PERP)&(along>0)
            for b_i in np.where(sel)[0]:
                s=along[b_i]/L; tried+=1
                T=dict(s=s,theta=0.0,reflect=True,
                       t=np.array([P[a][0]-s*D[i][0], P[a][1]+s*D[i][1]]))
                dd,mi=tree.query(apply(T,D))
                ok=(dd<TOL_M)&np.array([mtype[q]==t for q,t in zip(mi,dt)])
                if best is None or ok.sum()>best[0]: best=(int(ok.sum()),T,ok.copy(),mi.copy())
    n_,T,ok,mi=best
    for _ in range(10):
        T=helmert(D[ok],M[mi[ok]],True); dd,mi=tree.query(apply(T,D))
        ok=(dd<TOL_M)&np.array([mtype[q]==t for q,t in zip(mi,dt)])
    dd,mi=tree.query(apply(T,D))
    ok=(dd<TOL_M)&np.array([mtype[q]==t for q,t in zip(mi,dt)])
    print(f'{name}: hypotheses={tried}  anchor types={sorted(tidx)}')
    return T,ok,mi,dd,D

reg=json.load(open('registration.json')); deckall=json.load(open('deck_fittings.json'))
for loc in ('LOC-02','LOC-03'):
    T,ok,mi,dd,D=solve(deckall[loc],loc)
    ii=np.where(ok)[0]
    Tf=helmert(D[ii[0::2]],M[mi[ii[0::2]]],True)
    hv=np.linalg.norm(apply(Tf,D[ii[1::2]])-M[mi[ii[1::2]]],axis=1)
    q=apply(T,D); exact=(dd<0.05).sum()
    print(f'   matched {ok.sum()}/{len(D)}  ({exact} within 50 mm)  free-refit scale={1/T["s"]:,.1f} EMU/m  rot={math.degrees(T["theta"]):+.5f} deg')
    print(f'   fit RMS={math.sqrt((dd[ok]**2).mean()):.4f} m  max={dd[ok].max():.4f} m   HOLD-OUT RMS={math.sqrt((hv**2).mean()):.4f} m on {len(hv)}')
    print(f'   window x[{q[:,0].min():.1f},{q[:,0].max():.1f}] y[{q[:,1].min():.1f},{q[:,1].max():.1f}]')
    reg[loc]=dict(s=T['s'],theta=T['theta'],t=T['t'].tolist(),reflect=True,
                  matched=int(ok.sum()),n=len(D),exact50mm=int(exact),
                  rms=float(math.sqrt((dd[ok]**2).mean())),maxres=float(dd[ok].max()),
                  holdout_rms=float(math.sqrt((hv**2).mean())),holdout_n=int(len(hv)),
                  inliers=ok.tolist(),match=mi.tolist(),resid=dd.tolist(),
                  window=[float(q[:,0].min()),float(q[:,1].min()),float(q[:,0].max()),float(q[:,1].max())])
json.dump(reg,open('registration.json','w'),indent=1); print('saved')
