# -*- coding: utf-8 -*-
# 装配轮·目验渲染：关键页 150dpi png → _tmpP1装配0912/目验/
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf
ASM = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\装配"
OUT = r"C:\提示词\工作区\_tmpP1装配0912\目验"
os.makedirs(OUT, exist_ok=True)
JOBS = [
    ("册目录页.pdf", [1], "目录"),
    ("导学本.pdf", [3, 4, 11, 14, 15, 16], "导学界"),   # 件界 3|4 / 11 首 / 14|15 章末首 / 16|17 本界
    ("练习本.pdf", [1, 3, 4, 7, 10, 13, 14], "练习"),   # 本首＋内部件界＋14(P30=本界尾)
    ("拓展本.pdf", [1, 10], "拓展"),
    ("测评本.pdf", [1, 2, 3], "测评"),                    # 全 3 页（清扫＋速查表专改）
    ("答案本.pdf", [1, 2, 3, 4, 5], "答案"),              # 全 5 页（义6-1 新页流）
    ("学史切片.pdf", [1], "学史"),
]
for fn, pages, tag in JOBS:
    d = pymupdf.open(os.path.join(ASM, fn))
    for p in pages:
        pix = d[p - 1].get_pixmap(dpi=150)
        out = os.path.join(OUT, f"{tag}-p{p:02d}.png")
        pix.save(out)
    d.close()
print("rendered:", sorted(os.listdir(OUT)))
