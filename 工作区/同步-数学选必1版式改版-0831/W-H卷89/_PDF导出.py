# -*- coding: utf-8 -*-
"""W-H卷89 §14 PDF前5页抽查导出：Word原生ExportAsFixedFormat（Range=FromTo 1-5）
派发预警：PDFCreator主路径本轮同机已损（W-B§四.2），直接走备用路径；COM独立子进程＋Quit。"""
import sys, io, os, time, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

WD = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(WD, 'PDF临时')
os.makedirs(PDFDIR, exist_ok=True)
SRC = os.path.join(WD, 'H工作副本.docx')
LOCAL = os.path.join(PDFDIR, 'H-导出副本.docx')
OUT = os.path.join(PDFDIR, 'H-前5页.pdf')
shutil.copy(SRC, LOCAL)
time.sleep(2)

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    d = word.Documents.Open(LOCAL, ReadOnly=True, AddToRecentFiles=False)
    try:
        t0 = time.time()
        # 17=wdExportFormatPDF; Range=2(wdExportFromTo), From=1, To=5
        d.ExportAsFixedFormat(OUT, 17, False, 0, 2, 1, 5)
        print('ExportAsFixedFormat(前5页) %.1fs' % (time.time() - t0))
    finally:
        d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('PDF:', OUT, os.path.getsize(OUT), 'bytes')
