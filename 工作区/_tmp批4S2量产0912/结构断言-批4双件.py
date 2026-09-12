# -*- coding: utf-8 -*-
# 批4 结构断言（承批3 口径：组数/题数按版面印式 PDF 级＋源级双核）
# 课时07＝1.2.2（探究点5/例5/变5/小结5/判断组3子5/评价恒5/提示2/ZSD3/空13/答档8/图5行）
# 课时08＝1.2.3（探究点5/例5/变5/小结5/判断组3子5/评价恒5/提示2/ZSD3/空18/答档4/图8行）
import re, sys, io
import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = r"C:\提示词\工作区\M2-第1章量产0911\成卷\导学件"

def run(dirname, want):
    doc = pymupdf.open(BASE + "\\" + dirname + r"\main.pdf")
    full = "\n".join(p.get_text() for p in doc)
    raw = open(BASE + "\\" + dirname + r"\main.tex", encoding="utf-8").read()
    # 源级计数剥去注释行（文件头登记注释含宏名字样）
    src = "\n".join(l for l in raw.splitlines() if not l.strip().startswith("%"))
    def pcnt(pat): return len(re.findall(pat, full))
    def scnt(pat): return len(re.findall(pat, src))
    fails = []
    print(f"===== {dirname}（PDF {len(doc)} 页）=====")
    for name, pat, n in want:
        c = pcnt(pat) if name.startswith("PDF") else scnt(pat)
        ok = c == n
        print(f"{name}: {c}/{n} {'PASS' if ok else 'FAIL'}")
        if not ok:
            fails.append(name)
    print("RESULT:", "ALL PASS" if not fails else f"FAILS={fails}")
    print()
    return not fails

common07 = [
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
    ("SRC \\zsd", r"\\zsd\{", 3),
    ("SRC \\huaxing(课前/课中/课堂)", r"\\huaxing\{", 3),
]
w07 = common07 + [
    ("SRC \\kongbai(课前11+评价2)", r"\\kongbai\{\}", 13),
    ("SRC \\kongwei(选择答档9)", r"\\kongwei", 9),
    ("SRC \\bindopt(选项段)", r"\\bindopt", 26),
    ("SRC includegraphics(图调用8=图行5)", r"\\includegraphics", 8),
    ("SRC \\liubai(书写留白)", r"\\liubai\[", 4),
]
w08 = common07 + [
    ("SRC \\kongbai(课前9+课中7+评价2)", r"\\kongbai\{\}", 18),
    ("SRC \\kongwei(选择答档4)", r"\\kongwei", 4),
    ("SRC \\bindopt(选项段)", r"\\bindopt", 6),
    ("SRC includegraphics(图调用10=图行8)", r"\\includegraphics", 10),
    ("SRC \\liubai(书写留白)", r"\\liubai\[", 4),
]
ok = run("课时07", w07) and run("课时08", w08)
sys.exit(0 if ok else 1)
