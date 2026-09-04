# -*- coding: utf-8 -*-
import zipfile, re, difflib, os
BAK = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\tmp\章码重盖前备份"
SYNC = r"C:\提示词\高中数学\高中数学同步"
for k, fn in [("C","人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"),
              ("H","人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx")]:
    a = zipfile.ZipFile(os.path.join(BAK, fn)).read("word/document.xml").decode("utf-8")
    b = zipfile.ZipFile(os.path.join(SYNC, fn)).read("word/document.xml").decode("utf-8")
    print("====", k, "len old/new:", len(a), len(b))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(tag, "OLD:", repr(a[max(0,i1-80):i2+80]))
            print(tag, "NEW:", repr(b[max(0,j1-80):j2+80]))
