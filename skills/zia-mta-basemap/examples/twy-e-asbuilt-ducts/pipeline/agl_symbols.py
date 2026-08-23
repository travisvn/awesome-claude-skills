"""As-built AGL asset symbology.

Symbol per asset type, coloured to the light's own showing where it has one (ICAO/AC
convention: taxiway centreline green, taxiway edge blue, stop bar red, runway guard
amber), and shaped by family so the drawing reads without colour: circle = light,
square = civil chamber, triangle = earthing, rectangle = sign foundation.

The works-action overlay from Rev P05/P06 is deliberately NOT touched by any of this --
action symbology on a field-governed drawing should not move under the crew's feet.
These symbols are the base as-built asset layer only.
"""
import sys, json, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS",
                 "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures
from ducts import sheet_window, inv, FRAME
from parse_deck import shapes

RING={'CC0000','0055CC','E8710A','9AA0A6'}      # Rev P05 works-action ring colours
FRAME_R=FRAME['x']+FRAME['w']

# asset_type -> (legend text, shape, fill, outline, size EMU, order)
SYM = {
 'Taxiway centreline light':      ('TWY CENTRELINE LIGHT',      'ellipse', '1E8E3E', '0B5323',  91440, 10),
 'Taxiway edge light':            ('TWY EDGE LIGHT',            'ellipse', '1A56DB', '0B2E7A',  91440, 20),
 'Stop bar light':                ('STOP BAR LIGHT',            'ellipse', 'CC0000', '7A0000',  91440, 30),
 'Lead-in light':                 ('LEAD-IN LIGHT',             'ellipse', '2E9E4F', '13502A',  91440, 40),
 'Holding position light':        ('HOLDING POSITION LIGHT',    'ellipse', 'E8B000', '8A6900',  91440, 50),
 'Runway guard light / RRM':      ('RUNWAY GUARD LIGHT / RRM',  'ellipse', 'E8B000', '8A6900', 100584, 60),
 'Runway centreline light':       ('RWY CENTRELINE LIGHT',      'ellipse', 'FFFFFF', '5F6368',  91440, 70),
 'Runway edge light':             ('RWY EDGE LIGHT',            'ellipse', 'FFFFFF', '5F6368',  91440, 80),
 'RETIL':                         ('RETIL',                     'ellipse', 'E8B000', '8A6900',  91440, 90),
 'Existing light base':           ('EXISTING LIGHT BASE (NO FITTING)', 'ellipse', None, '5F6368', 100584, 100),
 'New light base':                ('NEW LIGHT BASE',            'ellipse', None, '1E8E3E', 100584, 110),
 'Sign foundation':               ('SIGN FOUNDATION',           'rect',    '5D4037', '3A2520', 100584, 120),
 'Handhole':                      ('HANDHOLE (HH)',             'rect',    None,     'BB00BB', 128016, 130),
 'Existing handhole':             ('EXISTING HANDHOLE',         'rect',    None,     'BB00BB', 128016, 140),
 'Existing transformer handhole': ('TRANSFORMER HANDHOLE (SECONDARY FEED HUB)', 'rect', None, '00838F', 146304, 150),
 'Existing transformer pit':      ('TRANSFORMER PIT',           'rect',    None,     '00838F', 146304, 160),
 'Manhole':                       ('MANHOLE (MH)',              'rect',    None,     '7B1FA2', 173736, 170),
 'Existing manhole':              ('EXISTING MANHOLE',          'rect',    None,     '7B1FA2', 173736, 175),
 'Existing transformer manhole':  ('TRANSFORMER MANHOLE (SEC. FEED)', 'rect', None,   '00838F', 173736, 180),
 'Transformer handhole':          ('TRANSFORMER HANDHOLE',      'rect',    None,     '00838F', 146304, 155),
 'Earthing point':                ('EARTHING POINT',            'triangle','795548', '3E2A23',  82296, 190),
 'Earthing pit':                  ('EARTHING PIT',              'triangle',None,     '795548', 100584, 200),
}

def works_markers(slide_xml):
    """Rev P05 works-action rings -- assets these sit on keep their action symbology."""
    out=[]
    for s in shapes(slide_xml):
        if s['prst']!='ellipse' or s['fill'] is not None: continue
        if s['line'] not in RING or s['x']>FRAME_R: continue
        out.append((s['x']+s['cx']/2, s['y']+s['cy']/2))
    return out

def sheet_assets(loc, T, slide_xml):
    """Every as-built asset inside the sheet frame, typed, flagged for whether a Rev P05
    works-action marker already claims it and whether Rev P05 drew it at all."""
    L,W = sheet_window(T)
    src = load_fixtures(bbox=W.bounds, assets_only=True).reset_index(drop=True)
    if len(src)==0: return []
    emu = inv(T, src[['x','y']].to_numpy(float))
    wm = works_markers(slide_xml)
    wtree = cKDTree(np.array(wm)) if wm else None
    deck = json.load(open('deck_fittings.json'))[loc]
    dtree = cKDTree(np.array([[p['px'],p['py']] for p in deck],float)) if deck else None
    out=[]
    for i,(x,y) in enumerate(emu):
        t = src.asset_type[i]
        if t not in SYM: continue                       # never invent a symbol for an unmapped type
        claimed = bool(wtree is not None and wtree.query([x,y])[0] < 140000)
        drawn   = bool(dtree is not None and dtree.query([x,y])[0] < 140000)
        out.append(dict(type=t, leaf=src.leaf[i], x=float(x), y=float(y),
                        local_x=float(src.x[i]), local_y=float(src.y[i]),
                        works_claimed=claimed, drawn_in_p05=drawn))
    return out

if __name__=='__main__':
    reg=json.load(open('registration.json'))
    census={}
    for loc,sl in (('LOC-01',2),('LOC-02',3),('LOC-03',4)):
        r=reg[loc]; T=dict(s=r['s'],theta=r['theta'],t=np.array(r['t']),reflect=r['reflect'])
        a=sheet_assets(loc,T,f'pptx_in/ppt/slides/slide{sl}.xml')
        census[loc]=a
        c=collections.Counter(x['type'] for x in a)
        new=sum(1 for x in a if not x['drawn_in_p05'])
        claimed=sum(1 for x in a if x['works_claimed'])
        print(f'{loc}: {len(a)} typed as-built assets in frame '
              f'({claimed} already carry a works-action ring, {new} were not drawn in Rev P05)')
        for k in sorted(c, key=lambda k: SYM[k][5]):
            print(f'    {SYM[k][0]:44s} {c[k]:3d}')
        print()
    json.dump(census, open('asset_census.json','w'))
    print('saved asset_census.json')
