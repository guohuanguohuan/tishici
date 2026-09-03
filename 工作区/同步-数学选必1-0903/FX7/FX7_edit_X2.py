# -*- coding: utf-8 -*-
"""FX7 edit X2 v3: ①2.8节标题行补「　本节13题」 ②空格卫生（token流边界感知：w:t与oMath按真实邻接）"""
import os, re, copy
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
DOC = os.path.join(WK, "unpack", "X2", "word", "document.xml")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
FW = "，。；：、？！"

tree = etree.parse(DOC)
ps = list(tree.getroot().iter(W + "p"))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

def inline_tokens(p):
    """按文档序返回段落inline token流：('t', w:t) 与 ('M', oMath)；oMath作原子不深入。"""
    toks = []
    def walk(el):
        for c in el:
            if c.tag == W + "t":
                toks.append(("t", c))
            elif c.tag == M + "oMath":
                toks.append(("M", c))
            elif c.tag in (W + "p", W + "r", W + "smartTag", W + "ins"):
                walk(c)
    walk(p)
    return toks

n_q = sum(1 for p in ps if re.match(r"^2\.8\.\d+-\d+．", ptext(p)))
assert n_q == 13

# ---------- ① 2.8节标题统计段 ----------
RPR_FONTS = ('<w:rFonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
             'w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/>')
added = 0
for i, p in enumerate(ps):
    t = ptext(p)
    if t != "2.8 直线与圆锥曲线的位置关系":
        continue
    szs = [z.get(W + "val") for r in p.iter(W + "r") for z in r.iter(W + "sz")]
    if "2" in szs and "28" not in szs:
        continue
    assert not re.search(r"本节\d+题", t)
    last_title_run = None
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        z = rpr.find(W + "sz")
        if z is not None and z.get(W + "val") == "28":
            last_title_run = r
    sep_r = etree.Element(W + "r")
    sep_r.append(copy.deepcopy(last_title_run.find(W + "rPr")))
    etree.SubElement(sep_r, W + "t").text = "\u3000"
    stat_r = etree.Element(W + "r")
    rpr = etree.SubElement(stat_r, W + "rPr")
    rpr.append(etree.fromstring(RPR_FONTS))
    etree.SubElement(rpr, W + "sz").set(W + "val", "24")
    etree.SubElement(rpr, W + "szCs").set(W + "val", "24")
    etree.SubElement(stat_r, W + "t").text = f"本节{n_q}题"
    p.append(sep_r)
    p.append(stat_r)
    added += 1
    print(f"X2 ① p#{i} 统计段追加: 本节{n_q}题")
assert added == 1

# ---------- ② 空格卫生 ----------
def fix_paragraph_spaces(p):
    changed = []
    toks = inline_tokens(p)
    tvals = [ (t.text or "") if k == "t" else None for k, t in toks ]
    # 步骤0：w:t内 nbsp→空格
    for k, el in toks:
        if k == "t" and el.text and "\xa0" in el.text:
            el.text = el.text.replace("\xa0", " ")
            changed.append("nbsp")
    # 步骤1：w:t元素内
    for k, el in toks:
        if k != "t" or not el.text:
            continue
        s = el.text
        s = re.sub(r"[ ]+([" + FW + "])", r"\1", s)
        s = re.sub(r"([" + FW + "])[ ]+", r"\1", s)
        s = re.sub(r"[ ]{2,}", " ", s)
        if s != el.text:
            el.text = s
            changed.append("in")
    # 步骤2：真实相邻的两个w:t token之间（中间隔oMath不算）
    for _ in range(10):
        touched = False
        for a in range(len(toks) - 1):
            if toks[a][0] != "t" or toks[a + 1][0] != "t":
                continue
            ea, eb = toks[a][1], toks[a + 1][1]
            ta, tb = ea.text or "", eb.text or ""
            if not ta or not tb:
                continue
            if ta[-1] in FW and tb[0] == " ":
                eb.text = tb.lstrip(" "); touched = True; changed.append("bd"); continue
            if ta[-1] == " " and tb[0] in FW:
                ea.text = ta.rstrip(" "); touched = True; changed.append("bd"); continue
            if ta[-1] == " " and tb[0] == " ":
                ea.text = ta.rstrip(" ")
                eb.text = " " + tb.lstrip(" ") if tb.lstrip(" ") else ""
                touched = True; changed.append("bd2")
        if not touched:
            break
    # 步骤3：段尾（最后inline token须为w:t才处理）
    if toks and toks[-1][0] == "t":
        el = toks[-1][1]
        if el.text and el.text.endswith(" "):
            el.text = el.text.rstrip(" ")
            changed.append("tail")
    return changed

touched = []
for i, p in enumerate(ps):
    ch = fix_paragraph_spaces(p)
    if ch:
        touched.append((i, sorted(set(ch))))
        print(f"X2 ② p#{i} {sorted(set(ch))}: {repr(ptext(p)[:64])}")
print("X2 ② 触及段:", touched)

# ---------- 复核（token流真实邻接） ----------
bad = []
for i, p in enumerate(ps):
    toks = inline_tokens(p)
    stream = "".join((el.text or "") if k == "t" else "\uE000" for k, el in toks)  # oMath占位
    # 仅w:t内部+真实w:t邻接
    if re.search(r"[ ]{2,}|[ ]+[" + FW + "]|[" + FW + "][ ]+|\xa0", stream.replace("\uE000", "\uE001")):
        # 排除占位符干扰（占位非空格非FW）
        bad.append(("wt", i))
    if toks and toks[-1][0] == "t" and (toks[-1][1].text or "").endswith(" "):
        bad.append(("tail", i))
print("X2 复核·残留:", bad)
assert not bad
print("p#14 终态:", repr(ptext(ps[14])))
tree.write(DOC, xml_declaration=True, encoding="UTF-8", standalone=True)
print("X2 document.xml 已写回")
