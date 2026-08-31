# -*- coding: utf-8 -*-
"""W-F卷90 §14 PDF前5页抽查导出：Word原生ExportAsFixedFormat（Range前5页）＋清残留"""
import sys, io, os, time, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

WD = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(WD, 'PDF临时')
os.makedirs(PDFDIR, exist_ok=True)
SRC = os.path.join(WD, 'F卷90-步骤11自检后.docx')
LOCAL = os.path.join(PDFDIR, 'F卷90-导出副本.docx')
OUT = os.path.join(PDFDIR, 'F卷90-前5页.pdf')
shutil.copy(SRC, LOCAL)
time.sleep(2)

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    d = word.Documents.Open(LOCAL, ReadOnly=True, AddToRecentFiles=False)
    try:
        d.Repaginate()
        t0 = time.time()
        # wdExportFromTo: Range=3, From=1, To=5（wdExportFormatPDF=17）
        d.ExportAsFixedFormat(OUT, 17, False, 0, 3, 1, 5, 0, True, True, 0, 0, False, True)
        print('Exported in %.1fs' % (time.time() - t0))
    finally:
        d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('PDF:', OUT, os.path.getsize(OUT) if os.path.exists(OUT) else 'MISSING', 'bytes')
