# -*- coding: utf-8 -*-
r"""探_拉伸行.py —— 行内拉伸异常扫描（片F #41 证据源）
口径：逐页取 rawdict，行内按 x 排序相邻字符对，gap = x0[i+1] − x1[i]；
      凡 gap > 0.5em（em = 该对左侧字符 size，正文 10.05pt → 5.03pt；题侧/标签行按各自 size）
      且左侧字符为 CJK（U+3000-9FFF/F900-FAFF/全角标点）→ 记一处「空档」；
      含空档的行 = 拉伸异常行。矢量箭头组合符（U+20D7 等）与零宽字符跳过。
用法：python 探_拉伸行.py <pdf> [--json out.json] [--csv out.csv]
"""
import sys
import json
import unicodedata

import pymupdf

CJK_RANGES = [
    (0x2E80, 0x2EFF), (0x3000, 0x303F), (0x3041, 0x30FF), (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0xFE30, 0xFE4F), (0xFF00, 0xFFEF),
]
SKIP_CHARS = set('\u20d7\u20d6\u20d0\u20d1\u20e1\u0338\u00a0')


def is_cjk(ch):
    if not ch:
        return False
    o = ord(ch[0])
    return any(a <= o <= b for a, b in CJK_RANGES)


def line_chars(l):
    out = []
    for sp in l['spans']:
        for c in sp['chars']:
            ch = c['c']
            if ch in SKIP_CHARS:
                continue
            if not ch.strip():
                continue
            bb = c['bbox']
            if bb[2] - bb[0] <= 0.05:   # 零宽（组合符残留）
                continue
            out.append({'c': ch, 'bbox': bb, 'font': sp['font'], 'size': sp['size']})
    return out


def scan(path, thresh_em=0.5):
    doc = pymupdf.open(path)
    rows = []
    for pno in range(len(doc)):
        d = doc[pno].get_text('rawdict')
        for b in d['blocks']:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                chars = sorted(line_chars(l), key=lambda x: x['bbox'][0])
                if len(chars) < 2:
                    continue
                txt = ''.join(c['c'] for c in chars)
                gaps = []
                for i in range(len(chars) - 1):
                    a, bb = chars[i], chars[i + 1]
                    gap = bb['bbox'][0] - a['bbox'][2]
                    lim = thresh_em * a['size']
                    if gap > lim and (is_cjk(a['c']) or is_cjk(bb['c'])):
                        gaps.append({
                            'left': a['c'], 'right': bb['c'],
                            'gap': round(gap, 2), 'lim': round(lim, 2),
                            'x': round(a['bbox'][2], 1),
                            'y': round(a['bbox'][1], 1),
                            'lf': a['font'], 'rf': bb['font'],
                            'lsz': round(a['size'], 2), 'rsz': round(bb['size'], 2),
                        })
                if gaps:
                    rows.append({
                        'page': pno + 1,
                        'y': round(l['bbox'][1], 1),
                        'x0': round(l['bbox'][0], 1),
                        'text': txt,
                        'gaps': gaps,
                        'n': len(gaps),
                    })
    return rows


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'main.pdf'
    rows = scan(path)
    print(f'文件：{path}')
    print(f'拉伸异常行 = {len(rows)}（空档总数 {sum(r["n"] for r in rows)}）')
    for r in rows:
        print(f'  p{r["page"]} y={r["y"]} x0={r["x0"]} 空档×{r["n"]}  {r["text"][:56]!r}')
        for g in r['gaps']:
            print(f'      {g["left"]!r}→{g["right"]!r} gap={g["gap"]}pt (限{g["lim"]}) '
                  f'{g["lf"][:18]} {g["lsz"]}→{g["rf"][:18]} {g["rsz"]} @x={g["x"]}')
    for i, a in enumerate(sys.argv):
        if a == '--json':
            json.dump(rows, open(sys.argv[i + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('json →', sys.argv[i + 1])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
