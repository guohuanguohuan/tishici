# -*- coding: utf-8 -*-
"""_成册诊断.py — 三册成册门红病灶定位（err/missing/seat diff/[答案]缺位）。"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T
import fitz

for d in ('导学答案册', '练习答案册', '拓展答案册'):
    p = os.path.join(HERE, d)
    print('=====', d)
    for sh in ('ansbook-true', 'ansbook-false'):
        log = open(os.path.join(p, sh + '.log'), encoding='utf-8',
                   errors='replace').read()
        errs = re.findall(r'^!.*$', log, re.M)
        miss = re.findall(r'Missing character[^\n]*', log)
        unds = re.findall(r'Underfull[^\n]*', log)
        overs = re.findall(r'Overfull[^\n]*', log)
        print(' %s: err=%d miss=%d under=%d over=%d' % (sh, len(errs), len(miss),
                                                        len(unds), len(overs)))
        for e in errs[:4]:
            print('   !', e[:100])
        for m in sorted(set(miss))[:3]:
            print('   miss:', m[:90])
    # seat 序 diff（对 true 档）
    rd = json.load(open(os.path.join(p, '成册读数.json'), encoding='utf-8'))
    doc = fitz.open(os.path.join(p, 'ansbook-true.pdf'))
    txt = '\n'.join(pg.get_text() for pg in doc)
    doc.close()
    got = re.findall(r'(?<![0-9A-Za-z])([0-9A-Za-z]{1,4})\.\s*\[答案\]', txt)
    # 期望 seats：从 ansbook.tex 复抽
    src = T.read_text(os.path.join(p, 'ansbook.tex'))
    exp = re.findall(r'\\ansitem\{([^{}]*)\}\{', src)
    n = min(len(got), len(exp))
    diff = next((i for i in range(n) if got[i] != exp[i]), n)
    print(' seat: got=%d exp=%d 首歧@%d got[%s] exp[%s]' %
          (len(got), len(exp), diff, got[diff] if diff < len(got) else '-',
           exp[diff] if diff < len(exp) else '-'))
    if diff < len(exp):
        i = txt.find('[答案]', 0)
        # 找歧位附近文本
        pos = 0
        for _ in range(diff + 1):
            pos = txt.find('[答案]', pos) + 1
        print('   歧位上下文:', txt[max(0, pos - 60):pos + 30].replace('\n', '⏎')[:110])
    if len(got) < len(exp):
        print('   缺位：expect %s（未见于 PDF 文本正则）' % exp[len(got) - 1:][:3])
