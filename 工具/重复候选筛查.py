# -*- coding: utf-8 -*-
"""重复候选筛查.py — 高度重复查重预筛：数字归一化＋相似度，输出疑似「只换数字/换外壳」题对清单
用法: python 重复候选筛查.py <docx路径...> [-o 输出.md] [--threshold 0.80]
多个文件一起传入即跨文件比对（同步线§2.3跨两池统一查重口径）。
**仅做候选预筛（机械文本比对）；「知识点+题型+解法是否相同」的高度重复判定必须亲算（公共规则§5），
禁止照搬脚本相似度直接判重。**几百题内分钟级；题量更大时可先用元素区间分段再分批传入。"""
import sys, os, re, itertools
from difflib import SequenceMatcher
from dump_docx import body_elements, is_qstart

def norm(text):
    """数字→#、中文数字→#、去图/换行/空白/全半角标点、小写——归一化后只剩结构与文字骨架。"""
    t = re.sub(r'\d+(?:\.\d+)?%?', '#', text)
    t = re.sub(r'[零一二两三四五六七八九十百千万]+', '#', t)
    t = t.replace('【图】', '').replace('⏎', '').replace('\n', '')
    t = re.sub(r'\s+', '', t)
    t = re.sub(r'[，。；：、（）()\[\]【】“”‘’\'",.!?！？—－\-…·/／]', '', t)
    return t.lower()

def load_blocks(path):
    els = body_elements(path)
    starts = [(i, q) for i, tag, text in els if tag == 'p' and (q := is_qstart(text)) is not None]
    out = []
    for k, (i, q) in enumerate(starts):
        j = starts[k+1][0] - 1 if k + 1 < len(starts) else els[-1][0]
        txt = '\n'.join(t for ii, tag, t in els if i <= ii <= j and t is not None)
        first = next((t.strip() for ii, tag, t in els if ii == i and t), '')[:30].replace('|', '／')
        n = norm(txt)
        if len(n) >= 20:
            out.append((os.path.basename(path), q, n, first))
    return out

def main():
    args = sys.argv[1:]
    out, thr = '重复候选筛查.md', 0.80
    if '-o' in args:
        k = args.index('-o'); out = args[k+1]; args = args[:k] + args[k+2:]
    if '--threshold' in args:
        k = args.index('--threshold'); thr = float(args[k+1]); args = args[:k] + args[k+2:]
    blocks = []
    for p in args:
        blocks.extend(load_blocks(p))
    pairs = []
    for (fa, qa, na, sa), (fb, qb, nb, sb) in itertools.combinations(blocks, 2):
        if len(na) > len(nb) * 2 or len(nb) > len(na) * 2:
            continue
        r = SequenceMatcher(None, na, nb).ratio()
        if r >= thr:
            pairs.append((r, fa, qa, sa, fb, qb, sb))
    pairs.sort(reverse=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('# 重复候选清单（预筛草稿）\n\n')
        f.write('> 机械预筛：数字归一化＋相似度≥%.2f，共 %d 对（题池 %d 块）。**只换数/换外壳的最终判定必须亲算'
                '（公共规则§5：知识点+题型+解法相同且只换数才算高度重复），禁止照搬相似度直接判重。**\n\n' % (thr, len(pairs), len(blocks)))
        f.write('| 相似度 | 题A（文件·题号） | 题A首句 | 题B（文件·题号） | 题B首句 |\n|---|---|---|---|---|\n')
        for r, fa, qa, sa, fb, qb, sb in pairs:
            f.write('| %.3f | %s·%s | %s | %s·%s | %s |\n' % (r, fa, qa, sa, fb, qb, sb))
    print('OK 题池=%d 候选对=%d -> %s' % (len(blocks), len(pairs), out))

if __name__ == '__main__':
    main()
