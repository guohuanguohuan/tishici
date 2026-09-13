# -*- coding: utf-8 -*-
"""M3 批A 命制入槽 逐字对合（题块照录禁改核验）
七块全对合：01-E15/E16（源＝命制件 命A/B）、03-E12/E14（源＝命制件 命C/E 回修版）、
03-E13/E15/E16（源＝定稿汇总 §九9.4 命D/F/G，命制件§二无此三题）。
口径：两侧剥除全部空白后比对；源侧仅去块头加粗与「题面：」标签（随件例省去）。零写入定稿层。"""
import io, re

MZ = io.open(r"工作区\M3-第2章量产0913\命制\轮4回修与01新命-0913.md", encoding="utf-8").read()
HZ = io.open(r"工作区\M3-第2章量产0913\定稿\定稿汇总-第2章.md", encoding="utf-8").read()
F01 = r"工作区\M3-第2章量产0913\定稿\批A-课时01-坐标法.md"
F03 = r"工作区\M3-第2章量产0913\定稿\批A-课时03-方向向量与法向量.md"

def nb(t): return re.sub(r"\s+", "", t)

def 件(path, head):
    t = io.open(path, encoding="utf-8").read()
    i = t.index(head)
    rest = t[t.index("】", i) + 1:]
    m = re.search(r"\n【\d\d-|\n## ", rest)
    return rest[:m.start()] if m else rest

def src(doc, q):
    j = doc.index(q)
    rest = doc[j:]
    m = re.search(r"\n###|\n\*\*", rest[1:])
    blk = rest[:m.start()+1] if m else rest
    blk = re.sub(r"^\*\*[^*]*\*\*", "", blk)
    return blk.replace("题面：", "", 1)

cases = [
    ("01-E15", F01, "【01-E15｜", MZ, "在 Rt△ABC 中"),
    ("01-E16", F01, "【01-E16｜", MZ, "在△ABC 中，以 B 为原点"),
    ("03-E12", F03, "【03-E12｜", MZ, "直线 l 经过 A(1,2)、B(3,6) 两点"),
    ("03-E13", F03, "【03-E13｜", HZ, "**03-命D（填空·简）**"),
    ("03-E14", F03, "【03-E14｜", MZ, "已知直线 l₁: 3x−y+1=0 与 l₂: ax+2y−6=0"),
    ("03-E15", F03, "【03-E15｜", HZ, "**03-命F（解答·中）**"),
    ("03-E16", F03, "【03-E16｜", HZ, "**03-命G（填空·简）**"),
]
ok = True
for name, f, head, doc, q in cases:
    a, b = nb(件(f, head)), nb(src(doc, q))
    same = a == b
    ok &= same
    print(("PASS " if same else "FAIL ") + name, len(a), len(b))
    if not same:
        for x, (c, d) in enumerate(zip(a, b)):
            if c != d:
                print("  首异位 %d：件内…%r vs 源…%r" % (x, a[max(0,x-15):x+15], b[max(0,x-15):x+15])); break
print("逐字对合：" + ("7/7 全一致 ✓（题面/答案/详解/亲算一字未动；仅「题面：」标签随件例省去）" if ok else "存在差异，须回查"))
