# -*- coding: utf-8 -*-
"""值域裸 `_` 逐块精判：逐下标分类（数学段/文本段），护栏需求判定。
结论口径＝护栏包/不包的唯一定据。只读。"""
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import CJ, T

RE_ITEM_ANY = re.compile(r'\\ansitem\{([^{}]*)\}\{')


def blocks_of(pdir):
    src = T.read_text(os.path.join(pdir, 'main.tex'))
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    out, cur = [], None
    for i, raw in enumerate(lines):
        code = T.strip_comment(raw)
        mb = T.RE_BEGIN.match(code)
        if mb and cur is None:
            cur = {'key': mb.group(1), 'val': None, 'note': None}
            continue
        if cur is not None:
            mi = RE_ITEM_ANY.search(code)
            if mi and cur['val'] is None:
                cur['val'], _ = T.extract_arg(lines, i, mi.end() - 1)
                continue
            mn = T.RE_NOTE.search(code)
            if mn and cur['note'] is None:
                cur['note'], _ = T.extract_arg(lines, i, mn.end() - 1)
                continue
            if T.RE_END.match(code):
                out.append(cur)
                cur = None
    return out


def math_mask(s):
    """返回 s 的布尔掩码：True＝处数学段（$…$／\\(…\\) 内）。配对按扫描序。"""
    n = len(s)
    mask = [False] * n
    i = 0
    in_math = False
    opened = None  # '$' 或 '\\('
    while i < n:
        if s[i] == '\\':
            if s.startswith('\\(', i):
                in_math, opened = True, '\\('
                mask[i] = True
                mask[i + 1] = True
                i += 2
                continue
            if s.startswith('\\)', i):
                in_math, opened = False, None
                mask[i] = True
                mask[i + 1] = True
                i += 2
                continue
            i += 2
            continue
        if s[i] == '$':
            if not in_math:
                in_math, opened = True, '$'
            else:
                in_math, opened = False, None
            i += 1
            continue
        mask[i] = in_math
        i += 1
    return mask


def classify(pdir):
    rows = []
    for b in blocks_of(pdir):
        v = b['val'] or ''
        j = 0
        txt, mth = [], []
        while j < len(v):
            if v[j] == '\\':
                j += 2
                continue
            if v[j] == '_':
                (mth if math_mask(v)[j] else txt).append(j)
            j += 1
        if txt or mth:
            rows.append((b['key'], len(txt), len(mth),
                         ('文本@' + repr(v[max(0, txt[0] - 16):txt[0] + 16])) if txt else '',
                         ('数学@' + repr(v[max(0, mth[0] - 16):mth[0] + 16])) if mth else ''))
    return rows


for jx in ('导学件', '练习件', '拓展册'):
    for pdir in sorted(glob.glob(os.path.join(CJ, jx, '*'))):
        if not os.path.exists(os.path.join(pdir, 'main.tex')):
            continue
        for r in classify(pdir):
            print(jx, os.path.basename(pdir), r)
