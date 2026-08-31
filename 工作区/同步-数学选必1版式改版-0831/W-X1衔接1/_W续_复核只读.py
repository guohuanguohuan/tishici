# -*- coding: utf-8 -*-
# 续跑复核（只读）：字号解析计数／＿＿残留／题号块两段式／w:ind・jc现状／docDefaults
import zipfile, re, sys, json
from lxml import etree
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s'%(WNS,t)
p = sys.argv[1]
z = zipfile.ZipFile(p); doc = etree.fromstring(z.read('word/document.xml')); z.close()
body = doc.find(q('body'))
paras = list(body.iter(q('p')))
out = {}
out['段落总数'] = len(paras)

# 1 字号解析（显式sz统计，标题豁免run按32/28/24核对）
sz_hist = {}
for r in body.iter(q('r')):
    rpr = r.find(q('rPr'))
    if rpr is None: continue
    sz = rpr.find(q('sz'))
    if sz is None: continue
    v = sz.get(q('val'))
    sz_hist[v] = sz_hist.get(v,0)+1
out['run显式sz直方图'] = dict(sorted(sz_hist.items(), key=lambda x:-x[1]))
# 段落标记sz
pmark = {}
for para in paras:
    ppr = para.find(q('pPr'))
    if ppr is None: continue
    rpr = ppr.find(q('rPr'))
    if rpr is None: continue
    sz = rpr.find(q('sz'))
    if sz is not None:
        v = sz.get(q('val')); pmark[v]=pmark.get(v,0)+1
out['段落标记sz直方图'] = pmark

# 2 ＿＿残留
ush = 0
for t in body.iter(q('t')):
    if t.text and '＿' in t.text: ush += t.text.count('＿')
out['全角下划线＿字符数'] = ush

# 3 题号块两段式
two = re.compile(r'^(\d+)．（衔接必会·卡壳看答案）')
nums = []
for para in paras:
    txt = ''.join(t.text or '' for t in para.iter(q('t')))
    mm = two.match(txt)
    if mm: nums.append(int(mm.group(1)))
out['两段式题号块计数'] = len(nums)
out['两段式序列连续1..29'] = (nums == list(range(1,30)))

# 4 w:ind 残留（按段落）
ind_paras = []
for i,para in enumerate(paras,1):
    ppr = para.find(q('pPr'))
    if ppr is None: continue
    ind = ppr.find(q('ind'))
    if ind is not None:
        txt = ''.join(t.text or '' for t in para.iter(q('t')))[:30]
        ind_paras.append((i, dict(ind.attrib), txt))
out['带w:ind段落数'] = len(ind_paras)
out['w:ind明细'] = ind_paras

# 5 jc 非left统计
jc_hist = {}
for para in paras:
    ppr = para.find(q('pPr'))
    if ppr is None: jc_hist['<无pPr>'] = jc_hist.get('<无pPr>',0)+1; continue
    jc = ppr.find(q('jc'))
    if jc is None: jc_hist['<无jc=默认left>'] = jc_hist.get('<无jc=默认left>',0)+1
    else:
        v = jc.get(q('val')); jc_hist[v]=jc_hist.get(v,0)+1
out['段落jc直方图'] = jc_hist

# 6 docDefaults
z2 = zipfile.ZipFile(p); styles = etree.fromstring(z2.read('word/styles.xml')); z2.close()
dd = styles.find(q('docDefaults'))
out['docDefaults'] = etree.tostring(dd, encoding='unicode')[:600] if dd is not None else None

# 7 spacing行距直方图
sp_hist = {}
for para in paras:
    ppr = para.find(q('pPr'))
    if ppr is None: sp_hist['<无pPr>'] = sp_hist.get('<无pPr>',0)+1; continue
    sp = ppr.find(q('spacing'))
    if sp is None: sp_hist['<无spacing>'] = sp_hist.get('<无spacing>',0)+1; continue
    key = 'line=%s,%s' % (sp.get(q('line')), sp.get(q('lineRule')))
    sp_hist[key] = sp_hist.get(key,0)+1
out['spacing直方图'] = sp_hist

# 8 段前段后非0
ba = []
for i,para in enumerate(paras,1):
    ppr = para.find(q('pPr'))
    if ppr is None: continue
    sp = ppr.find(q('spacing'))
    if sp is None: continue
    b = sp.get(q('before')); a = sp.get(q('after'))
    if (b not in (None,'0')) or (a not in (None,'0')):
        ba.append((i,b,a))
out['段前段后非0段数'] = len(ba)

# 9 禁排属性
cnt = {k:0 for k in ['pageBreakBefore','keepNext','keepLines']}
for para in paras:
    ppr = para.find(q('pPr'))
    if ppr is None: continue
    for k in cnt:
        if ppr.find(q(k)) is not None: cnt[k]+=1
br_page = sum(1 for br in body.iter(q('br')) if br.get(q('type'))=='page')
br_text = sum(1 for br in body.iter(q('br')) if br.get(q('type')) is None)
out['禁排属性'] = cnt; out['br分页'] = br_page; out['br文本换行'] = br_text

# 10 样式残留六计数
w_ins = len(body.findall('.//'+q('ins'))); w_del = len(body.findall('.//'+q('del')))
color_bad = 0; strike = 0; hl = 0
for r in body.iter(q('r')):
    rpr = r.find(q('rPr'))
    if rpr is None: continue
    c = rpr.find(q('color'))
    if c is not None:
        v = c.get(q('val'))
        if v not in ('auto','000000','1F4E79'): color_bad += 1
    if rpr.find(q('strike')) is not None: strike += 1
    if rpr.find(q('highlight')) is not None: hl += 1
out['w:ins/w:del'] = [w_ins, w_del]
out['彩色run(非auto/000000/1F4E79)'] = color_bad
out['strike'] = strike; out['highlight'] = hl

# 11 wp:anchor / oMathPara / 表格
anch = len(body.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}anchor'))
inline = len(body.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'))
out['wp:anchor'] = anch; out['wp:inline'] = inline
omathpara = len(body.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara'))
out['oMathPara'] = omathpara
out['表格数'] = len(body.findall(q('tbl')))

print(json.dumps(out, ensure_ascii=False, indent=1))
