# -*- coding: utf-8 -*-
"""render目验-课时17.py — 双档 PDF→PNG（150dpi）；双档全入 过程件/目验PNG/{true,false}/（练习件片目录不放 png/，承 W2臂B 口径）。"""
import glob
import os

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import fitz  # pymupdf

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时17-2.8①压轴综合一'
PROC = 'C:/提示词/工作区/_tmpM3S3W2臂D0914/目验PNG'

for tag in ('true', 'false'):
    src = os.path.join(PIECE, f'main-{tag}.pdf')
    out = os.path.join(PROC, tag)
    os.makedirs(out, exist_ok=True)
    for p in glob.glob(os.path.join(out, f'目验-课时17-{tag}-p*.png')):
        os.remove(p)
    doc = fitz.open(src)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(out, f'目验-课时17-{tag}-p{i}.png'))
    print(tag, len(doc), 'pages')
    doc.close()
print('ok')
