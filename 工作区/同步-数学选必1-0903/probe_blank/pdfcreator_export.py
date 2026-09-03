# -*- coding: utf-8 -*-
# §14主路径：PDFCreator打印导出（spool快照→PrintOut→轮询新.pdf）
import os, sys, io, time, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom
import fitz

SPOOL = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'PDFCreator', 'Spool')
SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1·册目录页.docx"
OUTDIR = r"C:\提示词\工作区\同步-数学选必1-0903\probe_blank\render"
LOCAL = os.path.join(OUTDIR, "册目录页_local.docx")
shutil.copy(SRC, LOCAL)

os.makedirs(SPOOL, exist_ok=True)
before = set(os.listdir(SPOOL))
print('spool snapshot:', len(before), 'files', flush=True)

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
try:
    d = word.Documents.Open(LOCAL, ReadOnly=True, AddToRecentFiles=False)
    d.PrintOut(Background=False)   # 默认打印机=PDFCreator
    d.Close(False)
finally:
    word.Quit(); pythoncom.CoUninitialize()

newpdf = None
for _ in range(120):  # 轮询至多120秒
    time.sleep(1)
    cur = set(os.listdir(SPOOL)) - before
    pdfs = [f for f in cur if f.lower().endswith('.pdf')]
    if pdfs:
        newpdf = os.path.join(SPOOL, pdfs[0]); break
if not newpdf:
    print('NO PDF FROM SPOOL — task list:', list(set(os.listdir(SPOOL))-before)); sys.exit(2)
print('got task file:', os.path.basename(newpdf), flush=True)
doc = fitz.open(newpdf)
print('pages:', doc.page_count, flush=True)
for i in range(min(3, doc.page_count)):
    doc[i].get_pixmap(dpi=80).save(os.path.join(OUTDIR, f"册目录页_p{i+1}.png"))
doc.close()
inf = newpdf[:-4] + '.inf'
for f in [newpdf, inf]:
    if os.path.exists(f): os.remove(f)
print('cleaned task files OK', flush=True)
