# -*- coding: utf-8 -*-
#
# 收编：2026-08-27 选必1整册任务·F2收尾（来源轮次：A4样张首创五杠杆 → C5参数化定稿；此为工具文件夹唯一常驻版，A4/C5桌面scripts副本不再维护）
#
# 用法: python 工具/COM页数实测.py <a.docx> [b.docx ...]
# 功能: Word COM 自建实例(DispatchEx)只读开卷 Repaginate 实测页数，用完 Quit——紧凑化铺开与盖章前的标准页数口径

"""count_pages.py — Word COM 实测页数（自建实例，用完Quit）
用法: python count_pages.py <docx> [docx2 ...]"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for src in sys.argv[1:]:
        src = os.path.abspath(src)
        d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        try:
            d.Repaginate()
            pages = d.ComputeStatistics(2)   # wdStatisticPages
            print(os.path.basename(src), '->', pages, 'pages')
        finally:
            d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
