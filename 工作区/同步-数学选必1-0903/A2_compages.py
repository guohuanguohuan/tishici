# -*- coding: utf-8 -*-
"""A2 COM页数实测：自建Word实例、ReadOnly打开、用完Quit。"""
import win32com.client, pythoncom, os, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FILES = [
 ('X2', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
 ('I2', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
 ('E',  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
 ('F',  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
 ('G',  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
 ('H',  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for code, path in FILES:
        try:
            doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False, Visible=False)
            pages = doc.ComputeStatistics(2)  # wdStatisticPages
            print('%s: %d 页  (%.2f MB)' % (code, pages, os.path.getsize(path)/1048576.0))
            doc.Close(False)
        except Exception as e:
            print('%s: ERROR %s' % (code, e))
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('DONE')
