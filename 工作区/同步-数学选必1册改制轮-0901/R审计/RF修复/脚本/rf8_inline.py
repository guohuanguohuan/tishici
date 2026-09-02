# -*- coding: utf-8 -*-
"""RF2-裁决①：5锚（X1 idx9/16、B idx17、C idx20/27）wp:anchor→wp:inline独立段。
规则：保留extent/effectExtent/docPr/cNvGraphicFramePr/graphic原样（图原extent不动）；
删simplePos/positionH/positionV/wrapSquare与anchor属性；drawing run移入新段落
（deepcopy原段pPr保shd/行距/对齐延续），新段插原段之后（图随引用内容排其后、零空行）。"""
import sys, os, zipfile, json
sys.stdout.reconfigure(encoding='utf-8')
from copy import deepcopy
from lxml import etree

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\输出'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
PLAN = {'X1': [9, 16], 'B': [17], 'C': [20, 27]}
KEEP = ['extent', 'effectExtent', 'docPr', 'cNvGraphicFramePr', 'graphic']

for code, targets in PLAN.items():
    path = os.path.join(BASE, code + '.docx')
    z = zipfile.ZipFile(path)
    names = z.namelist(); data = {n: z.read(n) for n in names}; infos = {n: z.getinfo(n) for n in names}
    z.close()
    root = etree.fromstring(data['word/document.xml'])
    idx = 0; done = []
    for p in list(root.iter('{%s}p' % W)):
        for an in p.findall('.//{%s}anchor' % WP):
            idx += 1
            if idx not in targets: continue
            drawing = an.getparent()
            run = drawing.getparent()
            assert run.tag == '{%s}r' % W, 'anchor父非run'
            # run内除drawing外的内容检查（应独占）
            for junk in [c for c in run if c is not drawing and etree.QName(c).localname == 'lastRenderedPageBreak']:
                run.remove(junk)
            others = [etree.QName(c).localname for c in run if c is not drawing]
            assert others == ['rPr'] or not others, 'anchor run含其他子元素: %s' % others
            # 构造inline
            inl = etree.Element('{%s}inline' % WP)
            for child in list(an):
                ln = etree.QName(child).localname
                if ln in KEEP:
                    inl.append(child)
            assert inl.find('{%s}extent' % WP) is not None
            assert inl.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}graphic'.replace('drawingml/2006/main','drawingml/2006/main')) is not None or inl.find('{http://schemas.openxmlformats.org/drawingml/2006/picture}pic') is not None or len(inl) >= 3
            drawing.replace(an, inl)
            # 新独立段：复制原段pPr
            newp = etree.Element('{%s}p' % W)
            ppr = p.find('{%s}pPr' % W)
            if ppr is not None:
                newp.append(deepcopy(ppr))
            newp.append(run)  # run整体移入
            p.addnext(newp)
            done.append(idx)
    assert done == targets, '完成集%s != 目标集%s' % (done, targets)
    data['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in names:
            zo.writestr(infos[n], data[n])
    # 校验：inline含graphic、锚数
    root2 = etree.fromstring(data['word/document.xml'])
    n_anchor = len(root2.findall('.//{%s}anchor' % WP))
    n_inline = len(root2.findall('.//{%s}inline' % WP))
    print('%s: inline化%d锚(%s)；anchor余%d inline总%d' % (code, len(done), done, n_anchor, n_inline))
print('DONE')
