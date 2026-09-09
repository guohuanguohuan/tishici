# -*- coding: utf-8 -*-
"""取证B组·全景扫描：p1–p7 全部 ∥ 矢量对 与 全部 = 的 advance 胶宽，标记拉伸实例。"""
import pymupdf

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\main.pdf"
doc = pymupdf.open(SRC)

print("=== 全部 ∥（矢量对合并）===")
for pno in range(1, 8):
    page = doc[pno - 1]
    strokes = []
    for d in page.get_drawings():
        if d["fill"] is None: continue
        r = pymupdf.Rect(d["rect"])
        if 7.5 < r.height < 12.0 and 2.5 < r.width < 8.0:
            strokes.append(r)
    # 合并成对（x 间距 <4pt，y 重叠）
    used = [False]*len(strokes)
    pairs = []
    for i, a in enumerate(strokes):
        if used[i]: continue
        for j in range(i+1, len(strokes)):
            b = strokes[j]
            if used[j]: continue
            if abs(a.y0-b.y0) < 1 and 2 < b.x0-a.x0 < 5.5:
                pairs.append(pymupdf.Rect(min(a.x0,b.x0), a.y0, max(a.x1,b.x1), a.y1))
                used[i]=used[j]=True
                break
    for pr in pairs:
        raw = page.get_text("rawdict")
        yc = (pr.y0+pr.y1)/2
        cand=[(ch["c"], pymupdf.Rect(ch["bbox"])) for blk in raw["blocks"] if blk["type"]==0
              for line in blk["lines"] for span in line["spans"] for ch in span["chars"]
              if pymupdf.Rect(ch["bbox"]).y0 < yc+7 and pymupdf.Rect(ch["bbox"]).y1 > yc-7]
        lefts=[t for t in cand if t[1].x1<=pr.x0+1 and t[1].x0>=pr.x0-30]
        rights=[t for t in cand if t[1].x0>=pr.x1-1 and t[1].x0<=pr.x1+30]
        gl = (pr.x0-max(lefts,key=lambda t:t[1].x1)[1].x1) if lefts else None
        gr = (min(rights,key=lambda t:t[1].x0)[1].x0-pr.x1) if rights else None
        flag = " <-- 拉伸" if (gl and gl>3.4) or (gr and gr>3.4) else ""
        print(f'p{pno} y={pr.y0:6.1f} x={pr.x0:6.1f} w={pr.width:4.2f}  L={gl and round(gl*25.4/72,2)}mm R={gr and round(gr*25.4/72,2)}mm{flag}')

print("\n=== 全部 = 胶宽（>1.2mm 标拉伸）===")
for pno in range(1, 8):
    page = doc[pno - 1]
    raw = page.get_text("rawdict")
    for blk in raw["blocks"]:
        if blk["type"] != 0: continue
        for line in blk["lines"]:
            chars=[(ch["c"], pymupdf.Rect(ch["bbox"])) for span in line["spans"] for ch in span["chars"]]
            for i,(c,r) in enumerate(chars):
                if c!="=": continue
                prev=chars[i-1] if i>0 else None
                nxt=chars[i+1] if i+1<len(chars) else None
                gl=r.x0-prev[1].x1 if prev else None
                if gl is not None and gl*25.4/72>1.2:
                    print(f'p{pno} y={r.y0:6.1f} x={r.x0:6.1f} L={gl:5.2f}pt={gl*25.4/72:4.2f}mm  拉伸')
