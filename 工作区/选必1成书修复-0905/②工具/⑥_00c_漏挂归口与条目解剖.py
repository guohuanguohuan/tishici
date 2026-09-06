# -*- coding: utf-8 -*-
"""⑥轮诊断探针3：①漏挂段三分归口（知识点行/题型竖条标题/其他）＋条目号段run解剖＋I1参照。"""
import importlib.util, zipfile, re, os, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, '..', '..', '..', '工具', '六类底纹计数.py'))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
q = lc.q
BASE = os.path.join(ROOT, '副本_④轮')
FILES = {
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
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
    anchor_idx = {i for i, el in enumerate(els)
                  if el.tag == q('p') and lc.pstyle_of(el) in anchor_ids}
    heads = [h for h in lc.classify_headings(els, ptexts) if h[0] not in anchor_idx]
    return els, ptexts, sf, sbold, heads

def has_left_bar(el):
    ppr = el.find(q('pPr'))
    if ppr is None: return False
    pbdr = ppr.find(q('pBdr'))
    if pbdr is None: return False
    return pbdr.find(q('left')) is not None

def any_bold(el, sbold):
    return any(lc.eff_bold(r, sbold) for r in el.iter(q('r'))
               if ''.join(x.text or '' for x in r.findall(q('t'))).strip())

CHIP_LEAD = re.compile(r'^【\u2060?[一-鿿]+')
for tag in ['B', 'C', 'E', 'F', 'G', 'H', 'X1', 'X2']:
    els, ptexts, sf, sbold, heads = load(tag)
    t1_have = set()
    for i, el in enumerate(els):
        if el.tag != q('p'): continue
        f, _ = lc.para_shading(el, sf)
        if f == lc.FILL_TITLE1: t1_have.add(i)
    t1_exp = {h[0] for h in heads if h[1] in ('chapter', 'section')}
    miss = sorted(t1_exp - t1_have)
    # 前驱非空段
    def prev_text(i):
        j = i - 1
        while j >= 0:
            if els[j].tag == q('p') and ptexts[j].strip():
                return ptexts[j]
            if els[j].tag == q('tbl'):
                return '<tbl>'
            j -= 1
        return ''
    buck = collections.Counter()
    others = []
    for i in miss:
        t, pt = ptexts[i].strip(), prev_text(i)
        pt_norm = pt.replace('⁠', '')
        if pt_norm.startswith('【知识点】'):
            buck['知识点内容行'] += 1
        elif has_left_bar(els[i]) or (any_bold(els[i], sbold) and re.match(r'^\d+题[：:]', '')):
            buck['竖条/加粗标题'] += 1
        elif any_bold(els[i], sbold):
            buck['加粗无竖条'] += 1
            others.append(i)
        else:
            buck['其他非加粗'] += 1
            others.append(i)
    print(f'{tag}: ①漏挂 {len(miss)} → {dict(buck)}')
    for i in others[:6]:
        print(f'   其他 body[{i}] 前文={prev_text(i)[:24]!r} 文={ptexts[i][:40]!r}')

# —— 条目号段 run 解剖：X1 加粗/非加粗各2段 + I1 参照1段 ——
ENTRY = re.compile(r'^\d+(?:\.\d+)+-\d+．')
def anatomy_entry(tag, want_bold, n=2):
    els, ptexts, sf, sbold, heads = load(tag)
    got = 0
    for i, el in enumerate(els):
        if el.tag != q('p') or not ENTRY.match(ptexts[i].strip()): continue
        # 段首C7连续run
        lead = []
        for r in el.iter(q('r')):
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '': continue
            rpr = r.find(q('rPr'))
            if lc.shd_fill(rpr) == lc.FILL_CONTENT: lead.append((r, t))
            else: break
        lead_txt = ''.join(t for _, t in lead)
        if not lead: continue
        isb = any(lc.eff_bold(r, sbold) for r, _ in lead)
        if isb != want_bold: continue
        print(f'  {tag} body[{i}] lead={lead_txt!r} lead加粗={isb}')
        for r in el.iter(q('r')):
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if not t: continue
            rpr = r.find(q('rPr'))
            print(f'      run {"B" if lc.eff_bold(r, sbold) else "-"} shd={lc.shd_fill(rpr)} {t[:30]!r}')
        got += 1
        if got >= n: break

print('—— 条目号段解剖 ——')
anatomy_entry('X1', True)
anatomy_entry('X1', False)
anatomy_entry('X2', True, 1)
anatomy_entry('I1', False, 2)
