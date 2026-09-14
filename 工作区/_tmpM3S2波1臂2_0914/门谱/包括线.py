# -*- coding: utf-8 -*-
"""包括线.py — 按 门-值快照键型判模 的估高读数，把指定键的 ansblock 包成括线模
（`{\\ansblockgrayfalse` … `\\end{ansblock}}`）。母版体例§四.2 口径：python 处理落盘脚本执行，
反斜杠一律 chr(92) 拼，禁 bash heredoc 直写 tex。幂等：已包的不重复包。
用法: python 包括线.py <件目录名> <键短名…>   （键短名＝E3/T6 之类，自动补全为全键）
"""
import io
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件'
BS = chr(92)
piece, shorts = sys.argv[1], sys.argv[2:]
P = os.path.join(ROOT, piece, 'main.tex')
lines = open(P, encoding='utf-8', newline='').read().split(chr(10))

# 全键名解析：按短名匹配 \begin{ansblock}[…-KEY]
keys = {}
for ln in lines:
    i = ln.find(BS + 'begin{ansblock}[')
    if i >= 0:
        k = ln[i + len(BS + 'begin{ansblock}['):ln.find(']', i)]
        keys[k.rsplit('-', 1)[-1]] = k
want = []
for s in shorts:
    assert s in keys, f'键短名不存在：{s}（可选：{sorted(keys)}）'
    want.append(keys[s])

opened, closed, skip = 0, 0, 0
out = []
cur = None
for idx, ln in enumerate(lines):
    i = ln.find(BS + 'begin{ansblock}[')
    if i >= 0:
        k = ln[i + len(BS + 'begin{ansblock}['):ln.find(']', i)]
        if k in want:
            prev = out[-1].rstrip(chr(13)) if out else ''
            if 'ansblockgrayfalse' not in prev:
                out.append('{' + BS + 'ansblockgrayfalse')
                opened += 1
            else:
                skip += 1
            cur = k
        else:
            cur = None
    if cur and ln.strip() == BS + 'end{ansblock}':
        out.append(ln.replace(BS + 'end{ansblock}', BS + 'end{ansblock}' + '}'))
        closed += 1
        cur = None
        continue
    out.append(ln)

open(P, 'w', encoding='utf-8', newline='').write(chr(10).join(out))
print(f'新包 {opened} 处｜已在括线模 {skip} 处｜闭合 {closed} 处')
print('键：', '、'.join(k.rsplit("-", 1)[-1] for k in want))
