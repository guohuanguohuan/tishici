# -*- coding: utf-8 -*-
"""M配页·使用说明页图例区更新（A'改制口径H）：
[002]题号块→层级制2.4-13．（底纹盖全号）；[005]答案值分型两式样＋段落浅底F2F2F2；
[008]条目号→2.4-1．；[010]双档试字行→解析块浅底式样＋归一制说明；其余式样复验不动。
同构基准＝B/I1/I2实物run级参数（sample_real.py实测）。
"""
import copy, io, sys, zipfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return '{%s}%s' % (W, t)

DOC = '使用说明_wip.docx'
with zipfile.ZipFile(DOC) as z:
    names = z.namelist()
    contents = {n: z.read(n) for n in names}
root = etree.fromstring(contents['word/document.xml'])
body = root.find(qn('body'))
paras = body.findall(qn('p'))
assert len(paras) == 26, len(paras)

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(qn('t')))

def runs_of(p):
    return p.findall(qn('r'))

def set_rpr(r, shd=None, color=None, sz=None, bold=None):
    """在既有rPr上改/增/删 shd/color/sz/szCs/b/bCs；None=不动，'DEL'=删除。"""
    rPr = r.find(qn('rPr'))
    if rPr is None:
        rPr = etree.SubElement(r, qn('rPr'))
        r.insert(0, rPr)
    def setv(tag, val, attrs):
        el = rPr.find(qn(tag))
        if val == 'DEL':
            if el is not None: rPr.remove(el)
            return
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        for k, v in attrs.items(): el.set(qn(k), v)
    if shd is not None:
        setv('shd', shd, {'val': 'clear', 'color': 'auto', 'fill': shd} if shd != 'DEL' else {})
    if color is not None:
        setv('color', color, {'val': color} if color != 'DEL' else {})
    if sz is not None:
        setv('sz', sz, {'val': sz} if sz != 'DEL' else {})
        setv('szCs', sz, {'val': sz} if sz != 'DEL' else {})
    if bold is not None:
        setv('b', bold, {} if bold == 'DEL' else {'val': bold})
        setv('bCs', bold, {} if bold == 'DEL' else {'val': bold})

def mk_run(template, text, **kw):
    r = copy.deepcopy(template)
    for t in r.findall(qn('t')):
        r.remove(t)
    t = etree.SubElement(r, qn('t'))
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    set_rpr(r, **kw)
    return r

# ---------- [002] 题号块：层级制 ----------
p = paras[2]
assert ptext(p).startswith('1．（简单'), ptext(p)[:30]
rs = runs_of(p)
assert ''.join(t.text or '' for t in rs[0].iter(qn('t'))) == '1．'
rs[0].find(qn('t')).text = '2.4-13．'
# 说明run（最后一个18号run）
expl = rs[-1]
expl.find(qn('t')).text = ('　题号块（N6·层级制）：题号「节号-序号．（档位·提分线·卡壳看答案）」——底纹盖整个'
                           '「节号-序号．」（含节号段）、括注不挂底纹、整块加粗；序号＝节内连续、跨分卷接续；'
                           '题与题之间不留空行，靠它分隔。衔接件不区分难度、全部必会——两段式'
                           '「节号-序号．（衔接必会·卡壳看答案）」。')

# ---------- [005] 答案值分型＋解析块浅底 ----------
p = paras[5]
assert ptext(p).startswith('【答案】'), ptext(p)[:20]
# 段落浅底（w:shd 在 spacing 之前）
pPr = p.find(qn('pPr'))
assert pPr.find(qn('shd')) is None
shd_el = etree.Element(qn('shd'))
shd_el.set(qn('val'), 'clear'); shd_el.set(qn('color'), 'auto'); shd_el.set(qn('fill'), 'F2F2F2')
sp = pPr.find(qn('spacing'))
pPr.insert(list(pPr).index(sp), shd_el)
# 重建runs：模板＝现【答案】chip run（18→24）
rs = runs_of(p)
chip_tmpl = rs[0]
val_tmpl = rs[2]      # C：shd+深蓝
plain_tmpl = rs[3]    # 全角空格 plain
new_runs = [
    mk_run(chip_tmpl, '【答案】', shd='C9C9C9', sz='24'),
    mk_run(plain_tmpl, ' ', sz='24'),
    mk_run(val_tmpl, 'C', shd='C9C9C9', color='1F4E79', sz='24'),          # 文字型
    mk_run(plain_tmpl, '　', sz='24'),
    mk_run(val_tmpl, 'x²＋y²＝4', shd='DEL', color='1F4E79', sz='24'),     # 公式型
    mk_run(plain_tmpl, '　', sz='24'),
    mk_run(chip_tmpl, '【知识点】', shd='C9C9C9', sz='24'),
    mk_run(plain_tmpl, ' ', sz='24'),
    mk_run(plain_tmpl, '2.4 曲线与方程', sz='24'),
    mk_run(rs[-1], '　答案值分型（N7·A\u2032改制）：【答案】后的值按形态分型——文字型（选项字母、数值、词语，'
                   '如「C」）＝灰底C9C9C9＋深蓝#1F4E79；公式型（值内含公式，如「x²＋y²＝4」）＝不挂灰底、'
                   '纯深蓝#1F4E79；混合型（任一部分含公式）整值按公式型；需背内容同款分型。块标签芯片'
                   '（【答案】【知识点】等）只盖【×】、不加粗、黑字。', sz='18'),
]
for r in rs:
    p.remove(r)
for r in new_runs:
    p.append(r)

# ---------- [008] 条目号层级制 ----------
p = paras[8]
assert ptext(p).startswith('1．〔基〕'), ptext(p)[:20]
rs = runs_of(p)
assert ''.join(t.text or '' for t in rs[0].iter(qn('t'))) == '1．'
rs[0].find(qn('t')).text = '2.4-1．'
rs[1].find(qn('t')).text = '〔基〕曲线的方程与方程的曲线'
rs[-1].find(qn('t')).text = ('　条目号与条目第一子层：条目号「节号-序号．」（节内连续）与第一子层「（N）」同款灰底、'
                             '不加粗、只盖序号本身；〔基〕/〔进〕分类标记不挂底纹；第二子层①②③不挂。')

# ---------- [010] 双档试字行 → 解析块浅底式样＋归一制 ----------
p = paras[10]
assert '双档' in ptext(p), ptext(p)[:30]
pPr = p.find(qn('pPr'))
if pPr.find(qn('shd')) is None:
    shd_el = etree.Element(qn('shd'))
    shd_el.set(qn('val'), 'clear'); shd_el.set(qn('color'), 'auto'); shd_el.set(qn('fill'), 'F2F2F2')
    sp = pPr.find(qn('spacing'))
    pPr.insert(list(pPr).index(sp), shd_el)
rs = runs_of(p)
new_runs = [
    mk_run(rs[0], '【详解】', shd='C9C9C9', sz='24', bold='DEL'),
    mk_run(rs[0], ' ', sz='24', bold='DEL'),
    mk_run(rs[-1], '解析块浅底（第七类底纹·A\u2032改制）：带题件解析块全部段落（【答案】【知识点】标签行、'
                   '【分析】【详解】【点睛】块、【编注】【大招指引】【题后反思】【温馨提醒】、题型通式句）'
                   '整段铺#F2F2F2浅底（本段与上行【答案】行即式样）——浅底即题干与解析的区分线；题干、选项、'
                   '小问、讲部讲解正文白底，知识清单全件白底。字号行距归一（A\u2032改制）：全件正文与解析一律'
                   '小4号12pt、行距统一（旧双档字号制废止）。', sz='18', bold='DEL'),
]
for r in rs:
    p.remove(r)
for r in new_runs:
    p.append(r)

# ---------- 复验项（只断言不动）：[003]ADC2DA [004]C6D4E3 [006]pBdr [007]芯片 [009]图例句 ----------
def pshd(p):
    pPr = p.find(qn('pPr'))
    if pPr is None: return None
    e = pPr.find(qn('shd'))
    return e.get(qn('fill')) if e is not None else None
assert pshd(paras[3]) == 'ADC2DA'
assert pshd(paras[4]) == 'C6D4E3'
assert paras[6].find(qn('pPr')).find(qn('pBdr')) is not None
chips = [r for r in paras[7].findall(qn('r')) if (r.find(qn('rPr')) is not None and r.find(qn('rPr')).find(qn('shd')) is not None)]
assert len(chips) >= 9, len(chips)  # 9个【×】芯片
assert '〔基〕＝基础必会' in ptext(paras[9]) and '〔进〕＝进阶汇总' in ptext(paras[9])
# 答案用法关键句维持（[018]带底纹）
kw = paras[18]
assert ptext(kw).startswith('每题先独立读题动手')
assert (kw.findall(qn('r'))[0].find(qn('rPr')).find(qn('shd')) is not None)
# 件型用法段落[020]-[025]文字不动：记录哈希前8位
import hashlib
hashes = [hashlib.md5(ptext(paras[i]).encode()).hexdigest()[:8] for i in range(19, 26)]

contents['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = DOC + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.writestr(n, contents[n])
shutil.move(tmp, DOC)
print('使用说明图例区更新完成；复验断言全过（ADC2DA/C6D4E3/pBdr/9芯片/图例句/答案用法底纹）；')
print('件型用法段[019]-[025]未动，hash前8：', hashes)
