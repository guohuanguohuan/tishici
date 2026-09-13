# -*- coding: utf-8 -*-
"""滚A 修后收尾：①旧版同位 600dpi 对照裁片 ②第2页零回归（文本＋像素摘要）③栏1 行数增量账。"""
import io, sys, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

NEW = r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A\main.pdf"
OLD = r"C:\提示词\工作区\_tmp滚A修Q3压字0913\_probe-旧版\main.pdf"
OUT = r"C:\提示词\工作区\_tmp滚A修Q3压字0913"
MM = 72 / 25.4

dn, do = pymupdf.open(NEW), pymupdf.open(OLD)

# ① 旧版同位裁片（题干＋被挤在一行的四选项）
clip = pymupdf.Rect(8 * MM, 98 * MM, 132 * MM, 118 * MM)
do[0].get_pixmap(dpi=600, clip=clip).save(OUT + r"\600dpi-滚A-Q3选项裁片-旧版对照.png")
print("旧版对照裁片 →", OUT + r"\600dpi-滚A-Q3选项裁片-旧版对照.png")

# ② 第 2 页零回归
for pno in (1,):
    t1, t2 = dn[pno].get_text(), do[pno].get_text()
    h1 = hashlib.md5(dn[pno].get_pixmap(dpi=300).samples).hexdigest()
    h2 = hashlib.md5(do[pno].get_pixmap(dpi=300).samples).hexdigest()
    print(f"第{pno+1}页 文本一致={t1 == t2} 像素一致(300dpi md5)={h1 == h2} 文本长度={len(t1)}/{len(t2)}")

# ③ 第 1 页栏1 行数账（应 +1 行，且其余两栏不动）
def col_lines(doc, pno, x0, x1):
    ys = set()
    for blk in doc[pno].get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            if x0 <= ln["bbox"][0] / MM < x1:
                ys.add(round(ln["bbox"][1] / MM, 1))
    return len(ys)

for name, (a, b) in (("栏1", (8, 130)), ("栏2", (130, 251)), ("栏3", (251, 400))):
    print(f"第1页 {name} 行数 旧={col_lines(do,0,a,b)} 新={col_lines(dn,0,a,b)}")
dn.close(); do.close()
