# -*- coding: utf-8 -*-
r"""反例探针：摘掉 `\jpcol` 里的 \linewidth/\columnwidth 补钉行，量括线实际取宽。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
d = "测评卷"
src = os.path.join(HERE, d, "main-fix.tex")
dst = os.path.join(HERE, d, "main-nolinewidth.tex")
lines = open(src, encoding="utf-8").read().splitlines(True)
n = 0
out = []
for l in lines:
    if "setlength" in l and "linewidth" in l and "jpcolw" in l:
        n += 1
        out.append("  %% 反例探针：此行（\\linewidth/\\columnwidth 补钉）已摘除\n")
        continue
    out.append(l)
open(dst, "w", encoding="utf-8").write("".join(out))
print("摘除补钉行 %d 处 → %s" % (n, os.path.basename(dst)))
