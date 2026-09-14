# -*- coding: utf-8 -*-
"""_强折形复验.py — 对 9 件「逐键值印面在册」假红做臂侧强折形复验。
强折形＝\sqrt→√、\( \)剥、\allowbreak/\hspace{..}/\\{\\} 剥、上下标结构符剥等渲染近似。"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T, fold
import fitz


def strong_needle(val):
    v = val or ''
    v = re.sub(r'\\(?:allowbreak|hspace\{[^{}]*\}|quad|qquad|,|;|!|:)', '', v)
    v = re.sub(r'\\sqrt\[(\d+)\]', lambda m: '√' + m.group(1) + '√', v)
    v = v.replace('\\sqrt', '√')
    v = re.sub(r'\\(?:text|mathrm|mathbf|mathit)\{([^{}]*)\}', r'\1', v)
    for _ in range(3):
        v = re.sub(r'\\(?:left|right|big[lr]?[ld]?)?\s?([\(\)\[\]\{\}|.])', r'\1', v)
    v = re.sub(r'\\(?:lfloor|rfloor)', '', v)
    v = v.replace('\\{', '{').replace('\\}', '}')
    v = v.replace('\\(', '').replace('\\)', '')
    v = v.replace('\\iff', '\u27fa').replace('\\Leftrightarrow', '\u27fa')
    v = v.replace('\\leqslant', '\u2a7d').replace('\\geqslant', '\u2a7e')
    v = v.replace('\\times', '×').replace('\\div', '÷').replace('\\pm', '±')
    v = v.replace('\\in', '∈').replace('\\cup', '∪').replace('\\cap', '∩')
    v = v.replace('\\infty', '∞').replace('\\triangle', '△')
    v = re.sub(r'\\[a-zA-Z]+\*?', '', v)          # 余下控制序列剥
    v = v.replace('$', '').replace('_', '').replace('^', '')
    v = v.replace('{', '').replace('}', '')
    return fold(v)


out = {}
for d in sorted(glob.glob(os.path.join(HERE, '*-课时*')) +
                glob.glob(os.path.join(HERE, '*-衔接节'))):
    rp = os.path.join(d, '抽册读数.json')
    if not os.path.exists(rp):
        continue
    rd = json.load(open(rp, encoding='utf-8'))
    if not any('逐键值印面' in r for r in (rd.get('红') or [])):
        continue
    hay = {}
    for tag in ('true', 'false'):
        p = os.path.join(d, 'ansbook-%s.pdf' % tag)
        doc = fitz.open(p)
        hay[tag] = fold('\n'.join(pg.get_text() for pg in doc))
        doc.close()
    miss = []
    for k, v in (rd.get('册值快照') or {}).items():
        nv = strong_needle(v)
        if not (nv in hay['true'] and nv in hay['false']):
            miss.append((k, nv[:50]))
    out[os.path.basename(d)] = {'缺印键': miss[:6], '缺印数': len(miss)}

tot = {k: v['缺印数'] for k, v in out.items()}
json.dump(out, open(os.path.join(HERE, '强折形复验.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('强折形复验（假红核实）：', tot if tot else '9 件全中')
