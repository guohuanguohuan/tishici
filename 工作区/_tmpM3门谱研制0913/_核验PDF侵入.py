# -*- coding: utf-8 -*-
"""调试4：直接量测旗行各 span 墨宽（只读）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pymupdf


def dump(pdf, pno_want, needle):
    doc = pymupdf.open(pdf)
    page = doc[pno_want - 1]
    d = page.get_text('rawdict')
    for b in d['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                t = ''.join(ch['c'] for ch in s['chars'])
                if t.strip() and (needle in t or 'D' in t[:2] or 'C' in t[:2]):
                    bb = s['bbox']
                    print(f'p{pno_want} [{t[:24]}] x0={bb[0]:.1f} x1={bb[2]:.1f} 宽={bb[2]-bb[0]:.1f}pt')
    doc.close()


base = r'C:/提示词/工作区/M2-第1章量产0911/成卷'
dump(base + r'/导学件/课时06/main.pdf', 4, '既不充分')
print('---')
dump(base + r'/装配/练习本/拓展册-下册/main.pdf', 12, '60°')
