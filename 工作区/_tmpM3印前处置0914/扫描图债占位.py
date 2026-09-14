# -*- coding: utf-8 -*-
"""A2 前哨：练习件/导学件 图债占位行扫描（S3 图债哨同口径）。只读。"""
import io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
RE_INLINE = re.compile(r'(?<!\\)%.*$')
PAT = ('如图', '〔图', '图嵌', '图债')

PIECES = {
    '02': '课时02-倾斜角与斜率',
    '12': '课时12-2.5.2椭圆的几何性质',
    '13': '课时13-2.6.1双曲线的标准方程',
    '15': '课时15-2.7.1抛物线方程',
    '18': '课时18-2.8②压轴综合二',
    '19': '课时19-章末总结与复习',
    '17': '课时17-2.8①压轴综合一',
}

for tree in ('练习件', '导学件'):
    for pid, fn in PIECES.items():
        p = os.path.join(CJ, tree, fn, 'main.tex')
        if not os.path.exists(p):
            continue
        occ = []
        for i, l in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
            lb = RE_INLINE.sub('', l)
            if any(w in lb for w in PAT):
                occ.append(i)
        print('%s-%s %s' % (tree, pid, occ))
