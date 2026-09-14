# -*- coding: utf-8 -*-
"""needle 诊断：拓-课时01-T1 值的强折形串 vs ansbook PDF 提取面 逐段定位。只读。"""
import io
import json
import re
import sys

sys.path.insert(0, r'C:/提示词/工作区/_tmpM3S5抽册0914')
from _s5lib import T, fold  # noqa: E402
import fitz  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open(r'拓展册-上册/抽册读数.json', encoding='utf-8'))
val = d['册值快照']['2章-拓-课时01-T1']
print('值原串:', val[:120])

v = val
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
v = re.sub(r'\\[a-zA-Z]+\*?', '', v)
v = v.replace('$', '').replace('_', '').replace('^', '')
v = v.replace('{', '').replace('}', '')
nd = fold(v)
print('needle:', nd)

doc = fitz.open(r'拓展册-上册/ansbook-false.pdf')
hay = fold('\n'.join(p.get_text() for p in doc))
hay = hay.translate({ord('_'): None, ord('^'): None})
doc.close()
print('haystack 有 needle?', nd in hay)
# 二分定位最长匹配前缀
lo, hi = 0, len(nd)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if nd[:mid] in hay:
        lo = mid
    else:
        hi = mid - 1
print('最长匹配前缀 len=%d: %r' % (lo, nd[:lo]))
print('断点后 24 字:', repr(nd[lo:lo + 24]))
i = hay.find(nd[:lo][-8:] if lo >= 8 else nd[:lo])
print('haystack 该处实际后文:', repr(hay[i:i + 40]) if i >= 0 else '前缀未中')
