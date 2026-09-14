# -*- coding: utf-8 -*-
"""波5 编译三零双档汇总（读 main.log/main-pure.log＋PDF 页数；读数写 _门谱读数/）。"""
import io, re, sys
from pathlib import Path
import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = Path(__file__).parent / "测评卷"
OUT = Path(__file__).parent / "_门谱读数" / "_编译三零双档汇总.txt"
WANT = {f"测-{i}" for i in range(1, 20)}

L = ["# P1 测评本·编译三零双档汇总（波5，2026-09-14）", ""]
logsets = {}
for tag, lg in [("印本档true（两遍稳态）", "main.log"), ("纯题档pure（两遍稳态）", "main-pure.log")]:
    t = (HERE / lg).read_text(encoding="utf-8", errors="replace")
    err = len(re.findall(r"^! ", t, re.M))
    ovh = len(re.findall(r"Overfull \\hbox", t))
    ovv = len(re.findall(r"Overfull \\vbox", t))
    mc = len(re.findall(r"Missing character", t))
    keys = set(re.findall(r"M3-ANSKEY: (\S+)", t))
    logsets[tag] = keys
    d = pymupdf.open(HERE / lg.replace(".log", ".pdf"))
    n = len(d)
    d.close()
    ok = (err == 0 and ovh == 0 and ovv == 0 and mc == 0)
    L.append(f"- {tag}：Error {err}｜Overfull h{ovh}·v{ovv}｜Missing char {mc}（三零{'✓' if ok else '✗'}）"
             f"｜M3-ANSKEY {len(keys)} 键｜页数 {n}")
a, b = logsets.values()
L += ["", f"- 两档 M3-ANSKEY 键集合恒等：{'✓' if a == b else '✗'}｜＝键账 测-1..19：{'✓' if a == WANT else '✗'}",
      f"- M3-TAILFILL：true log {len(re.findall('M3-TAILFILL', (HERE/'main.log').read_text(encoding='utf-8', errors='replace')))} 处"
      f"（附卷尾块）｜pure log {len(re.findall('M3-TAILFILL', (HERE/'main-pure.log').read_text(encoding='utf-8', errors='replace')))} 处（附卷整页跳过＝设计内）"]
txt = "\n".join(L) + "\n"
OUT.write_text(txt, encoding="utf-8")
print(txt)
