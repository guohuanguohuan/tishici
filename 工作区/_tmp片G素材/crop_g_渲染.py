# -*- coding: utf-8 -*-
import fitz, numpy as np, sys
def render(pdf, dpi, out=None):
    d = fitz.open(pdf); p = d[0]
    pix = p.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a
def inkbox(a, thr=200):
    m = a < thr
    ys, xs = np.where(m)
    if len(xs)==0: return None
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv)>1 else "片G-image4-二面角-standalone.pdf"
    d = fitz.open(pdf); p = d[0]
    print("page mm: %.4f x %.4f" % (p.rect.width*25.4/72, p.rect.height*25.4/72))
    a = render(pdf, 302)
    print("raster:", a.shape, "inkbox(px):", inkbox(a))
    s = 66.3/788.0
    print("expect inkbox for canvas-aligned render: (12,21,744,404) at 66.3mm=788px scale")
    print("actual mm: ", [round(v*a.shape[1]/788.0*s,3) for v in inkbox(a)])
