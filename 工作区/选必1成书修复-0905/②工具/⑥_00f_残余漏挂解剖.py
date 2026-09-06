# -*- coding: utf-8 -*-
"""⑥轮诊断探针6：残余漏挂/非加粗段解剖（B/C/E/G）＋⑦清点跃升归因（WJ致ANA边界失效验证）。"""
import importlib.util, zipfile, re, os
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, '..', '..', '..', '工具', '六类底纹计数.py'))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
q = lc.q
BASE = os.path.join(ROOT, '副本_④轮')
FILES = {
    'B': ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', [816, 841, 1056]),
    'C': ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', [147, 285, 318, 347, 375, 477]),
    'E': ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', [271]),
    'G': ('人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', [798, 1127]),
}
for tag, (fn, idxs) in FILES.items():
    z = zipfile.ZipFile(os.path.join(BASE, fn))
    doc = lc.etree.fromstring(z.read('word/document.xml'))
    sf, sbold = lc.load_styles(z)
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (lc.ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    print(f'===== {tag}')
    for i in idxs:
        for j in range(max(0, i-1), min(len(els), i+2)):
            el = els[j]
            if el.tag != q('p'):
                print(f'  body[{j}] <{lc.tag(el)}>'); continue
            f, _ = lc.para_shading(el, sf)
            ppr = el.find(q('pPr'))
            pbdr = ppr.find(q('pBdr')) if ppr is not None else None
            bar = None
            if pbdr is not None and pbdr.find(q('left')) is not None:
                bar = pbdr.find(q('left')).get(q('sz'))
            runs = []
            for r in el.iter(q('r')):
                t = ''.join(x.text or '' for x in r.findall(q('t')))
                if not t: continue
                rpr = r.find(q('rPr'))
                sz = col = None
                if rpr is not None:
                    se = rpr.find(q('sz')); sz = se.get(q('val')) if se is not None else None
                    ce = rpr.find(q('color')); col = ce.get(q('val')) if ce is not None else None
                runs.append(f'{"B" if lc.eff_bold(r, sbold) else "-"}{"s"+sz if sz else ""}{"c"+col if col else ""}:{t[:16]!r}')
            mark = '◀◀' if j == i else '   '
            print(f'  {mark} body[{j}] shd={f} barL={bar} | ' + ' '.join(runs[:5]) + f' | 文={ptexts[j][:40]!r}')
# WJ 验证：B 的【答案】行是否带 ⁠ 致 ANA 边界失效
z = zipfile.ZipFile(os.path.join(BASE, FILES['B'][0]))
doc = lc.etree.fromstring(z.read('word/document.xml')); z.close()
els = list(doc.find(q('body')))
n_wj = n_plain = 0
for el in els:
    if el.tag != q('p'): continue
    t = lc.ptext(el)
    if t.startswith('【⁠答⁠案⁠】'): n_wj += 1
    elif t.startswith('【答案】'): n_plain += 1
print(f'===== B 答案行形态：WJ-laden {n_wj}｜纯净 {n_plain}（WJ 存在即 ANA_LABELS 边界失效——⑦清点口径需归一化）')
