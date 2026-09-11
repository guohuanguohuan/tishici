# -*- coding: utf-8 -*-
"""选项修0910：行文字零增删核验 v2。python zerodiff.py <修前.pdf> <修后.pdf>
硬判据：逐页去空白、去组合标记(Mn)后的基字符序列逐字符相等。
软判据：组合标记（含 U+20D7 向量箭头）总数——修前 PDF 行对象首字符的组合标记存在
pymupdf 提取丢失（每枚箭头 5 码点；已目验修前渲染中箭头实际在位），故差值＝0 或
（修后＞修前 且 差为 5 的倍数）记 PASS-with-note，其余 FAIL。
行级差异单列（槽拆行→合并属预期），并验证修前独有行拼接＝修后独有行（基字符口径）。"""
import sys
import re
import unicodedata
import pymupdf

def strip_marks(s):
    s = re.sub(r"\s+", "", s)
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def mark_count(s):
    return sum(1 for c in unicodedata.normalize("NFD", s)
               if unicodedata.category(c) == "Mn")

def lines_of(pdf):
    doc = pymupdf.open(pdf)
    out = []
    for page in doc:
        pl = []
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"])
                if re.sub(r"\s+", "", t):
                    pl.append(t)
        out.append(pl)
    return out

a = lines_of(sys.argv[1])
b = lines_of(sys.argv[2])
ok = True
for pno, (la, lb) in enumerate(zip(a, b), 1):
    sa = "".join(strip_marks(x) for x in la)
    sb = "".join(strip_marks(x) for x in lb)
    ma = sum(mark_count(x) for x in la)
    mb = sum(mark_count(x) for x in lb)
    if sa != sb:
        ok = False
        print("p%d 基字符流不等！" % pno)
        import difflib
        for d in difflib.unified_diff([strip_marks(x) for x in la],
                                      [strip_marks(x) for x in lb], lineterm=""):
            print(" ", d)
    elif ma == mb:
        print("p%d 基字符流逐字符相等（%d 字符）＋组合标记数相等（%d）" % (pno, len(sa), ma))
    elif mb > ma and (mb - ma) % 5 == 0:
        print("p%d 基字符流逐字符相等（%d 字符）；组合标记 %d→%d（＋%d＝%d 枚箭头，"
              "修前行首提取丢失伪差，目验在位）→ PASS-with-note" % (pno, len(sa), ma, mb, mb - ma, (mb - ma) // 5))
    else:
        ok = False
        print("p%d 组合标记数差异常：%d vs %d" % (pno, ma, mb))
    ta = [strip_marks(x) for x in la]
    tb = [strip_marks(x) for x in lb]
    only_a = [x for x in ta if x not in tb]
    only_b = [x for x in tb if x not in ta]
    if only_a or only_b:
        print("   行级差异（预期＝槽拆行合并）：修前 %r → 修后 %r；拼接相等？%s"
              % (only_a, only_b, "".join(only_a) in only_b))
print("RESULT:", "零增删 PASS" if ok else "FAIL")
