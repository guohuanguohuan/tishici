# -*- coding: utf-8 -*-
"""FX6 打包部署：tmp/FX6_H → 原位H件（仅document.xml变更，其余部件字节原样）"""
import zipfile, shutil, os, hashlib

BAK = r"C:\提示词\工作区\同步-数学选必1-0903\FX6\H_备份-0903.docx"
DST = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx"
NEWDOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\FX6\H_fixed.docx"

with open(NEWDOC, "rb") as f:
    newdoc = f.read()

changed = []
with zipfile.ZipFile(BAK) as zin, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            if data != newdoc:
                changed.append((item.filename, hashlib.md5(data).hexdigest(), hashlib.md5(newdoc).hexdigest()))
            data = newdoc
        zout.writestr(item, data)

print("entries:", len(zipfile.ZipFile(OUT).namelist()))
print("changed parts:", changed)
print("OUT:", OUT, os.path.getsize(OUT), "bytes")

# 部署（原位覆盖）
shutil.copyfile(OUT, DST)
print("DEPLOYED:", DST)
with open(DST, "rb") as f:
    print("deployed md5:", hashlib.md5(f.read()).hexdigest())
