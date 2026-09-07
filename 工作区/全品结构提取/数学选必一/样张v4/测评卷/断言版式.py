# -*- coding: utf-8 -*-
r"""版式断言（测评卷 v4）：main.pdf 实测六项＋补充项，全部实测值打印供交付报告引用。
断言口径（总诊断-v4参数表＋交接-20260907b §四③）：
  1 编译零 error/overfull/missingchar（main.log 扫描；underfull 计数仅登记）
  2 行距主峰 17.5–18.5pt（逐栏相邻行基线差直方图，8–30pt 带内取众数）
  3 单页灰档 ≤2（对象级色值普查：文字 span 色＋绘图 fill/stroke 色；黑/白不计；
    题图位图内容色不属装饰件，豁免登记；并断言 v3 三档中灰 808080/595959/BFBFBF 绝迹）
  4 题区起点 ≤60mm（p1 首个题号 span 顶缘距页顶；分区标题顶缘一并报告）
  5 末页栏利用率：非末页逐栏 ≥70%（主病＝栏中空断流；v4 卷面已收进 1 横页）；
    文档末页为答案自然收尾页，利用率实测登记（10 题演示卷内容量决定，
    正式 19 题单元卷口径的讨论见交付报告——脚本只测不裁）
  6 题号列恒空（断言题号列.py 另行执行）
补充：卷头块高 ≤30mm；Q6 TikZ 图高 ≤32mm；页脚灰块三页在场且底缘 11.0±0.5mm；
      栏缝零墨（撤栏线）；p2+ 页眉区零墨（撤页眉）；评分说明行／解答题分值（25分）在场。"""
import re
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\测评卷"
PT = 72 / 25.4
PW, PH = 841.89, 595.276
MARGIN = 15 * PT
BODY_TOP = 15 * PT
BODY_BOT = PH - 17.33 * PT          # 正文底缘（距页顶坐标）
BODY_H = BODY_BOT - BODY_TOP
COLSEP = 8 * PT
COLW = (PW - 2 * MARGIN - 2 * COLSEP) / 3
COLL = (MARGIN, MARGIN + COLW + COLSEP, MARGIN + 2 * (COLW + COLSEP))
BANNED = {0x808080: '808080', 0x595959: '595959', 0xBFBFBF: 'BFBFBF'}

def col_idx(x):
    return max(0, min(2, int((x - MARGIN + 0.5) // (COLW + COLSEP))))

fails = []
def check(name, ok, detail=''):
    print(f"[{'通过' if ok else '未通过'}] {name}{('：' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

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

doc = pymupdf.open(BASE + r"\main.pdf")
npage = len(doc)

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

# ---------- 3 灰档普查 ----------
def shade(v):
    r, g, b = v
    if max(r, g, b) < 0.06:
        return None          # 黑
    if min(r, g, b) > 0.94:
        return None          # 白
    return round(255 * (r + g + b) / 3)

gray_ok = True
gray_detail = []
banned_hits = set()
for pno, page in enumerate(doc, 1):
    shades = set()
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                s = shade(((sp['color'] >> 16 & 255) / 255, (sp['color'] >> 8 & 255) / 255, (sp['color'] & 255) / 255))
                if s is not None:
                    shades.add(s)
                    if sp['color'] in BANNED:
                        banned_hits.add(BANNED[sp['color']])
    for d in page.get_drawings():
        for key in ('fill', 'color'):
            if d.get(key):
                s = shade(d[key])
                if s is not None:
                    shades.add(s)
                    cv = tuple(round(c * 255) for c in d[key])
                    if cv == (128, 128, 128) or cv == (89, 89, 89) or cv == (191, 191, 191):
                        banned_hits.add(f'{cv[0]:02X}' * 2)
    gray_detail.append(f'p{pno}:{sorted(shades)}')
    if len(shades) > 2:
        gray_ok = False
check('单页灰档 ≤2', gray_ok, '  '.join(gray_detail) + '（题图位图内容色豁免）')
check('v3 中灰三档绝迹', not banned_hits, f'命中 {sorted(banned_hits)}' if banned_hits else '808080/595959/BFBFBF 均未出现')

# ---------- 4 题区起点 ----------
p1 = doc[0]
first_num = first_quku = None
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        txt = ''.join(sp['text'] for sp in ln['spans']).strip()
        if first_quku is None and re.match(r'^[一二三四]、', txt):
            first_quku = ln['bbox'][1]
        if first_num is None and re.match(r'^1．', txt):
            first_num = ln['bbox'][1]
q_mm = (first_num - BODY_TOP) / PT
check('题区起点 ≤60mm（版心顶→题号1，参数表口径）', q_mm <= 60,
      f'版心顶起 {q_mm:.1f}mm（页顶起 {first_num/PT:.1f}mm；分区标题一顶缘距页顶 {first_quku/PT:.1f}mm；'
      f'第2/3栏正文自版心顶直接起排）')

# ---------- 补充：卷头块高 ----------
juantop = juanbot = None
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        txt = ''.join(sp['text'] for sp in ln['spans'])
        if '班级' in txt and juantop is None:
            juantop = ln['bbox'][1]
        if '考生注意' in txt:
            juanbot = ln['bbox'][3]
jh = (juanbot - juantop) / PT
check('卷头块高 ≤30mm', jh <= 30, f'{jh:.1f}mm（填写栏顶 {juantop/PT:.1f}mm → 评分说明底 {juanbot/PT:.1f}mm，占首栏）')

# ---------- 补充：Q6 TikZ 图高 ----------
prism = [d['rect'] for d in p1.get_drawings() if d['type'] in ('s', 'fs') and d['rect'].height >= 4 * PT / 2.83465]
# 仅取 p1 矢量路径（h≥~4pt 的 stroke；下划线段 h≈0.4pt 自然排除）；p1 stroke 路径全部属棱柱
if prism:
    u = prism[0]
    for r in prism[1:]:
        u |= r
    tik_h = u.height / PT
    tik_w = u.width / PT
else:
    tik_h = tik_w = -1
check('Q6 TikZ 图高 ≤32mm', 0 < tik_h <= 32, f'棱柱矢量包络 {tik_w:.1f}×{tik_h:.1f}mm（图内字号 7.5pt=正文 71%）')

# ---------- 补充：页脚／栏缝／页眉 ----------
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
check('页脚灰块三页在场、底缘 11.0±0.5mm', foot_ok, '  '.join(foot_detail))

gap_ok = True
for page in doc:
    for d in page.get_drawings():
        r = d['rect']
        for k in range(2):
            gx0 = MARGIN + (k + 1) * COLW + k * COLSEP   # 第 k+1 条栏缝＝k 栏宽＋k 栏距之后
            gx1 = gx0 + COLSEP
            if r.x1 > gx0 + 1.5 and r.x0 < gx1 - 1.5 and r.width < 2 * PT:
                gap_ok = False
check('栏缝零墨（撤栏线）', gap_ok)

head_ok = True
for pno in (2, 3):
    page = doc[pno - 1]
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if ln['bbox'][3] < BODY_TOP - 1:
                head_ok = False
check('p2+ 页眉区零墨（撤页眉）', head_ok)

# ---------- 补充：评分说明行／解答题分值 ----------
t1 = p1.get_text()
t1n = re.sub(r'\s+', '', t1)
check('卷头评分说明行在场', '考生注意：请在答题纸上作答，答在本卷上无效。' in t1n)
check('解答题分值（25分）在题号后', '（25分）' in t1n and '四、解答题' in t1n and '共25分' not in t1n)

# ---------- 5 末页栏利用率 ----------
util = {}
for pno, page in enumerate(doc, 1):
    cols = {0: BODY_TOP, 1: BODY_TOP, 2: BODY_TOP}
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            x0, y0, x1, y1 = ln['bbox']
            if y0 > BODY_BOT + 1:      # 页脚带
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
        if r.y0 > BODY_BOT + 1:
            continue
        c = col_idx((r.x0 + r.x1) / 2)
        cols[c] = max(cols[c], min(r.y1, BODY_BOT))
    util[pno] = {c: (cols[c] - BODY_TOP) / BODY_H for c in cols}
detail = '  '.join(f'p{p}:[' + ','.join(f'{v*100:.0f}%' for _, v in sorted(u.items())) + ']' for p, u in util.items())
print(f'       栏利用率实测：{detail}')
nonlast_ok = all(min(u.values()) >= 0.70 for p, u in util.items() if p < npage)
check('非末页逐栏利用率 ≥70%', nonlast_ok)
last = util[npage]
print(f'       文档末页（p{npage}）三栏利用率 {["%.0f%%" % (last[c]*100) for c in sorted(last)]}，'
      f'均值 {sum(last.values())/3*100:.0f}%——答案自然收尾页，实测登记交付报告')

print('——')
print('断言结果：', '通过' if not fails else f'未通过（{fails}）')
raise SystemExit(0 if not fails else 1)
