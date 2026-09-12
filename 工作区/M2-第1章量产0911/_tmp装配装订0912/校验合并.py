# -*- coding: utf-8 -*-
# 装配产物校验：页脚印刷页码连续性（取每页底部 60pt 文字）＋书签清单
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ASM = r"C:\提示词\工作区\M2-第1章量产0911\成卷\装配"
CHECK = {  # 书名: [(物理页1基, 期望印刷页码列表...)]
    "导学本.pdf": [1, 21, 44],
    "练习本.pdf": [1, 10, 21, 38],
    "测评本.pdf": [1, 4, 7],
    "答案本.pdf": [1, 7, 14],
}
START = {"导学本.pdf": 1, "练习本.pdf": 45, "测评本.pdf": 83, "答案本.pdf": 90}
for fn, pages in CHECK.items():
    d = pymupdf.open(os.path.join(ASM, fn))
    print(f"== {fn}（{len(d)}页）书签{len(d.get_toc())}条")
    for lvl, title, pg in d.get_toc():
        print(f"   {'  '*(lvl-1)}p{pg:>3d} {title}")
    base = START[fn]
    for p in pages:
        pg = d[p - 1]
        r = pg.rect
        foot = pg.get_text(clip=pymupdf.Rect(0, r.height - 55, r.width, r.height)).replace("\n", " ")
        foot = " ".join(foot.split())
        print(f"   物理{p:>2d} 期望页码{base + p - 1:>3d} | 页脚: {foot[:80]}")
    d.close()
