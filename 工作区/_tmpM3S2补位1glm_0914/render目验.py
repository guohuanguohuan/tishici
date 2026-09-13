# -*- coding: utf-8 -*-
"""render目验.py — 补位1glm 三片：双档 PDF→PNG（150dpi）；true 入片 png/，双档入过程件。"""
import glob
import os

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import fitz

BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件'
PROC = 'C:/提示词/工作区/_tmpM3S2补位1glm_0914/目验PNG'
for piece in ('衔接节', '课时02-倾斜角与斜率', '课时03-方向向量与法向量'):
    PIECE = f'{BASE}/{piece}'
    for tag in ('true', 'false'):
        src = os.path.join(PIECE, f'main-{tag}.pdf')
        out = os.path.join(PROC, piece, tag)
        os.makedirs(out, exist_ok=True)
        for p in glob.glob(os.path.join(out, 'page*.png')):
            os.remove(p)
        doc = fitz.open(src)
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=150)
            pix.save(os.path.join(out, f'page{i}.png'))
            if tag == 'true':
                os.makedirs(os.path.join(PIECE, 'png'), exist_ok=True)
                pix.save(os.path.join(PIECE, 'png', f'page{i}.png'))
        print(piece, tag, len(doc), 'pages')
        doc.close()
print('ok')
