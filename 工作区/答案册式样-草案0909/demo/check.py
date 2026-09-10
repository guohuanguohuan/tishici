"""答案册式样草案 demo 自检（编译三 0 ＋ 关键几何/色值实测）。

口径：编译侧＝build2.txt 正则计数；PDF 侧＝pymupdf 直读（不依赖渲染器色管）。
跑法：python check.py
"""
import collections
import os
import re

import numpy as np
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PT2MM = 25.4 / 72

raw = open(os.path.join(HERE, "build2.txt"), encoding="utf-8", errors="replace").read()
print("① 编译三 0：error=%d overfull=%d missingchar=%d"
      % (len(re.findall(r"^! ", raw, re.M)), raw.count("Overfull"),
         len(re.findall(r"Missing character", raw))))

doc = pymupdf.open(os.path.join(HERE, "main.pdf"))
page = doc[0]
print("② 页数=%d 页面=%.1f×%.1fmm" % (len(doc), page.rect.width * PT2MM, page.rect.height * PT2MM))

spans = [sp for b in page.get_text("dict")["blocks"] if b.get("type") == 0
         for l in b["lines"] for sp in l["spans"]]
ys0 = [sp["bbox"][1] * PT2MM for sp in spans]

# 墨缘/行距走 300dpi 墨迹（pymupdf span bbox 在 banjiao 模式下含标点全宽盒，
# 行末标点会虚报越界——实测墨迹不越界，故以栅格墨迹为准）
pix = page.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
px = 300 / 25.4
body = img[: int(275 * px), :]
cols = np.where((body < 160).any(axis=0))[0]
rows_ink = np.where((body < 160).any(axis=1))[0]
print("③ 正文墨缘 左=%.2fmm 右=%.2fmm（版心 17.20–192.80mm）"
      % (cols[0] / px, cols[-1] / px))
print("   墨迹顶=%.2fmm（章首方块越出标题行＝全品 ZS-01 形态）" % (rows_ink[0] / px))

rowsum = (body < 160).sum(axis=1)
idx = [i for i, v in enumerate(rowsum) if v > 0]
segs, s, prev = [], idx[0], idx[0]
for v in idx[1:]:
    if v - prev > 2:
        segs.append(s)
        s = v
    prev = v
segs.append(s)
gaps = collections.Counter(round((b - a) / px, 2) for a, b in zip(segs, segs[1:])
                           if 5.0 < (b - a) / px < 8.0)
print("④ 行距主峰=%.2fmm（18.0pt＝6.35mm；墨带行数 %d）" % (gaps.most_common(1)[0][0], len(segs)))
band = img[int(90 * px):int(150 * px), :]
col = np.median(band, axis=0)
lo, hi = int(103 * px), int(107 * px)
x = lo + int(np.argmin(col[lo:hi]))
print("⑤ 栏线 x=%.2fmm 中位灰=%d（靶 188／窗 170–210）" % (x / px, int(col[x])))

sub = img[int(275 * px):, :]
m = (sub > 195) & (sub < 248)
rows = np.where(m.sum(axis=1) > 150)[0] + int(275 * px)
runs, s, prev = [], None, None
for v in np.where((img[int(282 * px), :] > 195) & (img[int(282 * px), :] < 248))[0]:
    if prev is None or v - prev > 3:
        if s is not None:
            runs.append((s, prev))
        s = v
    prev = v
runs.append((s, prev))
runs.sort(key=lambda t: t[1] - t[0])
a, b = runs[-1]
print("⑥ 页码灰块 y=%.2f–%.2fmm 高=%.2fmm 底距页底=%.2fmm（靶 7.8／11.2）"
      % (rows[0] / px, rows[-1] / px, (rows[-1] - rows[0]) / px, 297 - rows[-1] / px))
print("   块右缘=%.2fmm 距纸右缘=%.2fmm（全品 p06 块出血到纸边；我方止于版心＝在案差异）"
      % (b / px, 210 - b / px))

fonts = sorted({f[3].split("+")[-1] for f in page.get_fonts()})
print("⑦ 字体=%s" % ", ".join(fonts))
