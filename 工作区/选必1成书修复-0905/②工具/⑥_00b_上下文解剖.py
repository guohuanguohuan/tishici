# -*- coding: utf-8 -*-
"""⑥轮诊断探针2：重名节段上下文×格式解剖（判定锚段/标题/正文引用）＋SM body[0]。"""
import importlib.util, zipfile, re, os
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, '..', '..', '..', '工具', '六类底纹计数.py'))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
q = lc.q
BASE = os.path.join(ROOT, '副本_④轮')
FILES = {
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'SM': '人教B版选必1·使用说明.docx',
}

def load(tag):
    z = zipfile.ZipFile(os.path.join(BASE, FILES[tag]))
    doc = lc.etree.fromstring(z.read('word/document.xml'))
    sf, sbold = lc.load_styles(z)
    sb = z.read('word/styles.xml')
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (lc.ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    anchor_ids = lc.anchor_style_set(sb)
    return els, ptexts, sf, sbold, anchor_ids

def anatomy(els, ptexts, sf, sbold, anchor_ids, i):
    el = els[i]
    if el.tag != q('p'):
        return f'body[{i}] <{lc.tag(el)}>'
    f, direct = lc.para_shading(el, sf)
    ps = lc.pstyle_of(el)
    bits = []
    for r in el.iter(q('r')):
        t = ''.join(x.text or '' for x in r.findall(q('t')))
        if not t:
            continue
        rpr = r.find(q('rPr'))
        sz = col = None
        if rpr is not None:
            szel = rpr.find(q('sz'));  sz = szel.get(q('val')) if szel is not None else None
            cel = rpr.find(q('color')); col = cel.get(q('val')) if cel is not None else None
        bits.append(f'{"B" if lc.eff_bold(r, sbold) else "-"}{"s"+sz if sz else ""}{"c"+col if col else ""}:{t[:18]!r}')
    star = '★锚样式' if ps in anchor_ids else ''
    return f'body[{i}] pStyle={ps}{star} shd={f} | ' + ' '.join(bits[:6]) + f' | 文={ptexts[i][:34]!r}'

for tag, idxs in [('X1', [58, 59, 60, 61, 62, 88, 89, 90, 91, 92]),
                  ('E', [10, 11, 12, 13, 14, 18, 19, 20, 21, 22, 43, 44, 45, 46, 47]),
                  ('SM', [0, 1])]:
    els, ptexts, sf, sbold, anchor_ids = load(tag)
    print(f'===== {tag} (锚样式集={anchor_ids})')
    for i in idxs:
        print(' ', anatomy(els, ptexts, sf, sbold, anchor_ids, i))
