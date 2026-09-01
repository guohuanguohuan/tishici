# -*- coding: utf-8 -*-
"""S盖章·盖章前COM页数实测（只读开卷、wdStatisticPages=2）＋与基准比对。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client

OUT = r'C:\提示词\高中数学\高中数学同步'
FILES = [  # （代号, 文件名, 基准页数）
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 16),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 20),
    ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 77),
    ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 77),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 5),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 39),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 53),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 56),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 41),
    ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 71),
]

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('Word COM 版本: %s (build %s)' % (word.Version, word.Build))
res = {}
try:
    for tag, fn, base in FILES:
        p = os.path.join(OUT, fn)
        doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
        try:
            n = doc.ComputeStatistics(2)
        finally:
            doc.Close(False)
        res[tag] = n
        print('%s | %d页 | 基准%d | %s' % (tag, n, base, 'OK' if n == base else '!!!不一致!!!'))
finally:
    word.Quit()
total = sum(res.values())
print('合计 %d 页（基准 455）| %s' % (total, 'OK' if total == 455 else '!!!不一致!!!'))
ok = all(res[t] == b for t, _, b in FILES)
print('比对结论: %s' % ('全部一致' if ok else '存在不一致——停'))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pre_pages.json'), 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
sys.exit(0 if ok else 1)
