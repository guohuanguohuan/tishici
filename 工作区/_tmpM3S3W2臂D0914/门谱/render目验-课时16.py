# -*- coding: utf-8 -*-
"""render目验-课时16.py — 双档 PDF→PNG（150dpi）；双档全入 过程件/目验PNG/{true,false}/（练习件片目录不放 png/，承 W2臂B 口径）。
（照抄母版 render目验.py，PIECE/PROC 换片＋命名 目验-课时16-<档>-pN.png＋剔片目录 png/ 写出。）"""
import glob
import os

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import fitz  # pymupdf

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时16-2.7.2抛物线性质'
PROC = 'C:/提示词/工作区/_tmpM3S3W2臂D0914/目验PNG'

for tag in ('true', 'false'):
    src = os.path.join(PIECE, f'main-{tag}.pdf')
    out = os.path.join(PROC, tag)
    os.makedirs(out, exist_ok=True)
    for p in glob.glob(os.path.join(out, f'目验-课时16-{tag}-p*.png')):
        os.remove(p)
    doc = fitz.open(src)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(out, f'目验-课时16-{tag}-p{i}.png'))
    print(tag, len(doc), 'pages')
    doc.close()
print('ok')
