# -*- coding: utf-8 -*-
"""FX6 COM验证：开卷/节/栏/起始页码/页数/首段/页眉同串（自建实例用完Quit）"""
import win32com.client, pythoncom

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx"
pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(SRC, ReadOnly=True, AddToRecentFiles=False)
    print("opened OK (无修复对话框)")
    print("Sections.Count =", doc.Sections.Count)
    sec = doc.Sections(1)
    print("TextColumns.Count =", sec.PageSetup.TextColumns.Count)
    print("TextColumns.Spacing(pt) =", round(sec.PageSetup.TextColumns.Spacing, 1))
    print("StartPageNumber =", sec.Headers(1).PageNumbers.StartingNumber)
    print("PageSetup: W×H(pt) =", round(sec.PageSetup.PageWidth,1), "×", round(sec.PageSetup.PageHeight,1))
    print("Margins T/B/L/R(pt) =", [round(x,1) for x in (sec.PageSetup.TopMargin, sec.PageSetup.BottomMargin, sec.PageSetup.LeftMargin, sec.PageSetup.RightMargin)])
    print("HeaderDist/FooterDist =", round(sec.PageSetup.HeaderDistance,1), round(sec.PageSetup.FooterDistance,1))
    print("ComputedPages =", doc.ComputeStatistics(2))  # wdStatisticPages
    print("FirstPara =", repr(doc.Paragraphs(1).Range.Text[:40]))
    print("Para2 =", repr(doc.Paragraphs(2).Range.Text[:40]))
    print("Para3 =", repr(doc.Paragraphs(3).Range.Text[:40]))
    hdr = sec.Headers(1).Range.Text
    ftr = sec.Footers(1).Range.Text
    print("Header =", repr(hdr))
    print("Footer =", repr(ftr))
    print("OMaths.Count =", doc.OMaths.Count)
    doc.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print("COM DONE (Quit)")
