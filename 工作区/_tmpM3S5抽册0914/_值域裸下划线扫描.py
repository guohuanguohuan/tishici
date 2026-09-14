# -*- coding: utf-8 -*-
"""值域裸下划线扫描（补强①前置）：全 44 件 blocks 值/详解中裸 `_`（非 \\_）分布、
源 ansitem 行护栏先例计数、裸 `_` 是否处数学段内。只读。"""
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import CJ, T

RE_ITEM_ANY = re.compile(r'\\ansitem\{([^{}]*)\}\{')
GUARD = 'catcode'


def blocks_of(pdir):
    src = T.read_text(os.path.join(pdir, 'main.tex'))
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    out, cur = [], None
    for i, raw in enumerate(lines):
        code = T.strip_comment(raw)
        mb = T.RE_BEGIN.match(code)
        if mb and cur is None:
            cur = {'key': mb.group(1), 'line': '', 'rawline': '', 'val': None,
                   'note': None}
            continue
        if cur is not None:
            mi = RE_ITEM_ANY.search(code)
            if mi and cur['val'] is None:
                cur['line'] = code
                cur['rawline'] = raw
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


def raw_underscore_positions(s):
    """值串内裸 `_`（未被反斜杠转义）位置表。"""
    pos = []
    j = 0
    while j < len(s):
        if s[j] == '\\':
            j += 2
            continue
        if s[j] == '_':
            pos.append(j)
        j += 1
    return pos


def math_context(s, pos):
    """判定位置 pos 处字符是否处 $…$ 或 \\(…\\) 数学段内。"""
    for p in pos:
        before = s[:p]
        doll = before.count('$') - before.count('\\$') * 0  # 粗计：\$ 少见
        # \\( 与 \\) 配对
        par = len(re.findall(r'\\\(', before)) - len(re.findall(r'\\\)', before))
        if doll % 2 == 1 or par % 2 == 1:
            return True
    return False


tot = {'块': 0, '值裸_': 0, '详解裸_': 0, '源件护栏行': 0, '裸_处数学段': 0}
det = []
for jx in ('导学件', '练习件', '拓展册'):
    for pdir in sorted(glob.glob(os.path.join(CJ, jx, '*'))):
        if not os.path.exists(os.path.join(pdir, 'main.tex')):
            continue
        bs = blocks_of(pdir)
        for b in bs:
            tot['块'] += 1
            if GUARD in b.get('rawline', ''):
                tot['源件护栏行'] += 1
            pv = raw_underscore_positions(b['val'] or '')
            pn = raw_underscore_positions(b.get('note') or '')
            if pv:
                tot['值裸_'] += 1
                if math_context(b['val'], pv):
                    tot['裸_处数学段'] += 1
                det.append((jx, os.path.basename(pdir), b['key'], '值', len(pv),
                            math_context(b['val'], pv), (b['val'][max(0, pv[0]-14):pv[0]+14])))
            if pn:
                tot['详解裸_'] += 1
                det.append((jx, os.path.basename(pdir), b['key'], '详解', len(pn),
                            math_context(b.get('note') or '', pn), ''))
print('总块', tot['块'])
print(json.dumps(tot, ensure_ascii=False))
print('裸_样例（件/键/域/个数/处数学段/片段）:')
for d in det[:30]:
    print(' ', d)
import json  # noqa
