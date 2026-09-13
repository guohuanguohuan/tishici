# -*- coding: utf-8 -*-
"""改前后比对：数学内容与键值须逐字不变，只允许选项换行/宏名变化。"""
import io, sys, re, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A"
old = open(D + r"\main.tex.bak_滚A修Q3压字0913", encoding="utf-8").read()
new = open(D + r"\main.tex", encoding="utf-8").read()

# 1) 全文数学体 \(...\) 逐段比对
math_re = re.compile(r"\\\((.+?)\\\)", re.S)
mo, mn = math_re.findall(old), math_re.findall(new)
print("数学体段数 old/new =", len(mo), "/", len(mn), "| 逐字一致 =", mo == mn)

# 2) 全文中文＋字母数字序列（剥掉所有反斜杠宏与花括号）比对
def stripped(t):
    t = re.sub(r"\\[A-Za-z]+\*?", "", t)
    return re.sub(r"[{}\s]", "", t)
print("剥宏后全文一致 =", stripped(old) == stripped(new))

# 3) 答案速查表行
for tag, txt in (("old", old), ("new", new)):
    row = [l.strip() for l in txt.splitlines() if l.strip().startswith("答案 &")]
    print(tag, "答案速查行 =", row)

print("\n--- unified diff (n=0) ---")
for l in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0):
    print(l)
