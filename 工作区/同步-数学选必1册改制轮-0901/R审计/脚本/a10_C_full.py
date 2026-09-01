# -*- coding: utf-8 -*-
"""R1审计——C件全件PDF导出（§14异常回退全件检查）＋全部页页脚实压判定＋其余5页件XML级预测。"""
import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
import fitz
import numpy as np
import win32com.client as wc

D = r'C:\提示词\高中数学\高中数学同步'
PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
src = os.path.join(D, '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx')
local = os.path.join(PDFDIR, 'C_full_local.docx')
shutil.copy2(src, local)
word = wc.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
pdf = os.path.join(PDFDIR, 'C_full.pdf')
doc.ExportAsFixedFormat(pdf, 17, False, 0, 0)
doc.Close(False)
word.Quit()
os.remove(local)
print('exported', os.path.getsize(pdf))

FOOT = fitz.Rect(40, 782, 540, 804)
def dark(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(4,4), clip=FOOT, colorspace=fitz.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a < 128
docz = fitz.open(pdf)
print('C_full 页数=', docz.page_count)
bad = []
for pi in range(docz.page_count):
    page = docz[pi]
    before = dark(page)
    page.add_redact_annot(FOOT)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                          graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_NONE)
    after = dark(page)
    rec = int((after & ~before).sum())
    if rec > 300:
        bad.append((pi+1, rec, int(before.sum()), int(after.sum())))
print('C_full 页脚实压页（recovered>300px）:', bad)
docz.close()
