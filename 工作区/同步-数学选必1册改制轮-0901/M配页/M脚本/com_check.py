# -*- coding: utf-8 -*-
"""M配页·COM页数实测＋PDF导出（自建Word实例，用完Quit）。用法：com_check.py <docx...>（均导PDF到PDF/）"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pythoncom, win32com.client

WORK = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\M配页'
PDFDIR = os.path.join(WORK, 'PDF')
os.makedirs(PDFDIR, exist_ok=True)
files = [os.path.abspath(a) for a in sys.argv[1:]]

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
ver = word.Version
print('Word COM version:', ver)
try:
    for f in files:
        doc = word.Documents.Open(f, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.Repaginate()
            pages = doc.ComputeStatistics(2)
            base = os.path.splitext(os.path.basename(f))[0]
            pdf = os.path.join(PDFDIR, base + '.pdf')
            doc.ExportAsFixedFormat(pdf, 17)   # wdExportFormatPDF
            print(f'{os.path.basename(f)}: pages={pages} -> {pdf}')
        finally:
            doc.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('done')
