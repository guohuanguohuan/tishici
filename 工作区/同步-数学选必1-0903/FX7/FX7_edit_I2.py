# -*- coding: utf-8 -*-
"""FX7 edit I2: ①315深蓝2run去色 ②图例行000000→auto ③20段编注线性数学→oMath
④sz21剥除 ⑤空格卫生（token流边界感知，全件w:t） ⑥灰底越界2处缩回值本身"""
import os, re, copy
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
DOC = os.path.join(WK, "unpack", "I2", "word", "document.xml")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"
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

# ============ ① p#315 深蓝2run：仅剥除废止色1F4E79（灰底C9C9C9已在位） ============
n_blue = 0
for r in ps[315].iter(W + "r"):
    rpr = r.find(W + "rPr")
    if rpr is None:
        continue
    col = rpr.find(W + "color")
    if col is not None and col.get(W + "val") == "1F4E79":
        rpr.remove(col)
        n_blue += 1
print("I2 ① 315深蓝run去色:", n_blue)
assert n_blue == 2

# ============ ② 图例行 000000→auto ============
n_black = 0
for i in (1, 2):
    for r in ps[i].iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        col = rpr.find(W + "color")
        if col is not None and col.get(W + "val") == "000000":
            col.set(W + "val", "auto")
            n_black += 1
print("I2 ② 图例行色→auto:", n_black)
assert n_black == 2

# ============ ③ 编注段线性数学→oMath（20段45 span；p#210判假阳性不动） ============
SPANS = {
    12:  ["0°≤α<180°", "0°", "180°"],
    22:  ["k=tanα", "α=90°"],
    28:  ["n=(x,y)", "k=y/x", "x=0"],
    230: ["λ≠1", "λ=1"],
    316: ["|MF₁|+|MF₂|=2a", "2a>|F₁F₂|", "2a=|F₁F₂|", "2a<|F₁F₂|"],
    336: ["e=c/a∈(0,1)"],
    364: ["2(a+c)", "|PF₁||PF₂|=2b²/(1+cosθ)", "S=b²·tan(θ/2)"],
    394: ["r=S/(a+c)", "|IN|/|IP|=e"],
    416: ["||MF₁|−|MF₂||=2a", "0<2a<|F₁F₂|", "2a=0", "2a≥|F₁F₂|"],
    487: ["x²−y²=λ", "λ≠0"],
    492: ["|PF₁||PF₂|=2b²/(1−cosθ)", "S=b²·cot(θ/2)"],
    569: ["1/(k_PA·k_PB)=e²−1"],
    665: ["|AF|=p/(1−cosθ)", "|AB|=2p/sin²θ", "S=p²/(2sinθ)"],
    673: ["y_A·y_B=−p²", "1/|AF|+1/|BF|=2/p"],
    682: ["M(m,0)", "x_A·x_B=m²", "y_A·y_B=−2pm"],
    730: ["k=∓b²x₀/(a²y₀)", "k=p/y₀"],
    776: ["AF=ep/(1∓ecosθ)", "cosθ", "sinθ"],
    799: ["x=a²/m"],
    852: ["AM=λMB"],
    867: ["k=y/x"],
}

def rebuild_bianzhou(p, spans):
    assert ptext(p).startswith("【编注】")
    # 安全断言：无图/无tab/无br
    assert not any(True for _ in p.iter(W + "drawing"))
    assert not any(True for _ in p.iter(W + "tab"))
    assert not any(True for _ in p.iter(W + "br"))
    toks = inline_tokens(p)
    assert toks[0][0] == "t" and toks[0][1].text == "【编注】", "首token应為【编注】芯片"
    body = toks[1:]
    stream = ""
    owner = []  # 每 char → body token idx
    for ti, (k, el) in enumerate(body):
        s = (el.text or "") if k == "t" else "".join(t.text or "" for t in el.iter(M + "t"))
        stream += s
        owner.extend([ti] * len(s))
    # token长度表
    tlen = []
    for k, el in body:
        tlen.append(len((el.text or "")) if k == "t" else len("".join(t.text or "" for t in el.iter(M + "t"))))
    # 定位 span（顺序、不重叠；不得切断oMath token）
    marks = [False] * len(stream)  # True=math
    cursor = 0
    found = []
    for sp in spans:
        pos = stream.find(sp, cursor)
        assert pos >= 0, f"span未找到: {sp!r} in [{stream[:80]}...]"
        for j in range(pos, pos + len(sp)):
            assert not marks[j], f"span重叠: {sp!r}"
        for j in range(pos, pos + len(sp)):
            if body[owner[j]][0] == "M":
                # 该oMath须整token在span内
                tj = owner[j]
                j0 = sum(tlen[:tj])
                j1 = j0 + tlen[tj]
                assert j0 >= pos and j1 <= pos + len(sp), f"span切断oMath: {sp!r}"
        for j in range(pos, pos + len(sp)):
            marks[j] = True
        cursor = pos + len(sp)
        found.append(sp)
    # 参考文本run rPr（body第一个含非空w:t的run）
    ref_rpr = None
    for k, el in body:
        if k == "t" and el.text:
            par = el.getparent()
            while par is not None and par.tag != W + "r":
                par = par.getparent()
            if par is not None and par.find(W + "rPr") is not None:
                ref_rpr = par.find(W + "rPr")
                break
    assert ref_rpr is not None
    # 重建
    new_nodes = []
    def flush_text(buf):
        if buf:
            r = etree.Element(W + "r")
            r.append(copy.deepcopy(ref_rpr))
            t = etree.SubElement(r, W + "t")
            t.set(XMLSPACE, "preserve")
            t.text = "".join(buf)
            new_nodes.append(r)
    def make_mr(s):
        mr = etree.Element(M + "r")
        mt = etree.SubElement(mr, M + "t")
        mt.set(XMLSPACE, "preserve")
        mt.text = s
        return mr
    buf = []
    i = 0
    while i < len(stream):
        if not marks[i]:
            buf.append(stream[i])
            i += 1
        else:
            flush_text(buf); buf = []
            om = etree.Element(M + "oMath")
            while i < len(stream) and marks[i]:
                ti = owner[i]
                k, el = body[ti]
                if k == "M":
                    for child in list(el):
                        om.append(child)
                    i += tlen[ti]
                else:
                    j0 = i
                    while i < len(stream) and marks[i] and owner[i] == ti:
                        i += 1
                    om.append(make_mr(stream[j0:i]))
            new_nodes.append(om)
    flush_text(buf)
    # 字符守恒断言
    def nodes_text(nodes):
        out = []
        for n in nodes:
            if n.tag == W + "r":
                out.append("".join(t.text or "" for t in n.iter(W + "t")))
            else:
                out.append("".join(t.text or "" for t in n.iter(M + "t")))
        return "".join(out)
    assert nodes_text(new_nodes) == stream, "字符守恒失败"
    # 移除旧内容（保留pPr与【编注】芯片run），挂新内容
    keep = []
    for child in list(ps_p_children(p)):
        if child.tag == W + "pPr":
            keep.append(child)
        elif child.tag == W + "r" and "".join(t.text or "" for t in child.iter(W + "t")) == "【编注】":
            keep.append(child)
    for child in list(p):
        p.remove(child)
    for child in keep:
        p.append(child)
    for n in new_nodes:
        p.append(n)
    return found

def ps_p_children(p):
    return list(p)

total_spans = 0
for idx, spans in sorted(SPANS.items()):
    found = rebuild_bianzhou(ps[idx], spans)
    total_spans += len(found)
    print(f"I2 ③ p#{idx}: {len(found)}个span转oMath ✓ ({';'.join(found)[:60]})")
print("I2 ③ 总span数:", total_spans)

tree.write(DOC, xml_declaration=True, encoding="UTF-8", standalone=True)
print("I2 阶段①②③ 已写回（④⑤⑥待下一步脚本）")
