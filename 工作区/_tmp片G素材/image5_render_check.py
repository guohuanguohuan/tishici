# -*- coding: utf-8 -*-
"""Render fig-image5-fold.pdf at source scale (1px = 1 source px) and compare with source."""
import numpy as np, pymupdf
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image5.png"
PDF = r"C:\提示词\工作区\_tmp片G素材\fig-image5-fold.pdf"
OUT = r"C:\提示词\工作区\_tmp片G素材"

S_MM_PX = 54.7 / 1798.0          # mm per source px
PX_MM = 1.0 / S_MM_PX             # 32.8673 source px per mm
ZOOM = PX_MM * 25.4 / 72.0        # pdf pt -> px

doc = pymupdf.open(PDF)
page = doc[0]
print("pdf page size (pt):", page.rect.width, page.rect.height,
      "=> mm:", page.rect.width / 72 * 25.4, page.rect.height / 72 * 25.4)
pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), alpha=False)
pix.save(OUT + r"\_redraw_raw.png")
g = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 0]
red = g < 128
print("redraw raster:", red.shape)

src = np.array(Image.open(SRC))[:, :, 3] > 128
print("source raster:", src.shape)

from scipy import ndimage


def comps(mask, minsize=50):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        cnt = int((lab[sl] == i + 1).sum())
        if cnt < minsize:
            continue
        out.append(dict(x0=sl[1].start, x1=sl[1].stop, y0=sl[0].start, y1=sl[0].stop,
                        w=sl[1].stop - sl[1].start, h=sl[0].stop - sl[0].start, px=cnt))
    return out


rs = comps(red)
ss = comps(src)
rs.sort(key=lambda d: -d['px']); ss.sort(key=lambda d: -d['px'])
print("\n-- redraw components --")
for d in rs[:20]:
    print(f"  px={d['px']:6d} x[{d['x0']},{d['x1']}) y[{d['y0']},{d['y1']}) w={d['w']} h={d['h']}")
print("\n-- source components --")
for d in ss[:20]:
    print(f"  px={d['px']:6d} x[{d['x0']},{d['x1']}) y[{d['y0']},{d['y1']}) w={d['w']} h={d['h']}")

# ink bbox comparison
for nm, mask in (("source", src), ("redraw", red)):
    ys, xs = np.where(mask)
    print(f"\n{nm} ink bbox: x {xs.min()}..{xs.max()} (w={xs.max()-xs.min()+1}) "
          f"y {ys.min()}..{ys.max()} (h={ys.max()-ys.min()+1})")
