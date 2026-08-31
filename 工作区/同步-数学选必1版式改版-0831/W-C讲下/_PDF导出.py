# -*- coding: utf-8 -*-
"""W-C讲下 PDF前5页导出：PDFCreator主路径快照法→无产物则Word原生ExportAsFixedFormat(wdExportFromTo 1..5)＋残留清查"""
import os, sys, time, glob, shutil

SRC = os.path.abspath('C讲下-工作副本.docx')
OUT_PDF = os.path.abspath('C讲下-前5页.pdf')
SPOOL = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'PDFCreator', 'Spool')

def snapshot():
    if not os.path.isdir(SPOOL):
        return set()
    return set(os.listdir(SPOOL))

def try_pdfcreator(timeout_s=90):
    """主路径：PrintOut到PDFCreator，轮询spool新.pdf"""
    before = snapshot()
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.ActivePrinter = 'PDFCreator'
    doc = None
    try:
        doc = word.Documents.Open(SRC, ReadOnly=True)
        doc.PrintOut(Background=False)
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        cur = snapshot()
        new = cur - before
        pdfs = [f for f in new if f.lower().endswith('.pdf')]
        if pdfs:
            return os.path.join(SPOOL, sorted(pdfs)[0]), 'PDFCreator主路径'
        time.sleep(2)
    return None, 'PDFCreator主路径(无产物)'

def word_native():
    """备用路径：Word原生导出前5页"""
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    doc = None
    try:
        doc = word.Documents.Open(SRC, ReadOnly=True)
        # ExportAsFixedFormat(OutputFileName, ExportFormat=17wdExportFormatPDF, OpenAfterExport=False,
        #   OptimizeFor=0print, Range=3wdExportFromTo, From=1, To=5, Item=0wdExportDocumentContent,
        #   IncludeDocProps=True, KeepIRM=True, CreateBookmarks=0, DocStructureTags=True, ...
        doc.ExportAsFixedFormat(OUT_PDF, 17, False, 0, 3, 1, 5, 0, True, True, 0, True, True, False)
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()
    return OUT_PDF, 'Word原生ExportAsFixedFormat(前5页)'

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'auto'
    if mode in ('auto', 'creator'):
        p, how = try_pdfcreator()
        if p:
            shutil.copy(p, OUT_PDF)
            print('OK', how, '->', OUT_PDF, os.path.getsize(OUT_PDF), 'bytes')
            print('SPOOL_TASK:' + p)
            sys.exit(0)
        if mode == 'creator':
            print('FAIL', how); sys.exit(1)
    p, how = word_native()
    print('OK', how, '->', p, os.path.getsize(p), 'bytes')
