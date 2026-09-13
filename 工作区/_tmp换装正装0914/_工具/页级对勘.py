# -*- coding: utf-8 -*-
r"""页级对勘.py — 正装波1 件级页级对勘（试迁报告§五同法）：原印面（迁移前基线 main.pdf）
↔ 换装双档（main-true/pure.pdf）。
  ①文字段强归一（剥全部空白）多重集Containment：原件段在 true/pure 中的缺失数＋样本；
  ②页数三方；
  ③p1 渲染 PNG md5 三方对照（逐字节同＝版面同）。
用法: python 页级对勘.py   # 全 12 件，stdout 读数
"""
import hashlib, io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.join(HERE, '..', 'M2导学本')
norm = lambda s: re.sub(r'\s+', '', s)


def lines_of(f):
    doc = pymupdf.open(f)
    n = doc.page_count
    ls = [norm(x) for pg in doc for x in pg.get_text().split('\n')]
    return n, Counter(x for x in ls if x)


def png_md5(f, page=0, zoom=2.0):
    doc = pymupdf.open(f)
    pix = doc[page].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return hashlib.md5(pix.tobytes('png')).hexdigest()


def miss(base, tgt):
    c = Counter(base)
    c.subtract(tgt)
    return sum(v for v in c.values() if v > 0), [k for k, v in c.items() if v > 0]


def main():
    for piece in sorted(os.listdir(TREE)):
        d = os.path.join(TREE, piece)
        if not os.path.isdir(d):
            continue
        f0, ft, fp = (os.path.join(d, x) for x in ('main.pdf', 'main-true.pdf', 'main-pure.pdf'))
        n0, L0 = lines_of(f0)
        nt, Lt = lines_of(ft)
        np_, Lp = lines_of(fp)
        mt, st = miss(L0, Lt)
        mp_, sp = miss(L0, Lp)
        m0, m1, m2 = (png_md5(x) for x in (f0, ft, fp))
        print('[%s] 页 %d→true %d/pure %d' % (piece, n0, nt, np_))
        print('  true 缺原段 %d/%d %s' % (mt, sum(L0.values()), ('样本: ' + ' ¦ '.join(st[:5])) if st else ''))
        print('  pure 缺原段 %d/%d %s' % (mp_, sum(L0.values()), ('样本: ' + ' ¦ '.join(sp[:5])) if sp else ''))
        print('  p1 md5 原 %s｜true %s｜pure %s' % (m0[:8], m1[:8], m2[:8]))


if __name__ == '__main__':
    main()
