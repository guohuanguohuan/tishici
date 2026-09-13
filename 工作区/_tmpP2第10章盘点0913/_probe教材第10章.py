# -*- coding: utf-8 -*-
"""P2第10章盘点探针：必修3教材PDF第10章结构扫描（只读PDF，输出到本目录）"""
import fitz, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF = r"C:/提示词/高中物理/2019人教版高中物理教材/人教03+普通高中教科书·物理必修+第三册.pdf"
doc = fitz.open(PDF)
print(f"总页数={doc.page_count}")

# 扫描 PDF 页 28~60（书页23~55），覆盖第10章及第11章起始边界
pat_sec = re.compile(r'^\s*(\d)\s*$/')                      # 独行节号
pat_any = re.compile(r'(第十章|第十一章|例题|练习与应用|复习与提高|科学漫步|思考与讨论|演示|实验|做一做|STSE|说一说)')
for i in range(27, 62):
    t = doc[i].get_text()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    hits = [l for l in lines if pat_any.search(l)]
    if hits:
        print(f"--- PDF页{i+1}(书页{i+1-5}) ---")
        for h in hits[:14]:
            print("   ", h[:60])
doc.close()
