# -*- coding: utf-8 -*-
"""③二期 04 目检切片：对差分定位到的变化页，把页内图片框在 ②E 基线 PDF 与 ③二期 PDF 各裁高dpi图，
上下堆叠（上=②E旧图，下=③新图）落 ②工具\PDF对比\③二期_PNG\，供逐张目检（落位/清晰/不变形）。
"""
import io, os, json
import pymupdf
from PIL import Image, ImageDraw

OLD = r'C:/提示词/工作区/选必1成书修复-0905/②工具/巡检_②E/pdf'
NEW = r'C:/提示词/工作区/选必1成书修复-0905/②工具/巡检_③二期/pdf'
OUTD = r'C:/提示词/工作区/选必1成书修复-0905/②工具/PDF对比/③二期_PNG'
os.makedirs(OUTD, exist_ok=True)
DIFF = json.load(open(r'C:/提示词/工作区/选必1成书修复-0905/②工具/报告/③二期_02_页面对照.json', encoding='utf-8'))
ZOOM = 220 / 72  # 220dpi 裁片

for code, changed in DIFF['changed_pages'].items():
    pages = [c[0] if isinstance(c, (list, tuple)) else c for c in changed]
    dold, dnew = pymupdf.open(os.path.join(OLD, f'{code}.pdf')), pymupdf.open(os.path.join(NEW, f'{code}.pdf'))
    for pno in pages:
        i = pno - 1
        infos = dnew[i].get_image_info()
        for k, it in enumerate(infos):
            bb = pymupdf.Rect(it['bbox'])
            if bb.width < 40 or bb.height < 40:  # 忽略页眉装饰等小件
                continue
            clip = bb & dnew[i].rect
            pm_new = dnew[i].get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), clip=clip, colorspace=pymupdf.csGRAY)
            pm_old = dold[i].get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), clip=clip, colorspace=pymupdf.csGRAY)
            im_new = Image.frombytes('L', (pm_new.width, pm_new.height), pm_new.samples)
            im_old = Image.frombytes('L', (pm_old.width, pm_old.height), pm_old.samples)
            w = max(im_old.width, im_new.width)
            sep, lab = 14, 18
            canvas = Image.new('L', (w, im_old.height + im_new.height + sep + lab * 2), 255)
            dr = ImageDraw.Draw(canvas)
            dr.text((4, 2), f'{code} p{pno} img{k} 220dpi  OLD(2E) {it["width"]}x{it["height"]}', fill=0)
            canvas.paste(im_old, (0, lab))
            dr.text((4, lab + im_old.height + 1), f'NEW(3er)', fill=0)
            canvas.paste(im_new, (0, lab + im_old.height + sep))
            fn = f'{code}_p{pno:03d}_img{k}_{it["width"]}x{it["height"]}.png'
            canvas.save(os.path.join(OUTD, fn))
            print('落', fn)
print('DONE')
