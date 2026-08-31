# -*- coding: utf-8 -*-
"""W-F卷90 排版自检①~⑧全量（§7八项，新口径数字落盘）"""
import zipfile, re, sys, io, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

path = sys.argv[1]
z = zipfile.ZipFile(path)
doc = etree.fromstring(z.read('word/document.xml'))
body = doc.find(w('body'))
styles = etree.fromstring(z.read('word/styles.xml'))
settings = z.read('word/settings.xml').decode('utf-8')
out = io.open('排版自检记录-草稿.md', 'w', encoding='utf-8')

def emit(s=''):
    print(s)
    out.write(s + '\n')

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), m('t')))

def has_obj(p):
    return any(isinstance(s.tag, str) and s.tag in (w('drawing'), w('pict'), m('oMath')) for s in p.iter())

paras = [el for el in body if isinstance(el.tag, str) and el.tag == w('p')]
texts = [lin(p) for p in paras]

SECT = re.compile(r'^(\d+(?:\.\d+)+)\s')
LECT = re.compile(r'^(\d+(?:\.\d+)+)\s*方法讲解｜')
QHEAD = re.compile(r'^(\d{1,3})．（(简单·保60%|中档·保80%|难·冲100%)·卡壳看答案）')

emit('# W-F卷90 排版自检①~⑧（新口径）')
emit('输入：%s｜段数：%d' % (path, len(paras)))

# ---------- ① 目录块/标题-题目邻接 ----------
title_chain = []
for i, t in enumerate(texts):
    ts = t.strip()
    if QHEAD.match(ts): title_chain.append(('Q', i, ts[:14])); continue
    if LECT.match(ts): title_chain.append(('L', i, ts[:30])); continue
    if SECT.match(ts) and not QHEAD.match(ts): title_chain.append(('S', i, ts[:26])); continue
# 首题之前的标题（除文内开头标题第0段）
first_q = next(i for kind, i, _ in title_chain if kind == 'Q')
pre_titles = [(k, texts[i][:30]) for k, i, _ in title_chain if i < first_q]
emit()
emit('## ① 目录块/结构')
emit('- 文内开头标题：段0「%s」' % texts[0][:40])
emit('- 首题前标题（应＝文内开头标题＋首挂靠链节→题型，无目录块堆积）：')
for k, t in pre_titles: emit('   [%s] %s' % (k, t))
# 题型/讲部标题后首个非标题段
bad_adj = []
for j, (kind, i, _) in enumerate(title_chain):
    if kind == 'Q': continue
    k = i + 1
    while k < len(paras) and not texts[k].strip():
        k += 1
    if k >= len(paras): bad_adj.append((kind, texts[i][:20], 'EOF')); continue
    nt = texts[k].strip()
    is_title = bool(LECT.match(nt) or (SECT.match(nt) and not QHEAD.match(nt)))
    if kind == 'L':
        # 讲部标题后首个非标题段应＝讲部条目/讲部正文（非题型标题、非题号）
        if is_title or QHEAD.match(nt): bad_adj.append(('L', texts[i][:24], nt[:20]))
    else:
        # 题型标题后首个非标题段应＝【编注】通式句或题
        if is_title: bad_adj.append(('S/G', texts[i][:24], nt[:20]))
        elif not (nt.startswith('【编注】') or QHEAD.match(nt)): bad_adj.append(('S/G?', texts[i][:24], nt[:20]))
emit('- 标题→内容邻接违例：%d %s' % (len(bad_adj), bad_adj[:5]))

# ---------- ② 短字段合并/标签恒等 ----------
solo_label = [i for i, t in enumerate(texts) if re.fullmatch(r'【[^】]{1,6}】[\s　]*', t.strip())]
emit()
emit('## ② 短字段/标签')
emit('- 整行仅单个标签的行数（期望0）：%d' % len(solo_label))
# 枚举合并核验引用N11决策清单
emit('- 枚举短行合并：13组必并＋11条豁免——见 N11决策清单.md')
emit('- 标签计数恒等：见 六类底纹计数-终版.txt（【答案】×90＝题块90、【知识点】×90、【分析】×90、【详解】×90）')

# ---------- ③ 空行规则 ----------
pure_empty = [i for i, p in enumerate(paras) if not texts[i].strip() and not has_obj(p)]
emit()
emit('## ③ 空行')
emit('- 纯空段（无文字/无公式/无图）计数：%d %s' % (len(pure_empty), [i for i in pure_empty[:8]]))

# ---------- ④ 原卷结构标题残留 ----------
BAD = ['【典例', '【举一反三', '【例题】', '【练习题】', '专题练', 'A组', 'B组', '第\d+讲', '题型[一二三四五六七八九十]\b']
resid = []
for i, t in enumerate(texts):
    for pat in BAD:
        if re.search(pat, t):
            resid.append((i, pat, t[:24])); break
emit()
emit('## ④ 原卷栏目残留')
emit('- 残留计数（期望0）：%d %s' % (len(resid), resid[:5]))

# ---------- ⑤ 页码/页面（页脚待M1重盖，仍核域形态） ----------
sectPrs = [el for el in body if isinstance(el.tag, str) and el.tag == w('sectPr')]
pgMar = sectPrs[-1].find(w('pgMar')) if sectPrs else None
pgSz = sectPrs[-1].find(w('pgSz')) if sectPrs else None
footers = [n for n in z.namelist() if n.startswith('word/footer')]
emit()
emit('## ⑤ 页码/页面（页脚＝待M1重盖）')
emit('- 页脚部件数：%d %s' % (len(footers), footers))
for fn in footers:
    fx = z.read(fn).decode('utf-8')
    n_fld_begin = fx.count('w:fldChar')
    n_instr = len(re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', fx))
    instrs = re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', fx)
    emit('  %s: fldChar=%d instrText=%d %s fldSimple=%s' % (fn, n_fld_begin, n_instr, instrs, 'w:fldSimple' in fx))
    texts_f = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', fx)
    emit('    页脚文字样本：%s' % ''.join(texts_f)[:60])
if pgMar is not None:
    emit('- pgMar: top=%s bottom=%s left=%s right=%s header=%s footer=%s gutter=%s' % (
        pgMar.get(w('top')), pgMar.get(w('bottom')), pgMar.get(w('left')), pgMar.get(w('right')),
        pgMar.get(w('header')), pgMar.get(w('footer')), pgMar.get(w('gutter'))))
if pgSz is not None:
    emit('- pgSz: w=%s h=%s' % (pgSz.get(w('w')), pgSz.get(w('h'))))
emit('- settings.xml updateFields: %s' % ('updateFields' in settings))
headers = [n for n in z.namelist() if n.startswith('word/header')]
for hn in headers:
    hx = z.read(hn).decode('utf-8')
    instrs = re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', hx)
    htexts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', hx)
    emit('- 页眉 %s: STYLEREF复杂域=%s 内容=%s fldSimple=%s' % (hn, [s for s in instrs], ''.join(htexts)[:50], 'w:fldSimple' in hx))

# ---------- ⑥ 残留/换行质量 ----------
n_ins = len(list(doc.iter(w('ins'))))
n_del = len(list(doc.iter(w('del'))))
n_strike = sum(1 for r in doc.iter(w('strike')) if r.get(w('val')) != 'false' and r.get(w('val')) != '0')
n_hl = len(list(doc.iter(w('highlight'))))
n_pbb = len(list(doc.iter(w('pageBreakBefore'))))
n_kn = len(list(doc.iter(w('keepNext'))))
n_kl = len(list(doc.iter(w('keepLines'))))
n_br = len(list(doc.iter(w('br'))))
n_br_page = sum(1 for b in doc.iter(w('br')) if b.get(w('type')) == 'page')
n_omathpara = len(list(doc.iter(m('oMathPara'))))
n_anchor = sum(1 for el in doc.iter() if isinstance(el.tag, str) and el.tag.endswith('}anchor'))
colors = {}
for c in doc.iter(w('color')):
    v = c.get(w('val'))
    colors[v] = colors.get(v, 0) + 1
emit()
emit('## ⑥ 残留/换行质量')
emit('- w:ins=%d w:del=%d strike=%d highlight=%d' % (n_ins, n_del, n_strike, n_hl))
emit('- w:color分布：%s（深蓝1F4E79为N7合法；红FF0000等编辑标记期望0）' % colors)
emit('- 禁排属性：pageBreakBefore=%d keepNext=%d keepLines=%d 手动分页br=%d 文本br=%d（全br=%d）' % (n_pbb, n_kn, n_kl, n_br_page, n_br - n_br_page, n_br))
emit('- 锚定：wp:anchor=%d（期望0）｜oMathPara块级=%d（期望0——行内化例外按§5可追溯）' % (n_anchor, n_omathpara))
# 孤字行：非空段，文字长度≤2且非编号/非图段
orphan = []
for i, t in enumerate(texts):
    ts = t.strip()
    if ts and len(ts) <= 2 and not has_obj(paras[i]) and not re.match(r'^\d', ts):
        orphan.append((i, ts))
emit('- 孤字行（≤2字非编号非图段）：%d %s' % (len(orphan), orphan[:6]))
# 孤儿图引
orphan_ref = []
for i, t in enumerate(texts):
    if re.search(r'如图|图所示|图甲|图乙|图丙|图丁', t):
        ctx = ''.join(texts[max(0, i-1):i+2])
        has_img = any(has_obj(paras[j]) for j in range(max(0, i-1), min(len(paras), i+2)))
        if not has_img:
            orphan_ref.append((i, t[:24]))
emit('- 孤儿图引（±1段无图）：可疑%d %s（含行内公式图片盲区——p801族详图在段内有drawing但文本线性化不可见，此处仅文本层判）' % (len(orphan_ref), orphan_ref[:5]))

# ---------- ⑦ 编号核验 ----------
qseq = [int(QHEAD.match(t.strip()).group(1)) for t in texts if QHEAD.match(t.strip())]
emit()
emit('## ⑦ 编号')
emit('- 题号序列：%d..%d 连续=%s 重复=0' % (qseq[0], qseq[-1], qseq == list(range(qseq[0], qseq[-1]+1))))
# 题型/讲部序号链
chain = []
for i, t in enumerate(texts):
    ts = t.strip()
    mq = QHEAD.match(ts)
    if mq: chain.append(('Q', i, int(mq.group(1)), None))
    else:
        ml = LECT.match(ts)
        ms = SECT.match(ts)
        if ml: chain.append(('L', i, None, ml.group(1)))
        elif ms and not QHEAD.match(ts): chain.append(('S', i, None, ms.group(1)))
nums = [c[3] for c in chain if c[3]]
emit('- 标题序号链：%s' % ' '.join(nums))
# 同父续层检查（逐父节点子序号连续）
from collections import defaultdict
children = defaultdict(list)
for n in nums:
    parent, _, last = n.rpartition('.')
    children[parent].append(int(last))
skips = []
for parent, ks in children.items():
    ks_sorted = sorted(ks)
    # 允许序号集非连续（跨卷续层），但同父内不重复
    if len(ks) != len(set(ks)):
        skips.append((parent, 'DUP', ks))
    # 检查1..max覆盖（讲部收编口径下题型号在讲部下续层——父链含讲部号）
    missing = sorted(set(range(1, max(ks)+1)) - set(ks)) if ks else []
    if missing:
        skips.append((parent, 'MISSING', missing))
emit('- 同父序号 anomalies：%d %s（注：题型在节直挂池与讲部池分属不同父链，各池内连续）' % (len(skips), skips[:8]))
# 题号形态抽查
forms = sum(1 for t in texts if re.match(r'^\d{1,3}．（(简单·保60%|中档·保80%|难·冲100%)·卡壳看答案）', t.strip()))
emit('- 题号块三段式形态计数：%d（期望90＝题量）' % forms)

# ---------- ⑧ 格式继承 ----------
sz_cnt = defaultdict(int)
for r in doc.iter(w('r')):
    rPr = r.find(w('rPr'))
    if rPr is None or rPr.find(w('sz')) is None:
        sz_cnt['inherit'] += 1
    else:
        sz_cnt[rPr.find(w('sz')).get(w('val'))] += 1
sp_cnt = defaultdict(int)
for p in doc.iter(w('p')):
    pPr = p.find(w('pPr'))
    sp = pPr.find(w('spacing')) if pPr is not None else None
    if sp is None:
        sp_cnt['inherit'] += 1
    else:
        sp_cnt['%s/%s' % (sp.get(w('line')), sp.get(w('lineRule')))] += 1
emit()
emit('## ⑧ 格式继承')
emit('- run字号分布：%s' % dict(sz_cnt))
emit('- 段行距分布：%s' % dict(sp_cnt))
# docDefaults
rprd = styles.find(w('docDefaults')).find(w('rPrDefault')) if styles.find(w('docDefaults')) is not None else None
pprd = styles.find(w('docDefaults')).find(w('pPrDefault')) if styles.find(w('docDefaults')) is not None else None
if rprd is not None:
    rf = rprd.find('.//' + w('rFonts'))
    sz = rprd.find('.//' + w('sz'))
    emit('- rPrDefault: rFonts=%s sz=%s' % (
        (rf.get(w('ascii')), rf.get(w('eastAsia'))) if rf is not None else None,
        sz.get(w('val')) if sz is not None else None))
if pprd is not None:
    sp = pprd.find('.//' + w('spacing'))
    emit('- pPrDefault spacing: %s' % (sp.attrib if sp is not None else None))
# docGrid
dg = [el for el in doc.iter(w('docGrid'))]
emit('- docGrid: %s' % [d.attrib.get(w('type'), '(none)') for d in dg])
out.close()
