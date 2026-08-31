# -*- coding: utf-8 -*-
"""I2独占段oMathPara定位核验（只读）。"""
import os, zipfile
from lxml import etree
NSW = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (NSW, t)

base = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
fn = '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
z = zipfile.ZipFile(os.path.join(base, fn))
doc = etree.fromstring(z.read('word/document.xml'))
paras = list(doc.iter(q('p')))

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

for i, p in enumerate(paras):
    omps = p.findall('.//{%s}oMathPara' % M)
    if not omps: continue
    txt = ''
    for child in p:
        if child.tag == q('pPr'): continue
        if child.tag in ('{%s}oMathPara' % M, '{%s}oMath' % M): continue
        txt += ''.join(t.text or '' for t in child.iter(q('t')))
    if txt.strip(): continue
    # 独占段：打印上下文
    prev = ptext(paras[i-1])[:60] if i > 0 else ''
    nxt = ptext(paras[i+1])[:60] if i+1 < len(paras) else ''
    # 是否在表格内
    anc = p.getparent()
    in_tbl = False
    while anc is not None:
        if anc.tag == q('tc'): in_tbl = True; break
        anc = anc.getparent()
    lin = ''
    ppr = p.find(q('pPr'))
    sp = ppr.find(q('spacing')) if ppr is not None else None
    if sp is not None: lin = sp.get(q('line'))
    mtxt = ' ‖ '.join(''.join(t.text or '' for t in o.iter('{%s}t' % M)) for o in omps)[:120]
    print('段#%d 表内=%s line=%s | 前段: %r | 本段公式: %s | 后段: %r' % (i, in_tbl, lin, prev, mtxt, nxt))
