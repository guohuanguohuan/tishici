# -*- coding: utf-8 -*-
"""探针：分步计时 Open/Repaginate/ComputeStatistics/PrintOut(1页)，unbuffered，看门狗自断。"""
import sys, io, os, time, threading
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom

SRC = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'
DO_PRINT = '--print' in sys.argv

def watchdog(sec):
    time.sleep(sec)
    print('[看门狗] %ds 到限，强制退出进程' % sec, flush=True)
    os._exit(9)

threading.Thread(target=watchdog, args=(150,), daemon=True).start()
t0 = time.time()
pythoncom.CoInitialize()
print('[%.1fs] DispatchEx...' % (time.time() - t0), flush=True)
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('[%.1fs] Open...' % (time.time() - t0), flush=True)
d = word.Documents.Open(SRC, ReadOnly=True, AddToRecentFiles=False)
print('[%.1fs] Open 完成' % (time.time() - t0), flush=True)
d.Repaginate()
print('[%.1fs] Repaginate 完成' % (time.time() - t0), flush=True)
pages = d.ComputeStatistics(2)
print('[%.1fs] 页数=%d' % (time.time() - t0, pages), flush=True)
if DO_PRINT:
    word.ActivePrinter = 'PDFCreator'
    print('[%.1fs] ActivePrinter=PDFCreator 完成' % (time.time() - t0), flush=True)
    d.PrintOut(Background=False)
    print('[%.1fs] PrintOut 完成' % (time.time() - t0), flush=True)
d.Close(False)
word.Quit()
pythoncom.CoUninitialize()
print('[%.1fs] 全部完成' % (time.time() - t0), flush=True)
