# -*- coding: utf-8 -*-
"""main.pdf 文本级竖向测量：逐行基线(origin y)提取＋关键对基线距。
只读测量，输出到 stdout；证据裁片由 m_mine_ink.py 另出。"""
import fitz, re, sys
sys.stdout.reconfigure(encoding="utf-8")
PT2MM = 25.4 / 72.0

DOC = r"C:/提示词/工作区/字替对照-0909/variantF/main.pdf"
doc = fitz.open(DOC)
MID = 595.28 / 2

def lines_of(pno):
    page = doc[pno]
    d = page.get_text("dict")
    out = []
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt:
                continue
            sp0 = l["spans"][0]
            out.append(dict(text=txt, x0=round(l["bbox"][0], 1),
                            base=round(sp0["origin"][1], 2),
                            size=round(sp0["size"], 2)))
    return out

def show(pno, col, ylo, yhi, tag):
    print(f"---- p{pno+1} {tag} (base y in [{ylo},{yhi}] pt) ----")
    rows = [r for r in lines_of(pno)
            if ylo <= r["base"] <= yhi and ((r["x0"] < MID) == (col == 0))]
    rows.sort(key=lambda r: r["base"])
    prev = None
    for r in rows:
        d = "" if prev is None else f"  Δ={r['base']-prev:6.2f}pt={ (r['base']-prev)*PT2MM:5.2f}mm"
        print(f"y={r['base']:7.2f} x0={r['x0']:6.1f} {r['size']:5.2f}pt | {r['text'][:46]}{d}")
        prev = r["base"]
    return rows

# p1 左栏：条目1→条目2→(2)段→条目3
show(0, 0, 390, 720, "左栏 知识点一 条目区(意见28)")
# p1 右栏：诊断分析 判断题(1)(2)(意见32)
show(0, 1, 560, 800, "右栏 诊断分析 判断(1)(2)(意见32)")
# p2 右栏 知识点二判断题 佐证
show(1, 1, 60, 400, "p2 诊断分析 判断(1)(2)佐证")
