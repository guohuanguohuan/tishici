# -*- coding: utf-8 -*-
"""片D 定位辅助v3：按 no 字段打印 61..79。"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r'C:\提示词\工作区\M2-第1章量产0911'
d = json.load(open(BASE + r'\_tmp结构-讲下.json', encoding='utf-8'))
qs = d['questions']
for q in qs:
    if 55 <= q['no'] <= 79:
        print(q['no'], 'start=', q['start'], 'end=', q['end'], 'diff=', q['diff'], 'sec=', q['sec'])
