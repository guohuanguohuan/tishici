# -*- coding: utf-8 -*-
"""第10章逐页全文 dump＋题号/结构锚点精查"""
import fitz, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PDF = r"C:/提示词/高中物理/2019人教版高中物理教材/人教03+普通高中教科书·物理必修+第三册.pdf"
doc = fitz.open(PDF)
out = open(r"C:/提示词/工作区/_tmpP2第10章盘点0913/教材第10章全文.txt", "w", encoding="utf-8")
for i in range(29, 57):
    out.write(f"\n========== PDF页{i+1}（书页{i-4}） ==========\n")
    out.write(doc[i].get_text())
out.close()
doc.close()
print("dump完成")

# 结构锚点
txt = open(r"C:/提示词/工作区/_tmpP2第10章盘点0913/教材第10章全文.txt", encoding="utf-8").read()
for m in re.finditer(r'^\s*(\d)\s*\n?\s*[．.]?\s*(电势能和电势|电势差|电势差与电场强度的关系|电容器的电容|带电粒子在电场中的运动)', txt, re.M):
    print("节:", m.group(0).replace('\n', ' '))
print("---- 例题锚 ----")
for m in re.finditer(r'【例题\d?】|例题\s*\d|^\s*例题', txt, re.M):
    ln = txt[:m.start()].count('\n') + 1
    print(f"  行{ln}: {m.group(0)!r}")
print("---- 练习与应用/复习与提高 锚 ----")
for m in re.finditer(r'练习与应用|复习与提高|^A\s*组|^B\s*组|A组|B组', txt, re.M):
    ln = txt[:m.start()].count('\n') + 1
    print(f"  行{ln}: {m.group(0)!r}")
