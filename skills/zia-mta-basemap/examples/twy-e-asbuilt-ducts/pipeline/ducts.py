"""Clip the real as-built duct geometry to each sheet window and convert to slide EMU."""
import sys, json, math
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np, pandas as pd
from shapely import wkt as swkt
from shapely.geometry import box, LineString, MultiLineString
from basemap import load_routes, load_fixtures

DUCT = r"DUCT|CONDUIT|SAWCUT|SECONDARY|SEC[_ ]"
FRAME = dict(x=320040, y=777240, w=9555480, h=9555480)   # plot frame on slides 2-4, EMU

# how each source layer is drawn: (display name, colour, width EMU, dash)
STYLE = {
 'CV_OUTER DUCT 4x110mm dia':   ('EX DUCTBANK 4x110 mm (outer)', '0B3D91', 22225, 'solid'),
 'CV_INNER DUCT 4x110mm dia':   ('EX DUCTBANK 4x110 mm (inner)', '0B3D91', 12700, 'solid'),
 'CV_STH DUCT 6x110mm dia':     ('EX DUCT 6x110 mm (south)',     '6A1B9A', 22225, 'solid'),
 'CV_DUCT CROSSING 6x110mm dia':('EX DUCT CROSSING 6x110 mm',    'C2185B', 22225, 'solid'),
 'CV-EX SEC CONDUIT':           ('EX SECONDARY CONDUIT',         '00838F', 15875, 'solid'),
 'CV-NEW SEC CONDUIT':          ('NEW SECONDARY CONDUIT',        '1E8E3E', 15875, 'sysDash'),
 'CV-NEW SEC SAWCUT':           ('NEW SECONDARY IN SAWCUT',      'E8710A', 15875, 'sysDash'),
 'CV_GRND DUCT':                ('EARTHING DUCT',                '795548',  9525, 'sysDot'),
}

def inv(T, P):
    """local grid metres -> slide EMU"""
    P = np.atleast_2d(np.asarray(P, float))
    th = T['theta']; R = np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]])
    Q = ((P - T['t'])/T['s']) @ R
    if T['reflect']: Q = Q*np.array([1.0,-1.0])
    return Q

def fwd(T, P):
    P = np.atleast_2d(np.asarray(P,float)).copy()
    if T['reflect']: P[:,1] = -P[:,1]
    th=T['theta']; R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]])
    return T['s']*(P@R.T) + T['t']

def sheet_window(T):
    """the four frame corners, in local grid metres"""
    f=FRAME
    corners=np.array([[f['x'],f['y']],[f['x']+f['w'],f['y']],
                      [f['x']+f['w'],f['y']+f['h']],[f['x'],f['y']+f['h']]],float)
    L=fwd(T,corners)
    return L, box(L[:,0].min(), L[:,1].min(), L[:,0].max(), L[:,1].max())

def ducts_for(T, pad=0.0):
    L, W = sheet_window(T)
    if pad: W = W.buffer(pad, join_style=2)
    b = W.bounds
    r = load_routes(leaf_regex=DUCT, bbox=(b[0]-5,b[1]-5,b[2]+5,b[3]+5))
    out=[]
    for _,row in r.iterrows():
        g = swkt.loads(row.wkt)
        c = g.intersection(W)
        if c.is_empty: continue
        parts = list(c.geoms) if isinstance(c,(MultiLineString,)) else [c]
        for p in parts:
            if not isinstance(p, LineString) or p.length < 0.05: continue
            out.append(dict(leaf=row.leaf, xref=row.xref, approx=int(row.approx),
                            clipped_m=p.length, coords=list(p.coords)))
    return out, W

if __name__=='__main__':
    reg=json.load(open('registration.json')); res={}
    for loc in ('LOC-01','LOC-02','LOC-03'):
        r=reg[loc]; T=dict(s=r['s'],theta=r['theta'],t=np.array(r['t']),reflect=r['reflect'])
        d,W=ducts_for(T)
        for it in d:
            e=inv(T, it['coords'])
            it['emu']=[[int(round(a)),int(round(b))] for a,b in e]
        res[loc]=dict(window_wkt=W.wkt, ducts=d,
                      transform=dict(s=r['s'],theta=r['theta'],t=list(r['t']),reflect=r['reflect']))
        df=pd.DataFrame([{k:v for k,v in x.items() if k not in ('coords','emu')} for x in d])
        g=df.groupby('leaf').agg(segments=('clipped_m','size'), on_sheet_m=('clipped_m','sum'))
        print(f'=== {loc}: {len(d)} duct segments on sheet, {df.clipped_m.sum():.1f} m inside the frame')
        print(g.round(1).to_string()); print()
    json.dump(res, open('sheet_ducts.json','w'))
    print('saved sheet_ducts.json')
