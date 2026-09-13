# -*- coding: utf-8 -*-
r"""滚A p1 换装漂移定位：逐行 bbox+文本 数值对勘（原印面 vs 对照件），点名每一差异行。"""
import io, os, sys, re
import pymupdf as fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [("滚动卷A", r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A\main.pdf", "main-ctl-fixprobe.pdf"),
         ("滚动卷B", r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚B\main.pdf", "main-ctl-fixprobe.pdf"),
         ("测评卷", r"C:\提示词\工作区\M2-第1章量产0911\成卷\测评卷\main.pdf", "main-ctl-fixprobe.pdf")]


def lines(doc):
    r = []
    for pno, pg in enumerate(doc, 1):
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                bb = l["bbox"]
                t = "".join(s["text"] for s in l["spans"])
                f = "+".join(sorted({re.sub(r"-0$", "", s["font"]) for s in l["spans"]}))
                r.append((pno, round(bb[0], 1), round(bb[1], 1), round(bb[2], 1), round(bb[3], 1), t, f))
    return r


for label, opath, nfile in PAIRS:
    o = fitz.open(opath)
    n = fitz.open(os.path.join(HERE, label, nfile))
    lo, ln = lines(o), lines(n)
    print("\n### %s：%s vs %s（行 %d / %d）" % (label, os.path.basename(opath), nfile, len(lo), len(ln)))
    key = lambda r: (r[0], round(r[2], 0))
    mo = {key(r): r for r in lo}
    mn = {key(r): r for r in ln}
    bad = 0
    for k in sorted(set(mo) | set(mn)):
        a, b = mo.get(k), mn.get(k)
        if a is None or b is None:
            print("  页%d y%.0f 仅%侧存在：%s" % (k[0], k[1], "新" if a is None else "原",
                                                  (b or a)[5][:28])); bad += 1; continue
        dx0, dx1, dy = b[1] - a[1], b[3] - a[3], b[2] - a[2]
        if abs(dx0) > 0.4 or abs(dx1) > 0.4 or abs(dy) > 0.4 or a[5] != b[5]:
            bad += 1
            print("  p%d y%.0f Δx0=%+.1f Δx1=%+.1f Δy=%+.1f | %s%s"
                  % (k[0], a[2], dx0, dx1, dy, a[5][:26],
                     "" if a[6] == b[6] else "  字体[%s]→[%s]" % (a[6][:28], b[6][:28])))
        if bad > 14:
            print("  …（截断）"); break
    print("  差异行数：%d" % bad)
    o.close(); n.close()
