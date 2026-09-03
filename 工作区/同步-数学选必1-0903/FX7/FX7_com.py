# -*- coding: utf-8 -*-
"""FX7 COM页数实测（自建实例ReadOnly、用完Quit）"""
import win32com.client, os

SYNC = r"C:\提示词\高中数学\高中数学同步"
FILES = [
    ("X1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx", 16),
    ("I1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx", 14),
    ("X2", "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx", 6),
    ("I2", "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx", 28),
]
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    for tag, name, base in FILES:
        p = os.path.join(SYNC, name)
        doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        print(f"{tag}: COM实测页数={pages}（基线{base}）{'✓不变' if pages == base else '⚠变化'}")
        doc.Close(False)
finally:
    word.Quit()
print("COM done, instance quit")
