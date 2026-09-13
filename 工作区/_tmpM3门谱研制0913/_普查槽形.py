# -*- coding: utf-8 -*-
"""普查 M2 练件槽行形状（只读探针，供槽宽门口径标定）。"""
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
MB = re.compile(r'\\makebox\[(\\dimexpr)?([0-9.]+)\\linewidth-([0-9.]+)em')
FS = re.compile(r'\\fontsize\{([0-9.]+)pt\}')
census = {}
odd = []
nolw = []
files = []
for d in ('导学件', '练习件', '章末-本章总结提升', '衔接节-1.2.1前'):
    files += glob.glob(d + '/**/*.tex', recursive=True)
for f in files:
    for i, ln in enumerate(open(f, encoding='utf-8'), 1):
        if 'newcommand' in ln:
            continue
        if 'makebox' not in ln:
            continue
        ms = MB.findall(ln)
        if ms:
            key = tuple(sorted(set(ms)))
            census[key] = census.get(key, 0) + 1
            if len(ms) not in (2, 4):
                odd.append((f, i, len(ms)))
        elif 'linewidth' in ln:
            nolw.append((f, i, ln.strip()[:100]))
print('== 槽形普查（(dimexpr?, 系数, 扣em) → 行数）==')
for k, v in sorted(census.items(), key=lambda x: -x[1]):
    print(v, k)
print('非2/4槽行数:', len(odd))
for o in odd[:10]:
    print('  ', o)
print('含makebox含linewidth但正则未中行数:', len(nolw))
for o in nolw[:10]:
    print('  ', o[0], o[1])
    print('    ', o[2])
