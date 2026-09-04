# -*- coding: utf-8 -*-
"""B件COM分步探针：定位挂起点（Open/Repaginate/ComputeStatistics 分步计时，flush输出）。"""
import sys, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pythoncom, win32com.client

SRC = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
DST = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\tmp\B_probe.docx'

os.makedirs(os.path.dirname(DST), exist_ok=True)
import shutil
shutil.copy2(SRC, DST)
print('copied %.1fMB' % (os.path.getsize(DST) / 1048576), flush=True)

pythoncom.CoInitialize()
t0 = time.time()
word = win32com.client.DispatchEx('Word.Application')
print('DispatchEx %.1fs' % (time.time() - t0), flush=True)
word.Visible = False
word.DisplayAlerts = 0
t0 = time.time()
doc = word.Documents.Open(os.path.abspath(DST), ReadOnly=True, AddToRecentFiles=False)
print('Open %.1fs' % (time.time() - t0), flush=True)
t0 = time.time()
doc.Repaginate()
print('Repaginate %.1fs' % (time.time() - t0), flush=True)
t0 = time.time()
p = doc.ComputeStatistics(2)
print('ComputeStatistics pages=%d %.1fs' % (p, time.time() - t0), flush=True)
doc.Close(False)
word.Quit()
print('DONE', flush=True)
