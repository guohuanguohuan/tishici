# -*- coding: utf-8 -*-
"""E2任务B-导出：六部分首件（X1/I1/B/X2/I2/E）本地副本导出PDF。
PDFCreator主路径本机已损（W轮多件报告证实），按§14备用路径①Word原生ExportAsFixedFormat。
导出件用完即删（校验后另行脚本删除）。COM实例自建自Quit。"""
import os, sys, io, shutil, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import win32com.client

ROOT = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
OUT = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(OUT, 'PDF')
os.makedirs(PDFDIR, exist_ok=True)
FILES = {
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
}
wdExportFormatPDF = 17
wdExportOptimizeForPrint = 0
wdExportAllDocument = 0
wdExportDocumentContent = 0
wdExportDocumentWithMarkup = 7
wdExportCreateHeadingBookmarks = 0

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for code, fn in FILES.items():
        src = os.path.join(ROOT, fn)
        local = os.path.join(PDFDIR, fn)
        shutil.copy2(src, local)
        pdf = os.path.join(PDFDIR, code + '.pdf')
        t0 = time.time()
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        word.ActiveWindow.View.Type = 3  # wdPrintView，防域不刷
        doc.Fields.Update()
        doc.ExportAsFixedFormat(OutputFileName=pdf, ExportFormat=wdExportFormatPDF,
                                OpenAfterExport=False, OptimizeFor=wdExportOptimizeForPrint,
                                Range=wdExportAllDocument, Item=wdExportDocumentContent,
                                IncludeDocProps=False, KeepIRM=True, CreateBookmarks=wdExportCreateHeadingBookmarks,
                                DocStructureTags=False, BitmapMissingFonts=True, UseISO19005_1=False)
        n = doc.ComputeStatistics(2)  # wdStatisticPages
        doc.Close(False)
        print(f'{code}: exported {n} pages (COM), {os.path.getsize(pdf)//1024}KB, {time.time()-t0:.1f}s')
        os.remove(local)
finally:
    word.Quit()
    print('Word Quit done')
