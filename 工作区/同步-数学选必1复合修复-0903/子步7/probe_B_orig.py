# -*- coding: utf-8 -*-
"""原路径B开卷探针（ReadOnly，分步计时）。"""
import sys, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pythoncom, win32com.client

SRC = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
pythoncom.CoInitialize()
t0 = time.time()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('DispatchEx %.1fs' % (time.time() - t0), flush=True)
t0 = time.time()
doc = word.Documents.Open(SRC, ReadOnly=True, AddToRecentFiles=False)
print('Open %.1fs' % (time.time() - t0), flush=True)
t0 = time.time()
p = doc.ComputeStatistics(2)
print('pages=%d %.1fs' % (p, time.time() - t0), flush=True)
doc.Close(False)
word.Quit()
print('DONE', flush=True)
