# -*- coding: utf-8 -*-
"""导出PDF.py — 轮②验证用：Word COM ExportAsFixedFormat(17) 批量导出。
用法: python 导出PDF.py <outdir> <docx...>"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

outdir = sys.argv[1]
os.makedirs(outdir, exist_ok=True)
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for src in sys.argv[2:]:
        src = os.path.abspath(src)
        out = os.path.join(os.path.abspath(outdir), os.path.splitext(os.path.basename(src))[0] + '.pdf')
        d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        try:
            d.Repaginate()
            pages = d.ComputeStatistics(2)
            d.ExportAsFixedFormat(out, 17)   # wdExportFormatPDF
            print('%s -> %d pages, %d KB' % (os.path.basename(src), pages, os.path.getsize(out) // 1024))
        finally:
            d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
