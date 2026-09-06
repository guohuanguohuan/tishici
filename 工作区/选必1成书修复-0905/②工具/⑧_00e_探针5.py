# -*- coding: utf-8 -*-
"""⑧轮债1探针5：与计数器 :727-763 覆盖循环逐腿同构的模拟（仅把 :736 门做 WJ 归一），测 cov 足额性。"""
import sys, re, zipfile
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
WJ = '\u2060'
CHIP_RE = re.compile(r'【[^】]{1,16}】')
NUMDOT_RE = re.compile(r'^\d+．$')
FILL_CONTENT = 'C7C7C7'
DEEP_BLUE = '1F4E79'
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None
def deep_blue(rpr):
    if rpr is None: return False
    c = rpr.find(q('color'))
    return c is not None and c.get(q('val')) == DEEP_BLUE

for code, path in [('X1', r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
                   ('X2', r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
                   ('SM', r'C:/提示词/高中数学/高中数学同步/人教B版选必1·使用说明.docx')]:
    st = structure(path)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    items = st['items']
    cov = 0; nocov = []
    for qu in st['questions']:
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        hit = False
        for ci in range(s_el, e_el):
            p = els[ci]
            if tag(p) != 'p': continue
            t = ptexts[ci]
            if not t.replace(WJ, '').startswith('【答案】'):   # 唯一改笔＝门 WJ 归一
                continue
            for r in p.iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                if txt and not CHIP_RE.fullmatch(txt) and \
                        (shd_fill(r.find(q('rPr'))) == FILL_CONTENT or deep_blue(r.find(q('rPr')))):
                    hit = True; break
            if not hit:
                for el in p.iter():
                    if etree.QName(el).namespace == M and tag(el) in ('r', 'ctrlPr') and \
                            (shd_fill(el.find(q('rPr'))) == FILL_CONTENT or deep_blue(el.find(q('rPr')))):
                        hit = True; break
            if not hit and '【知识点】' not in t.replace(WJ, ''):
                cj = ci + 1
                while cj < e_el and tag(els[cj]) == 'p' and not ptexts[cj].strip():
                    cj += 1
                if cj < e_el and tag(els[cj]) == 'p':
                    for r in els[cj].iter(q('r')):
                        txt = ''.join(x.text or '' for x in r.findall(q('t')))
                        if txt and not CHIP_RE.fullmatch(txt) and not NUMDOT_RE.match(txt) \
                                and (shd_fill(r.find(q('rPr'))) == FILL_CONTENT
                                     or deep_blue(r.find(q('rPr')))):
                            hit = True; break
            break
        if hit: cov += 1
        else: nocov.append(qu['no'])
    print('%s: 题块 %d｜门归一后模拟覆盖 %d/%d%s' % (code, len(st['questions']), cov, len(st['questions']),
          ('' if not nocov else '｜未覆盖样本 %s' % nocov[:6])))
