# -*- coding: utf-8 -*-
"""FX9: unpack document.xml from E/H/X1 backups (current deployed state)."""
import zipfile, shutil, os

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\FX9"
files = {
    "E": "E_backup.docx",
    "H": "H_backup.docx",
    "X1": "X1_backup.docx",
}
for tag, fn in files.items():
    src = os.path.join(BASE, fn)
    dst = os.path.join(BASE, tag + "_document.xml")
    with zipfile.ZipFile(src) as z:
        data = z.read("word/document.xml")
        names = z.namelist()
    with open(dst, "wb") as f:
        f.write(data)
    print(tag, "parts:", len(names), "document.xml bytes:", len(data))
print("done")
