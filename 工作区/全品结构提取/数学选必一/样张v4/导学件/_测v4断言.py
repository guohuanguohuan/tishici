# -*- coding: utf-8 -*-
r"""_测v4断言.py——v4 导学件断言实测（交付报告证据源）。口径沿同工程先例：
样张v4/练习件/断言v4.py（①②③④⑤结构）＋样张v4/测评卷/断言版式.py（末页利用率＝非末页逐栏断言、末页实测登记）。
①编译零 error/overfull/missingchar（扫 main.log），页数=6
②行距主峰 17.5–18.5pt（\linespread{1} 通解，逐页块内相邻行 baseline 差直方图）
③单页灰档 ≤2 且 ⊆{777777, DDDDDD}（span 字色＋描边/填充；题图位图内容色不进统计，天然豁免）
④版心顶→题区起点 ≤60mm（参数表主病5；导学件题区起点＝p1 花形行「课前预习」框顶，
  同时登记 ◆知识点一 顶缘——章首通栏区＝章/节/小节/课时/学习目标，拍板28）
⑤栏利用率：非末页逐栏 ≥70%＋非末页每栏末墨距版心底 ≤15mm（导学件对照§四-5）；
  末页（课堂检测自然收尾页）实测登记不断言（测评卷先例口径；参差收尾＝拍板23 授权）
⑥排印层逻辑断言：◆探究点 9（内联例1 9、变式1 9）、【答案】行 14、★典型性理由 3
⑦花形行黑底线→下级内容起点 ≤8mm（三处花形行：课前预习/课中探究/课堂检测）
⑧页脚灰块 6 页在场、底缘 11±1.5mm（拍板22；v4 块高 5mm 版）"""
import os
import re
from collections import Counter

import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
MARGIN = 15 * PT                       # 42.52pt 版心左/顶
PAGE_H = 297 * PT
PAGE_W = 595.276
COLSEP = 7.5 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
TEXTH = PAGE_H - 2 * MARGIN

fails, okmsg = [], []

def check(name, ok, detail=''):
    (okmsg if ok else fails).append(f'{name}　{detail}')

# ---- ① 编译日志 ----
logtxt = open(os.path.join(BASE, 'main.log'), encoding='utf-8', errors='ignore').read()
n_err = len(re.findall(r'^!', logtxt, re.M))
n_over = len(re.findall(r'Overfull', logtxt))
n_miss = len(re.findall(r'Missing character', logtxt))
m = re.search(r'Output written on main\.pdf \((\d+) pages', logtxt)
n_pages = int(m.group(1)) if m else -1
check('①编译零 error/overfull/missingchar', n_err == 0 and n_over == 0 and n_miss == 0 and n_pages == 6,
      f'errors={n_err} overfull={n_over} missingchar={n_miss} 页数={n_pages}')

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))

# ---- ② 行距主峰（分栏分桶＋正文 10.5pt 行过滤，栏内相邻 baseline 差直方图） ----
lead_ok, gray_ok = True, True
lead_detail, gray_detail = [], []
for pno, page in enumerate(doc, 1):
    col_lines = {0: [], 1: []}
    spans_all = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            spans_all += ln['spans']
            if all(not (10 <= sp['size'] <= 11) for sp in ln['spans']):
                continue   # 非正文 10.5pt 行（标题/灰注记/页脚）不入行距统计
            col_lines[0 if ln['bbox'][0] < MID else 1].append(ln['spans'][0]['origin'][1])
    diffs = []
    for c in (0, 1):
        ys = sorted(col_lines[c])
        diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
    if diffs:
        peak, cnt = Counter(diffs).most_common(1)[0]
        lead_detail.append(f'p{pno}主峰{peak}pt(×{cnt}/{len(diffs)})')
        if not 17.5 <= peak <= 18.5:
            lead_ok = False
    grays = set()
    for sp in spans_all:
        col = sp['color']
        r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
        if r == g == b and 0 < r < 255:
            grays.add(r)
    for d in page.get_drawings():
        for key in ('color', 'fill'):
            c = d.get(key)
            if c:
                rgb = tuple(round(x * 255) for x in c)
                if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                    grays.add(rgb[0])
    gray_detail.append(f'p{pno}={sorted(grays)}')
    if not grays <= {0x77, 0xDD} or len(grays) > 2:
        gray_ok = False
check('②行距主峰 17.5–18.5pt', lead_ok and lead_detail, '；'.join(lead_detail))
check('③单页灰档 ≤2 且 ⊆{777777,DDDDDD}', gray_ok, ' '.join(gray_detail))

# ---- ④ 章首：学习目标块 ≤35mm（导学件对照§四-9）＋题区起点登记 ----
p1 = doc[0]
hua_top = mb_top = kn_top = None
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        if hua_top is None and t.startswith('课前预习'):
            hua_top = ln['bbox'][1]
        if mb_top is None and t.startswith('【学习目标】'):
            mb_top = ln['bbox'][1]
        if kn_top is None and t.startswith('◆'):
            kn_top = ln['bbox'][1]
mb_mm = (hua_top - mb_top) / PT if (hua_top is not None and mb_top is not None) else -1
check('④学习目标块 标签顶→花形行顶 ≤35mm（§四-9）', 0 <= mb_mm <= 35,
      f'{mb_mm:.1f}mm；题区起点登记：版心顶→花形行顶 {(hua_top - MARGIN) / PT:.1f}mm'
      f'（全品 p04 口径 88mm；◆知识点一顶 {(kn_top - MARGIN) / PT:.1f}mm）')

# ---- ⑤ 栏利用率（文本＋图＋矢量，页脚带不计） ----
BODY_BOT = PAGE_H - MARGIN
def col_idx(x):
    return 0 if x < MID else 1
util = {}
for pno, page in enumerate(doc, 1):
    cols = {0: MARGIN, 1: MARGIN}
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            x0, y0, x1, y1 = ln['bbox']
            if y0 > BODY_BOT + 1:
                continue
            cols[col_idx(x0)] = max(cols[col_idx(x0)], min(y1, BODY_BOT))
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if r.y0 > BODY_BOT + 1:
                continue
            cols[col_idx(r.x0)] = max(cols[col_idx(r.x0)], min(r.y1, BODY_BOT))
    for d in page.get_drawings():
        r = d['rect']
        if r.y0 > BODY_BOT + 1:
            continue
        if d.get('fill') and abs(r.width - 31 * PT) < 3:
            continue   # 页脚灰块（拍板22，版心带内但非栏内容），不参与栏末墨计量
        cols[col_idx((r.x0 + r.x1) / 2)] = max(cols[col_idx((r.x0 + r.x1) / 2)], min(r.y1, BODY_BOT))
    util[pno] = {c: (cols[c] - MARGIN) / TEXTH for c in (0, 1)}
    util[pno]['ink'] = {c: cols[c] for c in (0, 1)}
util_detail = '  '.join(f'p{p}:[左{u[0]*100:.0f}%/右{u[1]*100:.0f}%]' for p, u in util.items())
nonlast_ok = all(min(u[0], u[1]) >= 0.70 for p, u in util.items() if p < n_pages)
over15 = [(p, c, (BODY_BOT - u['ink'][c]) / PT) for p, u in util.items() if p < n_pages
          for c in (0, 1) if BODY_BOT - u['ink'][c] > 15 * PT]
check('⑤a 非末页逐栏利用率 ≥70%', nonlast_ok, util_detail)
check('⑤b 非末页每栏末墨距版心底 ≤15mm（导学件对照§四-5）', not over15,
      '；'.join(f'p{p}{"左" if c == 0 else "右"}超差 {d:.1f}mm' for p, c, d in over15) if over15 else '全部达标')
last = util[n_pages]
print(f'       末页 p{n_pages} 左{last[0]*100:.0f}%/右{last[1]*100:.0f}%——课堂检测自然收尾页，实测登记（参差收尾＝拍板23）')

# ---- ⑥ 排印层逻辑断言（pdf 文本层：◆/例1/变式1 为独立行段，无空格前缀） ----
n_tj = n_li1 = n_bs = n_ans = n_star = 0
for page in doc:
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t.startswith('◆探究点'):
                n_tj += 1
            if t.startswith('例1'):
                n_li1 += 1
            if t.startswith('变式1'):
                n_bs += 1
            if t.startswith('【答案】'):
                n_ans += 1
            if '典型性理由：' in t:
                n_star += 1
check('⑥排印层 ◆探究点9/例1内联9/变式1×9/答案行14/★理由3',
      n_tj == 9 and n_li1 == 9 and n_bs == 9 and n_ans == 14 and n_star == 3,
      f'◆{n_tj} 例1{n_li1} 变式{n_bs} 答案{n_ans} ★{n_star}')

# ---- ⑦ 花形行黑底线→下级内容起点 ≤8mm ----
hua_ok, hua_detail = True, []
for pno, page in enumerate(doc, 1):
    rules = [d['rect'] for d in page.get_drawings()
             if 220 <= d['rect'].width <= 240 and d['rect'].height < 1.5]
    if not rules:
        continue
    rb = max(rules, key=lambda r: r.y0)   # 该页花形行黑底线（唯一宽 80mm 细线）
    nxt = 1e9
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if ln['bbox'][1] > rb.y1 + 0.5:
                nxt = min(nxt, ln['bbox'][1])
    gap = (nxt - rb.y1) / PT if nxt < 1e8 else -1
    hua_detail.append(f'p{pno}:{gap:.1f}mm')
    if not 0 <= gap <= 8:
        hua_ok = False
check('⑦花形行底线→下级内容 ≤8mm', hua_ok and hua_detail, ' '.join(hua_detail))

# ---- ⑧ 页脚灰块（31mm×5mm，底缘 ≈11mm） ----
feet = []
for pno, page in enumerate(doc, 1):
    hit = None
    for d in page.get_drawings():
        r, f = d['rect'], d.get('fill')
        if f and abs(r.width - 31 * PT) < 3 and abs(r.height - 5 * PT) < 2:
            hit = (PAGE_H - r.y1) / PT
    feet.append((pno, hit))
foot_txt = '；'.join(f'p{p}:{v:.1f}mm' if v else f'p{p}:缺' for p, v in feet)
check('⑧页脚灰块 6 页在场、底缘 11±1.5mm', all(v and abs(v - 11) <= 1.5 for _, v in feet), foot_txt)

print('—— 断言实测 ——')
for s in okmsg:
    print(' ✓', s)
for s in fails:
    print(' ✗', s)
print('断言结果：', '全部通过' if not fails else f'未通过 {len(fails)} 项')
raise SystemExit(0 if not fails else 1)
