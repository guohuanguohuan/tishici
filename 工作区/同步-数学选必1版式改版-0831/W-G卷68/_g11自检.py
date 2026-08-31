# -*- coding: utf-8 -*-
"""W-G卷68 排版自检①~⑧全量（新口径）——结果落盘 排版自检记录.md"""
import zipfile, re, json, io
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def wt(t): return '{%s}%s' % (W, t)
def mt(t): return '{%s}%s' % (M, t)

PATH = 'G工作副本.docx'
z = zipfile.ZipFile(PATH)
parts = {n: z.read(n) for n in z.namelist()}
doc = etree.fromstring(parts['word/document.xml'])
body = doc.find(wt('body'))
els = list(body)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (wt('t'), mt('t')))

paras = [(i, e, lin(e)) for i, e in enumerate(els) if isinstance(e.tag, str) and e.tag == wt('p')]
R = {}

# ---------- ① 结构：无目录块；题型标题→首个非标题段=通式句/讲部；节标题→通式句或题或讲部 ----------
TITLE = re.compile(r'^\d+(\.\d+)+\s')
LECT = re.compile(r'^\d+(\.\d+)+\s*方法讲解')
QHEAD = re.compile(r'^\d{1,4}．（')
titles = [(i, t) for i, e, t in paras if TITLE.match(t) or (t and t.startswith('人教B版'))]
bad_follow = []
for k, (i, t) in enumerate(titles):
    nxt = None
    for j in range(i + 1, len(els)):
        e = els[j]
        if isinstance(e.tag, str) and e.tag == wt('p'):
            tt = lin(e)
            if tt.strip():
                nxt = tt; break
        else:
            nxt = '(非段元素)'; break
    is_qtype = TITLE.match(t) and not LECT.match(t) and not re.match(r'^\d+\.\d+\.\d+\s', t) and re.match(r'^\d+(\.\d+){3,}', t)
    if is_qtype and nxt and not (nxt.startswith('【编注】') or QHEAD.match(nxt)):
        bad_follow.append((t[:40], nxt[:40]))
R['①题型标题后首段违例'] = bad_follow
R['①标题总数'] = len(titles)
# 首题前标题数（挂靠链）：文内标题→2.6→2.6.1→2.6.1.1→通式句→183题：链长=4
first_q = next(i for i, e, t in paras if QHEAD.match(t))
R['①首题前标题链'] = [t[:30] for i, t in titles if i < first_q]

# ---------- ② 标签行横排＋孤标签行 ----------
solo = []
for i, e, t in paras:
    ts = t.strip()
    for lab in ('【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】'):
        if ts.startswith(lab) and len(ts) < len(lab) + 1:
            solo.append(ts)
R['②孤标签行'] = solo
# 【答案】行同时含【知识点】计数（横排合并核验）
ans_lines = [t for i, e, t in paras if t.strip().startswith('【答案】')]
R['②【答案】行数'] = len(ans_lines)
R['②【答案】行内含【知识点】'] = sum(1 for t in ans_lines if '【知识点】' in t)

# ---------- ③ 空行规则：纯空段（无图无公式无文字）计数 ----------
empt = 0
for i, e, t in paras:
    if t.strip(): continue
    has_obj = any(isinstance(s.tag, str) and s.tag in (wt('drawing'), wt('pict')) for s in e.iter())
    has_math = any(isinstance(s.tag, str) and s.tag == mt('oMath') for s in e.iter())
    if not has_obj and not has_math:
        empt += 1
R['③纯空段'] = empt

# ---------- ④ 原卷栏目名残留 ----------
bad4 = []
for i, e, t in paras:
    for b in ['【典例', '【举一反三】', '【例题】', '【练习题】', '专题练', 'A组', 'B组', '题型一', '题型二']:
        if b in t:
            bad4.append((b, t[:40]))
R['④栏目名残留'] = bad4

# ---------- ⑤ 页脚/页面 ----------
sect = body.find(wt('sectPr'))
pgsz = sect.find(wt('pgSz')); pgmar = sect.find(wt('pgMar'))
R['⑤pgSz'] = (pgsz.get(wt('w')), pgsz.get(wt('h')))
R['⑤pgMar'] = {k.split('}')[1]: v for k, v in pgmar.attrib.items()}
foot_parts = [n for n in parts if n.startswith('word/footer')]
R['⑤footer部件数'] = len(foot_parts)
fxml = parts[foot_parts[0]].decode('utf-8') if foot_parts else ''
R['⑤footer域形态'] = {'fldChar': fxml.count('fldChar'), 'instrText': len(re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', fxml)),
                    'instr内容': re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', fxml)[:3],
                    'fldSimple': fxml.count('fldSimple'), 'NUMPAGES': fxml.count('NUMPAGES')}
m = re.search(r'<w:footnotePr|<w:ftr', fxml)
R['⑤footer可见文本'] = re.sub(r'<[^>]+>', '', fxml)[:80]
st = etree.fromstring(parts['word/settings.xml'])
R['⑤updateFields'] = st.find(wt('updateFields')) is not None
R['⑤evenAndOddHeaders'] = st.find(wt('evenAndOddHeaders')) is not None
hdr_parts = [n for n in parts if n.startswith('word/header')]
R['⑤header部件数'] = len(hdr_parts)

# ---------- ⑥ 样式残留与图公式十项 ----------
cnt6 = {'w:ins': 0, 'w:del': 0, '彩行run': 0, 'strike': 0, 'highlight': 0, 'pageBreakBefore': 0,
        'keepNext': 0, 'keepLines': 0, 'w:br': 0, 'w:anchor': 0, 'oMathPara': 0}
for tag, key in [('ins', 'w:ins'), ('del', 'w:del'), ('anchor', 'w:anchor')]:
    cnt6[key] = len(doc.findall('.//' + wt(tag))) if tag != 'anchor' else len(doc.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}anchor'))
cnt6['oMathPara'] = len(doc.findall('.//' + mt('oMathPara')))
for r in doc.iter(wt('r')):
    rpr = r.find(wt('rPr'))
    if rpr is None: continue
    c = rpr.find(wt('color'))
    if c is not None and c.get(wt('val')) not in ('000000', 'auto', '1F4E79'):
        cnt6['彩行run'] += 1
    if rpr.find(wt('strike')) is not None or rpr.find(wt('dstrike')) is not None:
        cnt6['strike'] += 1
    if rpr.find(wt('highlight')) is not None:
        cnt6['highlight'] += 1
for p in doc.iter(wt('p')):
    ppr = p.find(wt('pPr'))
    if ppr is None: continue
    if ppr.find(wt('pageBreakBefore')) is not None: cnt6['pageBreakBefore'] += 1
    if ppr.find(wt('keepNext')) is not None: cnt6['keepNext'] += 1
    if ppr.find(wt('keepLines')) is not None: cnt6['keepLines'] += 1
for br in doc.iter(wt('br')):
    cnt6['w:br'] += 1
R['⑥残留计数'] = cnt6
R['⑥表格数'] = sum(1 for e in els if isinstance(e.tag, str) and e.tag == wt('tbl'))
R['⑥挖空双标记'] = '复扫残余＿=0（N15步骤实测）'

# ---------- ⑦ 编号核验 ----------
seq = []
for i, e, t in paras:
    m2 = re.match(r'^(\d{1,4})．（', t)
    if m2: seq.append(int(m2.group(1)))
gaps = [(seq[k-1], seq[k]) for k in range(1, len(seq)) if seq[k] != seq[k-1] + 1]
R['⑦题号序列'] = {'起': seq[0], '终': seq[-1], '数': len(seq), '断点': gaps}
# 题型序号链
qchains = {}
for i, e, t in paras:
    m3 = re.match(r'^(\d+(?:\.\d+)+)\s', t)
    if m3:
        qchains.setdefault(m3.group(1), 0)
        qchains[m3.group(1)] += 1
R['⑦序号链数'] = len(qchains)
R['⑦序号重复'] = {k: v for k, v in qchains.items() if v > 1}

# ---------- ⑧ 格式继承 ----------
sz = {}; line = {}
for r in doc.iter(wt('r')):
    rpr = r.find(wt('rPr'))
    if rpr is None: continue
    s_ = rpr.find(wt('sz'))
    if s_ is not None:
        v = s_.get(wt('val'))
        sz[v] = sz.get(v, 0) + 1
R['⑧run字号分布'] = dict(sorted(sz.items(), key=lambda x: -x[1]))
for p in doc.iter(wt('p')):
    ppr = p.find(wt('pPr'))
    if ppr is None: continue
    sp = ppr.find(wt('spacing'))
    if sp is not None and sp.get(wt('line')):
        key = sp.get(wt('line')) + '/' + (sp.get(wt('lineRule')) or '')
        line[key] = line.get(key, 0) + 1
R['⑧行距分布'] = line
sty = etree.fromstring(parts['word/styles.xml'])
dd = sty.find(wt('docDefaults'))
rprd = dd.find(wt('rPrDefault'))
szd = rprd.find('.//' + wt('sz')) if rprd is not None else None
fnd = rprd.find('.//' + wt('rFonts')) if rprd is not None else None
R['⑧rPrDefault'] = {'sz': szd.get(wt('val')) if szd is not None else None,
                   'fonts': {k.split('}')[1]: v for k, v in (fnd.attrib if fnd is not None else {}).items()}}
docgrid = sect.find(wt('docGrid'))
R['⑧docGrid'] = {k.split('}')[1]: v for k, v in (docgrid.attrib if docgrid is not None else {}).items()}
# 三色与深蓝
fills = {}
for shd in doc.iter(wt('shd')):
    f = shd.get(wt('fill'))
    if f: fills[f] = fills.get(f, 0) + 1
R['⑧shd三色'] = {k: v for k, v in fills.items() if k in ('C9C9C9', 'ADC2DA', 'C6D4E3')}
blue = 0
for c in doc.iter(wt('color')):
    if c.get(wt('val')) == '1F4E79': blue += 1
R['⑧深蓝color节点'] = blue
z.close()
io.open('排版自检-数据.json', 'w', encoding='utf-8').write(json.dumps(R, ensure_ascii=False, indent=1, default=str))
print(json.dumps(R, ensure_ascii=False, indent=1, default=str)[:3500])
