# -*- coding: utf-8 -*-
"""B2 保底位试验：把 :105 钩块移到 :117 \\setmathfont 之后（仍用 \\AtBeginDocument）。"""
import io, os, shutil, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

BLOCK = r"""\AtBeginDocument{\renewcommand{\parallel}{\mathrel{\begin{tikzpicture}[x=1em,y=1em,baseline={(0,0)}]
  \fill (-0.412,-0.016) -- (-0.375,-0.016) -- (0.114,0.956) -- (0.077,0.956) -- cycle;
  \fill (-0.115,-0.016) -- (-0.078,-0.016) -- (0.411,0.956) -- (0.374,0.956) -- cycle;
\end{tikzpicture}}}}"""

ANCHOR = r"""\setmathfont{texgyretermes-math.otf}[Scale=1.02]"""

os.makedirs(os.path.join(HERE, "mech2"), exist_ok=True)
s = open(os.path.join(HERE, "qp-m3-orig.sty"), encoding="utf-8").read()
assert s.count(BLOCK) == 1 and s.count(ANCHOR) == 1
s = s.replace(BLOCK, "% [B2 试验] 原位钩块已移至 setmathfont 之后")
s = s.replace(ANCHOR, ANCHOR + "\n% [B2 试验] 钩块新位（仍 AtBeginDocument，注册序在 unicode-math 之后）：\n" + BLOCK)
shutil.copy(os.path.join(HERE, "p-stages.tex"), os.path.join(HERE, "mech2", "p-stages.tex"))
open(os.path.join(HERE, "mech2", "qp-m3.sty"), "w", encoding="utf-8").write(s)
print("mech2 ready")
