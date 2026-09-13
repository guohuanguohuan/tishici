# -*- coding: utf-8 -*-
r"""两钉负测门：复现旧病→补丁病愈的证据脚本（全部最小探针件，不涉正装编译）。
面谱（负测/ 下，每面一个最小探针）：
  orig/p-stages   旧病复现①②：BEGINDOCEND 仍 ∥、EH=0.0pt
  mech/p-stages   机理钉：:105 钩确有执行（HOOK105-POST=TikZ）但随后被覆盖（BEGINDOCEND=∥）
  mech2/p-stages  负结果档：钩块移到 setmathfont 之后（仍包标签）不救（BEGINDOCEND=∥）
  patch/p-stages  病愈档：补丁稿（begindocument/end＋extrarowheight）全绿
  six/p-stages-six 对照档：六宏世界 top-level 标签殿后存活（LATE=TikZ、EH=4.84pt）
  orig/p-eh vs patch/p-eh   钉①量化：EH 0→4.83694pt（=1.7mm）、表盒高 +5.08pt（=1.05×E，与试迁
                            实测速查表首行 −5.1pt 位移同量）
  orig/p-linewidth vs patch/p-linewidth  钉③量化：ansblock 内 \linewidth 1086.9pt（382mm 跨三栏）
                            → 341.4pt（=120mm 栏宽）；vtop 外 \linewidth 不受扰
"""
import io, os, re, subprocess, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
XELATEX = r"C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex"
FAILS = []

def run(face, tex):
    subprocess.run([XELATEX, "-interaction=nonstopmode", tex], cwd=os.path.join(HERE, face),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    log = open(os.path.join(HERE, face, tex.replace(".tex", ".log")), encoding="utf-8", errors="replace").read()
    return log

def check(name, ok, detail):
    print("[%s] %s ｜ %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        FAILS.append(name)

def val(log, key):
    m = re.search(re.escape(key) + r"[^\n]*", log)
    return m.group(0) if m else "(缺)"

TIKZ = r"macro:->\mathrel {\begin {tikzpicture}"

# ① \parallel 三态 + ② extrarowheight
log = run("orig", "p-stages.tex")
check("旧病复现/orig：begindocument 段后 ∥ 残留", "STAGE-BEGINDOCEND: the character ∥" in log, val(log, "STAGE-BEGINDOCEND")[:60])
check("旧病复现/orig：EH=0.0pt（速查表行高回落根因）", "EH=0.0pt" in log, val(log, "STAGE-BODY"))
log = run("mech", "p-stages.tex")
check("机理/mech：:105 钩确有执行且 renew 成功", "HOOK105-POST: " + TIKZ in log, val(log, "HOOK105-POST")[:40])
check("机理/mech：钩后仍被覆盖（覆盖块在包标签序后段）", "STAGE-BEGINDOCEND: the character ∥" in log, val(log, "STAGE-BEGINDOCEND")[:60])
log = run("mech2", "p-stages.tex")
check("负结果/mech2：sty 内移位（仍 qp-m3 标签）不救", "STAGE-BEGINDOCEND: the character ∥" in log, val(log, "STAGE-BEGINDOCEND")[:60])
log = run("patch", "p-stages.tex")
check("病愈/patch：begindocument/end 段 TikZ 复位", "STAGE-BEGINDOCEND: " + TIKZ in log, val(log, "STAGE-BEGINDOCEND")[:40])
check("病愈/patch：文档体 TikZ 保持", "STAGE-BODY: " + TIKZ in log, val(log, "STAGE-BODY")[:40])
check("病愈/patch：EH=4.83694pt（=1.7mm）", "EH=4.83694pt" in log, val(log, "STAGE-BODY"))
log = run("six", "p-stages-six.tex")
check("对照/six：六宏世界 LATE 段 TikZ 存活", "STAGE-BEGINDOC-LATE: " + TIKZ in log, val(log, "STAGE-BEGINDOC-LATE")[:40])

# ① 量化：表盒高差
lo = run("orig", "p-eh.tex"); pa = run("patch", "p-eh.tex")
h1 = float(re.search(r"TAB-HT: ([0-9.]+)pt", lo).group(1))
h2 = float(re.search(r"TAB-HT: ([0-9.]+)pt", pa).group(1))
check("量化/钉①：补丁后表盒高 +5.08pt（=1.05×1.7mm，对齐试迁 −5.1pt 实测）",
      5.0 < h2 - h1 < 5.2, "orig %.5fpt → patch %.5fpt（Δ=%.5fpt）" % (h1, h2, h2 - h1))

# ③ linewidth
lo = run("orig", "p-linewidth.tex"); pa = run("patch", "p-linewidth.tex")
w1 = float(re.search(r"LW-IN-BLOCK: ([0-9.]+)pt", lo).group(1))
w2 = float(re.search(r"LW-IN-BLOCK: ([0-9.]+)pt", pa).group(1))
wo = float(re.search(r"LW-OUTSIDE: ([0-9.]+)pt", pa).group(1))
check("旧病复现/钉③：无补钉 ansblock 取页宽 >1000pt（跨三栏）", w1 > 1000, "%.2fpt" % w1)
check(r"病愈/钉③：补 \linewidth=\jpcolw 后 ansblock 取 120mm 栏宽", abs(w2 - 341.43306) < 0.01, "%.5fpt（=120.0mm）" % w2)
check(r"病愈/钉③：vtop 外 \linewidth 不受扰（仍页宽）", abs(wo - w1) < 0.01, "OUTSIDE %.2fpt" % wo)

print("-" * 56)
print("负测门：%s（%d FAIL）" % ("全过" if not FAILS else "有挂红", len(FAILS)))
sys.exit(1 if FAILS else 0)
