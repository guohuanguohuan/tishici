# -*- coding: utf-8 -*-
"""W-E卷92 §14 PDF前5页抽查导出：先PDFCreator主路径（快照→PrintOut→轮询），失败走Word原生ExportAsFixedFormat(1-5页)
独立COM子进程＋Quit；产物只认spool快照差集；用完删净"""
import sys, io, os, time, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

WD = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(WD, 'PDF临时')
os.makedirs(PDFDIR, exist_ok=True)
SRC = os.path.join(WD, 'E卷92-工作副本.docx')
LOCAL = os.path.join(PDFDIR, 'E卷92-导出副本.docx')
OUT = os.path.join(PDFDIR, 'E卷92-前5页.pdf')
shutil.copy(SRC, LOCAL)
time.sleep(1)

SPOOL = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'PDFCreator', 'Spool')

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
used_main = False
try:
    d = word.Documents.Open(LOCAL, ReadOnly=True, AddToRecentFiles=False)
    try:
        # 主路径：PDFCreator前5页（PrintOut Range="1-5"）
        snap = set(glob.glob(os.path.join(SPOOL, '*'))) if os.path.isdir(SPOOL) else set()
        word.ActivePrinter = 'PDFCreator'
        t0 = time.time()
        d.PrintOut(Background=False, Range='wdPrintFromTo', From='1', To='5')
        print('主路径PrintOut returned in %.1fs' % (time.time() - t0))
        out = None
        for i in range(30):
            time.sleep(2)
            cur = set(glob.glob(os.path.join(SPOOL, '*')))
            new = [f for f in cur - snap if f.lower().endswith('.pdf')]
            if new:
                out = sorted(new, key=os.path.getmtime)[-1]
                break
            if time.time() - t0 > 120:
                break
        if out:
            for i in range(8):
                try:
                    shutil.copy(out, OUT); break
                except PermissionError:
                    time.sleep(4)
            used_main = True
            print('主路径产物:', OUT, os.path.getsize(OUT), 'bytes')
            # 清自己的任务文件
            for f in glob.glob(os.path.splitext(out)[0] + '.*'):
                for i in range(6):
                    try: os.remove(f); break
                    except PermissionError: time.sleep(4)
        else:
            print('主路径spool无产物——转备用路径（Word原生导出前5页）')
    finally:
        d.Close(False)
    if not used_main:
        d2 = word.Documents.Open(LOCAL, ReadOnly=True, AddToRecentFiles=False)
        try:
            t0 = time.time()
            d2.ExportAsFixedFormat(OutputFileName=OUT, ExportFormat=17, OpenAfterExport=False,
                                   OptimizeFor=0, Range=3, From=1, To=5, Item=0,
                                   IncludeDocProps=True, KeepIRM=True, CreateBookmarks=0,
                                   DocStructureTags=True, BitmapMissingFonts=True, UseISO19005_1=False)
            print('备用路径ExportAsFixedFormat(1-5页) %.1fs -> %s %d bytes' % (time.time() - t0, OUT, os.path.getsize(OUT)))
        finally:
            d2.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('DONE used_main=%s' % used_main)
