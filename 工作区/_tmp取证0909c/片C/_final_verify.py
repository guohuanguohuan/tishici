# -*- coding: utf-8 -*-
"""片C 终验汇总（#27/#29/#34/#37）：输出可引用数值。"""
import re
import numpy as np
import pymupdf
from PIL import Image

PTMM = 72 / 25.4
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
BASE_PDF = r'C:\提示词\工作区\_tmp取证0909c\片C\基线_main.pdf'
doc = pymupdf.open(PDF)

print('### #37 √ 字体归属')
fonts = {}
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                if '√' in sp['text']:
                    fonts.setdefault(sp['font'], 0)
                    fonts[sp['font']] += sp['text'].count('√')
print('  √ 承载字体:', fonts, '（FZSSJW 承载:', any('FZSSJW' in k for k in fonts), '）')

print('### #34 × 矢量几何（去重后按 rect 分组）')
seen, xs = set(), []
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        r = pymupdf.Rect(d['rect'])
        w, h = r.width / PTMM, r.height / PTMM
        if 2.2 < w < 2.6 and 2.2 < h < 2.6:
            k = (pno, round(r.x0, 1), round(r.y0, 1))
            if k in seen:
                continue
            seen.add(k)
            xs.append((pno, r, w, h))
print(f'  × 墨盒 {len(xs)} 个（含章首装饰方块 1 个）')
sizes = sorted((w, h) for _, _, w, h in xs)
print('  尺寸中位:', f'{sizes[len(sizes)//2][0]:.3f}×{sizes[len(sizes)//2][1]:.3f}mm')
# 笔画：取 p2 答案位 × 的矢量多边形对边长
for pno, r, w, h in xs:
    if pno == 2 and abs(r.x0 - 268.7) < 0.5:
        for d in doc[pno - 1].get_drawings():
            if d['fill'] is None:
                continue
            rr = pymupdf.Rect(d['rect'])
            if abs(rr.x0 - r.x0) < 0.1 and abs(rr.y0 - r.y0) < 0.1:
                pts = []
                for item in d['items']:
                    if item[0] == 'l':
                        pts += [(round(item[1].x, 3), round(item[1].y, 3)),
                                (round(item[2].x, 3), round(item[2].y, 3))]
                uniq = []
                for p in pts:
                    if p not in uniq:
                        uniq.append(p)
                def pdist(p, a, b):
                    return abs((b[0]-a[0])*(a[1]-p[1]) - (a[0]-p[0])*(b[1]-a[1])) / np.hypot(b[0]-a[0], b[1]-a[1])
                sw = pdist(uniq[3], uniq[1], uniq[2])
                print(f'  矢量对边距（线宽）= {sw:.4f}pt = {sw/PTMM:.4f}mm（靶 0.4pt=0.141mm）')
                break
        break
# 600dpi 二值墨盒
page = doc[1]
r = pymupdf.Rect(268.72, 546.92, 275.55, 553.76)
pix = page.get_pixmap(dpi=600, clip=pymupdf.Rect(r.x0-1, r.y0-1, r.x1+1, r.y1+1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
a = np.array(im) < 128
bb = Image.fromarray((a*255).astype(np.uint8)).getbbox()
print(f'  600dpi 二值墨盒 { (bb[2]-bb[0])/600*25.4:.2f}×{(bb[3]-bb[1])/600*25.4:.2f}mm')
# 括号带居中
for pno in (2, 3):
    page = doc[pno-1]
    raw = page.get_text('rawdict')
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        rr = pymupdf.Rect(d['rect'])
        if 2.2 < rr.width/PTMM < 2.6 and 2.2 < rr.height/PTMM < 2.6:
            yc = (rr.y0 + rr.y1) / 2
            parens = []
            for blk in raw['blocks']:
                if blk['type'] != 0:
                    continue
                for ln in blk['lines']:
                    for sp in ln['spans']:
                        for ch in sp['chars']:
                            if ch['c'] in '()' and abs((ch['bbox'][1]+ch['bbox'][3])/2 - yc) < 8:
                                parens.append(pymupdf.Rect(ch['bbox']))
            lefts = [q for q in parens if q.x1 <= rr.x0+2]
            rights = [q for q in parens if q.x0 >= rr.x1-2]
            if lefts and rights:
                lp = max(lefts, key=lambda q: q.x1); rp = min(rights, key=lambda q: q.x0)
                bc = (min(lp.y0, rp.y0) + max(lp.y1, rp.y1)) / 2
                print(f'  p{pno} 答案位 × 中心距括号带中心 {(yc-bc)/PTMM:+.3f}mm')
                break

print('### #29 =/∥ 胶宽（advance 口径）与悬挂')
def scan(pdf):
    d = pymupdf.open(pdf)
    eq, par = [], 0
    for pno, page in enumerate(d, 1):
        raw = page.get_text('rawdict')
        chars = [ch for blk in raw['blocks'] if blk['type'] == 0
                 for ln in blk['lines'] for sp in ln['spans'] for ch in sp['chars']]
        for i, ch in enumerate(chars):
            if ch['c'] != '=':
                continue
            prev = chars[i-1] if i > 0 else None
            if prev is None:
                continue
            eq.append((ch['bbox'][0] - prev['bbox'][2]) / PTMM)
        strokes = [pymupdf.Rect(x['rect']) for x in page.get_drawings()
                   if x['fill'] is not None and 2.5 < pymupdf.Rect(x['rect']).width < 8.0
                   and 7.5 < pymupdf.Rect(x['rect']).height < 12.0]
        used = [False]*len(strokes)
        for i, A in enumerate(strokes):
            if used[i]:
                continue
            for j in range(i+1, len(strokes)):
                B = strokes[j]
                if used[j]:
                    continue
                if abs(A.y0-B.y0) < 1 and 2 < B.x0-A.x0 < 5.5:
                    par += 1
                    used[i] = used[j] = True
                    break
    return eq, par
for tag, pdf in (('基线', BASE_PDF), ('改后', PDF)):
    eq, npar = scan(pdf)
    over = [v for v in eq if v > 1.2]
    print(f'  {tag}: = 实例 {len(eq)}，>1.2mm 读数 {len(over)}，单侧中位 {sorted(eq)[len(eq)//2]:.3f}mm；∥ 实例 {npar}')
