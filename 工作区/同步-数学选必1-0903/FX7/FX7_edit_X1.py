# -*- coding: utf-8 -*-
"""FX7 edit X1: ①节级统计段2处（本节15题/本节14题） ②p#84选项tab→「；」 ③段尾空格7处清零"""
import os, re, copy
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
DOC = os.path.join(WK, "unpack", "X1", "word", "document.xml")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

tree = etree.parse(DOC)
ps = list(tree.getroot().iter(W + "p"))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

# 预计算：每节题数（按题号块前缀）
sec_counts = {}
for p in ps:
    mq = re.match(r"^(1\.2\.\d)\.\d+-\d+．", ptext(p))
    if mq:
        sec_counts[mq.group(1)] = sec_counts.get(mq.group(1), 0) + 1
print("题号块按节:", sec_counts)
assert sec_counts == {"1.2.1": 15, "1.2.5": 14}

# ---------- ① 节级统计段 ----------
RPR_FONTS = ('<w:rFonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
             'w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/>')
added = []
for i, p in enumerate(ps):
    t = ptext(p)
    m = re.match(r"^(1\.2\.[15]) (空间中的点、直线与空间向量|空间中的距离)$", t)
    if not m:
        continue
    # 排除节名锚：锚run为sz=2
    szs = [z.get(W + "val") for r in p.iter(W + "r") for z in r.iter(W + "sz")]
    if "2" in szs and "28" not in szs:
        continue
    n = sec_counts[m.group(1)]
    # 找最后一个28号标题run
    last_title_run = None
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        z = rpr.find(W + "sz")
        if z is not None and z.get(W + "val") == "28":
            last_title_run = r
    assert last_title_run is not None
    # 分隔run：克隆标题run rPr，文本全角空格
    sep_r = etree.Element(W + "r")
    sep_r.append(copy.deepcopy(last_title_run.find(W + "rPr")))
    etree.SubElement(sep_r, W + "t").text = "\u3000"
    # 统计run：rFonts+sz24+szCs24（照B件统计run形态）
    stat_r = etree.Element(W + "r")
    rpr = etree.SubElement(stat_r, W + "rPr")
    rpr.append(etree.fromstring(RPR_FONTS))
    etree.SubElement(rpr, W + "sz").set(W + "val", "24")
    etree.SubElement(rpr, W + "szCs").set(W + "val", "24")
    etree.SubElement(stat_r, W + "t").text = f"本节{n}题"
    p.append(sep_r)
    p.append(stat_r)
    added.append((i, t, n))

print("X1 ① 统计段追加:", added)
assert len(added) == 2 and sum(n for _, _, n in added) == 29

# ---------- ② 选项段 tab→「；」 ----------
run_tabs = []
tabs_groups = set()
for p in ps:
    for el in p.iter(W + "tab"):
        par = el.getparent()
        if par.tag == W + "r":
            run_tabs.append(el)
        elif par.tag == W + "tabs":
            tabs_groups.add(par)
for el in run_tabs:
    par = el.getparent()
    idx = list(par).index(el)
    tnode = etree.Element(W + "t")
    tnode.text = "；"
    par.remove(el)
    par.insert(idx, tnode)
for grp in tabs_groups:
    grp.getparent().remove(grp)
print(f"X1 ② run级tab→；: {len(run_tabs)}处（期望3）；pPr停靠定义组移除: {len(tabs_groups)}组")
assert len(run_tabs) == 3 and len(tabs_groups) == 1

for p in ps:
    txt = ptext(p)
    if "A．7.2" in txt:
        print("   选项段修复后:", repr(txt))
        assert txt == "A．7.2；B．6；C．12；D．24", txt

# ---------- ③ 段尾空格 ----------
stripped = []
for i, p in enumerate(ps):
    last = None
    for el in p.iter():
        if el.tag in (W + "t", M + "t"):
            last = el
    if last is not None and last.text and re.search(r"[ \u00A0\u3000]+$", last.text):
        stripped.append((i, repr(last.text[-12:])))
        last.text = re.sub(r"[ \u00A0\u3000]+$", "", last.text)
print("X1 ③ 段尾空格清零:", stripped)
assert len(stripped) == 7

tree.write(DOC, xml_declaration=True, encoding="UTF-8", standalone=True)
print("X1 document.xml 已写回")
