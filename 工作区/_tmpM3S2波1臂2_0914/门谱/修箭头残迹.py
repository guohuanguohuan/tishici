# -*- coding: utf-8 -*-
"""修箭头残迹.py — 母版体例§四.2 口径：python 处理落盘脚本执行、反斜杠用 chr(92) 拼。
修 05 main.tex 中 bash-heredoc 事故产物：`\(` + CR + `ightarrow\)` → `\(` + BS + `rightarrow\)`。
只改这一处模式，其余字节原样回写（CRLF 保持）。
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR = chr(92), chr(13)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
s = open(P, encoding='utf-8', newline='').read()
bad = BS + '(' + CR + 'ightarrow' + BS + ')'
good = BS + '(' + BS + 'rightarrow' + BS + ')'
n = s.count(bad)
s = s.replace(bad, good)
open(P, 'w', encoding='utf-8', newline='').write(s)
d = open(P, encoding='utf-8', newline='').read()
print('修复处数:', n, '｜残留残迹:', d.count(bad), '｜正常 \\(rightarrow\\):', d.count(good))
print('CR 总数（应＝行数 401，纯 CRLF）:', d.count(CR), '｜LF 总数:', d.count(chr(10)))
