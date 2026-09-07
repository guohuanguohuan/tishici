# -*- coding: utf-8 -*-
r"""断言v4.py——v4 练习件六项断言实测（交付报告证据源）＋版式细目测量。
断言口径（交接-20260907b §四；总诊断-v4参数表 §一断言列）：
  ①编译零 error/overfull/missingchar（扫 main.log）
  ②行距主峰 17.5–18.5pt——按列分桶（x0<MID 分左右栏），栏内按 origin 排序取相邻差
    5–40pt 作直方图取峰（块级分组会把双栏行混编，作废）
  ③单页灰档 ≤2（拍板27，黑/白不计）
  ④题区起点 ≤60mm——版心顶→「夯基达标」组行字面顶（A13 方块是章首装饰件，
    不是题区起点，旧口径作废）
  ⑤末页栏利用率 ≥70%（\raggedcolumns；页脚行 y0≥278mm 排除——页码块顶 278.2mm
    在版心底 277.5mm 之下方，属页脚区）
  ⑥题↔答案区一一对应（逻辑断言④）——题号/答案行统一口径「行首 ^\d+． 且
    x0<栏左+3pt」（题号顶格题号列；题7 题侧 6.5pt 与题号被 PDF 拆行，按行首匹配兜住）
细目：页码块底距页底 ≈11mm（拍板22；底边距 19.5mm 冲突裁决后实测 11.00mm）、
章首方块 13.9×16.8mm #777777（A13）、灰值集合 ⊆ {777777, DDDDDD}、
raster 图 0（TikZ 矢量化，拍板24）。
版面基准（main.tex 现行）：边距上/左/右 15mm、下 19.5mm（底边距冲突裁决，L225 待过目），
版心高 262.5mm，版心底 277.5mm，页码块顶 278.2mm。"""
import re
from collections import Counter

import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\练习件"
PT = 72 / 25.4
MARGIN_T = 15 * PT                       # 版心顶
MARGIN_B = 19.5 * PT                     # 底边距（冲突裁决值）
PAGE_H = 297 * PT
PAGE_W = 595.276
COLSEP = 7.5 * PT
COLW = (PAGE_W - 2 * 15 * PT - COLSEP) / 2
MID = 15 * PT + COLW + COLSEP / 2        # 栏中缝
COLL = (15 * PT, 15 * PT + COLW + COLSEP)
TEXTH = PAGE_H - MARGIN_T - MARGIN_B     # 版心高 262.5mm
FOOT_Y0 = 278 * PT                       # 页脚区起点（块顶 278.2mm 上方留 0.2mm）

fail = []
okmsg = []

# ---- ① 编译日志 ----
logtxt = open(BASE + r'\main.log', encoding='utf-8', errors='ignore').read()
n_err = len(re.findall(r'^!', logtxt, re.M))
n_over = len(re.findall(r'Overfull', logtxt))
n_miss = len(re.findall(r'Missing character', logtxt))
m = re.search(r'Output written on main.pdf \((\d+) pages', logtxt)
n_pages = int(m.group(1)) if m else -1
(okmsg if (n_err == 0 and n_over == 0 and n_miss == 0) else fail).append(
    f'①编译 errors={n_err} overfull={n_over} missingchar={n_miss} 页数={n_pages}')

doc = pymupdf.open(BASE + r'\main.pdf')
grays_ok, gray_all = True, {}
lead_peak_all = []
for pno, page in enumerate(doc, 1):
    # ---- ② 行距直方图（按列分桶，栏内排序取相邻 origin 差） ----
    buckets = ([], [])
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if not ln['spans']:
                continue
            sp0 = max(ln['spans'], key=lambda s: s['size'])
            if sp0['size'] < 9.5:          # 只计正文级行（题侧 6.5pt/图内 7.5pt 不计）
                continue
            ci = 0 if ln['bbox'][0] < MID else 1
            buckets[ci].append(sp0['origin'][1])
    diffs = []
    for ys in buckets:
        ys.sort()
        for a, b in zip(ys, ys[1:]):
            dy = b - a
            if 5 < dy < 40:
                diffs.append(round(dy * 4) / 4)
    if diffs:
        c = Counter(diffs)
        peak, cnt = c.most_common(1)[0]
        lead_peak_all.append((pno, peak, cnt, len(diffs)))
    # ---- ③ 灰档普查（span 字色＋描边/填充） ----
    grays = set()
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
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
    gray_all[pno] = sorted(grays)
    if not grays <= {0x77, 0xDD} or len(grays) > 2:
        grays_ok = False

peak_txt = '；'.join(f'p{p}主峰{pk}pt(×{n}/{t})' for p, pk, n, t in lead_peak_all)
ok = all(17.5 <= pk <= 18.5 for _, pk, _, _ in lead_peak_all) and lead_peak_all
(okmsg if ok else fail).append(f'②行距主峰 {peak_txt}（要求各页主峰 17.5–18.5pt）')
(okmsg if grays_ok else fail).append(
    f'③单页灰档 ' + '；'.join(f'p{p}={v}' for p, v in gray_all.items()) + '（要求 ≤2 且 ⊆{77,221}）')

# ---- ④ 题区起点（p1：版心顶→「夯基达标」组行字面顶） ----
page1 = doc[0]
hua_y0 = None
for blk in page1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans'])
        if '夯基达标' in t:
            hua_y0 = ln['bbox'][1] if hua_y0 is None else min(hua_y0, ln['bbox'][1])
q1_top = None
for blk in page1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        if re.match(r'^1．', t) and ln['bbox'][0] < 15 * PT + 3:
            q1_top = ln['bbox'][1]
            break
start_mm = (hua_y0 - MARGIN_T) / PT if hua_y0 is not None else None
ok4 = start_mm is not None and start_mm <= 60
(okmsg if ok4 else fail).append(
    f'④题区起点 版心顶→夯基达标行顶 {start_mm:.1f}mm（≤60；全品 58.2；题1 字面顶 '
    + (f'{(q1_top - MARGIN_T) / PT:.1f}mm' if q1_top else '未检出') + '）'
    if start_mm is not None else '④题区起点 未检出组行')
# ---- A13 方块尺寸/色值细目 ----
cube = [d for d in page1.get_drawings()
        if d.get('fill') and abs(d['rect'].width - 13.9 * PT) < 3
        and abs(d['rect'].height - 16.8 * PT) < 3]
cube_col = ''
if cube:
    rgb = tuple(round(x * 255) for x in cube[0]['fill'])
    cube_col = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
okmsg.append(f'· A13 章首方块 {len(cube)} 只 13.9×16.8mm {cube_col}（要求 #777777）'
             + ('' if cube and cube_col == '#777777' else ' ⚠校验'))

# ---- ⑤ 末页栏利用率（\raggedcolumns；页脚区 y0≥278mm 排除） ----
last = doc[-1]
colmax = [0.0, 0.0]
for blk in last.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        x0, y0, x1, y1 = ln['bbox']
        if y0 >= FOOT_Y0:              # 页脚行不计（页码/小字）
            continue
        t = ''.join(sp['text'] for sp in ln['spans'])
        if t.strip().isdigit() and y1 > 280 * PT:
            continue
        ci = 0 if x0 < MID else 1
        if 15 * PT - 2 <= x0 <= COLL[1] + COLW + 2:
            colmax[ci] = max(colmax[ci], y1)
for d in last.get_drawings():
    r = d['rect']
    if r.y0 >= FOOT_Y0 or r.y1 < MARGIN_T:
        continue
    if abs(r.width - 31 * PT) < 3:     # 页码灰块
        continue
    ci = 0 if r.x0 < MID else 1
    if 15 * PT - 2 <= r.x0 <= COLL[1] + COLW + 2:
        colmax[ci] = max(colmax[ci], r.y1)
fills = [(y - MARGIN_T) / TEXTH * 100 for y in colmax]
page_fill = max(fills)
ok5 = page_fill >= 70
(okmsg if ok5 else fail).append(
    f'⑤末页(p{n_pages})栏利用率 左{fills[0]:.1f}%／右{fills[1]:.1f}%（≥70；栏墨底 左'
    f'{colmax[0] / PT:.1f}／右{colmax[1] / PT:.1f}mm vs 版心底 {(PAGE_H - MARGIN_B) / PT:.1f}mm，'
    f'A1 左栏满到底 {"✓" if colmax[0] >= (PAGE_H - MARGIN_B) - 2 * 18 else "✗"}）')

# ---- ⑥ 题↔答案一一对应（逻辑断言④）＋题号列细目（x0 口径） ----
qnos, anos = [], []
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            cl = COLL[0] if ln['bbox'][0] < MID else COLL[1]
            mq = re.match(r'^(\d+)．', t)
            if mq and ln['bbox'][0] < cl + 3:
                if pno == 1 and '【答案】' not in t:
                    qnos.append(int(mq.group(1)))
                elif pno == n_pages:
                    # 答案行口径＝行首题号顶格（\ansul 下划线盒会致「N．」与「【答案】」被
                    # PDF 拆行，不得要求同行；续行恒悬挂缩进 7mm 不会误入）
                    anos.append(int(mq.group(1)))
ok6 = len(qnos) == 11 and len(anos) == 11 and qnos == anos == list(range(1, 12))
(okmsg if ok6 else fail).append(
    f'⑥题↔答案一一对应 题号{qnos} 答案{anos}（各 11 条、序号 1..11 连续对位）')

# ---- 细目：页码块位置（拍板22 ≈11mm）----
feet = []
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r, f = d['rect'], d.get('fill')
        if f and abs(r.width - 31 * PT) < 3 and abs(r.height - 7.8 * PT) < 3:
            feet.append((pno, (PAGE_H - r.y1) / PT))
foot_txt = '；'.join(f'p{p} 底距页底 {v:.2f}mm' for p, v in feet)
foot_ok = all(9.5 <= v <= 12.5 for _, v in feet) and feet
(okmsg if foot_ok else fail).append(f'· 页码块{foot_txt}（要求 ≈11±1.5mm，拍板22）')
okmsg.append(f'· 题区题号 {len(qnos)}、答案行 {len(anos)}、raster 图 {sum(len(p.get_images()) for p in doc)}'
             '（TikZ 矢量化→raster=0，拍板24）')

print('—— 断言实测 ——')
for s in okmsg:
    print(' ✓', s)
for s in fail:
    print(' ✗', s)
print('断言结果：', '全部通过' if not fail else f'未通过 {len(fail)} 项')
raise SystemExit(0 if not fail else 1)
