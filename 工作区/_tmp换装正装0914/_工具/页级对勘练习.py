# -*- coding: utf-8 -*-
r"""页级对勘练习.py — 波2 件级页级对勘（试迁报告§四同法·波1 页级对勘.py 加强制断言版）。

对照面：原印面（迁移前基线 main.pdf，源自正件拷贝）↔ 换装双档（main-true/pure.pdf）。
断言（试迁口径＋波2 加强）：
  ①文字段强归一（剥全部空白）多重集：true 缺原段＝0（题面零漂移铁面）；
  ②pure 缺原段＝0 且 pure 新增段 ⊆ 尾块文本族（\tailfill 设计内新增，答案块全吞零印）；
  ③pure p1 渲染 PNG md5 ＝ 原 p1 md5（逐像素同＝版面零漂移最强证，试迁 false-p1≡orig-p1 同源）；
  ④页数三方读数。
用法: python 页级对勘练习.py   # 全 12 件，退出码 0/1
"""
import hashlib
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.join(HERE, '..', 'M2练习本')
PIECES = ['课时%02d' % i for i in range(1, 11)] + ['上册', '下册']
norm = lambda s: re.sub(r'\s+', '', s)
TAILFILL_TXT = ('笔记与错题整理', '课堂笔记', '错题重做', '疑问登记', '此处笔记')
FOOTER_TXT = ('第一章', '空间向量与立体几何', '拓展册（上）', '拓展册（下）', '练习件',
              '高中数学', '选择性必修第一册(人教B版)')


def is_page_artifact(s, cnt_diff, n0, np_):
    """页数差伪段：页码裸数（每页 1 个）或页脚丛名/件名族（每页 1 次，差＝页数差）。"""
    if re.fullmatch(r'\d{1,3}', s):
        return cnt_diff <= max(n0 - np_, 0) + 1 and cnt_diff <= 2
    return s in FOOTER_TXT and cnt_diff == max(n0 - np_, 1)


def lines_of(f):
    doc = pymupdf.open(f)
    ls = [norm(x) for pg in doc for x in pg.get_text().split('\n')]
    return doc.page_count, Counter(x for x in ls if x)


def png_md5(f, page=0, zoom=2.0):
    doc = pymupdf.open(f)
    pix = doc[page].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return hashlib.md5(pix.tobytes('png')).hexdigest()


def miss(base, tgt):
    c = Counter(base)
    c.subtract(tgt)
    return Counter({k: v for k, v in c.items() if v > 0})


def main():
    bad = 0
    for piece in PIECES:
        d = os.path.join(TREE, piece)
        f0, ft, fp = (os.path.join(d, x) for x in ('main.pdf', 'main-true.pdf', 'main-pure.pdf'))
        n0, L0 = lines_of(f0)
        nt, Lt = lines_of(ft)
        np_, Lp = lines_of(fp)
        mt, mpu = miss(L0, Lt), miss(L0, Lp)
        add_pu = miss(Lp, L0)
        m0, m1, m2 = png_md5(f0), png_md5(ft), png_md5(fp)
        reds = []
        if mt:
            reds.append('true 缺原段 %d/%d（题面漂移红）' % (sum(mt.values()), sum(L0.values())))
        art, real = [], {}
        for s, v in mpu.items():
            if is_page_artifact(s, v, n0, np_):
                art.append((s, v))
            else:
                real[s] = v
        if real:
            reds.append('pure 缺原段 %d/%d 样本 %s' % (sum(real.values()), sum(L0.values()),
                                                       ' ¦ '.join(list(real)[:4])))
        tail_tokens, art_add, real_add = 0, [], []
        for s, v in add_pu.items():
            if any(t in s for t in TAILFILL_TXT):
                tail_tokens += v
            elif re.fullmatch(r'\d{1,3}', s) or s in FOOTER_TXT:
                art_add.append((s, v))
            else:
                real_add.append(s)
        if real_add:
            reds.append('pure 新增段出尾块/页脚族：%s' % real_add[:4])
        if m2 != m0:
            reds.append('pure p1 md5 漂移 %s≠%s' % (m2[:8], m0[:8]))
        if reds:
            bad += 1
            print('[红] %s：%s' % (piece, '｜'.join(reds)))
            print('     页 %d→true %d/pure %d｜p1 md5 原 %s/true %s/pure %s'
                  % (n0, nt, np_, m0[:8], m1[:8], m2[:8]))
        else:
            print('[过] %s：页 %d→true %d/pure %d｜true 缺原段 0｜pure 缺原段 0（页数差伪段 %d：页脚/页码族）｜'
                  'pure 新增＝尾块族 %d 段＋页脚伪段 %d｜pure p1 md5＝原（%s）'
                  % (piece, n0, nt, np_, sum(v for _, v in art), tail_tokens,
                     sum(v for _, v in art_add), m0[:8]))
    print('页级对勘（练习本）：%s' % ('FAIL %d 件红' % bad if bad else '全过 12 件'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
