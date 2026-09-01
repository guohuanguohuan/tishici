# -*- coding: utf-8 -*-
"""R1审计——B/C弱命中段dump v3：先按扫描器同款朴素线性化定位段，再给该段全部oMath的结构级视图。"""
import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
def mq(t): return '{%s}%s'%(M,t)

def plain_omath(om):
    return ''.join(t.text or '' for t in om.iter(mq('t')))

def mlin(el):
    t = etree.QName(el).localname
    if t == 't': return el.text or ''
    if t == 'f':
        num = el.find(mq('num')); den = el.find(mq('den'))
        return 'f(%s)/f(%s)' % (mlin(num) if num is not None else '', mlin(den) if den is not None else '')
    if t == 'rad':
        deg = el.find(mq('deg')); e = el.find(mq('e'))
        return 'rad(%s|%s)' % (mlin(deg) if deg is not None else '', mlin(e) if e is not None else '')
    if t == 'sSup':
        e = el.find(mq('e')); sup = el.find(mq('sup'))
        return '%s^{%s}' % (mlin(e) or '', mlin(sup) or '')
    if t == 'sSub':
        e = el.find(mq('e')); sub = el.find(mq('sub'))
        return '%s_{%s}' % (mlin(e) or '', mlin(sub) or '')
    if t == 'sSubSup':
        e = el.find(mq('e')); sub = el.find(mq('sub')); sup = el.find(mq('sup'))
        return '%s_{%s}^{%s}' % (mlin(e) or '', mlin(sub) or '', mlin(sup) or '')
    if t == 'd':
        seps = [mlin(s) for s in el.findall(mq('sepChr'))]
        inner = ' ;; '.join(mlin(e) for e in el.findall(mq('e')))
        return '(' + inner + ')'
    if t == 'eqArr':
        return ' EQARR[' + ' ;; '.join(mlin(e) for e in el.findall(mq('e'))) + '] '
    if t == 'func':
        fn = el.find(mq('fName')); e = el.find(mq('e'))
        return '%s%s' % (mlin(fn) or '', mlin(e) or '')
    if t == 'nary':  # 求和/积分
        sub = el.find(mq('sub')); sup = el.find(mq('sup')); e = el.find(mq('e'))
        return 'NARY(Σ_%s^%s %s)' % (mlin(sub) or '', mlin(sup) or '', mlin(e) or '')
    parts = []
    for c in el:
        if etree.QName(c).localname == 'rPr': continue
        parts.append(mlin(c))
    return ''.join(parts)

def para_dump(p):
    """段落朴素线性化（公式=⟦朴素⟧）"""
    out = []
    def walk(el):
        for c in el:
            t = etree.QName(c).localname; ns = etree.QName(c).namespace
            if t == 't' and ns == W: out.append(c.text or '')
            elif t == 'oMath': out.append('⟦' + plain_omath(c) + '⟧')
            else: walk(c)
    walk(p)
    return ''.join(out)

HITS = [
 ('B','x=-4y=2'),('B','x=1z=-2'),('B','x+2y+3z=03x+2y+z=0'),
 ('B','n⋅A1B=x+z=0n⋅A1D=y+12z=0'),('B','PB⋅n=32x-32z=0'),('B','2x=0-x-2y+3z=0'),
 ('B','VA-A1BC=13S△A1BC'),('B','m=ijk111020'),('B','n=ijk111200'),
 ('B','m⋅BD=x+y+z=0m⋅BA=2y=0'),('B','n⋅BD=a+b+c=0n⋅BC=2a=0'),
 ('B','n⋅AP=-x+3z=0n⋅BP=-3y+3z=0'),('B','n⋅AE=33x+y+32z=0n⋅AB=43x=0'),
 ('B','m⋅AE=33a+b+32c=0m⋅AC=12b=0'),('B','2x-y-2z=0y=0'),
 ('B','S△BDE=12×32a×12a=38a2'),('B','53x-6z=08y=0'),
 ('C','n⋅AB=23x+2y=0'),('C','3a=2R=3'),('C','PA=PB=PC=2x=2'),
 ('C','3-33a=23-33a=23-3'),('C','DH=23×32a=33a'),('C','r=64a=122'),
 ('C','V=13×34a2×63a=212a3'),('C','BH=23×32l=33l'),('C','SB-2l=2r=l-rSB'),
 ('C','r=33R=33×32=32'),('C','2r=3AA1=3×22a=62a'),
 ('C','VS-ABC=13Sr=13×24(1+2)r=16'),('C','x-y=0-y+2z=0'),
 ('C','r2=3102n=102'),('C','-x+y+z=01-ax+y-2z=0'),
]
D = r'C:\提示词\高中数学\高中数学同步'
FN = {'B':'人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
      'C':'人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'}
out = open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a4c_BC弱命中dump.txt','w',encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out)
cache = {}
for code, sig in HITS:
    if code not in cache:
        z = zipfile.ZipFile(os.path.join(D, FN[code]))
        doc = etree.fromstring(z.read('word/document.xml'))
        cache[code] = list(doc.find(q('body')).iter(q('p')))
    found = False
    for i, p in enumerate(cache[code]):
        lin = para_dump(p)
        if sig in lin.replace('⟦','').replace('⟧','') or sig in lin:
            P('===== %s p#%d 签名=%r' % (code, i+1, sig))
            P('  段(朴素): %s' % lin[:460])
            for om in p.iter(mq('oMath')):
                pl = plain_omath(om)
                if any(k in sig[:8] for k in [pl[:8]]) or sig[:6] in pl or pl[:6] in sig:
                    P('  命中块结构: %s' % mlin(om)[:600])
                else:
                    P('  他块(朴素): ⟦%s⟧' % pl[:120])
            P('')
            found = True
            break
    if not found:
        P('===== %s 签名=%r ——未定位' % (code, sig)); P('')
out.close()
print('DONE')
