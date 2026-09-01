# -*- coding: utf-8 -*-
"""一次性脚本（E3讲练B）——PDF前2页导出（COM ExportAsFixedFormat FromTo）＋Quit"""
import win32com.client, pythoncom, os, sys

src = r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\工作\B_终.docx"
out = r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\工作\B_终_前2页.pdf"
pythoncom.CoInitialize()
app = win32com.client.DispatchEx("Word.Application")
app.Visible = False
try:
    doc = app.Documents.Open(src, ReadOnly=True)
    # wdExportFormatPDF=17, OpenAfterExport=False, OptimizeFor=0(print),
    # Range=3(wdExportFromTo), From=1, To=2
    doc.ExportAsFixedFormat(out, 17, False, 0, 3, 1, 2)
    print('导出页数(Information):', doc.ComputeStatistics(2))  # wdStatisticPages
    doc.Close(False)
finally:
    app.Quit()
    pythoncom.CoUninitialize()
print('OK ->', out, os.path.getsize(out), 'bytes')
