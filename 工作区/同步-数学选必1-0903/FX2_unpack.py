# FX2: 解包C件XML到tmp/FX2_C/（只读提取，不修改原件）
import zipfile, os, shutil

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    p = os.path.join(OUT, f)
    if os.path.isfile(p):
        os.remove(p)
with zipfile.ZipFile(SRC) as z:
    names = z.namelist()
    for n in names:
        if n in ("word/document.xml", "word/header1.xml", "word/footer1.xml",
                 "word/settings.xml", "word/styles.xml", "[Content_Types].xml",
                 "word/_rels/document.xml.rels") or n.startswith("word/header") or n.startswith("word/footer"):
            z.extract(n, OUT)
print("extracted:", sorted(os.listdir(os.path.join(OUT, "word"))))
# 备份document/header/footer原样供diff
for n in ("word/document.xml", "word/header1.xml", "word/footer1.xml"):
    src = os.path.join(OUT, n.replace("/", os.sep))
    bak = src + ".orig"
    shutil.copy2(src, bak)
print("orig backups done")
