# -*- coding: utf-8 -*-
"""改前快照同法抽取值，判定 02-T2 / 17-11 / 17-04 值面转写差异是否存量。只读。"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
G = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
SNAP = {"课时02": ("改前快照/课时02_main.tex", "课时02-倾斜角与斜率"),
        "课时17": ("改前快照/课时17_main.tex", "课时17-2.8①压轴综合一")}


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


for pid, (sp, d) in SNAP.items():
    src = io.open(os.path.join(HERE, sp.replace("/", os.sep)), encoding="utf-8").read()
    led = json.load(open(os.path.join(G, d, "值台账-%s.json" % pid), encoding="utf-8"))
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
    print(pid, "改前快照 同法抽取 差异键:", diff)
