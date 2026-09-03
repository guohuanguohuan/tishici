# -*- coding: utf-8 -*-
"""FX6 probe3: 编注5段完整run级结构+题块上下文；灰底越界扫描；边界空run；空格卫生"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
DOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
tree = etree.parse(DOC)
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def run_seq(p):
    out = []
    def walk(el):
        for ch in el:
            tag = etree.QName(ch).localname
            if tag == "r":
                rPr = ch.find(f"{{{W}}}rPr")
                shd = col = None
                if rPr is not None:
                    s = rPr.find(f"{{{W}}}shd")
                    if s is not None: shd = s.get(f"{{{W}}}fill")
                    c = rPr.find(f"{{{W}}}color")
                    if c is not None: col = c.get(f"{{{W}}}val")
                txt = "".join(ch.itertext())
                out.append(("R", shd, col, txt))
            elif tag in ("oMath", "oMathPara"):
                out.append(("M", "", "", "".join(ch.itertext())))
            else:
                walk(ch)
    walk(p)
    return out

# 编注5段的题块上下文：向前找题号块段
targets = [186, 275, 419, 490, 852]
for k in targets:
    print(f"\n########## p#{k} ##########")
    # 向前找题号（最近题号段）
    for j in range(k, -1, -1):
        txt = "".join(paras[j].itertext())
        m = re.match(r"^(2\.8[\d.]*-\d+．)", txt)
        if m:
            print(f"所在题: p#{j} {txt[:110]!r}")
            break
    # 题干+选项（题号段到本题【答案】前）
    for j in range(k - 1, min(k, j + 6) if False else k, 1) if False else []:
        pass
    for typ, shd, col, txt in run_seq(paras[k]):
        print(f"  {typ} shd={shd} col={col} {txt[:90]!r}")

print("\n\n=== 题干上下文（题号段起4段） ===")
for k in targets:
    for j in range(k, -1, -1):
        txt = "".join(paras[j].itertext())
        if re.match(r"^2\.8[\d.]*-\d+．", txt):
            print(f"\n-- p#{k}所在题 p#{j}:")
            for q in range(j, min(j + 5, k + 1)):
                t = "".join(paras[q].itertext())
                print(f"   p#{q}: {t[:130]!r}")
            break

# ---- 灰底越界扫描：含C9C9C9 run的段中灰底run文本 ----
print("\n\n=== 【答案】行灰底run形态（找越界：灰底含【】标签/长句/多个值粘连） ===")
n_ans = 0
for k, p in enumerate(paras):
    txt = "".join(p.itertext())
    if "【答案】" not in txt:
        continue
    n_ans += 1
    seq = run_seq(p)
    grey = [(i, t) for i, (typ, shd, col, t) in enumerate(seq) if shd == "C9C9C9"]
    if not grey:
        print(f"p#{k} 无灰底run!! 文本: {txt[:60]!r}")
        continue
    # 越界判定：灰底文本含【、】、或长度>40、或含"；"
    for i, gt in grey:
        if ("【" in gt or "】" in gt) or len(gt) > 60 or ("；" in gt and len(gt) > 30):
            print(f"p#{k} 越界候选灰底run: {gt[:80]!r}")
print("【答案】段数:", n_ans)

# ---- 边界空run缺分隔（空w:t后随[B-D]字母） ----
print("\n=== 边界空run/粘连扫描（选项行[A-D]边界） ===")
for k, p in enumerate(paras):
    txt = "".join(p.itertext())
    if not re.match(r"^\s*A．", txt):
        continue
    seq = [(typ, t) for typ, shd, col, t in run_seq(p)]
    joined = ""
    marks = []
    for typ, t in seq:
        if typ == "R":
            joined += t
        else:
            joined += f"⟦M:{t}⟧"
    # 检查A-D选项边界：B．/C．/D．前无；分隔
    for m in re.finditer(r"(?<=[^\s；;])(?=[BCD]．)", joined):
        a = joined[max(0, m.start() - 25):m.start()]
        print(f"p#{k} 无分隔边界: …{a}｜{joined[m.start():m.start()+12]}…")
