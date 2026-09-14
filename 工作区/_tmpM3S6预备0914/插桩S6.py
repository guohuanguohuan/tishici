# -*- coding: utf-8 -*-
"""S6 销案·S2-A5 残 9 键图债插桩（导学件 10/14/16）。
制式照 S4：\\ansfig{\\includegraphics[width=..mm]{figs/键.png}}，插于题面行后（双档恒显）。
10-G2 题面图注改留「照录自源」短注；33-12 择情境图（主图含解设标注防纯题档泄答不插）。
图源＝成卷/图资源（md5 对 清单.txt 钉值前缀）；写入域＝三片 main.tex＋figs/。零 git。
"""
import hashlib, io, os, re, shutil, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CJ = r"C:/提示词/工作区/M3-第2章量产0913/成卷"
G = CJ + "/导学件"
RES = CJ + "/图资源"

# (片目录, 键, 图文件, 宽mm, 锚行子串)
JOBS = [
    ("课时10-2.4曲线与方程", "10-G2", "10-G2.png", 36, "numboldjian 18"),
    ("课时14-2.6.2双曲线性质", "14-拓04", "14-拓04.png", 36, r"例\textbf{20}"),
    ("课时14-2.6.2双曲线性质", "14-拓11", "14-拓11.png", 40, r"变式\textbf{34}"),
    ("课时14-2.6.2双曲线性质", "14-拓18", "14-拓18.png", 38, r"例\textbf{39}"),
    ("课时14-2.6.2双曲线性质", "14-拓33-12", "14-拓33-12_情境.png", 24, r"例\textbf{46}"),
    ("课时14-2.6.2双曲线性质", "14-拓33-13", "14-拓33-13.png", 40, r"变式\textbf{47}"),
    ("课时14-2.6.2双曲线性质", "14-拓34-2", "14-拓34-2.png", 40, r"变式\textbf{49}"),
    ("课时14-2.6.2双曲线性质", "14-拓34-6", "14-拓34-6.png", 36, r"变式\textbf{53}"),
    ("课时16-2.7.2抛物线性质", "16-拓10", "16-拓10.png", 32, r"变式\textbf{39}"),
]

# 清单 md5（短码）核对表
pin = {}
for l in io.open(RES + "/清单.txt", encoding="utf-8"):
    m = re.match(r"(\S+)\s+md5:([0-9a-f]+)", l)
    if m:
        pin[m.group(1)] = m.group(2)

done = []
for d, key, img, w, anchor in JOBS:
    src = RES + "/" + img
    h = hashlib.md5(open(src, "rb").read()).hexdigest()
    expect = pin.get(img)
    assert expect and h.startswith(expect), "md5 钉值不符 %s: %s vs %s" % (img, h, expect)
    pdir = G + "/" + d
    os.makedirs(pdir + "/figs", exist_ok=True)
    shutil.copyfile(src, "%s/figs/%s" % (pdir, img))
    lines = io.open(pdir + "/main.tex", encoding="utf-8").read().splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if anchor in l and not l.lstrip().startswith("%")]
    assert len(hits) == 1, "锚不唯一 %s %s: %s" % (d, anchor, hits)
    i = hits[0]
    assert "ding{" not in lines[i]
    lines.insert(i + 1, "\\ansfig{\\includegraphics[width=%dmm]{figs/%s}}\n" % (w, img))
    io.open(pdir + "/main.tex", "w", encoding="utf-8", newline="").write("".join(lines))
    done.append("%s ← %s %dmm (锚行%d)" % (d.split("-")[0] + d.split("-")[1][:2], img, w, i + 1))
    print("插桩 %s: figs/%s ← 图资源 md5 %s… ✓，\\ansfig %dmm 插于原第 %d 行后" % (key, img, expect, w, i + 1))

# 10-G2 题面图注改短注（图已插真图，长图注收「照录自源」短注）
p10 = G + "/课时10-2.4曲线与方程/main.tex"
s = io.open(p10, encoding="utf-8").read()
old = "〔图注：折叠示意图，照录自源〕"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "〔照录自源〕")
io.open(p10, "w", encoding="utf-8", newline="").write(s)
print("10-G2 题面图注：〔图注：折叠示意图，照录自源〕→〔照录自源〕（1 处）")

# 择位登记（33-12/33-13 变体）
print("择位登记：14-拓33-12 题面插 情境图（青花瓷实物）；主图 33-12.png 系截面示意含解设标注(B/A1/A2)，防纯题档泄答不插、留存图资源。")
print("择位登记：14-拓33-13 题面插 主图（无坐标轴题图）；33-13_答案侧.png 系带建系坐标轴答案侧变体，不插、留存图资源。")
print("done:", len(done), "键")
