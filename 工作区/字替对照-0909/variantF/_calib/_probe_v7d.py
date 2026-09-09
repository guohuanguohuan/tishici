# -*- coding: utf-8 -*-
# 0909 收尾轮探针：为 _测v4断言.py 适配取实测值（只读 main.pdf/body.tex，不改版面）
import re, os
import pymupdf

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT = 72 / 25.4
MARGIN = 17.575 * PT
PAGE_W = 595.0
COLSEP = 9.25 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
DPI = 150
SC = DPI / 72.0

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
blkfile = open(os.path.join(BASE, 'qp-blocks.tex'), encoding='utf-8').read()

lines_of = {}
chars_of = {}
for pno, page in enumerate(doc, 1):
    ls, cs = [], []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append((t, ln['bbox'], ln['spans']))
    for blk in page.get_text('rawdict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                for ch in sp['chars']:
                    cs.append((ch['c'], ch['bbox'], sp['size'], sp['font']))
    lines_of[pno] = ls
    chars_of[pno] = cs

print('==== A. 判断行（p1/p3 含 √ 或 × 的行片段） ====')
for pno in (1, 3):
    for t, bb, sps in lines_of[pno]:
        if '√' in t or '×' in t:
            frags = [sp['text'] for sp in sps]
            print(f'p{pno} y={bb[1]:.1f} x1={bb[2]:.2f} 行={t!r}')
            print(f'   片段={frags!r}')
            cl = COLL[0] if bb[0] < MID else COLL[1]
            print(f'   栏右-行bbox右 = {(cl + COLW - bb[2]) / PT:.2f}mm')

print('==== A2. N1 ink 实测（尾为括号答案的行） ====')
for pno in (1, 3):
    page = doc[pno - 1]
    for t, bb, sps in lines_of[pno]:
        mt = re.search(r'\(\s*[√×]\s*\)$', t)
        if not mt:
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
        w, h, s = pm.width, pm.height, pm.samples
        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC
        ink_d = (cl + COLW - ink_r) / PT
        bb_d = (cl + COLW - bb[2]) / PT
        print(f'p{pno} {t[-6:]!r} ink距栏右{ink_d:.2f} bbox距栏右{bb_d:.2f}')

print('==== B. 变/例 12pt 字符字体名＋密度样本 ====')
def _dens_probe(pno, bb):
    page = doc[pno - 1]
    pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1))
    w, h, s = pm.width, pm.height, pm.samples
    dk = sum(255 - v for v in s if v < 200)
    return dk / max(1, (bb[2] - bb[0]) * (bb[3] - bb[1])) * 1000
for key in ('变', '例'):
    seen = {}
    for pno in range(1, 8):
        for c, bb, sz, fn in chars_of[pno]:
            if c == key and 11.6 <= sz <= 12.4:
                seen.setdefault(fn.split('+')[-1].split('--')[0], []).append(_dens_probe(pno, bb))
    for fn, ds in seen.items():
        med = sorted(ds)[len(ds) // 2]
        print(f'{key}: 字体={fn} n={len(ds)} 密度中位={med:.1f}')

print('==== C. N4 表组：逐组行数/行距/文本 ====')
def rgb255(c):
    return tuple(round(x * 255) for x in c)
tab_groups = []
for pno in range(1, 8):
    page = doc[pno - 1]
    hrs = []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c or rgb255(c) != (122, 122, 122):
            continue
        if r.width > 15 * PT and r.height < 3:
            hrs.append(r)
    bycol = {}
    for r in hrs:
        cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
        bycol.setdefault(cl, []).append(r)
    for cl, lst in bycol.items():
        lst.sort(key=lambda x: x.y0)
        cur = [lst[0]]
        for r in lst[1:]:
            if r.y0 - cur[-1].y1 > 60:
                if len(cur) >= 3:
                    tab_groups.append((pno, cl, cur))
                cur = [r]
            else:
                cur.append(r)
        if len(cur) >= 3:
            tab_groups.append((pno, cl, cur))
for pno, cl, rs in tab_groups:
    inrows = [(t, sps[0]['origin'][1]) for t, bb, sps in lines_of[pno]
              if rs[1].y0 <= bb[1] and bb[3] <= rs[-1].y1 + 1 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7]
    inrows.sort(key=lambda x: x[1])
    ys = [y for _, y in inrows]
    pits = [(b - a) / PT for a, b in zip(ys, ys[1:])]
    print(f'p{pno} cl={cl:.0f} 规则线{len(rs)}条 文本行{len(inrows)} 行距pt{["%.1f" % p for p in pits]}')
    for t, _ in inrows:
        print(f'    行: {t[:40]!r}')

print('==== D. N5/N8 楷体字体名实测 ====')
for pno in range(1, 8):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('①识别') or (pno == 1 and '掌握' in t[:6]):
            print(f'p{pno} {t[:14]!r} 字体={sps[0]["font"]} 字号={sps[0]["size"]:.2f}')

print('==== E. N6 p2 图后邻行文本 ====')
page = doc[1]
for img in page.get_images(full=True):
    for r in page.get_image_rects(img[0]):
        w_ = r.width / PT
        cl = COLL[0] if r.x0 < MID else COLL[1]
        if abs((r.x0 + r.x1) / 2 - cl - COLW / 2) / PT > 3 or not (58 < w_ < 62):
            continue
        below = [(bb[1], t) for t, bb, sps in lines_of[2] if bb[1] > r.y1 - 2 and cl - 7 <= bb[0] <= cl + COLW + 7]
        below.sort()
        print(f'图 y1={r.y1:.1f} 后续行: ' + ' | '.join(f'{t[:24]!r}' for _, t in below[:3]))

print('==== F. 条目号行（^\\d+\\.）逐列 ====')
for pno in range(1, 8):
    for cl in COLL:
        rows = [(bb[1], bb[3], t) for t, bb, sps in lines_of[pno]
                if cl - 7 <= bb[0] < cl + COLW + 7]
        rows.sort()
        nums = [(y0, t) for y0, y1, t in rows if re.match(r'^\d+\.(?!\d)', t)]
        kn0 = next((k for k, (y0, y1, t) in enumerate(rows) if t.startswith('◆知识点')), -1)
        if nums:
            print(f'p{pno} cl={cl:.0f} kn0={kn0} 条目号行: ' + ' | '.join(f'y{y:.0f}{t[:8]!r}' for y, t in nums))

print('==== G. ⑨ 源空格残留 7 处定位 ====')
_CJKC = '\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u2018\u2019\u201c\u201d'
_sp_pat = r'\\[a-zA-Z]+ +| +(?=[' + _CJKC + r'])|(?<=[' + _CJKC + r']) +'
for i, m in enumerate(re.finditer(_sp_pat, body)):
    g = m.group(0)
    if g.startswith('\\'):
        continue
    ln = body.count('\n', 0, m.start()) + 1
    ctx = body[max(0, m.start() - 50):m.end() + 30].replace('\n', '⏎')
    print(f'#{i + 1} 行{ln} 匹配={g!r} 上下文=…{ctx!r}…')

print('==== H. ⑧ 页脚小字字号集合 ====')
for pno in range(1, 8):
    szs = set()
    for t, bb, sps in lines_of[pno]:
        if bb[1] > 742:
            for sp in sps:
                if sp['text'].strip():
                    szs.add(round(sp['size'], 2))
    print(f'p{pno} 字号集={sorted(szs)}')

print('==== I. ⑭ () 相邻对全量 ====')
for pno in range(1, 8):
    cs = chars_of[pno]
    for i in range(len(cs) - 1):
        if cs[i][0] == '(' and cs[i + 1][0] == ')':
            v = (cs[i + 1][1][0] - cs[i][1][2]) / PT
            print(f'p{pno} y={cs[i][1][1]:.0f} gap={v:.2f}')

print('==== J. ④ 基线归并组（p1/p3 含括号答案的组） ====')
_grp = {}
for pno in (1, 3):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
for k, frs in sorted(_grp.items()):
    mt = ''.join(x[1] for x in sorted(frs))
    if '√' in mt or '×' in mt:
        print(f'{k} 片段={[x[1] for x in sorted(frs)]!r}')
print('==== 完 ====')
