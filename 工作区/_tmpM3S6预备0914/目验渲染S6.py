# -*- coding: utf-8 -*-
"""S6 目验渲染（照 S4 制）：插桩 9 图所在页渲染 PNG 落 目验S6/。只读 PDF＋写 PNG。"""
import io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

G = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
OUT = r"C:\提示词\工作区\_tmpM3S6预备0914\目验S6"
os.makedirs(OUT, exist_ok=True)

PIECES = {
    "课时02": "课时02-倾斜角与斜率", "课时10": "课时10-2.4曲线与方程",
    "课时14": "课时14-2.6.2双曲线性质", "课时16": "课时16-2.7.2抛物线性质",
}
n = 0
for pid, d in PIECES.items():
    doc = pymupdf.open(os.path.join(G, d, "main-true.pdf"))
    for pno in range(len(doc)):
        page = doc[pno]
        if page.get_images(full=True):
            pix = page.get_pixmap(dpi=110)
            f = os.path.join(OUT, "%s-p%d.png" % (pid, pno + 1))
            pix.save(f)
            n += 1
            print(f)
    doc.close()
print("渲染含图页", n, "张")
