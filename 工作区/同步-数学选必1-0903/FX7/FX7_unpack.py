# -*- coding: utf-8 -*-
"""FX7 unpack: 解包四件（原位编辑对象）+ B讲练件（只读参照）到 FX7/unpack/"""
import zipfile, os, shutil

BASE = r"C:\提示词"
SYNC = os.path.join(BASE, "高中数学", "高中数学同步")
WK = os.path.join(BASE, "工作区", "同步-数学选必1-0903", "FX7")

FILES = {
    "X1": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "I1": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "X2": "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
    "I2": "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
    "B":  "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",  # 只读参照
}

for tag, name in FILES.items():
    src = os.path.join(SYNC, name)
    dst = os.path.join(WK, "unpack", tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    with zipfile.ZipFile(src) as z:
        z.extractall(dst)
    # 只读参照B：仅留document.xml，防止误改
    if tag == "B":
        pass
    print(tag, "unpacked ->", dst)
print("done")
