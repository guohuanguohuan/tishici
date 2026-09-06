# -*- coding: utf-8 -*-
"""⑥轮诊断探针：§六遗留4项定性——漏挂段/非加粗run/SM段级误挂 逐类取样（只读）。"""
import importlib.util, zipfile, re, os, sys, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, '..', '..', '..', '工具', '六类底纹计数.py'))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
q = lc.q

BASE = os.path.join(ROOT, '副本_④轮')
FILES = {
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'SM': '人教B版选必1·使用说明.docx',
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
}

def load(tag):
    path = os.path.join(BASE, FILES[tag])
    z = zipfile.ZipFile(path)
    doc = lc.etree.fromstring(z.read('word/document.xml'))
    styles_fill, styles_bold = lc.load_styles(z)
    sb = z.read('word/styles.xml')
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (lc.ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    anchor_ids = lc.anchor_style_set(sb)
    anchor_idx = {i for i, el in enumerate(els)
                  if el.tag == q('p') and lc.pstyle_of(el) in anchor_ids}
    heads = [h for h in lc.classify_headings(els, ptexts) if h[0] not in anchor_idx]
    return els, ptexts, styles_fill, styles_bold, heads, anchor_idx

def pat_group(texts):
    """把文本归模式：数字→N，汉字/其他保留首12字。"""
    pats = collections.Counter()
    samples = {}
    for t in texts:
        p = re.sub(r'\d+', 'N', t.strip())[:26]
        pats[p] += 1
        samples.setdefault(p, t.strip()[:40])
    return pats, samples

for tag in ['E', 'X1', 'X2']:
    els, ptexts, sf, sbold, heads, anchor_idx = load(tag)
    head_by_idx = {h[0]: h[1] for h in heads}
    t1_exp = {h[0] for h in heads if h[1] in ('chapter', 'section')}
    t2_exp = {h[0] for h in heads if h[1] in ('lecture', 'group')}
    t1_have, t2_have = set(), set()
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        f, _d = lc.para_shading(el, sf)
        if f == lc.FILL_TITLE1: t1_have.add(i)
        elif f == lc.FILL_TITLE2: t2_have.add(i)
    t1_miss = sorted(t1_exp - t1_have)
    t2_miss = sorted(t2_exp - t2_have)
    print(f'===== {tag}: heads 章{sum(1 for h in heads if h[1]=="chapter")} 节{sum(1 for h in heads if h[1]=="section")} 讲部{sum(1 for h in heads if h[1]=="lecture")} 题型{sum(1 for h in heads if h[1]=="group")}｜①漏挂{len(t1_miss)} ②漏挂{len(t2_miss)}')
    pats, samples = pat_group([ptexts[i] for i in t1_miss])
    print('  ①漏挂模式TOP:', pats.most_common(6))
    for p, c in pats.most_common(4):
        print('    样本:', repr(samples[p]))
    pats2, samples2 = pat_group([ptexts[i] for i in t2_miss])
    print('  ②漏挂模式TOP:', pats2.most_common(4))
    for p, c in pats2.most_common(3):
        print('    样本:', repr(samples2[p]))
    # 标题行非加粗 run 取样
    nb = []
    for i in sorted(head_by_idx):
        for r in els[i].iter(q('r')):
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t.strip() and not lc.eff_bold(r, sbold):
                nb.append((i, head_by_idx[i], t[:24]))
    print(f'  标题行非加粗run {len(nb)}，按段kind分布:', collections.Counter(k for _, k, _ in nb))
    for i, k, t in nb[:8]:
        print(f'    body[{i}] {k} run={t!r} 段文={ptexts[i][:36]!r}')

# SM 专项
els, ptexts, sf, sbold, heads, anchor_idx = load('SM')
print('===== SM: heads =', [(h[0], h[1], h[2][:30]) for h in heads])
for i, el in enumerate(els):
    if el.tag != q('p'):
        continue
    f, direct = lc.para_shading(el, sf)
    if f in (lc.FILL_TITLE1, lc.FILL_TITLE2, lc.FILL_CONTENT, lc.FILL_STEM):
        print(f'  段级底纹 body[{i}] fill={f} direct={direct} 文={ptexts[i][:50]!r}')
