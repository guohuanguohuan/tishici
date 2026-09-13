# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S2 波1 臂6 课时10·回流门（零强制跳页）＋CJK 审计。
参数化自 母版 门谱，常量换片：PIECE。
断言面：
  ①main.tex 剔注释后，以下强制版面原子零出现：
    \newpage \clearpage \pagebreak \vbox \vtop \ketangboxed \columnbreak \eject
    （\vbox 系 M2「右栏全空」病灶根因；规格书 v2 §四.二.10② 撤强制跳页。）
  ②CJK 审计：控制词紧贴汉字（`\word`后无空格直连 CJK，防 catcode=11 控制词被吸入
    csname 的三坑病灶）零命中。
用法: python 门-回流.py     退出码: 0＝全过；1＝有红。
"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时10-2.4曲线与方程'
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
for w in BAD:
    n = body.count(w)
    tag = '绿' if n == 0 else '红'
    print(f'  [{tag}] {w} ×{n}')
    if n:
        reds.append(w)

# CJK 审计：\控制词与汉字**零间隔直连**（`\quad平` 式 catcode=11 吸并 csname 病灶）→ 命中即红。
#   宏名后带空格（`\quad 平`）＝空格收束控制词名，合法排版，不旗；带参宏 `{` 起参亦天然排除。
hits = []
for m in re.finditer(r'\\[a-zA-Z]+(?=[\u4e00-\u9fff])', body):
    hits.append(f'{m.group(0)}@{body.count(chr(10), 0, m.start()) + 1}')
tag = '绿' if not hits else '红'
print(f'  [{tag}] CJK审计（\\控制词紧贴汉字）×{len(hits)}' + (f'｜{hits[:8]}' if hits else ''))
if hits:
    reds.append('CJK审计')

print()
print('回流门：', '全绿（零强制跳页＋CJK审计零命中）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
