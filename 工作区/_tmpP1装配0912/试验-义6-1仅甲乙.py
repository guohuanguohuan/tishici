# -*- coding: utf-8 -*-
# 试验丙-义6-1：仅撤 甲→乙 分本 \clearpage（P2 留白位点精准处置），乙→丙/丙→丁 界不动
import io, sys, os, re, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader
SRC = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\答案册"
DST = r"C:\提示词\工作区\_tmpP1装配0912\_试验-义6-1仅甲乙"
SKIP = re.compile(r"^(png|__pycache__)$|\.aux$|\.log$|\.out$|\.py$|\.pdf$|\.md$|\.json$")
if os.path.exists(DST):
    shutil.rmtree(DST)
os.makedirs(DST)
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in ("png", "__pycache__")]
    rel = os.path.relpath(root, SRC)
    tgt = DST if rel == "." else os.path.join(DST, rel)
    os.makedirs(tgt, exist_ok=True)
    for f in files:
        if not SKIP.search(f):
            shutil.copy2(os.path.join(root, f), os.path.join(tgt, f))
bp = os.path.join(DST, "body.tex")
t = open(bp, encoding="utf-8").read()
t = t.replace("\\setcounter{page}{1}", "\\setcounter{page}{44}", 1)
t, n = re.subn(r"^\\clearpage   % 分本切页：甲→乙.*$",
               "%装配轮义6-1：甲→乙 clearpage 撤除（P2 留白位点·栏流接续）", t, count=1, flags=re.M)
assert n == 1
open(bp, "w", encoding="utf-8").write(t)
for _ in range(2):
    subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"], cwd=DST, capture_output=True)
log = open(os.path.join(DST, "main.log"), encoding="utf-8", errors="ignore").read()
print("err=%d Overfull=%d Underfull=%d MissChar=%d QPFIGS=%d 页数=%d" % (
    len(re.findall(r"^! ", log, re.M)), log.count("Overfull"), log.count("Underfull"),
    log.count("Missing character"), len(re.findall(r"QP-FIGS", log)),
    len(PdfReader(os.path.join(DST, "main.pdf")).pages)))
import pymupdf
d = pymupdf.open(os.path.join(DST, "main.pdf"))
for i, pg in enumerate(d):
    H = pg.rect.height
    foot = H - 52
    blocks = [b for b in pg.get_text("blocks") if b[4].strip() and b[1] < foot - 4]
    ymax = max((b[3] for b in blocks if b[3] < foot + 6), default=0)
    print(f"P{i+1} 内容底y={ymax:.0f} 充实度≈{max(0,(ymax-24)/(764-24))*100:.0f}% | 首行: {(blocks[0][4].strip().splitlines()[0][:30] if blocks else '')}")
d.close()
