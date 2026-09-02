# -*- coding: utf-8 -*-
"""I1内容手术v2：结构图×6删除＋图例行拆两段（重建式）"""
import zipfile, os, sys, re, copy
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
def q(t): return '{%s}%s' % (W, t)
p = sys.argv[1] if len(sys.argv) > 1 else 'wip/I1.docx'
z = zipfile.ZipFile(p); parts = {n: z.read(n) for n in z.namelist()}; z.close()
doc = etree.fromstring(parts['word/document.xml'])
body = doc.find(q('body'))
els = list(body)
XMLSP = '{http://www.w3.org/XML/1998/namespace}space'
ANCHOR_TXT = re.compile(r'^\d+(?:\.\d+)+ \S{1,30}$')

def ptext(e): return ''.join(t.text or '' for t in e.iter(q('t')))
def has_img(e): return next(e.iter(WP+'anchor'), None) is not None or next(e.iter(WP+'inline'), None) is not None

# —— 1) 图例行拆两段（重建式）：找「〔基〕…｜〔进〕…」单段 ——
LEG1 = '〔基〕＝基础必会：必须学完本条目，才能做本章题目'
LEG2 = '〔进〕＝进阶汇总：本章各题型常识/结论的汇总，方便复习，必须先做题再回看'
split_done = 0
for e in list(body):
    if e.tag != q('p'): continue
    t = ptext(e).strip()
    if t.startswith('〔基〕') and '〔进〕' in t and '｜' in t:
        # 模板run＝段内首个含文字run
        tmpl = None
        for r in e.findall(q('r')):
            if any((x.text or '') for x in r.findall(q('t'))):
                tmpl = r; break
        assert tmpl is not None, '图例行无文字run'
        def mkpara(text):
            np_ = etree.Element(q('p'))
            ppr_src = e.find(q('pPr'))
            if ppr_src is not None:
                np_.append(copy.deepcopy(ppr_src))
            nr = copy.deepcopy(tmpl)
            for x in nr.findall(q('t')): nr.remove(x)
            nt = etree.SubElement(nr, q('t')); nt.text = text; nt.set(XMLSP, 'preserve')
            np_.append(nr)
            return np_
        e.addnext(mkpara(LEG2))
        e.addprevious(mkpara(LEG1))
        body.remove(e)
        split_done = 1
        break
print('图例行拆段:', split_done)
assert split_done == 1, '图例行未拆（定位失败）'

# —— 2) 结构图删除：头部区（真节标题前）纯图段 ——
els = list(body)
first_sec = None
for i, e in enumerate(els):
    if e.tag != q('p'): continue
    txt = ptext(e).strip()
    if not txt: continue
    ppr = e.find(q('pPr'))
    shd = ppr.find(q('shd')) if ppr is not None else None
    if shd is not None and shd.get(q('fill')) == 'ADC2DA' and txt[0].isdigit():
        first_sec = i; break                            # 真节标题（ADC2DA）优先判——与节名锚同文本形态
    if ANCHOR_TXT.match(txt): continue                  # 节名锚文本形态跳过
assert first_sec, '未找到首个节标题'
removed = []
for i in range(first_sec - 1, -1, -1):
    e = els[i]
    if e.tag != q('p'): continue
    txt = ptext(e)
    if has_img(e) and not txt.strip():
        removed.append(i); body.remove(e)
    elif (txt.strip().startswith('〔基〕') or txt.strip().startswith('〔进〕')
          or not txt.strip() or ANCHOR_TXT.match(txt.strip())):
        continue                      # 图例行/空段/节名锚段跳过
    else:
        break
print('结构图删除:', len(removed), '段@', removed)
assert len(removed) == 6, '期望6张结构图，实删%d' % len(removed)
parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = p + '.s2'
zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for nm, b in parts.items(): zo.writestr(nm, b)
zo.close(); os.replace(tmp, p)
print('I1 surgery v2 done')
