# -*- coding: utf-8 -*-
"""批6章末件二轮微调：①ASCII 引号→CJK 弯引号；②块尾留白 13mm→6mm（块间留白不动）。"""
import io, re
p = r'C:\提示词\工作区\M2-第1章量产0911\成卷\导学件\章末-本章总结提升\main.tex'
s = io.open(p, encoding='utf-8').read()

pairs = [
    ('"系数和＝1"', '\u201c系数和＝1\u201d'),
    ('"关于谁不变谁、其余变号"', '\u201c关于谁不变谁、其余变号\u201d'),
    ('"向量化"', '\u201c向量化\u201d'),
    ('"设→表→算→判"', '\u201c设→表→算→判\u201d'),
]
for a, b in pairs:
    assert a in s, a
    s = s.replace(a, b)

# 块尾 zhankong＝其后仅跨空行与 % 注释行即遇 vbox 闭合 }
pat = re.compile(r'\\zhankong\{13mm\}(?=(?:[ \t]*\n[ \t]*(?:%[^\n]*)?)*[ \t]*\})')
hits = len(pat.findall(s))
assert hits == 12, hits
s = pat.sub(r'\\zhankong{6mm}', s)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('quotes fixed; trailing zhankong reduced:', hits)
