# -*- coding: utf-8 -*-
r"""片H1 · 标点 ink 空档精测（rawdict origin 切分，绝无邻字渗入）
对 PDF：找「CJK ＋ 标点 ＋CJK」三元组，按 origin 中点切三格渲染 600dpi，
量 标点前墨隙（前字 ink 右缘→标点 ink 左缘）与 后墨隙（标点 ink 右缘→后字 ink 左缘）。
用法：python 量_标点.py <pdf> [--json out.json]"""
import sys
import json
import statistics as st

import pymupdf
from PIL import Image

DPI = 600
PXPT = DPI / 72.0
PTMM = 72 / 25.4
THR = 128
PUNCTS = '，、；：'


def ink_extent(doc, pno, x0, x1, y0, y1):
    if x1 - x0 < 1:
        return None
    clip = pymupdf.Rect(x0, y0, x1, y1)
    pix = doc[pno - 1].get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    g = im.point(lambda v: 255 if v < THR else 0)
    b = g.getbbox()
    if b is None:
        return None
    return (clip.x0 + b[0] / PXPT, clip.x0 + b[2] / PXPT)


def scan(path):
    doc = pymupdf.open(path)
    rows = []
    for pno in range(1, len(doc) + 1):
        d = doc[pno - 1].get_text('rawdict')
        for b in d['blocks']:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                chars = []
                for sp in l['spans']:
                    for c in sp['chars']:
                        chars.append((c['c'], c['bbox'], c['origin'][0], c['origin'][1], sp['size']))
                chars.sort(key=lambda r: r[2])
                for i in range(1, len(chars) - 1):
                    cL, c, cR = chars[i - 1], chars[i], chars[i + 1]
                    if c[0] not in PUNCTS:
                        continue
                    if not (0x4E00 <= ord(cL[0]) <= 0x9FFF and 0x4E00 <= ord(cR[0]) <= 0x9FFF):
                        continue
                    if abs(cL[3] - c[3]) > 1.5 or abs(cR[3] - c[3]) > 1.5:
                        continue
                    xa = (cL[2] + c[2]) / 2
                    xb = (c[2] + cR[2]) / 2
                    y0 = min(cL[1][1], c[1][1], cR[1][1]) - 1
                    y1 = max(cL[1][3], c[1][3], cR[1][3]) + 1
                    iL = ink_extent(doc, pno, cL[2] - 1, xa, y0, y1)
                    iC = ink_extent(doc, pno, xa, xb, y0, y1)
                    iR = ink_extent(doc, pno, xb, cR[2] + cR[1][2] - cR[1][0] + 1, y0, y1)
                    if not (iL and iC and iR):
                        continue
                    rows.append({'page': pno, 'y': round(c[3], 1), 'punct': c[0],
                                 'trio': cL[0] + c[0] + cR[0],
                                 'before_mm': round((iC[0] - iL[1]) / PTMM, 3),
                                 'after_mm': round((iR[0] - iC[1]) / PTMM, 3),
                                 'before_px360': round((iC[0] - iL[1]) / PTMM * 14.176, 1),
                                 'after_px360': round((iR[0] - iC[1]) / PTMM * 14.176, 1)})
    return rows


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'main.pdf'
    rows = scan(path)
    b_ = [r['before_mm'] for r in rows]
    a_ = [r['after_mm'] for r in rows]
    print(f'n={len(rows)}')
    if rows:
        print('前墨隙 mm: med=%.3f p10=%.3f p90=%.3f | px360 med=%.1f p10=%.1f p90=%.1f' % (
            st.median(b_), sorted(b_)[len(b_) // 10], sorted(b_)[9 * len(b_) // 10],
            st.median(b_) * 14.176, sorted(b_)[len(b_) // 10] * 14.176, sorted(b_)[9 * len(b_) // 10] * 14.176))
        print('后墨隙 mm: med=%.3f p10=%.3f p90=%.3f | px360 med=%.1f p10=%.1f p90=%.1f' % (
            st.median(a_), sorted(a_)[len(a_) // 10], sorted(a_)[9 * len(a_) // 10],
            st.median(a_) * 14.176, sorted(a_)[len(a_) // 10] * 14.176, sorted(a_)[9 * len(a_) // 10] * 14.176))
        for r in rows[:24]:
            print(' ', r)
    for i, a in enumerate(sys.argv):
        if a == '--json':
            json.dump(rows, open(sys.argv[i + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('json →', sys.argv[i + 1])
