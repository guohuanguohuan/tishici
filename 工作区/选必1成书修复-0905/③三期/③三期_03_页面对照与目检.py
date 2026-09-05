# -*- coding: utf-8 -*-
"""③三期 03 页面对照与目检：③三期副本 PDF vs ③二期终 PDF（＝回写前基线）。
1) 页数对照（预期 32/32/32，有变即停跑信号）
2) 逐页像素差分（100dpi）：定位变化页；变化页差分像素须 ⊆ 图片框∪容差 6pt（零回流判据）
3) 目检切片：image3 框（新旧堆叠 220dpi）＋底缘放大条（400dpi，本论修复靶点）
落 ②工具\\PDF对比\\③三期_PNG\\。"""
import io, os, json
import pymupdf
from PIL import Image, ImageDraw

OLD = r'C:/提示词/工作区/选必1成书修复-0905/②工具/巡检_③二期/pdf/清单2.pdf'
NEW = r'C:/提示词/工作区/选必1成书修复-0905/②工具/巡检_③三期/pdf/清单2.pdf'
OUTD = r'C:/提示词/工作区/选必1成书修复-0905/②工具/PDF对比/③三期_PNG'
REPORT = r'C:/提示词/工作区/选必1成书修复-0905/②工具/报告'
os.makedirs(OUTD, exist_ok=True)
EXPECT = 32
DPI = 100
TOL_PT = 6

def render(page, dpi=DPI):
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    return pm.samples, pm.width, pm.height

dold, dnew = pymupdf.open(OLD), pymupdf.open(NEW)
n1, n2 = len(dold), len(dnew)
out = {'pages': {'old': n1, 'new': n2, 'expect': EXPECT, 'ok': n1 == n2 == EXPECT},
       'changed_pages': [], 'reflow_alerts': []}
print(f'页数 {n1} vs {n2} (expect {EXPECT}) {"OK" if out["pages"]["ok"] else "PAGE-CHANGE!"}')
assert n1 == n2 == EXPECT, '页数有变 —— 停跑呈报!'
out['ALLOK'] = True
for i in range(n1):
    s1, w, h = render(dold[i])
    s2, w2, h2 = render(dnew[i])
    if (w, h) != (w2, h2):
        out['changed_pages'].append(i + 1); out['reflow_alerts'].append(f'p{i+1} 尺寸变化'); continue
    diff = [k for k in range(0, len(s1), 2) if abs(s1[k] - s2[k]) > 6]
    if len(diff) < 8:
        continue
    imgs = [tuple(v * DPI / 72 for v in it['bbox']) for it in dnew[i].get_image_info()]
    T = TOL_PT / 72 * DPI
    viol = []
    for k in diff:
        x, y = k % w, k // w
        if not any(bx0 - T <= x <= bx1 + T and by0 - T <= y <= by1 + T for (bx0, by0, bx1, by1) in imgs):
            viol.append((x, y))
    out['changed_pages'].append([i + 1, len(diff), len(viol)])
    print(f'  变化页 p{i+1}: diff={len(diff)}px 越界={len(viol)}px')
    if len(viol) > 50:
        xs = [v[0] for v in viol]; ys = [v[1] for v in viol]
        out['reflow_alerts'].append(f'p{i+1} 越界差分像素{len(viol)} bbox=({min(xs):.0f},{min(ys):.0f},{max(xs):.0f},{max(ys):.0f})px@100dpi')
out['ALLOK'] = not out['reflow_alerts']
json.dump(out, open(os.path.join(REPORT, '③三期_页面对照.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('SUMMARY_DIFF ALLOK =', out['ALLOK'])

# ---- 目检切片：仅变化页，锁定 image3 框（画布比 437×342）----
ZOOM = 220 / 72
for chg in out['changed_pages']:
    pno = chg[0]
    i = pno - 1
    infos = dnew[i].get_image_info()
    for k, it in enumerate(infos):
        bb = pymupdf.Rect(it['bbox'])
        if bb.width < 40 or bb.height < 40:
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
        dr.text((4, 2), f'清单2 p{pno} img{k} 220dpi  OLD(3二期) {it["width"]}x{it["height"]}', fill=0)
        canvas.paste(im_old, (0, lab))
        dr.text((4, lab + im_old.height + 1), 'NEW(3三期 fix)', fill=0)
        canvas.paste(im_new, (0, lab + im_old.height + sep))
        fn = f'清单2_p{pno:03d}_img{k}_{it["width"]}x{it["height"]}.png'
        canvas.save(os.path.join(OUTD, fn))
        print('落', fn)
        # 底缘放大条（400dpi，取框下部 22%＋左缘 30%：O 与 x 落位处）
        zb = pymupdf.Rect(clip.x0, clip.y0 + clip.height * 0.78, clip.x1, clip.y1)
        pm_z = dnew[i].get_pixmap(matrix=pymupdf.Matrix(400 / 72, 400 / 72), clip=zb, colorspace=pymupdf.csGRAY)
        zo = Image.frombytes('L', (pm_z.width, pm_z.height), pm_z.samples)
        zb2 = pymupdf.Rect(clip.x0, clip.y0, clip.x0 + clip.width * 0.30, clip.y1)
        pm_z2 = dnew[i].get_pixmap(matrix=pymupdf.Matrix(400 / 72, 400 / 72), clip=zb2, colorspace=pymupdf.csGRAY)
        zo2 = Image.frombytes('L', (pm_z2.width, pm_z2.height), pm_z2.samples)
        fn2 = f'清单2_p{pno:03d}_img{k}_底缘400dpi.png'
        zo.save(os.path.join(OUTD, fn2)); print('落', fn2)
        fn3 = f'清单2_p{pno:03d}_img{k}_左缘400dpi.png'
        zo2.save(os.path.join(OUTD, fn3)); print('落', fn3)
print('DONE')
