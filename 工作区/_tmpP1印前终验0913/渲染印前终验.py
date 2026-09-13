# -*- coding: utf-8 -*-
# P1 印前终验逐页渲染（只读既有 PDF，仅写本目录 PNG）
import pymupdf, os

SRC = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/装配"
OUT = r"C:/提示词/工作区/_tmpP1印前终验0913/测评本 1-3"
os.makedirs(OUT, exist_ok=True)

ZOOM = 150 / 72  # 150dpi
PLAN = [  # (pdf名, 起全局页号, 输出页号列表)
    ("导学本.pdf", 1, list(range(1, 17))),
    ("练习本.pdf", 17, list(range(17, 31))),
    ("拓展本.pdf", 31, list(range(31, 41))),
    ("测评本.pdf", 41, list(range(41, 44))),
    ("答案本.pdf", 44, list(range(44, 49))),
    ("学史切片.pdf", 1, ["学史1"]),
]

for name, start, pages in PLAN:
    doc = pymupdf.open(os.path.join(SRC, name))
    print(f"{name}: {doc.page_count}页")
    for i, target in enumerate(pages):
        if i >= doc.page_count:
            print(f"  !! 页数不足: 目标{target} 越界"); continue
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM))
        fn = os.path.join(OUT, f"page-{target}.png")
        pix.save(fn)
    print(f"  → 已出 {min(len(pages), doc.page_count)} 张 png")
    doc.close()
print("完成。共", len(os.listdir(OUT)), "文件")
