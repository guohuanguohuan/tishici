# -*- coding: utf-8 -*-
"""_seat歧位定位.py — 三册 seat 序红：逐位 diff＋ntext 上下文。"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T, pieces_of
from 复核成册门S5 import fold2, BOOKLETS
from 汇编答案册S5 import parse_raw
import fitz

seat_re = re.compile(
    r'(?<![0-9A-Za-z\-])([0-9A-Za-z]{1,4}(?:-[0-9A-Za-z]{1,4})*)\.\[答案\]')
for outname, jxs, _ in BOOKLETS:
    out = os.path.join(HERE, outname)
    seats = [b['seat'] for jx in jxs for _p, pd in pieces_of(jx)
             for b in parse_raw(pd)]
    doc = fitz.open(os.path.join(out, 'ansbook-true.pdf'))
    nt = fold2('\n'.join(p.get_text() for p in doc))
    doc.close()
    got = seat_re.findall(nt)
    n = min(len(got), len(seats))
    diffs = [i for i in range(n) if got[i] != seats[i]]
    print('==', outname, 'got', len(got), 'exp', len(seats), '歧位数(前段)', len(diffs))
    for i in diffs[:3]:
        pos = nt.find('[答案]')
        p = 0
        for _ in range(i + 1):
            p = nt.find('[答案]', p) + 1
        print('  @%d got[%s] exp[%s] 上下文: %s' %
              (i, got[i], seats[i], nt[max(0, p - 45):p + 12]))
    if len(got) != len(seats):
        print('  枚数不等：尾段 got%s exp%s' % (got[-3:], seats[-3:]))
