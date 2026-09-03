# -*- coding: utf-8 -*-
"""FX5-G probe 6: hunt source for p#754 (题2.7.2.13.4-18) — signature search in reference folders"""
import os, zipfile, re, sys

ROOTS = [
    r'C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何',
    r'C:\提示词\高中数学\参考\组卷网\【新课标 新探索】大单元作业设计\人教A版选择性必修1',
]
SIGS = ['过抛物线', '焦点的直线', '的两个交点为', '三点在一条直线上', '垂直抛物线准线']

def lin_text(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read('word/document.xml').decode('utf-8')
    except Exception as e:
        return ''
    # strip tags, keep text
    txt = re.sub(r'<[^>]+>', '', xml)
    return txt

hits = {}
for root in ROOTS:
    for dirpath, dirs, files in os.walk(root):
        for fn in files:
            if not fn.lower().endswith('.docx'):
                continue
            p = os.path.join(dirpath, fn)
            t = lin_text(p)
            if '的两个交点为' in t or ('过抛物线' in t and '焦点' in t and '交点为A' in t.replace(' ', '')):
                score = sum(1 for s in SIGS if s in t)
                hits[p] = (score, t)

for p, (score, t) in sorted(hits.items(), key=lambda kv: -kv[1][0]):
    print(score, p)
print('total', len(hits))
