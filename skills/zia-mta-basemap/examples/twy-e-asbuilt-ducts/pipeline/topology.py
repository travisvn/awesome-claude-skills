"""Chain the secondary-conduit fragments into runs by endpoint snapping, and read off the
feed topology. The source drawing stores these as loose segments; the chaining below is
MINE, at a stated 0.30 m snap tolerance, and is reported as such."""
import sys, json, math, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures

SNAP=0.30
def build(loc, sd, fx, ftree):
    segs=[it for it in sd[loc]['ducts'] if 'SEC CONDUIT' in it['leaf'] or 'SEC SAWCUT' in it['leaf']]
    if not segs: return None
    pts=[]; seg_nodes=[]
    for it in segs:
        a,b=tuple(it['coords'][0]), tuple(it['coords'][-1])
        pts += [a,b]
    P=np.array(pts); t=cKDTree(P)
    nid=-np.ones(len(P),int); nodes=[]
    for i in range(len(P)):
        if nid[i]>=0: continue
        grp=[g for g in t.query_ball_point(P[i],SNAP) if nid[g]<0]
        k=len(nodes)
        for g in grp: nid[g]=k
        nodes.append(P[grp].mean(0))
    nodes=np.array(nodes)
    adj=collections.defaultdict(list)
    for k,it in enumerate(segs):
        u,v=nid[2*k], nid[2*k+1]
        if u==v: continue
        L=sum(math.dist(it['coords'][i],it['coords'][i+1]) for i in range(len(it['coords'])-1))
        adj[u].append((v,L,it['leaf'])); adj[v].append((u,L,it['leaf']))
    deg={k:len(v) for k,v in adj.items()}
    # hubs: the transformer handholes the fans radiate from
    hubs=[]
    for k,d in deg.items():
        dd,j=ftree.query(nodes[k])
        if d>=3 and dd<0.30 and 'ETRANS' in fx.iloc[j].leaf:
            hubs.append((int(k),str(fx.iloc[j].leaf),float(dd)))
    runs=[]
    for h,hleaf,hd in hubs:
        for start,_,_ in adj[h]:
            # walk outward until a leaf or a junction
            prev,cur,length,leaves=h,start,0.0,None
            path=[h]
            while True:
                nxt=[(v,L) for v,L,_ in adj[cur] if v!=prev]
                seg=[L for v,L,_ in adj[prev] if v==cur]
                length+=seg[0] if seg else 0.0
                path.append(cur)
                if len(nxt)!=1: break
                prev,cur=cur,nxt[0][0]
            dd,j=ftree.query(nodes[cur])
            runs.append(dict(hub=int(h),hub_layer=hleaf,end=int(cur),length_m=round(length,2),
                             end_fixture=str(fx.iloc[j].leaf), end_type=str(fx.iloc[j].asset_type),
                             end_dist=round(float(dd),3), hops=len(path)-1))
    return dict(n_segments=len(segs), n_nodes=len(nodes), hubs=hubs, runs=runs,
                degrees=[int(v) for v in sorted(deg.values(), reverse=True)])

if __name__=='__main__':
    sd=json.load(open('sheet_ducts.json'))
    fx=load_fixtures(assets_only=True).reset_index(drop=True)
    ftree=cKDTree(fx[['x','y']].to_numpy(float))
    out={}
    for loc in ('LOC-01','LOC-02','LOC-03'):
        r=build(loc,sd,fx,ftree)
        out[loc]=r
        print(f'=== {loc}: {r["n_segments"]} secondary segments -> {r["n_nodes"]} nodes, '
              f'{len(r["hubs"])} transformer-handhole hubs, {len(r["runs"])} spurs')
        for h,hl,hd in r['hubs']: print(f'   hub node {h} on {hl} (offset {hd:.3f} m)')
        for s in sorted(r['runs'], key=lambda z:-z['length_m']):
            print(f"   spur {s['length_m']:7.2f} m ({s['hops']} seg) -> {s['end_type']:32s} "
                  f"[{s['end_fixture']}] at {s['end_dist']:.2f} m")
        print()
    json.dump(out, open('topology.json','w'), indent=1)
