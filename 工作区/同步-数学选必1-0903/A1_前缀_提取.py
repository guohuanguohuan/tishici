# -*- coding: utf-8 -*-
"""A1审计：解包被审docx的XML部件到 tmp/A1_parts/（只读审计，不改原文件）"""
import zipfile, os, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = r"C:\提示词\高中数学\高中数学同步"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_parts"
FILES = {
    "X1": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "I1": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "B":  "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
    "C":  "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
    "E":  "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",  # 前缀宽度旁证
}
shutil.rmtree(OUT, ignore_errors=True)
for tag, name in FILES.items():
    d = os.path.join(OUT, tag)
    os.makedirs(d, exist_ok=True)
    src = os.path.join(SRC, name)
    with zipfile.ZipFile(src) as z:
        for n in z.namelist():
            z.extract(n, d)
    sz = os.path.getsize(src)
    print(f"{tag}\t{sz/1048576:.2f}MB\t{len(os.listdir(os.path.join(d,'word')))} parts")
print("done ->", OUT)
