# -*- coding: utf-8 -*-
"""FX4-F 主控修复（一次到位）：从原始document.xml重建终态。
含：S1结构折叠+S2选项归一+空run补；S3 399克隆；S4编注（rPr正确包裹）；S5图移位+空格。"""
import copy, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
ns = {'w': W, 'm': M}
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)

def make_text_run(text, style_run):
    r = etree.Element(q('r'))
    rpr = style_run.find(q('rPr'))
    if rpr is not None: r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, q('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return r

def make_omath(text):
    om = etree.Element(mq('oMath'))
    mr = etree.SubElement(om, mq('r'))
    mt = etree.SubElement(mr, mq('t'))
    mt.text = text
    return om

def omtext(om): return ''.join(x.text or '' for x in om.iter(mq('t')))

def split_out(p, frag, r, t):
    """把 t 内 frag 切出为 oMath，插在 r 后；after 文字另起 run 在 oMath 后。"""
    i0 = t.text.index(frag)
    before, after = t.text[:i0], t.text[i0+len(frag):]
    t.text = before
    pos = list(p).index(r)
    p.insert(pos+1, make_omath(frag))
    if after: p.insert(pos+2, make_text_run(after, r))

def flatten_big_run(p):
    """把嵌套大run拍平：其 rPr+直属t 包成新run；oMath/嵌套r 原样提升为段级。"""
    rs = [c for c in p if etree.QName(c).localname == 'r']
    big = rs[2]
    kids = list(big)
    assert etree.QName(kids[0]).localname == 'rPr'
    pos = list(p).index(big)
    newr = etree.Element(q('r'))
    newr.append(kids[0])
    if len(kids) > 1 and kids[1].tag == q('t'):
        newr.append(kids[1])
        rest = kids[2:]
    else:
        rest = kids[1:]
    p.remove(big)
    p.insert(pos, newr)
    for j, ch in enumerate(rest):
        p.insert(pos+1+j, ch)

tree = etree.parse('F_unzip/word/document.xml')
body = tree.getroot().find('w:body', ns)
paras = body.findall('w:p', ns)
assert len(paras) == 1066
P = {i: paras[i] for i in range(len(paras))}
def runs(p): return [c for c in p if etree.QName(c).localname == 'r']
def strip_stops(p):
    ppr = p.find(q('pPr'))
    if ppr is not None:
        for st in ppr.findall(q('tabs')): ppr.remove(st)
def tabs_of(p):
    return [(r, tb) for r in runs(p) for tb in r.findall(q('tab'))]
def tab_to_sep(r_run, tab_el):
    idx = list(r_run).index(tab_el)
    r_run.remove(tab_el)
    t = etree.Element(q('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = '；'
    r_run.insert(idx, t)
def tab_drop(r_run, tab_el):
    r_run.remove(tab_el)
    if not [c for c in r_run if etree.QName(c).localname != 'rPr']:
        r_run.getparent().remove(r_run)

log = []
# ===== S2 选项归一 =====
specs = [
    (163,['S','S'],[('A．；','A．'),('C．；','C．')]), (202,['S','S'],[('A．；','A．'),('C．；','C．')]),
    (321,['S','S','S'],[('A．；','A．'),('B．；','B．'),('C．；','C．')]), (375,['S','D'],[('．；','．')]),
    (427,['D','D','D'],[]), (453,['D','D','D'],[]),
    (482,['S','S','S'],[('A．；','A．'),('B．；','B．'),('C．；','C．')]),
    (489,['S','S','S'],[('A．；','A．'),('B．；','B．'),('C．；','C．')]),
    (500,['S'],[]), (501,['S'],[('C．；','C．')]),
    (542,['S','S','S'],[('A．；','A．'),('B．；','B．'),('C．；','C．')]),
    (614,['D','D','D'],[]), (622,['D','D','D'],[]), (643,['D','D','D'],[]), (719,['D','D','D'],[]),
    (761,['D','D','D'],[]), (781,['S','S','S'],[]), (793,['D','D','D'],[]), (798,['D','D','D'],[]),
    (845,['D','D','D'],[]), (938,['S','S','S'],[]), (1006,['S','S','S'],[('A．；','A．'),('C．；','C．')]),
    (399,['S','S'],[('A．；','A．'),('C．；','C．')]),
]
for i, ops, fixes in specs:
    p = P[i]; ts = tabs_of(p)
    assert len(ts)==len(ops), (i, len(ts), len(ops))
    for (r,tb),op in zip(ts,ops):
        tab_to_sep(r,tb) if op=='S' else tab_drop(r,tb)
    for old,new in fixes:
        done=False
        for r in runs(p):
            for t in r.findall(q('t')):
                if (t.text or '')==old: t.text=new; done=True; break
            if done: break
        assert done, (i, old)
    strip_stops(p)
for i in (76,271,333): strip_stops(P[i])
n=0
for r in runs(P[117]):
    for t in r.findall(q('t')):
        if (t.text or '')=='\u00a0\u00a0\u00a0\u00a0': t.text='；'; n+=1
assert n==3
log.append('S2 选项归一：%d段tab处置＋3段stops＋117nbsp×3' % len(specs))

# 空run边界补；（B→C边界与长句选项粘连）
import re as _re
patA = _re.compile(r'^[B-D]$|^[B-D]．')
fixed_b = []
for i in (163,202,333,399,514,1019):
    p = P[i]
    tss = [t for t in p.iter(q('t'))]
    for j,t in enumerate(tss):
        if (t.text or '') != '': continue
        nxt = None
        for k in range(j+1,len(tss)):
            if (tss[k].text or '')!='': nxt=tss[k].text; break
        if nxt and patA.match(nxt):
            t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
            t.text='；'; fixed_b.append(i)
log.append('S2b 边界空run补；：%s' % fixed_b)

# ===== S3 [399] C/D 克隆 =====
sp = etree.fromstring(zipfile.ZipFile(r"C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\模块8大招2动点问题处理策略（解题大招）.docx").read('word/document.xml'))
tgt = None
for pp in sp.iter(q('p')):
    t = ''.join(x.text or '' for x in pp.iter() if x.tag in (q('t'), mq('t')))
    if t.startswith('C．'): tgt = pp; break
oms = tgt.findall('.//'+mq('oMath'))
assert len(oms)==2
c_m, d_m = copy.deepcopy(oms[0]), copy.deepcopy(oms[1])
p399 = P[399]
for txt, mth in (('C．',c_m), ('D．',d_m)):
    for r in runs(p399):
        tt = r.find(q('t'))
        if tt is not None and (tt.text or '')==txt:
            r.addnext(mth); break
log.append('S3 [399] C/D源克隆')

# ===== S4 编注 =====
p = P[102]
for r in runs(p):
    for t in r.findall(q('t')):
        if t.text and '定长√2' in t.text: split_out(p,'√2',r,t); break
p = P[176]
for r in runs(p):
    for t in r.findall(q('t')):
        if t.text and '∠OMF=90°' in t.text: split_out(p,'∠OMF=90°',r,t); break
p = P[519]
for r in runs(p):
    for t in r.findall(q('t')):
        if t.text and '(c−a)²' in t.text: split_out(p,'r1·r2=(c−a)²',r,t); break

# [800]
p = P[800]
flatten_big_run(p)
def add_mr(om, text):
    mr=etree.SubElement(om, mq('r')); mt=etree.SubElement(mr, mq('t')); mt.text=text
frag1='|PM|²=|PA|²−|AM|²=|PA|²−1'
for r in runs(p):
    for t in r.findall(q('t')):
        if t.text and frag1 in t.text: split_out(p,frag1,r,t); break
for r in runs(p):
    for t in r.findall(q('t')):
        if t.text and '√3' in t.text:
            i0=t.text.index('√3'); before,after=t.text[:i0],t.text[i0+2:]
            t.text=before
            om=make_omath('√3'); r.addnext(om)
            if after: om.addnext(make_text_run(after,r))
            break
x_om=next(o for o in p if etree.QName(o).localname=='oMath' and omtext(o)=='x²')
y_om=next(o for o in p if etree.QName(o).localname=='oMath' and omtext(o)=='y²')
r25=None
for r in runs(p):
    tt=r.find(q('t'))
    if tt is not None and (tt.text or '')=='/25+': r25=r; break
add_mr(x_om,'/25+')
for ch in list(y_om): x_om.append(ch)
p.remove(y_om); p.remove(r25)
for r in runs(p):
    tt=r.find(q('t'))
    if tt is not None and (tt.text or '').startswith('/16=1'):
        add_mr(x_om,'/16=1')
        rest=tt.text[5:]
        if rest: tt.text=rest
        else: p.remove(r)
        break
log.append('S4 [800] 拍平+|PM|²链+√3+x²/25+y²/16=1合并')

# [963]
p = P[963]
flatten_big_run(p)
for r in runs(p):
    for t in r.findall(q('t')):
        if t.text and '∠APB' in t.text: split_out(p,'∠APB',r,t); break
def merge_pair(p, first, slash, second):
    o1=next(o for o in p if etree.QName(o).localname=='oMath' and omtext(o)==first)
    o2=next(o for o in p if etree.QName(o).localname=='oMath' and omtext(o)==second)
    rs2=None
    for r in runs(p):
        tt=r.find(q('t'))
        if tt is not None and (tt.text or '')==slash: rs2=r; break
    assert rs2 is not None
    add_mr(o1, slash)
    for ch in list(o2): o1.append(ch)
    p.remove(o2); p.remove(rs2)
merge_pair(p,'x²','/','a²+y²=1')
merge_pair(p,'e²=1−1','/','a²')
o3=next(o for o in p if etree.QName(o).localname=='oMath' and omtext(o)=='(0,√6')
for r in runs(p):
    tt=r.find(q('t'))
    if tt is not None and (tt.text or '').startswith('/3)'):
        add_mr(o3,'/3)')
        rest=tt.text[3:]
        if rest: tt.text=rest
        else: p.remove(r)
        break
log.append('S4 [963] 拍平+∠APB+三处合并')

# ===== S5 图移位+空格 =====
p858, p851 = P[858], P[851]
body.remove(p858)
body.insert(list(body).index(p851)+1, p858)
sp100=[r for r in runs(P[100]) if r.find(q('t')) is not None and (r.find(q('t')).text or '')==' ']
sp100[0].find(q('t')).text='\u00a0\u00a0'; sp100[1].find(q('t')).text='\u00a0\u00a0'
for r in runs(P[181]):
    for t in r.findall(q('t')):
        if (t.text or '')=='. ': t.text='.'
for i in (338,787):
    p=P[i]; last=None
    for r in runs(p):
        for t in r.findall(q('t')): last=(r,t)
    if last and (last[1].text or '')==' ': p.remove(last[0])
log.append('S5 图移位+空格4段')

# ===== S1 结构折叠（最后） =====
body.remove(P[0])
sect=body.find(q('sectPr'))
order=['headerReference','footerReference','pgSz','pgMar','pgNumType','cols','docGrid']
keep={}
for ch in list(sect):
    ln=etree.QName(ch).localname
    if ln in order: keep[ln]=ch; sect.remove(ch)
    else: raise AssertionError('sectPr子元素:'+ln)
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
href=etree.Element(q('headerReference')); href.set(q('type'),'default'); href.set('{%s}id'%R,'rId305')
fref=etree.Element(q('footerReference')); fref.set(q('type'),'default'); fref.set('{%s}id'%R,'rId9')
pgn=etree.Element(q('pgNumType')); pgn.set(q('start'),'50')
keep['headerReference']=href; keep['footerReference']=fref; keep['pgNumType']=pgn
for nm in order: sect.append(keep[nm])
log.append('S1 段[0]删+sectPr折叠')

# ===== 终检断言 =====
assert len(body.findall('w:sectPr', ns))==1
assert len(list(body.iter(q('tab'))))==0
assert len(list(body.iter(q('tabs'))))==0
stray = [p for p in body.findall('w:p', ns) if any(c.tag==q('rPr') for c in p)]
assert not stray, stray[:3]
out = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
open('F_unzip/word/document.xml.new','wb').write(out)
print('MASTER DONE bytes:', len(out))
for l in log: print(' -', l)
