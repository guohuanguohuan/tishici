# -*- coding: utf-8 -*-
"""片C #29 复核：= 拉伸实例归因——按前邻字形分组，取基线同组最小值作「自然底」。
若改后读数 ≤ 基线同组底（或与之相等），则为字形自然间距（5mu＋斜体修正），非拉伸。"""
import pymupdf

PTMM = 72 / 25.4
BASE = r'C:\提示词\工作区\_tmp取证0909c\片C\基线_main.pdf'
NEW = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'


def collect(pdf):
    doc = pymupdf.open(pdf)
    rows = []
    for pno, page in enumerate(doc, 1):
        raw = page.get_text('rawdict')
        for blk in raw['blocks']:
            if blk['type'] != 0:
                continue
            for ln in blk['lines']:
                chars = [ch for sp in ln['spans'] for ch in sp['chars']]
                for i, ch in enumerate(chars):
                    if ch['c'] != '=':
                        continue
                    prev = chars[i - 1] if i > 0 else None
                    if prev is None:
                        continue
                    gl = (ch['bbox'][0] - prev['bbox'][2]) / PTMM
                    rows.append((prev['c'], round(gl, 3), pno, round(ch['bbox'][1], 1)))
    return rows


base = collect(BASE)
new = collect(NEW)
floors = {}
for c, gl, pno, y in base:
    floors[c] = min(floors.get(c, 99), gl)
print('== 基线各前邻字形最小胶宽（自然底）==')
for c in sorted(floors, key=lambda k: floors[k]):
    if floors[c] > 0.5:
        print(f'  {c!r}: {floors[c]:.3f}mm')
print()
print('== 改后 >1.2mm 实例逐条归因 ==')
n_attr = 0
for c, gl, pno, y in new:
    if gl <= 1.2:
        continue
    f = floors.get(c)
    verdict = '自然（=基线同组底）' if f is not None and abs(gl - f) < 0.02 else (
        f'自然（同组底 {f:.3f}）' if f is not None and gl <= f + 0.02 else f'超底 {(gl - (f or 0)):.3f}mm')
    if '自然' in verdict:
        n_attr += 1
    print(f'  p{pno} y={y} 前邻{c!r} L={gl:.3f}mm → {verdict}')
print(f'\n归因为自然字形间距 {n_attr} 处；真拉伸 {sum(1 for c, gl, p, y in new if gl > 1.2) - n_attr} 处')
print('改后全量单侧胶宽：min %.3f 中位 %.3f max %.3f mm' % (
    min(gl for c, gl, p, y in new),
    sorted(gl for c, gl, p, y in new)[len(new) // 2],
    max(gl for c, gl, p, y in new)))
