import os, sys
import win32com.client
import fitz

SRC = r"C:\提示词\高中数学\高中数学同步"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\probe_blank\render"
files = [
    ("讲练1上", "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"),
    ("衔接1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx"),
    ("清单1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx"),
    ("部分封面-讲练1", "人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx"),
    ("使用说明", "人教B版选必1·使用说明.docx"),
]
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    for tag, fn in files:
        path = os.path.join(SRC, fn)
        pdf = os.path.join(OUT, tag + ".pdf")
        doc = word.Documents.Open(path, ReadOnly=True)
        doc.ExportAsFixedFormat(pdf, 17)  # wdExportFormatPDF
        doc.Close(False)
        d = fitz.open(pdf)
        n = min(3, d.page_count)
        for i in range(n):
            pix = d[i].get_pixmap(dpi=80)
            pix.save(os.path.join(OUT, f"{tag}_p{i+1}.png"))
        print(tag, "pages:", d.page_count, "-> rendered", n)
        d.close()
finally:
    word.Quit()
print("OK")
