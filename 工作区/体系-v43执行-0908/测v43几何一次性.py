# -*- coding: utf-8 -*-
"""v4.3 导学件一次性几何测量脚本（执行轮调参用，非断言）：
输出 章首几何/级间距、花形组几何、表格线、题号隙、括号列位、页脚、图距 等实测值，
与任务书/派工规格书目标值对照，供回填 corrg 系调参常量。"""
import os
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件"
PT = 72 / 25.4
MARGIN = 15 * PT
COLW = (595.276 - 2 * MARGIN - 7.5 * PT) / 2
MID = MARGIN + COLW + 7.5 * PT / 2
COLL = (MARGIN, MARGIN + COLW + 7.5 * PT)
COLR = 595.276 - MARGIN
BODY_BOT = 842.0 - 20 * PT
mm = lambda v: v / PT

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
p1 = doc[0]
print('=== 章首几何（p1） ===')
squares = []
for d in p1.get_drawings():
    r = d['rect']
    f = d.get('fill')
    if f and r.y0 < 200 and r.width < 200:
        rgb = tuple(round(x * 255) for x in f)
        if rgb in ((221, 221, 221), (119, 119, 119)):
            squares.append((rgb[0], r))
for g, r in sorted(squares, key=lambda t: (t[0], t[1].y0, t[1].x0)):
    print(f'  方块 fill={g} x0={mm(r.x0):.2f} y0={mm(r.y0):.2f} x1={mm(r.x1):.2f} y1={mm(r.y1):.2f} w={mm(r.width):.2f} h={mm(r.height):.2f}')
if squares:
    ux0 = min(r.x0 for _, r in squares); ux1 = max(r.x1 for _, r in squares)
    uy0 = min(r.y0 for _, r in squares); uy1 = max(r.y1 for _, r in squares)
    print(f'  union: {mm(ux1-ux0):.2f} x {mm(uy1-uy0):.2f} mm（目标 13.8×16.6）')
# 章名/节/小节/课时/学习目标/横线
lines1 = []
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        if t:
            lines1.append((t, ln['bbox']))
def find(pre):
    for t, bb in lines1:
        if t.startswith(pre):
            return bb
    return None
zh = find('第一章'); jie = find('1.1 空间向量'); xj = find('1.1.1'); ks = find('第1课时'); mb = find('【学习目标】')
hlines = [(d['rect']) for d in p1.get_drawings() if d['rect'].width > 300 and d['rect'].height <= 2]
if hlines and zh:
    hl = hlines[0]
    print(f'  横线 y={mm(hl.y0):.2f} 厚={mm(hl.height):.3f}mm（目标 0.2pt=0.071mm）')
    print(f'  章名 x0={mm(zh[0]):.2f}（方块右+3.1 目标）')
    for nm, bb, tgt in (('横线→节', jie, 6.9), ('节→小节', xj, 5.5), ('小节→课时', ks, 5.9), ('课时→目标', mb, 5.8)):
        if bb:
            print(f'  {nm}: {mm(bb[1] - hl.y1):.2f}mm（目标 {tgt}）')
    if mb:
        print(f'  章首占地 版心顶→【学习目标】顶 = {mm(mb[1] - MARGIN):.2f}mm（目标 ≈57）')

print('=== 花形组（3 处） ===')
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        rgb = tuple(round(x * 255) for x in c)
        if rgb == (77, 77, 77) and r.height <= 3 and r.width > 100:
            cl = MARGIN if (r.x0 + r.x1) / 2 < MID else MARGIN + COLW + 7.5 * PT
            # 菱形组 bbox（同栏线上方 25pt 内白底黑边 path）
            dias = []
            for d2 in page.get_drawings():
                r2 = d2['rect']
                if r2.y1 <= r.y0 + 1 and r2.y1 >= r.y0 - 25 and r2.x0 >= cl - 2 and r2.x1 <= cl + COLW + 2 and 10 < r2.width < 40:
                    dias.append(r2)
            if dias:
                dx0 = min(x.x0 for x in dias); dx1 = max(x.x1 for x in dias)
                dy0 = min(x.y0 for x in dias); dy1 = max(x.y1 for x in dias)
            else:
                dx0 = dx1 = dy0 = dy1 = 0
            # 右词
            word = None
            for blk in page.get_text('dict')['blocks']:
                for ln in blk.get('lines', []):
                    t = ''.join(sp['text'] for sp in ln['spans']).strip()
                    if any(k in t for k in ('知识导学', '考点探究', '知识评价')):
                        for sp in ln['spans']:
                            if sp['bbox'][1] > r.y0 - 20 and sp['bbox'][3] < r.y1 + 6:
                                word = sp
            print(f'p{pno} 底线 厚={mm(r.height):.3f}(目0.42) 起点+{mm(r.x0-cl):.2f}(目2.77) 终点距栏线{mm(cl+COLW-r.x1):.2f}(目4.0)'
                  f' 菱形组 {mm(dx1-dx0):.1f}×{mm(dy1-dy0):.1f}(目23.5×6.7) 贴线{mm(r.y0-dy1):.2f}(目0.3)'
                  + (f' 右词底-线顶={mm(r.y0-word["bbox"][3]):.2f}(目0.43) 词右距栏线{mm(cl+COLW-word["bbox"][2]):.2f}(目4.0) 词号{word["size"]:.1f}' if word else ' 无右词'))

print('=== 表线抽样（表1 p1 右栏） ===')
tab_rules = []
for d in p1.get_drawings():
    r = d['rect']
    c = d.get('color')
    if not c:
        continue
    rgb = tuple(round(x * 255) for x in c)
    if rgb == (122, 122, 122) and r.y0 > 200:
        tab_rules.append((r.width, r.height, r))
hs = sorted({round(mm(r.height), 3) for _, h, r in tab_rules if r.width > 20 for r in [r]})
vs = sorted({round(mm(r.width), 3) for w, _, r in tab_rules if r.height > 20 for r in [r]})
print(f'  横线厚度集合 {hs}（目标 内0.141/外0.282） 竖线宽度集合 {vs}')

print('=== 题号/题侧/题干隙（检测题 11.4pt 题号） ===')
gaps = []
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            sps = ln['spans']
            for i, sp in enumerate(sps):
                if abs(sp['size'] - 11.4) < 0.4 and sp['text'].strip().endswith('．'):
                    rest = sps[i+1:]
                    if rest:
                        gaps.append(mm(rest[0]['bbox'][0] - sp['bbox'][2]))
print(f'  题号→题侧 ink 隙 n={len(gaps)} ' + ' '.join(f'{g:.2f}' for g in gaps))
gaps2 = []
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            sps = ln['spans']
            for i, sp in enumerate(sps):
                t = sp['text'].strip()
                if t.endswith('）〕') and sp['size'] < 9:
                    rest = sps[i+1:]
                    if rest:
                        gaps2.append(mm(rest[0]['bbox'][0] - sp['bbox'][2]))
print(f'  题侧→题干 ink 隙 n={len(gaps2)} ' + ' '.join(f'{g:.2f}' for g in gaps2))

print('=== 判断题括号列位 ===')
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t.endswith('（√）') or t.endswith('（×）'):
                cl = MARGIN if ln['bbox'][0] < MID else MARGIN + COLW + 7.5 * PT
                print(f'  p{pno} …{t[-6:]} ）右缘距栏线 {mm(cl + COLW - ln["bbox"][2]):.2f}mm（目 5.4±0.5）')

print('=== 页脚 ===')
for pno, page in enumerate(doc, 1):
    blk_rect = None
    for d in page.get_drawings():
        r = d['rect']
        f = d.get('fill')
        if f and r.y0 > BODY_BOT - 10:
            rgb = tuple(round(x * 255) for x in f)
            if rgb == (221, 221, 221):
                blk_rect = r
    if blk_rect:
        num = None
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                for sp in ln['spans']:
                    if sp['text'].strip() == str(pno) and sp['bbox'][1] > BODY_BOT - 10:
                        num = sp
        odd = pno % 2 == 1
        inner = blk_rect.x0 if odd else blk_rect.x1
        d_edge = mm(abs((num['bbox'][0] + num['bbox'][2]) / 2 - inner)) if num else -1
        print(f'  p{pno} 块 {mm(blk_rect.width):.1f}×{mm(blk_rect.height):.1f}(目26.2×7.8) 底{mm(842.0 - blk_rect.y1):.1f}'
              f' 数字中心距版心侧缘 {d_edge:.1f}mm 数字{num["size"] if num else -1:.1f}pt')

print('=== 居中图与上下距 ===')
for pno, page in enumerate(doc, 1):
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            cl = MARGIN if r.x0 < MID else MARGIN + COLW + 7.5 * PT
            if abs(r.x0 + r.x1 - 2 * cl - COLW) < 8 and r.width > 50:
                print(f'  p{pno} 图宽 {mm(r.width):.1f}mm y0={mm(r.y0):.1f} y1={mm(r.y1):.1f}')

print('=== 选项行距直方图（19/21 档验证） ===')
from collections import Counter
diffs = []
for page in doc:
    cols = {0: [], 1: []}
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if any(10 <= sp['size'] <= 11 for sp in ln['spans']):
                cols[0 if ln['bbox'][0] < MID else 1].append(ln['spans'][0]['origin'][1])
    for c in (0, 1):
        ys = sorted(cols[c])
        diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
cnt = Counter(diffs)
print('  主峰档:', cnt.most_common(8))
print('=== 灰档全集 ===')
grays = set()
for page in doc:
    for sp in [sp for blk in page.get_text('dict')['blocks'] for ln in blk.get('lines', []) for sp in ln['spans']]:
        col = sp['color']
        r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
        if r == g == b and 0 < r < 255:
            grays.add(r)
    for d in page.get_drawings():
        for key in ('color', 'fill'):
            c = d.get(key)
            if c:
                rgb = tuple(round(x * 255) for x in c)
                if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                    grays.add(rgb[0])
print(' ', sorted(grays))
