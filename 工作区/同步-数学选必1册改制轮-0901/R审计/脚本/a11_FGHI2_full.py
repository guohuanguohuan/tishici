# -*- coding: utf-8 -*-
"""R1审计——F/G/H/I2全件PDF导出＋全部页页脚实压判定。"""
import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
import fitz
import numpy as np
import win32com.client as wc

D = r'C:\提示词\高中数学\高中数学同步'
PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
FILES = [('F','人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
         ('G','人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
         ('H','人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
         ('I2','人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx')]
word = wc.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
try:
    for code, fn in FILES:
        local = os.path.join(PDFDIR, code + '_full_local.docx')
        shutil.copy2(os.path.join(D, fn), local)
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        pdf = os.path.join(PDFDIR, code + '_full.pdf')
        doc.ExportAsFixedFormat(pdf, 17, False, 0, 0)
        doc.Close(False)
        os.remove(local)
        print('exported', code, os.path.getsize(pdf))
finally:
    word.Quit()

FOOT = fitz.Rect(40, 782, 540, 804)
def dark(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(4,4), clip=FOOT, colorspace=fitz.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a < 128
for code, _ in FILES:
    docz = fitz.open(os.path.join(PDFDIR, code + '_full.pdf'))
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
            bad.append((pi+1, rec))
    print('%s_full 页数=%d 页脚实压页=%s' % (code, docz.page_count, bad or '无'))
    docz.close()
