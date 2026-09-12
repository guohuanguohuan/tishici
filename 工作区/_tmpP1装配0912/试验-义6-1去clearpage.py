# -*- coding: utf-8 -*-
# 装配轮·试验甲：答案册分本切页留白（义6-1）——副本去 \clearpage 试编译定页流
# 口径：装配副本层处置（原件 body.tex 不动）；判据＝五0＋页数读数；若 Overfull 复发→回退维持 \clearpage
import io, sys, os, re, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader

SRC = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\答案册"
DST = r"C:\提示词\工作区\_tmpP1装配0912\_试验-义6-1"
SKIP = re.compile(r"^(png|__pycache__|figs)$|\.aux$|\.log$|\.out$|\.py$|\.pdf$|\.md$|\.json$")

def copy(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ("png", "__pycache__")]
        rel = os.path.relpath(root, src)
        tgt = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(tgt, exist_ok=True)
        for f in files:
            if SKIP.search(f):
                continue
            shutil.copy2(os.path.join(root, f), os.path.join(tgt, f))

copy(SRC, DST)
bp = os.path.join(DST, "body.tex")
t = open(bp, encoding="utf-8").read()
t2 = t.replace("\\setcounter{page}{1}", "\\setcounter{page}{44}", 1)
n = len(re.findall(r"^\\clearpage   % 分本切页", t2, re.M))
t3 = re.sub(r"^\\clearpage   % 分本切页.*$", "%装配轮义6-1：分本切页 clearpage 撤除（起新页→自然流页）", t2, flags=re.M)
assert n == 3 and t3 != t2
open(bp, "w", encoding="utf-8").write(t3)
for _ in range(2):
    subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"], cwd=DST, capture_output=True)
log = open(os.path.join(DST, "main.log"), encoding="utf-8", errors="ignore").read()
err = len(re.findall(r"^! ", log, re.M))
ovr = log.count("Overfull")
und = log.count("Underfull")
mch = log.count("Missing character")
qpf = len(re.findall(r"QP-FIGS", log))
pg = len(PdfReader(os.path.join(DST, "main.pdf")).pages)
print(f"去clearpage 试验：err={err} Overfull={ovr} Underfull={und} MissChar={mch} QPFIGS={qpf} 页数={pg}")
for m in re.finditer(r"Overfull \\vbox \(([\d.]+)pt", log):
    print("  vbox溢", m.group(1))
for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt", log):
    print("  hbox溢", m.group(1))
