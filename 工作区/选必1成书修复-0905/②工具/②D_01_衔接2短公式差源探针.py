# -*- coding: utf-8 -*-
"""②D_01_衔接2短公式差源探针.py — T9c 冒烟差 −2 差源定位。
对比 工具建设期留档（T9_dry 基线态 dd62e2…）与 ②-C 终态副本（c41a87…）的衔接2：
①两态各自按 T9 工具同口径清点（短/长/oMath段总数）；②oMath 段序列 diff 定位差异段。"""
import sys, io, os, re, zipfile, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
WJ = '⁠'

def eff_len(s):
    return sum(1.0 if ord(c) > 0x2E7F else 0.5 for c in s)

def omath_paras(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    out = []
    for p in body.iter(q('p')):
        if not list(p.iter(qm('oMath'))):
            continue
        t = ''.join(tt.text or '' for tt in p.iter(q('t')))
        out.append((round(eff_len(t), 1), len(list(p.iter(qm('oMath')))), t.replace(WJ, '')[:50]))
    return out

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本_工具建设期留档',
                 '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本',
                 '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')
la, lb = omath_paras(A), omath_paras(B)
for tag, L in (('建设期(T9_dry基线)', la), ('②C终态(现副本)', lb)):
    short = sum(1 for e, _, _ in L if e <= 60)
    lng = sum(1 for e, _, _ in L if e > 60)
    print('%s: oMath段 %d｜短(≤60) %d｜长(>60) %d' % (tag, len(L), short, lng))
print()
sm = difflib.SequenceMatcher(a=[x[2] for x in la], b=[x[2] for x in lb], autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        continue
    print('== %s 建设期[%d:%d] → ②C终态[%d:%d]' % (tag, i1, i2, j1, j2))
    for e, n, t in la[i1:i2]:
        print('   基线 - eff=%s oMath=%d | %s' % (e, n, t))
    for e, n, t in lb[j1:j2]:
        print('   现态 + eff=%s oMath=%d | %s' % (e, n, t))
print()
print('全段数对比（不分是否含oMath）：')
def all_paras(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    return list(doc.find(q('body')).iter(q('p')))
pa, pb = all_paras(A), all_paras(B)
print('  建设期 body.p = %d｜②C终态 body.p = %d（差 %+d）' % (len(pa), len(pb), len(pb) - len(pa)))
