# -*- coding: utf-8 -*-
"""滚A 新版 Q3 选项行 字符级 2D 墨迹碰撞复验（x 与 y 同时相交才算真压字）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

NEW = r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A\main.pdf"
OLD = r"C:\提示词\工作区\_tmp滚A修Q3压字0913\_probe-旧版\main.pdf"
MM = 72 / 25.4
COMB = 0x20D7


def chars(pdf, y0, y1):
    d = pymupdf.open(pdf)
    out = []
    for blk in d[0].get_text("rawdict")["blocks"]:
        for ln in blk.get("lines", []):
            for s in ln["spans"]:
                for c in s["chars"]:
                    b = c["bbox"]
                    if y0 <= b[1] / MM <= y1 and b[0] / MM < 132 and ord(c["c"]) != COMB:
                        out.append((c["c"], b[0] / MM, b[1] / MM, b[2] / MM, b[3] / MM))
    d.close()
    return out


def collide(a, b):
    # 元组＝(字符, x0, y0, x1, y1)
    xo = min(a[3], b[3]) - max(a[1], b[1])
    yo = min(a[4], b[4]) - max(a[2], b[2])
    return (xo, yo) if (xo > 0.2 and yo > 0.2) else None


for tag, pdf, bands in (("旧版", OLD, ((109.5, 113.0),)),
                        ("新版", NEW, ((109.5, 113.0), (115.5, 119.0)))):
    print(f"===== {tag} {pdf.split(chr(92))[-3]} =====")
    tot = 0
    for y0, y1 in bands:
        cs = chars(pdf, y0, y1)
        hits = []
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                r = collide(cs[i], cs[j])
                if r:
                    hits.append((cs[i][0], cs[j][0], round(r[0], 2), round(r[1], 2)))
        tot += len(hits)
        print(f"  y {y0}~{y1}mm 字符数={len(cs)} 真2D墨迹碰撞对={len(hits)}")
        for h in hits[:12]:
            print(f"     «{h[0]}»×«{h[1]}» x侵入{h[2]}mm y侵入{h[3]}mm")
    print(f"  >>> {tag} Q3 区真碰撞合计 = {tot}")
