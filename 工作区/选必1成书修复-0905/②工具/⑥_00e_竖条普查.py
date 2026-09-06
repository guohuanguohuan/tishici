# -*- coding: utf-8 -*-
"""⑥轮诊断探针5：正文段竖条归属普查（底纹减法'左粗竖条'是否在正文段批量误挂）。"""
import importlib.util, zipfile, re, os, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, '..', '..', '..', '工具', '六类底纹计数.py'))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
q = lc.q
BASE = os.path.join(ROOT, '副本_④轮')
F_B = '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
F_E = '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'
F_X1 = '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'
F_I1 = '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'

def load(fn):
    z = zipfile.ZipFile(os.path.join(BASE, fn))
    doc = lc.etree.fromstring(z.read('word/document.xml'))
    sf, sbold = lc.load_styles(z)
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (lc.ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    return els, ptexts, sf, sbold

def left_bar_el(el):
    ppr = el.find(q('pPr'))
    if ppr is None: return None
    pbdr = ppr.find(q('pBdr'))
    if pbdr is None: return None
    return pbdr.find(q('left'))

HEAD_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]+\S')   # 数码起段（节/题型标题形）
ENTRY_RE = re.compile(r'^\d+(?:\.\d+)+-\d+．')

for tag, fn in [('B', F_B), ('E', F_E), ('X1', F_X1), ('I1', F_I1)]:
    els, ptexts, sf, sbold = load(fn)
    buck = collections.Counter(); bar_attrs = collections.Counter(); samples = {}
    for i, el in enumerate(els):
        if el.tag != q('p'): continue
        lb = left_bar_el(el)
        if lb is None: continue
        t = ptexts[i].strip()
        bold = any(lc.eff_bold(r, sbold) for r in el.iter(q('r'))
                   if ''.join(x.text or '' for x in r.findall(q('t'))).strip())
        if HEAD_RE.match(t) and bold: k = '数码标题形(加粗)'
        elif HEAD_RE.match(t): k = '数码起段(非加粗)'
        elif ENTRY_RE.match(t): k = '条目号起段'
        elif not t: k = '空段'
        else: k = '正文段'
        buck[k] += 1
        bar_attrs[(lb.get(q('val')), lb.get(q('sz')), lb.get(q('color')), lb.get(q('space')))] += 1
        samples.setdefault(k, []).append((i, t[:34]))
    print(f'===== {tag}: 竖条段合计 {sum(buck.values())} → {dict(buck)}')
    print('  竖条属性分布:', bar_attrs.most_common(3))
    for k, ss in samples.items():
        print(f'  {k} 样本:', ss[:4])
