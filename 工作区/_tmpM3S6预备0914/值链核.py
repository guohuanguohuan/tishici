# -*- coding: utf-8 -*-
"""件面 ansitem 值 ≡ 值台账 vals 逐字核（6 片）。只读。"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
PIECES = {"课时02": "课时02-倾斜角与斜率", "课时03": "课时03-方向向量与法向量",
          "课时10": "课时10-2.4曲线与方程", "课时14": "课时14-2.6.2双曲线性质",
          "课时16": "课时16-2.7.2抛物线性质", "课时17": "课时17-2.8①压轴综合一"}


def find_brace(s, i):
    d, j = 0, i
    while j < len(s):
        if s[j] == "\\" and j + 1 < len(s):
            j += 2
            continue
        if s[j] == "{":
            d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0:
                return s[i + 1:j], j
        j += 1
    raise ValueError


for pid, d in PIECES.items():
    src = io.open(os.path.join(ROOT, d, "main.tex"), encoding="utf-8").read()
    led = json.load(open(os.path.join(ROOT, d, "值台账-%s.json" % pid), encoding="utf-8"))
    vals = led["vals"]
    tex = {}
    cur = None
    for ln in src.split("\n"):
        ls = ln.strip()
        if ls.startswith("%"):
            continue
        mb = re.match(r"\\begin\{ansblock\}\[([^\]]+)\]", ls)
        if mb:
            cur = mb.group(1)
            continue
        ma = re.search(r"\\ansitem\{(\d+)\}\{", ls)
        if ma and cur:
            v, _ = find_brace(ls, ma.end() - 1)
            tex[cur] = v
    diff = [k for k in vals if (tex.get(k) or "") != (vals.get(k) or "")]
    print(pid, "件面ansitem数", len(tex), "| 台账vals数", len(vals), "| 件面≡台账:", not diff, diff[:3])
