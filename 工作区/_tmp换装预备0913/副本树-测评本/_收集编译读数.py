# -*- coding: utf-8 -*-
r"""汇总三件各档 log 读数 → _双档编译读数.md（每档跑两遍，取末遍 log）"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
FACES = ["main", "main-pure", "main-fix", "main-pure-fix", "main-ctl",
         "main-ctl-fixprobe", "main-ctl-parprobe"]
rows = []
for d in ("测评卷", "滚动卷A", "滚动卷B"):
    for f in FACES:
        lg = os.path.join(HERE, d, f + ".log")
        if not os.path.exists(lg):
            continue
        s = open(lg, encoding="utf-8", errors="replace").read()
        pg = re.search(r"Output written on \S+ \((\d+) pages", s)
        rows.append((d, f,
                     len(re.findall(r"(?m)^! ", s)),
                     len(re.findall(r"Overfull .vbox", s)),
                     len(re.findall(r"Overfull .hbox", s)),
                     len(re.findall(r"Underfull", s)),
                     len(re.findall(r"Missing character", s)),
                     pg.group(1) if pg else "?",
                     len(re.findall(r"M3.ANSKEY", s))))
head = ["| 件 | 档 | error（`^! `） | Overfull vbox | Overfull hbox | Underfull | Missing char | 页数 | M3-ANSKEY |",
        "|---|---|---|---|---|---|---|---|---|"]
body = ["| %s | %s | %d | %d | %d | %d | %d | %s | %d |" % r for r in rows]
txt = "# 双档编译读数（每档均跑两遍，取末遍 log）\n\n" + "\n".join(head + body) + "\n"
open(os.path.join(HERE, "_双档编译读数.md"), "w", encoding="utf-8").write(txt)
print(txt)
