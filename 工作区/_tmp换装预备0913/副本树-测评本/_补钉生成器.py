# -*- coding: utf-8 -*-
r"""给三件生成「补钉版」：件面末位补 qp-m3 未复刻的两条（\extrarowheight / \parallel 再注册）。

两条补钉的出处与必要性（本轮实测定位，详见试迁报告）：
  1) \setlength{\extrarowheight}{1.7mm}
     六宏 qp-layout.tex:130 全局设 1.7mm；qp-m3 只复刻了 \arrayrulewidth / \tabcolsep /
     \arraystretch，未复刻 \extrarowheight → 件面自带 tabular（卷末答案速查表）行高回落。
     实测：测评卷 p3、滚A p2、滚B p2 三处速查表像素差 0.28–0.36%，补回后归 0。
  2) \AtBeginDocument{\renewcommand{\parallel}{…TikZ 复刻…}}
     qp-m3.sty:105 已注册同一条，但被 unicode-math 后手覆盖（实测 \meaning\parallel
     = "the character ∥"），六宏世界同一注册却生效 → 件面凡用 \parallel 处符号变体。
     实测：滚A p1 差 0.0743%（5 处 ∥ 的 10 个矢量笔画框 → 0 个），补回后归 0。
"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)
PATCH = ("% ---- 补钉（qp-m3 未复刻/被覆盖两条；出处见 _补钉生成器.py 注释） ----\n"
         + BS + "setlength{" + BS + "extrarowheight}{1.7mm}\n"
         + BS + "AtBeginDocument{" + BS + "renewcommand{" + BS + "parallel}{" + BS + "mathrel{"
         + BS + "begin{tikzpicture}[x=1em,y=1em,baseline={(0,0)}]\n"
         + "  " + BS + "fill (-0.412,-0.016) -- (-0.375,-0.016) -- (0.114,0.956) -- (0.077,0.956) -- cycle;\n"
         + "  " + BS + "fill (-0.115,-0.016) -- (-0.078,-0.016) -- (0.411,0.956) -- (0.374,0.956) -- cycle;\n"
         + BS + "end{tikzpicture}}}}\n").replace("% ----", "% " + "-" * 4)

for label in ("测评卷", "滚动卷A", "滚动卷B"):
    for src, dst in (("main.tex", "main-fix.tex"), ("main-pure.tex", "main-pure-fix.tex")):
        s = open(os.path.join(HERE, label, src), encoding="utf-8").read()
        i = s.index(BS + "begin{document}")
        open(os.path.join(HERE, label, dst), "w", encoding="utf-8").write(s[:i] + PATCH + s[i:])
        print("生成 %s/%s" % (label, dst))
