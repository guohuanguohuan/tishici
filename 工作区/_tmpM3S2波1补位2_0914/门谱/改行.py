# -*- coding: utf-8 -*-
"""改行.py — 按行号精确改 tex 一行（母版体例§四.2：python 落盘脚本执行，反斜杠 chr(92) 拼）。
用法: python 改行.py <tex路径> <行号1基> <旧整行> <新整行>   （旧整行须与该行内容逐字一致，否则中止）
"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path, n = sys.argv[1], int(sys.argv[2])
old, new = sys.argv[3], sys.argv[4]
CR, LF = chr(13), chr(10)
raw = open(path, encoding='utf-8', newline='').read()
lines = raw.split(LF)
cur = lines[n - 1].rstrip(CR)
if cur != old:
    print('MISMATCH 中止')
    print('期望:', repr(old))
    print('实际:', repr(cur))
    sys.exit(2)
lines[n - 1] = new + (CR if lines[n - 1].endswith(CR) else '')
open(path, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print(f'第 {n} 行已改：{old} → {new}')
