# -*- coding: utf-8 -*-
r"""门谱P1.py — 换装正装波4a 件级门谱合集（只读）：值守恒＋ANSKEY 两档集合恒等＋
[E] 印面对账（[答案]/[详解] 计数）＋页级对勘（原印面↔双档）。

用法: python 门谱P1.py <件名>            # 单件（件目录须已含 main.tex/main-true.log/main-pure.log/三 PDF）
      python 门谱P1.py --all            # 5 件全量
退出码: 0＝全过；1＝有红。
口径：
  值守恒＝main.tex ansblock 块体（剥 % ans: 行）与「按迁移器同源提取重渲染块」逐字相等；
    块数/键集合==键账（判符号形归一与迁移器同制）。
  ANSKEY＝两档 log `M3-ANSKEY:` 键多重集恒等且==件键账（对号两档可跑）。
  [E]＝true PDF 文本层 `[答案]` 计数==ansitem 数、`[详解]`==ansnote 详解数；pure 两计全零（泄答红）。
  页勘＝原 main.pdf 文字段（剥空白多重集）在 true 缺失必须 0；pure 缺段逐一列出（归因素养小结/答案值
    ＝设计内，只登记）；页数 pure≤true；p1 PNG md5 三方登记。
红线：只读；零 git。
"""
import hashlib, io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 迁移P1导学 as MG

TREE = MG.TREE
PIECES = MG.DAOXUE + [MG.ZM]


def tex_blocks(tex):
    out = []
    for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\]\n(.*?)\\end\{ansblock\}', tex, re.S):
        body = '\n'.join(l for l in m.group(2).split('\n') if not l.startswith('% ans:'))
        out.append((m.group(1), body.rstrip('\n')))
    return out


def label_of(key):
    m = re.match(r'^导-课时9\d-(.+)$', key)
    suf = m.group(1) if m else re.match(r'^导-章末-(\d)$', key).group(1)
    if suf == '预习填空':
        return '预习填空'
    if suf == '拓展':
        return '拓展延伸'
    m2 = re.match(r'^判(\d)$', suf)
    if m2:
        n = int(m2.group(1))
        return '(%d)' % ((n - 1) % 2 + 1)          # 判题号循知识点组 (1)(2)×3＝件面 \zhentib 实参
    m2 = re.match(r'^探(\d)-例1$', suf)
    if m2:
        return '例1'
    m2 = re.match(r'^探(\d)-变式1$', suf)
    if m2:
        return '变式1'
    m2 = re.match(r'^[评章]?末?(\d)$', suf) or re.match(r'^评(\d)$', suf)
    return str(int(suf[-1]))


def log_anskeys(logpath):
    if not os.path.isfile(logpath):
        return None
    return [m.group(1) for m in re.finditer(r'M3-ANSKEY: (\S+)', io.open(logpath, encoding='utf-8', errors='replace').read())]


def pdf_text(f):
    doc = pymupdf.open(f)
    return doc.page_count, ''.join(p.get_text() for p in doc)


def lines_multiset(f):
    doc = pymupdf.open(f)
    ls = [re.sub(r'\s+', '', x) for pg in doc for x in pg.get_text().split('\n')]
    return doc.page_count, Counter(x for x in ls if x)


def png_md5(f, page=0, zoom=2.0):
    doc = pymupdf.open(f)
    pix = doc[page].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return hashlib.md5(pix.tobytes('png')).hexdigest()


def gate(piece):
    reds, notes = [], []
    d = os.path.join(TREE, piece)
    tex = io.open(os.path.join(d, 'main.tex'), encoding='utf-8').read()
    blk = tex_blocks(tex)
    keys = [k for k, _ in blk]
    # —— 值守恒 ——
    K, DETAIL = MG.extract()
    want = {}
    if piece == MG.ZM:
        want = {str(n): ('导-章末-%d' % n) for n in range(1, 6)}
        want_keys = ['导-章末-%d' % n for n in range(1, 6)]
    else:
        i = MG.DAOXUE.index(piece) + 1
        want_keys = MG.expect_keys_ks(i)
        want = None
    want_set = set(want_keys)
    if set(keys) != want_set:
        reds.append('值守恒:键集合不平（多 %s 少 %s）' % (sorted(set(keys) - want_set)[:3], sorted(want_set - set(keys))[:3]))
    for k, body in blk:
        det = DETAIL.get(k)
        exp = MG.block(k, label_of(k), K[k], det)
        exp = exp[exp.index('\n') + 1:exp.rindex('\n\\end{ansblock}')]
        exp = '\n'.join(l for l in exp.split('\n') if not l.startswith('% ans:')).rstrip('\n')
        if body != exp:
            reds.append('值守恒:块体漂移 %s' % k)
    notes.append('值守恒: %d 块键集合==键账，块体重渲染逐字平（详解随键 %d）' % (len(blk), sum(1 for k in keys if k in DETAIL)))
    # —— ANSKEY 两档 ——
    at, ap = log_anskeys(os.path.join(d, 'main-true.log')), log_anskeys(os.path.join(d, 'main-pure.log'))
    if at is None or ap is None:
        reds.append('ANSKEY: log 缺（先编译）')
    else:
        if Counter(at) != Counter(ap):
            reds.append('ANSKEY: 两档多重集不平 true%d/pure%d' % (len(at), len(ap)))
        if set(at) != want_set:
            reds.append('ANSKEY: 键集合≠键账')
        notes.append('ANSKEY: true %d＝pure %d＝键账 %d' % (len(at), len(ap), len(want_set)))
    # —— [E] 印面 ——
    nt, tt = pdf_text(os.path.join(d, 'main-true.pdf'))
    np_, tp = pdf_text(os.path.join(d, 'main-pure.pdf'))
    n_item = sum(1 for k in keys)
    n_det = sum(1 for k in keys if k in DETAIL)
    ct, cdt = tt.count('[答案]'), tt.count('[详解]')
    cp, cdp = tp.count('[答案]'), tp.count('[详解]')
    if ct != n_item or cdt != n_det:
        reds.append('[E]: true [答案]%d/%d [详解]%d/%d' % (ct, n_item, cdt, n_det))
    if cp or cdp:
        reds.append('[E]: pure 泄答 [答案]%d [详解]%d' % (cp, cdp))
    notes.append('[E]: true [答案]×%d＝块数、[详解]×%d＝详解数；pure 全零' % (ct, cdt))
    # —— 页级对勘 ——
    n0, L0 = lines_multiset(os.path.join(d, 'main.pdf'))
    n1, L1 = lines_multiset(os.path.join(d, 'main-true.pdf'))
    n2, L2 = lines_multiset(os.path.join(d, 'main-pure.pdf'))

    def miss(base, tgt):
        c = Counter(base)
        c.subtract(tgt)
        return sum(v for v in c.values() if v > 0), [k for k, v in c.items() if v > 0]

    mt, st = miss(L0, L1)
    mp, sp = miss(L0, L2)
    if mt != 0:
        reds.append('页勘: true 缺原段 %d' % mt)
    if n2 > n1:
        reds.append('页勘: 页数 pure%d>true%d' % (n2, n1))
    m0, m1, m2 = (png_md5(os.path.join(d, x)) for x in ('main.pdf', 'main-true.pdf', 'main-pure.pdf'))
    notes.append('页勘: 页 %d→true %d/pure %d｜true 缺原段 %d/%d｜pure 缺段 %d（样本 %s）'
                 % (n0, n1, n2, mt, sum(L0.values()), mp, (' ¦ '.join(sp[:3]))[:80]))
    notes.append('p1 md5 原%s true%s pure%s' % (m0[:8], m1[:8], m2[:8]))
    print('[%s]' % piece)
    for x in notes:
        print('  ' + x)
    for x in reds:
        print('  [红] ' + x)
    return not reds


def main():
    args = sys.argv[1:]
    todo = PIECES if args and args[0] == '--all' else ([args[0]] if args else [])
    if not todo:
        print(__doc__)
        return 2
    ok = all(gate(p) for p in todo)
    print('[门谱P1 %s]' % ('全过' if ok else '有红'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
