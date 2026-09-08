# -*- coding: utf-8 -*-
"""v4.3 执行轮像素探针（三轮）：150dpi 墨口径，与全品扫差同法。
测：章首四档墨间距、章首占地、花形组几何（底线厚/右词坐线/行总高/前距）、
表顶前距/行高、判断题括号行真身、解析行→下题题号墨隙、页脚数字-块缘。"""
import os
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件"
PT = 72 / 25.4
MARGIN = 15 * PT
COLW = (595.276 - 2 * MARGIN - 7.5 * PT) / 2
mm = lambda v: v / PT
DPI = 150
SC = DPI / 72.0

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))

def bands(page, x0, x1, y0, y1, thresh=128):
    """行带投影：返回 [(带顶pt, 带底pt)]，x∈[x0,x1)pt，y∈[y0,y1)pt，暗于 thresh 记墨。"""
    pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = []
    for r in range(h):
        base = r * w
        dark = any(s[base + c] < thresh for c in range(w))
        rows.append(dark)
    out = []
    st = None
    for i, d in enumerate(rows):
        if d and st is None:
            st = i
        elif not d and st is not None:
            out.append((y0 + st / SC, y0 + i / SC))
            st = None
    if st is not None:
        out.append((y0 + st / SC, y0 + h / SC))
    return out

def col_x(page_idx=0):
    return MARGIN, MARGIN + COLW

print('=== 章首四档墨间距（p1 通栏 x 全版心） ===')
p1 = doc[0]
X0, X1 = MARGIN, 595.276 - MARGIN
bs = bands(p1, X0, X1, MARGIN, 100 * PT)
for i, (a, b) in enumerate(bs[:12]):
    print('  带%d y %.2f-%.2f h=%.2f' % (i, mm(a), mm(b), mm(b - a)))
for i in range(len(bs) - 1):
    g = mm(bs[i + 1][0] - bs[i][1])
    print('  带%d→带%d 墨隙 %.2f mm' % (i, i + 1, g))

print('=== 花形组几何（p1 左栏 y 100-135mm） ===')
bs2 = bands(p1, X0, X0 + COLW, 95 * PT, 135 * PT)
for i, (a, b) in enumerate(bs2):
    print('  带%d y %.2f-%.2f h=%.2f' % (i, mm(a), mm(b), mm(b - a)))
# 菱形组横向 bbox（取菱形带行）
if bs2:
    dia_band = bs2[0]
    pm = p1.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                       clip=pymupdf.Rect(X0, dia_band[0], X0 + COLW, dia_band[1]))
    w, h, s = pm.width, pm.height, pm.samples
    cols = [any(s[r * w + c] < 128 for r in range(h)) for c in range(w)]
    try:
        first = cols.index(True); last = w - 1 - cols[::-1].index(True)
        print('  菱形组带 x %.2f-%.2f 宽 %.2f（目 23.5）' % (mm(X0 + first / SC), mm(X0 + last / SC), mm((last - first) / SC)))
    except ValueError:
        print('  菱形带无墨')
# 右词带与底线带之间的墨隙即坐线；底线带厚度
print('=== 判断题括号行真身（p1 y 226-229pt 左栏横向墨 run） ===')
pm = p1.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                   clip=pymupdf.Rect(X0, 226.5 * PT, X0 + COLW, 229 * PT))
w, h, s = pm.width, pm.height, pm.samples
cols = [any(s[r * w + c] < 128 for r in range(h)) for c in range(w)]
runs = []
st = None
for i, d in enumerate(cols):
    if d and st is None:
        st = i
    elif not d and st is not None:
        runs.append((st, i)); st = None
if st is not None:
    runs.append((st, w))
gaps = [(mm(X0 + b / SC), mm(X0 + runs[j + 1][0] / SC), mm(X0 + runs[j + 1][0] / SC) - mm(X0 + b / SC))
        for j, (a2, b) in enumerate(runs) if j + 1 < len(runs) and (runs[j + 1][0] - b) / SC > 1.5]
print('  大隙(>1.5mm)：', [(round(p, 2), round(q, 2), round(g, 2)) for p, q, g in gaps])
print('  行墨右缘 x=%.2f 栏右=%.2f 距=%.2f' % (mm(X0 + runs[-1][1] / SC), mm(X0 + COLW), mm(COLW - runs[-1][1] / SC)))

print('=== 表顶前距（表1 p1 右栏；表2 p2 左栏） ===')
CL_R0 = MARGIN + COLW + 7.5 * PT
for pno, tabtop, clx in ((1, 108.4, CL_R0), (2, 85.96, X0)):
    page = doc[pno - 1]
    bs3 = bands(page, clx, clx + COLW, (tabtop - 14) * PT, tabtop * PT + 1)
    if bs3:
        prev = bs3[-1]
        print('  p%d 表顶 %.2f 上方带底 %.2f 前距 %.2f（目 2.77±0.5）' % (pno, tabtop, mm(prev[1]), tabtop - mm(prev[1])))
# 表行高复核（表1 灰122 线间已测 PDF；像素复核头行）
print('=== 解析行→下题题号墨隙（p7 检测区左栏） ===')
p7 = doc[6]
rows = []
for blk in p7.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        rows.append((ln['bbox'][1], ln['bbox'][3], t))
rows.sort()
prev_jx = None
for y0, y1, t in rows:
    is_jx = t.startswith('【解析】')
    is_ti = len(t) > 2 and t[0] in '12345' and (t[1] == '．' or t[1] == '.')
    if prev_jx is not None and is_ti:
        cl = X0
        print('  解析底→题号顶 墨隙（PDF bbox 口径）%.2f mm  %s' % (mm(y0 - prev_jx[0]), t[:16]))
        prev_jx = None
    elif is_jx:
        prev_jx = (y0, y1)
print('=== 页脚（p1 奇）数字左缘-块左缘 ===')
for d in p1.get_drawings():
    r = d['rect']
    f = d.get('fill')
    if f and r.y0 > (842 - 20 * PT) - 10 and tuple(round(x * 255) for x in f) == (221, 221, 221):
        print('  块 x %.2f-%.2f y %.2f-%.2f（mm）' % (mm(r.x0), mm(r.x1), mm(r.y0), mm(r.y1)))
