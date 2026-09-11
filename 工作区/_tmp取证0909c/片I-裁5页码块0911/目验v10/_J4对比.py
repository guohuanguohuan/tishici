# -*- coding: utf-8 -*-
"""J4 拉伸对比：同一判据（CJK-CJK 隙>0.5×字号）跑 v9 包内样张页 vs v10 现件。"""
import io
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
MM2PT = 72 / 25.4


def is_cjk(ch):
    o = ord(ch)
    return 0x3000 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or 0x2018 <= o <= 0x201D


def j4(pdf, pages, tag):
    doc = pymupdf.open(pdf)
    out = []
    for i in pages:
        page = doc[i - 1]
        for b in page.get_text("rawdict")["blocks"]:
            if b.get("type") != 0:
                continue
            for l in b["lines"]:
                for sp in l["spans"]:
                    chars = sp["chars"]
                    for a, c in zip(chars, chars[1:]):
                        if not (a["c"].strip() and c["c"].strip()):
                            continue
                        if is_cjk(a["c"]) and is_cjk(c["c"]):
                            gap = (c["bbox"][0] - a["bbox"][2]) * MM2PT
                            if gap > 0.5 * sp["size"]:
                                out.append((i, round(gap, 2), a["c"], c["c"]))
    print(tag, len(out), out[:8])
    doc.close()


j4(r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf', [13, 14], 'v9样张p13-14:')
j4(r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\答案册\main.pdf', [1, 2], 'v10样张现件:')
j4(r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf', [7, 8, 9, 10], 'v9册v1p7-10:')
j4(r'C:\提示词\工作区\字替对照-0909\导学件答案册-v1\main.pdf', [1, 2, 3, 4], 'v10册v1现件:')
