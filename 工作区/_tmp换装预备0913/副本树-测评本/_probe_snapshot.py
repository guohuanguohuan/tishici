# -*- coding: utf-8 -*-
"""只读探查④（修正）：值快照丁区 51 键 vs body.tex ansitem 行逐键恒等核对。"""
import io, os, re, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册"
snap = json.load(io.open(os.path.join(ROOT, "值快照.json"), encoding="utf-8"))
d = {k: v for k, v in snap.items() if k.startswith(("测-", "滚A-", "滚B-"))}
lines = io.open(os.path.join(ROOT, "body.tex"), encoding="utf-8").read().split("\n")
i0 = next(i for i, l in enumerate(lines) if "【丁】" in l)

cur, pairs = None, {}
for ln in lines[i0:]:
    m = re.match(r"^% pair:(\S+)$", ln.strip())
    if m:
        cur = m.group(1); continue
    if cur:
        m = re.match(r"^\\ansitem\{(\d+)\}\{(.*)\}$", ln.strip())
        if m:
            pairs[cur] = m.group(2)
            cur = None

print("body 丁区 ansitem 键数:", len(pairs), "| 快照丁区键数:", len(d))
print("键集相等:", set(pairs) == set(d))
diff = [(k, pairs[k], d[k]) for k in d if pairs.get(k) != d[k]]
print("值不等键:", diff if diff else "0（51/51 恒等）")
