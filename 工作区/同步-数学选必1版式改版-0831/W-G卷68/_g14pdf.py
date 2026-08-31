# -*- coding: utf-8 -*-
"""W-G PDF前5页导出：Word原生ExportAsFixedFormat（独立子进程、自建实例、用完Quit）
派发预警：PDFCreator主路径本机已实测无产物（W-B同族先例）——直接走备用路径Word原生导出"""
import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
import pythoncom
import win32com.client

SRC = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
OUT = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G前5页.pdf"

pythoncom.CoInitialize()
word = None
try:
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(SRC, ReadOnly=True)
    # wdExportFormatPDF=17, wdExportFromTo=3, 前5页
    doc.ExportAsFixedFormat(OUT, 17, False, 0, 3, 1, 5)
    doc.Close(False)
    print('导出OK:', OUT, os.path.getsize(OUT), 'bytes')
finally:
    if word is not None:
        word.Quit()
    pythoncom.CoUninitialize()
