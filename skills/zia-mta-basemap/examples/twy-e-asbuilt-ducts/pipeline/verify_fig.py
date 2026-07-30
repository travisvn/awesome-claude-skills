"""Verification figure for sheet 6: real duct geometry vs the Rev P05 indicative lines,
in the source drawing's own grid."""
import sys, json, math
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from basemap import load_fixtures
from ducts import STYLE, fwd, sheet_window
from parse_deck import shapes
INDICATIVE={'C9CDD2','BB00BB'}          # per the Rev P05 legend

reg=json.load(open('registration.json')); sd=json.load(open('sheet_ducts.json'))
deckall=json.load(open('deck_fittings.json'))
fig,axes=plt.subplots(1,3,figsize=(21,7.2))
for ax,(loc,sl) in zip(axes,(('LOC-01',2),('LOC-02',3),('LOC-03',4))):
    r=reg[loc]; T=dict(s=r['s'],theta=r['theta'],t=np.array(r['t']),reflect=r['reflect'])
    L,W=sheet_window(T); b=W.bounds
    fx=load_fixtures(bbox=(b[0]-5,b[1]-5,b[2]+5,b[3]+5), assets_only=True)
    ax.scatter(fx.x,fx.y,s=7,c='#c9cdd2',zorder=1,label=f'source-drawing fixtures ({len(fx)})')
    first=True
    for s in shapes(f'pptx_in/ppt/slides/slide{sl}.xml'):
        if s['prst']!='line' or s['line'] not in INDICATIVE: continue
        if s['x']>320040+9555480: continue
        x0,y0=s['x'],s['y']; x1,y1=s['x']+s['cx'],s['y']+s['cy']
        if s['flipH']: x0,x1=x1,x0
        if s['flipV']: y0,y1=y1,y0
        P=fwd(T,[[x0,y0],[x1,y1]])
        ax.plot(P[:,0],P[:,1],color='#d4a017',lw=1.1,ls=':',zorder=2,
                label='Rev P05 INDICATIVE duct (removed)' if first else None); first=False
    seen=set()
    for it in sd[loc]['ducts']:
        nm,col,w,dash=STYLE[it['leaf']]
        C=np.array(it['coords'])
        ax.plot(C[:,0],C[:,1],color='#'+col,lw=max(1.1,w/9500),
                ls='--' if dash!='solid' else '-',zorder=3,
                label=nm if nm not in seen else None); seen.add(nm)
    D=np.array([[p['px'],p['py']] for p in deckall[loc]],float); Q=fwd(T,D)
    ok=np.array(r['inliers'])
    ax.scatter(Q[ok,0],Q[ok,1],s=42,marker='x',c='#0055cc',lw=1.5,zorder=6,
               label='sheet fitting matched to source')
    ax.plot(*W.exterior.xy,color='#1e2761',lw=1.5,zorder=4,label='sheet frame')
    ax.set_title(f'{loc}  ·  registration hold-out RMS {r["holdout_rms"]*1000:.2f} mm',fontsize=11)
    ax.set_aspect('equal'); ax.legend(fontsize=6.4,loc='upper right',framealpha=.92)
    ax.grid(alpha=.18); ax.set_xlabel('ZIA local grid X (m)',fontsize=8)
    ax.set_ylabel('ZIA local grid Y (m)',fontsize=8)
    ax.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig('verify_fig.png',dpi=140,facecolor='white')
print('wrote verify_fig.png')
