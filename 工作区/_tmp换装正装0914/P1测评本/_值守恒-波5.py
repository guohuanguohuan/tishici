# -*- coding: utf-8 -*-
"""波5 值守恒终检：tex ansblock 值==值快照值 逐字（读数附 _门谱读数/）。"""
import io, sys, json, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = Path(__file__).parent
snap = json.loads((Path(r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\答案册") / "值快照.json").read_text(encoding="utf-8"))
t = (HERE / "测评卷" / "main.tex").read_text(encoding="utf-8")
pat = re.compile(r"\\begin\{ansblock\}\[(测-\d+)\]\n  % ans:\1\n  \\ansitem\{\d+\}\{(.*?)\}\n  \\end\{ansblock\}", re.S)
found, bad = 0, []
for m in pat.finditer(t):
    k, v = m.group(1), m.group(2)
    found += 1
    if snap[k] != v:
        bad.append(k)
out = f"值守恒终检：tex ansblock {found} 块（期望 19）值==快照值逐字——{'PASS' if found == 19 and not bad else 'FAIL ' + str(bad)}"
print(out)
(HERE / "_门谱读数" / "_值守恒-波5.txt").write_text(out + "\n", encoding="utf-8")
sys.exit(0 if found == 19 and not bad else 1)
