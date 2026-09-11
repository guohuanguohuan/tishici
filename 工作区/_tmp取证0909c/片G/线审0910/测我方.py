# -*- coding: utf-8 -*-
# 我方探针 PDF 矢量属性审计：逐线提取 stroke width / dash / color / 端点
import fitz, json, math
import numpy as np

PT = 72.27 / 25.4  # pt per mm（tex pt）
doc = fitz.open(r"C:/提示词/工作区/_tmp取证0909c/片G/线审0910/我方探针.pdf")
FIGS = [  # (页, 名, 自然宽mm, 置宽mm, 自然高mm)
    (0, "g6", 86.0, 80.8, 22.8440),
    (1, "g1", 41.100, 41.1, 68.936),
    (2, "g2", 42.0, 42.0, 42.0),
    (3, "g3", 86.0, 36.3, 82.0),
    (4, "g4", 66.3000, 30.5, 35.6741),
    (5, "g5", None, 28.2, None),
]

def segs_of(page):
    out = []
    for d in page.get_drawings():
        w = d.get("width"); dashes = d.get("dashes"); color = d.get("color")
        for it in d["items"]:
            if it[0] == "l":
                p1, p2 = it[1], it[2]
                out.append(dict(x1=p1.x, y1=p1.y, x2=p2.x, y2=p2.y,
                                w=w, dash=dashes, color=color))
    return out

report = {}
for pno, name, nw, pw, nh in FIGS:
    page = doc[pno]
    segs = segs_of(page)
    report[name] = []
    print("=" * 16, name, "页", pno + 1, "段数", len(segs))
    for s in segs:
        L = math.hypot(s["x2"] - s["x1"], s["y2"] - s["y1"])
        wmm = s["w"] / PT if s["w"] else None
        dash = s["dash"]
        col = s["color"]
        colg = round(col[0], 3) if col else None
        print("  (%7.2f,%7.2f)-(%7.2f,%7.2f) L=%6.2fpt 宽=%smm dash=%s 灰=%s" % (
            s["x1"], s["y1"], s["x2"], s["y2"], L,
            ("%.4f" % wmm) if wmm else "-", dash, colg))
        report[name].append(s)

with open(r"C:/提示词/工作区/_tmp取证0909c/片G/线审0910/线审-我方矢量.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("saved")
