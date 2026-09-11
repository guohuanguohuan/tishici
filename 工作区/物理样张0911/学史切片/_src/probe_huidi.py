# -*- coding: utf-8 -*-
"""探针：物理学史清单.docx 必修第三册段——逐段输出文本，灰底（shading/highlight）span 用 ⟪…⟫ 标出。
灰底取证口径：w:rPr/w:shd@w:fill 非 auto/非 FFFFFF，或 w:highlight 非 none。
仅供样张件灰底标记点复验，可删。"""
import re
from docx import Document

SRC = r'C:\提示词\高中物理\高中物理同步\物理学史清单.docx'
doc = Document(SRC)
body = doc.element.body
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

in_bk3 = False
out = []
for p in body.iterchildren():
    if p.tag != W + 'p':
        out.append('──表──')
        continue
    text_parts = []
    for r in p.iter(W + 'r'):
        rpr = r.find(W + 'rPr')
        t = ''.join((t.text or '') for t in r.findall(W + 't'))
        if not t:
            continue
        huid = False
        if rpr is not None:
            shd = rpr.find(W + 'shd')
            if shd is not None:
                fill = shd.get(W + 'fill')
                if fill and fill not in ('auto', 'FFFFFF'):
                    huid = True
            hl = rpr.find(W + 'highlight')
            if hl is not None and hl.get(W + 'val') not in (None, 'none'):
                huid = True
        text_parts.append(('⟪' + t + '⟫') if huid else t)
    line = ''.join(text_parts)
    if re.match(r'^必修第[一二三]册$', line.strip()):
        in_bk3 = (line.strip() == '必修第三册')
    if in_bk3 or re.match(r'^选择性必修第一册$', line.strip()):
        out.append(line)
print('\n'.join(out)).__class__
with open(r'C:\提示词\工作区\物理样张0911\学史切片\_src\必修三灰底.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('OK 段数=%d' % len(out))
