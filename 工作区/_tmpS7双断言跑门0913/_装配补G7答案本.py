# -*- coding: utf-8 -*-
r"""S7 装配刷新补步（成卷/装配记录.md §一.3／§六「双轨各自重编」口径的机器化）——
装配四本.py 复跑后，答案册装配副本的第二重置位 body.tex:6「独立册起页 1」须按 G7 双轨归口
改写 90（该行注释自留改写位；原件 成卷/答案册/body.tex 不动），副本重编 ×2 后重并 答案本.pdf。
只写 成卷/装配/答案本/ 副本与 答案本.pdf＝快照刷新，非内容改。"""
import io, sys, os, re, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader, PdfWriter

CP = r"C:\提示词\工作区\M2-第1章量产0911\成卷\装配\答案本\答案册"
OUT = r"C:\提示词\工作区\M2-第1章量产0911\成卷\装配\答案本.pdf"

bp = os.path.join(CP, "body.tex")
t = open(bp, encoding="utf-8").read()
repl = ("\\setcounter{page}{90}  % 装配轮G7跨本连续页码（方案B）改写：原独立册起页 1"
        "（G12 双轨归口：独立起页原件保留于 成卷/答案册/ 不动）")
new, n = re.subn(r"\\setcounter\{page\}\{1\}(\s*%[^\n]*)?", lambda m: repl, t, count=1)
assert n == 1, "body.tex:6 重置位未找到"
open(bp, "w", encoding="utf-8").write(new)
print("body.tex:6 →90 改写完成（副本）")

for i in (1, 2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"], cwd=CP, capture_output=True)
    print(f"xelatex#{i} rc={r.returncode}")
log = open(os.path.join(CP, "main.log"), encoding="utf-8", errors="ignore").read()
err = len(re.findall(r"^! ", log, re.M))
ovr = log.count("Overfull")
mch = log.count("Missing character")
npg = len(PdfReader(os.path.join(CP, "main.pdf")).pages)
print(f"副本三0：err={err} ovr={ovr} mch={mch} 页数={npg}")
assert err == ovr == mch == 0 and npg == 13

w = PdfWriter()
r = PdfReader(os.path.join(CP, "main.pdf"))
w.append(r)
w.add_outline_item("参考答案册（导学·练习·拓展·测评全含）", 0)
with open(OUT, "wb") as fh:
    w.write(fh)
print("答案本.pdf 重并完成（13 页，书签1条）")
