# -*- coding: utf-8 -*-
"""只读探查②：答案册丁区（测/滚A/滚B）键结构＋卷件 \ti 题号集（键账预核）。"""
import io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷"
body = io.open(os.path.join(ROOT, "答案册/body.tex"), encoding="utf-8").read()
lines = body.split("\n")

i0 = next(i for i, l in enumerate(lines) if "【丁】" in l)
seg = lines[i0:]
cur = None
recs = []
for ln in seg:
    m = re.match(r"^% pair:(\S+)$", ln.strip())
    if m:
        cur = {"key": m.group(1), "ansitem": None, "notes": []}
        recs.append(cur)
        continue
    if cur is None:
        continue
    m = re.match(r"^\\ansitem\{(\d+)\}\{(.*)\}$", ln.strip())
    if m and cur["ansitem"] is None:
        cur["ansitem"] = (m.group(1), m.group(2))
        continue
    m = re.match(r"^\\ansline\{(.+?)\}\{(.*)\}$", ln.strip())
    if m:
        cur["notes"].append((m.group(1), m.group(2)))

print("丁区键数:", len(recs))
for pre in ("测-", "滚A-", "滚B-"):
    rs = [r for r in recs if r["key"].startswith(pre)]
    print("%s 键 %d | ansitem 齐 %d | 无值 %s | 解析行数分布 %s" % (
        pre, len(rs), sum(1 for r in rs if r["ansitem"]),
        [r["key"] for r in rs if not r["ansitem"]],
        sorted({len(r["notes"]) for r in rs})))
bad = [r["key"] for r in recs if r["ansitem"] and r["key"].split("-")[-1] != r["ansitem"][0]]
print("键号≠ansitem号:", bad)
lab = sorted({l for r in recs for l, _ in r["notes"]})
print("解析标签集:", lab)
# 值长度分布（灰底/括线判据估高用）
long_ = [(r["key"], len(r["ansitem"][1]) + sum(len(v) for _, v in r["notes"])) for r in recs if r["ansitem"]]
long_.sort(key=lambda x: -x[1])
print("最长值前 8:", long_[:8])
print("最短值后 5:", long_[-5:])

# 卷件题号集
for name in ("测评卷", "滚动卷/滚A", "滚动卷/滚B"):
    t = io.open(os.path.join(ROOT, name, "main.tex"), encoding="utf-8").read()
    tis = re.findall(r"^  \\ti\{(\d+)\}", t, re.M)
    print(name, "\\ti 题数:", len(tis), "题号:", ",".join(tis))
    print("   \\kongbai 次数:", len(re.findall(r"\\kongbai", t)),
          "| \\kw 次数:", len(re.findall(r"\\kw\b", t)),
          "| \\qpart 次数:", len(re.findall(r"\\qpart\{", t)))
