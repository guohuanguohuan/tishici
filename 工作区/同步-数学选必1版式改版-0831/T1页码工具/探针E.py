# -*- coding: utf-8 -*-
"""COM探针：单开E副本，GoTo+Information逐页，定位RPC崩溃点。"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom

BASE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(BASE, 'P6', 'E.docx')
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('word up', flush=True)
try:
    doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
    print('opened, pages=', doc.ComputeStatistics(2), flush=True)
    for k in (1, 25, 50):
        rng = doc.GoTo(1, 1, k)
        print('goto', k, 'type=', type(rng).__name__, flush=True)
        adj = rng.Information(1)
        print('  info1=', adj, flush=True)
        adj3 = rng.Information(3)
        print('  info3=', adj3, flush=True)
    doc.Close(False)
    print('closed', flush=True)
finally:
    try:
        word.Quit()
        print('quit ok', flush=True)
    except Exception as e:
        print('QUIT FAILED:', e, flush=True)
    pythoncom.CoUninitialize()
