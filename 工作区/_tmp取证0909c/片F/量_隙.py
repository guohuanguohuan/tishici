# -*- coding: utf-8 -*-
r"""量_隙.py v3 —— 片F 逐处墨隙实测（600dpi 逐字 ink 口径）
①判断题序号「(N)」后隙：')' 墨右缘 → 题干首字墨左缘（筛法：序号在栏左＋题干首字 ∈ {两,相,若}）
②条目号「N.」后隙：'.' 墨右缘 → 内容首字墨左缘
③=/∥ 墨隙：全部 '=' 字符逐处（左右墨隙分布）＋ ∥ 自绘（get_drawings 双杠对）逐处
用法：python 量_隙.py <pdf> [--json out.json]
"""
import sys
import json
import statistics as st

import pymupdf
from PIL import Image

DPI = 600
PXPT = DPI / 72.0
PTMM = 72 / 25.4
THR = 128
COLL = (49.79, 308.27)
ZHENTI_BODY = set('两相若')


def char_ink(doc, pno, bb, padx=2.0, pady=1.0):
    clip = pymupdf.Rect(bb[0] - padx, bb[1] - pady, bb[2] + padx, bb[3] + pady)
    page = doc[pno - 1]
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    g = im.point(lambda v: 255 if v < THR else 0)
    b = g.getbbox()
    if b is None:
        return None
    return (clip.x0 + b[0] / PXPT, clip.x0 + b[2] / PXPT)


def page_chars(doc, pno):
    out = []
    d = doc[pno - 1].get_text('rawdict')
    for blk in d['blocks']:
        if blk['type'] != 0:
            continue
        for l in blk['lines']:
            for sp in l['spans']:
                for c in sp['chars']:
                    out.append({'c': c['c'], 'bbox': c['bbox'], 'font': sp['font'],
                                'size': sp['size'], 'y': l['bbox'][1]})
    return out


def next_char(chars, anchor):
    cands = [c for c in chars if abs(c['y'] - anchor['y']) < 1.6
             and c['bbox'][0] > anchor['bbox'][2] - 0.6 and c['c'].strip()]
    cands.sort(key=lambda c: c['bbox'][0])
    return cands[0] if cands else None


def prev_char(chars, anchor):
    cands = [c for c in chars if abs(c['y'] - anchor['y']) < 1.6
             and c['bbox'][2] < anchor['bbox'][0] + 0.6 and c['c'].strip()]
    cands.sort(key=lambda c: -c['bbox'][2])
    return cands[0] if cands else None


def gap_between(doc, pno, a, b):
    ia = char_ink(doc, pno, a['bbox'])
    ib = char_ink(doc, pno, b['bbox'])
    if ia is None or ib is None:
        return None
    return {'gap_pt': round(ib[0] - ia[1], 3), 'gap_mm': round((ib[0] - ia[1]) / PTMM, 3),
            'adv_pt': round(b['bbox'][0] - a['bbox'][2], 3),
            'a_ink_x1': round(ia[1], 2), 'b_ink_x0': round(ib[0], 2),
            'a_bbox': [round(x, 2) for x in a['bbox']],
            'b_bbox': [round(x, 2) for x in b['bbox']]}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'main.pdf'
    doc = pymupdf.open(path)
    out = {'zhenti': [], 'tiaomu': [], 'eq': [], 'par': []}

    for pno in range(1, len(doc) + 1):
        chars = page_chars(doc, pno)

        for c in chars:
            if c['c'] != '(':
                continue
            if min(abs(c['bbox'][0] - x) for x in COLL) > 3.0:
                continue
            nxt = next_char(chars, c)
            if nxt is None or not nxt['c'].isdigit():
                continue
            rp = next_char(chars, nxt)
            if rp is None or rp['c'] != ')':
                continue
            body = next_char(chars, rp)
            if body is None or body['c'] not in ZHENTI_BODY:
                continue
            g = gap_between(doc, pno, rp, body)
            if g:
                g.update({'page': pno, 'y': round(c['y'], 1), 'num': nxt['c'], 'body': body['c']})
                out['zhenti'].append(g)

        for c in chars:
            if not c['c'].isdigit():
                continue
            if min(abs(c['bbox'][0] - x) for x in COLL) > 3.0:
                continue
            dot = next_char(chars, c)
            if dot is None or dot['c'] != '.':
                continue
            body = next_char(chars, dot)
            if body is None:
                continue
            g = gap_between(doc, pno, dot, body)
            if g:
                g.update({'page': pno, 'y': round(c['y'], 1), 'num': c['c'], 'body': body['c']})
                out['tiaomu'].append(g)

        # '=' 逐处（正文，排除表格线区；取同 line y 容差内邻字）
        for c in chars:
            if c['c'] != '=':
                continue
            L, R = prev_char(chars, c), next_char(chars, c)
            if L is None or R is None:
                continue
            ie = char_ink(doc, pno, c['bbox'])
            il, ir = char_ink(doc, pno, L['bbox']), char_ink(doc, pno, R['bbox'])
            if not (ie and il and ir):
                continue
            out['eq'].append({'page': pno, 'y': round(c['y'], 1),
                              'left_mm': round((ie[0] - il[1]) / PTMM, 3),
                              'right_mm': round((ir[0] - ie[1]) / PTMM, 3),
                              'L': L['c'], 'R': R['c']})

    # ∥ 自绘：双杠对（每根 ~5.3×9.8pt，fill 黑），合并为墨盒
    for pno in range(1, len(doc) + 1):
        drs = [d for d in doc[pno - 1].get_drawings()
               if 4.5 < d['rect'].width < 6.5 and 9.0 < d['rect'].height < 11.0
               and d.get('fill') == (0.0, 0.0, 0.0)]
        used = set()
        for i, a in enumerate(drs):
            if i in used:
                continue
            for j, b in enumerate(drs):
                if j <= i or j in used:
                    continue
                ra, rb = a['rect'], b['rect']
                if abs(ra.y0 - rb.y0) < 0.6 and abs(ra.y1 - rb.y1) < 0.6 and abs(ra.x0 - rb.x0) < 3.0:
                    used.add(i); used.add(j)
                    box = pymupdf.Rect(min(ra.x0, rb.x0), ra.y0, max(ra.x1, rb.x1), ra.y1)
                    chars = page_chars(doc, pno)
                    L = None; R = None
                    for c in chars:
                        cy = (c['bbox'][1] + c['bbox'][3]) / 2
                        if not (box.y0 - 2 <= cy <= box.y1 + 2):
                            continue
                        if c['bbox'][2] <= box.x0 + 0.5:
                            if L is None or c['bbox'][2] > L['bbox'][2]:
                                L = c
                        if c['bbox'][0] >= box.x1 - 0.5:
                            if R is None or c['bbox'][0] < R['bbox'][0]:
                                R = c
                    il = char_ink(doc, pno, L['bbox']) if L else None
                    ir = char_ink(doc, pno, R['bbox']) if R else None
                    out['par'].append({'page': pno, 'y': round(box.y0, 1),
                                       'box': [round(v, 2) for v in box],
                                       'left_mm': round((box.x0 - il[1]) / PTMM, 3) if il else None,
                                       'right_mm': round((ir[0] - box.x1) / PTMM, 3) if ir else None,
                                       'L': L['c'] if L else None, 'R': R['c'] if R else None})
                    break

    print(json.dumps(out, ensure_ascii=False, indent=1))
    for i, a in enumerate(sys.argv):
        if a == '--json':
            json.dump(out, open(sys.argv[i + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('json →', sys.argv[i + 1])
    # 汇总
    def stat(rows, key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return f'n={len(vals)} min={min(vals):.3f} med={st.median(vals):.3f} max={max(vals):.3f}' if vals else 'n=0'
    print('--- 汇总 ---')
    print('判断题序号后隙 mm:', stat(out['zhenti'], 'gap_mm'))
    print('条目号后隙 mm:', stat(out['tiaomu'], 'gap_mm'))
    print('= 左墨隙 mm:', stat(out['eq'], 'left_mm'), '| 右墨隙 mm:', stat(out['eq'], 'right_mm'))
    print('∥ 左墨隙 mm:', stat(out['par'], 'left_mm'), '| 右墨隙 mm:', stat(out['par'], 'right_mm'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
