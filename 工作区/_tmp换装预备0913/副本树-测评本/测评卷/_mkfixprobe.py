# -*- coding: utf-8 -*-
"""修因探针：给对照件补回六宏的全局 \extrarowheight=1.7mm（qp-m3 未复刻），
   验证「换装本身」在测评卷 p3 答案速查表处的 0.36% 像素差是否由此一条造成。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = "main-ctl.tex"
s = open(p, encoding="utf-8").read()
anchor = chr(92) + "ansblockgrayfalse"
assert anchor in s, "anchor missing"
add = ("\n%% 修因探针：六宏 qp-layout.tex:130 全局 extrarowheight=1.7mm，qp-m3 未复刻"
       "\n" + chr(92) + "setlength{" + chr(92) + "extrarowheight}{1.7mm}")
out = s.replace(anchor, anchor + add, 1)
open("main-ctl-fixprobe.tex", "w", encoding="utf-8").write(out)
print("written; 探针行已插入")
