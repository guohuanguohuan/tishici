# -*- coding: utf-8 -*-
"""M3 批A 五课时全域互撞扫（军师账审§八案3口径：同课时 G5↔练习↔拓展 两两）
机械层：逐课时切题块，抽取数值指纹（坐标/向量二元组、方程系数串），课时内两两求交。
凡共享指纹 ≥2 个（或 ≥1 个且含非常规指纹）者列为待判对，人工层再判条目/题式。零写入定稿层。"""
import re, io, os, itertools, sys

BASE = r"C:\提示词\工作区\M3-第2章量产0913\定稿"
FILES = {
    "01": "批A-课时01-坐标法.md",
    "02": "批A-课时02-倾斜角与斜率.md",
    "03": "批A-课时03-方向向量与法向量.md",
    "04": "批A-课时04-点斜式与斜截式.md",
    "05": "批A-课时05-两点式与一般式.md",
}
# 数值 token：整数/小数/分数/√数，兼容全半角括号逗号、unicode 负号
NUM = r"[-−–]?\d+(?:\.\d+)?(?:/\d+)?|[-−–]?√\d+(?:/\d+)?|[-−–]?\d+√\d+(?:/\d+)?|[-−–]?π"
TUPLE = re.compile(r"[（(]\s*(" + NUM + r")\s*[，,]\s*(" + NUM + r")\s*[）)]")
TRIVIAL = {"(0,0)", "(1,1)", "(1,0)", "(0,1)"}
HEAD = re.compile(r"【(\d\d-[GET][\wＢ]*?)｜")

def norm(s):
    s = s.replace("−", "-").replace("–", "-").replace("（", "(").replace("）", ")")
    s = s.replace("，", ",").replace("．", ".").replace(" ", "")
    return s

def blocks(path):
    text = io.open(path, encoding="utf-8").read()
    out, cur = [], None
    for line in text.splitlines():
        m = HEAD.search(line)
        if m:
            if cur: out.append(cur)
            cur = [m.group(1), []]
        elif line.startswith("## "):  # 节标题＝块硬边界，防件尾账表文字染入末题块指纹
            if cur: out.append(cur); cur = None
        elif cur is not None:
            cur[1].append(line)
    if cur: out.append(cur)
    # 过滤占位块（05 前移留空号席、05-T1 占位行）
    real = []
    for k, body in out:
        b = "\n".join(body)
        if "已前移课时04" in b or "占位跳过" in b:
            continue
        real.append((k, b))
    return real

def fingerprints(body):
    fps = set()
    for a, b in TUPLE.findall(body):
        t = norm("(%s,%s)" % (a, b))
        if t not in TRIVIAL:
            fps.add(t)
    return fps

report = []
for lesson, fn in sorted(FILES.items()):
    bl = blocks(os.path.join(BASE, fn))
    hits = []
    for (k1, b1), (k2, b2) in itertools.combinations(bl, 2):
        f1, f2 = fingerprints(b1), fingerprints(b2)
        shared = sorted(f1 & f2)
        if len(shared) >= 1:
            hits.append((k1, k2, shared))
    report.append((lesson, len(bl), hits))

print("=== 批A 全域互撞扫·机械层（课时内两两数值指纹交） ===")
total_pairs = 0
for lesson, n, hits in report:
    print("\n课时%s：实扫题块 %d，两两组合 %d，有共享指纹对 %d" %
          (lesson, n, n*(n-1)//2, len(hits)))
    for k1, k2, shared in hits:
        total_pairs += 1
        print("  %s ↔ %s ：共享 %s" % (k1, k2, ",".join(shared)))
print("\n合计待判对：%d（人工层逐对判条目/题式后定红旗/黄注/白，见互撞扫报告.md）" % total_pairs)
