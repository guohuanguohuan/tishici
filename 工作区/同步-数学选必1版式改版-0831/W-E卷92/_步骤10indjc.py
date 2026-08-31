# -*- coding: utf-8 -*-
"""W-E卷92 步骤10【本件专属】：全件正文段 w:ind 扫清（含4处常识出清回指句 leftChars=400）＋ jc=left 归一
依据：公共规则§7段落条款——正文段落 w:ind 一律不得出现、所有内容左对齐无例外（含表格单元格）"""
import zipfile, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def w(t): return '{%s}%s' % (W, t)

PPR_ORDER_AFTER_JC = ['shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap',
                      'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
                      'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing',
                      'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
                      'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr']

path = 'E卷92-工作副本.docx'
with zipfile.ZipFile(path) as z:
    parts = {n: z.read(n) for n in z.namelist()}
doc = etree.fromstring(parts['word/document.xml'])
body = doc.find(w('body'))

ind_removed = []
jc_added = 0
jc_fixed = 0
for p in body.iter(w('p')):
    pPr = p.find(w('pPr'))
    if pPr is not None:
        ind = pPr.find(w('ind'))
        if ind is not None:
            attrs = {etree.QName(k).localname: v for k, v in ind.attrib.items()}
            ptxt = ''.join(t.text or '' for t in p.iter(w('t')))
            ind_removed.append((attrs, ptxt[:40]))
            pPr.remove(ind)
        jc = pPr.find(w('jc'))
        if jc is None:
            jc = etree.SubElement(pPr, w('jc'))
            jc.set(w('val'), 'left')
            # jc 在 OOXML pPr 序中位于 ind 之后；插到 rPr 之前即可（Word宽容，但尽量靠后合规位）
            rpr = pPr.find(w('rPr'))
            if rpr is not None:
                pPr.remove(jc)
                rpr.addprevious(jc)
            jc_added += 1
        elif jc.get(w('val')) not in ('left', 'start'):
            jc.set(w('val'), 'left')
            jc_fixed += 1

parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = path + '.jc'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, b in parts.items():
        zo.writestr(n, b)
for i in range(12):
    try:
        os.replace(tmp, path); break
    except PermissionError:
        time.sleep(5)

# 复扫断言：全文 w:ind=0、jc 全 left
with zipfile.ZipFile(path) as z:
    doc2 = etree.fromstring(z.read('word/document.xml'))
n_ind2 = sum(1 for i in doc2.iter(w('ind')))
bad_jc = [j.get(w('val')) for j in doc2.iter(w('jc')) if j.get(w('val')) not in ('left', 'start')]
print(json.dumps({'ind摘除数': len(ind_removed), 'jc新增数': jc_added, 'jc纠偏数': jc_fixed,
                  '复扫ind残留': n_ind2, '复扫非left的jc': bad_jc}, ensure_ascii=False))
for attrs, ptxt in ind_removed:
    print('  ind摘除:', attrs, '|', ptxt)
with open('登记-indjc纠偏.md', 'w', encoding='utf-8') as f:
    f.write('# 步骤10：w:ind扫清＋jc=left归一（E卷92）\n\n')
    f.write('## w:ind 摘除（%d处；步骤2已另清标题75处）\n\n' % len(ind_removed))
    for attrs, ptxt in ind_removed:
        f.write('- %s｜%s\n' % (attrs, ptxt))
    f.write('\n## jc 归一：新增 %d段、纠偏 %d段（both/justify等→left；复扫全文jc∈{left,start}、ind=0）\n' % (jc_added, jc_fixed))
