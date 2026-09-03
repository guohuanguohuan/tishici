# -*- coding: utf-8 -*-
"""FX5-G probe 12: group 13.2 structure (around p#720-760) + source 大招7 平均性质 statement"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
SRC = r'C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\模块8大招7平均性质.docx'

tree = etree.parse(DOC)
body = tree.getroot().find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def ptext(p):
    out = []
    def walk(el):
        for c in el:
            if c.tag == f'{{{W}}}t' and c.text is not None:
                out.append(c.text)
            elif c.tag == f'{{{M}}}t' and c.text is not None:
                out.append(c.text)
            else:
                walk(c)
    walk(p)
    return ''.join(out)

print('=== G paras 715-760 (group 13.x structure) ===')
for i in range(715, min(761, len(paras))):
    t = ptext(paras[i]).replace('\xa0', '␣')
    # only titles/question numbers/answers/analysis markers
    if re.match(r'^\s*2\.7', t) or '题型' in t[:12] or t.startswith('【'):
        print(f'  p#{i}: {t[:100]!r}')

# source: 平均性质 statement
with zipfile.ZipFile(SRC) as z:
    sxml = z.read('word/document.xml')
sroot = etree.fromstring(sxml)
sbody = sroot.find(f'{{{W}}}body')
sparas = sbody.findall(f'{{{W}}}p')
stexts = [ptext(p) for p in sparas]
print('\n=== source 大招7 平均性质 statement ===')
for i, t in enumerate(stexts[:40]):
    if t.strip():
        print(f'  src p#{i}: {t[:150]!r}')
