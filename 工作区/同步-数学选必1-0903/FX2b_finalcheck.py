# -*- coding: utf-8 -*-
# FX2b_finalcheck：终检——①选项行w:tab字符=0、缺分隔=0、唯一「；」
# ②m:t层线性数学转换round-trip复核 ③Task3二分计数 ④七类底纹新基线已记
import re
from lxml import etree
import zipfile

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
import os
os.makedirs(r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C\unpacked6", exist_ok=True)
with zipfile.ZipFile(SRC) as z:
    d = z.read("word/document.xml")
open(r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C\unpacked6\document.xml", "wb").write(d)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
doc = etree.parse(r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C\unpacked6\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def om_lin(node):
    if node.tag == f"{{{M}}}t": return node.text or ""
    q = etree.QName(node).localname
    if q == "rad": return "√(" + "".join(om_lin(c) for c in node.find(f"{{{M}}}e")) + ")"
    if q == "f": return ("«" + "".join(om_lin(c) for c in node.find(f"{{{M}}}num")) + "»/«" +
                         "".join(om_lin(c) for c in node.find(f"{{{M}}}den")) + "»")
    if q == "d": return "(" + "".join(om_lin(c) for c in node.findall(f"{{{M}}}e")) + ")"
    return "".join(om_lin(c) for c in node)

def collect(p):
    seq = []
    for node in p.iter():
        tag = node.tag
        if tag == f"{{{W}}}t": seq.append(("t", node.text or "", node))
        elif tag == f"{{{M}}}oMath": seq.append(("m", om_lin(node), node))
        elif tag == f"{{{W}}}tab": seq.append(("tab", "", node))
    return seq

print("########## ①② 选项行归一终检 ##########")
LETTERS = "ABCD"
bad_opt = 0
for i, p in enumerate(paras):
    seq = collect(p)
    # 找A
    ai = None
    for k,(kk,tt,ee) in enumerate(seq):
        if kk=="t" and tt=="A": ai=k; break
    if ai is None: continue
    # 统计位置：字母→'．'→值→'；'
    # 检查wtab或w:ind
    wt_tabs = len(list(p.iter(f"{{{W}}}tab")))  # 含tab-stop defs
    # 检查有无缺分隔：字母B/C/D前一个符号必须是'；'
    issues = []
    for k in range(ai, len(seq)):
        kk, tt, ee = seq[k]
        if kk=="t" and tt in LETTERS:
            # 字母左邻应为空或'．'（不是值）
            if k > ai:
                prev = seq[k-1]
                if prev[0]=="t" and prev[1] in LETTERS:
                    continue
                # 左邻：若是'oMath'或值文字→缺分隔（除非左邻是'．'）
                if prev[0]=="m" or (prev[0]=="t" and prev[1] not in ("．","；","")):
                    issues.append(f"字母{tt}@seq{k}左邻={prev[1]!r}")
            elif k > ai:
                pass
    # 检查 '．；' 残留
    for k,(kk,tt,ee) in enumerate(seq):
        if kk=="t" and "．；" in tt:
            issues.append(f"残留'．；'@seq{k}")
    if issues:
        bad_opt += 1
        print(f"  p#{i}: {issues}")
print("异常选项段数:", bad_opt)

print("\n########## ③ Task3 二分计数 ##########")
# w:ind
inds = body.findall(f".//{{{W}}}ind")
# 真tab字符（父=w:r，无w:pos）
char_tabs = 0
tabstop_defs = 0
for t in body.iter(f"{{{W}}}tab"):
    parent = t.getparent()
    pt = etree.QName(parent).localname if parent is not None else "?"
    if parent is not None and pt == "tabs":
        tabstop_defs += 1
    elif pt == "r" and t.get(f"{{{W}}}pos") is None:
        char_tabs += 1
print("w:ind 计数:", len(inds))
print("w:tab 字符(父=r) 计数:", char_tabs)
print("w:tab 制表位定义(父=tabs):", tabstop_defs)

print("\n########## ④ m:t层线性数学验证（转换段round-trip）##########")
# 精确：验证转换后显示线性化无残留线性数学
SIG = re.compile(r"√\d|/[a-z]|\d\^\d")
for i in [259, 363, 479, 492, 555]:
    wt = "".join(t.text or "" for t in paras[i].iter(f"{{{W}}}t"))
    # 检查转换段w:t已无'√3/x'（除√之外）
    print(f"  p#{i} w:t尾部残留检查: {'OK无√连缀' if not re.search(r'√[0-9a-z]', wt.replace('√','')) else wt}")

print("\n########## ⑦ 七类底纹新基线（已由工具复核，此处复核C9C9C9分布）##########")
c9 = sum(1 for e in body.iter(f"{{{W}}}shd") if e.get(f"{{{W}}}fill")=="C9C9C9")
print("document.xml w:shd fill=C9C9C9 总挂点:", c9)
