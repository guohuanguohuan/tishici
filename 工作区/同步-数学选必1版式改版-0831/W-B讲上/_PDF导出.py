# -*- coding: utf-8 -*-
"""§14 全件PDF导出：PDFCreator主路径（快照→PrintOut→轮询spool新文件）"""
import sys, io, os, time, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

WD = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(WD, 'PDF临时')
os.makedirs(PDFDIR, exist_ok=True)
SRC = os.path.join(WD, 'B讲上-工作副本.docx')
LOCAL = os.path.join(PDFDIR, 'B讲上-导出副本.docx')
shutil.copy(SRC, LOCAL)
time.sleep(2)

SPOOL = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'PDFCreator', 'Spool')

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    snap = set(glob.glob(os.path.join(SPOOL, '*'))) if os.path.isdir(SPOOL) else set()
    d = word.Documents.Open(LOCAL, ReadOnly=True, AddToRecentFiles=False)
    try:
        word.ActivePrinter = 'PDFCreator'
        t0 = time.time()
        d.PrintOut(Background=False)
        print('PrintOut returned in %.1fs' % (time.time() - t0))
    finally:
        d.Close(False)
    # 轮询新文件
    out = None
    for i in range(120):
        time.sleep(2)
        cur = set(glob.glob(os.path.join(SPOOL, '*')))
        new = [f for f in cur - snap if f.lower().endswith('.pdf')]
        if new:
            out = sorted(new, key=os.path.getmtime)[-1]
            break
        if time.time() - t0 > 600:
            print('TIMEOUT 10min'); break
    if out:
        dst = os.path.join(PDFDIR, 'B讲上-全件.pdf')
        for i in range(12):
            try:
                shutil.copy(out, dst); break
            except PermissionError:
                time.sleep(5)
        print('PDF:', dst, os.path.getsize(dst), 'bytes')
        # 清自己的任务文件
        base = out
        for f in glob.glob(os.path.splitext(base)[0] + '.*'):
            for i in range(6):
                try: os.remove(f); break
                except PermissionError: time.sleep(5)
    else:
        print('NO NEW SPOOL FILE')
finally:
    word.Quit()
    pythoncom.CoUninitialize()
