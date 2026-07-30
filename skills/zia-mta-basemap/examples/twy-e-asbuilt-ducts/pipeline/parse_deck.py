import re, json
from lxml import etree
A='http://schemas.openxmlformats.org/drawingml/2006/main'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
ns={'a':A,'p':P}

def shapes(slide):
    x=etree.parse(slide)
    out=[]
    for sp in x.iter('{%s}sp'%P):
        nv=sp.find('.//p:nvSpPr/p:cNvPr',ns)
        xf=sp.find('.//a:xfrm',ns)
        if xf is None: continue
        off=xf.find('a:off',ns); ext=xf.find('a:ext',ns)
        pg=sp.find('.//a:prstGeom',ns)
        sf=sp.find('./p:spPr/a:solidFill/a:srgbClr',ns)
        ln=sp.find('./p:spPr/a:ln',ns)
        lc=ln.find('.//a:srgbClr',ns) if ln is not None else None
        dsh=ln.find('.//a:prstDash',ns) if ln is not None else None
        txt=''.join(t.text or '' for t in sp.iter('{%s}t'%A))
        out.append(dict(id=int(nv.get('id')), name=nv.get('name'),
            prst=pg.get('prst') if pg is not None else 'custom',
            x=int(off.get('x')), y=int(off.get('y')),
            cx=int(ext.get('cx')), cy=int(ext.get('cy')),
            flipH=xf.get('flipH')=='1', flipV=xf.get('flipV')=='1',
            rot=int(xf.get('rot') or 0),
            fill=sf.get('val') if sf is not None else None,
            line=lc.get('val') if lc is not None else None,
            w=int(ln.get('w')) if (ln is not None and ln.get('w')) else None,
            dash=dsh.get('val') if dsh is not None else None,
            text=txt))
    return out

if __name__=='__main__':
    for n in (2,3,4):
        sh=shapes(f'pptx_in/ppt/slides/slide{n}.xml')
        json.dump(sh, open(f'slide{n}_shapes.json','w'), indent=1)
        teal=[s for s in sh if s['prst']=='ellipse' and s['fill']]
        print(f'slide{n}: {len(sh)} shapes; filled ellipses(fittings)={len(teal)}',
              'gold-duct=',len([s for s in sh if s["line"]=="C7A400"]),
              'magenta-duct=',len([s for s in sh if s["line"]=="BB00BB"]),
              'grey-line=',len([s for s in sh if s["line"]=="7A8288"]))
