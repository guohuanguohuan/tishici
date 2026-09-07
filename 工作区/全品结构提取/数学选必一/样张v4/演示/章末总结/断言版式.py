# -*- coding: utf-8 -*-
r"""版式断言（演示波④章末总结）：承 演示/滚动小卷/断言版式.py 拷贝改造，差异逐条登记：
  · 路径改 演示/章末总结；版式改 A4 竖放双栏（PAGE_W=595.276/PAGE_H=841.89、四边 15mm、
    栏缝 7.5mm、COLW≈244.49pt）并新增页面尺寸断言——滚动小卷为横放三栏；
  · 题区起点断言改「花形行顶 ≤60mm 硬门（版心顶→首个花形行文字顶缘）＋首题号（例1）
    顶缘实测登记」——本件无题号 1．；
  · 灰档断言改全集口径：全文档灰档 ⊆ {119, 221}（777777 注记档＋DDDDDD 页脚块，
    纯黑白豁免）——滚动小卷为单页灰档 ≤2 计数口径；
  · 栏利用率不设 70% 硬门：本件 2 页、无答案页，任务书明示演示件不足页按参差收尾登记，
    逐页双栏实测登记；
  · 卷头块高／题9 TikZ 图高／卷名范围分值断言删除（本件无卷头、无 TikZ、无分值口径），
    新增 p1「第1章 空间向量与立体几何＋章末总结提升」件名在场断言；
  · 其余口径不变（编译零 error/overfull/missingchar、行距主峰 17.5–18.5pt、
    页脚灰块逐页在场底缘 11.0±0.5mm、栏缝零墨、p2+ 页眉区零墨）。"""
import re
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\演示\章末总结"
PT = 72 / 25.4
PW, PH = 595.276, 841.89
MARGIN = 15 * PT
BODY_TOP = MARGIN
BODY_BOT = PH - MARGIN
COLSEP = 7.5 * PT
COLW = (PW - 2 * MARGIN - COLSEP) / 2
GRAY_OK = {119, 221}

def col_idx(x):
    return max(0, min(1, int((x - MARGIN + 0.5) // (COLW + COLSEP))))

fails = []
def check(name, ok, detail=''):
    print(f"[{'通过' if ok else '未通过'}] {name}{('：' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

# ---------- 0 页面尺寸 ----------
doc = pymupdf.open(BASE + r"\main.pdf")
sz_ok = all(abs(p.rect.width - PW) < 0.5 and abs(p.rect.height - PH) < 0.5 for p in doc)
check('页面尺寸 595.276×841.89pt（A4 竖放）', sz_ok,
      f'实测 {doc[0].rect.width:.3f}×{doc[0].rect.height:.3f}pt，共 {len(doc)} 页')
npage = len(doc)

# ---------- 1 编译日志 ----------
log = open(BASE + r"\main.log", encoding='utf-8', errors='ignore').read()
n_err = len(re.findall(r'^!', log, re.M))
n_over = len(re.findall(r'Overfull', log))
n_undef_err = len(re.findall(r'Undefined control sequence', log))
n_miss = len(re.findall(r'Missing character', log))
n_under = len(re.findall(r'Underfull', log))
check('编译 error=0', n_err == 0 and n_undef_err == 0, f'error {n_err}')
check('编译 overfull=0', n_over == 0, f'overfull {n_over}')
check('编译 missingchar=0', n_miss == 0, f'missing {n_miss}')
print(f'       （登记）underfull {n_under}')

# ---------- 2 行距主峰 ----------
from collections import Counter
hist = Counter()
for page in doc:
    lines = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            x0, y0, x1, y1 = ln['bbox']
            lines.append((col_idx(x0), y0, y1))
    lines.sort()
    prev = {}
    for c, y0, y1 in lines:
        if c in prev:
            d = y0 - prev[c]
            if 8 < d < 30:
                hist[round(d, 1)] += 1
        prev[c] = y0
peak_d, peak_n = hist.most_common(1)[0]
top3 = hist.most_common(3)
check('行距主峰 17.5–18.5pt', 17.5 <= peak_d <= 18.5,
      f'主峰 {peak_d:.1f}pt（{peak_n} 次）；前三 {[(round(d,1), n) for d, n in top3]}')

# ---------- 3 灰档全集 ⊆ {119, 221} ----------
def shade(v):
    r, g, b = v
    if max(r, g, b) < 0.06:
        return None
    if min(r, g, b) > 0.94:
        return None
    return round(255 * (r + g + b) / 3)

shades_all = set()
detail = []
for pno, page in enumerate(doc, 1):
    shades = set()
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                s = shade(((sp['color'] >> 16 & 255) / 255, (sp['color'] >> 8 & 255) / 255, (sp['color'] & 255) / 255))
                if s is not None:
                    shades.add(s)
    for d in page.get_drawings():
        for key in ('fill', 'color'):
            if d.get(key):
                s = shade(d[key])
                if s is not None:
                    shades.add(s)
    shades_all |= shades
    detail.append(f'p{pno}:{sorted(shades)}')
check('全文档灰档 ⊆ {119, 221}（777777＋DDDDDD）', shades_all <= GRAY_OK,
      '  '.join(detail) + f'；越档 {sorted(shades_all - GRAY_OK)}' if not shades_all <= GRAY_OK else '  '.join(detail))

# ---------- 4 花形行顶 ≤60mm 硬门＋首题号顶缘登记 ----------
p1 = doc[0]
hua_top = li_top = None
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        txt = ''.join(sp['text'] for sp in ln['spans']).strip()
        if hua_top is None and re.match(r'^题型归类$', txt):
            hua_top = ln['bbox'][1]
        if li_top is None and re.match(r'^例1', txt):
            li_top = ln['bbox'][1]
h_mm = (hua_top - BODY_TOP) / PT
check('花形行顶 ≤60mm（版心顶→花形行「题型归类」顶缘）', h_mm <= 60, f'{h_mm:.1f}mm')
li_mm = (li_top - BODY_TOP) / PT
print(f'       （登记）首题号（题型一 例1）顶缘：版心顶起 {li_mm:.1f}mm')

# ---------- 5 页脚灰块 ----------
foot_ok = True
foot_detail = []
for pno, page in enumerate(doc, 1):
    hit = None
    for d in page.get_drawings():
        r = d['rect']
        if d['fill'] and tuple(round(c, 2) for c in d['fill']) == (0.87, 0.87, 0.87):
            hit = (PH - r.y1) / PT
    if hit is None or abs(hit - 11.0) > 0.5:
        foot_ok = False
    foot_detail.append(f'p{pno}:{hit:.2f}mm' if hit else f'p{pno}:缺')
check('页脚灰块逐页在场、底缘 11.0±0.5mm', foot_ok, '  '.join(foot_detail))

# ---------- 6 栏缝零墨／页眉零墨 ----------
gap_ok = True
for page in doc:
    for d in page.get_drawings():
        r = d['rect']
        gx0 = MARGIN + COLW
        gx1 = gx0 + COLSEP
        if r.x1 > gx0 + 1.5 and r.x0 < gx1 - 1.5 and r.width < 2 * PT:
            gap_ok = False
check('栏缝零墨（撤栏线）', gap_ok)

head_ok = True
for pno in range(2, npage + 1):
    page = doc[pno - 1]
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if ln['bbox'][3] < BODY_TOP - 1:
                head_ok = False
check('p2+ 页眉区零墨（撤页眉）', head_ok)

# ---------- 7 件名在场（p1） ----------
t1 = re.sub(r'\s+', '', p1.get_text())
check('件名在场（p1）：第1章＋章末总结提升', '第1章空间向量与立体几何' in t1 and '章末总结提升' in t1)

# ---------- 8 栏利用率（实测登记，无硬门） ----------
util = {}
for pno, page in enumerate(doc, 1):
    cols = {0: BODY_TOP, 1: BODY_TOP}
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            x0, y0, x1, y1 = ln['bbox']
            if y0 > BODY_BOT + 1:
                continue
            c = col_idx(x0)
            cols[c] = max(cols[c], y1)
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if r.y0 > BODY_BOT + 1:
                continue
            c = col_idx(r.x0)
            cols[c] = max(cols[c], r.y1)
    for d in page.get_drawings():
        r = d['rect']
        if r.y0 > BODY_BOT + 1 or r.y1 > BODY_BOT + 3:
            continue
        c = col_idx((r.x0 + r.x1) / 2)
        cols[c] = max(cols[c], min(r.y1, BODY_BOT))
    util[pno] = {c: (cols[c] - BODY_TOP) / (BODY_BOT - BODY_TOP) for c in cols}
detail = '  '.join(f'p{p}:[' + ','.join(f'{v*100:.0f}%' for _, v in sorted(u.items())) + ']' for p, u in util.items())
print(f'       栏利用率实测：{detail}')
last = util[npage]
print(f'       末页（p{npage}）双栏利用率 {["%.0f%%" % (last[c]*100) for c in sorted(last)]}，'
      f'均值 {sum(last.values())/2*100:.0f}%——演示件参差收尾口径，实测登记交付报告（任务书豁免，无硬门）')

print('——')
print('断言结果：', '通过' if not fails else f'未通过（{fails}）')
raise SystemExit(0 if not fails else 1)
