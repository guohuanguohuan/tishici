# -*- coding: utf-8 -*-
"""只读探查③：测评卷六宏 vs qp-m3.sty 版面基准逐项对照（换装版面漂移源排查）。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷/测评卷"
STY = r"C:/提示词/工作区/_tmpM3toolchain0913/qp-m3.sty"
six = ["qp-fonts.tex", "qp-layout.tex", "qp-parts.tex", "qp-headfoot.tex", "qp-titles.tex", "qp-blocks.tex"]
t6 = "\n".join(io.open(os.path.join(ROOT, f), encoding="utf-8").read() for f in six)
ts = io.open(STY, encoding="utf-8").read()

pats = [r"\\\\normalsize\}\{[^}]*\}\{[^}]*\}", r"\\renewcommand\{\\normalsize\}\{[^}]*\}",
        r"\\DeclareMathSizes\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}",
        r"\\setlength\{\\columnsep\}\{[^}]*\}", r"\\setlength\{\\columnseprule\}\{[^}]*\}",
        r"\\setlength\{\\parindent\}\{[^}]*\}", r"\\setlength\{\\parskip\}\{[^}]*\}",
        r"\\linespread\{[^}]*\}", r"\\flushbottom|\\raggedbottom", r"\\setlength\{\\multicolsep\}\{[^}]*\}",
        r"\\RequirePackage\[[^\]]*\]\{geometry\}", r"\\usepackage\[[^\]]*\]\{geometry\}",
        r"\\multicolundershoot=[0-9pt]*", r"\\tolerance=[0-9]*", r"\\emergencystretch=[^%\n]*",
        r"\\arrayrulewidth\}\{[^}]*\}", r"\\arraystretch\}\{[^}]*\}", r"\\tabcolsep\}\{[^}]*\}",
        r"\\setCJKmainfont[^%]*", r"\\xeCJKsetup\{[^%]*\}"]
for p in pats:
    a = re.findall(p, t6)
    b = re.findall(p, ts)
    tag = "SAME" if [x.strip() for x in a] == [x.strip() for x in b] else "DIFF"
    print("%-4s | 六宏: %-70s | sty: %s" % (tag, (a[:2] or ["-"]), (b[:2] or ["-"])))
