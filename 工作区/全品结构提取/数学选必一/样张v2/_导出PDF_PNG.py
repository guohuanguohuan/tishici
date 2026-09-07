# -*- coding: utf-8 -*-
"""v2样张 docx -> PDF (Word COM 主路径) -> PNG (pymupdf 150dpi)"""
import os, sys, glob

BASE = r"工作区/全品结构提取/数学选必一/样张v2"
DOCX = os.path.abspath(os.path.join(BASE, "人教B版选必1-1.1.1-v2样张.docx"))
PDF  = os.path.abspath(os.path.join(BASE, "人教B版选必1-1.1.1-v2样张.pdf"))
PNGD = os.path.abspath(os.path.join(BASE, "png"))
os.makedirs(PNGD, exist_ok=True)
for f in glob.glob(os.path.join(PNGD, "*.png")): os.remove(f)

pages = None
try:
    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    d = word.Documents.Open(DOCX, ReadOnly=False, AddToRecentFiles=False)
    d.SaveAs2(PDF, FileFormat=17)
    pages = d.ComputeStatistics(2)  # wdStatisticPages
    d.Close(False)
    word.Quit()
    print(f"[COM] Word 导出成功，实测页数 = {pages}")
except Exception as e:
    print("[COM] 失败:", repr(e))
    if "word" in dir(): pass
    try: word.Quit()
    except Exception: pass
    r = os.system(f'soffice --headless --convert-to pdf --outdir "{os.path.dirname(PDF)}" "{DOCX}"')
    print("[soffice] 退路返回码:", r)

if not os.path.exists(PDF):
    sys.exit("PDF 不存在，导出失败")

import pymupdf
doc = pymupdf.open(PDF)
names = []
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    p = os.path.join(PNGD, f"p{i+1:02d}.png")
    pix.save(p); names.append(p)
print(f"[pymupdf] PDF 页数 = {doc.page_count}，渲染 {len(names)} 张 PNG @150dpi")
for n in names: print("  ", n)
