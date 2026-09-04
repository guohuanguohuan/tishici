# -*- coding: utf-8 -*-
"""子步4：COM开卷冒烟（DispatchEx自建实例，用完Quit；页数仅登记不作断言——子步7才重测基线）。"""
import sys, io, os, json, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

FILES = {
 'I1': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'I2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
}
out = {}
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for code, p in FILES.items():
        t0 = time.time()
        try:
            d = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
            d.Repaginate()
            pages = d.ComputeStatistics(2)   # wdStatisticPages
            d.Close(False)
            out[code] = {'ok': True, 'pages': pages, 'sec': round(time.time() - t0, 1)}
            print('[%s] OK 页数=%d %.1fs' % (code, pages, time.time() - t0))
        except Exception as e:
            out[code] = {'ok': False, 'err': repr(e)}
            print('[%s] FAIL %r' % (code, e))
finally:
    word.Quit()
    pythoncom.CoUninitialize()
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'COM冒烟_子步4.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('落盘 COM冒烟_子步4.json')
