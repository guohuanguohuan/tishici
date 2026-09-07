# -*- coding: utf-8 -*-
"""E 补测（独立复测代理，只验证不改）：
导学件 p1 两个块起点的毫米实测：「版心顶→学习目标块起点」「版心顶→课前预习块起点（首内容块起点）」。
口径双报：a) 文字行 bbox 顶；b) 花形 tcbox 框顶缘（与目标文字行 y 区间相交、且宽≥2mm 的 drawing 最小 y0；
宽<2mm 的竖直装饰线不计——v3 p1 存在跨 83→283mm 的竖线，会污染框顶缘）。
对象：v4/v3 导学件 main.pdf 第 1 页；版心顶＝15mm=42.52pt（两件 geometry margin 均 15mm）。
v3 对账载值（导学件对照.md）：标签顶 83.7mm、花形行顶 156.0mm（页面坐标）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

PT = 72 / 25.4
TOP = 15 * PT
BASE = 'C:/提示词/工作区/全品结构提取/数学选必一'
DOCS = [('v4', BASE + '/样张v4/导学件/main.pdf'), ('v3', BASE + '/样张v3/导学件/main.pdf')]
MARKS = [('学习目标', '【学习目标】'), ('课前预习', '课前预习'), ('知识点一', '知识点一')]

for tag, path in DOCS:
    doc = pymupdf.open(path)
    page = doc[0]
    lines = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans'])
            lines.append((t.strip(), ln['bbox']))
    draws = [d['rect'] for d in page.get_drawings()]
    wide = [r for r in draws if r.width >= 2 * PT]
    print('=' * 16, tag, '导学件 p1', '=' * 16)
    for key, sub in MARKS:
        hit = [(t, bb) for t, bb in lines if sub in t]
        if not hit:
            print(key + ': 未找到'); continue
        t, bb = hit[0]
        y0 = bb[1]
        print(f'{key} 文字顶「{t[:22]}」: 页面y={y0/PT:6.1f}mm  版心顶起={(y0-TOP)/PT:6.1f}mm')
        inter = [r for r in wide if r.y0 <= bb[3] and r.y1 >= bb[1]]
        if inter:
            inter.sort(key=lambda r: r.y0)
            for r in inter[:4]:
                print(f'    相交横向drawing: 框顶缘y={r.y0/PT:6.2f}mm(版心顶起{(r.y0-TOP)/PT:5.2f}) '
                      f'底y={r.y1/PT:6.2f}mm 宽={r.width/PT:5.1f}mm x0={r.x0/PT:5.1f}mm')
        else:
            print('    相交横向drawing: 无（纯文字标签行，无框）')
    doc.close()
