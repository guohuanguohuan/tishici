# -*- coding: utf-8 -*-
"""J 族同类风险旁证：三件卷 PDF 全页字符级 x 侵入 >2.5mm 的真压字普查（只读，不编译不改件）。"""
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
COMB = 0x20D7
MM = 72 / 25.4

for it in (r"\滚动卷\滚A\main.pdf", r"\滚动卷\滚B\main.pdf", r"\测评卷\main.pdf"):
    d = pymupdf.open(ROOT + it)
    tot = []
    for pno in range(d.page_count):
        cs = []
        for blk in d[pno].get_text("rawdict")["blocks"]:
            for ln in blk.get("lines", []):
                for s in ln["spans"]:
                    for c in s["chars"]:
                        if ord(c["c"]) == COMB:
                            continue
                        b = c["bbox"]
                        cs.append((c["c"], b[0] / MM, b[1] / MM, b[2] / MM, b[3] / MM))
        bk = collections.defaultdict(list)
        for c in cs:
            bk[round(c[2] / 2.0)].append(c)
        for row in bk.values():
            row.sort(key=lambda t: t[1])
            for i in range(len(row)):
                for j in range(i + 1, min(i + 12, len(row))):
                    if row[j][1] - row[i][3] > 0:
                        break
                    xo = min(row[i][3], row[j][3]) - max(row[i][1], row[j][1])
                    yo = min(row[i][4], row[j][4]) - max(row[i][2], row[j][2])
                    if xo > 2.5 and yo > 2.5:
                        tot.append((pno + 1, round(row[i][2], 1), row[i][0], row[j][0], round(xo, 2)))
    print(f"{it.split(chr(92))[-2]:6s} 真压字对(x>2.5mm∩y>2.5mm) = {len(tot)}  页数={d.page_count}")
    for t in tot[:8]:
        print("    页%s y=%smm «%s»×«%s» x侵入%smm" % t)
    d.close()
