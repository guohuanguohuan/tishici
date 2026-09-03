# -*- coding: utf-8 -*-
"""FX6 probe1: H件基线结构探查——sectPr/段0/tab/sz21/1F4E79/题块/底纹计数"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
DOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
print("总段数(body直接子p):", len(paras))
print("body子元素构成: p=%d tbl=%d sectPr=%d 其它=%d" % (
    len(body.findall(f"{{{W}}}p")), len(body.findall(f"{{{W}}}tbl")),
    len(body.findall(f"{{{W}}}sectPr")),
    len(body) - len(body.findall(f"{{{W}}}p")) - len(body.findall(f"{{{W}}}tbl")) - len(body.findall(f"{{{W}}}sectPr"))))

# sectPr 结构（段落内嵌 + body级）
print("\n=== sectPr 分布 ===")
i = 0
for p in paras:
    pPr = p.find(f"{{{W}}}pPr")
    if pPr is not None and pPr.find(f"{{{W}}}sectPr") is not None:
        print(f"段内sectPr @ p#{i}, 段文本前40字: {''.join(p.itertext())[:40]!r}")
    i += 1
body_sect = body.findall(f"{{{W}}}sectPr")
print("body级sectPr数:", len(body_sect))

def dump_sectPr(sp, label):
    print(f"--- {label} ---")
    for child in sp:
        tag = etree.QName(child).localname
        attrs = {etree.QName(k).localname: v for k, v in child.attrib.items()}
        print("  ", tag, attrs)
        if tag == "cols":
            for sub in child:
                print("      ", etree.QName(sub).localname, {etree.QName(k).localname: v for k, v in sub.attrib.items()})

i = 0
for p in paras:
    pPr = p.find(f"{{{W}}}pPr")
    if pPr is not None:
        sp = pPr.find(f"{{{W}}}sectPr")
        if sp is not None:
            dump_sectPr(sp, f"头部节sectPr(嵌段#{i})")
    i += 1
for sp in body_sect:
    dump_sectPr(sp, "正文末body级sectPr")

# 段[0]
print("\n=== 段[0] XML(截断1200) ===")
print(etree.tostring(paras[0], encoding="unicode")[:1200])
print("段[0]文本:", "".join(paras[0].itertext()))
print("\n=== 段[1..4] 文本 ===")
for k in range(1, 5):
    print(f"p#{k}:", "".join(paras[k].itertext())[:60])

# 题块计数（C9C9C9+加粗+题号文本）
def run_props(r):
    rPr = r.find(f"{{{W}}}rPr")
    shd = b = sz = color = None
    txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
    if rPr is not None:
        s = rPr.find(f"{{{W}}}shd")
        if s is not None: shd = s.get(f"{{{W}}}fill")
        bEl = rPr.find(f"{{{W}}}b")
        if bEl is not None: b = bEl.get(f"{{{W}}}val", "on")
        szEl = rPr.find(f"{{{W}}}sz")
        if szEl is not None: sz = szEl.get(f"{{{W}}}val")
        cEl = rPr.find(f"{{{W}}}color")
        if cEl is not None: color = cEl.get(f"{{{W}}}val")
    return shd, b, sz, color, txt

tiHao = 0
seq = []
for k, p in enumerate(paras):
    for r in p.findall(f"{{{W}}}r"):
        shd, b, sz, color, txt = run_props(r)
        if shd == "C9C9C9" and b and txt and re.fullmatch(r"\d+(?:\.\d+)*-\d+．", txt):
            tiHao += 1
            seq.append((k, txt))
print("\n题号块run数(C9C9C9+加粗+层级号):", tiHao)
print("首5:", seq[:5]); print("末3:", seq[-3:])

# tab 分布：run级 w:tab 元素 vs pPr w:tabs 停靠定义
run_tabs = []
tabs_defs = []
for k, p in enumerate(paras):
    for r in p.findall(f"{{{W}}}r"):
        for t in r.findall(f"{{{W}}}tab"):
            run_tabs.append(k)
    pPr = p.find(f"{{{W}}}pPr")
    if pPr is not None:
        tabs = pPr.find(f"{{{W}}}tabs")
        if tabs is not None:
            n = len(tabs.findall(f"{{{W}}}tab"))
            tabs_defs.append((k, n))
print("\nrun级w:tab元素总数:", len(run_tabs), "所在段数:", len(set(run_tabs)))
print("pPr w:tabs停靠定义段数:", len(tabs_defs), "定义总数:", sum(n for _, n in tabs_defs))

# sz=21 run
sz21 = []
for k, p in enumerate(paras):
    for r in p.iter(f"{{{W}}}r"):
        rPr = r.find(f"{{{W}}}rPr")
        if rPr is not None:
            szEl = rPr.find(f"{{{W}}}sz")
            if szEl is not None and szEl.get(f"{{{W}}}val") == "21":
                has_draw = r.find(f"{{{W}}}drawing") is not None
                txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
                sz21.append((k, "draw" if has_draw else "-", repr(txt[:20])))
print("\nsz21 run数:", len(sz21))
for row in sz21[:10]:
    print("  ", row)

# 1F4E79
for k, p in enumerate(paras):
    for r in p.iter(f"{{{W}}}r"):
        rPr = r.find(f"{{{W}}}rPr")
        if rPr is not None:
            cEl = rPr.find(f"{{{W}}}color")
            if cEl is not None and cEl.get(f"{{{W}}}val", "").upper() == "1F4E79":
                txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
                ptxt = "".join(p.itertext())
                print("\n1F4E79 run @ p#%d run文本=%r" % (k, txt))
                print("  全段文本:", ptxt[:150])

# 七类底纹计数基线
cnt_adc2da_p = 0; cnt_c6d4e3_p = 0; cnt_e0e0e0_p = 0
for p in paras:
    pPr = p.find(f"{{{W}}}pPr")
    if pPr is not None:
        s = pPr.find(f"{{{W}}}shd")
        if s is not None:
            f = s.get(f"{{{W}}}fill")
            if f == "ADC2DA": cnt_adc2da_p += 1
            elif f == "C6D4E3": cnt_c6d4e3_p += 1
            elif f == "E0E0E0": cnt_e0e0e0_p += 1
print("\n段级底纹: ADC2DA=%d C6D4E3=%d E0E0E0=%d (A2基线: 2/73/138)" % (cnt_adc2da_p, cnt_c6d4e3_p, cnt_e0e0e0_p))
doc_text = open(DOC, encoding="utf-8").read()
print("全XML C9C9C9:", doc_text.count('w:fill="C9C9C9"'), "(A2基线1220)")
