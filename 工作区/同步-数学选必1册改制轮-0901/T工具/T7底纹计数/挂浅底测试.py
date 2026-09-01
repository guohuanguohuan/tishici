# -*- coding: utf-8 -*-
# 一次性测试：给讲练件副本人为挂 F2F2F2 段落底纹，验证⑦类计数（不依赖其他代理）。
# 三变体：全量（清点段全铺→恒等式应成立）/半量（仅前100段→应报清点未铺）/含错（全铺+2题干段+1个run级挂点→应报误铺与段外挂点）。
import sys, os, zipfile, shutil
sys.path.insert(0, r'C:\提示词\工具')
from lxml import etree
import 六类底纹计数 as T
from extract_structure import structure

W = T.W
def q(t): return '{%s}%s' % (W, t)

SRC = r'副本\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'

# pPr 内 shd 的合法插入位（CT_PPr 序：shd 之后的首个既有子元素之前）
AFTER = {q(t) for t in ('tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct',
                        'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd',
                        'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents',
                        'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
                        'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr',
                        'pPrChange')}

def add_para_shd(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.SubElement(p, q('pPr'))
        p.remove(ppr); p.insert(0, ppr)
    old = ppr.find(q('shd'))
    if old is not None:
        ppr.remove(old)
    shd = etree.Element(q('shd'))
    shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), 'F2F2F2')
    pos = len(list(ppr))
    for k, ch in enumerate(ppr):
        if ch.tag in AFTER:
            pos = k; break
    ppr.insert(pos, shd)

def add_run_shd(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    old = rpr.find(q('shd'))
    if old is not None:
        rpr.remove(old)
    shd = etree.SubElement(rpr, q('shd'))
    shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), 'F2F2F2')

def save(doc, out):
    data = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    zin = zipfile.ZipFile(SRC)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            if it.filename == 'word/document.xml':
                zo.writestr(it, data)
            else:
                zo.writestr(it, zin.read(it.filename))
    zin.close()

# —— 复用工具的清点逻辑确定目标段（工具口径＝真值侧）——
z = zipfile.ZipFile(SRC)
doc = etree.fromstring(z.read('word/document.xml'))
z.close()
els = list(doc.find(q('body')))
ptexts = {i: (T.ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
st = structure(SRC)
qstart_els = {st['items'][qu['start']]['el'] for qu in st['questions']}
heads = T.classify_headings(els, ptexts)
head_by_idx = {h[0]: h[1] for h in heads}
ncensus, census_idx = T.analysis_census(els, ptexts, qstart_els, head_by_idx)
print('解析块段落清点数 =', ncensus)

# 找2个非清点、非标题、非题号块的题干段（含错变体用）
extra_targets = []
for i in sorted(qstart_els):
    j = i + 1
    while j < len(els) and els[j].tag == q('p') and not ptexts[j].strip():
        j += 1
    if j < len(els) and els[j].tag == q('p') and j not in census_idx and j not in head_by_idx:
        extra_targets.append(j)
    if len(extra_targets) == 2:
        break
print('误铺目标题干段 =', extra_targets)

# 变体1：全量
for i in census_idx:
    add_para_shd(els[i])
save(doc, r'副本\变体_挂浅底全量.docx')

# 变体2：半量（重建 DOM）
z = zipfile.ZipFile(SRC); doc2 = etree.fromstring(z.read('word/document.xml')); z.close()
els2 = list(doc2.find(q('body')))
for i in sorted(census_idx)[:100]:
    add_para_shd(els2[i])
save(doc2, r'副本\变体_挂浅底半量.docx')

# 变体3：含错（全量＋2题干段＋1个run级挂点）
z = zipfile.ZipFile(SRC); doc3 = etree.fromstring(z.read('word/document.xml')); z.close()
els3 = list(doc3.find(q('body')))
for i in census_idx:
    add_para_shd(els3[i])
for j in extra_targets:
    add_para_shd(els3[j])
# run级挂点：第一个误铺段里首个有文字的 run
for r in els3[extra_targets[0]].iter(q('r')):
    if ''.join(x.text or '' for x in r.findall(q('t'))).strip():
        add_run_shd(r); print('run级违规挂点已加于段', extra_targets[0]); break
save(doc3, r'副本\变体_挂浅底含错.docx')
print('三变体落盘完成')
