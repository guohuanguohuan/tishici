# -*- coding: utf-8 -*-
"""A0勘察：Word COM实测页数（自建实例，逐件Open/Close，末尾Quit）"""
import json, io, os, time
import win32com.client

BASE = r'C:\提示词\高中数学\高中数学同步'
FILES = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\A0勘察\pages_out.json'

res = {}
word = None
try:
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    ver = word.Version
    res['_word_version'] = ver
    print('Word COM version:', ver)
    for code, fn in FILES.items():
        path = os.path.join(BASE, fn)
        t0 = time.time()
        try:
            doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False, Visible=False)
            doc.Repaginate()
            pages = doc.ComputeStatistics(2)  # wdStatisticPages
            words = doc.ComputeStatistics(0)  # wdStatisticWords
            doc.Close(False)
            res[code] = {'pages': pages, 'words': words, 'sec': round(time.time() - t0, 1)}
            print(f'{code}: {pages}p ({time.time()-t0:.0f}s)')
        except Exception as e:
            res[code] = {'error': repr(e)}
            print(f'{code}: ERR {e!r}')
finally:
    if word is not None:
        try:
            word.Quit()
            print('Word Quit done')
        except Exception as e:
            print('Quit err:', e)
with io.open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print('saved pages_out.json')
