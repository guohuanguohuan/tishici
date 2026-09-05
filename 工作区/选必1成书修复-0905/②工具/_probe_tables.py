# -*- coding: utf-8 -*-
import sys, io, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s'%(W,t)
def celltext(tc):
    return ''.join(t.text or '' for t in tc.iter(q('t')))
def cellsum(tc):
    gs = tc.find(q('tcPr'))
    span=vm=tcw=''
    if gs is not None:
        g=gs.find(q('gridSpan')); span='跨'+g.get(q('val')) if g is not None else ''
        v=gs.find(q('vMerge'))
        if v is not None: vm='vM'+(v.get(q('val')) or '续')
        w=gs.find(q('tcW'))
        if w is not None: tcw=w.get(q('w'))
    nom=len(tc.findall('.//{%s}oMath'%M)) + len(tc.findall('.//{%s}oMathPara'%M))
    ndraw=len(tc.findall('.//{%s}drawing'%W))
    txt=celltext(tc).replace('\r','')
    paras=tc.findall(q('p'))
    pstyles=[]
    for p in paras:
        ppr=p.find(q('pPr'))
        st=''
        if ppr is not None:
            ps=ppr.find(q('pStyle'))
            st=ps.get(q('val')) if ps is not None else ''
        pstyles.append(st)
    return span,vm,tcw,nom,ndraw,len(paras),pstyles,txt

def dump(f, idx, label):
    z=zipfile.ZipFile('副本/'+f)
    doc=etree.fromstring(z.read('word/document.xml'))
    z.close()
    body=doc.find(q('body'))
    tbls=list(body.iter(q('tbl')))
    tbl=tbls[idx]
    print('\n'+'='*80)
    print('### %s  [%s 表%d]  rows=%d'%(label,f,idx,len(tbl.findall(q('tr')))))
    # tblPr / grid
    tblpr=tbl.find(q('tblPr'))
    grid=tbl.find(q('tblGrid'))
    if grid is not None:
        gc=[c.get(q('w')) for c in grid.findall(q('gridCol'))]
        print('  tblGrid(%d列): %s sum=%s'%(len(gc),gc,sum(int(x) for x in gc)))
    if tblpr is not None:
        tw=tblpr.find(q('tblW'))
        print('  tblW:', (tw.get(q('w')),tw.get(q('type'))) if tw is not None else None)
        ind=tblpr.find(q('tblInd'))
        print('  tblInd:', ind.get(q('w')) if ind is not None else None)
        jc=tblpr.find(q('jc'))
        print('  jc:', jc.get(q('val')) if jc is not None else None)
    for ri,tr in enumerate(tbl.findall(q('tr'))):
        trpr=tr.find(q('trPr'))
        trinfo=''
        if trpr is not None:
            if trpr.find(q('tblHeader')) is not None: trinfo+='tblHeader,'
            if trpr.find(q('cantSplit')) is not None: trinfo+='cantSplit,'
            th=trpr.find(q('trHeight'))
            if th is not None: trinfo+='h=%s(%s),'%(th.get(q('val')),th.get(q('hRule')) or '')
        cells=tr.findall(q('tc'))
        print('  row%d [%s] %d格'%(ri,trinfo,len(cells)))
        for ci,tc in enumerate(cells):
            span,vm,tcw,nom,ndraw,np_,pstyles,txt = cellsum(tc)
            meta=' '.join(x for x in ['gridSpan=%s'%span if span else '', vm, 'w=%s'%tcw if tcw else '',
                   ('oMath%d'%nom if nom else ''), ('图%d'%ndraw if ndraw else ''), 'p=%d'%np_] if x)
            tdisp = txt[:40] + ('…' if len(txt)>40 else '')
            print('    c%d %s | pStyle=%s | 「%s」'%(ci, meta, pstyles, tdisp))
