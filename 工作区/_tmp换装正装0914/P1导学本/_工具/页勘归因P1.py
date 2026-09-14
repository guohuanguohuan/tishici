# -*- coding: utf-8 -*-
r"""页勘归因P1.py — pure 档缺原段全清单＋逐段归因（只读，读数落 ../_门谱读数/_页勘-pure缺段归因.txt）。
归因判据（命中其一即设计内）：
  A 素养小结＝段（或其前 12 字）见于该件 main.src.tex 的 \xiaojie{…} 体（pure 隐讲解层＝主脑 0914 裁）；
  B 重排＝段为原 PDF 换行切片，同文见于 pure 任一段的子串关系（去空白后互为子串）；
  C 其余＝登记待裁（须为 0）。
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 迁移P1导学 as MG

TREE = MG.TREE
norm = lambda s: re.sub(r'\s+', '', s)
OUT = os.path.join(TREE, '_门谱读数', '_页勘-pure缺段归因.txt')
rep = []


def segs(f):
    doc = pymupdf.open(f)
    return Counter(norm(x) for pg in doc for x in pg.get_text().split('\n') if norm(x))


def allsegs(f):
    doc = pymupdf.open(f)
    return [norm(x) for pg in doc for x in pg.get_text().split('\n') if norm(x)]


for piece in MG.DAOXUE + [MG.ZM]:
    d = os.path.join(TREE, piece)
    src = io.open(os.path.join(d, 'main.src.tex'), encoding='utf-8').read()
    xj = []
    for m in re.finditer(r'\\xiaojie\{', src):          # 体含 \frac{…} 花括号→配平提取
        i, depth, j = m.end(), 1, m.end()
        while j < len(src) and depth:
            if src[j] == '{':
                depth += 1
            elif src[j] == '}':
                depth -= 1
            j += 1
        xj.append(norm(src[i:j - 1]))
    L0, Lp = segs(os.path.join(d, 'main.pdf')), segs(os.path.join(d, 'main-pure.pdf'))
    c = Counter(L0)
    c.subtract(Lp)
    missing = [k for k, v in c.items() if v > 0 for _ in range(v)]
    pure_all = allsegs(os.path.join(d, 'main-pure.pdf'))
    rep.append('[%s] pure 缺原段 %d' % (piece, len(missing)))
    nc = 0
    cjk = lambda s: re.sub(r'[^\u4e00-\u9fff，。；：、（）]', '', s)
    for seg in missing:
        if any(seg in x or (cjk(seg) and cjk(seg) in cjk(x)) for x in xj):
            tag = 'A素养小结'                      # CJK 投影＝数学斜体切片仍归小结（公式边界换行）
        elif any((seg in p2) or (p2 and seg and p2 in seg) for p2 in pure_all):
            tag = 'B重排切片'
        else:
            tag = 'C待裁'
            nc += 1
        rep.append('   %s ｜ %s' % (tag, seg[:46]))
    if nc:
        rep.append('   !! C 待裁 %d 段' % nc)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
print('\n'.join(l for l in rep if l.startswith('[') or 'C 待裁' in l))
print('全清单 → %s' % OUT)
