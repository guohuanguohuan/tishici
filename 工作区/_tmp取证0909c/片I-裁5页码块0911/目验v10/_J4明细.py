# -*- coding: utf-8 -*-
"""J4 明细（v10-B 拉伸副作用登记用）：按「视觉行」聚合 CJK-CJK 超阈隙，报行宽均摊与最大孔。
判据同 check.py J4：相邻 CJK 字符墨隙 > 0.5×字号。"""
import io
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
MM2PT = 72 / 25.4


def is_cjk(ch):
    o = ord(ch)
    return 0x3000 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or 0x2018 <= o <= 0x201D


def run(pdf, pages, tag):
    doc = pymupdf.open(pdf)
    print(f'== {tag} {pdf}')
    for i in pages:
        page = doc[i - 1]
        for b in page.get_text('rawdict')['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                for sp in l['spans']:
                    chars = sp['chars']
                    txt = ''.join(c['c'] for c in chars)
                    hits = []
                    for a, c in zip(chars, chars[1:]):
                        if not (a['c'].strip() and c['c'].strip()):
                            continue
                        if is_cjk(a['c']) and is_cjk(c['c']):
                            gap = (c['bbox'][0] - a['bbox'][2]) * MM2PT
                            if gap > 0.5 * sp['size']:
                                hits.append((round(gap, 2), a['c'], c['c']))
                    if hits:
                        w = (l['bbox'][2] - l['bbox'][0]) * MM2PT
                        print(f'  p{i} 行宽{w:5.1f}mm 字号{sp["size"]:.2f} 孔{len(hits)}处 '
                              f'最大{max(h[0] for h in hits):.2f}pt 列{[h[0] for h in hits][:12]} |{txt[:34]}|')
    doc.close()


if __name__ == '__main__':
    run(r'C:\提示词\工作区\字替对照-0909\导学件答案册-v1\main.pdf', [1, 2, 3, 4], 'v10册v1')
    run(r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf', [7, 8, 9, 10], 'v9册v1')
    run(r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\答案册\main.pdf', [1, 2], 'v10样张')
    run(r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf', [13, 14], 'v9样张')
