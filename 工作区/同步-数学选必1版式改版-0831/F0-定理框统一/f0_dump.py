# -*- coding: utf-8 -*-
"""F0-定理框统一：结构dump——逐body元素输出（序号/类型/pBdr/文字前缀），供逐条重判。"""
import sys, zipfile
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
path, out = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(path)
root = etree.fromstring(zin.read('word/document.xml'))
zin.close()
body = root.find(W + 'body')
els = list(body)
lines = []
for i, el in enumerate(els):
    tag = el.tag.split('}')[-1]
    if tag == 'tbl':
        lines.append(f'e{i:04d}|TBL|')
        continue
    if tag != 'p':
        lines.append(f'e{i:04d}|{tag}|')
        continue
    ppr = el.find(W + 'pPr')
    pbdr = ''
    if ppr is not None and ppr.find(W + 'pBdr') is not None:
        sides = []
        for s in ('top', 'left', 'bottom', 'right'):
            e = ppr.find(W + 'pBdr/' + W + s)
            if e is not None:
                sides.append(f"{s}:sz{e.get(W+'sz')},sp{e.get(W+'space')}")
        pbdr = 'PBDR[' + ','.join(sides) + ']'
    nimg = sum(1 for x in el.iter() if x.tag.endswith('}blip'))
    nom = sum(1 for x in el.iter() if x.tag.endswith('}oMath'))
    txt = ''.join(x.text or '' for x in el.iter(W + 't'))
    lines.append(f'e{i:04d}|P|img={nimg}|om={nom}|{pbdr}|{txt[:90]}')
open(out, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'{path}: {len(els)} body elements -> {out}')
