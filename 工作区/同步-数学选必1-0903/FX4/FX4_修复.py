# -*- coding: utf-8 -*-
"""FX4-F 修复脚本：F件（选必1第2章 讲练 2.3.4—2.5.2·90题）
修复1 删段[0]文内标题＋sectPr折叠；修复2 选项行tab/nbsp归一「；」＋[399]C/D源克隆补齐；
修复3 编注线性数学→oMath（4段5处+合并半转换式）；修复4 [858]图段移至[851]后；
修复6 空格卫生4段。全部按原树元素引用操作。输出 word/document.xml 新版。"""
import copy
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
ns = {'w': W, 'm': M}
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)

tree = etree.parse('F_unzip/word/document.xml')
root = tree.getroot()
body = root.find('w:body', ns)
paras = body.findall('w:p', ns)
assert len(paras) == 1066, len(paras)

# ---------- 元素引用快照（原索引） ----------
P = {i: paras[i] for i in (0, 100, 102, 117, 163, 176, 176, 181, 202, 321, 338, 375,
                           399, 519, 500, 501, 787, 800, 858, 851,
                           76, 271, 321, 333, 427, 453, 482, 489, 542, 614, 622,
                           643, 719, 761, 781, 793, 798, 845, 938, 1006)}

def runs(p):
    return [c for c in p if etree.QName(c).localname == 'r']

def direct_children(p):
    return list(p)

def make_text_run(text, style_run):
    """新建 w:r（rPr 克隆自 style_run），含 w:t text。"""
    r = etree.Element(q('r'))
    rpr = style_run.find(q('rPr'))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, q('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return r

def make_omath(text):
    """库内既定形态：oMath > r > t（文本直迁，同段[800]先例）。"""
    om = etree.Element(mq('oMath'))
    mr = etree.SubElement(om, mq('r'))
    mt = etree.SubElement(mr, mq('t'))
    mt.text = text
    return om

def find_text_run(p, exact=None, contains=None):
    for r in runs(p):
        for t in r.findall(q('t')):
            v = t.text or ''
            if exact is not None and v == exact: return r, t
            if contains is not None and contains in v: return r, t
    raise KeyError((exact, contains))

def replace_tab_with(r_run, tab_el, p, text='；'):
    """把 run 内 w:tab 换成 w:t text（rPr 不动）。"""
    idx = list(r_run).index(tab_el)
    r_run.remove(tab_el)
    t = etree.Element(q('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    r_run.insert(idx, t)

def drop_tab(r_run, tab_el):
    r_run.remove(tab_el)
    # run 内无内容子元素则整 run 删
    content = [c for c in r_run if etree.QName(c).localname not in ('rPr',)]
    if not content:
        r_run.getparent().remove(r_run)

def strip_stops(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return
    for st in ppr.findall(q('tabs')):
        ppr.remove(st)

log = []

# ---------- 修复2：选项行归一（先做，索引无关） ----------
def fix_option_para(i, tab_ops, text_fixes):
    """tab_ops: 序列，元素 'D'=删tab / 'S'=tab→'；'（按文档序对应段内tab）；
    text_fixes: list of (old, new) 对段内 w:t 精确替换。"""
    p = P[i]
    tabs = []
    for r in runs(p):
        for tb in r.findall(q('tab')):
            tabs.append((r, tb))
    assert len(tabs) == len(tab_ops), (i, len(tabs), len(tab_ops))
    for (r, tb), op in zip(tabs, tab_ops):
        if op == 'S': replace_tab_with(r, tb, p)
        else: drop_tab(r, tb)
    for old, new in text_fixes:
        done = False
        for r in runs(p):
            for t in r.findall(q('t')):
                if (t.text or '') == old:
                    t.text = new; done = True; break
            if done: break
        assert done, (i, old)
    strip_stops(p)
    log.append(f"修复2 [{i}] tabs={''.join(tab_ops) or '-'} text_fixes={len(text_fixes)}")

fix_option_para(163,  ['S','S'], [('A．；','A．'), ('C．；','C．')])
fix_option_para(202,  ['S','S'], [('A．；','A．'), ('C．；','C．')])
fix_option_para(321,  ['S','S','S'], [('A．；','A．'), ('B．；','B．'), ('C．；','C．')])
fix_option_para(375,  ['S','D'], [('．；','．')])
fix_option_para(427,  ['D','D','D'], [])
fix_option_para(453,  ['D','D','D'], [])
fix_option_para(482,  ['S','S','S'], [('A．；','A．'), ('B．；','B．'), ('C．；','C．')])
fix_option_para(489,  ['S','S','S'], [('A．；','A．'), ('B．；','B．'), ('C．；','C．')])
fix_option_para(500,  ['S'], [])
fix_option_para(501,  ['S'], [('C．；','C．')])
fix_option_para(542,  ['S','S','S'], [('A．；','A．'), ('B．；','B．'), ('C．；','C．')])
fix_option_para(614,  ['D','D','D'], [])
fix_option_para(622,  ['D','D','D'], [])
fix_option_para(643,  ['D','D','D'], [])
fix_option_para(719,  ['D','D','D'], [])
fix_option_para(761,  ['D','D','D'], [])
fix_option_para(781,  ['S','S','S'], [])
fix_option_para(793,  ['D','D','D'], [])
fix_option_para(798,  ['D','D','D'], [])
fix_option_para(845,  ['D','D','D'], [])
fix_option_para(938,  ['S','S','S'], [])
fix_option_para(1006, ['S','S','S'], [('A．；','A．'), ('C．；','C．')])
# [399] 特殊：tab归一 + C/D 空值从源克隆补齐（后置处理，先做tab与文字）
fix_option_para(399,  ['S','S'], [('A．；','A．'), ('C．；','C．')])
# 无run-tab但有tab停止定义的选项段：仅清 stops
for i in (76, 271, 333):
    strip_stops(P[i]); log.append(f"修复2 [{i}] stops清除")

# [117] nbsp 分隔 → 「；」
p117 = P[117]
n_nbsp = 0
for r in runs(p117):
    for t in r.findall(q('t')):
        if (t.text or '') == '\u00a0\u00a0\u00a0\u00a0':
            t.text = '；'; n_nbsp += 1
assert n_nbsp == 3, n_nbsp
strip_stops(p117)
log.append("修复2 [117] nbsp×3→『；』")

# ---------- 修复2b：[399] C/D 选项值从源克隆 ----------
import zipfile as _zf
_src_path = r"C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\模块8大招2动点问题处理策略（解题大招）.docx"
src = etree.fromstring(_zf.ZipFile(_src_path).read('word/document.xml')).getroottree()
sbody = src.getroot().find('w:body', ns)
sparas = sbody.findall('.//w:p', ns)
def sft(p):
    return ''.join(t.text or '' for t in p.iter() if t.tag in (q('t'), mq('t')))
tgt = None
for k, sp in enumerate(sparas):
    if sft(sp).startswith('C．'):
        tgt = sp; break
assert tgt is not None
src_oms = tgt.findall('.//m:oMath', ns)
assert len(src_oms) == 2, len(src_oms)
c_math = copy.deepcopy(src_oms[0])   # x²/16+y²/15=1
d_math = copy.deepcopy(src_oms[1])   # x²/4+y²/3=1，x≠−2
p399 = P[399]
# 定位插入点：t'C．' 所在 run 后、t'D．' 所在 run 后
anch_c = find_text_run(p399, exact='C．')[0]
anch_d = find_text_run(p399, exact='D．')[0]
anch_c.addnext(c_math)
anch_d.addnext(d_math)
log.append("修复2b [399] C/D源克隆补齐 C=x²/16+y²/15=1 D=x²/4+y²/3=1,x≠−2")

# ---------- 修复3：编注线性数学→oMath ----------
# [102] "√2"
p = P[102]
r, t = find_text_run(p, contains='定长√2')
frag = '√2'
i0 = t.text.index(frag)
before, after = t.text[:i0], t.text[i0+len(frag):]
r_parent = p
pos = list(p).index(r)
# 拆三段：文字run(前) + oMath + 文字run(后)
t.text = before
om = make_omath(frag)
r2 = make_text_run(after, r) if after else None
p.insert(pos+1, om)
if r2 is not None: p.insert(pos+2, r2)
log.append("修复3 [102] 『√2』→oMath")

# [176] "∠OMF=90°"
p = P[176]
r, t = find_text_run(p, contains='∠OMF=90°')
frag = '∠OMF=90°'
i0 = t.text.index(frag)
before, after = t.text[:i0], t.text[i0+len(frag):]
pos = list(p).index(r)
t.text = before
om = make_omath(frag)
p.insert(pos+1, om)
if after:
    p.insert(pos+2, make_text_run(after, r))
log.append("修复3 [176] 『∠OMF=90°』→oMath")

# [519] "r1·r2=(c−a)²"
p = P[519]
r, t = find_text_run(p, contains='(c−a)²')
frag = 'r1·r2=(c−a)²'
i0 = t.text.index(frag)
before, after = t.text[:i0], t.text[i0+len(frag):]
pos = list(p).index(r)
t.text = before
om = make_omath(frag)
p.insert(pos+1, om)
if after:
    p.insert(pos+2, make_text_run(after, r))
log.append("修复3 [519] 『r1·r2=(c−a)²』→oMath")

# [800] ①拍平嵌套run（外层w:r内嵌w:r/oMath——历史工具产物，Word容忍；拍平为零视觉变化）
#      ②"|PM|²=|PA|²−|AM|²=|PA|²−1"→oMath ③"√3"→oMath ④合并 /25+ 与 /16=1 完成半转换式
p = P[800]
outer = [c for c in p if etree.QName(c).localname == 'r']
big = outer[2]  # 第三个run＝嵌套大run
assert any(etree.QName(c).localname == 'r' for c in big), '非预期：[800]第三run无嵌套'
pos = list(p).index(big)
lifted = list(big)
for j, ch in enumerate(lifted):
    p.insert(pos + j, ch)
p.remove(big)
# 若拍平后某 oMath 父级为 w:r（非），确认均为 p 直接子级
assert all(etree.QName(c.getparent()).localname == 'p'
           for c in p if etree.QName(c).localname in ('r', 'oMath'))
frag1 = '|PM|²=|PA|²−|AM|²=|PA|²−1'
r, t = None, None
for rr in runs(p):
    for tt in rr.findall(q('t')):
        if frag1 in (tt.text or ''): r, t = rr, tt; break
assert t is not None
i0 = t.text.index(frag1)
before, after = t.text[:i0], t.text[i0+len(frag1):]
pos = list(p).index(r)
t.text = before
om = make_omath(frag1)
p.insert(pos+1, om)
tail_r = make_text_run(after, r) if after else None
if tail_r is not None: p.insert(pos+2, tail_r)

# "√3" 在尾部文字 run（tail 或原 run）
frag2 = '√3'
found = False
for rr in runs(p):
    for tt in rr.findall(q('t')):
        if frag2 in (tt.text or ''):
            i0 = tt.text.index(frag2)
            b2, a2 = tt.text[:i0], tt.text[i0+len(frag2):]
            tt.text = b2
            rr.addnext(make_omath(frag2))
            if a2:
                rr.addnext(make_text_run(a2, rr))  # 紧跟 oMath 之后
            found = True
            break
    if found: break
assert found

# 合并半转换式：oMath(x²)+t"/25+"+oMath(y²)+t"/16=1的右焦点…" → 单oMath
oms = [c for c in p if etree.QName(c).localname == 'oMath']
def omtext(om): return ''.join(x.text or '' for x in om.iter(mq('t')))
x_om = next(o for o in oms if omtext(o) == 'x²')
y_om = next(o for o in oms if omtext(o) == 'y²')
slash25_run = next(o1 for o1 in runs(p) if (o1.find(q('t')) is not None and (o1.find(q('t')).text or '') == '/25+'))
# "/16=1的右焦点…" run：拆出"/16=1"并入
r16 = None
for rr in runs(p):
    tt = rr.find(q('t'))
    if tt is not None and (tt.text or '').startswith('/16=1'):
        r16, t16 = rr, tt; break
assert r16 is not None
rest16 = t16.text[len('/16=1'):]
# x_om 内追加 m:r "/25+"，再把 y_om 的 m:r 移入，再追加 "/16=1"
def add_mr(om, text):
    mr = etree.SubElement(om, mq('r')); mt = etree.SubElement(mr, mq('t')); mt.text = text
add_mr(x_om, '/25+')
for child in list(y_om):
    x_om.append(child)
body_p_index = list(p).index(y_om)
p.remove(y_om)
add_mr(x_om, '/16=1')
# 删 "/25+" run
p.remove(slash25_run)
# "/16=1…" run 文字改剩余部分
if rest16:
    t16.text = rest16
else:
    p.remove(r16)
log.append("修复3 [800] |PM|²链→oMath；√3→oMath；x²/25+y²/16=1合并为单oMath")

# ---------- 修复4：[858]图段移至[851]后 ----------
p858, p851 = P[858], P[851]
body.remove(p858)
idx851 = list(body).index(p851)
body.insert(idx851+1, p858)
log.append("修复4 [858]图段(image24,A₁A₂FO椭圆图)移至[851]『解：如图所示，』后")

# ---------- 修复6：空格卫生 ----------
# [100] 双半空格答题位 → nbsp×4
p = P[100]
sp_runs = [rr for rr in runs(p) if (rr.find(q('t')) is not None and (rr.find(q('t')).text or '') == ' ')]
assert len(sp_runs) == 2, len(sp_runs)
sp_runs[0].find(q('t')).text = '\u00a0\u00a0'
sp_runs[1].find(q('t')).text = '\u00a0\u00a0'
log.append("修复6 [100] 答题位双半空格→nbsp×4")

# [181] '. '→'.'
p = P[181]
for rr in runs(p):
    for tt in rr.findall(q('t')):
        if (tt.text or '') == '. ':
            tt.text = '.'; log.append("修复6 [181] 段尾空格清除"); break

# [338] 尾 run ' ' → 删
p = P[338]
prs = runs(p)
last_t = None
for rr in prs:
    for tt in rr.findall(q('t')):
        last_t = (rr, tt)
if last_t and (last_t[1].text or '') == ' ':
    p.remove(last_t[0]); log.append("修复6 [338] 段尾空格run删除")

# [787] 尾 run ' ' → 删
p = P[787]
prs = runs(p)
last_t = None
for rr in prs:
    for tt in rr.findall(q('t')):
        last_t = (rr, tt)
if last_t and (last_t[1].text or '') == ' ':
    p.remove(last_t[0]); log.append("修复6 [787] 段尾空格run删除")

# ---------- 修复1：删段[0]标题＋sectPr折叠（最后做） ----------
p0 = P[0]
assert '讲练件（90题）' in ''.join(t.text or '' for t in p0.iter(q('t')))
body.remove(p0)

sect = body.find(q('sectPr'))
assert sect is not None
# 子元素整体重排为 schema 序：headerReference, footerReference, pgSz, pgMar, pgNumType, cols, docGrid
XMLNS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
href = etree.Element(q('headerReference')); href.set(q('type'), 'default'); href.set('{%s}id' % XMLNS_R, 'rId305')
fref = etree.Element(q('footerReference')); fref.set(q('type'), 'default'); fref.set('{%s}id' % XMLNS_R, 'rId9')
pgn = etree.Element(q('pgNumType')); pgn.set(q('start'), '50')
order = ['headerReference', 'footerReference', 'pgSz', 'pgMar', 'pgNumType', 'cols', 'docGrid']
keep = {}
for ch in list(sect):
    ln = etree.QName(ch).localname
    if ln in order:
        keep[ln] = ch
        sect.remove(ch)
    else:
        raise AssertionError('未预期的sectPr子元素: ' + ln)
keep['headerReference'] = href
keep['footerReference'] = fref
keep['pgNumType'] = pgn
for name in order:
    sect.append(keep[name])
log.append("修复1 段[0]文内标题删除；headerRef(rId305)/footerRef(rId9)/pgNumType start=50并入正文末sectPr（cols=2/425/1原样）")

# ---------- 序列化 ----------
out = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
open('F_unzip/word/document.xml.new', 'wb').write(out)
print("OK, new document.xml bytes:", len(out))
for line in log:
    print(" -", line)
