# -*- coding: utf-8 -*-
"""FX5-G FIX4b: 编注断链碎片修复第二批（扩展签名9段：20/35/45/158/178/211/243/247/276）"""
import re
from copy import deepcopy
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return f'{{{W}}}{t}'
def m(t): return f'{{{M}}}{t}'

parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse(DOC, parser)
root = tree.getroot()
body = root.find(w('body'))
paras = body.findall(w('p'))

def make_omath(text):
    om = etree.Element(m('oMath'))
    r_el = etree.SubElement(om, m('r'))
    t_el = etree.SubElement(r_el, m('t'))
    t_el.text = text
    return om

def om_text(om):
    return ''.join(x.text or '' for x in om.iter(m('t')))

def replace_hybrid(p, lead_text, om_texts, new_math, occurrence=1):
    """replace run whose first w:t==lead_text and following inline oMath texts==om_texts with single oMath"""
    n_seen = 0
    for r_el in list(p.findall(w('r'))):
        ts = r_el.findall(w('t'))
        if ts and ts[0].text == lead_text:
            oms = r_el.findall(f'.//{m("oMath")}')  # 含嵌套r内的oMath（历史工具嵌套run形态）
            got = [om_text(o) for o in oms]
            if got == om_texts:
                n_seen += 1
                if n_seen < occurrence:
                    continue
                idx = list(p).index(r_el)
                p.remove(r_el)
                p.insert(idx, make_omath(new_math))
                return
    raise AssertionError(f'hybrid not found: {lead_text!r} + {om_texts}')

def replace_text_run(p, old, new_math):
    for r_el in list(p.findall(w('r'))):
        ts = r_el.findall(w('t'))
        if len(ts) == 1 and ts[0].text == old:
            idx = list(p).index(r_el)
            p.remove(r_el)
            p.insert(idx, make_omath(new_math))
            return
    raise AssertionError(f'text run not found: {old!r}')

log = []
# p#20
p = paras[20]
replace_hybrid(p, '||P', ['F₁', 'F₂'], '||PF₁|−|PF₂||=2a')
replace_text_run(p, '2a', '2a')
replace_text_run(p, 'a+c', 'a+c')
log.append('p#20: ||PF₁|−|PF₂||=2a重建＋2a/a+c转oMath')

# p#35
p = paras[35]
replace_hybrid(p, 'S=½|P', ['F₁', 'F₂'], 'S=½|PF₁||PF₂|')
replace_text_run(p, '2a', '2a')
log.append('p#35: S=½|PF₁||PF₂|重建（直角焦点三角形面积）＋2a转oMath')

# p#45
p = paras[45]
replace_text_run(p, 'm−n=6', 'm−n=6')
replace_text_run(p, 'mn=32', 'mn=32')
replace_text_run(p, 'n−m=6', 'n−m=6')
replace_hybrid(p, '½mn=½|', ['F₁F₂'], '½mn=½|F₁F₂|·h')
log.append('p#45: m−n=6/mn=32/n−m=6转oMath＋½mn=½|F₁F₂|·h重建（等面积求高h=mn/|F₁F₂|亲算核验）')

# p#158
p = paras[158]
replace_hybrid(p, '|P', ['F₁'], '|PF₁|', occurrence=1)
replace_hybrid(p, '|P', ['F₂'], '|PF₂|', occurrence=1)
replace_hybrid(p, 'm+n=2', ['a₁'], 'm+n=2a₁')
replace_hybrid(p, 'n−m=2', ['a₂'], 'n−m=2a₂')
replace_hybrid(p, '°', ['∠F₁PF₂=90'], '∠F₁PF₂=90°')
replace_hybrid(p, '1/', ['e₁²+1', 'e₂²=2'], '1/e₁²+1/e₂²=2')
replace_hybrid(p, '½(1/', ['e₁²+1', 'e₂²)'], '½(1/e₁²+1/e₂²)')
log.append('p#158: |PF₁|/|PF₂|/m+n=2a₁/n−m=2a₂/∠=90°（乱序°复位）/1/e₁²+1/e₂²=2/½(1/e₁²+1/e₂²)重建（e关系与9/2最小值亲算核验）')

# p#178
p = paras[178]
replace_text_run(p, '−1', '−1')
replace_text_run(p, '2a', '2a')
replace_text_run(p, '2b', '2b')
log.append('p#178: −1/2a/2b转oMath')

# p#211
p = paras[211]
replace_text_run(p, 'F(−c,0)', 'F(−c,0)')
replace_text_run(p, 'A(a,0)', 'A(a,0)')
replace_text_run(p, 'B(0,b)', 'B(0,b)')
replace_text_run(p, 'b/a', 'b/a')
log.append('p#211: F(−c,0)/A(a,0)/B(0,b)/b/a转oMath')

# p#243
p = paras[243]
replace_text_run(p, '120°', '120°')
replace_hybrid(p, '|P', ['F₂', 'F₁'], '|PF₂|−|PF₁|=2a')
replace_text_run(p, 'e=c/a', 'e=c/a')
log.append('p#243: 120°转oMath＋|PF₂|−|PF₁|=2a重建＋e=c/a转oMath')

# p#247
p = paras[247]
replace_hybrid(p, '°', ['∠F₁PF₂=90'], '∠F₁PF₂=90°')
replace_hybrid(p, '°', ['∠PF₂F₁=30'], '∠PF₂F₁=30°')
replace_hybrid(p, '|P', ['F₂', '=√3c'], '|PF₂|=√3c')
replace_hybrid(p, '|P', ['F₁'], '|PF₁|')
replace_hybrid(p, '|P', ['F₂', 'F₁'], '|PF₂|−|PF₁|=2a')
log.append('p#247: ∠=90°/∠=30°（°乱序复位）＋|PF₂|=√3c/|PF₁|/|PF₂|−|PF₁|=2a重建（正六边形e=√3+1亲算核验）')

# p#276
p = paras[276]
replace_hybrid(p, '−', ['b²', 'a²'], '−b²/a²')
log.append('p#276: −b²/a²重建（椭圆第三定义斜率积）')

# 最终全量复扫（扩展签名）
sig = re.compile(r'[√½¼¾²³¹°−∠⊥∈∩∪≈≤≥≠±⋅·×₀-₉_]')
n = 0
for i, pp in enumerate(paras):
    full = ''.join(t.text or '' for t in pp.iter(w('t'))) + ''.join(t.text or '' for t in pp.iter(m('t')))
    if '【编注】' not in full:
        continue
    wt = ''.join(t.text or '' for t in pp.iter(w('t')))
    hits = sig.findall(wt)
    if hits:
        n += 1
        print(f'  RESIDUAL p#{i}: {hits} :: {wt[:80]!r}')
assert n == 0, f'{n} residual'
print('扩展签名全量复扫（全部编注段 w:t层）= 0 ✓')

tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
with open(DOC + '.fix4b_log.txt' if False else r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\fx5_fix4b_log.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))
print('\n'.join(log))
print('FIX4b SAVED')
