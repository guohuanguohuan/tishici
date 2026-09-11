# -*- coding: utf-8 -*-
"""选项修0910：修前 PDF 第二槽段（x≈71.7mm, y≈67.4mm）逐字符取证＋源级剥排版符核验。"""
import re
import unicodedata
import pymupdf

# —— A. 修前 PDF：Q1-A 行域内全部字符（含无 Unicode 映射者）——
doc = pymupdf.open("main-修前.pdf")
p = doc[0]
PTMM = 72 / 25.4
for b in p.get_text("rawdict")["blocks"]:
    for ln in b.get("lines", []):
        y = ln["bbox"][1] / PTMM
        if not (66.5 < y < 70.5):
            continue
        for s in ln["spans"]:
            chars = s["chars"]
            x0 = chars[0]["origin"][0] / PTMM
            x1 = chars[-1]["origin"][0] / PTMM
            seq = "".join(repr(c["c"]) + ("" if ord(c["c"]) != 0x20D7 else "*") for c in chars)
            print("span x %.2f–%.2f font=%s" % (x0, x1, s["font"]))
            print("   ", seq[:400])
print()
# —— B. 源级剥排版符逐行等 ——
def strip_tex(s):
    s = s.replace("\\nobreak", "")
    s = re.sub(r"\\optline|\\optII", "", s)
    s = re.sub(r"[{}]", "", s)
    return s.strip()

base = r"C:/提示词/工作区/字替对照-0909/靠齐样张-0910/测评卷"
old = open(base + "/main.tex.bak_选项修0910", encoding="utf-8").read().splitlines()[184]
new = open(base + "/main.tex", encoding="utf-8").read().splitlines()[184]
o, n = strip_tex(old), strip_tex(new)
print("源级剥排版符逐行等？", o == n)
print("OLD:", o)
print("NEW:", n)
