# -*- coding: utf-8 -*-
"""render目验.py — 双档 PDF→PNG（150dpi）入过程件 目验PNG-<件>/{true,false}/。
母版件＝工作区/_tmpM3S2母版0914/门谱/render目验.py；本片口径差异：png 不落片目录
（派工件清单：main.tex＋双壳＋值台账＋件manifest；目验件留过程件，登记于终报）。
用法: python render目验.py <04|05|06>
"""
import glob
import os
import sys

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import fitz  # pymupdf

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = {'04': '课时04-点斜式与斜截式', '05': '课时05-两点式与一般式',
        '06': '课时06-两条直线的位置关系'}
tag = sys.argv[1] if len(sys.argv) > 1 else '04'
PIECE = os.path.join(ROOT, '成卷/导学件', DIRS[tag])
PROC = os.path.join(HERE, '..', f'目验PNG-{tag}')

for mode in ('true', 'false'):
    src = os.path.join(PIECE, f'main-{mode}.pdf')
    out = os.path.join(PROC, mode)
    os.makedirs(out, exist_ok=True)
    for p in glob.glob(os.path.join(out, 'page*.png')):
        os.remove(p)
    doc = fitz.open(src)
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=150).save(os.path.join(out, f'page{i}.png'))
    print(f'{tag} {mode}: {len(doc)} 页 → {out}')
    doc.close()
print('ok')
