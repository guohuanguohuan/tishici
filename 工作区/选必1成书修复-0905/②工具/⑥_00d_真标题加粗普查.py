# -*- coding: utf-8 -*-
"""⑥轮诊断探针4：真标题段（①底纹段＋竖条段）内非加粗run普查＋X1节区结构解剖。"""
import importlib.util, zipfile, re, os, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, '..', '..', '..', '工具', '六类底纹计数.py'))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
q = lc.q
BASE = os.path.join(ROOT, '副本_④轮')
FILES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
}

def load(tag):
    z = zipfile.ZipFile(os.path.join(BASE, FILES[tag]))
    doc = lc.etree.fromstring(z.read('word/document.xml'))
    sf, sbold = lc.load_styles(z)
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (lc.ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    return els, ptexts, sf, sbold

def has_left_bar(el):
    ppr = el.find(q('pPr'))
    if ppr is None: return False
    pbdr = ppr.find(q('pBdr'))
    return pbdr is not None and pbdr.find(q('left')) is not None

print('—— 真标题段（①/②底纹段＋竖条段）内非空非加粗run普查 ——')
for tag in FILES:
    els, ptexts, sf, sbold = load(tag)
    bad = []
    n_title = 0
    for i, el in enumerate(els):
        if el.tag != q('p'): continue
        f, _ = lc.para_shading(el, sf)
        is_title = f in (lc.FILL_TITLE1, lc.FILL_TITLE2) or has_left_bar(el)
        if not is_title: continue
        n_title += 1
        for r in el.iter(q('r')):
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t.strip() and not lc.eff_bold(r, sbold):
                bad.append((i, f, has_left_bar(el), t[:20], ptexts[i][:36]))
    print(f'{tag}: 真标题段 {n_title}，其内非加粗run {len(bad)}')
    for row in bad[:6]:
        print('   ', row)

print()
print('—— X1 节区结构解剖（body[0..8]、①底纹段、竖条段及后继） ——')
els, ptexts, sf, sbold = load('X1')
for i, el in enumerate(els[:9]):
    if el.tag != q('p'):
        print(f'  body[{i}] <{lc.tag(el)}>'); continue
    f, _ = lc.para_shading(el, sf)
    b = any(lc.eff_bold(r, sbold) for r in el.iter(q('r')))
    szs = {r.find(q('rPr')).find(q('sz')).get(q('val')) for r in el.iter(q('r'))
           if r.find(q('rPr')) is not None and r.find(q('rPr')).find(q('sz')) is not None}
    print(f'  body[{i}] shd={f} 竖条={has_left_bar(el)} 加粗={b} sz={szs} 文={ptexts[i][:40]!r}')
for i, el in enumerate(els):
    if el.tag != q('p'): continue
    f, _ = lc.para_shading(el, sf)
    if f == lc.FILL_TITLE1 or (has_left_bar(el) and '本节' not in ptexts[i]):
        # ①底纹段 或 竖条段：打印自身与下一非空段
        nxt = ''
        for j in range(i+1, min(i+4, len(els))):
            if els[j].tag == q('p') and ptexts[j].strip():
                nxt = ptexts[j][:30]; break
        b = all(lc.eff_bold(r, sbold) for r in el.iter(q('r'))
                if ''.join(x.text or '' for x in r.findall(q('t'))).strip())
        print(f'  标题候选 body[{i}] shd={f} 竖条={has_left_bar(el)} 全加粗={b} 文={ptexts[i][:38]!r} 后继={nxt!r}')
