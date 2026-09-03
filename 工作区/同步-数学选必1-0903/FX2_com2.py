# -*- coding: utf-8 -*-
# FX2 COM补验2：Section.Headers/Footers同串＋两处新oMath段渲染文本＋逐页页眉页脚抽测
import shutil

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
CP = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C\C_verify_copy.docx"
shutil.copy2(SRC, CP)

import pythoncom
import win32com.client
pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(CP, ReadOnly=True, AddToRecentFiles=False)
    sec = doc.Sections(1)
    print("HEADER:", sec.Headers(1).Range.Text.replace("\r", "⏎"))
    print("FOOTER:", sec.Footers(1).Range.Text.replace("\r", "⏎"))
    print("FOOTER.PageNumbers预览/起始:", sec.Footers(1).PageNumbers.StartingNumber)
    # 两处新公式段Word端渲染文本
    print("--- 段65:", doc.Paragraphs(65).Range.Text.strip()[:170])
    print("--- 段484:", doc.Paragraphs(484).Range.Text.strip()[:170])
    # 逐页页脚在位抽测：第1/30/60页
    doc.Repaginate()
    n = doc.ComputeStatistics(2)
    print("页数:", n)
    for pg in (1, 30, n):
        r = doc.GoTo(True, 1, 1, pg) if False else doc.GoTo(What=1, Which=1, Count=pg)  # wdGoToPage
        pn = r.Information(3)
        print(f"GoTo第{pg}页→实际页{pn}")
finally:
    doc.Close(False)
    word.Quit()
    print("COM实例已Quit")
