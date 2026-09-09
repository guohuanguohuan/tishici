# -*- coding: utf-8 -*-
r"""复审计·片B 独立重测（二）：表格净空（600dpi）
对象：表1（p1 右栏 名称/定义/表示）、表2（p2 左栏 运算/法则要点/运算律举例）
量：表头行高（顶线→次线）、多行格每行「行级最紧侧」顶/底净空（墨缘→线墨缘）
方法：自检横线（行内暗像素占表宽 >0.9）＋竖线（列内暗像素占表高 >0.9）→ 网格；
     每格墨带取 600dpi gray<128；净空＝线墨底缘→墨顶（顶侧）、墨底→线墨顶缘（底侧）。
"""
import json
import os

import numpy as np
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
DPI = 600
PT = 72 / 25.4
MMPP = 25.4 / DPI  # mm per pixel


def render(page):
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)


def rules_h(mask, x0, x1, minfrac=0.9):
    seg = mask[:, x0:x1]
    frac = seg.mean(axis=1)
    rows = np.where(frac > minfrac)[0]
    groups = []
    for r in rows:
        if groups and r - groups[-1][-1] <= 2:
            groups[-1].append(r)
        else:
            groups.append([r])
    return [(g[0], g[-1]) for g in groups]


def rules_v(mask, y0, y1, minfrac=0.9):
    seg = mask[y0:y1, :]
    frac = seg.mean(axis=0)
    cols = np.where(frac > minfrac)[0]
    groups = []
    for c in cols:
        if groups and c - groups[-1][-1] <= 2:
            groups[-1].append(c)
        else:
            groups.append([c])
    return [(g[0], g[-1]) for g in groups]


def measure_table(page, xmm0, xmm1, ymm0, ymm1, name):
    img = render(page)
    px = lambda mm: int(round(mm * DPI / 25.4))
    x0, x1 = px(xmm0), px(xmm1)
    y0, y1 = px(ymm0), px(ymm1)
    mask = img[y0:y1, x0:x1] < 128
    hrs = rules_h(mask, 5, mask.shape[1] - 5)
    vrs = rules_v(mask, 5, mask.shape[0] - 5)
    print(f'--- {name}: 横线 {len(hrs)} 条 -> ' + ', '.join(f'{(y0+a)*MMPP:.2f}-{(y0+b)*MMPP:.2f}' for a, b in hrs))
    print(f'    竖线 {len(vrs)} 条 -> ' + ', '.join(f'{(x0+a)*MMPP:.1f}' for a, b in vrs))
    out = dict(hrs=[(round((y0 + a) * MMPP, 3), round((y0 + b) * MMPP, 3)) for a, b in hrs],
               vrs=[(round((x0 + a) * MMPP, 2), round((x0 + b) * MMPP, 2)) for a, b in vrs],
               header_h=None, rows=[])
    if len(hrs) >= 2:
        out['header_h'] = round((hrs[1][0] - hrs[0][1]) * MMPP, 2)
        print(f'    表头行高（顶线墨底→次线墨顶）={out["header_h"]}mm；'
              f'线心距={round((sum(hrs[1])/2-sum(hrs[0])/2)*MMPP,2)}mm')
    # 逐数据行（横线之间）
    for ri in range(1, len(hrs) - 1):
        rtop = hrs[ri][1] + 3      # 上行线墨底缘（px，+3px 避 AA）
        rbot = hrs[ri + 1][0] - 2  # 下行线墨顶缘（px，−2px 避 AA）
        # 列切分（竖线之间；两侧各退 4px 以避开竖线 AA 边缘）
        cols = [(0, mask.shape[1])]
        if len(vrs) >= 2:
            cols = []
            for vi in range(len(vrs) - 1):
                cols.append((vrs[vi][1] + 4, vrs[vi + 1][0] - 4))
        cells = []
        for (c0, c1) in cols:
            if c1 - c0 < 8:
                continue
            sub = mask[rtop + 1:rbot, c0:c1]
            rows = np.where(sub.any(axis=1))[0]
            if len(rows) == 0:
                continue
            # 行带数（折数）
            bands = 0
            prev = -9
            for r in rows:
                if r - prev > 4:
                    bands += 1
                prev = r
            top_clear = (rows.min() + 1) * MMPP
            bot_clear = (rbot - rtop - 1 - rows.max()) * MMPP
            cells.append(dict(bands=bands, top=round(top_clear, 2), bottom=round(bot_clear, 2)))
        if not cells:
            continue
        row = dict(idx=ri, y_top=round((y0 + rtop) * MMPP, 2),
                   max_bands=max(c['bands'] for c in cells),
                   top_min=min(c['top'] for c in cells),
                   bottom_min=min(c['bottom'] for c in cells),
                   cells=cells)
        out['rows'].append(row)
        tag = '多行' if row['max_bands'] >= 2 else '单行'
        print(f"    行{ri}（{tag}，最多{row['max_bands']}折）顶净空min={row['top_min']} 底净空min={row['bottom_min']} ｜ 各格 {cells}")
    return out


doc = pymupdf.open(PDF)
res = {}
res['表1_p1右'] = measure_table(doc[0], 108.5, 193.5, 100.0, 200.0, '表1 p1右（名称/定义/表示）')
res['表2_p2左'] = measure_table(doc[1], 16.5, 101.5, 108.0, 185.0, '表2 p2左（运算/法则要点/运算律举例）')

# 汇总多行格窗
tops, bots = [], []
for t in res.values():
    for r in t['rows']:
        if r['max_bands'] >= 2:
            tops.append(r['top_min']); bots.append(r['bottom_min'])
print(f"\n=== 多行格行级最紧侧汇总 ===\n顶净空 {min(tops)}–{max(tops)}mm（n={len(tops)}）；底净空 {min(bots)}–{max(bots)}mm")
print('表头行高：', {k: v['header_h'] for k, v in res.items()})
with open(os.path.join(BASE, 'm_片B_表_result.json'), 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print('saved m_片B_表_result.json')
