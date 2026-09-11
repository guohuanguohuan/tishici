# -*- coding: utf-8 -*-
"""选项修0910 探针：按页取文本行→span 位置，可选按关键字过滤行。
用法：python spans.py <pdf> [关键字...]；无关键字则打全部行。"""
import sys
import pymupdf

PT = 72.0 / 25.4  # mm→pt: pt = mm*72/25.4

pdf = sys.argv[1]
keys = sys.argv[2:]
doc = pymupdf.open(pdf)
print("pages", doc.page_count, "size mm %.1fx%.1f" % (doc[0].rect.width / PT, doc[0].rect.height / PT))
for pno, page in enumerate(doc, 1):
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            spans = ln["spans"]
            text = "".join(s["text"] for s in spans)
            if keys and not any(k in text for k in keys):
                continue
            ymm = ln["bbox"][1] / PT
            print("p%d y=%6.2fmm | %s" % (pno, ymm, text))
            for s in spans:
                print("      x %7.2f–%7.2f mm (w=%5.2f sz=%.1f) |%s|" % (
                    s["bbox"][0] / PT, s["bbox"][2] / PT,
                    (s["bbox"][2] - s["bbox"][0]) / PT, s["size"], s["text"]))
