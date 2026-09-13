# -*- coding: utf-8 -*-
"""机制探针注桩：给 mech/qp-m3.sty 的 :105 钩体插 PRE/POST 读数＋分发探针件。"""
import io, os, shutil, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

OLD = r"""\AtBeginDocument{\renewcommand{\parallel}{\mathrel{\begin{tikzpicture}[x=1em,y=1em,baseline={(0,0)}]
  \fill (-0.412,-0.016) -- (-0.375,-0.016) -- (0.114,0.956) -- (0.077,0.956) -- cycle;
  \fill (-0.115,-0.016) -- (-0.078,-0.016) -- (0.411,0.956) -- (0.374,0.956) -- cycle;
\end{tikzpicture}}}}"""

NEW = r"""\AtBeginDocument{\typeout{HOOK105-PRE: \meaning\parallel}%
\renewcommand{\parallel}{\mathrel{\begin{tikzpicture}[x=1em,y=1em,baseline={(0,0)}]
  \fill (-0.412,-0.016) -- (-0.375,-0.016) -- (0.114,0.956) -- (0.077,0.956) -- cycle;
  \fill (-0.115,-0.016) -- (-0.078,-0.016) -- (0.411,0.956) -- (0.374,0.956) -- cycle;
\end{tikzpicture}}}%
  \typeout{HOOK105-POST: \meaning\parallel}}"""

p = os.path.join(HERE, "mech", "qp-m3.sty")
s = open(p, encoding="utf-8").read()
assert s.count(OLD) == 1, "hook block not found exactly once: %d" % s.count(OLD)
open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW))
print("mech sty instrumented")

for d in ("orig", "mech", "patch"):
    shutil.copy(os.path.join(HERE, "p-stages.tex"), os.path.join(HERE, d, "p-stages.tex"))
for d in ("orig", "patch"):
    shutil.copy(os.path.join(HERE, "p-eh.tex"), os.path.join(HERE, d, "p-eh.tex"))
shutil.copy(os.path.join(HERE, "p-linewidth-bad.tex"), os.path.join(HERE, "orig", "p-linewidth.tex"))
shutil.copy(os.path.join(HERE, "p-linewidth-good.tex"), os.path.join(HERE, "patch", "p-linewidth.tex"))
print("probes distributed")
