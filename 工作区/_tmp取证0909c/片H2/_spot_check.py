# -*- coding: utf-8 -*-
"""片H2 维持项抽点复测：判断题序号隙 / = 墨隙 / ∥ 墨隙 / 标点前后墨隙。"""
import numpy as np
import pymupdf
from PIL import Image
import io

doc = pymupdf.open(r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf')


def ink(pno, rect, thr=170, dpi=600):
    px = dpi / 72
    pix = doc[pno].get_pixmap(dpi=dpi, clip=pymupdf.Rect(*rect))
    a = np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('L')).astype(np.uint8) < thr
    ys, xs = np.nonzero(a)
    if not len(xs):
        return None
    return dict(x0=rect[0] + xs.min() / px, x1=rect[0] + xs.max() / px,
                y0=rect[1] + ys.min() / px, y1=rect[1] + ys.max() / px)


# 判断题：找 "(1)" 形态行（p1/p2 诊断）
hits = []
for pno in range(doc.page_count):
    d = doc[pno].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            cs = [c for sp in l['spans'] for c in sp['chars'] if c['c'].strip()]
            if len(cs) > 6 and cs[0]['c'] == '(' and cs[1]['c'].isdigit() and cs[2]['c'] == ')' and 0x4e00 <= ord(cs[3]['c'][0]) <= 0x9fff:
                hits.append((pno, [round(v, 2) for v in cs[0]['bbox']], [round(v, 2) for v in cs[1]['bbox']],
                             [round(v, 2) for v in cs[2]['bbox']], [round(v, 2) for v in cs[3]['bbox']]))
print('判断题 (N) 序号行 n =', len(hits))
for h in hits[:6]:
    pno = h[0]
    rb = ink(pno, (h[3][0] - 0.2, h[3][1] + 2, h[3][2] + 0.2, h[3][3] - 1))
    rt = ink(pno, (h[4][0] - 0.5, h[4][1] + 3, h[4][0] + 0.5 + (h[4][2] - h[4][0]) * 0.4, h[4][3] - 1))
    print(f'   p{pno+1} 「)」→首字 ink 隙 = {(h[4][0]-h[3][2]):.3f}pt = {(h[4][0]-h[3][2])*25.4/72:.3f}mm')

# = 墨隙：找 "=" 两侧
for pno in range(doc.page_count):
    d = doc[pno].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            cs = [c for sp in l['spans'] for c in sp['chars'] if c['c'].strip()]
            for i, c in enumerate(cs):
                if c['c'] == '=' and 0 < i < len(cs) - 1 and cs[i-1]['c'] not in '=<>≤≥≠':
                    L = ink(pno, (cs[i-1]['bbox'][0]-0.3, cs[i-1]['bbox'][1]+2, cs[i-1]['bbox'][2], cs[i-1]['bbox'][3]-2))
                    M = ink(pno, (c['bbox'][0]-0.3, c['bbox'][1]+2, c['bbox'][2]+0.3, c['bbox'][3]-2))
                    R = ink(pno, (cs[i+1]['bbox'][0], cs[i+1]['bbox'][1]+2, cs[i+1]['bbox'][2]+0.3, cs[i+1]['bbox'][3]-2))
                    if L and M and R and 'a' <= cs[i+1]['c'][0].lower() <= 'z':
                        print(f'= 隙 p{pno+1}: 左 {(M["x0"]-L["x1"])*25.4/72:.3f}mm 右 {(R["x0"]-M["x1"])*25.4/72:.3f}mm')
                        break
            else:
                continue
            break
        else:
            continue
        break
    else:
        continue
    break
