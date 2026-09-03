# -*- coding: utf-8 -*-
"""FX6 probe5: 疑点XML细节 + 空位④扫描 + 库内oMath形态样例"""
import re, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
DOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\FX6\扫描-probe5.txt"
tree = etree.parse(DOC)
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
buf = io.StringIO()
def P(*a): print(*a, file=buf)

def seq_of(p):
    out = []
    def walk(el, in_m=False):
        for ch in el:
            tag = etree.QName(ch).localname
            if tag == "t" and not in_m: out.append(("t", ch.text or ""))
            elif tag == "tab" and not in_m: out.append(("TAB", ""))
            elif tag == "drawing": out.append(("IMG", ""))
            elif tag in ("oMath","oMathPara"):
                out.append(("M", "".join(ch.itertext()), etree.tostring(ch, encoding="unicode")))
            else: walk(ch, in_m or tag in ("oMath","oMathPara"))
    walk(p)
    return out

# 1) p#345 细节（A2计双半空格段345）
P("=== p#345 w:t逐个 ===")
for k, p in enumerate(paras):
    if k == 345:
        for i, t in enumerate(p.iter(f"{{{W}}}t")):
            P(f"  t[{i}]={t.text!r}")
        P("  段文本:", "".join(p.itertext())[:200])

# 2) p#617 灰底run XML（两值粘连）
P("\n=== p#617 灰底值run XML ===")
for r in paras[617].iter(f"{{{W}}}r"):
    rPr = r.find(f"{{{W}}}rPr")
    if rPr is not None and rPr.find(f"{{{W}}}shd") is not None:
        P(etree.tostring(r, encoding="unicode", pretty_print=True)[:600])

# 3) p#319 / p#976 「/3」错位形态
P("\n=== p#319 序列 ===")
for typ, *rest in [(s[0], *s[1:]) for s in seq_of(paras[319])]:
    P(" ", typ, rest[0][:60] if rest else "")
P("=== p#976 序列 ===")
for s in seq_of(paras[976]):
    P(" ", s[0], (s[1][:60] if len(s)>1 else ""))

# 4) 库内既有 oMath XML 形态样例（p#6的选项oMath）
P("\n=== 库内oMath形态样例（p#6第一个oMath的XML） ===")
for s in seq_of(paras[6]):
    if s[0] == "M":
        P(s[2][:1500])
        break

# 5) 空位④多赋值粘连扫描（E件口径签名：字母直接粘连下一方程首元）
P("\n=== 空位④扫描（oMath线性化内  方程=…粘连） ===")
pat = re.compile(r"(?<=[\w\d\)\]²₀-])\s*[a-hj-zA-HJ-Z](?=[0-9]?\s*[=≠<>])")  # 弱签名
n = 0
for k, p in enumerate(paras):
    for s in seq_of(p):
        if s[0] != "M": continue
        lin = s[1]
        # 签名: =右边完整式后紧跟 新变量=（E件口径正则: rE=、)E=、I₁E= 类）
        for m in re.finditer(r"(?<=[\w\)\]²₀₁₂\}\]])(?=[a-zA-Z][₀₁₂₃]?=)", lin):
            ctx = lin[max(0,m.start()-40):m.end()+40]
            # 排除 eqArr（结构化方程组）
            P(f"p#{k}: …{ctx}…")
            n += 1
P("④候选总数:", n)

open(OUT, "w", encoding="utf-8").write(buf.getvalue())
print("written", OUT)
