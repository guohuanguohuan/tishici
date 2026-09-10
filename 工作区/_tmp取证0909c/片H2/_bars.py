# -*- coding: utf-8 -*-
"""横杠检测器：在 360dpi 页图上找 '薄宽横杠'（分式杠/减号/等于号），
按上下文分类：分式杠（上下有墨）/ 减号（两侧有同带墨、无上下）并给邻隙。
两口径通用（我方 main.pdf 360dpi 渲染 / 全品 png 14.176px-per-mm）。"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

PXMM_REF = 14.176


def load_ink(path, thr=170):
    gray = np.asarray(Image.open(path).convert('L')).astype(np.uint8)
    return gray < thr


def bars(path, x0=None, x1=None, y0=None, y1=None, thr=170):
    ik = load_ink(path, thr)
    if x0 is not None:
        m = np.zeros_like(ik)
        m[y0:y1, x0:x1] = True
        ik = ik & m
    lab, n = ndimage.label(ik, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)
    out = []
    for sl in objs:
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if not (1 <= h <= 7 and 12 <= w <= 90):
            continue
        xa, xb, ya, yb = xs.start, xs.stop, ys.start, ys.stop
        # 上下文：上方 30px 内与下方 30px 内的墨
        up = ik[max(0, ya - 30):ya, xa:xb].sum()
        dn = ik[yb:yb + 30, xa:xb].sum()
        lw = ik[ya - 12:yb + 12, max(0, xa - 40):xa]
        rw = ik[ya - 12:yb + 12, xb:xb + 40]
        # 左右的紧邻成分（跳白找）
        def gap_to(region, axis):
            colhas = region.sum(axis=axis) > 0
            idx = np.where(colhas)[0]
            if not len(idx):
                return None
            return int(idx[0]) if axis == 0 else int(len(colhas) - 1 - idx[-1])
        gl = gap_to(lw, 0)
        gr = gap_to(rw, 0)
        frac = up > 20 and dn > 20
        out.append(dict(x=(xa, xb), y=(ya, yb), w=w, h=h, up=int(up), dn=int(dn),
                        gap_l=gl, gap_r=gr, kind='frac' if frac else 'dash'))
    return out


if __name__ == '__main__':
    p = sys.argv[1]
    kw = {}
    if len(sys.argv) > 5:
        kw = dict(x0=int(sys.argv[2]), x1=int(sys.argv[3]), y0=int(sys.argv[4]), y1=int(sys.argv[5]))
    for b in bars(p, **kw):
        print(f"{b['kind']:4} x{b['x'][0]}-{b['x'][1]} y{b['y'][0]}-{b['y'][1]} w{b['w']} h{b['h']} "
              f"up{b['up']} dn{b['dn']} gaps L{b['gap_l']} R{b['gap_r']}")
