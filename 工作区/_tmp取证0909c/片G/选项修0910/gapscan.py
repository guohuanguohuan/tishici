# -*- coding: utf-8 -*-
r"""选项修0910：全卷异常间隙扫描。
python gapscan.py <pdf> [阈值pt=15]
口径：pymupdf span 位置；同栏、同基线（y1 差 ≤0.3mm）行对象合并为「行」；行内相邻 span
间隙 > 阈值 → 记录并分类。设计槽位类＝选项网格（TJ-07：下一 span 为 A-D 标签，或分数带
旁注）、括号固定列位（TJ-08：下一 span 以（开头）、填写行下划线（JT-02）、\quad（JT-05）、
页脚段隙（YJ-02 实测隙）；其余＝异常候选（人工复核）。旋转文本（丝带）不参与。"""
import sys
import re
import pymupdf

PT = 72.0 / 25.4
pdf = sys.argv[1]
THR = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0  # pt
doc = pymupdf.open(pdf)
print("# 间隙扫描：%s｜阈值＝同行相邻 span 间隙 > %.0fpt（%.2fmm）" % (pdf, THR, THR / PT))
print("# 口径＝同栏同基线合并行；分类含设计槽位豁免（TJ-07/TJ-08/JT-02/JT-05/YJ-02）")
rows_all = []
for pno, page in enumerate(doc, 1):
    items = []  # (col, ybase, spans)
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            d = ln.get("dir", (1, 0))
            if abs(d[1]) > 0.05:      # 旋转（丝带「数学」）不参与
                continue
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            x0 = ln["bbox"][0] / PT
            y = ln["bbox"][3] / PT    # 基线近似＝bbox 底
            col = "页脚" if y > 265 else ("栏1" if x0 < 132 else ("栏2" if x0 < 264 else "栏3"))
            items.append([col, round(y / 0.3), sorted(spans, key=lambda s: s["bbox"][0])])
    # 合并同栏同基线桶
    merged = {}
    for col, yk, spans in items:
        merged.setdefault((col, yk), []).extend(spans)
    for (col, yk), spans in sorted(merged.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        spans = sorted(spans, key=lambda s: s["bbox"][0])
        y = yk * 0.3
        rowtxt = "".join(s["text"] for s in spans)
        for i in range(len(spans) - 1):
            a, c = spans[i], spans[i + 1]
            gap = (c["bbox"][0] - a["bbox"][2]) / PT   # mm
            if gap * PT <= THR:                        # THR 单位 pt
                continue
            nxt = c["text"].strip()
            if col == "页脚":
                cls = "设计：页脚段隙（YJ-02 实测隙）"
            elif "班级" in rowtxt:
                cls = "设计：填写行下划线（JT-02）"
            elif "（时间" in rowtxt:
                cls = "设计：\\quad（JT-05）"
            elif re.match(r"^[A-D]．", nxt) or re.fullmatch(r"[A-D]", nxt):
                cls = "设计：选项网格槽（TJ-07）"
            elif nxt.startswith("（"):
                cls = "设计：括号固定列位（TJ-08 \\hfill）"
            elif re.search(r"(?:^|[；;])\s*$", a["text"]) and re.match(r"^[A-D]$", nxt):
                cls = "设计：选项网格槽（TJ-07）"
            else:
                # 分数带旁注：本行无汉字（分子/分母带纯数字符号）且 ±3mm 内同行对象含选项标签 → 设计
                sib = (not re.search(r"[\u4e00-\u9fff]", rowtxt)) and any(
                    abs(k[1] * 0.3 - y) <= 3.0 and k[0] == col and
                    re.search(r"[A-D]．", "".join(s["text"] for s in v))
                    for k, v in merged.items())
                cls = "设计：选项网格槽（TJ-07 分数带）" if sib else "★异常候选"
            rows_all.append((pno, col, y, gap, a["text"][-8:], nxt[:8], cls, rowtxt))
print("# 命中 %d 条（>%.0fpt）" % (len(rows_all), THR))
for pno, col, y, gmm, prev, nxt, cls, rowtxt in rows_all:
    print("p%d %s y=%6.2fmm 间隙=%5.2fmm(%.1fpt) %s｜…%s ⇄ %s…｜行=%s" % (
        pno, col, y, gmm, gmm * PT, cls, prev, nxt, rowtxt[:44]))
abn = [r for r in rows_all if r[6].startswith("★")]
print("## 汇总：总命中 %d；设计槽位 %d；异常候选 %d" % (len(rows_all), len(rows_all) - len(abn), len(abn)))
