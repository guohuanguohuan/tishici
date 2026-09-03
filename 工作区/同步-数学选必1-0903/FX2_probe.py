# FX2: 探查C件头部结构——段[0]标题、头部节sectPr、节隔断段、首若干段、末段sectPr
from lxml import etree
import os

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

tree = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
print("total paragraphs:", len(paras))

def ptext(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

def pinfo(i, p):
    txt = ptext(p)
    ppr = p.find(f"{{{W}}}pPr")
    attrs = []
    if ppr is not None:
        # sectPr in pPr = 节隔断段
        if ppr.find(f"{{{W}}}sectPr") is not None:
            attrs.append("SECT-BREAK")
        shd = ppr.find(f"{{{W}}}shd")
        if shd is not None:
            attrs.append("shd=" + shd.get(f"{{{W}}}fill", ""))
        st = ppr.find(f"{{{W}}}pStyle")
        if st is not None:
            attrs.append("style=" + st.get(f"{{{W}}}val"))
    nmath = len(p.findall(f".//{{{W}}}oMath")) if False else len(list(p.iter("{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath")))
    ndraw = len(list(p.iter(f"{{{W}}}drawing")))
    return f"[{i}] {'|'.join(attrs) or '-'} math={nmath} draw={ndraw} len={len(txt)} :: {txt[:60]}"

for i in range(0, 8):
    print(pinfo(i, paras[i]))

# 所有含sectPr的段落
sect_paras = [i for i, p in enumerate(paras) if p.find(f"{{{W}}}pPr/{{{W}}}sectPr") is not None]
print("\nparagraphs with sectPr (section breaks):", sect_paras)

# body末尾直接子元素
print("\nbody tail children (last 3):")
kids = list(body)
for k in kids[-3:]:
    tag = etree.QName(k).localname
    if tag == "p":
        idx = paras.index(k) if k in paras else -1
        print("  tail p idx", idx, ptext(k)[:40])
    else:
        print("  tail", tag)

# 头部节sectPr详情（第一个sectPr，无论在段内还是body末）
sect1 = body.find(f".//{{{W}}}p/{{{W}}}pPr/{{{W}}}sectPr")
print("\n--- head sectPr (in-paragraph) ---")
print(etree.tostring(sect1, pretty_print=True).decode()[:2200])

# body末sectPr
last_sect = body.find(f"{{{W}}}sectPr")
print("--- body-final sectPr ---")
print(etree.tostring(last_sect, pretty_print=True).decode()[:2200])

# 头部节内容段范围：段0..sect_paras[0]（隔断段含前）
if sect_paras:
    b0 = sect_paras[0]
    print(f"\nhead-section paragraphs: 0..{b0} (break para = {b0})")
    for i in range(0, b0 + 1):
        print(pinfo(i, paras[i]))
