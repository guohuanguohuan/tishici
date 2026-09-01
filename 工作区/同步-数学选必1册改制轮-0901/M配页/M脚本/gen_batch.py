# -*- coding: utf-8 -*-
"""由S盖章parts.json生成节页码定位TSV配置（仅六讲练件；反斜杠路径；start留空→--record补齐）。"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = r'C:/提示词/工作区/同步-数学选必1册改制轮-0901/S盖章/parts.json'
d = json.load(open(src, encoding='utf-8'))
rows = []
for part in d['parts']:
    for f in part['files']:
        if '讲练件' in f:
            rows.append(f.replace('/', '\\'))
out = 'mulu_batch.tsv'
with open(out, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('# M配页 节页码定位配置（六讲练件；start列空→由S盖章记录补齐）\n')
    for r in rows:
        fh.write(r + '\t-\t\n')
print(open(out, encoding='utf-8').read())
