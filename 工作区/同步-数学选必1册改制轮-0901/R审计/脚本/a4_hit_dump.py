# -*- coding: utf-8 -*-
"""R1审计——B/C弱命中段OMML结构级dump（人工核验素材）。
对每个命中段：输出段落全文（公式以⟦…⟧线性化）＋命中块的OMML结构树（分数/根号/上下标标注）。"""
import sys, os, re, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
def mq(t): return '{%s}%s'%(M,t)

def mlin(el):
    """OMML结构化线性化：分数 f(num)/f(den)、根号 rad(...)、上标^{}、下标_{}。"""
    t = etree.QName(el).localname
    if t == 't':
        return el.text or ''
    if t == 'f':
        num = el.find(mq('num')); den = el.find(mq('den'))
        return 'f(%s)/f(%s)' % (mlin(num) if num is not None else '', mlin(den) if den is not None else '')
    if t == 'rad':
        deg = el.find(mq('deg')); e = el.find(mq('e'))
        return 'rad(%s|%s)' % (mlin(deg) if deg is not None else '', mlin(e) if e is not None else '')
    if t == 'sSup':
        e = el.find(mq('e')); sup = el.find(mq('sup'))
        return '%s^{%s}' % (mlin(e) if e is not None else '', mlin(sup) if sup is not None else '')
    if t == 'sSub':
        e = el.find(mq('e')); sub = el.find(mq('sub'))
        return '%s_{%s}' % (mlin(e) if e is not None else '', mlin(sub) if sub is not None else '')
    if t == 'sSubSup':
        e = el.find(mq('e')); sub = el.find(mq('sub')); sup = el.find(mq('sup'))
        return '%s_{%s}^{%s}' % (mlin(e) if e is not None else '', mlin(sub) if sub is not None else '', mlin(sup) if sup is not None else '')
    if t == 'd':  # delimiter
        return '(' + ''.join(mlin(e) for e in el.findall(mq('e'))) + ')'
    if t == 'eqArr':
        return ' EQARR[' + ' ;; '.join(mlin(e) for e in el.findall(mq('e'))) + '] '
    if t == 'func':
        fn = el.find(mq('fName')); e = el.find(mq('e'))
        return '%s%s' % (mlin(fn) if fn is not None else '', mlin(e) if e is not None else '')
    parts = []
    for c in el:
        ct = etree.QName(c).localname
        if ct == 'rPr': continue
        parts.append(mlin(c))
    return ''.join(parts)

def para_lin(p):
    """段落线性化：文字＋⟦公式⟧交错流（公式用普通线性化）。"""
    out = []
    def walk(el):
        for c in el:
            t = etree.QName(c).localname
            ns = etree.QName(c).namespace
            if t == 't' and ns == W:
                out.append(c.text or '')
            elif t == 'oMath':
                out.append('⟦' + mlin(c) + '⟧')
            elif t == 'p' and ns == W:
                walk(c)
            elif t == 'oMathPara':
                walk(c)
            else:
                walk(c)
    walk(p)
    return ''.join(out)

HITS = {
 'B': [('1.1.1-1',59),('1.1.1-1',62),('1.1.1-1',63),('1.1.1-6',103),('1.1.2-1',146),
       ('1.1.3-8',254),('1.1.3-8',257),('1.1.3-10',278),('1.2.1-2',301),('1.2.2-1',368),
       ('1.2.2-1',371),('1.2.2-2',374),('1.2.2-5',417),('1.2.2-1',431),('1.2.2-7',472),
       ('1.2.3-1',515),('1.2.3-7',573),('1.2.4-3',709),('1.2.4-3',724),('1.2.4-3',725),
       ('1.2.4-3',730),('1.2.4-3',746),('1.2.4-3',747),('1.2.4-4',787),('1.2.4-5',837),
       ('1.2.4-5',839),('1.2.4-7',948),('1.2.4-9',982),('1.2.4-12',1062)],
 'C': [('1.2.5-2',19),('1.2.5-6',72),('1.2.5-10',115),('1.2.5-12',150),('1.2.5-26',293),
       ('1.2.5-26',294),('1.2.5-28',308),('1.2.5-34',375),('1.2.5-43',449),('1.2.5-47',482),
       ('1.2.5-48',495),('1.2.5-48',498),('1.2.5-50',516),('1.2.5-52',551),('1.2.5-53',558),
       ('1.2.5-55',591),('1.2.5-57',656),('1.2.5-72',886),('1.2.5-76',949)],
}
D = r'C:\提示词\高中数学\高中数学同步'
FN = {'B':'人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
      'C':'人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'}
out = open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a4_BC弱命中dump.txt','w',encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out)
for code, hits in HITS.items():
    z = zipfile.ZipFile(os.path.join(D, FN[code]))
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    # 段落列表＝body全子元素序（含表格内段落，iter顺序）
    paras = list(body.iter(q('p')))
    for qno, pn in hits:
        if pn-1 >= len(paras):
            P('## %s 题%s p#%d —— 段号越界' % (code, qno, pn)); continue
        p = paras[pn-1]
        P('## %s 题%s p#%d' % (code, qno, pn))
        P('  全段: %s' % para_lin(p)[:400])
        P('')
out.close()
print('DONE')
