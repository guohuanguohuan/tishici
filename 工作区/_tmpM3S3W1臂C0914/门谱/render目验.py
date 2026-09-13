# -*- coding: utf-8 -*-
"""render目验.py — 双档 PDF→PNG（150dpi）；true 入片 png/，双档入 过程件/目验PNG/{true,false}/。
照抄 母版门谱 render目验 同构，换 PIECE/PROC 路径。"""
import glob
import os

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import fitz  # pymupdf

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时06B-2.2.4点到直线距离'
PROC = 'C:/提示词/工作区/_tmpM3S3W1臂C0914/目验PNG'

for tag in ('true', 'false'):
    src = os.path.join(PIECE, f'main-{tag}.pdf')
    out = os.path.join(PROC, tag)
    os.makedirs(out, exist_ok=True)
    for p in glob.glob(os.path.join(out, 'page*.png')):
        os.remove(p)
    doc = fitz.open(src)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(out, f'page{i}.png'))
        if tag == 'true':
            os.makedirs(os.path.join(PIECE, 'png'), exist_ok=True)
            for p in glob.glob(os.path.join(PIECE, 'png', 'page*.png')):
                os.remove(p)
            pix.save(os.path.join(PIECE, 'png', f'page{i}.png'))
    print(tag, len(doc), 'pages')
    doc.close()
print('ok')
