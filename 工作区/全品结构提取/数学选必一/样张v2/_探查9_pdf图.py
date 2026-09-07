# -*- coding: utf-8 -*-
import pymupdf
doc = pymupdf.open(r"工作区/全品结构提取/数学选必一/样张v2/人教B版选必1-1.1.1-v2样张.pdf")
for pno in range(doc.page_count):
    page = doc[pno]
    infos = page.get_image_info(xrefs=True)
    if not infos: continue
    print(f"--- 第{pno+1}页 (页面 {page.rect.width:.0f}x{page.rect.height:.0f}pt) ---")
    for inf in infos:
        b = inf["bbox"]
        w_mm = (b[2]-b[0]) / 72 * 25.4
        h_mm = (b[3]-b[1]) / 72 * 25.4
        print(f"  xref={inf['xref']} bbox=({b[0]:.0f},{b[1]:.0f})-({b[2]:.0f},{b[3]:.0f})pt "
              f"= {w_mm:.1f}x{h_mm:.1f}mm 像素={inf['width']}x{inf['height']}")
