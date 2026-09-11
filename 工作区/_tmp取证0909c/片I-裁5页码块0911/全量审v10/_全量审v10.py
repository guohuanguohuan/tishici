# -*- coding: utf-8 -*-
r"""全量逐页审 v10（卷四·1 全量逐页目验＋卷四·3 防漏门六项）。

对 v10 包与 v9 包（件序/页数相同，包内页号一一对应）逐页跑同一套机器判据，
每页落一行证据（含 v9→v10 读数差），命中项另落细目供人工归类。
判据（全为复跑/测量级，卷四·2）：
  S   页面尺寸（mm，横排加「横」）
  ①   生产注记串命中（值在此/题源待补/待源/占位/待补/待校/待改/勿印/内部口径/草案/TBD/TODO/FIXME/×××/……位）
  ②   品牌·占位串命中（全品/学练考/曲一线/五三/5·3）
  ③   题源标计数（（20YY…）形制）——本轮不涉题源，v9→v10 读数须不变
  ④   装饰-文字重叠（填充图形 ∩ 文本词框，交面积 >0.5pt²）
  ④b  位图数／位图-文字重叠／位图越栏
  ⑤   拉伸门 J4（同栏 CJK-CJK 墨隙 >0.5×字号）＋峰值
  断   孤字行（视觉行去空白 ≤2 字符且非标签/非数学/非括号槽）
  ⑥   缩进-像素复核＝另册 _缩进复测.py（本行仅指认）
用法：python _全量审v10.py
"""
import io
import re
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PT = 72 / 25.4
V10 = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v10-21页0911.pdf'
V9 = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf'
NOTE = ['值在此', '题源待补', '待源', '占位', '待补', '待校', '待改', '勿印', '内部口径',
        '草案', 'TBD', 'TODO', 'FIXME', '×××', '……位']
BRAND = ['全品', '学练考', '曲一线', '五三', '5·3']
LABELS = ('[答案]', '[解析]', '[分析]', '[详解]', '[点睛]', '[题型总结]', '[解法', '[难度]')
MATHY = re.compile('[\u20d7\U0001d434-\U0001d7ff√∈≠≤≥∘°⟩⟨（）()·×÷⋅]')


def is_cjk(ch):
    o = ord(ch)
    return 0x3000 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or 0x2018 <= o <= 0x201D


def cols_of(page):
    """按页宽推双栏界（pt）：A4 纵向＝margin17.2/sep7.6→栏宽84.0；其余单栏。"""
    w = page.rect.width
    if abs(w / PT - 210.0) < 1.0:
        m, cs = 17.2 * PT, 7.6 * PT
        cw = (w - 2 * m - cs) / 2
        return [(m, m + cw), (m + cw + cs, w - m)]
    return [(6 * PT, w - 6 * PT)]


def inter_area(a, b):
    x0, y0 = max(a.x0, b.x0), max(a.y0, b.y0)
    x1, y1 = min(a.x1, b.x1), min(a.y1, b.y1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0) * PT * PT


def scan(pdf):
    doc = pymupdf.open(pdf)
    rows = []
    for i, page in enumerate(doc, 1):
        raw = page.get_text('rawdict')
        txt = page.get_text()
        tflat = re.sub(r'\s+', '', txt)
        W, H = page.rect.width / PT, page.rect.height / PT
        cl = cols_of(page)
        mid = (cl[0][1] + cl[-1][0]) / 2 if len(cl) > 1 else cl[0][1]
        hit_n = [k for k in NOTE if k in tflat]
        hit_b = [k for k in BRAND if k in tflat]
        n_src = len(re.findall(r'（20\d\d', txt))
        n_gk = txt.count('高考') + txt.count('真题')   # 题源标在场域（高考题位/标签）
        j4, words = [], []
        for b in raw['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                ci = 0 if l['bbox'][0] < mid else (1 if len(cl) > 1 else 0)
                for sp in l['spans']:
                    ch = sp['chars']
                    t = ''.join(c2['c'] for c2 in ch)
                    if t.strip():
                        words.append(pymupdf.Rect(sp['bbox']))
                    for a, c in zip(ch, ch[1:]):
                        if not (a['c'].strip() and c['c'].strip()):
                            continue
                        if is_cjk(a['c']) and is_cjk(c['c']):
                            g = (c['bbox'][0] - a['bbox'][2]) * PT
                            if g > 0.5 * sp['size']:
                                j4.append((round(g, 2), a['c'], c['c'], i, ci))
        # 孤字行：同栏同基线（±2pt 聚类，数学上下标偏移不拆行）合并后，
        # 去空白 ≤3 字符且含 ≥1 汉字（纯标点/纯数字/数学碎片不算——它们是数学片段非视觉行）
        spans_row = []
        for b in raw['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                for sp in l['spans']:
                    t = ''.join(c['c'] for c in sp['chars'])
                    if t.strip():
                        spans_row.append((sp['origin'][1], l['bbox'][0], t))
        spans_row.sort()
        rows_out, cur, curbase = [], [], None
        for base, x0, t in spans_row:
            if cur and abs(base - curbase) > 2.0:
                rows_out.append(cur); cur = []
            cur.append((base, x0, t))
            curbase = base if not cur[:-1] else curbase
        if cur:
            rows_out.append(cur)
        orph = []
        for frs in rows_out:
            mt = re.sub(r'\s+', '', ''.join(t for _b, _x, t in frs))
            if 0 < len(mt) <= 3 and re.search(r'[\u4e00-\u9fff]', mt) \
                    and not mt.startswith(LABELS):
                orph.append(mt)
        # ④ 装饰-文字重叠：命中按成因分档——白底（花形/标签反白）、页码灰块（y>275mm 出血块）、
        #    墨盒（≤3mm 小方＝「错误的打×」自绘）均系设计内；其余计「真压字」＝缺陷档。
        wrects = words
        ov_fill, ov_w, ov_f, ov_b = [], 0, 0, 0
        for d in page.get_drawings():
            if d.get('fill') is None:
                continue
            r = pymupdf.Rect(d['rect'])
            if r.width < 1.5 or r.height < 1.5 or r.width > 500 or r.height > 500:
                continue
            hitw = [wr for wr in wrects if inter_area(wr, r) > 0.5]
            if not hitw:
                continue
            g = d['fill']
            if all(abs(x - 1.0) < 0.02 for x in g):
                ov_w += 1
            elif r.y0 / PT > 275.0:
                ov_f += 1
            elif r.width / PT <= 3.0 and r.height / PT <= 3.0:
                ov_b += 1
            else:
                ov_fill.append((round(r.x0 / PT, 1), round(r.y0 / PT, 1),
                                round(r.width / PT, 1), round(r.height / PT, 1)))
        imgs = [pymupdf.Rect(inf['bbox']) for inf in page.get_image_info()]
        ov_img = sum(1 for ir in imgs if any(inter_area(wr, ir) > 0.5 for wr in wrects))
        out_col = sum(1 for ir in imgs
                      if len(cl) > 1 and not any(a - 1.0 <= ir.x0 and ir.x1 <= b + 1.0 for a, b in cl))
        rows.append(dict(p=i, size=f'{W:.0f}×{H:.0f}{"" if W < H else "横"}',
                         note=hit_n, brand=hit_b, src=n_src, gk=n_gk, j4=len(j4),
                         j4max=max([x[0] for x in j4], default=0.0),
                         orphan=sorted(orph), ov=len(ov_fill), ovbox=ov_fill[:4],
                         ovw=ov_w, ovf=ov_f, ovb=ov_b,
                         img=len(imgs), ovimg=ov_img, outcol=out_col))
    doc.close()
    return rows


def fmt(r):
    return (f"p{r['p']:>2} {r['size']:>9} ①注记{'0' if not r['note'] else ','.join(r['note'])} "
            f"②品牌{'0' if not r['brand'] else ','.join(r['brand'])} ③题源{r['src']}/高考域{r['gk']} "
            f"④真压字{r['ov']}（白底{r['ovw']}/页码块{r['ovf']}/墨盒{r['ovb']}） "
            f"④b图{r['img']}/压字{r['ovimg']}/越栏{r['outcol']} "
            f"⑤拉伸{r['j4']}(峰{r['j4max']:.2f}) 断孤行{len(r['orphan'])}"
            f"{'(' + ','.join(r['orphan']) + ')' if r['orphan'] else ''} ⑥另册")


a9 = scan(V9)
a10 = scan(V10)
print('=' * 104)
print('v10 包 21 页逐页证据（卷四·1 检查单机器项；⑥缩进＝_缩进复测.py 另册留档）')
print('=' * 104)
for r10, r9 in zip(a10, a9):
    d = []
    for k in ('src', 'gk', 'j4', 'j4max', 'ov', 'ovw', 'ovf', 'ovb', 'img', 'ovimg', 'outcol'):
        if r10[k] != r9[k]:
            d.append(f'{k}:{r9[k]}→{r10[k]}')
    if r10['note'] != r9['note']:
        d.append('①' + str(r9['note']) + '→' + str(r10['note']))
    if r10['brand'] != r9['brand']:
        d.append('②' + str(r9['brand']) + '→' + str(r10['brand']))
    if r10['orphan'] != r9['orphan']:
        d.append('断' + str(r9['orphan']) + '→' + str(r10['orphan']))
    print(fmt(r10) + '  ｜v9→v10 ' + ('；'.join(d) if d else '全同'))
print('=' * 104)
print('合计：注记命中页', [r['p'] for r in a10 if r['note']],
      '｜品牌命中页', [r['p'] for r in a10 if r['brand']],
      '｜真压字页', [r['p'] for r in a10 if r['ov']],
      '｜图越栏页', [r['p'] for r in a10 if r['outcol']],
      '｜图压字页', [r['p'] for r in a10 if r['ovimg']],
      '｜拉伸合计', sum(r['j4'] for r in a10), '（v9＝', sum(r['j4'] for r in a9), '）')
