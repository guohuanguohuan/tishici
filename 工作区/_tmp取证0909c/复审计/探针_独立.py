# 独立复审计探针（只读）：D① 页数+md5；D② 六图矢量墨簇与栏心偏
import hashlib, pymupdf

PDF = r"C:/提示词/工作区/字替对照-0909/variantF/main.pdf"
MM = 72.0 / 25.4  # pt per mm
A4W = 595.276
ML = 17.2 * MM                      # 左边距
CW = 84.0 * MM                      # 栏宽
GAP = 7.6 * MM                      # 栏间
C1 = ML + CW / 2                    # 栏1心 x(pt)
C2 = ML + CW + GAP + CW / 2         # 栏2心 x(pt)
BND = ML + CW + GAP / 2             # 栏界 x

raw = open(PDF, 'rb').read()
doc = pymupdf.open(PDF)
print(f"D1 页数={doc.page_count} md5={hashlib.md5(raw).hexdigest()} 字节={len(raw)}")

def dark(c):
    return c is not None and max(c) - min(c) < 0.02 and max(c) <= 0.40

for pno in range(doc.page_count):
    page = doc[pno]
    boxes = []
    for d in page.get_drawings():
        r = d['rect']
        if dark(d.get('color')) or dark(d.get('fill')):
            boxes.append(pymupdf.Rect(r))
    n = len(boxes)
    # 并查集聚类（扩 2pt 相交合并）
    par = list(range(n))
    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    ex = [b + (-2, -2, 2, 2) for b in boxes]
    for i in range(n):
        for j in range(i + 1, n):
            if ex[i].intersects(ex[j]):
                par[find(i)] = find(j)
    cl = {}
    for i, b in enumerate(boxes):
        cl.setdefault(find(i), []).append(b)
    bigs = []
    for m, bs in cl.items():
        u = bs[0]
        for b in bs[1:]:
            u |= b
        w, h = (u.x1 - u.x0) / MM, (u.y1 - u.y0) / MM
        if w >= 15 and h >= 10:
            col = 1 if (u.x0 + u.x1) / 2 < BND else 2
            off = ((u.x0 + u.x1) / 2 - (C1 if col == 1 else C2)) / MM
            bigs.append((round(w, 2), round(h, 2), col, round(off, 2), round(u.x0 / MM, 2), round(u.y0 / MM, 2), len(bs)))
    if bigs:
        print(f"p{pno+1}: 簇(bw×bh mm, 栏, 栏心偏mm, x0, y0, 笔画数) = {bigs}")
    else:
        print(f"p{pno+1}: (无≥15×10mm 暗色矢量簇) 全页暗色笔画={n}")
doc.close()
