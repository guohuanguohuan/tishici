# -*- coding: utf-8 -*-
"""R1审计——按签名定位B/C弱命中段（OMML结构级dump v2）。"""
import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
def mq(t): return '{%s}%s'%(M,t)

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
        return '(' + ''.join(mlin(e) for e in el.findall(mq('e'))) + ')'
    if t == 'eqArr':
        return ' EQARR[' + ' ;; '.join(mlin(e) for e in el.findall(mq('e'))) + '] '
    if t == 'func':
        fn = el.find(mq('fName')); e = el.find(mq('e'))
        return '%s%s' % (mlin(fn) or '', mlin(e) or '')
    parts = []
    for c in el:
        if etree.QName(c).localname == 'rPr': continue
        parts.append(mlin(c))
    return ''.join(parts)

def para_lin(p):
    out = []
    def walk(el):
        for c in el:
            t = etree.QName(c).localname; ns = etree.QName(c).namespace
            if t == 't' and ns == W: out.append(c.text or '')
            elif t == 'oMath': out.append('⟦' + mlin(c) + '⟧')
            else: walk(c)
    walk(p)
    return ''.join(out)

# (code, 题号, 签名子串, 类别, 备注)
HITS = [
 ('B','1.1.1-1','若a=b，则a=b或','③','选项行量词'),
 ('B','1.1.1-1','方向相反时是相反向量','③','详解A句'),
 ('B','1.1.1-1','若a,b为相反向量','③','表格B项'),
 ('B','1.1.1-6','平移向量','③','分析句'),
 ('B','1.1.2-1','故不能构成空间的一个基底','③','共面向量句'),
 ('B','1.1.3-8','x=-4y=2','④',None),
 ('B','1.1.3-10','）．⟦2,3⟧','②',None),
 ('B','1.2.1-2','x=1z=-2','④',None),
 ('B','1.2.2-1','）．⟦-1,2,1⟧','②',None),
 ('B','1.2.2-1','x+2y+3z=03x+2y+z=0','④',None),
 ('B','1.2.2-2','）．⟦P3,-3,4⟧','②',None),
 ('B','1.2.2-5','n⋅A1B=x+z=0n⋅A1D=y+12z=0','④',None),
 ('B','1.2.2-1','多面体截面：找截点','③','讲部两处'),
 ('B','1.2.2-7','）．⟦0,23⟧','②',None),
 ('B','1.2.3-1','PB⋅n=32x-32z=0','④',None),
 ('B','1.2.3-7','2x=0-x-2y+3z=0','④',None),
 ('B','1.2.4-3','VA-A1BC=13S△A1BC','④',None),
 ('B','1.2.4-3','m=ijk111020','④',None),
 ('B','1.2.4-3','n=ijk111200','④',None),
 ('B','1.2.4-3','m⋅BD=x+y+z=0m⋅BA=2y=0','④',None),
 ('B','1.2.4-3','n⋅BD=a+b+c=0n⋅BC=2a=0','④',None),
 ('B','1.2.4-4','n⋅AP=-x+3z=0n⋅BP=-3y+3z=0','④',None),
 ('B','1.2.4-5','n⋅AE=33x+y+32z=0n⋅AB=43x=0','④',None),
 ('B','1.2.4-5','m⋅AE=33a+b+32c=0m⋅AC=12b=0','④',None),
 ('B','1.2.4-7','2x-y-2z=0y=0','④',None),
 ('B','1.2.4-9','S△BDE=12×32a×12a=38a2','④',None),
 ('B','1.2.4-12','53x-6z=08y=0','④',None),
 ('C','1.2.5-2','n⋅AB=23x+2y=0','④',None),
 ('C','1.2.5-6','3a=2R=3','④',None),
 ('C','1.2.5-10','PA=PB=PC=2x=2','④',None),
 ('C','1.2.5-12','3-33a=23-33a=23-3','④',None),
 ('C','1.2.5-26','DH=23×32a=33a','④',None),
 ('C','1.2.5-26','r=64a=122','④',None),
 ('C','1.2.5-28','V=13×34a2×63a=212a3','④',None),
 ('C','1.2.5-34','V=13×34a2×63a=4×13','④',None),
 ('C','1.2.5-43','BH=23×32l=33l','④',None),
 ('C','1.2.5-47','SB-2l=2r=l-rSB','④',None),
 ('C','1.2.5-48','r=33R=33×32=32','④',None),
 ('C','1.2.5-48','2r=3AA1=3×22a=62a','④',None),
 ('C','1.2.5-50','VS-ABC=13Sr=13×24(1+2)r=16','④',None),
 ('C','1.2.5-52','x-y=0-y+2z=0','④',None),
 ('C','1.2.5-53','）．⟦16π9,3π⟧','②',None),
 ('C','1.2.5-55','）．⟦2π3,2π⟧','②',None),
 ('C','1.2.5-57','x-y=0-x+2z=0','④',None),
 ('C','1.2.5-72','r2=3102n=102','④',None),
 ('C','1.2.5-76','-x+y+z=01-ax+y-2z=0','④',None),
]
D = r'C:\提示词\高中数学\高中数学同步'
FN = {'B':'人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
      'C':'人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'}
out = open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a4b_BC弱命中dump.txt','w',encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out)
cache = {}
for code, qno, sig, cat, note in HITS:
    if code not in cache:
        z = zipfile.ZipFile(os.path.join(D, FN[code]))
        doc = etree.fromstring(z.read('word/document.xml'))
        cache[code] = list(doc.find(q('body')).iter(q('p')))
    found = False
    for i, p in enumerate(cache[code]):
        lin = para_lin(p)
        plain = lin.replace('⟦','').replace('⟧','')
        if sig in lin or sig in plain:
            P('## %s %s [%s] %s 签名=%r' % (code, qno, cat, note or '', sig))
            P('   段=%s' % lin[:500])
            P('')
            found = True
            break
    if not found:
        P('## %s %s [%s] 签名=%r —— 未找到（签名形态不符）' % (code, qno, cat, sig))
        P('')
out.close()
print('DONE')
