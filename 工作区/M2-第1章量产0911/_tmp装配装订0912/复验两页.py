# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
OUT = r"C:\提示词\工作区\M2-第1章量产0911\_tmp装配装订0912\目验"
for rel, p in [("拓展册/上册", 5), ("练习件/课时10", 2)]:
    d = pymupdf.open(os.path.join(ROOT, rel, "main.pdf"))
    t = d[p - 1].get_text().replace("\n", "")
    print(rel, f"p{p}", "含57.", "57." in t, "| 含58.", "58." in t, "| 含如图所示", "如图所示" in t)
    d[p - 1].get_pixmap(dpi=150).save(os.path.join(OUT, f"复验_{rel.replace('/', '_')}_p{p}.png"))
    d.close()
