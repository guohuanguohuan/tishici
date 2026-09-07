# -*- coding: utf-8 -*-
r"""v4 复测 A 项（独立复测代理，只验证不改）：①log ②行距主峰 ③灰档(PDF对象级+PNG像素级) ④题区起点 ⑤栏利用率
几何独立设定：导学/练习 A4竖放 双栏(栏距7.5mm) 左右15mm 上15mm 下15/19.5mm；测评 A4横放 3栏(栏距8mm) 15/15/17.33mm。"""
import os, re
from collections import Counter
import pymupdf
from PIL import Image
import numpy as np

ROOT = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4"
PT = 72 / 25.4
CFG = {
    '导学件': dict(portrait=True,  top=15.0,  bottom=15.0,  ncols=2, colsep=7.5),
    '练习件': dict(portrait=True,  top=15.0,  bottom=19.5,  ncols=2, colsep=7.5),
    '测评卷': dict(portrait=False, top=15.0,  bottom=17.33, ncols=3, colsep=8.0),
}
PALETTE = {0, 119, 221, 255}   # 黑/777777/DDDDDD/纸白

def scan_log(d):
    log = open(os.path.join(ROOT, d, 'main.log'), encoding='utf-8', errors='ignore').read()
    n_err = len(re.findall(r'^!', log, re.M))
    n_over = len(re.findall(r'Overfull', log))
    n_miss = len(re.findall(r'Missing character', log))
    n_under = len(re.findall(r'Underfull', log))
    m = re.search(r'Output written on main\.pdf \((\d+) pages', log)
    mt_tex = os.path.getmtime(os.path.join(ROOT, d, 'main.tex'))
    mt_log = os.path.getmtime(os.path.join(ROOT, d, 'main.log'))
    mt_pdf = os.path.getmtime(os.path.join(ROOT, d, 'main.pdf'))
    return dict(err=n_err, over=n_over, miss=n_miss, under=n_under,
                pages=int(m.group(1)) if m else -1,
                log_newer=mt_log > mt_tex, pdf_newer=mt_pdf >= mt_log)

def col_lefts(cfg, pw):
    m = 15 * PT
    if cfg['portrait']:
        colw = (pw - 2 * m - cfg['colsep'] * PT) / 2
        return [m, m + colw + cfg['colsep'] * PT], cfg['ncols']
    colw = (pw - 2 * m - 2 * cfg['colsep'] * PT) / 3
    return [m, m + colw + cfg['colsep'] * PT, m + 2 * (colw + cfg['colsep'] * PT)], cfg['ncols']

for d, cfg in CFG.items():
    print('=' * 22, d, '=' * 22)
    L = scan_log(d)
    print(f"①log: error={L['err']} overfull={L['over']} missingchar={L['miss']} (underfull={L['under']}) "
          f"页数={L['pages']} | log新于tex={L['log_newer']} pdf新于log={L['pdf_newer']}")
    doc = pymupdf.open(os.path.join(ROOT, d, 'main.pdf'))
    pw, ph = doc[0].rect.width, doc[0].rect.height
    coll, ncols = col_lefts(cfg, pw)
    top, bot = cfg['top'] * PT, (ph / PT - cfg['bottom']) * PT
    texth = bot - top

    # ② 行距主峰 + ③ PDF对象级灰档
    for pno, page in enumerate(doc, 1):
        cols = {c: [] for c in range(ncols)}
        spans_all, grays = [], set()
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                spans_all += ln['spans']
                mx = max((sp['size'] for sp in ln['spans']), default=0)
                if not (10.0 <= mx <= 11.0):
                    continue
                ci = min(ncols - 1, max(0, int((ln['bbox'][0] - coll[0] + 1) // (coll[1] - coll[0])))) if ncols > 1 else 0
                # 列归属：按最近的栏左
                ci = min(range(ncols), key=lambda c: abs(ln['bbox'][0] - coll[c]))
                if ln['bbox'][0] >= coll[ci] - 3:
                    cols[ci].append(ln['spans'][0]['origin'][1])
        diffs = []
        for c in range(ncols):
            ys = sorted(cols[c])
            diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 5 < b - a < 40]
        peak = Counter(diffs).most_common(3) if diffs else []
        for sp in spans_all:
            col = sp['color']
            r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
            if r == g == b and 0 < r < 255:
                grays.add(r)
        for dr in page.get_drawings():
            for key in ('color', 'fill'):
                c = dr.get(key)
                if c:
                    rgb = tuple(round(x * 255) for x in c)
                    if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                        grays.add(rgb[0])
        p3 = ' '.join(f'{v}×{n}' for v, n in peak)
        flag2 = 'OK' if peak and 17.5 <= peak[0][0] <= 18.5 else '!!'
        flag3 = 'OK' if grays <= {0x77, 0xDD} and len(grays) <= 2 else '!!'
        print(f"②p{pno} {flag2} diffs={len(diffs)} 峰值={p3}")
        print(f"③p{pno} {flag3} PDF灰档={sorted(grays)}")

    # ③b PNG 像素级
    pngdir = os.path.join(ROOT, d, 'png')
    for f in sorted(os.listdir(pngdir)):
        img = np.array(Image.open(os.path.join(pngdir, f)).convert('L'))
        h = np.bincount(img.ravel(), minlength=256)
        tot = img.size
        cov = sum(h[v] for v in PALETTE) / tot * 100
        top8 = sorted(enumerate(h), key=lambda kv: -kv[1])[:8]
        print(f"③b {f}: 调色板4值覆盖={cov:.2f}%  top值=" +
              ' '.join(f'{v}:{c * 100 / tot:.2f}%' for v, c in top8))

    # ④ 题区起点（逐标记实测）
    p1 = doc[0]
    marks = {}
    for blk in p1.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            for key, pat in [('课前预习', '课前预习'), ('【学习目标】', '【学习目标】'),
                             ('◆知识点一', '◆知识点'), ('夯基达标', '夯基达标'),
                             ('题1', r'^1．'), ('分区标题一', r'^[一二三四]、'),
                             ('班级栏', '班级'), ('考生注意', '考生注意')]:
                if key not in marks and re.search(pat, t):
                    marks[key] = ln['bbox']
    for k, bb in marks.items():
        print(f"④ {k}: 顶y={bb[1] / PT:.1f}mm 版心顶起={(bb[1] - top) / PT:.1f}mm")
    if '班级栏' in marks and '考生注意' in marks:
        jh = (marks['考生注意'][3] - marks['班级栏'][1]) / PT
        print(f"④ 测评卷头块高(班级栏顶→评分说明底)={jh:.1f}mm（门 ≤30）")

    # ⑤ 栏利用率（文本+图+矢量；排除页脚灰块31mm与版心底以下起笔元素）
    print('⑤ 栏利用率（每页各栏）:')
    for pno, page in enumerate(doc, 1):
        colmax = [top] * ncols
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                x0, y0, x1, y1 = ln['bbox']
                if y0 > bot + 1.5 or y1 > bot + 1.5:
                    continue
                ci = min(range(ncols), key=lambda c: abs(x0 - coll[c]))
                if coll[ci] - 3 <= x0 or x1 > coll[ci]:
                    colmax[ci] = max(colmax[ci], min(y1, bot))
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                if r.y0 > bot + 1.5:
                    continue
                ci = min(range(ncols), key=lambda c: abs(r.x0 - coll[c]))
                colmax[ci] = max(colmax[ci], min(r.y1, bot))
        for dr in page.get_drawings():
            r = dr['rect']
            if r.y0 > bot + 1.5 or r.y1 < top:
                continue
            if abs(r.width - 31 * PT) < 3:   # 页脚页码灰块
                continue
            ci = min(range(ncols), key=lambda c: abs((r.x0 + r.x1) / 2 - coll[c]))
            colmax[ci] = max(colmax[ci], min(r.y1, bot))
        utils = [(y - top) / texth for y in colmax]
        gaps = [(bot - y) / PT for y in colmax]
        npage = len(doc)
        tag = '末页' if pno == npage else ''
        util_str = '/'.join(f'{u * 100:.0f}%' for u in utils)
        gap_str = '/'.join(f'{g:.1f}mm' for g in gaps)
        bad = ('!!' if pno < npage and min(utils) < 0.70 else ('OK' if pno < npage else '登记'))
        print(f"  p{pno}{tag} {bad} 利用率={util_str} 末墨距版心底={gap_str}")
    doc.close()
