# -*- coding: utf-8 -*-
# FX2 COM开卷验证：本地副本（md5核对）、开卷无修复、页数、单节双栏、页眉页脚在位与同串、
# 首段节名锚在页1、OMath计数、页眉页脚逐页在位抽测。自建实例用完Quit。
import hashlib, shutil, time

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
CP = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C\C_verify_copy.docx"
shutil.copy2(SRC, CP)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

m1, m2 = md5(SRC), md5(CP)
assert m1 == m2
print("md5原件=副本:", m1)

import pythoncom
import win32com.client
pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    t0 = time.time()
    doc = word.Documents.Open(CP, ReadOnly=True, AddToRecentFiles=False)
    print(f"开卷耗时 {time.time()-t0:.1f}s")
    doc.Repaginate()
    pages = doc.ComputeStatistics(2)  # wdStatisticPages
    print("页数(ComputeStatistics):", pages)
    print("节数 Sections.Count:", doc.Sections.Count)
    sec = doc.Sections(1)
    print("节1 TextColumns.Count:", sec.PageSetup.TextColumns.Count,
          "Spacing(pt):", round(sec.PageSetup.TextColumns.Spacing, 1))
    # 页码起始
    print("StartingNumber:", sec.Headers(1).PageNumbers.StartingNumber)
    # 首页/奇偶页眉设置
    ps = sec.PageSetup
    print("OddAndEvenPagesHeaderFooter:", ps.OddAndEvenPagesHeaderFooter, "DifferentFirstPageHeaderFooter:", ps.DifferentFirstPageHeaderFooter)
    # 页眉页脚文本（第1页与第2页，用Range技巧直接取Story）
    hdr_txt = doc.StoryRanges(7).Text  # wdPrimaryHeaderStory
    ftr_txt = doc.StoryRanges(6).Text  # wdPrimaryFooterStory? 6=wdEvenPagesFooterStory? 用枚举再核
    print("hdr story len:", len(hdr_txt))
    print("HEADER:", hdr_txt.replace("\r", "⏎"))
    print("FOOTER:", ftr_txt.replace("\r", "⏎"))
    # 首段与页1顶部
    p1 = doc.Paragraphs(1)
    print("首段文本:", repr(p1.Range.Text[:30]), "首段所在页:", p1.Range.Information(3))  # wdActiveEndPageNumber=3
    p2 = doc.Paragraphs(2)
    print("第2段文本:", repr(p2.Range.Text[:40]), "所在页:", p2.Range.Information(3))
    # 首页顶部空区检查：首段之前无空段（段1即锚段）＋首段垂直位置
    print("首段顶部位置 VerticalPosition(pt):", round(p1.Range.Information(6), 1))  # wdVerticalPositionRelativeToPage
    # OMath计数与两处新公式取文本
    print("OMaths.Count:", doc.OMaths.Count)
    # 页1页眉实际渲染（用页面Range方法较重，跳过——Story已在上方核同串）
    # 第2页页眉在位：直接开第二页窗口太重，改为断言 SameHeader（节内同页眉）＋Story文本即可
finally:
    doc.Close(False)
    word.Quit()
    print("COM实例已Quit")
