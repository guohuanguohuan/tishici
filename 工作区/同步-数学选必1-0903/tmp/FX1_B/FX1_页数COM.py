# -*- coding: utf-8 -*-
"""FX1-B COM开卷页数实测（自建实例 ReadOnly 用完Quit）"""
import datetime
import pythoncom
from win32com.client import DispatchEx

PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
t0 = datetime.datetime.now()
pythoncom.CoInitialize()
word = None
try:
    word = DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(PATH, ReadOnly=True, AddToRecentFiles=False)
    pages = doc.ComputeStatistics(2)  # wdStatisticPages
    fname = doc.Name
    doc.Close(False)
    print(f'COM开卷: {fname}')
    print(f'实测页数={pages}')
    print(f'耗时={(datetime.datetime.now() - t0).total_seconds():.1f}s')
finally:
    if word is not None:
        word.Quit()
    pythoncom.CoUninitialize()
    print('实例已Quit')
