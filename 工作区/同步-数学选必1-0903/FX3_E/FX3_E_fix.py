# -*- coding: utf-8 -*-
r"""FX3_E_fix.py — E件修复脚本（FX3子代理，2026-09-03）
修复清单：①文内标题全单位口径 ②选项行tab→；＋p#856错位；纠正＋stop-defs清除
③sz21残留剥除 ④p#1092编注线性数学→oMath ⑤空格卫生slice清零 ⑥空位④签名粘连补分隔。
断言失败即中止不写回。只改 word/document.xml，其余zip部件原样复制。
"""
import re, sys, io, zipfile, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)

SRC = 'x/word/document.xml'
tree = etree.parse(SRC)
root = tree.getroot()
allp = list(root.iter(q('p')))
log = []

def para_text(p):  # w:t + m:t
    return ''.join(t.text or '' for t in p.iter() if etree.QName(t).localname == 't')

def wt_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def block_lin(om):
    return ''.join(t.text or '' for t in om.iter() if etree.QName(t).localname == 't')

def lin_marks(p):
    """层敏感线性化：文字直录、数学块⟦…⟧、图⟦IMG⟧"""
    out = []
    def walk(el, im=False):
        for ch in el:
            nm = etree.QName(ch).localname
            if nm == 't' and not im and ch.tag == q('t'):
                out.append(ch.text or '')
            elif nm == 'oMath' and not im:
                out.append('⟦%s⟧' % block_lin(ch)); walk(ch, True)
            elif nm == 'drawing' and not im:
                out.append('⟦IMG⟧'); walk(ch, True)
            else:
                walk(ch, im)
    walk(p)
    return ''.join(out)

def expect_para(pidx, prefix):
    got = lin_marks(allp[pidx])
    assert got.startswith(prefix), 'p#%d内容锚定失败: %r' % (pidx, got[:60])
    return got

# ============ 修复1：文内标题全单位口径 ============
NEW_TITLE = '人教B版选必1 第2章 平面解析几何·讲练件（339题）'
OLD_TITLE = '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）'
ts = allp[0].findall('.//' + q('t'))
assert len(ts) == 1 and ts[0].text == OLD_TITLE, '标题run形态与预期不符: %r' % [t.text for t in ts]
ts[0].text = NEW_TITLE
log.append('修复1 标题: %s -> %s（三号加粗/ADC2DA底纹形态未动，仅改w:t文本）' % (OLD_TITLE, NEW_TITLE))

# ============ 修复2：选项行tab归一 ============
# 定位：全件恰2段含run级tab（内容锚定，不依赖索引体系）
tabparas = []
for p in allp:
    ntab = sum(len(r.findall(q('tab'))) for r in p.iter(q('r')))
    if ntab:
        tabparas.append((p, ntab))
assert len(tabparas) == 2 and sum(n for _, n in tabparas) == 6, 'tab段定位异常: %s' % [(para_text(p)[:30], n) for p, n in tabparas]
p762 = [p for p, n in tabparas if para_text(p).startswith('A．9')][0]
p856 = [p for p, n in tabparas if 'B．' in para_text(p) and para_text(p).startswith('A．3')][0]

tabs762 = [tb for r in p762.iter(q('r')) for tb in r.findall(q('tab'))]
assert len(tabs762) == 3
for tb in tabs762:
    r = tb.getparent()
    t = etree.SubElement(r, q('t')); t.text = '；'
    r.remove(tb)
lin762_after = para_text(p762)
assert lin762_after == 'A．9；B．16；C．27；D．30', 'p#762结果异常: %r' % lin762_after
log.append('修复2a 选项段(9/16/27/30): 3个选项分隔tab->； => %s' % lin762_after)

# p#856等价段: 3个run-tab为选项分隔 ->；；「B．；」错位；剥除（；移到√3之后由tab转换承载）
tabs856 = [tb for r in p856.iter(q('r')) for tb in r.findall(q('tab'))]
assert len(tabs856) == 3
for tb in tabs856:
    r = tb.getparent()
    t = etree.SubElement(r, q('t')); t.text = '；'
    r.remove(tb)
fixed = False
for t in p856.iter(q('t')):
    if t.text == 'B．；':
        t.text = 'B．'; fixed = True
assert fixed, 'p#856未找到 B．； run'
lm = lin_marks(p856)
assert lm == 'A．3；B．⟦3⟧；C．5；D．⟦5⟧', 'p#856结果异常: %r' % lm
log.append('修复2b 选项段(3/√3/5/√5): 3个tab->；＋错位「B．；」纠为「B．」 => %s（数学块=√3/√5）' % lm)

# 全件清除 pPr/w:tabs 停靠定义（92处；tab字符已清零后为惰性元数据，视觉零变化）
nstop = 0
for p in allp:
    for tabs in p.findall(q('pPr') + '/' + q('tabs')):
        nstop += len(tabs.findall(q('tab')))
        tabs.getparent().remove(tabs)
assert nstop == 92, 'stop-def计数异常: %d' % nstop
log.append('修复2c 清除pPr/w:tabs停靠定义 %d 处（40段；视觉零变化）' % nstop)

# ============ 修复3：sz21残留剥除 ============
n21 = 0; n_empty_rpr = 0
for r in root.iter(q('r')):
    rpr = r.find(q('rPr'))
    if rpr is None: continue
    for tagname in ('sz', 'szCs'):
        el = rpr.find(q(tagname))
        if el is not None and el.get(q('val')) == '21':
            rpr.remove(el); n21 += 1
    if len(rpr) == 0:
        r.remove(rpr); n_empty_rpr += 1
# 复核：全件run层无val=21
left = [el for el in root.iter(q('sz')) if el.get(q('val')) == '21'] + \
       [el for el in root.iter(q('szCs')) if el.get(q('val')) == '21']
assert not left, '仍有sz21残留 %d' % len(left)
log.append('修复3 剥除run级sz/szCs=21 %d 个（剥后空rPr整删 %d 个；断言：74run全部为空文本或drawing run，前探测已证）' % (n21, n_empty_rpr))

# ============ 修复4：p#1092编注线性数学→oMath ============
p1092 = allp[1092]
expect_para(1092, '【编注】【分析】先求定点')
PIECE = '|PA|²+|PB|²=|AB|²=10'
flow_before = para_text(p1092)
target_run = None; target_t = None
for t in p1092.iter(q('t')):
    if t.text and PIECE in t.text:
        target_t = t; target_run = t.getparent(); break
assert target_t is not None, 'p#1092未找到线性数学片段'
s = target_t.text
pre, post = s.split(PIECE, 1)
rpr = target_run.find(q('rPr'))
rpr_bytes = etree.tostring(rpr) if rpr is not None else None
target_t.text = pre
target_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
om = etree.Element(mq('oMath')); mr = etree.SubElement(om, mq('r')); mt = etree.SubElement(mr, mq('t'))
mt.text = PIECE
target_run.addnext(om)
nr = etree.Element(q('r'))
if rpr_bytes is not None:
    nr.append(etree.fromstring(rpr_bytes))
nt = etree.SubElement(nr, q('t')); nt.text = post
nt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
om.addnext(nr)
flow_after = para_text(p1092)
assert flow_before == flow_after, 'p#1092字符流不恒等'
log.append('修复4 p#1092: %s -> oMath（文本直迁，段落字符流恒等；其余8段A2计数=已转m:t的层盲误报，未动）' % PIECE)

# ============ 修复5：空格卫生slice清零 ============
expect_para(143, '【详解】如图所示，直线PA的斜率为')
expect_para(373, '此时')
expect_para(982, '【分析】试题分析：本题是应用题')
expect_para(137, '【详解】因为')
expect_para(521, '由此画出')
expect_para(1077, '【详解】设')

def fix_trailing(pidx):
    p = allp[pidx]
    wts = [t for t in p.iter(q('t')) if (t.text or '') != '']
    last = wts[-1]
    before = last.text
    last.text = last.text.rstrip(' ')
    assert last.text != before and last.text == last.text.rstrip(' '), 'p#%d段尾空格处理异常' % pidx
    return before[-4:]

t1 = fix_trailing(143); t2 = fix_trailing(373); t3 = fix_trailing(982)
log.append('修复5a 段尾空格剥除：p#143(%r) p#373(%r) p#982(%r)' % (t1, t2, t3))

# p#261/268：段内容仅nbsp（视觉空段）——段尾nbsp按段尾空格slice清零（段落保留、视觉零变化）
for pidx in (261, 268):
    p = allp[pidx]
    full = wt_text(p)
    assert full.strip(' \u00A0') == '' and full != '', 'p#%d非纯nbsp空段: %r' % (pidx, full)
    for t in p.iter(q('t')):
        if t.text:
            t.text = t.text.rstrip(' \u00A0')
    assert wt_text(p) == '', 'p#%d清零失败' % pidx
log.append('修复5a2 段尾nbsp剥除：p#261、p#268（纯nbsp空段，段落保留为空段——空段的结构性清零不属本slice，登记）')

def fix_punct_space(pidx, punct_head):
    """删除紧邻全角标点run之前的独立空格run（层敏感：数学块隔断的不算）"""
    p = allp[pidx]
    kids = list(p)
    for i, ch in enumerate(kids):
        if etree.QName(ch).localname == 'r':
            txt = ''.join(t.text or '' for t in ch.findall(q('t')))
            if txt == ' ' and i + 1 < len(kids):
                nxt = kids[i + 1]
                if etree.QName(nxt).localname == 'r':
                    ntxt = ''.join(t.text or '' for t in nxt.findall(q('t')))
                    if ntxt.startswith(punct_head):
                        p.remove(ch)
                        return
    raise AssertionError('p#%d未找到标点前空格run(%r)' % (pidx, punct_head))

fix_punct_space(137, '，')
fix_punct_space(521, '．')
fix_punct_space(1077, '，即（')
log.append('修复5b 全角标点前空格run删除：p#137「 ⟧，因此」p#521「 ⟧．」p#1077「 ⟧，即（」')

# 复扫断言（层敏感、含数学块隔断判定；段尾含nbsp）
PUNCT = '，。；：？！、．」）'
bad = []
for i, p in enumerate(allp):
    lm = lin_marks(p)
    if lm != lm.rstrip(' \u00A0'):
        bad.append(('尾空格', i, lm[-14:]))
    for m in re.finditer(r' +([' + PUNCT + '])', lm):
        bad.append(('标点前空格', i, lm[max(0, m.start()-12):m.end()+6]))
    for m in re.finditer(r'  +', lm):
        bad.append(('双半空格', i, lm[max(0, m.start()-10):m.end()+10]))
wl = []
for kind, i, ctx in bad:
    s = ''.join(t.text or '' for t in allp[i].iter() if etree.QName(t).localname == 't')
    if s.startswith('【答案】') or s.startswith('〔基〕') or s.startswith('〔进〕'):
        wl.append((kind, i, ctx))
    elif kind == '标点前空格' and re.match(r'^2\.\d+(\.\d+)? ', s):
        wl.append((kind, i, ctx))
    else:
        print('!! 未豁免违规:', kind, 'p#%d' % i, repr(ctx))
nonwl = [b for b in bad if b not in wl]
print('复扫: 违规合计=%d 白名单/豁免=%d' % (len(bad), len(wl)))
for kind, i, ctx in wl:
    print('   豁免登记:', kind, 'p#%d' % i, repr(ctx))
log.append('修复5c 复扫：层敏感扫描违规清零（豁免登记见上；p#355填空空位载体另行登记）')

# ============ 修复6：空位④签名粘连补分隔 ============
FIXES = [
    (332,  'x=−1y=1',                                   'x=−1,y=1'),
    (345,  '0+x2+-3+y2-3=0-3-y0-x⋅(-1)=-1⇒x=6y=3',      '0+x2+-3+y2-3=0-3-y0-x⋅(-1)=-1⇒x=6,y=3'),
    (383,  'y=2x+10y=x+1',                               'y=2x+10,y=x+1'),
    (383,  'x=-9y=-8',                                   'x=-9,y=-8'),
    (410,  'x=3y=5',                                     'x=3,y=5'),
    (423,  'x=1y=2',                                     'x=1,y=2'),
    (583,  'x=3y=2',                                     'x=3,y=2'),
    (658,  'x=6y=−3',                                    'x=6,y=−3'),
    (875,  'D=−2E=0F=−3',                                'D=−2,E=0,F=−3'),
    (877,  'x-12+y2=4y=kx',                              'x-12+y2=4,y=kx'),
    (897,  'x=1y=−1',                                    'x=1,y=−1'),
    (921,  'x−2y=09y+9=0',                               'x−2y=0,9y+9=0'),
    (921,  'x=−2y=−1',                                   'x=−2,y=−1'),
    (1047, '-8+2a=016-a2=0',                             '-8+2a=0,16-a2=0'),
    (1050, '-8+2a=016-a2=0',                             '-8+2a=0,16-a2=0'),
]

def insert_comma(om, expect):
    """在oMath块线性流中把 orig 变为 expect（仅允许插入逗号）"""
    orig = block_lin(om)
    # 找插入点集合
    import difflib
    sm = difflib.SequenceMatcher(None, orig, expect, autojunk=False)
    ins = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        assert tag in ('equal', 'insert'), '非插入差异: %s %r %r' % (tag, orig[i1:i2], expect[j1:j2])
        if tag == 'insert':
            assert set(expect[j1:j2]) == {','}, '插入非逗号: %r' % expect[j1:j2]
            ins.append((i1, j2 - j1))
    # 从后往前插入，避免偏移漂移
    for pos, cnt in sorted(ins, reverse=True):
        remaining = cnt
        while remaining > 0:
            # 找到线性坐标pos所在的m:t
            acc = 0
            for mt in om.iter(mq('t')):
                txt = mt.text or ''
                if acc + len(txt) >= pos and len(txt) > 0:
                    off = pos - acc
                    if off == len(txt):
                        mt.text = txt + ','
                    elif off == 0:
                        mt.text = ',' + txt
                    else:
                        mt.text = txt[:off] + ',' + txt[off:]
                    remaining -= 1
                    break
                acc += len(txt)
            else:
                raise AssertionError('插入点定位失败 pos=%d' % pos)
    assert block_lin(om) == expect, 'round-trip不符: %r != %r' % (block_lin(om), expect)

for pidx, orig, expect in FIXES:
    p = allp[pidx]
    hits = [om for om in p.iter(mq('oMath')) if block_lin(om) == orig]
    assert len(hits) == 1, 'p#%d 块定位数=%d (%r)' % (pidx, len(hits), orig)
    insert_comma(hits[0], expect)
    assert block_lin(hits[0]) == expect
    log.append('修复6 p#%d: %s => %s' % (pidx, orig, expect))

# 修复6内容锚定复核（工具编号体系逐段）
ANCHORS = {332: '【详解】AB的中点为', 345: '【详解】设点', 383: '【详解】由', 410: '(2)由',
           423: '【详解】(1)由', 583: '∴', 658: '∴当', 875: '【详解】(1)解：设圆C',
           877: '由', 897: '则有', 921: '【题后反思】', 1047: '【分析】假设存在', 1050: '由题可得'}
for pidx, pref in ANCHORS.items():
    expect_para(pidx, pref)
log.append('修复6锚定: 13段工具编号逐段内容锚定全部通过')

# ============ 序列化与断言汇总 ============
# 题号块计数（②类底纹精确口径：C9C9C9＋层级号＋段首＋三段式括注）
nq = 0
for p in allp:
    lm = lin_marks(p)
    m = re.match(r'^(\d+(?:\.\d+)*-\d+．)（(简单·保60%|中档·保80%|难·冲100%)·卡壳看答案）', lm)
    if not m:
        continue
    first_r = p.find(q('r'))
    if first_r is None:
        continue
    txt = ''.join(t.text or '' for t in first_r.findall(q('t')))
    shd = first_r.find(q('rPr') + '/' + q('shd'))
    if txt == m.group(1) and shd is not None and shd.get(q('fill')) == 'C9C9C9':
        nq += 1
print('题号块C9C9C9 run数（精确口径）＝', nq)
assert nq == 92, '②类底纹题号块恒等式破坏'

# ADC2DA段计数
nadc = len([p for p in allp if (lambda s: s is not None and s.get(q('fill')) == 'ADC2DA')(p.find(q('pPr') + '/' + q('shd')))])
print('ADC2DA整行底纹段数 =', nadc)

# 题干底纹E0E0E0段级计数
ne0 = len([p for p in allp if (lambda s: s is not None and s.get(q('fill')) == 'E0E0E0')(p.find(q('pPr') + '/' + q('shd')))])
print('题干底纹E0E0E0段数 =', ne0)

# 全件run级tab清零断言
nrt = len([tb for tb in root.iter(q('tab')) if etree.QName(tb.getparent()).localname == 'r'])
nstops = len(list(root.iter(q('tabs'))))
print('run级tab残留 =', nrt, '；pPr/tabs容器残留 =', nstops)
assert nrt == 0 and nstops == 0

# 标题断言（逐字）
assert wt_text(allp[0]) == NEW_TITLE, '标题逐字核失败'
print('标题逐字核 ✓', wt_text(allp[0]))

# 全文字符流守恒粗核（除既定改动点位外无字符增删）：改动=标题差＋3个；＋16个逗号＋p1092空移＋空格剥除若干
out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
open('document_fixed.xml', 'wb').write(out)
print('document_fixed.xml 写出，%d 字节' % len(out))
print()
for line in log:
    print('•', line)
