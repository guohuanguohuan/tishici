# -*- coding: utf-8 -*-
"""FX6 probe8: p#918/p#1147等d内部m:r切分 + 库内oMath完整XML模板 + p#1147所在题"""
import re, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H"
tree = etree.parse(BASE + r"\word\document.xml")
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
buf = io.StringIO()
def P(*a): print(*a, file=buf)

def om_leaf(om):
    """叶子级切分: (tag, text) for m:r and structure markers with children text"""
    out = []
    def walk(el):
        for ch in el:
            ln = etree.QName(ch).localname
            if ln == "r":
                out.append(("R", "".join(ch.itertext())))
            elif ln in ("d", "f", "sSup", "sSub", "eqArr", "rad"):
                # 打印结构的子叶子
                sub = []
                def walk2(e2):
                    for c2 in e2:
                        l2 = etree.QName(c2).localname
                        if l2 == "r": sub.append("".join(c2.itertext()))
                        elif l2 not in ("dPr","fPr","sSupPr","sSubPr","eqArrPr","radPr","ctrlPr","rPr"):
                            walk2(c2)
                walk2(ch)
                out.append((ln, sub))
    walk(om)
    return out

for k in (57, 59, 293, 365, 524, 905, 918, 1131, 1147, 1173, 1252):
    for om in paras[k].iter(f"{{{M}}}oMath"):
        P(f"\np#{k}: " + repr(om_leaf(om))[:400])

# p#1147所在题与上下文
P("\n=== p#1147上下文 ===")
for q in range(1140, 1150):
    P(f"  p#{q}:", "".join(paras[q].itertext())[:100])

# 库内简单oMath完整XML模板（p#12 第一个）
P("\n=== 库内oMath完整XML（p#12首个，截1500字） ===")
for om in paras[12].iter(f"{{{M}}}oMath"):
    s = etree.tostring(om, encoding="unicode")
    # 去ns声明噪声
    s = re.sub(r'xmlns:\w+="[^"]*"\s*', '', s)
    P(s[:1500])
    break

# 检查库内 m:r 是否带 w:rPr（rFonts）
P("\n=== 库内m:r的rPr形态（p#12首oMath首m:r） ===")
for om in paras[12].iter(f"{{{M}}}oMath"):
    for mr in om.iter(f"{{{M}}}r"):
        s = etree.tostring(mr, encoding="unicode")
        s = re.sub(r'xmlns:\w+="[^"]*"\s*', '', s)
        P(s[:500])
        break
    break

open(BASE.replace("tmp\\FX6_H", "FX6") + r"\扫描-probe8.txt", "w", encoding="utf-8").write(buf.getvalue())
print("written")
