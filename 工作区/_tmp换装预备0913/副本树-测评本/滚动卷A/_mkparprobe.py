# -*- coding: utf-8 -*-
r"""生成 滚A 对照件的 `\parallel` 修因探针：件面末位再注册一次 qp-m3 的 TikZ 复刻。

背景：qp-m3.sty:105 用 \AtBeginDocument 注册 \parallel 的 TikZ 复刻，但实测换装后
      \meaning\parallel = "the character ∥"（unicode-math 的数学字符），即注册被后手覆盖；
      六宏世界同一位置注册却生效（原印面 p1 有 10 个 5.5×10.2pt 矢量笔画框，换装后 0 个）。
本探针在件面（所有包之后）再注册一次，验证「件面补一行」能否复原 ∥ 真迹与版面。
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BS = chr(92)
RENEW = (BS + "AtBeginDocument{" + BS + "renewcommand{" + BS + "parallel}{" + BS + "mathrel{"
         + BS + "begin{tikzpicture}[x=1em,y=1em,baseline={(0,0)}]\n"
         + "  " + BS + "fill (-0.412,-0.016) -- (-0.375,-0.016) -- (0.114,0.956) -- (0.077,0.956) -- cycle;\n"
         + "  " + BS + "fill (-0.115,-0.016) -- (-0.078,-0.016) -- (0.411,0.956) -- (0.374,0.956) -- cycle;\n"
         + BS + "end{tikzpicture}}}}\n")

p = "main-ctl-fixprobe.tex"
s = open(p, encoding="utf-8").read()
i = s.index(BS + "begin{document}")
out = s[:i] + "% —— 修因探针2：件面末位再注册 \\parallel 的 TikZ 复刻（qp-m3:105 的注册被 unicode-math 覆盖）\n" + RENEW + s[i:]
open("main-ctl-parprobe.tex", "w", encoding="utf-8").write(out)
print("written main-ctl-parprobe.tex")
