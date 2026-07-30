"""Extract deck fitting positions (EMU) with as-built asset IDs, per location slide."""
import json, math
from parse_deck import shapes

FITTING_FILL = {'12A5B8','0055CC','E8710A','1E8E3E','9AA0A6'}

def deck_fittings(slide_xml):
    sh = shapes(slide_xml)
    ell = [s for s in sh if s['prst']=='ellipse']
    labels = [s for s in sh if s['text'] and s['prst']=='rect' and 2 < len(s['text']) < 32
              and not s['text'].startswith(('SCOPE','LEGEND','GENERAL','LOCATION'))]
    for s in ell:
        s['px']=s['x']+s['cx']/2; s['py']=s['y']+s['cy']/2
    # dedupe concentric markers, keep the smallest (the fitting itself)
    ded=[]
    for s in sorted(ell, key=lambda s:s['cx']):
        if not any(math.dist((s['px'],s['py']),(d['px'],d['py']))<20000 for d in ded):
            ded.append(s)
    # nearest label
    for s in ded:
        if labels:
            b=min(labels,key=lambda l:(l['x']+l['cx']/2-s['px'])**2+(l['y']+l['cy']/2-s['py'])**2)
            s['asset']=b['text']
            s['label_d']=math.dist((b['x']+b['cx']/2,b['y']+b['cy']/2),(s['px'],s['py']))
        else:
            s['asset']=''; s['label_d']=None
    return [dict(px=s['px'],py=s['py'],asset=s['asset'],label_d=s['label_d'],
                 fill=s['fill'],line=s['line'],d=s['cx']) for s in ded]

CLASS = [
    ('SBC',  'Stop bar light'),
    ('TCCECH','Taxiway centreline light'),
    ('TCC',  'Taxiway centreline light'),
    ('TEC',  'Taxiway centreline light'),
    ('RRM',  'Runway guard light / RRM'),
    ('SGC',  'Sign foundation'),
    ('EL.EBASE','Existing light base'),
    ('EL.NBASE','New light base'),
    ('HH',   'Existing handhole'),
    ('MH',   'Existing manhole'),
    ('X_CV_STH_PITS','Existing transformer pit'),
    ('P',    'Existing transformer pit'),
]
def classify(asset):
    a=asset.replace(' ','')
    for pre,typ in CLASS:
        if a.upper().startswith(pre.upper()): return typ
    return 'Unknown'

if __name__=='__main__':
    out={}
    for n,loc in ((2,'LOC-01'),(3,'LOC-02'),(4,'LOC-03')):
        f=deck_fittings(f'pptx_in/ppt/slides/slide{n}.xml')
        for s in f: s['type']=classify(s['asset'])
        out[loc]=f
        import collections
        print(loc, len(f), dict(collections.Counter(s['type'] for s in f)))
    json.dump(out, open('deck_fittings.json','w'), indent=1)
