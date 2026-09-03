# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom
import fitz

SYNC=r"C:\提示词\高中数学\高中数学同步"
OUT=r"C:\提示词\工作区\同步-数学选必1-0903\probe_blank\render"
jobs=[
 ("讲练1上首屏", os.path.join(os.path.dirname(OUT),"jl1_head.docx")),
 ("衔接2", os.path.join(SYNC,"人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx")),
 ("部分封面-讲练1", os.path.join(SYNC,"人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx")),
 ("使用说明", os.path.join(SYNC,"人教B版选必1·使用说明.docx")),
]
pythoncom.CoInitialize()
word=win32com.client.DispatchEx('Word.Application')
word.Visible=False; word.DisplayAlerts=0
try:
    for tag,path in jobs:
        print('open',tag,flush=True)
        d=word.Documents.Open(path,ReadOnly=True,AddToRecentFiles=False)
        pdf=os.path.join(OUT,tag+'.pdf')
        d.ExportAsFixedFormat(pdf,17)
        d.Close(False)
        doc=fitz.open(pdf)
        print(tag,'pages:',doc.page_count,flush=True)
        for i in range(min(2,doc.page_count)):
            doc[i].get_pixmap(dpi=80).save(os.path.join(OUT,f"{tag}_p{i+1}.png"))
        doc.close()
finally:
    word.Quit(); pythoncom.CoUninitialize()
print('ALL DONE',flush=True)
