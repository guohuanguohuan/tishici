# -*- coding: utf-8 -*-
"""FX9 probe10: p#209完整XML＋p#79（公式型答案值挂灰先例）run解剖＋全件空格邻接全角标点复扫。"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W}

root = etree.parse("X1_document.xml").getroot()
paras = root.find("w:body", NS).findall("w:p", NS)

xml209 = etree.tostring(paras[209], encoding="unicode", pretty_print=False)
xml209 = re.sub(r'\sxmlns:\w+="[^"]*"', "", xml209)
print("### p#209 full XML (namespaces stripped):")
print(xml209)
print()

xml79 = etree.tostring(paras[79], encoding="unicode", pretty_print=False)
xml79 = re.sub(r'\sxmlns:\w+="[^"]*"', "", xml79)
print("### p#79 full XML (公式型答案值先例):")
print(xml79)
print()

# 全件复扫：token流（w:t字符＋oMath原子）中空格/nbsp邻接全角标点（排除【答案】/【知识点】标签后规定空格位）
FW = "，；。：、！？】"
def tokens(p):
    toks = []
    def walk(el):
        for ch in el:
            q = etree.QName(ch)
            if q.namespace == W and q.localname == "t":
                toks.append(("t", ch.text or ""))
            elif q.namespace == M and q.localname in ("oMath", "oMathPara"):
                toks.append(("M", "".join(t.text or "" for t in ch.iter("{%s}t" % M))))
            elif q.namespace == W and q.localname == "drawing":
                toks.append(("I", ""))
            elif q.namespace == W and q.localname in ("r", "hyperlink"):
                walk(ch)
    walk(p)
    return toks

print("### 全件空格邻接全角标点复扫（token流口径）")
hits = 0
for i, p in enumerate(paras):
    toks = tokens(p)
    stream = "".join(("⟦M⟧" if k == "M" else ("⟦I⟧" if k == "I" else v)) for k, v in toks)
    for m in re.finditer(r"[ \xa0\u3000]", stream):
        pos = m.start()
        prev = stream[pos - 1] if pos > 0 else ""
        nxt = stream[pos + 1] if pos + 1 < len(stream) else ""
        # 规定空格位：【答案】/【知识点】/【详解】等标签紧跟其后的单个半角空格
        if prev == "】" and stream[max(0, pos - 4):pos] in ("【答案】", "【知识点】", "【详解】", "【分析】", "【点睛】", "【编注】"):
            continue
        if prev in FW or nxt in FW:
            hits += 1
            print("p#%d: %r ←prev=%r next=%r :: …%s…" % (i, m.group(0), prev, nxt, stream[max(0, pos - 18):pos + 14]))
print("邻接命中总数:", hits)
