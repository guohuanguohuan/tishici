# -*- coding: utf-8 -*-
"""滚A 修后终检：①全页字符级 2D 碰撞普查（分型）②600dpi 整页＋Q3 局部裁片实证。"""
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

NEW = r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A\main.pdf"
OUT = r"C:\提示词\工作区\_tmp滚A修Q3压字0913"
MM = 72 / 25.4
COMB = 0x20D7

d = pymupdf.open(NEW)
pg = d[0]

# ---------- ① 全页三栏 字符级 2D 碰撞普查 ----------
cs = []
for blk in pg.get_text("rawdict")["blocks"]:
    for ln in blk.get("lines", []):
        for s in ln["spans"]:
            for c in s["chars"]:
                if ord(c["c"]) == COMB:
                    continue
                b = c["bbox"]
                cs.append((c["c"], b[0] / MM, b[1] / MM, b[2] / MM, b[3] / MM))
print("全页字符数（去组合箭头）=", len(cs))

# 按 y 分桶后仅比同桶，避免 O(n^2) 全比
buckets = collections.defaultdict(list)
for c in cs:
    buckets[round(c[2] / 2.0)].append(c)
hits = []
for b in buckets.values():
    b.sort(key=lambda t: t[1])
    for i in range(len(b)):
        for j in range(i + 1, min(i + 12, len(b))):
            if b[j][1] - b[i][3] > 0:
                break
            xo = min(b[i][3], b[j][3]) - max(b[i][1], b[j][1])
            yo = min(b[i][4], b[j][4]) - max(b[i][2], b[j][2])
            if xo > 0.2 and yo > 0.2:
                hits.append((round(b[i][2], 1), b[i][0], b[j][0], round(xo, 2), round(yo, 2)))
print("全页 x∩y 双相交（>0.2mm）字符对 =", len(hits))
pat = collections.Counter(tuple(sorted((h[1], h[2]))) for h in hits)
print("按字符对型别汇总（top12）：")
for k, v in pat.most_common(12):
    print(f"   {k[0]}×{k[1]} : {v}")
big = [h for h in hits if h[3] > 2.5]
print("x 侵入 >2.5mm 的重灾对 =", len(big))
for h in big[:10]:
    print("   ", h)

# ---------- ② 600dpi 出图 ----------
for pno in range(d.page_count):
    d[pno].get_pixmap(dpi=600).save(OUT + rf"\600dpi-滚A-p{pno+1}.png")
clip = pymupdf.Rect(8 * MM, 98 * MM, 132 * MM, 124 * MM)     # Q3 题干＋两行选项
pm = pg.get_pixmap(dpi=600, clip=clip)
pm.save(OUT + r"\600dpi-滚A-Q3选项裁片.png")
print("600dpi 出图：整页×%d ＋ Q3 裁片 %dx%d px" % (d.page_count, pm.width, pm.height))
d.close()
