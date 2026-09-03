# -*- coding: utf-8 -*-
"""FX6 probe2: tab逐处上下文/szCs/1F4E79邻域/编注线性数学(w:t层)/空格卫生/选项形态"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

# ---- 1) run级tab逐处：段落内元素级线性化（含oMath标记） ----
def para_linear(p):
    """段内元素级线性化: [E:text|TAB|MATH:...]按文档序"""
    out = []
    def walk(el, in_math):
        for ch in el:
            tag = etree.QName(ch).localname
            if tag == "t" and not in_math:
                out.append(("t", ch.text or ""))
            elif tag == "tab" and not in_math:
                out.append(("TAB", ""))
            elif tag == "drawing":
                out.append(("IMG", ""))
            elif tag == "oMath" or (tag == "oMathPara"):
                s = "".join(ch.itertext())
                out.append(("MATH", s))
            else:
                walk(ch, in_math or tag in ("oMath", "oMathPara"))
    walk(p, False)
    return out

print("=== run级tab 11段逐处 ===")
for k, p in enumerate(paras):
    lin = para_linear(p)
    has_tab = any(x[0] == "TAB" for x in lin)
    if not has_tab:
        continue
    s = "".join(x[1] for x in lin)
    print(f"\n-- p#{k} 全段: {s[:170]!r}")
    # tab前后各25字符
    plain = []
    for typ, txt in lin:
        plain.append(("[TAB]" if typ == "TAB" else ("[M]" if typ == "MATH" else ("[I]" if typ == "IMG" else txt))))
    joined = "".join(plain)
    for m in re.finditer(r"\[TAB\]", joined):
        a, b = max(0, m.start() - 30), min(len(joined), m.end() + 30)
        print(f"   TAB@{m.start()}: …{joined[a:b]}…")

print("\n=== pPr w:tabs 定义段 ===")
for k, p in enumerate(paras):
    pPr = p.find(f"{{{W}}}pPr")
    if pPr is None: continue
    tabs = pPr.find(f"{{{W}}}tabs")
    if tabs is not None:
        defs = [(t.get(f"{{{W}}}val"), t.get(f"{{{W}}}pos")) for t in tabs.findall(f"{{{W}}}tab")]
        s = "".join(p.itertext())
        print(f"p#{k} defs={defs} 段首50字={s[:50]!r}")

# ---- 2) sz21 run: szCs分布 + 内容类型 ----
n_sz_only = n_szcs = n_both = 0
content_kinds = {"empty": 0, "draw": 0, "text": 0, "lrpb": 0}
for p in paras:
    for r in p.iter(f"{{{W}}}r"):
        rPr = r.find(f"{{{W}}}rPr")
        if rPr is None: continue
        sz = rPr.find(f"{{{W}}}sz"); szcs = rPr.find(f"{{{W}}}szCs")
        v21 = sz is not None and sz.get(f"{{{W}}}val") == "21"
        c21 = szcs is not None and szcs.get(f"{{{W}}}val") == "21"
        if v21 or c21:
            if v21 and c21: n_both += 1
            elif v21: n_sz_only += 1
            else: n_szcs += 1
            txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
            if r.find(f"{{{W}}}drawing") is not None: content_kinds["draw"] += 1
            elif txt == "": content_kinds["empty"] += 1
            else: content_kinds["text"] += 1
            if r.find(f"{{{W}}}lastRenderedPageBreak") is not None: content_kinds["lrpb"] += 1
print("\n=== sz21 ===: sz_only=%d szcs_only=%d both=%d 内容=%s" % (n_sz_only, n_szcs, n_both, content_kinds))

# ---- 3) 1F4E79 p#46 邻域（run级线性化，标注oMath与颜色） ----
print("\n=== p#46 run级结构（1F4E79邻域） ===")
p = paras[46]
def run_seq(p):
    out = []
    def walk(el, depth=0):
        for ch in el:
            tag = etree.QName(ch).localname
            if tag in ("r",):
                rPr = ch.find(f"{{{W}}}rPr")
                col = None
                if rPr is not None:
                    c = rPr.find(f"{{{W}}}color")
                    if c is not None: col = c.get(f"{{{W}}}val")
                txt = "".join(ch.itertext())
                out.append(("R", col, txt))
            elif tag in ("oMath", "oMathPara"):
                out.append(("M", "", "".join(ch.itertext())))
            else:
                walk(ch, depth + 1)
    walk(p)
    return out
for typ, col, txt in run_seq(paras[46]):
    print(f"  {typ} col={col} {txt[:80]!r}")

# ---- 4) 【编注】段 w:t 层线性数学字符（层敏感验真） ----
LIN = re.compile(r"[√²³⁰¹²³⁴₅₆₇₈₉₀⊥∥∈]|x[0-9]|[yfgecmkbhp][0-9]")
def wt_only(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
n_bianzhu_wt = 0
hits = []
for k, p in enumerate(paras):
    t = wt_only(p)
    if "【编注】" in "".join(p.itertext()):
        # w:t层含 数学连缀字符
        if re.search(r"[√²¹⁰₃₄₅₆₇₈₉₂]|(?:\^)|(?:[a-zA-Z]²)", t):
            n_bianzhu_wt += 1
            hits.append((k, t[:100]))
print("\n=== 【编注】段 w:t层含线性数学字符: %d 段 ===" % n_bianzhu_wt)
for k, t in hits:
    print(f"  p#{k}: {t!r}")
