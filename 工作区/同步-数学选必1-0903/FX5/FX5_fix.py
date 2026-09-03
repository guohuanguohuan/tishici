# -*- coding: utf-8 -*-
"""FX5-G 主修复脚本（终版）— 断言驱动；任一失败即中止不写回。
项1 sectPr折叠；项2 选项分隔归一(含p#754源克隆)；项3 sz21剥除；项4 编注oMath；项6 灰底缩回；项7 空格卫生。"""
import re, shutil, zipfile, os
from copy import deepcopy
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
SRC = r'C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\模块8大招7平均性质.docx'
TMP = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
XMLNS = 'http://www.w3.org/XML/1998/namespace'
def w(t): return f'{{{W}}}{t}'
def m(t): return f'{{{M}}}{t}'

parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse(DOC, parser)
root = tree.getroot()
body = root.find(w('body'))
paras = body.findall(w('p'))
assert len(paras) == 767, f'para count {len(paras)}'

log = []
def logp(s):
    log.append(s); print(s)

shutil.copy2(DOC, DOC + '.orig')

# ---------- helpers ----------
def ptext_all(p):
    out = []
    for node in p.iter():
        if node.tag == w('t') and node.text:
            out.append(node.text)
        elif node.tag == m('t') and node.text:
            out.append(node.text)
    return ''.join(out)

def text_run(p, exact):
    """find w:r whose sole w:t text == exact"""
    for r_el in p.findall(w('r')):
        ts = r_el.findall(w('t'))
        if len(ts) == 1 and ts[0].text == exact:
            return r_el, ts[0]
    raise AssertionError(f'run with text {exact!r} not found')

def make_omath(text):
    om = etree.SubElement(etree.Element('root'), m('oMath'))
    r_el = etree.SubElement(om, m('r'))
    t_el = etree.SubElement(r_el, m('t'))
    t_el.text = text
    return om

def make_omath_sub():
    """structured oMath: x_A·x_B=p²/4"""
    xml = ('<m:oMath xmlns:m="%s">'
           '<m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>A</m:t></m:r></m:sub></m:sSub>'
           '<m:r><m:t>·</m:t></m:r>'
           '<m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>B</m:t></m:r></m:sub></m:sSub>'
           '<m:r><m:t>=</m:t></m:r>'
           '<m:sSup><m:e><m:r><m:t>p</m:t></m:r></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>'
           '<m:r><m:t>/4</m:t></m:r>'
           '</m:oMath>') % M
    return etree.fromstring(xml)

def replace_run_with_omath(p, exact, omath):
    r_el, _ = text_run(p, exact)
    idx = list(p).index(r_el)
    p.remove(r_el)
    p.insert(idx, omath)

# ============ FIX 1 ============
logp('== FIX1 sectPr fold ==')
p0 = paras[0]
assert '人教B版选必1' in ptext_all(p0) and '68题' in ptext_all(p0)
sect0 = p0.find(f'{w("pPr")}/{w("sectPr")}')
assert sect0 is not None
href = sect0.find(w('headerReference')); fref = sect0.find(w('footerReference')); pgn = sect0.find(w('pgNumType'))
assert href.get(f'{{{R}}}id') == 'rId49' and fref.get(f'{{{R}}}id') == 'rId50' and pgn.get(w('start')) == '103'
all_sect = root.findall(f'.//{w("sectPr")}')
assert len(all_sect) == 2 and all_sect[0] is sect0
final_sect = all_sect[1]
assert final_sect.getparent() is body
cf = final_sect.find(w('cols'))
assert (cf.get(w('num')), cf.get(w('space')), cf.get(w('sep'))) == ('2', '425', '1')
final_sect.insert(0, deepcopy(href))
final_sect.insert(1, deepcopy(fref))
final_sect.find(w('pgMar')).addnext(deepcopy(pgn))
body.remove(p0)
logp('FIX1: 段[0]标题删除；rId49/rId50/pgNumType(start=103)并入正文末sectPr；cols=2/425/1保留')

# ============ FIX 2 ============
logp('== FIX2 option separators ==')
assert len(body.findall(w('p'))) == 766

def fix_tabs_in_para(p, idx):
    ch = {'r1': 0, 'r2': 0, 'r3': 0}
    for t in p.iter(w('t')):
        if t.text == '．；':  # 选项点后错位；（标记run与字母run分立形态）
            t.text = '．'
            ch['r3'] += 1
    for r_el in list(p.findall(w('r'))):
        for tab in list(r_el.findall(w('tab'))):
            after = False; nxt = None
            for node in p.iter():
                if node is tab:
                    after = True; continue
                if after:
                    if node.tag == w('tab'):
                        break
                    if node.tag == w('t') and (node.text or '').strip():
                        nxt = node; break
            assert nxt is not None, f'p#{idx} tab no following text'
            if nxt.text.startswith('；'):
                tab.getparent().remove(tab); ch['r1'] += 1
            elif re.match(r'^[B-D]([．.]|$)', nxt.text):
                nxt.text = '；' + nxt.text
                tab.getparent().remove(tab); ch['r2'] += 1
            else:
                raise AssertionError(f'p#{idx} tab followed by {nxt.text[:12]!r}')
    return ch

tot = {'r1': 0, 'r2': 0, 'r3': 0}
for idx in (23, 29, 58, 152, 168, 202, 214, 228, 260, 311, 317, 423, 440, 461, 622, 646, 569, 578, 586, 613, 636, 694, 714):
    c = fix_tabs_in_para(paras[idx], idx)
    for k in tot: tot[k] += c[k]
assert tot == {'r1': 54, 'r2': 12, 'r3': 10}, f'tab totals {tot}'
logp(f'tab fixes: R1(del tab before ；)={tot["r1"]} R2(tab→；)={tot["r2"]} R3(rm misplaced X．；)={tot["r3"]}')

# p#516
p = paras[516]
for t in p.iter(w('t')):
    if t.text == '12 B': t.text = '12；B'
    elif t.text == '．；': t.text = '．'
    elif t.text == ' D': t.text = '；D'
c = fix_tabs_in_para(p, 516)
assert c == {'r1': 0, 'r2': 1, 'r3': 0}, f'p516 {c}'
assert ptext_all(p).count('；') == 3
logp('p#516: 题干内嵌选项分隔归一（12；B／B．；纠位／tab→；／；D）')

# p#246/275 nbsp（合并run与独立run两形态）
for idx in (246, 275):
    n = 0
    ts = [t for t in paras[idx].iter(w('t'))]
    for j, t in enumerate(ts):
        txt = t.text or ''
        if re.match(r'^\xa0+[B-D]$', txt):  # 合并形态：\xa0…B
            t.text = '；' + txt[-1]; n += 1
        elif txt and txt.strip() == '' and '\xa0' in txt:  # 独立nbsp run，后随标记字母run
            nk = None
            for k in range(j + 1, len(ts)):
                if (ts[k].text or '').strip():
                    nk = ts[k].text; break
            if nk and re.match(r'^[B-D]$', nk):
                t.text = '；'; n += 1
    assert n == 3, f'p#{idx} {n}'
logp('p#246/275: 选项间nbsp串→；×6')

# p#728
n = 0
for t in paras[728].iter(w('t')):
    if t.text == 'A.': t.text = 'A．'; n += 1
    elif t.text and re.match(r'^\d+[\xa0 ]+[B-D]\.$', t.text):
        mm = re.match(r'^(\d+)[\xa0 ]+([B-D])\.$', t.text)
        t.text = f'{mm.group(1)}；{mm.group(2)}．'; n += 1
assert n == 4
logp('p#728: 半角选项点A.→A．＋nbsp分隔→；×3')

# p#743
n = 0
for t in paras[743].iter(w('t')):
    if t.text == 'A.': t.text = 'A．'; n += 1
    elif t.text and re.match(r'^\xa0{2,}B\.$', t.text): t.text = '；B．'; n += 1
    elif t.text and re.match(r'^\xa0{2,}C\.4\xa0{2,}D\.12$', t.text): t.text = '；C．4；D．12'; n += 1
assert n == 3
logp('p#743: 图选项半角点归一＋nbsp→；')

# p#672
p = paras[672]
ts = [t for t in p.iter(w('t'))]
filled = 0
for j, t in enumerate(ts):
    if (t.text is None or t.text == ''):
        # next non-empty
        nk = None
        for k in range(j + 1, len(ts)):
            if (ts[k].text or '').strip():
                nk = ts[k].text; break
        if nk and re.match(r'^[B-D]$', nk):
            t.text = '；'; filled += 1
assert filled == 2, f'p672 filled {filled}'
_, tc = text_run(p, 'C')
tc.text = '；C'
logp('p#672: 长句选项粘连补；×3（A|B、B|C、C|D边界）')

# p#754 source clone
with zipfile.ZipFile(SRC) as z:
    sxml = z.read('word/document.xml')
sroot = etree.fromstring(sxml)
sparas = sroot.find(w('body')).findall(w('p'))
def om_from(sp_idx):
    return [deepcopy(om) for om in sparas[sp_idx].iter(m('oMath'))]
srcB, srcC, srcD = om_from(61), om_from(62), om_from(63)
assert len(srcB) == 2 and len(srcC) == 1 and len(srcD) == 2
for om in srcB + srcC + srcD:
    for rf in om.findall(f'.//{w("rFonts")}'):
        rf.attrib.pop(w('eastAsia'), None)
p = paras[754]
def settext(p, old, new):
    n = 0; tt = None
    for t in p.iter(w('t')):
        if t.text == old:
            t.text = new; n += 1; tt = t
    assert n == 1, f'settext {old!r} found {n}'
    return tt
def clone_text_run(tmpl_t, text):
    nr = deepcopy(tmpl_t.getparent())
    nt = nr.findall(w('t'))[0]
    nt.text = text
    nt.attrib.pop(f'{{{XMLNS}}}space', None)
    return nr
# B段: '坐标为，则' → '坐标为' + om(0,−1/2) + '，则' + om(AM·BM=0) + '；'
t8 = settext(p, '坐标为，则', '坐标为')
idx8 = list(p).index(t8.getparent())
p.insert(idx8 + 1, srcB[0])
p.insert(idx8 + 2, clone_text_run(t8, '，则'))
p.insert(idx8 + 3, srcB[1])
p.insert(idx8 + 4, clone_text_run(t8, '；'))
# C段: '．；' → '．' + om(|OA|+|OB|>√5) + '；'
t10 = settext(p, '．；', '．')
idx10 = list(p).index(t10.getparent())
p.insert(idx10 + 1, srcC[0])
p.insert(idx10 + 2, clone_text_run(t10, '；'))
# D段1: '．若垂直抛物线准线于点' → '．若' + om(BN) + '垂直抛物线准线于点'
t12 = settext(p, '．若垂直抛物线准线于点', '．若')
idx12 = list(p).index(t12.getparent())
p.insert(idx12 + 1, srcD[0])
p.insert(idx12 + 2, clone_text_run(t12, '垂直抛物线准线于点'))
# D段2: '，则三点在一条直线上' → '，则' + om(A,O,N) + '三点在一条直线上'
t14 = settext(p, '，则三点在一条直线上', '，则')
idx14 = list(p).index(t14.getparent())
p.insert(idx14 + 1, srcD[1])
p.insert(idx14 + 2, clone_text_run(t14, '三点在一条直线上'))
# A|B边界空run → '；'
for r_el in p.findall(w('r')):
    tsx = r_el.findall(w('t'))
    if len(tsx) == 1 and (tsx[0].text is None or tsx[0].text == ''):
        tsx[0].text = '；'; break
else:
    raise AssertionError('p754 boundary empty run not found')
expect = ('A．抛物线在点x=1处切线方程为2x-2y-1=0；B．若点M坐标为0,−12，则AM⋅BM=0；'
          'C．OA+OB>5；D．若BN垂直抛物线准线于点N，则A,O,N三点在一条直线上')
assert ptext_all(p) == expect, f'p754:\n{ptext_all(p)!r}'
logp('p#754: B/C/D装配丢式源克隆修复（OMML自大招7源逐字克隆）＋分隔；×3')

# pPr tabs defs
n_def = 0
for pp in body.findall(w('p')):
    pPr = pp.find(w('pPr'))
    if pPr is None: continue
    tw = pPr.find(w('tabs'))
    if tw is not None:
        n_def += len(tw.findall(w('tab')))
        pPr.remove(tw)
assert n_def == 63
n_run_tab = sum(len(r.findall(w('tab'))) for pp in body.findall(w('p')) for r in pp.findall(w('r')))
assert n_run_tab == 0
logp(f'pPr w:tabs停靠定义清除{ n_def }（run级tab=0 ✓）')

# ============ FIX 3 ============
logp('== FIX3 sz21 ==')
n21 = 0
for rPr in root.findall(f'.//{w("rPr")}'):
    for el in list(rPr):
        if el.tag in (w('sz'), w('szCs')) and el.get(w('val')) == '21':
            rPr.remove(el); n21 += 1
assert n21 == 84, f'{n21}'
n_left = sum(1 for rPr in root.findall(f'.//{w("rPr")}') for el in rPr
             if el.tag in (w('sz'), w('szCs')) and el.get(w('val')) == '21')
assert n_left == 0
logp('sz/szCs=21剥除84元素（42run全为空run/图run/渲染缓存run——视觉零变化）')

# ============ FIX 4 ============
logp('== FIX4 编注oMath ==')
# p#166
p = paras[166]
for frag in ('|MA|²+|MB|²', '2|MO|²+½|AB|²', '|MO|', '|AB|', '2a'):
    replace_run_with_omath(p, frag, make_omath(frag))
logp('p#166: 5表达式文本直迁oMath')

# p#234
p = paras[234]
replace_run_with_omath(p, 'b/a=tanθ', make_omath('b/a=tanθ'))
t_frag = None
for t in p.iter(w('t')):
    if t.text == '/a)²': t_frag = t; break
assert t_frag is not None
target_mt = None
for mt in p.iter(m('t')):
    if mt.text == 'e²=1+(b': target_mt = mt; break
assert target_mt is not None
target_mt.text = 'e²=1+(b/a)²'
run_f = t_frag.getparent()
run_f.remove(t_frag)  # 同run内还有OM(e²=1+(b)，仅移除w:t
logp('p#234: b/a=tanθ转oMath；乱序碎片/a)²并回e²=1+(b/a)²（顺序复位）')

# p#301
p = paras[301]
for frag in ('P(x,y)', '|x|≥a', '|c−a|'):
    replace_run_with_omath(p, frag, make_omath(frag))
logp('p#301: 3表达式文本直迁oMath')

# p#324
p = paras[324]
replace_run_with_omath(p, '|PO|²', make_omath('|PO|²'))
# 断链碎片：单run内 T'|P'+OM(F₁)+嵌套r+OM(F₂) → 重建 |PF₁||PF₂|
rP, _ = text_run(p, '|P')
oms = rP.findall(m('oMath'))
assert oms and [''.join(x.text or '' for x in om.iter(m('t'))) for om in oms] == ['F₁', 'F₂'], 'p324 om layout'
idxP = list(p).index(rP)
p.remove(rP)
p.insert(idxP, make_omath('|PF₁||PF₂|'))
logp('p#324: |PO|²转oMath；|P＋F₁＋F₂断链碎片重建为|PF₁||PF₂|（等轴双曲线恒等式|PF₁||PF₂|=|PO|²亲算核验）')

# p#726
p = paras[726]
rX, _ = text_run(p, 'x_A·x_B=')
oms = rX.findall(m('oMath'))
assert oms and ''.join(x.text or '' for x in oms[0].iter(m('t'))) == 'p²', 'p726 om layout'
idxX = list(p).index(rX)
p.remove(rX)
p.insert(idxX, make_omath_sub())
mt_all = ''.join(x.text or '' for x in paras[726].iter(m('t')))
assert 'p' in mt_all and '/4' in mt_all, 'p726 rebuild'
logp('p#726: x_A·x_B=p²重建为结构化oMath（sSub真下标）并纠值为p²/4（平均性质焦点弦m=p/2）')

# p#744
p = paras[744]
replace_run_with_omath(p, 'M(0,2)', make_omath('M(0,2)'))
t_oa = None
for t in p.iter(w('t')):
    if t.text == 'OA·': t_oa = t; break
assert t_oa is not None
mt_ob = None
for mt in p.iter(m('t')):
    if mt.text == 'OB=x₁x₂+y₁y₂=−4': mt_ob = mt; break
assert mt_ob is not None
mt_ob.text = 'OA·OB=x₁x₂+y₁y₂=−4'
run_oa = t_oa.getparent()
run_oa.remove(t_oa)  # 同run内保留OM(OB=…)
logp('p#744: M(0,2)转oMath；OA·碎片并入OA·OB=…oMath')

# w:t层签名复扫（6段）
sig = re.compile(r'[√½¼¾²³¹∠⊥∈∩∪≈≤≥≠±⋅·×₀-₉]|_')
for idx in (166, 234, 301, 324, 726, 744):
    wt = ''.join(t.text or '' for t in paras[idx].iter(w('t')))
    hits = sig.findall(wt)
    assert not hits, f'p#{idx} residual {hits}'
logp('编注6段 w:t层线性数学签名复扫=0 ✓')

# ============ FIX 6 ============
logp('== FIX6 灰底缩回 ==')
def unshade(p, texts):
    """remove C9C9C9 shd from runs whose w:t text is in texts (count all occurrences)"""
    done = {}
    for t in p.iter(w('t')):
        if t.text in texts:
            r_el = t.getparent()
            rPr = r_el.find(w('rPr'))
            if rPr is not None:
                shd = rPr.find(w('shd'))
                if shd is not None and shd.get(w('fill')) == 'C9C9C9':
                    rPr.remove(shd)
                    done[t.text] = done.get(t.text, 0) + 1
    return done

# 纯标点run去灰
for idx, texts in ((135, {'．'}), (140, {'.'}), (360, {'．'}), (392, {'.'})):
    d = unshade(paras[idx], texts)
    assert sum(d.values()) == 1, f'p#{idx} unshade {d}'

# p#182 叙述词+句号
d = unshade(paras[182], {'实轴长为', '，虚轴的长为', '，顶点的坐标', '和', '。'})
assert d == {'实轴长为': 1, '，虚轴的长为': 1, '，顶点的坐标': 1, '和': 1, '。': 1}, f'p182 {d}'
# p#447 叙述词+分隔逗号
d = unshade(paras[447], {'桥拱所在的抛物线方程为', '，溢流孔所在的抛物线方程分别为', '，', '，桥拱交点', '的坐标为', '．'})
assert d.get('，') == 5 and d.get('的坐标为') == 3 and d.get('．') == 1 and d.get('桥拱所在的抛物线方程为') == 1 \
    and d.get('，溢流孔所在的抛物线方程分别为') == 1 and d.get('，桥拱交点') == 1, f'p447 {d}'
logp('p#135/140/182/360/392/447: 分隔标点与叙述词run去灰（值本体与OMML整块保留）')

# 尾句点随值run拆分
def split_trailing_period(p, old):
    r_el, t_el = text_run(p, old)
    rPr = r_el.find(w('rPr'))
    shd = rPr.find(w('shd'))
    assert shd is not None and shd.get(w('fill')) == 'C9C9C9'
    t_el.text = old[:-1]
    nr = deepcopy(r_el)
    nt = nr.findall(w('t'))[0]
    nt.text = old[-1]
    nt.attrib.pop(f'{{{XMLNS}}}space', None)
    nrPr = nr.find(w('rPr'))
    ns = nrPr.find(w('shd'))
    if ns is not None: nrPr.remove(ns)
    r_el.addnext(nr)
for idx, old in ((91, '3.'), (236, '2.'), (326, '证明见解析.')):
    split_trailing_period(paras[idx], old)
logp('p#91/236/326: 值内尾句点拆出灰底（3.→3＋.；2.→2＋.；证明见解析.→…＋.）')

# ============ FIX 7 ============
logp('== FIX7 空格卫生 ==')
FWP = '，。；：？！、）．'
nsp = 0
for idx in (104, 262, 263, 266, 267, 268, 290, 296):
    p = paras[idx]
    ts = [t for t in p.iter(w('t'))]
    for j, t in enumerate(ts):
        txt = t.text or ''
        if txt and txt.strip() == '' and '\xa0' not in txt:  # half-space-only run
            nk = None
            for k in range(j + 1, len(ts)):
                if (ts[k].text or '').strip():
                    nk = ts[k].text; break
                if ts[k].text and '\xa0' in ts[k].text:
                    break
            if nk and nk[0] in FWP:
                r_el = t.getparent()
                if r_el.findall(w('t')) == [t]:
                    r_el.getparent().remove(r_el)
                else:
                    r_el.remove(t)
                nsp += 1
logp(f'标点前空格run删除: {nsp}（8段，层敏感复扫；答题位nbsp白名单未动）')
assert 12 <= nsp <= 16, f'nsp {nsp}'

tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
with open(os.path.join(TMP, 'fx5_fix_log.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))
print('\nALL FIXES APPLIED & SAVED — see fx5_fix_log.txt')
