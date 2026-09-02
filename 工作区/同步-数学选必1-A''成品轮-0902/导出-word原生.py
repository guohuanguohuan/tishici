# -*- coding: utf-8 -*-
"""§14备用路径①：Word ExportAsFixedFormat（B全件＋其余前5页 Range）"""
import glob, os, sys, win32com.client, pythoncom
BASE = r'C:\提示词' + chr(92) + '高中数学' + chr(92) + '高中数学同步'
OUT = 'wip/pdf'
os.makedirs(OUT, exist_ok=True)
jobs = [('B', glob.glob(BASE + chr(92) + '*（上）*')[0], None)]
for tag, pat in [('X1', '*第1章*衔接件*'), ('I1', '*第1章*知识清单*'), ('C', '*（下）*'),
                 ('X2', '*第2章*衔接件*'), ('I2', '*第2章*知识清单*'), ('E', '*2.1—2.3.3*'),
                 ('F', '*2.3.4—2.5.2*'), ('G', '*2.6.1—2.7.2*'), ('H', '*2.8）*')]:
    jobs.append((tag, glob.glob(BASE + chr(92) + pat)[0], 5))
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
try:
    for tag, f, n5 in jobs:
        d = word.Documents.Open(os.path.abspath(f), ReadOnly=True, AddToRecentFiles=False)
        out = os.path.abspath(os.path.join(OUT, tag + '.pdf'))
        if n5:
            d.ExportAsFixedFormat(out, 17, Range=0, From=1, To=5)   # wdExportFromTo
        else:
            d.ExportAsFixedFormat(out, 17)
        d.Close(False)
        print(tag, os.path.getsize(out) // 1024, 'KB')
finally:
    word.Quit(); pythoncom.CoUninitialize()
