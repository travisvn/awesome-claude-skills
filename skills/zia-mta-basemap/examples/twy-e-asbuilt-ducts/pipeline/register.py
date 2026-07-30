"""Register deck slide space (EMU) -> ZIA local grid (m).

Method follows references/coordinates.md:
  1. type-matched 2-point RANSAC to establish the correspondence (anchors drawn from
     the rarest asset types, so the candidate set stays small),
  2. 4-parameter Helmert (tx, ty, rotation, uniform scale) by least squares on the
     inliers -- not an affine, which would absorb error into fake shear,
  3. hold-out validation on pairs the fit never saw.
Reflection is allowed because PowerPoint y grows downward while the grid y grows up.
"""
import sys, json, math, itertools, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures

CORRIDOR = (5400, 53850, 6560, 55120)
SCALE_LO, SCALE_HI = 78_000, 108_000       # EMU per metre
TOL_M = 1.2

def helmert(src, dst, reflect):
    S = src.astype(float).copy()
    if reflect: S[:,1] = -S[:,1]
    cs, cd = S.mean(0), dst.mean(0)
    A, B = S-cs, dst-cd
    theta = math.atan2((A[:,0]*B[:,1]-A[:,1]*B[:,0]).sum(), (A*B).sum())
    R = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
    s = ((A@R.T)*B).sum() / (A*A).sum()
    return dict(s=s, theta=theta, t=cd - s*(R@cs), reflect=reflect)

def apply(T, pts):
    P = np.atleast_2d(pts).astype(float).copy()
    if T['reflect']: P[:,1] = -P[:,1]
    th=T['theta']; R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]])
    return T['s']*(P@R.T) + T['t']

def register(deck, fx, verbose=True):
    D = np.array([[p['px'],p['py']] for p in deck], float)
    dtype = [p['type'] for p in deck]
    M = fx[['x','y']].to_numpy(float); mtype = fx['asset_type'].tolist()
    tree = cKDTree(M)
    pop = collections.Counter(mtype)
    tidx = {t: np.array([i for i,v in enumerate(mtype) if v==t]) for t in set(dtype) if t in pop}

    anchors=[]
    for i,j in itertools.combinations(range(len(D)),2):
        if dtype[i]!=dtype[j] or dtype[i] not in tidx: continue
        d=math.dist(D[i],D[j])
        if d < 1_200_000: continue
        anchors.append((pop[dtype[i]], -d, i, j))       # rarest type first, then longest baseline
    anchors.sort()
    anchors=anchors[:40]
    probe=np.linspace(0,len(D)-1,min(10,len(D))).astype(int)
    if verbose:
        print(f'  deck pts={len(D)}  corridor fixtures={len(M)}  anchors={len(anchors)}'
              f'  anchor types={sorted({dtype[a[2]] for a in anchors})}')
    best=None; tried=0
    for _,_,i,j in anchors:
        idx=tidx[dtype[i]]; P=M[idx]; sub=cKDTree(P)
        d_emu=math.dist(D[i],D[j]); lo,hi=d_emu/SCALE_HI, d_emu/SCALE_LO
        pairs=sub.query_pairs(hi, output_type='ndarray')
        if len(pairs)==0: continue
        dm=np.linalg.norm(P[pairs[:,0]]-P[pairs[:,1]],axis=1)
        pairs=pairs[dm>=lo]
        src=D[[i,j]]
        for a,b in pairs:
            for k,l in ((idx[a],idx[b]),(idx[b],idx[a])):
                for refl in (True,False):
                    tried+=1
                    T=helmert(src, M[[k,l]], refl)
                    dd,_=tree.query(apply(T,D[probe]))
                    if (dd<TOL_M).sum()<4: continue
                    dd,mi=tree.query(apply(T,D))
                    ok=(dd<TOL_M) & np.array([mtype[m]==dt for m,dt in zip(mi,dtype)])
                    if best is None or ok.sum()>best['score']:
                        best=dict(score=int(ok.sum()),T=T,inliers=ok.copy(),mi=mi.copy(),
                                  resid=float(np.sqrt((dd[ok]**2).mean())))
    if verbose: print(f'  hypotheses={tried}  best type-consistent inliers={best["score"] if best else 0}/{len(D)}')
    return best, D, dtype, M, mtype, tree

def refine(best, D, dtype, M, mtype, tree, rounds=6):
    """Re-fit Helmert on inliers and re-associate, until stable."""
    ok=best['inliers']; mi=best['mi']; T=best['T']
    for _ in range(rounds):
        T=helmert(D[ok], M[mi[ok]], T['reflect'])
        dd,mi=tree.query(apply(T,D))
        new=(dd<TOL_M) & np.array([mtype[m]==dt for m,dt in zip(mi,dtype)])
        if new.sum()==0: break
        if (new==ok).all(): ok=new; break
        ok=new
    dd,mi=tree.query(apply(T,D))
    ok=(dd<TOL_M) & np.array([mtype[m]==dt for m,dt in zip(mi,dtype)])
    return T, ok, mi, dd

if __name__=='__main__':
    fx=load_fixtures(bbox=CORRIDOR, assets_only=True)
    deckall=json.load(open('deck_fittings.json'))
    out={}
    for loc in ('LOC-01','LOC-02','LOC-03'):
        print(loc, flush=True)
        best,D,dtype,M,mtype,tree = register(deckall[loc], fx)
        if best is None or best['score']<6:
            print('  NO CONVERGENCE'); continue
        T,ok,mi,dd = refine(best,D,dtype,M,mtype,tree)
        # hold-out: fit on even-indexed inliers, validate on odd
        ii=np.where(ok)[0]
        Tf=helmert(D[ii[0::2]], M[mi[ii[0::2]]], T['reflect'])
        hv=np.linalg.norm(apply(Tf,D[ii[1::2]])-M[mi[ii[1::2]]],axis=1)
        q=apply(T,D)
        print(f'  scale        = {1/T["s"]:,.0f} EMU/m   (plot window {9_555_480*T["s"]:.1f} m across)')
        print(f'  rotation     = {math.degrees(T["theta"]):.4f} deg   reflect={T["reflect"]}')
        print(f'  matched      = {ok.sum()}/{len(D)} deck fittings, type-consistent')
        print(f'  fit RMS      = {math.sqrt((dd[ok]**2).mean()):.3f} m   max {dd[ok].max():.3f} m')
        print(f'  HOLD-OUT RMS = {math.sqrt((hv**2).mean()):.3f} m  on {len(hv)} pairs never fitted')
        print(f'  window       = x[{q[:,0].min():.1f},{q[:,0].max():.1f}] y[{q[:,1].min():.1f},{q[:,1].max():.1f}]')
        out[loc]=dict(s=T['s'],theta=T['theta'],t=T['t'].tolist(),reflect=bool(T['reflect']),
                      matched=int(ok.sum()),n=len(D),rms=float(math.sqrt((dd[ok]**2).mean())),
                      maxres=float(dd[ok].max()), holdout_rms=float(math.sqrt((hv**2).mean())),
                      holdout_n=int(len(hv)),
                      inliers=ok.tolist(), match=mi.tolist(), resid=dd.tolist(),
                      window=[float(q[:,0].min()),float(q[:,1].min()),float(q[:,0].max()),float(q[:,1].max())])
        json.dump(out, open('registration.json','w'), indent=1)
