# -*- coding: utf-8 -*-
r"""复审计·片C 独立重测：=/∥ 墨隙、行尾悬挂、× 墨幅与笔画、√ 字体归属、悬空引用
① 正文「条目+数字」：body.tex 正则 + PDF 文本层双查（目标 0）
② =/∥ 单侧墨隙（600dpi gray<128；字符 bbox 定簇，左右各 3mm 窗取邻墨）＋行尾悬挂计数
③ ×（TikZ 矢量）：get_drawings 找 2.4mm 级墨盒，600dpi 实测墨幅＋EDT 笔画
④ √ 字体归属：rawdict span 字体名
"""
import json
import os
import re

import numpy as np
import pymupdf
from scipy import ndimage
from skimage.morphology import skeletonize

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
BODY = r'C:\提示词\工作区\字替对照-0909\variantF\body.tex'
DPI = 600
PT = 72 / 25.4
MMPP = 25.4 / DPI
MARGIN = 17.575 * PT
COLW = 82.8 * PT
COLSEP = 9.25 * PT
COLL = [MARGIN, MARGIN + COLW + COLSEP]
COLR = [MARGIN + COLW, MARGIN + COLW + COLSEP + COLW]

doc = pymupdf.open(PDF)
out = {}

# ---------- ① 悬空引用「条目+数字」 ----------
body = open(BODY, encoding='utf-8').read()
hits_body = re.findall(r'条目\s*\d', body)
pdf_text = ''.join(p.get_text() for p in doc)
hits_pdf = re.findall(r'条目\s*\d', pdf_text)
print(f'① 悬空引用「条目+数字」：body.tex {len(hits_body)} 处 {hits_body[:5]}；PDF 文本层 {len(hits_pdf)} 处 {hits_pdf[:5]}')
out['xuankong'] = dict(body=len(hits_body), pdf=len(hits_pdf))

# ---------- ② =/∥ 墨隙 ----------
def render(page):
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)

def char_gaps(img, page, target_chars):
    """返回每个目标字符的左右墨隙（mm）与行尾悬挂标记"""
    res = []
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            chars = [c for s in l['spans'] for c in s['chars']]
            for ci, c in enumerate(chars):
                if c['c'] not in target_chars:
                    continue
                bb = c['bbox']
                # 行内 x 范围
                lx0 = min(cc['bbox'][0] for cc in chars)
                lx1 = max(cc['bbox'][2] for cc in chars)
                ly0 = min(cc['bbox'][1] for cc in chars)
                ly1 = max(cc['bbox'][3] for cc in chars)
                px = lambda mm: int(round(mm * DPI / 25.4))
                rx0 = px((bb[0] / PT) - 3.5); rx1 = px((bb[2] / PT) + 3.5)
                ry0 = px((ly0 / PT) - 0.6); ry1 = px((ly1 / PT) + 0.6)
                reg = img[max(0, ry0):ry1, max(0, rx0):rx1]
                if reg.size == 0:
                    continue
                mask = reg < 128
                colprof = mask.any(axis=0)
                cols = np.where(colprof)[0]
                if len(cols) == 0:
                    continue
                # 目标字符墨簇＝覆盖字符 bbox 中心的连通列段
                c0 = px(bb[0] / PT) - max(0, rx0); c1 = px(bb[2] / PT) - max(0, rx0)
                mid = (c0 + c1) // 2
                # 找包含 mid 的列段
                segs = []
                st = None
                for i, v in enumerate(colprof):
                    if v and st is None:
                        st = i
                    elif not v and st is not None:
                        segs.append((st, i - 1)); st = None
                if st is not None:
                    segs.append((st, len(colprof) - 1))
                tgt = None
                for s in segs:
                    if s[0] <= mid <= s[1]:
                        tgt = s; break
                if tgt is None:
                    # 取与 bbox 重叠最大者
                    tgt = max(segs, key=lambda s: min(s[1], c1) - max(s[0], c0))
                left = [s for s in segs if s[1] < tgt[0]]
                right = [s for s in segs if s[0] > tgt[1]]
                gl = (tgt[0] - left[-1][1]) * MMPP if left else None
                gr = (right[0][0] - tgt[1]) * MMPP if right else None
                # 行尾悬挂：目标字符是该行最右字符且右侧无墨
                is_last = (ci == len(chars) - 1) or (bb[2] >= lx1 - 0.5)
                hang = bool(is_last and gr is None)
                res.append(dict(page=None, char=c['c'], gl=None if gl is None else round(gl, 2),
                                gr=None if gr is None else round(gr, 2),
                                x=round(bb[0] / PT, 1), y=round(bb[1] / PT, 1), hang=hang,
                                last=bool(is_last)))
    return res

all_gaps = []
for pno, page in enumerate(doc, 1):
    img = render(page)
    for r in char_gaps(img, page, {'=', '∥'}):
        r['page'] = pno
        all_gaps.append(r)
# 过滤：只保留正文区（排除表格/页脚——用 y 区间粗滤：页脚 >275mm；表格区不滤，登记）
body_gaps = [r for r in all_gaps if r['y'] < 275]
eq = [r for r in body_gaps if r['char'] == '=']
par = [r for r in body_gaps if r['char'] == '∥']
def stat(rs, key):
    vs = [r[key] for r in rs if r[key] is not None]
    return (round(min(vs), 2), round(max(vs), 2), round(float(np.median(vs)), 2), len(vs)) if vs else None
print(f'② = 出现 {len(eq)} 处；左隙 min/max/med/n={stat(eq,"gl")}；右隙 {stat(eq,"gr")}')
print(f'   ∥ 出现 {len(par)} 处；左隙 min/max/med/n={stat(par,"gl")}；右隙 {stat(par,"gr")}')
hang_all = [r for r in body_gaps if r['hang']]
print(f'   行尾悬挂（目标字符为行末且右侧无墨）：{len(hang_all)} 处 {[(r["page"], r["char"], r["x"], r["y"]) for r in hang_all][:6]}')
stretch2x = [r for r in body_gaps if (r['gl'] or 0) >= 1.96 or (r['gr'] or 0) >= 1.96]
print(f'   ≥2×（1.96mm）读数：{len(stretch2x)} 处')
out['eq'] = dict(n=len(eq), gl=stat(eq, 'gl'), gr=stat(eq, 'gr'),
                 samples=[(r['page'], r['x'], r['y'], r['gl'], r['gr']) for r in eq[:12]])
out['par'] = dict(n=len(par), gl=stat(par, 'gl'), gr=stat(par, 'gr'),
                  samples=[(r['page'], r['x'], r['y'], r['gl'], r['gr']) for r in par[:12]])
out['hang'] = [(r['page'], r['char'], r['x'], r['y']) for r in hang_all]
out['stretch2x'] = len(stretch2x)

# ---------- ③ × TikZ 墨幅与笔画 ----------
x_marks = []
for pno, page in enumerate(doc, 1):
    img = render(page)
    for d in page.get_drawings():
        r = d['rect']
        w, h = r.width / PT, r.height / PT
        if 2.0 <= w <= 2.8 and 2.0 <= h <= 2.8 and abs(w - h) < 0.3:
            # 排除章首装饰方块（实心方块：填充面积占比高）——渲染后按墨密度区分
            px = lambda mm: int(round(mm * DPI / 25.4))
            reg = img[max(0, px(r.y0 / PT) - 1):px(r.y1 / PT) + 1, max(0, px(r.x0 / PT) - 1):px(r.x1 / PT) + 1]
            mask = reg < 128
            if mask.size == 0 or not mask.any():
                continue
            ys, xs = np.where(mask)
            bw = (xs.max() - xs.min() + 1) * MMPP; bh = (ys.max() - ys.min() + 1) * MMPP
            density = mask.mean()
            edt = ndimage.distance_transform_edt(mask)
            sk = skeletonize(mask)
            stroke = 2 * float(np.median(edt[sk])) * MMPP if sk.any() else None
            x_marks.append(dict(page=pno, box=[round(r.x0 / PT, 2), round(r.y0 / PT, 2), round(r.x1 / PT, 2), round(r.y1 / PT, 2)],
                                ink_w=round(bw, 3), ink_h=round(bh, 3), density=round(float(density), 3),
                                stroke_mm=None if stroke is None else round(stroke, 4)))
print(f'③ × 候选墨盒 {len(x_marks)} 个：')
for m in x_marks:
    print(f"   p{m['page']} 盒{m['box']} 墨幅 {m['ink_w']}×{m['ink_h']}mm 笔画 {m['stroke_mm']}mm 密度 {m['density']}")
out['x_marks'] = x_marks

# ---------- ④ √ 字体归属 ----------
sqrt_fonts = {}
for pno, page in enumerate(doc, 1):
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            for s in l['spans']:
                t = ''.join(c['c'] for c in s['chars'])
                if '√' in t:
                    sqrt_fonts.setdefault(s['font'], []).append((pno, t[:20]))
print('④ √ 字体归属：')
for f, occ in sqrt_fonts.items():
    print(f'   {f}: {len(occ)} 处 {occ[:4]}')
out['sqrt_fonts'] = {k: len(v) for k, v in sqrt_fonts.items()}
fsj = [f for f in sqrt_fonts if 'FZSSJW' in f]
print(f'   FZSSJW 承载 √：{sum(len(sqrt_fonts[f]) for f in fsj)} 处（应 0）')

with open(os.path.join(BASE, 'm_片C_符号_result.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('saved m_片C_符号_result.json')
