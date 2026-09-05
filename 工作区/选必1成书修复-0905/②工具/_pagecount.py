# -*- coding: utf-8 -*-
"""_pagecount.py — COM 实测页数（轮②验证辅助）。用法: python _pagecount.py <docx...>"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for src in sys.argv[1:]:
        src = os.path.abspath(src)
        d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        try:
            d.Repaginate()
            print('%s -> %d pages' % (os.path.basename(src), d.ComputeStatistics(2)))
        finally:
            d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
