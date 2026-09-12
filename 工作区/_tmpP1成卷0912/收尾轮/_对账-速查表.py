# -*- coding: utf-8 -*-
"""义6-3 对账：测评卷卷末「答案速查」19 值 vs 答案册 body 测-1~19 值。

两侧同法归一（去排版宏、去花括号、去空白、\\dfrac→\\frac、全角标点折半角）后逐位比较。
速查表结构＝选择题 1~11 tabular 行＋填空/解答 12~19 流水行（\\datu{...} 组）。
"""
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BODY = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\答案册\body.tex"
PAPER = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\测评卷\main.tex"


def norm(s, strict=False):
    s = re.sub(r"\\(?:unit|text|mathrm)\s*", "", s)
    s = s.replace(r"\dfrac", r"\frac")
    if not strict:
        s = s.replace("\\,", "").replace("\\ ", "")   # 单位前薄空格＝两件排布层差异，不比
        s = s.replace(r"\tan", "tan").replace(r"\sin", "sin").replace(r"\cos", "cos")  # 函数名正体/斜体＝排版层差异
    s = re.sub(r"\\(?:quad|qquad|left|right|vskip|par|noindent|datu|small|rm)\b", "", s)
    s = re.sub(r"\d*\.\?\d*\s*mm", "", s)          # 残留段间距尺寸
    s = s.replace("$", "").replace(r"\cdot", "")
    s = re.sub(r"%.*?(?=\d+．|$)", "", s)            # 行内注释残留
    s = re.sub(r"\s+", "", s)
    return s.replace("；", ";").replace("，", ",").replace("。", "")


def datu_groups(text):
    r"""按平衡括号取所有 \datu{...} 内容。"""
    out = []
    i = 0
    while True:
        j = text.find(r"\datu{", i)
        if j < 0:
            break
        k = j + len(r"\datu{")
        depth = 1
        while depth:
            if text[k] == '{':
                depth += 1
            elif text[k] == '}':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out.append(text[j + len(r"\datu{"):k])
        i = k + 1
    return out


body = open(BODY, encoding="utf-8").read()
ans = {}
for m in re.finditer(r"% pair:测-(\d+)\n\\ansitem\{\d+\}\{(.*)\}", body):
    ans[int(m.group(1))] = m.group(2)
assert len(ans) == 19, "答案册测段键数 != 19：%d" % len(ans)

paper = open(PAPER, encoding="utf-8").read()
blk = paper[paper.index("卷末答案速查"):paper.index("\\begin{document}")]
row = re.search(r"答案\s*&\s*(.*?)\\\\", blk, re.S).group(1)
cells = [c.strip() for c in row.split("&")]
quick = {i + 1: cells[i] for i in range(11)}

stream = " ".join(g for g in datu_groups(blk) if "．" in g)
stream = re.sub(r"\\quad", " ", stream)
for m in re.finditer(r"(\d+)．(.+?)(?=(?:\s*\d+．)|$)", stream, re.S):
    k = int(m.group(1))
    if 12 <= k <= 19:
        quick.setdefault(k, m.group(2).strip())
assert len(quick) == 19, "速查表取到 %d 值：%s" % (len(quick), sorted(quick))

bad = []
soft = []
LAY = {16: r"卷面速查作 $mgtan\alpha$（函数名未用 \tan 正体）；册面作 $mg\tan\alpha$",
       17: r"卷面速查单位前无薄空格 $12{N}$；册面作 $12\,\unit{N}$"}
for k in range(1, 20):
    raw_a, raw_b = ans[k], quick[k]
    a, b = norm(raw_a), norm(raw_b)
    ok = (a == b)
    if not ok:
        bad.append(k)
    elif norm(raw_a, strict=True) != norm(raw_b, strict=True):
        soft.append(k)
    print(("OK  " if ok else "DIFF"), "测-%-2d" % k, "|册:", a, "|卷:", b)

print("")
print("排布层差异（值本体一致、写法不同）：", soft if soft else "无")
for k in soft:
    print("   测-%d：%s" % (k, LAY.get(k, "")))
print("对账结论：" + ("19/19 值本体逐位一致 ✓（义6-3 关闭；排布层差异随义6-2 清扫）"
                     if not bad else "值不一致题号 %s" % bad))
sys.exit(1 if bad else 0)
