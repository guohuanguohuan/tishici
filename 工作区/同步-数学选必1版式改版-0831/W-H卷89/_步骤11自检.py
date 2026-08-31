# -*- coding: utf-8 -*-
"""步骤11 排版自检①~⑧扫描（W-H卷89）"""
import zipfile, re, json
from collections import defaultdict
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WPNS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

with zipfile.ZipFile('H工作副本.docx') as z:
    doc = etree.fromstring(z.read('word/document.xml'))
    styles = etree.fromstring(z.read('word/styles.xml'))
    settings = etree.fromstring(z.read('word/settings.xml'))
    footer_files = [n for n in z.namelist() if 'footer' in n and n.endswith('.xml')]
    footers = {n: etree.fromstring(z.read(n)) for n in footer_files}
body = doc.find(w('body'))
els = list(body)

def ptext(p):
    return ''.join(s.text or '' for s in p.iter() if isinstance(s.tag, str) and s.tag in (w('t'), m('t')))
def has_obj(p):
    return any(isinstance(s.tag, str) and s.tag in (w('drawing'), w('pict')) for s in p.iter())

out = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    out.append(s)
    print(s)

# ③ 纯空段
empty = []
for i, el in enumerate(els):
    if isinstance(el.tag, str) and el.tag == w('p'):
        if not ptext(el).strip() and not has_obj(el) and not any(isinstance(s.tag, str) and s.tag == m('oMath') for s in el.iter()):
            empty.append(i)
P('③ 纯空段数:', len(empty), '位置(前12):', empty[:12])

# ④ 原卷栏目残留
bad_titles = []
for i, el in enumerate(els):
    if isinstance(el.tag, str) and el.tag == w('p'):
        t = ptext(el).strip()
        if re.match(r'^(【典例|【举一反三|专题[一二三四五六七八九十N0-9]|考点[0-9一二三四五六七八九十]|题型[0-9一二三四五六七八九十]+[、.]|A组|B组|第\d+讲)', t):
            bad_titles.append((i, t[:40]))
P('④ 原卷栏目名残留:', len(bad_titles), bad_titles[:5])

# ⑥ 六个残留计数
ins = sum(1 for _ in body.iter(w('ins'))) + sum(1 for _ in body.iter(w('del')))
color_runs = 0; strike_runs = 0; hl_runs = 0
for r in body.iter(w('r')):
    rPr = r.find(w('rPr'))
    if rPr is None: continue
    c = rPr.find(w('color'))
    if c is not None and c.get(w('val')) not in ('auto', '000000', '1F4E79'): color_runs += 1
    if rPr.find(w('strike')) is not None or rPr.find(w('dstrike')) is not None: strike_runs += 1
    if rPr.find(w('highlight')) is not None: hl_runs += 1
pbb = sum(1 for _ in body.iter(w('pageBreakBefore')))
kn = sum(1 for _ in body.iter(w('keepNext')))
kl = sum(1 for _ in body.iter(w('keepLines')))
br_page = sum(1 for b in body.iter(w('br')) if b.get(w('type')) == 'page')
br_all = sum(1 for _ in body.iter(w('br')))
P('⑥ w:ins+w:del=%d 彩色run=%d 删除线=%d 突出显示=%d pageBreakBefore=%d keepNext=%d keepLines=%d w:br(page)=%d w:br(全)=%d'
  % (ins, color_runs, strike_runs, hl_runs, pbb, kn, kl, br_page, br_all))

# ⑥ 图与公式
omp = sum(1 for _ in body.iter(m('oMathPara')))
anchor = sum(1 for _ in doc.iter('{%s}anchor' % WPNS))
blk = 0
for el in els:
    if isinstance(el.tag, str) and el.tag == w('p'):
        kids = [c for c in el if isinstance(c.tag, str) and c.tag != w('pPr')]
        if len(kids) == 1 and kids[0].tag == m('oMathPara'): blk += 1
P('⑥ oMathPara=%d anchor=%d 块级独立公式段=%d' % (omp, anchor, blk))

# 表格勘察
tbls = [el for el in els if isinstance(el.tag, str) and el.tag == w('tbl')]
P('表格数:', len(tbls))
for tb in tbls:
    rows = tb.findall(w('tr'))
    first = ''.join(s.text or '' for s in rows[0].iter() if isinstance(s.tag, str) and s.tag == w('t'))[:60] if rows else ''
    ncols = len(rows[0].findall(w('tc'))) if rows else 0
    P('  行数%d 列数%d 首行: %s' % (len(rows), ncols, first))

# ⑦ 题号序列
qseq = []
for i, el in enumerate(els):
    if isinstance(el.tag, str) and el.tag == w('p'):
        mm = re.match(r'^(\d{1,3})．', ptext(el))
        if mm: qseq.append(int(mm.group(1)))
gaps = [(qseq[k-1], qseq[k]) for k in range(1, len(qseq)) if qseq[k] != qseq[k-1] + 1]
P('⑦ 题号序列: 首=%d 末=%d 计数=%d 断点=%s' % (qseq[0], qseq[-1], len(qseq), gaps[:3]))

lect = []; typ = []
for i, el in enumerate(els):
    if isinstance(el.tag, str) and el.tag == w('p'):
        t = ptext(el).strip()
        mm = re.match(r'^(2\.8(?:\.\d+)+)\s', t)
        if mm:
            if '方法讲解' in t: lect.append(mm.group(1))
            else: typ.append(mm.group(1))
P('⑦ 讲部数=%d 题型数=%d' % (len(lect), len(typ)))
chain = defaultdict(list)
for t in typ:
    parts = t.split('.')
    parent = '.'.join(parts[:-1]); chain[parent].append(int(parts[-1]))
bad_chain = {}
for p_, v in chain.items():
    sv = sorted(v)
    if sv != list(range(sv[0], sv[0] + len(sv))):
        bad_chain[p_] = (sv,)
P('⑦ 题型链断点父:', dict(list(bad_chain.items())[:8]))

# ⑧ run字号/行距
szcnt = defaultdict(int); spcnt = defaultdict(int)
norf = 0; nosp = 0
for r in body.iter(w('r')):
    rPr = r.find(w('rPr'))
    if rPr is None or rPr.find(w('sz')) is None: norf += 1
    else: szcnt[rPr.find(w('sz')).get(w('val'))] += 1
for p in body.iter(w('p')):
    pPr = p.find(w('pPr'))
    sp = pPr.find(w('spacing')) if pPr is not None else None
    if sp is None: nosp += 1
    else: spcnt[(sp.get(w('line')), sp.get(w('lineRule')))] += 1
P('⑧ run字号分布:', dict(sorted(szcnt.items(), key=lambda x: -int(x[1]))), '| 无sz run:', norf)
P('⑧ 行距分布:', dict(spcnt), '| 无spacing段:', nosp)

dd = styles.find(w('docDefaults'))
rprd = dd.find(w('rPrDefault')); pprd = dd.find(w('pPrDefault'))
if rprd is not None:
    rpr = rprd.find(w('rPr'))
    fonts = rpr.find(w('rFonts'))
    szel = rpr.find(w('sz'))
    P('⑧ docDefaults rPrDefault: eastAsia=%s ascii=%s sz=%s'
      % (fonts.get(w('eastAsia')), fonts.get(w('ascii')), szel.get(w('val')) if szel is not None else None))
if pprd is not None:
    ppr = pprd.find(w('pPr'))
    sp = ppr.find(w('spacing')) if ppr is not None else None
    P('⑧ docDefaults pPrDefault spacing:', dict(sp.attrib) if sp is not None else None)

sect = body.find(w('sectPr'))
dg = sect.find(w('docGrid'))
P('⑧ docGrid:', dict(dg.attrib) if dg is not None else None)
pgsz = sect.find(w('pgSz')); pgmar = sect.find(w('pgMar'))
P('⑤ pgSz:', dict(pgsz.attrib) if pgsz is not None else None)
P('⑤ pgMar:', {k.split('}')[1]: v for k, v in pgmar.attrib.items()} if pgmar is not None else None)
P('⑤ settings updateFields:', settings.find(w('updateFields')) is not None)
P('⑤ footer部件:', footer_files)
for n, f in footers.items():
    txt = ''.join(t.text or '' for t in f.iter(w('t')))
    instr = ''.join(t.text or '' for t in f.iter(w('instrText')))
    fld = sum(1 for _ in f.iter(w('fldChar')))
    simple = sum(1 for _ in f.iter(w('fldSimple')))
    jc = [j.get(w('val')) for j in f.iter(w('jc'))]
    szs = set(s.get(w('val')) for s in f.iter(w('sz')))
    P('  %s: 文本=%r 域指令=%r fldChar=%d fldSimple=%d jc=%s sz=%s' % (n, txt[:60], instr[:40], fld, simple, jc, szs))
# 页眉
hdr_files = [n for n in zipfile.ZipFile('H工作副本.docx').namelist() if 'header' in n and n.endswith('.xml')]
P('⑤ header部件:', hdr_files)
with zipfile.ZipFile('H工作副本.docx') as z:
    for n in hdr_files:
        f = etree.fromstring(z.read(n))
        txt = ''.join(t.text or '' for t in f.iter(w('t')))
        instr = ''.join(t.text or '' for t in f.iter(w('instrText')))
        jc = [j.get(w('val')) for j in f.iter(w('jc'))]
        szs = set(s.get(w('val')) for s in f.iter(w('sz')))
        P('  %s: 文本=%r 域指令=%r jc=%s sz=%s' % (n, txt[:60], instr[:40], jc, szs))

n_pbdr = 0
for p in body.iter(w('p')):
    pPr = p.find(w('pPr'))
    if pPr is not None and pPr.find(w('pBdr')) is not None:
        n_pbdr += 1
P('pBdr段数(定理框N23+章底边框):', n_pbdr)

blue = 0
for r in body.iter(w('r')):
    rPr = r.find(w('rPr'))
    if rPr is not None:
        c = rPr.find(w('color'))
        if c is not None and c.get(w('val')) == '1F4E79': blue += 1
blue_om = 0
for holder in list(body.iter(m('r'))) + list(body.iter(m('ctrlPr'))):
    rPr = holder.find(w('rPr'))
    if rPr is not None:
        c = rPr.find(w('color'))
        if c is not None and c.get(w('val')) == '1F4E79': blue_om += 1
P('⑧ 深蓝#1F4E79 文字run=%d OMML挂点=%d' % (blue, blue_om))

# ① 目录块检查：连续标题堆积（无题间隔）
TITLE = re.compile(r'^2\.8(\.\d+)*\s')
run_titles = 0; max_run = 0
for i, el in enumerate(els):
    if isinstance(el.tag, str) and el.tag == w('p'):
        t = ptext(el).strip()
        if TITLE.match(t) or t.startswith('人教B版选必1'):
            run_titles += 1; max_run = max(max_run, run_titles)
        elif t:
            run_titles = 0
P('① 最长连续标题串:', max_run, '（≥3即目录块嫌疑）')

with open('自检实测.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('-> 自检实测.txt')
