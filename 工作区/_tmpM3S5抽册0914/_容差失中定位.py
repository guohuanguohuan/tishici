# -*- coding: utf-8 -*-
"""_容差失中定位.py — 容差层首个失中位上下文。"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, pieces_of
from 复核成册门S5 import fold2, BOOKLETS
from 汇编答案册S5 import parse_raw
import fitz

for outname, jxs, _ in BOOKLETS:
    out = os.path.join(HERE, outname)
    seats = [b['seat'] for jx in jxs for _p, pd in pieces_of(jx)
             for b in parse_raw(pd)]
    for tg in ('true', 'false'):
        doc = fitz.open(os.path.join(out, 'ansbook-%s.pdf' % tg))
        nt = fold2('\n'.join(p.get_text() for p in doc))
        doc.close()
        labs = [m.start() for m in re.finditer(r'\[答案\]', nt)]
        bad = [i for i, (p, s) in enumerate(zip(labs, seats))
               if not nt[:p].endswith(s)]
        print('%s[%s]: 标签 %d 失中 %d' % (outname, tg, len(labs), len(bad)))
        for i in bad[:3]:
            p = labs[i]
            print('  @%d exp[%s] 前40: %s' % (i, seats[i], nt[max(0, p - 40):p]))
