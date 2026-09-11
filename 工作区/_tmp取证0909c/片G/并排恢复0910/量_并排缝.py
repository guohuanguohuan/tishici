# -*- coding: utf-8 -*-
"""并排恢复0910 标定环：main.pdf 中 g1(image1)/g2(image2) 并排带——600dpi 墨级
顶差／墨缝（图墨左缘−带内文墨右缘max）／盒缝（图盒左缘−带内文墨右缘max）／右缘（栏右−图墨右缘）。
栏常数按现件实测：左栏 x0=48.8，右栏 x0=308.4，右栏右缘≈546.9（通栏行实测）。
用法：python 量_并排缝.py [pdf]"""
import sys
import pymupdf
import numpy as np
from PIL import Image as PILImage

PT = 72 / 25.4
COLL = (48.8, 308.4)
COLR = 546.5          # 右栏右缘＝栏左 308.4＋84.0mm×2.8346（通栏行实测 546.5）
MID = (COLL[0] + COLR) / 2

pdf = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
doc = pymupdf.open(pdf)
print(f'# {pdf} pages={len(doc)}')
for pno, page in enumerate(doc, 1):
    infos = page.get_image_info(xrefs=True)
    if not infos:
        continue
    tlines = [(pymupdf.Rect(l['bbox']), ''.join(sp['text'] for sp in l['spans']))
              for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b.get('lines', [])]
    for info in infos:
        rct = pymupdf.Rect(info['bbox'])
        wmm = rct.width / PT
        if info['width'] not in (691, 764):
            print(f'  跳过 {info["width"]}x{info["height"]}px x[{rct.x0:.1f},{rct.x1:.1f}] y[{rct.y0:.1f},{rct.y1:.1f}] 宽{wmm:.1f}mm（下置/他图）')
            continue
        cl2 = COLL[0] if rct.x0 < (COLL[0] + COLL[1]) / 2 else COLL[1]
        clip = pymupdf.Rect(cl2 - 2, rct.y0 - 8, COLR + 2, rct.y1 + 8)
        pix = page.get_pixmap(dpi=600, clip=clip)
        a = np.array(PILImage.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')) < 128
        sc = pix.width / clip.width
        ix0, iy0 = (rct.x0 + 0.6 - clip.x0) * sc, (rct.y0 + 0.6 - clip.y0) * sc
        ix1, iy1 = (rct.x1 - 0.6 - clip.x0) * sc, (rct.y1 - 0.6 - clip.y0) * sc
        sub = a[int(iy0):int(iy1), int(ix0):int(ix1)]
        ys, xs = np.nonzero(sub)
        ink = [clip.x0 + (int(ix0) + xs.min()) / sc, clip.y0 + (int(iy0) + ys.min()) / sc,
               clip.x0 + (int(ix0) + xs.max()) / sc, clip.y0 + (int(iy0) + ys.max()) / sc]
        # 带内文墨右缘 max（行 bbox 与图盒垂直重叠>1pt，且行在图左）
        best = None
        x_stop = int((rct.x0 - clip.x0) * sc) - 1
        x_start = int((cl2 - clip.x0) * sc)
        for yy in range(max(0, int((ink[1] - clip.y0) * sc)), min(a.shape[0], int((ink[3] - clip.y0) * sc))):
            nz = np.nonzero(a[yy, x_start:x_stop])[0]
            if len(nz):
                xr = clip.x0 + (x_start + nz.max()) / sc
                if best is None or xr > best:
                    best = xr
        # 首行墨顶（带内最上文字行）
        near = [(bb, tt) for bb, tt in tlines
                if bb.x0 >= cl2 - 2 and bb.x1 <= rct.x0 + 5 and bb.x0 < rct.x0
                and bb.y1 > rct.y0 and bb.y0 < rct.y1 and (bb.x1 - bb.x0) > 20
                and not tt.lstrip().startswith('◆') and not tt.lstrip().startswith('例')]
        first = min(near, key=lambda z: z[0].y0) if near else None
        ftop = None
        if first is not None:
            fy0 = int((first[0].y0 - 2 - clip.y0) * sc)
            fy1 = int((first[0].y1 + 1 - clip.y0) * sc)
            fx0 = int((first[0].x0 - clip.x0) * sc)
            fx1 = int((first[0].x1 + 1 - clip.x0) * sc)
            fsub = a[fy0:fy1, fx0:fx1]
            fys, _ = np.nonzero(fsub)
            ftop = clip.y0 + (fy0 + fys.min()) / sc if len(fys) else None
        tag = 'g1' if info['width'] == 691 else 'g2'
        top = (ink[1] - ftop) / PT if ftop else float('nan')
        seam = (ink[0] - best) / PT if best else float('nan')
        boxseam = (rct.x0 - best) / PT if best else float('nan')
        right = (COLR - ink[2]) / PT
        print(f'{tag}@p{pno} 盒[{rct.x0:.1f},{rct.x1:.1f}]x[{rct.y0:.1f},{rct.y1:.1f}] 盒宽{wmm:.2f} '
              f'带内行数{len(near)} 文墨右缘{(best-cl2)/PT if best else float("nan"):.2f}mm '
              f'｜顶差{top:+.2f} 墨缝{seam:.2f} 盒缝{boxseam:.2f} 右缘{right:.2f}')
