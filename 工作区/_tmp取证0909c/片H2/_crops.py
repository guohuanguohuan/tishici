# -*- coding: utf-8 -*-
"""片H2 裁片：数学式同尺对照（我方 vs 全品）＋改后典型公式行放大。全部 360dpi 同尺。"""
import os
import numpy as np
import pymupdf
from PIL import Image, ImageDraw

REF = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'
OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2/crops'
PDF = r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(PDF)
_pages = {}


def mine(pno, box_pt):
    """我方 PDF 取 360dpi 像素（box 为 pt）"""
    key = pno
    if key not in _pages:
        pix = doc[pno].get_pixmap(dpi=360)
        _pages[key] = Image.open(__import__('io').BytesIO(pix.tobytes('png'))).convert('RGB')
    im = _pages[key]
    x0, y0, x1, y1 = [v * 5 for v in box_pt]
    return im.crop((int(x0), int(y0), int(x1), int(y1)))


def ref(pno, box_px):
    im = Image.open(REF % pno).convert('RGB')
    return im.crop(box_px)


def stack(items, path, gap=10, label_h=24):
    W = max(i.width for i, _ in items)
    H = sum(i.height + label_h for i, _ in items) + gap * (len(items) - 1)
    c = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(c)
    y = 0
    for im, lab in items:
        d.text((4, y + 4), lab, fill=(200, 0, 0))
        y += label_h
        c.paste(im, (0, y))
        y += im.height + gap
    c.save(path)
    print('saved', path, c.size)


# 1. cap + 脚本 + 减号（字母串）：我方 p4 变式1 两行 vs 全品 p05 同串
mine_ab = mine(3, (46, 96, 292, 133))
ref_ab = ref('p05', (1540, 2835, 2790, 2910))
stack([(mine_ab, 'MINE  p4 变式1：ABCD-A1B1C1D1（cap 34px / 下标 18.6px / 短横 w13 隙4px）'),
       (ref_ab, 'QUANPIN p05：A1B1C1D1（cap 36-38px / 下标 19-20px）')],
      f'{OUT}/H2_E3_cap_脚本_字母串.png')

# 2. 减号（字母串短横）放大对照
mine_dash = mine(3, (270, 98, 290, 114))
ref_dash = ref('p06', (930, 1665, 1120, 1730))    # 全品 p06 例2 的 ABCDEF-A1B1 段
a2 = mine_dash.resize((mine_dash.width * 3, mine_dash.height * 3), Image.LANCZOS)
b2 = ref_dash.resize((ref_dash.width * 2, ref_dash.height * 2), Image.LANCZOS)
stack([(a2, 'MINE  ABCD-（3x：短横 w13 隙 4.2px@360）'),
       (b2, 'QUANPIN ABCDEF-A1（2x：短横 w15 隙 1-2px）')],
      f'{OUT}/H2_E3_减号对照.png')

# 3. 分式（÷ 大式）对照：我方 p6 详解行 vs 全品 p06 例3 选项 ½
mine_frac = mine(5, (305, 100, 560, 140))
ref_frac = ref('p06', (1630, 3730, 2100, 3870))
stack([(mine_frac, 'MINE  p6 详解：AM=1/2 BM=√3/2（dfrac 总高 104px）'),
       (ref_frac, 'QUANPIN p06 选项：½BD ½DB（总高 105px）')],
      f'{OUT}/H2_E3_分式对照.png')

# 4. 改后典型公式行放大（我方 p6 详解 + 选项，含分式与选项大式）
mine_row = mine(5, (305, 40, 560, 200))
big = mine_row.resize((mine_row.width * 2, mine_row.height * 2), Image.LANCZOS)
stack([(big, 'MINE p6 典型公式行（2x）：dfrac 分式 + 选项')], f'{OUT}/H2_改后典型公式行.png')

# 5. 全品 p06 同位对照（同尺）
ref_row = ref('p06', (1540, 3450, 2800, 3900))
stack([(ref_row, 'QUANPIN p06 同位（例3 题干+选项，dfrac 同款）')], f'{OUT}/H2_全品同位_p06.png')
