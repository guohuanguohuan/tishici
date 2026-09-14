# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S2 波1臂2（课时04/05/06）·回流门（零强制跳页）＋CJK 审计。
母版件＝工作区/_tmpM3S2母版0914/门谱/门-回流.py，逻辑零改动；并入 CJK catcode 审计
（体例说明§四.1「全文审计器 命中 0 才放行，回流门可并入」）。
断言面：main.tex 剔注释后，强制版面原子零出现：
  \newpage \clearpage \pagebreak \vbox \vtop \ketangboxed \columnbreak \eject
审计面（登记，命中 0 判绿）：rg 制式 \\[a-zA-Z]+\p{Han} ＝控制词直连 CJK。
用法: python 门-回流.py <件04|05|06>     退出码: 0＝全过；1＝有红。
"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
PIECES = {
    '04': '课时04-点斜式与斜截式',
    '05': '课时05-两点式与一般式',
    '06': '课时06-两条直线的位置关系',
}
tag = sys.argv[1] if len(sys.argv) > 1 else '04'
PIECE = f'{ROOT}/成卷/导学件/{PIECES[tag]}'
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
for w in BAD:
    n = body.count(w)
    t = '绿' if n == 0 else '红'
    print(f'  [{t}] {w} ×{n}')
    if n:
        reds.append(w)

RE_HAN = re.compile(r'\\[a-zA-Z]+[\u4e00-\u9fff\u3400-\u4dbf]')
hits = [(i + 1, l) for i, l in enumerate(src.split('\n')) if RE_HAN.search(l)]
print(f'  [{"绿" if not hits else "红"}] CJK 审计 \\控制词+汉字 命中 {len(hits)}')
for i, l in hits:
    print(f'      L{i}: {l[:90]}')
    reds.append(f'CJK@L{i}')
print()
print('回流门：', '全绿（零强制跳页）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
