# -*- coding: utf-8 -*-
# 试验乙-义6-1 (v3): 答案册装配副本＝甲乙丙并单 multicols（节标入栏，照甲段与 M2【甲】结构）＋丁维持 \clearpage 独立起页
# 试验层（原件零改动）。判据＝五0＋页数＋逐页页脚。失败回退＝维持三处 \clearpage（现行 6 页零溢态），留白定性分本界自然态登记。
import io, sys, os, re, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader

SRC = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\答案册"
DST = r"C:\提示词\工作区\_tmpP1装配0912\_试验-义6-1丙丁并栏"
SKIP = re.compile(r"^(png|__pycache__)$|\.aux$|\.log$|\.out$|\.py$|\.pdf$|\.md$|\.json$")

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

def cut(t, marker_end, marker_next, note):
    """撤 marker_end..marker_next 区间的 甲段尾\end{multicols}、\clearpage、后节 \begin{multicols} 三件套头（jietitle 留栏内）"""
    i2 = t.index(marker_end)
    i3 = t.index(marker_next)
    seg = t[i2:i3]
    o = seg
    seg, n1 = re.subn(r"\\end\{multicols\}", "%装配轮义6-1并栏：" + note + "——原 end-multicols 撤除（下节续栏）", seg, count=1)
    seg, n2 = re.subn(r"^\\clearpage   % 分本切页.*$", "%装配轮义6-1并栏：本界 clearpage 撤除（栏流接续）", seg, count=1, flags=re.M)
    seg, n3 = re.subn(r"\\begin\{multicols\}\{2\}\n\\raggedcolumns\n\\emergencystretch=1em\n",
                      "%装配轮义6-1并栏：本节独立 multicols 环境撤除（续上栏；节标入栏）\n", seg, count=1)
    assert n1 == 1 and n2 == 1 and n3 == 1, (marker_end, n1, n2, n3)
    return t[:i2] + seg + t[i3:]

assert "\\setcounter{page}{1}" in t
t = t.replace("\\setcounter{page}{1}", "\\setcounter{page}{44}", 1)
t = cut(t, "【甲】导学件答案", "【乙】练习件答案", "甲尾")
t = cut(t, "【乙】练习件答案", "【丙】拓展册答案", "乙尾")
# 丙→丁 界保持原样（丙尾 \end{multicols}＋\clearpage＋丁 jietitle＋丁 multicols）
open(bp, "w", encoding="utf-8").write(t)
for _ in range(2):
    subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"], cwd=DST, capture_output=True)
log = open(os.path.join(DST, "main.log"), encoding="utf-8", errors="ignore").read()
err = len(re.findall(r"^! ", log, re.M))
ovr = log.count("Overfull")
und = log.count("Underfull")
mch = log.count("Missing character")
qpf = len(re.findall(r"QP-FIGS", log))
pg = len(PdfReader(os.path.join(DST, "main.pdf")).pages)
print(f"甲乙丙并栏·丁独立：err={err} Overfull={ovr} Underfull={und} MissChar={mch} QPFIGS={qpf} 页数={pg}")
for m in re.finditer(r"Overfull \\vbox \(([\d.]+)pt", log):
    print("  vbox溢", m.group(1))
