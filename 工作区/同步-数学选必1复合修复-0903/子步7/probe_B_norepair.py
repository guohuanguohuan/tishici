# -*- coding: utf-8 -*-
import sys, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pythoncom, win32com.client
SRC = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
t0 = time.time()
doc = word.Documents.OpenNoRepairDialog(SRC, ReadOnly=True, AddToRecentFiles=False, ConfirmConversions=False)
print('OpenNoRepair %.1fs' % (time.time() - t0), flush=True)
p = doc.ComputeStatistics(2)
print('pages=%d' % p, flush=True)
doc.Close(False); word.Quit(); print('DONE', flush=True)
