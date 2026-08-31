# -*- coding: utf-8 -*-
# 排版自检①~⑧全量（X1衔接件·新口径）——只读
import zipfile, re, json, sys
from lxml import etree
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WPDNS='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
ANS='http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s'%(WNS,t)
p = sys.argv[1]
z = zipfile.ZipFile(p)
doc = etree.fromstring(z.read('word/document.xml'))
styles = etree.fromstring(z.read('word/styles.xml'))
settings = z.read('word/settings.xml').decode('utf-8')
z.close()
body = doc.find(q('body'))
paras = list(body.iter(q('p')))
R = {}

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

# ① 结构：标题识别（段级ADC2DA/C6D4E3）＋题型标题后首个非标题段
WPD='{%s}'%WPDNS
titles = []  # (idx, type, text)
for i, para in enumerate(paras):
    ppr = para.find(q('pPr'))
    if ppr is None: continue
    shd = ppr.find(q('shd'))
    if shd is None: continue
    f = shd.get(q('fill'))
    if f == 'ADC2DA': titles.append((i, '章节', ptext(para)))
    elif f == 'C6D4E3': titles.append((i, '题型', ptext(para)))
R['标题清单'] = [(i, t, s[:46]) for i,t,s in titles]
# 题型标题后首个非标题段必须是题（两段式题号块）
issues1 = []
tset = {i for i,_,_ in titles}
for i, t, s in titles:
    if t != '题型': continue
    j = i+1
    while j < len(paras) and j in tset: j += 1
    if j < len(paras):
        txt = ptext(paras[j])
        if not re.match(r'^\d+．（衔接必会·卡壳看答案）', txt):
            issues1.append((j, txt[:30]))
R['①题型标题后首段非题'] = issues1
# 目录块：开头连续标题列队（首题前>1条挂靠链）
first_q = next(i for i,p in enumerate(paras) if re.match(r'^1．（衔接必会', ptext(p)))
before = [i for i,_,_ in titles if i < first_q]
R['①首题前标题段数'] = len(before)

# ③ 空行：题块之间空段＋详解内空段（连续空段计数；空段=无文字无图无公式）
def is_empty(p):
    if ptext(p).strip(): return False
    if p.find('.//'+q('drawing')) is not None: return False
    if p.find('.//{%s}oMath'%'http://schemas.openxmlformats.org/officeDocument/2006/math') is not None: return False
    return True
empties = [i for i,p in enumerate(paras) if is_empty(p)]
R['③空段总数'] = len(empties)
R['③空段位置'] = empties[:20]

# ④ 原卷结构标题残留
bad_titles = []
for i,p in enumerate(paras):
    t = ptext(p).strip()
    if re.match(r'^(一|二|三|四|五|六|七|八|九|十)+、', t): bad_titles.append((i,t[:30]))
    if re.match(r'^(题型|专题|考点|典题|大招)\s*[一二三四五六七八九十\d]', t): bad_titles.append((i,t[:30]))
    if re.match(r'^A组|^B组|^第\d+讲', t): bad_titles.append((i,t[:30]))
R['④原卷结构标题残留'] = bad_titles

# ⑦ 编号核验：题块序列＋条目序列＋条目第一子层
qnums = [int(m.group(1)) for p in paras if (m:=re.match(r'^(\d+)．（衔接必会·卡壳看答案）', ptext(p)))]
R['⑦题块序列'] = qnums == list(range(1,30))
# 条目题名行（条目号底纹9个）＝N．xxx 且非题号块（无两段式括注）
items = [(i, ptext(p)) for i,p in enumerate(paras) if re.match(r'^\d+．(?!（衔接必会)', ptext(p)) and not re.match(r'^\d+．（', ptext(p))]
# 过滤：详解内步骤「1．」类？条目题名行有C9C9C9条目号底纹——用底纹判定
item_nos = []
for i,pp in enumerate(paras):
    for r in pp.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        shd = rpr.find(q('shd'))
        if shd is not None and shd.get(q('fill'))=='C9C9C9':
            t = ''.join(tt.text or '' for tt in r.iter(q('t')))
            m = re.fullmatch(r'(\d+)．', t)
            if m: item_nos.append((i,int(m.group(1))))
R['⑦条目号底纹run序列'] = [n for _,n in item_nos]
# 条目第一子层（N）
sub1 = []
for i,pp in enumerate(paras):
    for r in pp.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        shd = rpr.find(q('shd'))
        if shd is not None and shd.get(q('fill'))=='C9C9C9':
            t = ''.join(tt.text or '' for tt in r.iter(q('t')))
            m = re.fullmatch(r'（(\d+)）', t)
            if m: sub1.append(int(m.group(1)))
R['⑦第一子层（N）序列'] = sub1

# ⑧ 字体解析：非数学区run rFonts统计（显式eastAsia=宋体、ascii=TNR）
MNS='http://schemas.openxmlformats.org/officeDocument/2006/math'
bad_font = 0; no_font_runs = 0; total_runs = 0
in_math = set()
for om in body.iter('{%s}oMath'%MNS):
    for e in om.iter(): in_math.add(id(e))
for r in body.iter(q('r')):
    if id(r) in in_math: continue  # 数学区不查
    rpr = r.find(q('rPr'))
    total_runs += 1
    if rpr is None or rpr.find(q('rFonts')) is None:
        no_font_runs += 1; continue
    rf = rpr.find(q('rFonts'))
    ea = rf.get(q('eastAsia')); asc = rf.get(q('ascii'))
    if ea not in ('宋体',None) or asc not in ('Times New Roman',None):
        bad_font += 1
R['⑧正文run总数'] = total_runs
R['⑧无rFonts的run数'] = no_font_runs
R['⑧rFonts值异常run数'] = bad_font
# docDefaults
dd = styles.find(q('docDefaults'))
rprd = dd.find('.//'+q('rPrDefault')+'/'+q('rPr')) if dd is not None else None
if rprd is not None:
    rf = rprd.find(q('rFonts'))
    sz = rprd.find(q('sz'))
    R['⑧docDefaults'] = {'eastAsia': rf.get(q('eastAsia')) if rf is not None else None,
                          'ascii': rf.get(q('ascii')) if rf is not None else None,
                          'sz': sz.get(q('val')) if sz is not None else None}
# 深蓝字run计数
blue = 0
for r in body.iter(q('r')):
    rpr = r.find(q('rPr'))
    if rpr is None: continue
    c = rpr.find(q('color'))
    if c is not None and c.get(q('val'))=='1F4E79': blue += 1
R['⑧深蓝#1F4E79字run数'] = blue
# docGrid
dg = body.find(q('sectPr'))
if dg is not None:
    grid = dg.find(q('docGrid'))
    R['docGrid'] = dict(grid.attrib) if grid is not None else None
# settings updateFields
R['settings含updateFields'] = 'updateFields' in settings
# 页眉部件
names = []
import zipfile as zf2
zz = zf2.ZipFile(sys.argv[1])
R['包内部件页眉页脚'] = [n for n in zz.namelist() if 'header' in n or 'footer' in n]
zz.close()
print(json.dumps(R, ensure_ascii=False, indent=1))
