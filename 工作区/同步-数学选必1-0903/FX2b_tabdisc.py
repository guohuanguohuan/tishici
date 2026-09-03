# -*- coding: utf-8 -*-
# FX2b_tabdisc：区分 真tab字符(<w:tab/> 父=w:r) vs 制表位定义(<w:tab w:pos 父=w:tabs)
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

# 全文档
char_tabs = []  # (para_idx, parent tag, has pos)
stop_defs = []
for i, p in enumerate(paras):
    for t in p.iter(f"{{{W}}}tab"):
        parent = t.getparent()
        pt = etree.QName(parent).localname if parent is not None else "?"
        has_pos = t.get(f"{{{W}}}pos") is not None
        if pt == "r" and not has_pos:
            char_tabs.append((i, "r", "NOpos"))
        elif pt == "tabs":
            stop_defs.append((i, "tabs", has_pos))
        else:
            char_tabs.append((i, pt, has_pos))  # 其他

print("=== 真tab字符（父=r）===")
print("数量:", len([c for c in char_tabs if c[1]=='r']))
# 实际tab字符所在段
from collections import Counter
paras_with_chartab = sorted(set(c[0] for c in char_tabs if c[1]=='r'))
print("所在段数:", len(paras_with_chartab), paras_with_chartab)
print()
print("=== 制表位定义（父=tabs）===")
print("数量:", len(stop_defs))
print("所在段数:", len(set(d[0] for d in stop_defs)))
print("各段制表位数分布:", Counter(d[0] for d in stop_defs))
