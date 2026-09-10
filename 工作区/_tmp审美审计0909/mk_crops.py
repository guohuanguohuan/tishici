# -*- coding: utf-8 -*-
"""生成报告用同尺并排裁片（全部 360dpi 同尺度）。"""
from PIL import Image, ImageDraw
import numpy as np

M = 'render/snap-p0%d.png'
REF = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'

def load(p):
    return Image.open(p).convert('RGB')

def stack(items, gap=14, label_h=26, path='crops/x.png', bg='white'):
    """items: [(img, label)] 纵向堆叠，左对齐。"""
    W = max(i.width for i, _ in items)
    H = sum(i.height + label_h for i, _ in items) + gap * (len(items) - 1)
    c = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(c)
    y = 0
    for im, lab in items:
        d.text((4, y + 4), lab, fill=(200, 0, 0))
        y += label_h
        c.paste(im, (0, y))
        y += im.height + gap
    c.save(path)
    print('saved', path, c.size)

def row(items, gap=16, label_h=26, path='crops/x.png'):
    W = sum(i.width for i, _ in items) + gap * (len(items) - 1)
    H = max(i.height for i, _ in items) + label_h
    c = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(c)
    x = 0
    for im, lab in items:
        d.text((x + 4, 4), lab, fill=(200, 0, 0))
        c.paste(im, (x, label_h))
        x += im.width + gap
    c.save(path)
    print('saved', path, c.size)

# 1. 字距：纯汉字整行（我方 p2 y448-499 / 全品 p05 y278-326）
stack([(load(M % 2).crop((249, 444, 1425, 505)), 'MINE  p2 L (23 chars/line, pitch 51px)'),
       (load(REF % 'p05').crop((243, 274, 1433, 335)), 'QUANPIN p05 L (21 chars/line, pitch 56.5px)')],
      path='crops/E1-字距.png')

# 2. 标点：含逗号/分号的句段（我方 p3 / 全品 p05）
stack([(load(M % 3).crop((249, 700, 1425, 790)), 'MINE  p3 (full-width punct, 35px void after)'),
       (load(REF % 'p05').crop((243, 630, 1433, 720)), 'QUANPIN p05 (half-width punct, 16px both sides)')],
      path='crops/E2-标点.png')

# 3. 数学：ABCD-A1B1C1D1（已裁过，重裁同尺）
a = load(M % 5).crop((249, 1985, 880, 2060)).resize((1262, 150), Image.LANCZOS)
b = load(REF % 'p07').crop((1539, 1100, 2170, 1175)).resize((1262, 150), Image.LANCZOS)
stack([(a, 'MINE  p5: long minus + 0.70em subscript'),
       (b, 'QUANPIN p07: short hyphen + ~0.54em subscript')], path='crops/E3-数学.png')

# 3b. 分式
a2 = load(M % 7).crop((940, 2370, 1060, 2460)).resize((360, 270), Image.LANCZOS)
b2 = load(REF % 'p07').crop((1685, 2090, 1765, 2220)).resize((240, 390), Image.LANCZOS)
row([(a2, 'MINE 1/2 (h=61px)'), (b2, 'QUANPIN 1/3 (h=105px)')], path='crops/E3b-分式.png')

# 4. 图：立方体 vs 四面体（已有 cmp-fig.png，重命名+标注）
a3 = load(M % 5).crop((935, 1885, 1415, 2340))
b3 = load(REF % 'p07').crop((1700, 3320, 2400, 3920))
row([(a3, 'MINE p5 (labels 23px)'), (b3, 'QUANPIN p07 (labels 32px)')], path='crops/E4-图.png')

# 5. 页码块
a4 = load(M % 7).crop((2330, 3920, 2760, 4070))
b4 = load(REF % 'p06').crop((2540, 3890, 2977, 4040))
stack([(a4, 'MINE p7: number gray75, block stops at margin'),
       (b4, 'QUANPIN p06: number black bold, block bleeds to paper edge')], path='crops/E5-页码.png')

# 6. 栏线
a5 = load(M % 2).crop((1400, 800, 1580, 1400))
b5 = load(REF % 'p05').crop((1400, 800, 1580, 1400))
row([(a5, 'MINE rule gray153-170'), (b5, 'QUANPIN rule gray188')], path='crops/E6-栏线.png')

# 7. 版面整页对比
a6 = load(M % 2).resize((595, 842), Image.LANCZOS)
b6 = load(REF % 'p05').resize((595, 842), Image.LANCZOS)
row([(a6, 'MINE p2'), (b6, 'QUANPIN p05')], path='crops/E7-整页.png')

# 8. 行首标点
a7 = load(M % 2).crop((249, 520, 1425, 580))   # p2 y~107.9pt = 539.5px
b7 = load(REF % 'p05').crop((243, 700, 1433, 760))
stack([(a7, 'MINE p2: line starts with full-width comma (行首禁则违反)'),
       (b7, 'QUANPIN p05: no line-start punctuation in p04-p07')], path='crops/E8-行首.png')
