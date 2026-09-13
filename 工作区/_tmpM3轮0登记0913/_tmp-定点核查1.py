# -*- coding: utf-8 -*-
"""定点核查：①单元概况12题件 ②圆的弦长14题件 ③17抛物线中的弦双版题干指纹比对。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def para_text(p_el):
    parts = []
    def walk(el):
        for c in el:
            if c.tag == W + 't':
                parts.append(c.text or '')
            else:
                walk(c)
    walk(p_el)
    return ''.join(parts)

def paras(path):
    doc = Document(path)
    return [t.strip() for t in (para_text(p) for p in doc.element.body.iter(W + 'p')) if t.strip()]

ROOT = r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1'

print('═══ ① 单元概况（共12题）件：全文段落清单（前60段） ═══')
p1 = ROOT + '/第3章 圆锥曲线的方程/1第2章-平面解析几何-圆锥曲线的方程（共12题）完成.docx'
ts = paras(p1)
for i, t in enumerate(ts[:60]):
    print('[%d] %s' % (i, t[:64]))
print('...段总数=%d' % len(ts))
