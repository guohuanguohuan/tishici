# -*- coding: utf-8 -*-
"""E1复审计：COM页数复测＋PDF导出（本地副本，用毕即删）。只读产出原件。"""
import os, shutil, glob, time, sys, json
import win32com.client as win32

BASE = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
TMP = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\E1审计\tmp'
OUT = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\E1审计'
os.makedirs(TMP, exist_ok=True)

FILES = [
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 'full'),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 'full'),
    ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 5),
    ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 3),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 'full'),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 5),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 3),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 3),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 3),
    ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 3),
]

word = win32.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
res = {}
try:
    ver = word.Build
    for code, fn, pages in FILES:
        src = os.path.join(BASE, fn)
        local = os.path.join(TMP, fn)
        shutil.copy2(src, local)
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.Repaginate()
            n = doc.ComputeStatistics(2)  # wdStatisticPages
            pdf = os.path.join(OUT, 'pdf_%s.pdf' % code)
            if pages == 'full':
                doc.ExportAsFixedFormat(pdf, 17, False, 0, 0, 1, n)
            else:
                doc.ExportAsFixedFormat(pdf, 17, False, 0, 3, 1, min(pages, n))
            res[code] = {'pages': n, 'pdf_pages': 'full' if pages == 'full' else min(pages, n)}
            print(code, 'pages=', n)
        finally:
            doc.Close(False)
        try: os.remove(local)
        except OSError: pass
finally:
    word.Quit()
print('Word Build', ver)
json.dump(res, open(os.path.join(OUT, 'com_pages.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('SUM pages =', sum(v['pages'] for v in res.values()))
