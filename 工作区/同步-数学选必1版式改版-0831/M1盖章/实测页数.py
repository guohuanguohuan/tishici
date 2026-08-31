# -*- coding: utf-8 -*-
"""M1盖章轮·全十件COM只读实测页数（独立子进程、自建实例用完Quit）。落盘 实测页数.json/.txt"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client
from importlib.metadata import version as _ver

BASE = os.path.dirname(os.path.abspath(__file__))
PROD = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
FILES = [  # 装订序（规格书§0）：P1..P6
    ('P1', '第1章·衔接', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('P2', '第1章·清单', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
    ('P3', '第1章·讲练', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    ('P3', '第1章·讲练', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    ('P4', '第2章·衔接', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    ('P5', '第2章·清单', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
    ('P6', '第2章·讲练', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    ('P6', '第2章·讲练', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    ('P6', '第2章·讲练', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    ('P6', '第2章·讲练', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
W_ROUND = [20, 20, 78, 78, 4, 40, 47, 51, 36, 63]  # W轮报告值（派发语）

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
rows = []
try:
    for part, tag, name in FILES:
        p = os.path.join(PROD, name)
        assert os.path.isfile(p), '文件不存在: %s' % p
        doc = word.Documents.Open(os.path.abspath(p), ReadOnly=True, AddToRecentFiles=False)
        try:
            pg = doc.ComputeStatistics(2)
        finally:
            doc.Close(False)
        rows.append({'part': part, 'tag': tag, 'file': name, 'pages': pg})
finally:
    word.Quit()

mism = []
for r, w in zip(rows, W_ROUND):
    mark = 'OK' if r['pages'] == w else '!!与W轮不符(W=%d)' % w
    if r['pages'] != w:
        mism.append((r['file'], w, r['pages']))
    print('%s %s | %d页 | %s' % (r['part'], r['file'][:46], r['pages'], mark))
total = sum(r['pages'] for r in rows)
print('合计: %d页' % total)
json.dump({'rows': rows, 'total': total, 'w_round': W_ROUND,
           'pywin32': _ver('pywin32')},
          open(os.path.join(BASE, '实测页数.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
with open(os.path.join(BASE, '实测页数.txt'), 'w', encoding='utf-8') as f:
    for r, w in zip(rows, W_ROUND):
        f.write('%s\t%s\t%s\t%d\tW轮=%d\t%s\n'
                % (r['part'], r['tag'], r['file'], r['pages'], w,
                   'OK' if r['pages'] == w else 'MISMATCH'))
    f.write('合计\t%d\n' % total)
print('mismatch=%d' % len(mism))
