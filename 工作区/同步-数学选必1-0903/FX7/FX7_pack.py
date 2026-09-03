# -*- coding: utf-8 -*-
"""FX7 pack: 将四件unpack目录回包覆盖原位docx（保留其余zip条目，重写document.xml等被改部件）
本脚本只打包被修改的word/document.xml，其余条目原样字节级复制自原docx，最小扰动。"""
import os, zipfile, shutil

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
SYNC = r"C:\提示词\高中数学\高中数学同步"
FILES = {
    "X1": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "I1": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "X2": "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
    "I2": "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
}

for tag, name in FILES.items():
    src = os.path.join(SYNC, name)
    newdoc = open(os.path.join(WK, "unpack", tag, "word", "document.xml"), "rb").read()
    tmp = os.path.join(WK, "tmp_pack_" + tag + ".docx")
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = newdoc if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    # 校验回包可读
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        assert z.read("word/document.xml") == newdoc
    shutil.move(tmp, src)
    print(tag, "repacked ->", src, os.path.getsize(src), "bytes")
print("done")
