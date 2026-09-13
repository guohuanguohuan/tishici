# -*- coding: utf-8 -*-
"""独立对账：不吃 tex，纯 PDF 行盒法——逐行取 dict lines，凡同 y 基线上出现 ≥2 个
"A．/B．/C．/D．"起手的 span，且相邻 span 墨盒在 x 向有正交叠，即报。与主扫描器互为独立证据。"""
import pymupdf, os, re, sys

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷"
PT2MM = 25.4 / 72
SUBS = [r"导学件/" + x for x in ["课时01", "课时02", "课时03", "课时04", "课时05", "课时06",
        "课时07", "课时08", "课时09", "课时10", "衔接节-1.2.1前", "章末-本章总结提升"]]
MARK = re.compile(r"^\s*[ABCD]\s*[．.]")

hit = 0
for d in SUBS:
    doc = pymupdf.open(os.path.join(ROOT, d, "main.pdf"))
    for pno, pg in enumerate(doc):
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                sp = [s for s in l["spans"] if MARK.match(s["text"])]
                if len(sp) < 2:
                    continue
                sp.sort(key=lambda s: s["bbox"][0])
                ov = []
                for i in range(len(sp) - 1):
                    v = (sp[i]["bbox"][2] - sp[i + 1]["bbox"][0]) * PT2MM
                    ov.append(round(v, 2))
                pitch = [round(sp[i + 1]["bbox"][0] - sp[i]["bbox"][0], 1) for i in range(len(sp) - 1)]
                bad = [v for v in ov if v > 0]
                if bad:
                    hit += 1
                    txt = "".join(s["text"] for s in sp)
                    print(f"[交叠] {d} p{pno+1} y{round(sp[0]['bbox'][1],1)} 槽数={len(sp)} "
                          f"距{pitch} 交叠{ov}mm | {txt[:70]}")
print(f"\n行盒法：发现墨盒交叠行 {hit} 处")
