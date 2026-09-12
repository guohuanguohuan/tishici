# -*- coding: utf-8 -*-
# 课时06（1.2.1）结构断言｜批3 件1（承批1口径：组数/题数按版面印式 PDF 级＋源级双核）
# 期望：◆探究点5（\tjdnr 5＝点题+例1 同宏）／例1×5／变式1×5／【素养小结】×5／判断组头×3（子题5）／
#       课堂评价花形行＋组头标签2＋说明行1＋检测题5＋提示词2／ZSD标题3／花形行3（课前/课中/课堂）／
#       \bindopt 源级18＝讲部12＋评价6／学习目标1／课前预习1
#       （PDF 印式实测注：ZSD 标题行提取为「知识点N\n」；数字后带空格「本组共5 题」；花形四字连提「课堂评价」）
import re, sys, io
import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = r"C:\提示词\工作区\M2-第1章量产0911\成卷\导学件\课时06"
doc = pymupdf.open(BASE + r"\main.pdf")
full = "\n".join(p.get_text() for p in doc)
src = open(BASE + r"\main.tex", encoding="utf-8").read()

def pcnt(pat): return len(re.findall(pat, full))
def scnt(pat): return len(re.findall(pat, src))

checks = [
    ("PDF ◆探究点(一~五)", r"探究点[一二三四五]", 5),
    ("PDF 例1", r"例\s*1(?![\d])", 5),
    ("PDF 变式1", r"变式\s*1(?![\d])", 5),
    ("PDF 【素养小结】", r"【素养小结】", 5),
    ("PDF 判断正误组头", r"判断正误", 3),
    ("PDF 知识点标题(ZSD)", r"知识点[一二三]\n", 3),
    ("PDF 课堂评价(花形行＋组头标签)", r"课\s*堂\s*评\s*价", 2),
    ("PDF 评价说明行", r"本组共5 题", 1),
    ("PDF 评价提示词", r"提示：", 2),
    ("PDF 学习目标", r"学习目标", 1),
    ("PDF 课前预习", r"课前预习", 1),
    ("SRC \\tjdnr(探究点+例)", r"\\tjdnr\{", 5),
    ("SRC \\liB(变式)", r"\\liB\{", 5),
    ("SRC \\xiaojie", r"\\xiaojie\{", 5),
    ("SRC \\zhentib(判断子题)", r"\\zhentib\{", 5),
    ("SRC \\jiancestem(评价题)", r"\\jiancestem\{", 5),
    ("SRC \\bindopt(选项段·讲部12+评价6)", r"\\bindopt", 18),
    ("SRC \\zsd", r"\\zsd\{", 3),
    ("SRC \\huaxing(课前/课中/课堂)", r"\\huaxing\{", 3),
]
fails = []
for name, pat, want in checks:
    c = pcnt(pat) if name.startswith("PDF") else scnt(pat)
    ok = c == want
    print(f"{name}: {c}/{want} {'PASS' if ok else 'FAIL'}")
    if not ok:
        fails.append(name)
print("=" * 40)
print("RESULT:", "ALL PASS" if not fails else f"FAILS={fails}")
sys.exit(1 if fails else 0)
