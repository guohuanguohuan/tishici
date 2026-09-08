# -*- coding: utf-8 -*-
"""v4.3 执行轮定向探针（二轮）：存疑项一次查清。
1) get_drawings stroke/fill 结构（横线/花形底线/表线厚度读法）
2) 花形行右词全部灰 span（坐线+右缘）
3) 题号 11.4pt 行 spans（负隙）
4) （×）/（√）-2.04 行全文
5) 选项行基线 pitch（A．行）
6) 章首级间距链（墨口径近似：bbox 减字体上伸修正）
7) 表1/表2 横线 y 集合（行高/表顶前距）
8) 检测区解析行→下题号隙
9) 学习目标条目几何
"""
import os
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件"
PT = 72 / 25.4
MARGIN = 15 * PT
COLW = (595.276 - 2 * MARGIN - 7.5 * PT) / 2
MID = MARGIN + COLW + 7.5 * PT / 2
mm = lambda v: v / PT

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
p1 = doc[0]

print('=== 1) drawing 结构抽样（y<40mm p1） ===')
n = 0
for d in p1.get_drawings():
    r = d['rect']
    if r.y1 < 40 * PT and r.width > 100:
        print(' type=%s stroke=%s fill=%s width=%s rect_h=%.3fmm' % (
            d['type'], d.get('color'), d.get('fill'), d.get('width'), mm(r.height)))
        n += 1
        if n >= 4:
            break

print('=== 1b) 花形底线 p1（y 60-75mm 区全 drawing） ===')
for d in p1.get_drawings():
    r = d['rect']
    if 55 * PT < r.y0 < 75 * PT and r.width > 100:
        print(' type=%s stroke=%s fill=%s width=%s h=%.3fmm x0=%.2f x1=%.2f y0=%.2f' % (
            d['type'], d.get('color'), d.get('fill'), d.get('width'),
            mm(r.height), mm(r.x0), mm(r.x1), mm(r.y0)))

print('=== 1c) 表线结构（p1 右栏 y>200mm, 灰122） ===')
n = 0
for d in p1.get_drawings():
    r = d['rect']
    c = d.get('color')
    if c and tuple(round(x * 255) for x in c) == (122, 122, 122) and r.y0 > 200 * PT:
        print(' type=%s width=%s h=%.3fmm w=%.2fmm y=%.2f x=%.2f' % (
            d['type'], d.get('width'), mm(r.height), mm(r.width), mm(r.y0), mm(r.x0)))
        n += 1
        if n >= 6:
            break

print('=== 2) 花形行灰词 spans（全页 6.5pt 附近） ===')
for pno in (0, 1, 6):
    if pno >= len(doc):
        continue
    page = doc[pno]
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                if 6.0 <= sp['size'] <= 7.0 and sp['text'].strip():
                    cl = MARGIN if ln['bbox'][0] < MID else MARGIN + COLW + 7.5 * PT
                    print(' p%d [%s] size=%.2f x0=%.2f x1=%.2f(右距栏线%.2f) y0=%.2f y1=%.2f' % (
                        pno + 1, sp['text'], sp['size'], mm(sp['bbox'][0]), mm(sp['bbox'][2]),
                        mm(cl + COLW - sp['bbox'][2]), mm(sp['bbox'][1]), mm(sp['bbox'][3])))

print('=== 3) 题号 11.4pt 行 spans ===')
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            sps = ln['spans']
            if any(abs(sp['size'] - 11.4) < 0.4 and sp['text'].strip().endswith('．') for sp in sps):
                parts = ['%r[s%.1f x%.2f-%.2f]' % (sp['text'], sp['size'], mm(sp['bbox'][0]), mm(sp['bbox'][2])) for sp in sps]
                print(' p%d %s' % (pno, ' '.join(parts)))

print('=== 4) （×）/（√）行全文 ===')
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t.endswith('（√）') or t.endswith('（×）'):
                cl = MARGIN if ln['bbox'][0] < MID else MARGIN + COLW + 7.5 * PT
                print(' p%d 右距栏线%.2f 全文：%s' % (pno, mm(cl + COLW - ln['bbox'][2]), t[:60]))

print('=== 5) 选项行 pitch（行首 A．/B．/C．/D．） ===')
from collections import defaultdict
for pno, page in enumerate(doc, 1):
    cols = defaultdict(list)
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if len(t) > 1 and t[0] in 'ABCD' and t[1] in '．.':
                ci = 0 if ln['bbox'][0] < MID else 1
                cols[ci].append((t[:4], ln['spans'][0]['origin'][1], ln['spans'][0]['size']))
    for ci, items in cols.items():
        items.sort(key=lambda x: x[1])
        prev = None
        for t, y, sz in items:
            g = '%.2f' % mm(y - prev) if prev else '-'
            print(' p%d c%d %-6s y=%.1f sz=%.1f pitch_mm=%s' % (pno, ci, t, mm(y), sz, g))
            prev = y

print('=== 6) 章首级间距链（bbox 口径+墨修正参考） ===')
lines1 = []
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        if t:
            lines1.append((t, ln['bbox'], ln['spans'][0]['size'], ln['spans'][0]['origin'][1]))
def find2(pre):
    for t, bb, sz, oy in lines1:
        if t.startswith(pre):
            return (bb, sz, oy)
    return None
hl = None
for d in p1.get_drawings():
    r = d['rect']
    if r.width > 300 and r.height <= 2 and r.y0 < 40 * PT:
        hl = r
anchors = []
for pre in ('第一章', '1.1 ', '1.1.1', '第1课时', '【学习目标】'):
    a = find2(pre)
    anchors.append((pre, a))
for pre, a in anchors:
    if a:
        print(' %-14s bbox_y %.2f-%.2f size=%.1f base=%.2f' % (pre, mm(a[0][1]), mm(a[0][3]), a[1], mm(a[2])))
    else:
        print(' %-14s 未找到' % pre)
# 每行全部匹配（防错锚）
for pre in ('1.1 ', '1.1.1', '第1课时'):
    hits = [(t[:24], mm(bb[1]), sz) for t, bb, sz, oy in lines1 if t.startswith(pre)]
    print(' %r 全部命中: %s' % (pre, hits[:5]))

print('=== 7) 表1/表2 横线 y（灰122 fill/stroke 统一收） ===')
for pno, page in enumerate(doc, 1):
    ys = []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        rgb = tuple(round(x * 255) for x in c)
        if rgb == (122, 122, 122) and r.width > 15 * PT:
            ys.append((round(mm(r.y0), 2), round(mm(r.height if d['type'] == 'f' else (d.get('width') or 0) / PT), 3), round(mm(r.x0), 1)))
    if ys:
        ys.sort()
        print(' p%d n=%d:' % (pno, len(ys)), ys)

print('=== 8) 检测区解析行→下题号隙（p6） ===')
page = doc[5]
rows = []
for blk in page.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        y1 = ln['bbox'][3]
        y0 = ln['bbox'][1]
        rows.append((y0, y1, t))
rows.sort()
for i, (y0, y1, t) in enumerate(rows):
    if t.startswith('【解析】') or (len(t) > 2 and t[0] in '12345' and t[1] == '．'):
        print(' y %.2f-%.2f %s' % (mm(y0), mm(y1), t[:34]))

print('=== 9) 学习目标条目（p1 10.5pt 楷体行） ===')
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        sp0 = ln['spans'][0]
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        if 'KaiTi' in sp0['font'] or 'kai' in sp0['font'].lower():
            print(' x0=%.2f y=%.2f-%.2f sz=%.1f %s' % (mm(ln['bbox'][0]), mm(ln['bbox'][1]), mm(ln['bbox'][3]), sp0['size'], t[:30]))
