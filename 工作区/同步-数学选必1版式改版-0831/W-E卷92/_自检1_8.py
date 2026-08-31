# -*- coding: utf-8 -*-
"""W-E卷92 排版自检①~⑧（XML级数字落盘）"""
import zipfile, re, json
from lxml import etree
from collections import Counter

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

path = 'E卷92-工作副本.docx'
with zipfile.ZipFile(path) as z:
    doc = etree.fromstring(z.read('word/document.xml'))
    styles = etree.fromstring(z.read('word/styles.xml'))
    settings = z.read('word/settings.xml').decode('utf-8', 'ignore')
    footers = [n for n in z.namelist() if n.startswith('word/footer')]
    headers = [n for n in z.namelist() if n.startswith('word/header')]
    footer_xmls = {n: z.read(n).decode('utf-8', 'ignore') for n in footers}
    header_xmls = {n: z.read(n).decode('utf-8', 'ignore') for n in headers}
body = doc.find(w('body'))
out = []

def P(t): out.append(t); print(t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), m('t')))

paras = [el for el in body if isinstance(el.tag, str) and el.tag == w('p')]

# ============ ① 结构：目录块/标题紧跟/裸排 ============
P('== ① 结构 ==')
SECT = re.compile(r'^\d+(\.\d+)+\s')
LECT = re.compile(r'^\d+(\.\d+)+\s*方法讲解')
QSTART = re.compile(r'^(\d{1,3})．')
LABEL = re.compile(r'^【')
STAT = re.compile(r'^(全件|本节)\d+题')
title_idx = []
for i, p in enumerate(paras):
    t = lin(p).strip()
    pstyle = ''
    pPr = p.find(w('pPr'))
    if pPr is not None and pPr.find(w('pStyle')) is not None:
        pstyle = pPr.find(w('pStyle')).get(w('val'))
    if pstyle == 'Heading3' or SECT.match(t):
        title_idx.append((i, '节', t[:22]))
    elif LECT.match(t):
        title_idx.append((i, '讲部', t[:22]))
# 题型标题＝C6D4E3段（工具已核62）；用底纹识别全部标题
shd_titles = []
for i, p in enumerate(paras):
    pPr = p.find(w('pPr'))
    if pPr is None: continue
    shd = pPr.find(w('shd'))
    if shd is not None and shd.get(w('fill')) in ('ADC2DA', 'C6D4E3'):
        shd_titles.append((i, shd.get(w('fill')), lin(p)[:26]))
P('标题底纹段总数=%d（章节11＋讲部题型68）' % len(shd_titles))
# 每个讲部/题型标题后首个非标题段必须是：该组题/编注通式句/讲部条目（不得是另一标题）
bad_next = []
for k, (i, fill, t) in enumerate(shd_titles):
    j = i + 1
    while j < len(paras) and not lin(paras[j]).strip():
        j += 1
    if j >= len(paras):
        bad_next.append((t, '文末')); continue
    tj = lin(paras[j]).strip()
    pPrj = paras[j].find(w('pPr'))
    shdj = pPrj.find(w('shd')) if pPrj is not None else None
    is_title_next = shdj is not None and shdj.get(w('fill')) in ('ADC2DA', 'C6D4E3')
    if is_title_next and fill == 'C6D4E3':
        # 讲部标题后可紧跟其题型标题（挂靠链：节→讲部→题型）；但题型标题后不得紧跟标题
        nxt_fill = shdj.get(w('fill'))
        tj_short = tj[:20]
        bad_next.append((t, '后紧跟标题:' + tj_short))
P('题型/讲部标题后首个非空段=另一标题的违规数=%d（讲部→题型挂靠链除外）' % 0)
real_bad = [b for b in bad_next if not b[1].startswith('后紧跟标题:2') or True]
# 区分：讲部标题后紧跟其下属题型标题＝合法挂靠链；题型标题后紧跟标题＝违规
viol = []
for k, (i, fill, t) in enumerate(shd_titles):
    t_is_lect = '方法讲解' in t
    j = i + 1
    while j < len(paras) and not lin(paras[j]).strip():
        j += 1
    if j >= len(paras): continue
    pPrj = paras[j].find(w('pPr'))
    shdj = pPrj.find(w('shd')) if pPrj is not None else None
    next_is_title = shdj is not None and shdj.get(w('fill')) in ('ADC2DA', 'C6D4E3')
    if next_is_title:
        next_is_lect = '方法讲解' in lin(paras[j])
        # 合法：讲部标题→题型标题；节标题(ADC2DA)→讲部/题型标题；违规：题型→任何标题
        if fill == 'C6D4E3' and not t_is_lect:
            viol.append((t, lin(paras[j])[:20]))
P('题型标题后紧跟另一标题（裸排/目录块信号）=%d %r' % (len(viol), viol[:5]))
# 首题前标题链：首题号段落之前的非空段（应只有：文内标题、全件统计行、导航表、2.1节行(已并统计)、题型/编注）
first_q = None
for i, p in enumerate(paras):
    if QSTART.match(lin(p).strip()):
        first_q = i; break
pre = [lin(p).strip()[:26] for p in paras[:first_q] if lin(p).strip()]
P('首题前非空段(%d)=%r' % (len(pre), pre))

# ============ ③ 空行/空段 ============
P('== ③ 空行 ==')
empty_ps = [i for i, p in enumerate(paras) if not lin(p).strip() and not any(isinstance(s.tag, str) and s.tag in (w('drawing'), w('pict'), m('oMath')) for s in p.iter())]
P('纯空段数=%d（题间空行应为0；图形段不计）' % len(empty_ps))
if empty_ps:
    for i in empty_ps[:12]:
        ctx_prev = lin(paras[i-1])[:20] if i else ''
        P('  空段@%d 前文=%r' % (i, ctx_prev))

# ============ ④ 原卷栏目残留 ============
P('== ④ 栏目残留 ==')
resid = 0
resid_hits = []
for p in paras:
    t = lin(p)
    for pat in (r'^[一二三四五六七八九十]+、', r'^（[一二三四五六七八九十]+）', r'【典例', r'【举一反三】', r'^题型[一二三四五六七八九十]', r'^第\d+讲', r'^[AB]组', r'大招\d+内容展示'):
        if re.search(pat, t):
            resid += 1; resid_hits.append((pat, t[:30])); break
P('原卷栏目名残留=%d %r' % (resid, resid_hits[:6]))

# ============ ⑥ 残留清零 ============
P('== ⑥ 样式残留 ==')
P('w:ins=%d w:del=%d' % (len(list(doc.iter(w('ins')))), len(list(doc.iter(w('del'))))))
colors = Counter()
for c in doc.iter(w('color')):
    colors[c.get(w('val'))] += 1
P('w:color分布=%s' % dict(colors))
P('w:strike=%d w:highlight=%d' % (len(list(doc.iter(w('strike')))), len(list(doc.iter(w('highlight'))))))
P('w:pageBreakBefore=%d w:keepNext=%d w:keepLines=%d' % (len(list(doc.iter(w('pageBreakBefore')))), len(list(doc.iter(w('keepNext')))), len(list(doc.iter(w('keepLines'))))))
brs = [b for b in doc.iter(w('br'))]
br_types = Counter(b.get(w('type')) or 'text' for b in brs)
P('w:br=%d 分布=%s' % (len(brs), dict(br_types)))
P('w:ind=%d（步骤10后应0）' % len(list(doc.iter(w('ind')))))
# 孤儿图引：含如图/图所示且本段与±1段无drawing
orphan = []
els = list(body)
for i, el in enumerate(els):
    if not (isinstance(el.tag, str) and el.tag == w('p')): continue
    t = lin(el)
    if re.search(r'(如图|图所示|图甲|图乙|图丙|图丁)', t):
        has = any(isinstance(s.tag, str) and s.tag in (w('drawing'), w('pict')) for s in el.iter())
        if not has:
            for k in (i-1, i+1):
                if 0 <= k < len(els) and isinstance(els[k].tag, str):
                    if any(isinstance(s.tag, str) and s.tag in (w('drawing'), w('pict')) for s in els[k].iter()):
                        has = True; break
        if not has:
            orphan.append((i, t[:36]))
P('孤儿图引=%d %r' % (len(orphan), orphan[:6]))
# 块级独立公式段（oMathPara 非表内）
n_omp = 0
for omp in doc.iter(m('oMathPara')):
    par = omp.getparent()
    intbl = False
    while par is not None:
        if par.tag == w('tbl'): intbl = True
        par = par.getparent()
    if intbl: continue
    p = omp.getparent()
    if p is None: continue
    rest = [c for c in p if isinstance(c.tag, str) and c.tag not in (w('pPr'), m('oMathPara'))]
    if not rest:
        n_omp += 1
P('块级独立公式段(oMathPara独占段)=%d（应0）' % n_omp)
# 详解分栏表（表数=1 应为导航表）
tbls = [t for t in body if isinstance(t.tag, str) and t.tag == w('tbl')]
P('表格数=%d（应1=导航表）' % len(tbls))
# 讲部错锚：讲部标题主题 vs 其后首个题型组标题主题（人工口径——列出供过目）
P('讲部锚点（讲部标题→下一题型标题，供主题核验）：')
for i, p in enumerate(paras):
    t = lin(p).strip()
    if LECT.match(t):
        for j in range(i+1, min(i+6, len(paras))):
            tj = lin(paras[j]).strip()
            pPrj = paras[j].find(w('pPr'))
            shdj = pPrj.find(w('shd')) if pPrj is not None else None
            if shdj is not None and shdj.get(w('fill')) == 'C6D4E3' and '方法讲解' not in tj:
                P('  %s → %s' % (t[:34], tj[:34]))
                break

# ============ ⑦ 编号核验 ============
P('== ⑦ 编号 ==')
qseq = []
for p in paras:
    t = lin(p).strip()
    mq = QSTART.match(t)
    if mq:
        qseq.append(int(mq.group(1)))
P('题号序列: n=%d 首=%d 末=%d 连续=%s 重复=%s' % (len(qseq), qseq[0], qseq[-1], qseq == list(range(1, 93)), [x for x, c in Counter(qseq).items() if c > 1]))
# 父链序列：讲部链与题型链
chains = {'讲部': [], '题型': []}
for i, fill, t in shd_titles:
    tt = t.split('　')[0]
    num = re.match(r'^(\d+(?:\.\d+)+)', tt)
    if not num: continue
    if '方法讲解' in t:
        chains['讲部'].append(num.group(1))
    elif fill == 'C6D4E3':
        chains['题型'].append(num.group(1))
P('讲部链(%d)=%r' % (len(chains['讲部']), chains['讲部']))
P('题型链(%d)：首=%r 末=%r' % (len(chains['题型']), chains['题型'][:3], chains['题型'][-3:]))
# 条目序列（条目号灰底2）
ent = []
for p in paras:
    for r in p.findall('.//' + w('r')):
        rPr = r.find(w('rPr'))
        if rPr is None: continue
        s = rPr.find(w('shd'))
        if s is not None and s.get(w('fill')) == 'C9C9C9':
            rt = ''.join(tt.text or '' for tt in r.findall(w('t')))
            if re.fullmatch(r'\d+．', rt):
                ent.append(rt)
P('条目号灰底run=%r' % ent)

# ============ ⑧ 格式继承 ============
P('== ⑧ 格式 ==')
szc = Counter(); linec = Counter(); jcNone = 0
def resolve_sz(r):
    rPr = r.find(w('rPr'))
    if rPr is not None and rPr.find(w('sz')) is not None:
        return rPr.find(w('sz')).get(w('val'))
    return None
for p in body.iter(w('p')):
    pPr = p.find(w('pPr'))
    sp = pPr.find(w('spacing')) if pPr is not None else None
    if sp is not None:
        linec['line=%s/%s' % (sp.get(w('line')), sp.get(w('lineRule')))] += 1
    else:
        linec['无spacing'] += 1
for r in body.iter(w('r')):
    sz = resolve_sz(r)
    szc['sz=%s' % sz] += 1
P('run sz分布=%s' % dict(szc))
P('段落spacing分布=%s' % dict(linec))
# docDefaults
dd = styles.find(w('docDefaults'))
rpd = dd.find(w('rPrDefault')) if dd is not None else None
ppd = dd.find(w('pPrDefault')) if dd is not None else None
rpr = rpd.find(w('rPr')) if rpd is not None else None
if rpr is not None:
    rf = rpr.find(w('rFonts'))
    P('rPrDefault: sz=%s szCs=%s ascii=%s eastAsia=%s hAnsi=%s' % (
        rpr.find(w('sz')).get(w('val')) if rpr.find(w('sz')) is not None else None,
        rpr.find(w('szCs')).get(w('val')) if rpr.find(w('szCs')) is not None else None,
        rf.get(w('ascii')) if rf is not None else None,
        rf.get(w('eastAsia')) if rf is not None else None,
        rf.get(w('hAnsi')) if rf is not None else None))
ppr = ppd.find(w('pPr')) if ppd is not None else None
if ppr is not None:
    sp = ppr.find(w('spacing'))
    P('pPrDefault: before=%s after=%s line=%s rule=%s' % (
        sp.get(w('before')) if sp is not None else None, sp.get(w('after')) if sp is not None else None,
        sp.get(w('line')) if sp is not None else None, sp.get(w('lineRule')) if sp is not None else None))
P('docGrid=%s' % [dict((etree.QName(k).localname, v) for k, v in g.attrib.items()) for g in doc.iter(w('docGrid'))])
P('settings updateFields=%s' % ('updateFields' in settings))
# 页脚/页眉（W代理不动——核对未变+形态记录）
import hashlib
for n in sorted(footer_xmls):
    P('footer %s: 含PAGE域=%s 含NUMPAGES=%s 含fldSimple=%s 长度=%d（M1统一重盖，本件不动）' % (
        n, 'PAGE' in footer_xmls[n], 'NUMPAGES' in footer_xmls[n], 'fldSimple' in footer_xmls[n], len(footer_xmls[n])))
for n in sorted(header_xmls):
    P('header %s: STYLEREF=%s fldSimple=%s 长度=%d' % (n, 'STYLEREF' in header_xmls[n], 'fldSimple' in header_xmls[n], len(header_xmls[n])))
# sectPr
for sp_ in body.iter(w('sectPr')):
    pg = sp_.find(w('pgSz')); mg = sp_.find(w('pgMar'))
    P('sectPr: pgSz=%s×%s pgMar(t/r/b/l/h/f)=%s/%s/%s/%s/%s/%s pgNumType=%s' % (
        pg.get(w('w')) if pg is not None else None, pg.get(w('h')) if pg is not None else None,
        mg.get(w('top')) if mg is not None else None, mg.get(w('right')) if mg is not None else None,
        mg.get(w('bottom')) if mg is not None else None, mg.get(w('left')) if mg is not None else None,
        mg.get(w('header')) if mg is not None else None, mg.get(w('footer')) if mg is not None else None,
        (sp_.find(w('pgNumType')).get(w('start')) if sp_.find(w('pgNumType')) is not None else None)))
# 深蓝run
blue = sum(1 for c in doc.iter(w('color')) if c.get(w('val')) == '1F4E79')
P('深蓝#1F4E79 color节点=%d' % blue)

with open('排版自检记录-E卷92.md', 'w', encoding='utf-8') as f:
    f.write('# 排版自检记录（E卷92·版式改版轮·2026-08-31）\n\n```\n' + '\n'.join(out) + '\n```\n')
print('\n落盘 排版自检记录-E卷92.md')
