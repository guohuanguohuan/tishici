# -*- coding: utf-8 -*-
"""FX7 edit I2 part2: ④sz21剥除 ⑤空格卫生（token流边界感知全件） ⑥灰底越界2处缩回值本身"""
import os, re, copy
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
DOC = os.path.join(WK, "unpack", "I2", "word", "document.xml")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
FW = "，。；：、？！"

tree = etree.parse(DOC)
ps = list(tree.getroot().iter(W + "p"))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

def inline_tokens(p):
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

# ============ ④ sz=21 剥除（空文本/含图空壳run；验真后剥） ============
n21 = 0
for r in tree.getroot().iter(W + "r"):
    rpr = r.find(W + "rPr")
    if rpr is None:
        continue
    for tag in (W + "sz", W + "szCs"):
        z = rpr.find(tag)
        if z is not None and z.get(W + "val") == "21":
            # 验真：run须为空文本或仅含图
            wt = "".join(t.text or "" for t in r.iter(W + "t"))
            has_mt = any((t.text or "").strip() for t in r.iter(M + "t"))
            assert wt == "" and not has_mt, f"sz21 run含文字，不可剥: {wt[:30]}"
            rpr.remove(z)
            n21 += 1
# m:r内sz21同样检查
n21m = 0
for r in tree.getroot().iter(M + "r"):
    rpr = r.find(W + "rPr")
    if rpr is None:
        continue
    for tag in (W + "sz", W + "szCs"):
        z = rpr.find(tag)
        if z is not None and z.get(W + "val") == "21":
            mt = "".join(t.text or "" for t in r.iter(M + "t"))
            assert mt == "", f"m:r sz21含数学文本，人工复核: {mt[:30]}"
            rpr.remove(z)
            n21m += 1
print(f"I2 ④ sz21剥除: w:r侧{n21}个元素, m:r侧{n21m}个")

# ============ ⑥ 灰底越界2处缩回值本身 ============
def split_grey_run(p, target_text, keep_head):
    """keep_head=True: 前段保留灰底、后段去灰（'轴，'→'轴'灰+','白）
       keep_head=False: 前段去灰、后段保留（'，长轴长'→','白+'长轴长'灰）"""
    for r in p.iter(W + "r"):
        wt = "".join(t.text or "" for t in r.iter(W + "t"))
        if wt != target_text:
            continue
        rpr = r.find(W + "rPr")
        assert rpr is not None and rpr.find(W + "shd") is not None
        assert len(r.findall(W + "t")) == 1
        tnode = r.find(W + "t")
        assert len(target_text) >= 2
        head_txt, tail_txt = (target_text[0], target_text[1:]) if not keep_head else (target_text[:-1], target_text[-1])
        # head run
        r2 = copy.deepcopy(r)
        r2.find(W + "t").text = tail_txt
        tnode.text = head_txt
        if not keep_head:
            # head（'，'）去灰
            h = r2.find(W + "rPr").find(W + "shd")
            # r2现在承载tail=值本身保留灰；r承载head需去灰
            h2 = rpr.find(W + "shd")
            rpr.remove(h2)
        else:
            # tail（'，'）去灰
            h2 = r2.find(W + "rPr").find(W + "shd")
            r2.find(W + "rPr").remove(h2)
        parent = r.getparent()
        parent.insert(list(parent).index(r) + 1, r2)
        return True
    return False

ok1 = split_grey_run(ps[347], "，长轴长", keep_head=False)
ok2 = split_grey_run(ps[357], "轴，", keep_head=True)
print("I2 ⑥ 灰底越界缩回: p#347 =", ok1, "; p#357 =", ok2)
assert ok1 and ok2

# ============ ⑤ 空格卫生（token流边界感知；仅w:t） ============
def fix_paragraph_spaces(p):
    changed = []
    toks = inline_tokens(p)
    for k, el in toks:
        if k == "t" and el.text and "\xa0" in el.text:
            el.text = el.text.replace("\xa0", " ")
            changed.append("nbsp")
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
                rest = tb.lstrip(" ")
                eb.text = (" " + rest) if rest else ""
                touched = True; changed.append("bd2")
        if not touched:
            break
    if toks and toks[-1][0] == "t":
        el = toks[-1][1]
        if el.text and el.text.endswith(" "):
            el.text = el.text.rstrip(" ")
            changed.append("tail")
    return changed

tp = []
for i, p in enumerate(ps):
    ch = fix_paragraph_spaces(p)
    if ch:
        tp.append((i, sorted(set(ch))))
print("I2 ⑤ 触及段数:", len(tp))
print("I2 ⑤ 明细:", tp)

# 复核
bad = []
for i, p in enumerate(ps):
    toks = inline_tokens(p)
    stream = "".join(((el.text or "") if k == "t" else "\ue000") for k, el in toks)
    if re.search(r"[ ]{2,}|[ ]+[" + FW + "]|[" + FW + "][ ]+|\xa0", stream):
        bad.append(("wt", i))
    if toks and toks[-1][0] == "t" and (toks[-1][1].text or "").endswith(" "):
        bad.append(("tail", i))
print("I2 ⑤ 复核·残留:", bad)
assert not bad

tree.write(DOC, xml_declaration=True, encoding="UTF-8", standalone=True)
print("I2 part2 已写回")
