# -*- coding: utf-8 -*-
"""A1审计：Word COM 开卷实测页数（自建实例/ReadOnly/用完Quit）＋§12上限"""
import os, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client as w32
import pythoncom

SRC = r"C:\提示词\高中数学\高中数学同步"
FILES = {
    "X1": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "I1": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "B":  "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
    "C":  "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
}
EXPECT = {"X1":16, "I1":14, "B":53, "C":61}

pythoncom.CoInitialize()
word = w32.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
res = {}
try:
    for tag, name in FILES.items():
        path = os.path.join(SRC, name)
        doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False, Visible=False)
        try:
            doc.Repaginate()
            pages = doc.ComputeStatistics(2)  # wdStatisticPages
            res[tag] = pages
            print(f"{tag}\tCOM实测页数={pages}\t规格书登记={EXPECT[tag]}\t{'一致' if pages==EXPECT[tag] else '!!不一致'}")
        finally:
            doc.Close(SaveChanges=0)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print("Done. Word实例已Quit。")
rep = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_reports\COM页数.txt"
open(rep,'w',encoding='utf-8').write('\n'.join(f"{k}={v}" for k,v in res.items()))
# 残留进程自检
import subprocess
r = subprocess.run(["tasklist","/FI","IMAGENAME eq WINWORD.EXE"],capture_output=True,text=True)
print(r.stdout[-300:])
