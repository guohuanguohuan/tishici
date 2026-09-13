# -*- coding: utf-8 -*-
"""opt4up2up.py — M3 S2 波1 补位臂3·课时15 选项行 4-up→2-up 改制（槽宽门零旗改制件）。
14 片全 2-up 制（0.5\\linewidth-1em）为家法基线；15 的 8 条 4-up（0.25\\linewidth-0.5em）
行中 5 条触 strict 线、1 条（L406 B/D）连零误报档容差也超＝真静默溢出险。
改制只动题面装配层选项行排布，题面文字/答案字节零改动。
用法: python opt4up2up.py   （无参；源/目标＝课时15 main.tex；备份先落本目录）
"""
import io
import os
import re
import shutil
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时15-2.7.1抛物线方程'
TEX = os.path.join(PIECE, 'main.tex')
BAK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main-课时15-改前备份.tex')

HEAD = re.compile(r'^\\bindopt \{(\\fontsize\{10\.5pt\}\{(\\qpTJgLead(?:Liti|Pingjia))\}\\selectfont )')
MK = '\\makebox[\\dimexpr0.25\\linewidth-0.5em\\relax][l]{'
MK2 = '\\makebox[\\dimexpr0.5\\linewidth-1em\\relax][l]{'
TAIL = '\\par}'


def scan_body(s, i):
    """s[i]=='{' → 平衡花括号取体，返回 (body, 关闭括号后位置)。"""
    assert s[i] == '{'
    d, j = 0, i
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
            continue
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError('花括号不配平')


lines = open(TEX, encoding='utf-8').read().split('\n')
out, hit = [], 0
for ln in lines:
    m = HEAD.match(ln)
    if not m or MK not in ln:
        out.append(ln)
        continue
    rest = ln[m.end():]
    bodies = []
    ok = True
    for _ in range(4):
        if not rest.startswith(MK):
            ok = False
            break
        body, pos = scan_body(rest, len(MK) - 1)
        bodies.append(body)
        rest = rest[pos:]
    if not ok or rest != TAIL or len(bodies) != 4:
        out.append(ln)
        continue
    lead = m.group(1)
    half = lambda a, b: '\\bindopt {' + lead + MK2 + a + '}' + MK2 + b + '}' + TAIL
    out.append(half(bodies[0], bodies[1]))
    out.append(half(bodies[2], bodies[3]))
    hit += 1

if hit != 8:
    print(f'[ABORT] 改制行数 {hit} ≠ 8，零写回')
    sys.exit(1)

shutil.copyfile(TEX, BAK)
open(TEX, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print(f'[OK] 4-up→2-up 改制 {hit} 行（8→16 行）；备份→{BAK}')
