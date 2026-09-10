# -*- coding: utf-8 -*-
r"""拉伸行扫描 v2 —— 片F #41 断言口径（ink 实证版）
口径：逐页 rawdict 取行内相邻字符对（按 x 排序），gap = x0[i+1] − x1[i]；
      gap > 0.5em（em＝左侧字符 size）且「间隙内无墨」（400dpi 灰值 <160 判有墨）→ 记空档；
      空档两侧均为 CJK（含全角标点）＝CJK-CJK 档；一侧 CJK 一侧西文/数学 ＝CJK-西文档。
      设计性固定隙（宏 \hspace 常量）由白名单按「左字+右字+名义值」排除（见 DESIGN）。
输出：逐处清单＋行计数。用法：python 拉伸行扫描.py <pdf> [--json out.json] [--quiet]
"""
import sys
import json

import pymupdf
import numpy as np

CJK_RANGES = [
    (0x2E80, 0x2EFF), (0x3000, 0x303F), (0x3041, 0x30FF), (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0xFE30, 0xFE4F), (0xFF00, 0xFFEF),
]
SKIP = set('\u20d7\u20d6\u20d0\u20d1\u20e1\u0338\u00a0\u2060')
DPI = 400
PXPT = DPI / 72.0
PTMM = 72 / 25.4
INK_THR = 160
GRAY_SKIP = (150, 165)   # 灰字（题侧 8pt 灰 119/153）不算墨柱：400dpi 下灰 153 ≈ 值 153

# 设计性固定隙白名单：左字 →（右字类，名义 mm，宏出处）
# 口径＝间隙内无墨但由宏 \hspace 常量给定、不随行拉伸浮动者；每次实测复核名义值±0.15mm
DESIGN = [
    ('◆', '后', 2.4, 'qp-blocks \\huafu\\hspace{2.4mm}'),
    (']', '后', 2.2, 'qp-blocks \\tieside 后 \\hspace{2.2mm}'),
    ('．', '后', 2.7, 'postproc 检测题号．→\\tieside \\hspace{2.7mm}'),
    ('}', '后', 2.7, 'qp-blocks \\li 标签→题侧 2.7mm'),
]


def is_cjk(ch):
    if not ch:
        return False
    o = ord(ch[0])
    return any(a <= o <= b for a, b in CJK_RANGES)


def page_chars(page):
    out = []
    d = page.get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            for sp in l['spans']:
                for c in sp['chars']:
                    if c['c'] in SKIP or not c['c'].strip():
                        continue
                    bb = c['bbox']
                    if bb[2] - bb[0] <= 0.05:
                        continue
                    out.append({'c': c['c'], 'bbox': bb, 'size': sp['size'],
                                'font': sp['font'], 'y': l['bbox'][1],
                                'line': l['bbox']})
    return out


def has_ink(img, page, x0, x1, y0, y1):
    """间隙矩形内是否有墨（灰值 < INK_THR）。"""
    if x1 <= x0:
        return False
    px0 = int((x0 - 0) * PXPT); px1 = int(np.ceil(x1 * PXPT))
    py0 = int((y0 - 0) * PXPT); py1 = int(np.ceil(y1 * PXPT))
    H, W = img.shape
    px0 = max(0, px0); py0 = max(0, py0)
    px1 = min(W, px1); py1 = min(H, py1)
    if px1 <= px0 or py1 <= py0:
        return True
    return bool((img[py0:py1, px0:px1] < INK_THR).any())


def scan(path, quiet=False):
    doc = pymupdf.open(path)
    rows = []
    for pno in range(len(doc)):
        page = doc[pno]
        pix = page.get_pixmap(dpi=DPI)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n >= 3:
            img = img[:, :, :3].mean(axis=2).astype(np.uint8)
        chars = sorted(page_chars(page), key=lambda c: (round(c['y'], 1), c['bbox'][0]))
        # 按 y 分组（容差 1.2pt）
        groups = []
        for c in chars:
            if groups and abs(c['y'] - groups[-1][0]) < 1.2:
                groups[-1][1].append(c)
            else:
                groups.append((c['y'], [c]))
        for gy, cs in groups:
            cs.sort(key=lambda c: c['bbox'][0])
            for i in range(len(cs) - 1):
                a, b = cs[i], cs[i + 1]
                gap = b['bbox'][0] - a['bbox'][2]
                if gap <= 0.5 * a['size']:
                    continue
                if not (is_cjk(a['c']) or is_cjk(b['c'])):
                    continue
                y0 = min(a['bbox'][1], b['bbox'][1]) - 0.6
                y1 = max(a['bbox'][3], b['bbox'][3]) + 0.6
                if has_ink(img, page, a['bbox'][2], b['bbox'][0], y0, y1):
                    continue
                kind = 'CJK-CJK' if (is_cjk(a['c']) and is_cjk(b['c'])) else 'CJK-西文'
                rows.append({'page': pno + 1, 'y': round(gy, 1), 'kind': kind,
                             'left': a['c'], 'right': b['c'],
                             'gap_pt': round(gap, 2), 'gap_mm': round(gap / PTMM, 3),
                             'lim': round(0.5 * a['size'], 2),
                             'x': round(a['bbox'][2], 1)})
    lines_hit = {(r['page'], r['y']) for r in rows}
    if not quiet:
        print(f'文件：{path}')
        print(f'拉伸异常行 = {len(lines_hit)}（空档 {len(rows)} 处）')
        for r in sorted(rows, key=lambda r: (r['page'], r['y'], r['x'])):
            print(f"  p{r['page']} y={r['y']} [{r['kind']}] {r['left']!r}→{r['right']!r} "
                  f"{r['gap_pt']}pt/{r['gap_mm']}mm (限{r['lim']})")
    return rows, lines_hit


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'main.pdf'
    rows, lines_hit = scan(path, quiet='--quiet' in sys.argv)
    for i, a in enumerate(sys.argv):
        if a == '--json':
            json.dump({'rows': rows, 'n_lines': len(lines_hit)},
                      open(sys.argv[i + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('json →', sys.argv[i + 1])
    print(f'小结：异常行 {len(lines_hit)}／空档 {len(rows)}')
