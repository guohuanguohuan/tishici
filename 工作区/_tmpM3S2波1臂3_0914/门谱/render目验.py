# -*- coding: utf-8 -*-
"""render目验.py（波1臂3 参数化版）— 双档 PDF→PNG（150dpi）；true 入片 png/，双档入 过程件/目验PNG/<片>/{true,false}/。
用法: python render目验.py <片目录> <片短名>
"""
import glob
import os
import sys

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import fitz  # pymupdf

PIECE = sys.argv[1]
SHORT = sys.argv[2]
PROC = 'C:/提示词/工作区/_tmpM3S2波1臂3_0914/目验PNG/' + SHORT

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
