# -*- coding: utf-8 -*-
# COM页数实测＋PDF前5页导出（X1）——独立进程，用完Quit
import os, sys
import win32com.client

SRC = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\X1工作副本.docx'
PDF_OUT = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\PDF前5页.pdf'

word = None
try:
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(SRC, ReadOnly=True, AddToRecentFiles=False)
    doc.Repaginate()
    pages = doc.ComputeStatistics(2)  # wdStatisticPages
    print('COM页数:', pages)
    # §12体积
    print('文件大小MB: %.2f' % (os.path.getsize(SRC)/1048576))
    # PDF前5页导出（ExportAsFixedFormat，Range wdFromTo=3, 1..5）
    doc.ExportAsFixedFormat(PDF_OUT, 17, False, 0, 0, 1, 5, 7, True, True, 0, True, True, False)
    print('PDF前5页导出:', os.path.exists(PDF_OUT), os.path.getsize(PDF_OUT) if os.path.exists(PDF_OUT) else 0)
    doc.Close(False)
finally:
    if word is not None:
        word.Quit()
print('done')
