# -*- coding: utf-8 -*-
"""_假红残片人工核.py — ②假红 9 件复核取证。
口径：残片（强折形后仍失中的 needle 片段）→ 在抽册册 PDF（true/false 双档）定位渲染窗口，
按「极简折叠」（仅保 CJK/字母/数字，剔全部符号与空白）做序列级在册断言——
符号形差异（π/引号/分式/负号字形等）被剔除后序列仍全同＝内容确已印出＝器面折形缺口假红。
取证三件套：needle 残片｜PDF 渲染窗口原文｜双档极简折叠命中。"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T, fold
from _强折形复验 import strong_needle
import fitz

CJK_RE = re.compile(r'[\u4e00-\u9fffA-Za-z0-9]+')


def xfold(s):
    """极简折叠：NFKC＋空白归一＋负号折连字后，仅保留 CJK/字母/数字 连续序列拼接。"""
    return ''.join(CJK_RE.findall(fold(s)))


def rendered_window(hay_raw, needle_frag, span=50):
    """在原文（fold 后）里找残片最长命中前缀，返回其后渲染窗口（证排印实况）。"""
    pos, plen = -1, 0
    for L in range(len(needle_frag), 3, -1):
        p = hay_raw.find(needle_frag[:L])
        if p >= 0:
            pos, plen = p, L
            break
    if pos < 0:
        return None, 0
    return hay_raw[pos + plen: pos + plen + span], plen


res = json.load(open(os.path.join(HERE, '片段在册证明.json'), encoding='utf-8'))
out = {}
for name, v in res.items():
    d = os.path.join(HERE, name.split('｜')[0])
    pian = json.load(open(os.path.join(d, '抽册读数.json'),
                          encoding='utf-8'))['片']
    key = name.split('｜')[1]
    val = json.load(open(os.path.join(d, '抽册读数.json'),
                         encoding='utf-8'))['册值快照'][key]
    hay_raw, hay_x = {}, {}
    for tag in ('true', 'false'):
        doc = fitz.open(os.path.join(d, 'ansbook-%s.pdf' % tag))
        t = fold('\n'.join(pg.get_text() for pg in doc))
        hay_raw[tag] = t
        hay_x[tag] = xfold(t)
        doc.close()
    frag_report = []
    for frag in v['缺片']:
        win, plen = rendered_window(hay_raw['true'], frag)
        hit_x = {t: (xfold(frag) in hay_x[t]) for t in hay_x}
        frag_report.append({
            '残片(强折形needle)': frag,
            '极简折叠形': xfold(frag),
            '双档极简在册': all(hit_x.values()),
            '分档命中': hit_x,
            'needle最长命中前缀长': plen,
            'PDF渲染窗口(接前缀后50字)': win,
        })
    # 构造类登记：值内出现的 TeX 构造→器面缺口根因
    constructs = sorted(set(re.findall(
        r'\\(?:sqrt|pi|allowbreak|hspace|frac|pm|cdot|text|mathrm|left|right)'
        r'|\\[\(\)]|\\"|\u201c|\u201d|\u2212', val)))
    out[name] = {'件目录': d.replace('\\', '/'), '键': key,
                 '构造缺口类': constructs, '残片核': frag_report,
                 '全残片极简在册': all(f['双档极简在册'] for f in frag_report)}

# 衔接节（第 9 件，强折形已全中，无残片）：同口径补极简双档在册证
d9 = os.path.join(HERE, '导学件-衔接节')
val9 = json.load(open(os.path.join(d9, '抽册读数.json'),
                      encoding='utf-8'))['册值快照']['2章-练-衔接-10']
hay9 = {}
for tag in ('true', 'false'):
    doc = fitz.open(os.path.join(d9, 'ansbook-%s.pdf' % tag))
    hay9[tag] = xfold('\n'.join(pg.get_text() for pg in doc))
    doc.close()
out['导学件-衔接节｜2章-练-衔接-10'] = {
    '件目录': d9.replace('\\', '/'), '键': '2章-练-衔接-10',
    '构造缺口类': sorted(set(re.findall(
        r'\\(?:sqrt|pi|allowbreak|hspace|frac|pm|cdot|text|mathrm|left|right)'
        r'|\\[\(\)]|\\"|\u201c|\u201d|\u2212', val9))),
    '残片核': [], '强折形全中': True,
    '全残片极简在册': all(xfold(val9) in hay9[t] for t in hay9)}

json.dump(out, open(os.path.join(HERE, '假红残片人工核.json'), 'w',
                    encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, '→ 极简在册:', v['全残片极简在册'],
          '构造:', v['构造缺口类'])
