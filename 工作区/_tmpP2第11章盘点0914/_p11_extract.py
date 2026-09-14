# -*- coding: utf-8 -*-
"""P2溢出·第11章盘点探针：必修3教材PDF第11章逐页dump（只读PDF，输出到本目录）
体例照 _tmpP2第10章盘点0913/教材第10章全文.txt（页标注＝========== PDF页N（书页M）==========）
边界：第11章＝PDF页57~82（书页52~77），第十二章起PDF页83（书页78）。
"""
import fitz, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PDF = r"C:/提示词/高中物理/2019人教版高中物理教材/人教03+普通高中教科书·物理必修+第三册.pdf"
OUT = r"C:/提示词/工作区/_tmpP2第11章盘点0914/教材第11章全文.txt"
OFFSET = 5  # 书页 = PDF页 - 5
P0, P1 = 57, 82  # PDF页闭区间

doc = fitz.open(PDF)
assert doc.page_count >= P1, f"页数不足: {doc.page_count}"
n_chars = 0
with open(OUT, "w", encoding="utf-8") as f:
    for i in range(P0 - 1, P1):
        t = doc[i].get_text()
        n_chars += len(t.strip())
        f.write(f"\n========== PDF页{i+1}（书页{i+1-OFFSET}） ==========\n")
        f.write(t)
doc.close()
print(f"落盘 {OUT}")
print(f"PDF页{P0}~{P1}（书页{P0-OFFSET}~{P1-OFFSET}），共{P1-P0+1}页，非空字符{n_chars}")
