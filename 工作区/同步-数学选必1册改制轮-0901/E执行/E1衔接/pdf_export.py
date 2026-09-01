# -*- coding: utf-8 -*-
# 一次性脚本（E1衔接）：Word COM 导出PDF（ExportAsFixedFormat，自建实例用完Quit）＋PyMuPDF渲染前2页PNG＋逐页文字抽取
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

src, pdf, outdir = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
    try:
        d.ExportAsFixedFormat(pdf, 17)  # wdExportFormatPDF
    finally:
        d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('PDF ->', pdf)

import fitz
doc = fitz.open(pdf)
print('页数:', doc.page_count)
os.makedirs(outdir, exist_ok=True)
for i in range(min(2, doc.page_count)):
    p = doc[i]
    pix = p.get_pixmap(dpi=110)
    pix.save(os.path.join(outdir, 'page%d.png' % (i + 1)))
    print('---- 第%d页文字层 ----' % (i + 1))
    print(p.get_text()[:600])
doc.close()
