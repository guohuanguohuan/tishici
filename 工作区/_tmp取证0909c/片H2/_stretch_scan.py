# -*- coding: utf-8 -*-
"""片H2 拉伸异常行快扫（口径＝_测v4断言.py 第1860-1910行，逐字节同法）。"""
import sys
import numpy as np
import pymupdf as fitz


def cjk(ch):
    o = ord(ch[0]) if ch else 0
    return any(a <= o <= b for a, b in ((0x2E80, 0x2EFF), (0x3000, 0x303F), (0x3041, 0x30FF),
                                        (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF),
                                        (0xFE30, 0xFE4F), (0xFF00, 0xFFEF)))


SKIPCH = set('\u20d7\u20d6\u20d0\u20d1\u20e1\u0338\u00a0\u2060')


def scan(path):
    doc = fitz.open(path)
    rows = []
    for pno in range(len(doc)):
        pg = doc[pno]
        pix = pg.get_pixmap(dpi=400)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n >= 3:
            img = img[:, :, :3].mean(axis=2).astype(np.uint8)
        chars = []
        for b in pg.get_text('rawdict')['blocks']:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                for sp in l['spans']:
                    for c in sp['chars']:
                        bb = c['bbox']
                        if c['c'] in SKIPCH or not c['c'].strip() or bb[2] - bb[0] <= 0.05:
                            continue
                        chars.append((round(l['bbox'][1], 1), bb[0], c['c'], bb, sp['size']))
        chars.sort(key=lambda x: (x[0], x[1]))
        grp = []
        for c in chars:
            if grp and abs(c[0] - grp[-1][0]) < 1.2:
                grp[-1][1].append(c)
            else:
                grp.append((c[0], [c]))
        for gy, cs in grp:
            cs.sort(key=lambda x: x[1])
            for i in range(len(cs) - 1):
                a, b2 = cs[i], cs[i + 1]
                gap = b2[3][0] - a[3][2]
                if gap <= 0.5 * a[4] or not (cjk(a[2]) and cjk(b2[2])):
                    continue
                px0 = int(a[3][2] * 400 / 72); px1 = int(np.ceil(b2[3][0] * 400 / 72))
                py0 = int((min(a[3][1], b2[3][1]) - 0.6) * 400 / 72)
                py1 = int(np.ceil((max(a[3][3], b2[3][3]) + 0.6) * 400 / 72))
                px0 = max(0, px0); py0 = max(0, py0)
                px1 = min(pix.width, px1); py1 = min(pix.height, py1)
                if px1 > px0 and py1 > py0 and (img[py0:py1, px0:px1] < 160).any():
                    continue
                ratio = gap / a[4]
                if 0.9 <= ratio <= 1.1 or 1.9 <= ratio <= 2.1:
                    continue
                rows.append((pno + 1, gy, a[2], b2[2], round(gap, 2)))
    return rows


if __name__ == '__main__':
    for p in sys.argv[1:]:
        rows = scan(p)
        print(f'== {p.split("/")[-1]}: {len(rows)} 处')
        for r in rows[:20]:
            print(f'   p{r[0]} y{r[1]} {r[2]}|{r[3]} {r[4]}pt')
