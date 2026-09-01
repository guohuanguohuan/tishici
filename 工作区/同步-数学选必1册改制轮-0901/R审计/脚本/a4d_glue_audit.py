# -*- coding: utf-8 -*-
"""R1审计——B/C全量单块多式结构级核验：列出每个「朴素线性化含≥2等号且出现粘连边界」的oMath块，
标注其OMML结构（是否EQARR/分数/矩阵），供人工定性（§5单块多式连排禁令）。"""
import sys, os, zipfile, re
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
def mq(t): return '{%s}%s'%(M,t)

def plain_omath(om):
    return ''.join(t.text or '' for t in om.iter(mq('t')))

def struct_kind(om):
    """返回块内结构特征标签集合。"""
    kinds = set()
    for el in om.iter():
        t = etree.QName(el).localname
        if t == 'eqArr': kinds.add('EQARR')
        if t == 'f': kinds.add('FRAC')
        if t == 'm': kinds.add('MATRIX')
        if t == 'rad': kinds.add('RAD')
        if t == 'd': kinds.add('DELIM')
    return kinds

GLUE_RE = re.compile(r'[0-9a-zA-Z\)⟧]\s*[a-zA-Z\(][0-9a-zA-Z+\-]*=')  # 尾元粘连下一方程首元（含=）

def glue_segments(pl):
    """切出无分隔片段内的等号数与粘连点。分隔符=，;；、,（）()与文字。"""
    segs = re.split(r'[,;；,]', pl)
    hits = []
    for seg in segs:
        if seg.count('=') >= 2:
            # 粘连边界：值后直接跟字母/括号且随后有=
            for m in GLUE_RE.finditer(seg):
                hits.append((seg[max(0,m.start()-6):m.end()+6], seg.count('=')))
    return hits

D = r'C:\提示词\高中数学\高中数学同步'
FN = {'B':'人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
      'C':'人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'}
out = open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a4d_BC全量粘连核验.txt','w',encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out)
for code, fn in FN.items():
    z = zipfile.ZipFile(os.path.join(D, fn))
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    paras = list(body.iter(q('p')))
    P('######### %s' % code)
    n = 0
    for i, p in enumerate(paras):
        for om in p.iter(mq('oMath')):
            pl = plain_omath(om)
            hits = glue_segments(pl)
            if hits:
                kinds = struct_kind(om)
                n += 1
                P('[%s p#%d] %s 块=%r' % (code, i+1, '+'.join(sorted(kinds)) or 'PLAIN', pl[:160]))
                P('        粘连点: %s' % [h[0] for h in hits[:6]])
    P('## %s 合计含粘连签名块=%d' % (code, n))
    P('')
out.close()
print('DONE')
