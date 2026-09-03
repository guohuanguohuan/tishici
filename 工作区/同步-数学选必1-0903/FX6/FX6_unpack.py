# -*- coding: utf-8 -*-
"""FX6 解包H件到 tmp/FX6_H/word（一次性脚本）"""
import zipfile, shutil, os
SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx"
DST = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H"
if os.path.exists(os.path.join(DST, "word")):
    shutil.rmtree(os.path.join(DST, "word"))
with zipfile.ZipFile(SRC) as z:
    z.extractall(DST)
    names = z.namelist()
print("entries:", len(names))
print("has document.xml:", os.path.exists(os.path.join(DST, "word", "document.xml")))
