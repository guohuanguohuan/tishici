# -*- coding: utf-8 -*-
"""FX5-G FIX7b(v2): 8段空格修复重做——先从.orig整段恢复runs（他修复未触及此8段），
再以math-aware即时邻接判定重删标点前空格；p#742答题位形态统一。"""
from copy import deepcopy
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
ORIG = DOC + '.orig'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return f'{{{W}}}{t}'
def m(t): return f'{{{M}}}{t}'

parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse(DOC, parser)
obody = etree.parse(ORIG, parser).getroot().find(w('body'))
body = tree.getroot().find(w('body'))
paras = body.findall(w('p'))
oparas = obody.findall(w('p'))

FIX7 = [104, 262, 263, 266, 267, 268, 290, 296]
# 0) sanity + 1) wholesale restore：FIX7索引＝orig树索引；fixed树对应段=索引-1（段[0]已删）
for fi in FIX7:
    op, fp = oparas[fi], paras[fi - 1]
    opPr, fpPr = op.find(w('pPr')), fp.find(w('pPr'))
    assert (opPr is None) == (fpPr is None), f'p#{fi} pPr None mismatch'
    if opPr is not None:
        assert opPr.find(w('tabs')) is None, f'p#{fi} orig had pPr tabs'
        assert etree.tostring(opPr) == etree.tostring(fpPr), f'p#{fi} pPr mismatch'
    for ch in list(fp):
        if ch.tag != w('pPr'):
            fp.remove(ch)
    insert_at = 1 if fp.find(w('pPr')) is not None else 0
    for ch in op:
        if ch.tag != w('pPr'):
            fp.insert(insert_at, deepcopy(ch))
            insert_at += 1
print('8段runs已自.orig整段恢复（fixed=orig索引−1）')

# 2) math-aware re-delete: space-only w:t whose next document-order content event is w:t starting with FW punct
FW = '，。；：？！、）．'
n = 0
for fi in FIX7:
    p = paras[fi - 1]
    ev = []
    for node in p.iter():
        if node.tag == w('t'):
            ev.append(node)
        elif node.tag == m('t'):
            ev.append(node)
        elif node.tag == w('drawing'):
            ev.append(node)
    for j, node in enumerate(ev):
        if node.tag == w('t') and node.text == ' ':
            nk = None
            for k in range(j + 1, len(ev)):
                t2 = ev[k]
                if t2.tag == w('t'):
                    if (t2.text or '') == '':
                        continue
                    nk = t2
                    break
                else:
                    nk = t2  # math/drawing
                    break
            if nk is not None and nk.tag == w('t') and nk.text and nk.text[0] in FW:
                run_host = node.getparent()
                if run_host.findall(w('t')) == [node]:
                    run_host.getparent().remove(run_host)
                else:
                    run_host.remove(node)
                n += 1
print(f'math-aware标点前空格删除: {n}')
assert n == 9, f'expect 9 got {n}'

# 3) p#742-orig (fixed idx 741) 答题位：'（'+' '+')'分run形态 → 空格run改nbsp×4
p = paras[741]  # fixed树索引：orig 742 = fixed 741
done = False
for r_el in p.findall(w('r')):
    ts = r_el.findall(w('t'))
    if len(ts) == 1 and ts[0].text == ' ':
        nxt = r_el.getnext()
        if nxt is not None and nxt.tag == w('r'):
            nts = nxt.findall(w('t'))
            if nts and nts[0].text and nts[0].text.startswith('）'):
                ts[0].text = '\xa0\xa0\xa0\xa0'
                done = True
                break
assert done, 'p741 slot space run not found'
print('p#741(fix): 答题位（ ）→（4×nbsp）形态统一（FX4先例）')

tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('FIX7b v2 SAVED')
