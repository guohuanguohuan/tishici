# -*- coding: utf-8 -*-
"""FX6 probe4: 完整扫描——灰底值过目/边界无分隔/nbsp串/段尾空格/双半空格/空位④"""
import re, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\FX6\扫描-probe4.txt"
tree = etree.parse(DOC)
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
buf = io.StringIO()
def P(*a):
    print(*a, file=buf)

def run_seq(p):
    out = []
    def walk(el):
        for ch in el:
            tag = etree.QName(ch).localname
            if tag == "r":
                rPr = ch.find(f"{{{W}}}rPr")
                shd = None
                if rPr is not None:
                    s = rPr.find(f"{{{W}}}shd")
                    if s is not None: shd = s.get(f"{{{W}}}fill")
                txt = "".join(ch.itertext())
                out.append(("R", shd, txt))
            elif tag in ("oMath", "oMathPara"):
                out.append(("M", "OMML", "".join(ch.itertext())))
            else:
                walk(ch)
    walk(p)
    return out

# 1) 灰底值run过目（排除标签芯片【×】，输出全部值类灰底文本）
P("=== 1) 答案值类灰底run全量（排除合规标签芯片） ===")
n_chip = n_val = 0
val_runs = []
for k, p in enumerate(paras):
    for typ, shd, txt in run_seq(p):
        if shd == "C9C9C9":
            if re.fullmatch(r"【[^】]{1,6}】", txt):
                n_chip += 1
            else:
                n_val += 1
                val_runs.append((k, txt))
P(f"标签芯片run={n_chip}  值类灰底run={n_val}")
for k, txt in val_runs:
    P(f"  p#{k}: {txt!r}")

# 2) 选项边界无分隔（B．/C．/D．前无；/tab/nbsp串——即粘连）
P("\n=== 2) 选项行无分隔边界（正例：前字符既非；也非空白；含图片选项） ===")
for k, p in enumerate(paras):
    txt = "".join(p.itertext())
    if not re.match(r"^\s*A．", txt):
        continue
    seq = run_seq(p)
    joined = ""
    for typ, shd, t in seq:
        joined += (f"⟦M:{t}⟧" if typ == "M" else t)
    for m in re.finditer(r"(?<=[^\s；;])(?=[BCD]．)", joined):
        a = joined[max(0, m.start() - 30):m.start()]
        P(f"p#{k} 无分隔: …{a}▶{joined[m.start():m.start()+14]}…")

# 3) nbsp串段（≥2连续nbsp）上下文
P("\n=== 3) nbsp串段（≥2连续\\xa0）全量上下文 ===")
for k, p in enumerate(paras):
    seq = run_seq(p)
    joined = ""
    for typ, shd, t in seq:
        joined += (f"⟦M:{t}⟧" if typ == "M" else t)
    for m in re.finditer(r"\xa0{2,}", joined):
        a = joined[max(0, m.start() - 35):m.start()]
        b = joined[m.end():m.end() + 25]
        P(f"p#{k} nbsp×{m.end()-m.start()}: …{a}⟦N⟩{b}…")

# 4) 段尾空格（w:t层，真段末元素）
P("\n=== 4) 段尾空格（末w:t结尾空格/全nbsp尾） ===")
for k, p in enumerate(paras):
    ts = [t for t in p.iter(f"{{{W}}}t")]
    if not ts:
        continue
    last = ts[-1]
    txt = last.text or ""
    if txt.endswith(" ") or txt.endswith("\xa0"):
        P(f"p#{k}: 尾字符={txt[-3:]!r} 段文本尾40={(''.join(p.itertext()))[-40:]!r}")

# 5) 双半空格（w:t层）
P("\n=== 5) 连续双半空格 ===")
for k, p in enumerate(paras):
    for t in p.iter(f"{{{W}}}t"):
        if t.text and "  " in t.text:
            i = t.text.index("  ")
            P(f"p#{k}: {t.text[max(0,i-30):i+30]!r}")

# 6) 全角标点前空格（w:t层内直接相邻或跨run拼接）
P("\n=== 6) 全角标点前空格/nbsp（w:t层，段内拼接） ===")
for k, p in enumerate(paras):
    seq = run_seq(p)
    joined = ""
    for typ, shd, t in seq:
        if typ == "R":
            joined += t
        else:
            joined += "⟦M⟧"
    for m in re.finditer(r"[ \xa0]{1,4}(?=[，。；：、．！？（）])", joined):
        if "⟦M⟧" in joined[max(0, m.start()-2):m.end()+2]:
            continue
        a = joined[max(0, m.start() - 25):m.start()]
        P(f"p#{k}: …{a}▶标点={joined[m.end()]!r}")

open(OUT, "w", encoding="utf-8").write(buf.getvalue())
print("written:", OUT, len(buf.getvalue()), "chars")
