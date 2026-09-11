# 逻辑闸试点0911 · 裁判版提取器
# 从 答案册/body.tex 花括号配平提取 6 题（\ansitem 值组＋\ansline{详解} 体），落《答案-裁判版.md》。
# 只读本件与源件；产物仅写本目录。
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:/提示词/工作区/字替对照-0909/靠齐样张-0910/答案册/body.tex"
OUT = os.path.join(HERE, "答案-裁判版.md")

BS = chr(92)  # 反斜杠（防转写层剥除）


def read_group(s, i):
    assert s[i] == "{", "not a group at %d" % i
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced braces")


def parse_entry(n):
    k = src.find(BS + "ansitem{%d}" % n)
    assert k >= 0, "ansitem %d not found" % n
    _, pos = read_group(src, src.find("{", k))        # 题号组
    val, pos = read_group(src, src.find("{", pos))    # 答案值组
    nxt = src.find(BS + "ansitem{%d}" % (n + 1))
    end = min(p for p in (nxt if nxt >= 0 else len(src),
                          src.find(BS + "txsummaryhead") if src.find(BS + "txsummaryhead") >= 0 else len(src))
              if p > pos)
    seg = src[pos:end]
    d = seg.find(BS + "ansline{详解}")
    assert d >= 0, "xiangjie of %d not found" % n
    _, p2 = read_group(seg, seg.find("{", d))
    det, _ = read_group(seg, seg.find("{", p2))
    return val.strip(), det.strip()


src = io.open(SRC, encoding="utf-8").read()

SAMPLE = [(1, "选择"), (2, "选择"), (5, "填空"), (6, "填空"), (11, "解答"), (12, "解答")]

lines = [
    "# 逻辑闸试点0911 · 答案-裁判版（封印件）",
    "",
    "> 来源：`工作区/字替对照-0909/靠齐样张-0910/答案册/body.tex` 逐条目原样照抄（脚本花括号配平提取，杜绝转抄误差；提取器＝同目录 `_抽取裁判版.py`）。",
    "> 收录口径：题号＋[答案]值＋[详解]全段原文；[分析]、[点睛]、题型行、题型总结块未收录（非判分结论，原文仍在源件）。双解法段型（题15）不在本抽样。",
    "> 封印纪律：本件仅裁判（主脑）可见；解题臂只取同目录《题目-盲解版.md》。",
    "",
]
for n, kind in SAMPLE:
    val, det = parse_entry(n)
    lines += ["## 题%d（%s）" % (n, kind), "", "[答案] %s" % val, "", "[详解] %s" % det, ""]
    print("题%d 值=%s 详解=%d字" % (n, val, len(det)))

io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("written:", OUT)
