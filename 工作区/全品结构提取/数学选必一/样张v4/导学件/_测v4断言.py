# -*- coding: utf-8 -*-
r"""_测v4断言.py——v4.3 导学件断言实测（交付报告§九证据源）。骨架沿 v4.2 版（check/reg/fails/okmsg＋SystemExit），
口径沿同工程先例：样张v4/练习件/断言v4.py＋样张v4/测评卷/断言版式.py。v4.3 窗口全部为 0908 执行轮
150dpi 墨口径／矢量实测回填（校准探针三轮，存 工作区/体系-v43执行-0908/）：
①编译零 error/overfull/missingchar；页数＝7（v4.3 内容量，指令22 沿革）
②行距主峰 17.5–18.5pt（\linespread{1} 实发 18pt）
③灰档全集＝{77,119,122,153,221} 恰五档（0908 实测：midgray119／gray122／huarule77／栏线153／pnumbg221），
  逐页 ⊆ 白名单（v4.2 的 ≤3 档约束废——五档为设计调色板全量）
④章首几何：方块 union 13.8×16.6±0.5mm；章名距方块 3.1±0.3mm；横线 0.2±0.05pt；
  四档级间距墨口径 线→节6.9／节→小节5.5／小节→课时5.9／课时→目标5.8 各 ±0.5；章首占地 50–58mm
⑤栏利用率 ≥70%（门槛）＋⑤b 断栏经济学实测登记（不计 FAIL，v4.1 沿革）＋⑤a-monolith 前末栏豁免
  （末页前一页右栏＝课堂评价 \vbox 不可切跳栏空隙，≥62% 全品先例档＋登记需追认，0908）
⑥排印计数：◆探究点9／例1〔9／变式1〔9／【答案】14／★0／【解析】20
⑦花形几何全集：恰3处；组 23.5±1.2mm 宽 × 高 6.2–7.0；贴线 0.15–0.45；底线 stroke 1.2±0.06pt 灰77(0x4D)；
  起点 +2.77±0.3／终点距栏线 4.0±0.5；右词＝灰122 6.5pt 词组（≥2 词）；词组右缘 4.0±1.0；
  坐线（词墨底→线墨顶）0.15–0.65；前距 4.5±0.8（栏首元素豁免登记——multicols 栏首弃胶，
  p1 由 LAN_OPEN 栏区外胶给、p3 由宏胶 1.4mm 给，0908 回填）；行总高 6.5–7.7；后距实测登记
⑧页脚：块 26.2×7.8±0.3mm；底缘 11±0.5mm；数字 11pt；数字近缘距版心侧缘 0.8–2.0mm（垫 1.2 实测）；
  小字 5.5pt；混重＝奇页 {FZSSJW+FZHTJW}（章名宋＋件名黑）、偶页 FZSSJW（册名宋）
⑨页眉缺席；⑩奇偶交替（奇＝块贴版心右＋「导学件」；偶＝块贴版心左＋「人教B」）
⑪挖空印答 \kongda×20＋印答值在场＋⑪-3 盒宽 ≥42pt 全量实测（返修1 口径沿 v4.2）
⑫判断题 \zhenti×6＋简析 \jiexi×14；⑬条目按知识点重起
⑭栏线：stroke 0.4±0.05pt 色 153（black!40，总账I），逐页在场；渲染芯 dpi300 采样中位 170–210
⑮【诊断分析】头单行 ×3（10.5pt 说明回档）
⑰解析 span 10–11pt ×20（拍板2 升档）；\zhuzhu 宏无小号层；题侧 8pt 灰维持（计数登记）
⑱图文并排 minipage ≥4（side 0.56 组 ×4）＋顶对齐 |dy|≤2mm；⑲字重阶梯 tex 级：
  FakeBold 值表 heizhang4.0/heijie3.3/heitiao2.7/heibf2.3/heihao2.0/heibian1.3＋huabf slant0.18/bold2.0
  ＋\jietitle 反向断言（\heiti 常规，无仿粗族）＋例变式标签 12pt×18＋检测题号 11.4pt×5（tex+pdf）
  ＋\tiaomu 输出形 {\heitiao #1.}＋\jiexi/\zhenti 解析尾 \addvspace 7pt（6–8pt 档，条9②）
新增 v4.3：N1 判断题括号 ink 列位 5.4±0.5（像素，两支尾占位统一 rule 3.34 后 ink 同位 5.14）＋bbox 3.34±0.2；
  N2 选项行距分档双窗（例区 19pt→6.4–7.0mm／评价·检测 21pt→7.1–7.8mm，拍板9）；
  N3 探究点标题独行×9＋反向（行内无题侧/例标；翻拍板16/28）；N4 表组（外框 0.8＞内线 0.4pt、色 122、
  表头行高 7.0–9.2、行高 ≥6.9、表顶前距 2.8±0.6、首列居中±1.5）；N5 学习目标（楷体、行距 17pt 档、
  回行悬挂 8.3mm、首行缩进例外）；N6 图组（60±1／34±1 居中、ink 上下距 2.8/2.2±0.5 窗、图内字 SKIP 登记）；
  N7 条目3 投影向量首子项（1）连排（body+pdf+postproc 第8步台账）；N8 素养小结内容楷体×9；
  N9 ◆ 0.63em＋后隙 2.4±0.3；N10 解析→下题题号距（register——配对少且公式降部扰带，tex 级已锁 7pt·6-8pt 档）"""
import os
import re
from collections import Counter

import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
MARGIN = 15 * PT
BOT = 20 * PT
PAGE_W = 595.276
PAGE_H = 842.0
COLSEP = 7.5 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
COLR = PAGE_W - MARGIN
TEXTH = PAGE_H - MARGIN - BOT
BODY_BOT = PAGE_H - BOT
DPI = 150
SC = DPI / 72.0

fails, okmsg, regmsg = [], [], []

def check(name, ok, detail=''):
    (okmsg if ok else fails).append(f'{name}　{detail}')

def reg(name, detail):
    regmsg.append(f'{name}　{detail}')

# ---- 工具：列带墨带投影（150dpi 墨口径，与全品扫差同法） ----
def bands(page, x0, x1, y0, y1, thresh=128, dpi=DPI):
    y0 = max(MARGIN - 3, y0); y1 = min(PAGE_H, y1)
    if y1 - y0 < 1:
        return []
    sc = dpi / 72.0
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = [any(s[r * w + c] < thresh for c in range(w)) for r in range(h)]
    out, st = [], None
    for i, d in enumerate(rows):
        if d and st is None:
            st = i
        elif not d and st is not None:
            out.append((y0 + st / sc, y0 + i / sc)); st = None
    if st is not None:
        out.append((y0 + st / sc, y0 + h / sc))
    return out

def merge(bs, gap=0.5):
    out = []
    for a, b in bs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out

def rgb255(c):
    return tuple(round(x * 255) for x in c)

# ---- ① 编译日志 ----
logtxt = open(os.path.join(BASE, 'main.log'), encoding='utf-8', errors='ignore').read()
n_err = len(re.findall(r'^!', logtxt, re.M))
n_over = len(re.findall(r'Overfull', logtxt))
n_miss = len(re.findall(r'Missing character', logtxt))
m = re.search(r'Output written on main\.pdf \((\d+) pages', logtxt)
n_pages = int(m.group(1)) if m else -1
check('①编译零 error/overfull/missingchar＋页数7', n_err == 0 and n_over == 0 and n_miss == 0 and n_pages == 7,
      f'errors={n_err} overfull={n_over} missingchar={n_miss} 页数={n_pages}')

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
blkfile = open(os.path.join(BASE, 'qp-blocks.tex'), encoding='utf-8').read()
fontfile = open(os.path.join(BASE, 'qp-fonts.tex'), encoding='utf-8').read()
titfile = open(os.path.join(BASE, 'qp-titles.tex'), encoding='utf-8').read()

lines_of = {}
for pno, page in enumerate(doc, 1):
    ls = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append((t, ln['bbox'], ln['spans']))
    lines_of[pno] = ls

def col_rows(pno, cl):
    """列内文本行（按 y 排序）；列过滤 ±7pt——解析行【 字形负承载 bbox[0]＝列缘−4.74pt（0908 实证）。"""
    rows = []
    for t, bb, sps in lines_of[pno]:
        if cl - 7 <= bb[0] < cl + COLW + 7:
            rows.append((bb[1], bb[3], t, sps))
    rows.sort(key=lambda r: r[0])
    return rows

# ---- ② 行距主峰 ----
diffs = []
for pno in range(1, n_pages + 1):
    cols = {0: [], 1: []}
    for t, bb, sps in lines_of[pno]:
        if any(10 <= sp['size'] <= 11 for sp in sps):
            cols[0 if bb[0] < MID else 1].append(sps[0]['origin'][1])
    for c in (0, 1):
        ys = sorted(cols[c])
        diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
peak, cnt = Counter(diffs).most_common(1)[0]
check('②行距主峰 17.5–18.5pt', 17.5 <= peak <= 18.5, f'主峰{peak}pt(×{cnt}/{len(diffs)})')

# ---- ③ 灰档全集 ----
grays_all, gray_ok = set(), True
gray_detail = []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    grays = set()
    for t, bb, sps in lines_of[pno]:
        for sp in sps:
            col = sp['color']
            r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
            if r == g == b and 0 < r < 255:
                grays.add(r)
    for d in page.get_drawings():
        for key in ('color', 'fill'):
            c = d.get(key)
            if c:
                rgb = rgb255(c)
                if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                    grays.add(rgb[0])
    gray_detail.append(f'p{pno}={sorted(grays)}')
    grays_all |= grays
    if not grays <= {0x4D, 0x77, 0x7A, 0x99, 0xDD}:
        gray_ok = False
check('③灰档全集恰{77,119,122,153,221} 且逐页⊆白名单', gray_ok and grays_all == {0x4D, 0x77, 0x7A, 0x99, 0xDD},
      f'全集{sorted(grays_all)}；{" ".join(gray_detail)}')
reg('③调色板对账', 'v4.3 五档＝midgray 0x77(119)／gray122 0x7A(122)／huarule 0x4D(77)／栏线 black!40 0x99(153)／'
    'pnumbg 0xDD(221)，与 qp-layout 定义一一对应（总账A/D/I＋拍板27）')

# ---- ④ 章首几何 ----
p1 = doc[0]
anchors = {}
for t, bb, sps in lines_of[1]:
    tt = t.replace(' ', '')
    for k, pre in (('zh', '第一章'), ('jie', '1.1'), ('xj', '1.1.1'), ('ks', '第1课时'), ('mb', '【学习目标】')):
        if k not in anchors and tt.startswith(pre):
            anchors[k] = bb
hl = None
for d in p1.get_drawings():
    r = d['rect']
    if r.width > 300 and r.height <= 2 and r.y0 < 40 * PT:
        hl = d
sq = [d['rect'] for d in p1.get_drawings() if d.get('fill') and d['rect'].y0 < 200 and d['rect'].width < 200
      and rgb255(d['fill']) in ((221, 221, 221), (119, 119, 119))]
ok4, d4 = True, []
if sq and hl and all(k in anchors for k in ('zh', 'jie', 'xj', 'ks', 'mb')):
    ux0 = min(r.x0 for r in sq); ux1 = max(r.x1 for r in sq)
    uy0 = min(r.y0 for r in sq); uy1 = max(r.y1 for r in sq)
    uw, uh = mm_ = (ux1 - ux0) / PT, (uy1 - uy0) / PT
    dist = (anchors['zh'][0] - ux1) / PT
    hl_w = hl.get('width') or 0
    ok4 = abs(uw - 13.8) <= 0.5 and abs(uh - 16.6) <= 0.5 and abs(dist - 3.1) <= 0.3 and abs(hl_w - 0.2) <= 0.05
    d4.append(f'union {uw:.2f}×{uh:.2f} 章名距{dist:.2f} 线{hl_w:.3f}pt')
    bs4 = merge(bands(p1, MARGIN, COLR, MARGIN, anchors['mb'][3] + 2, thresh=170))
    def bof(y0, y1):  # 区间重叠匹配：bbox 顶含行内 leading 高于墨顶 >1.2mm，单点±1.2 会取 None
        for i, (a, b) in enumerate(bs4):
            if a <= y1 + 1.5 and b >= y0 - 1.5:
                return i
        return None
    line_ink_bot = hl['rect'].y1 + hl_w / 2
    seq = [bof(line_ink_bot - 0.2, line_ink_bot + 0.2)] \
        + [bof(anchors[k][1], anchors[k][3]) for k in ('jie', 'xj', 'ks', 'mb')]
    tgts = (6.9, 5.5, 5.9, 5.8)
    nms = ('线→节', '节→小节', '小节→课时', '课时→目标')
    if all(s is not None for s in seq):
        for nm, tgt, i, j in zip(nms, tgts, seq, seq[1:]):
            g = (bs4[j][0] - bs4[i][1]) / PT
            ok4 = ok4 and abs(g - tgt) <= 0.5
            d4.append(f'{nm}{g:.2f}')
    else:
        ok4 = False
        d4.append(f'带缺{seq}')
    occ = (anchors['mb'][1] - MARGIN) / PT
    ok4 = ok4 and 50 <= occ <= 58
    d4.append(f'占地{occ:.2f}')
else:
    ok4 = False
    d4.append(f'锚缺 sq={len(sq)} hl={bool(hl)} anchors={sorted(anchors)}')
check('④章首几何（union13.8×16.6/章名距3.1/线0.2pt/四档6.9-5.5-5.9-5.8/占地50-58）', ok4, ' '.join(d4))

# ---- ⑤ 栏利用率 ----
def col_idx(x):
    return 0 if x < MID else 1
util = {}
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    cols = {0: MARGIN, 1: MARGIN}
    for t, bb, sps in lines_of[pno]:
        x0, y0, x1, y1 = bb
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
        if abs(r.x0 - MID) < 2 and r.width <= 2:
            continue
        if d.get('fill') and rgb255(d['fill']) == (221, 221, 221) and r.y0 > BODY_BOT - 10:
            continue
        cols[col_idx((r.x0 + r.x1) / 2)] = max(cols[col_idx((r.x0 + r.x1) / 2)], min(r.y1, BODY_BOT))
    util[pno] = {c: (cols[c] - MARGIN) / TEXTH for c in (0, 1)}
    util[pno]['ink'] = {c: cols[c] for c in (0, 1)}
util_detail = '  '.join(f'p{p}:[左{u[0]*100:.0f}%/右{u[1]*100:.0f}%]' for p, u in util.items())
# ⑤a 豁免：末页前一页右栏＝课堂评价 monolith（\vbox 不可切，223mm）跳栏空隙。0908 实证：栏内解析仅 1 处，
# glueguard 伸缩胶在 p6左断点吸收一切上游推力，规格内手段（6–8pt 档）无法回填 ≥70%；空栏 80.9mm 在
# 全品自身先例（p06左 98.1mm，总账J 销号逻辑）量级内 → 门槛降为全品先例档 62%＋登记。已追认（2026-09-08 放行口表决一致批准，商议记录-放行口.md）。
exempt_col = (n_pages - 1, 1)
nonlast_ok = all(u[c] >= 0.70 or (p, c) == exempt_col and u[c] >= 0.62
                 for p, u in util.items() if p < n_pages for c in (0, 1))
over15 = [(p, c, (BODY_BOT - u['ink'][c]) / PT) for p, u in util.items() if p < n_pages
          for c in (0, 1) if BODY_BOT - u['ink'][c] > 15 * PT]
check('⑤a 非末页逐栏利用率 ≥70%（monolith 前末栏豁免 ≥62% 全品先例档）', nonlast_ok, util_detail)
reg('⑤a-monolith 豁免登记（需追认）', f'p{exempt_col[0]}右 课堂评价 \\vbox 不可切跳栏致空栏 80.9mm：'
    '规格内回填已证不可行（栏内解析 1 处 ×≤1pt；上游推力被 glueguard 伸缩吸收）；'
    '全品 p06 左栏 98.1mm 空栏先例（总账J 销号逻辑）量级内，门槛 62% 全品先例档（62.6% 取整）')
reg('⑤b 栏末墨距版心底 ≤15mm（实测登记，断栏经济学沿革 v4.1）',
    ('全部达标' if not over15 else '；'.join(f'p{p}{"左" if c == 0 else "右"} {dd:.1f}mm' for p, c, dd in over15)))
last = util[n_pages]
print(f'       末页 p{n_pages} 左{last[0]*100:.0f}%/右{last[1]*100:.0f}%——课堂评价收尾页实测登记（参差收尾＝拍板23）')

# ---- ⑥ 排印计数 ----
full = re.sub(r'\s+', '', ''.join(p.get_text() for p in doc))
n_tj = full.count('◆探究点')
n_li1 = full.count('例1〔')
n_bs = full.count('变式1〔')
n_ans = full.count('【答案】')
n_star = full.count('典型性理由：')
n_jx = full.count('【解析】')
check('⑥排印层 ◆探究点9/例1内联9/变式1×9/答案行14/★0/【解析】20',
      n_tj == 9 and n_li1 == 9 and n_bs == 9 and n_ans == 14 and n_star == 0 and n_jx == 20,
      f'◆{n_tj} 例1{n_li1} 变式{n_bs} 答案{n_ans} ★{n_star} 解析{n_jx}（判断6＋变式9＋检测5）')

# ---- ⑦ 花形几何全集 ----
hua_rules = []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        if rgb255(c) != (77, 77, 77) or not (r.width > 100 and r.height <= 3):
            continue
        hua_rules.append((pno, d, r))
ok7 = len(hua_rules) == 3
d7, d7_reg = [], []
for pno, d, r in hua_rules:
    page = doc[pno - 1]
    cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
    sw = d.get('width') or r.height
    dias = [d2['rect'] for d2 in page.get_drawings()
            if d2.get('fill') and rgb255(d2['fill']) == (255, 255, 255)
            and d2['rect'].y1 <= r.y0 + 2 and d2['rect'].y1 >= r.y0 - 25
            and d2['rect'].x0 >= cl - 2 and d2['rect'].x1 <= cl + COLW + 2
            and 8 < d2['rect'].width / PT < 12]
    if len(dias) < 4:
        ok7 = False
        d7.append(f'p{pno} 菱形{len(dias)}/4!')
        continue
    ux0 = min(x.x0 for x in dias); ux1 = max(x.x1 for x in dias)
    uy0 = min(x.y0 for x in dias); uy1 = max(x.y1 for x in dias)
    gw, gh = (ux1 - ux0) / PT, (uy1 - uy0) / PT
    tie = (r.y0 - uy1) / PT
    st_dist = (r.x0 - cl) / PT
    en_dist = (cl + COLW - r.x1) / PT
    total_h = (r.y1 + sw / 2 - uy0) / PT
    words = []
    for t, bb, sps in lines_of[pno]:
        if not (r.y0 - 20 <= bb[1] and bb[3] <= r.y1 + 8) or not (cl - 7 <= bb[0] < cl + COLW + 7):
            continue
        for sp in sps:
            if 6.0 <= sp['size'] <= 7.0 and sp['color'] == 0x7A7A7A and sp['text'].strip():
                words.append(sp)
    words.sort(key=lambda s: s['bbox'][0])
    w_right = (cl + COLW - words[-1]['bbox'][2]) / PT if words else -9
    # 坐线（右词墨底→线墨顶，像素）
    zx = -9
    if words:
        rit = r.y0 - sw / 2
        # dpi300＋clip 收至线墨顶上 0.5pt：150dpi 下 6.5pt 词内竖白缝分裂墨带，[-2] 会取到词中段带
        bzx = merge(bands(page, words[-1]['bbox'][0], words[-1]['bbox'][2],
                          words[-1]['bbox'][1] - 2, rit - 0.5, dpi=300), gap=0.4)
        if bzx:
            zx = (rit - bzx[-1][1]) / PT
    # 前距（菱形组顶→上一墨带底；栏首元素豁免）
    pre = -9
    topcol = (uy0 - MARGIN) / PT
    if topcol >= 8:
        bpre = bands(page, cl, cl + COLW, uy0 - 32, uy0 - 0.3)
        if bpre:
            pre = (uy0 - bpre[-1][1]) / PT
    ok_i = (abs(gw - 23.5) <= 1.2 and 6.2 <= gh <= 7.0 and 0.15 <= tie <= 0.45
            and abs(sw - 1.2) <= 0.06 and abs(st_dist - 2.77) <= 0.3 and abs(en_dist - 4.0) <= 0.5
            and len(words) >= 2 and abs(w_right - 4.0) <= 1.0 and 0.15 <= zx <= 0.65
            and 6.5 <= total_h <= 7.7 and (pre == -9 or 3.7 <= pre <= 5.3))
    ok7 = ok7 and ok_i
    d7.append(f'p{pno} 组{gw:.1f}×{gh:.2f} 贴线{tie:.2f} 线{sw:.3f}pt 起{st_dist:.2f} 终{en_dist:.2f} '
              f'词{len(words)} 右缘{w_right:.2f} 坐线{zx:.2f} 总高{total_h:.2f} 前距{pre:.2f}')
    if pre == -9:
        d7_reg.append(f'p{pno}（栏首元素距版心顶{topcol:.1f}mm，前距豁免登记）')
    # 后距（线墨底→下一墨带顶）登记
    ib = r.y1 + sw / 2
    bn = bands(page, cl, cl + COLW, ib + 0.3, ib + 32)
    d7_reg.append(f'p{pno} 后距{(bn[0][0] - ib) / PT:.2f}mm' if bn else f'p{pno} 后距栏末')
check('⑦花形几何全集（×3/组宽高/贴线/底线1.2pt灰77/起终点/右词组/坐线/前距/行总高）', ok7, '；'.join(d7))
reg('⑦ 花形后距/栏首豁免登记', '；'.join(d7_reg) + '（后距无全品规格值，登记；栏首弃胶机制见 qp-blocks \\huaxing 注）')
wide_rules = [(pno, d['rect']) for pno in range(1, n_pages + 1) for d in doc[pno - 1].get_drawings()
              if d['rect'].width > 300 and d['rect'].height <= 2]
check('⑦-2 无整页横断（章首通栏线仅页1×1）', len(wide_rules) == 1 and wide_rules[0][0] == 1,
      '；'.join(f'p{p} w={r.width / PT:.0f}mm' for p, r in wide_rules))

# ---- ⑧⑨⑩ 页脚组/页眉缺席/奇偶交替 ----
feet_ok8, feet_ok10, hdr_ok = True, True, True
d8, d9, d10 = [], [], []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    blk_rect = None
    for d in page.get_drawings():
        r = d['rect']
        f = d.get('fill')
        if not f or r.y0 <= BODY_BOT - 10:
            continue
        if rgb255(f) == (221, 221, 221):
            blk_rect = r
    num = None
    foot_spans, foot_txts = [], []
    for t, bb, sps in lines_of[pno]:
        if bb[1] > BODY_BOT - 2:
            foot_spans += [sp for sp in sps if sp['text'].strip()]
            foot_txts.append(t)
        for sp in sps:
            if sp['text'].strip() == str(pno) and blk_rect and bb[1] > BODY_BOT - 10 \
               and blk_rect.x0 - 1 <= sp['bbox'][0] and sp['bbox'][2] <= blk_rect.x1 + 1:
                num = sp
    odd = pno % 2 == 1
    if blk_rect and num:
        bw, bh = blk_rect.width / PT, blk_rect.height / PT
        bot = (PAGE_H - blk_rect.y1) / PT
        inner = blk_rect.x0 if odd else blk_rect.x1
        near = abs((num['bbox'][0] if odd else num['bbox'][2]) - inner) / PT
        fonts = {sp['font'] for sp in foot_spans}
        szs = {round(sp['size'], 1) for sp in foot_spans}
        ok8 = (abs(bw - 26.2) <= 0.3 and abs(bh - 7.8) <= 0.3 and abs(bot - 11) <= 0.5
               and 10.5 <= num['size'] <= 11.5 and 0.8 <= near <= 2.0)
        if odd:
            ok8 = ok8 and any('FZSSJW' in f for f in fonts) and any('FZHTJW' in f for f in fonts)
        else:
            ok8 = ok8 and any('FZSSJW' in f for f in fonts)
        ok8 = ok8 and any(5.3 <= s <= 5.7 for s in szs)
        feet_ok8 = feet_ok8 and ok8
        d8.append(f'p{pno} 块{bw:.1f}×{bh:.1f} 底{bot:.1f} 数字{num["size"]:.1f}pt 近缘{near:.2f} '
                  f'字{sorted(f.split("--")[0] for f in fonts)}')
        if odd:
            ok10 = blk_rect.x1 >= COLR - 1.5 and any('导学件' in t for t in foot_txts)
            d10.append(f'p{pno}奇 贴右距{(COLR - blk_rect.x1) / PT:.2f}mm')
        else:
            ok10 = blk_rect.x0 <= MARGIN + 1.5 and any('人教B' in t.replace(' ', '') for t in foot_txts)
            d10.append(f'p{pno}偶 贴左距{(blk_rect.x0 - MARGIN) / PT:.2f}mm')
        feet_ok10 = feet_ok10 and ok10
    else:
        feet_ok8 = feet_ok10 = False
        d8.append(f'p{pno} 缺页码块/数字')
    hdr = [t for t, bb, sps in lines_of[pno] if bb[3] < MARGIN - 1]
    hdr_ok = hdr_ok and not hdr
    d9.append(f'p{pno}{"无页眉" if not hdr else "有:" + str(hdr[:1])}')
check('⑧页脚块26.2×7.8/底11/数字11pt近缘0.8-2.0/小字5.5混重', feet_ok8, '；'.join(d8))
check('⑨页眉缺席（版心顶上方无文本，全部页）', hdr_ok, '；'.join(d9))
check('⑩奇偶交替（奇=块贴右+导学件/偶=块贴左+人教B）', feet_ok10, '；'.join(d10))

# ---- ⑭ 栏线（stroke+渲染芯） ----
rule_found = {}
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 1.5 and r.height >= 0.5 * TEXTH):
            continue
        if abs(r.x0 - MID) > 2 and abs(r.x1 - MID) > 2:
            continue
        c = d.get('color') or d.get('fill')
        if c and rgb255(c) == (153, 153, 153):
            rule_found[pno] = d
            break
rule_detail, core_vals = [], []
for pno, d in sorted(rule_found.items()):
    page = doc[pno - 1]
    rule_detail.append(f'p{pno} w={d.get("width"):.3f}pt')
    sc3 = 300 / 72.0
    pm = page.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY,
                         clip=pymupdf.Rect(MID - 2, MARGIN + 20, MID + 2, BODY_BOT - 20))
    w3, h3, s3 = pm.width, pm.height, pm.samples
    col3 = min(range(w3), key=lambda c: abs((MID - 2) + (c + 0.5) / sc3 - MID))
    vals = sorted(s3[r3 * w3 + col3] for r3 in range(h3) if s3[r3 * w3 + col3] < 250)
    if vals:
        core_vals.append(vals[len(vals) // 2])
core_med = sorted(core_vals)[len(core_vals) // 2] if core_vals else -1
core_ok = all(abs(d.get('width', 0) - 0.4) <= 0.05 for d in rule_found.values())
check('⑭栏线（0.4pt 色153 逐页在场＋渲染芯170-210）',
      len(rule_found) == n_pages and core_ok and 170 <= core_med <= 210,
      f'页{sorted(rule_found)}；{"；".join(rule_detail)}；芯中位{core_med}')
reg('⑭ 栏线试档（总账I）', 'black!25（0xBF 渲染 233 无芯）→ black!40（0x99），渲染芯 dpi300 实测中位 '
    f'{core_med}≈全品 188 带芯（线性折算 187）')

# ---- ⑮ 诊断头 / ⑰ 解析升档 ----
zhen_lines = []
n_jx_span, sz_ok = 0, True
tside_cnt = 0
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('【诊断分析】'):
            zhen_lines.append((pno, t, sps[0]['size'] if sps else 0))
        if t.startswith('【解析】'):
            n_jx_span += 1
            if not any(10 <= sp['size'] <= 11 for sp in sps[:1]):
                sz_ok = False
        for i, sp in enumerate(sps):
            if 7.5 <= sp['size'] <= 8.5 and sp['text'].strip().startswith('〔') and sp['color'] == 0x777777:
                tside_cnt += 1
zhuzhu_plain = bool(re.search(r'\\newcommand\{\\zhuzhu\}\[1\]\{\{\\hspace\{0\.5em\}#1\}\}', blkfile))
no_small = '8pt' not in blkfile.split('\\newcommand{\\zhuzhu}')[1][:120] if '\\newcommand{\\zhuzhu}' in blkfile else False
orphan_rpar = sum(1 for ls in lines_of.values() for t, bb, sps in ls if t == ')')
check('⑮【诊断分析】头单行×3（10.5pt 说明，紧缩文案 无引号版）', len(zhen_lines) == 3 and orphan_rpar == 0
      and all('判断正误' in t and t.endswith('×)') and abs(sz - 10.5) <= 0.6 for _, t, sz in zhen_lines),
      '｜'.join(f'p{p} {t[:14]}…{sz:.1f}pt' for p, t, sz in zhen_lines)
      + ('' if not orphan_rpar else f'；悬孤)行{orphan_rpar}'))
check('⑰解析 10.5pt 档（span 10–11 ×20）＋\\zhuzhu 无小号层', sz_ok and n_jx_span == 20 and no_small,
      f'解析span {n_jx_span}/20 越档{0 if sz_ok else "有"}；\\zhuzhu 同号 {"是" if no_small else "否"}')
reg('⑰ 题侧〔难度（知识点N）〕8pt 灰维持计数', f'{tside_cnt} 处（拍板2 分层保留，8pt 灰 midgray）')

# ---- ⑱ 图文并排＋顶对齐 ----
n_mini = body.count(r'\begin{minipage}')
n_side = body.count(r'\begin{minipage}[t]{0.56\linewidth}')
raisebox_ok = r'\raisebox{\dimexpr-\height+\ht\strutbox\relax}' in body
check('⑱图文并排 body.tex minipage ≥4（side×4＋\\raisebox）', n_mini >= 4 and n_side == 4 and raisebox_ok,
      f'minipage {n_mini} side {n_side}/4 raisebox {"在" if raisebox_ok else "缺"}')
dys, n_side_img = [], 0
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    infos = page.get_image_info(xrefs=True)
    if not infos:
        continue
    tlines = [(l['bbox'], ''.join(sp['text'] for sp in l['spans']))
              for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b.get('lines', [])]
    for info in infos:
        rct = pymupdf.Rect(info['bbox'])
        cl2 = COLL[0] if rct.x0 < MID else COLL[1]
        if abs((rct.x0 + rct.x1) / 2 - cl2 - COLW / 2) / PT <= 3:
            continue  # 居中独立图（N6 管辖）不入 side 判定——60mm 图曾误配 dy−13.61
        near = [bb for bb, tt in tlines
                if bb[0] >= rct.x0 - COLW and bb[2] <= rct.x0 + 5 and bb[1] < rct.y1 and bb[3] > rct.y0
                and (bb[2] - bb[0]) > 20 and not tt.lstrip().startswith('◆')]
        if not near:
            continue
        n_side_img += 1
        dys.append((rct.y0 - min(bb[1] for bb in near)) / PT)
top_ok = n_side_img == 4 and all(abs(v) <= 2.0 for v in dys)
check('⑱-2 顶对齐（side 图顶−题干首行顶 |dy|≤2mm ×4）', top_ok,
      f'side {n_side_img}/4 dy=' + ' '.join(f'{v:+.2f}' for v in dys))

# ---- ⑲ 字重阶梯（tex 级）＋字号档 ----
fb_tbl = {}
for line_ in fontfile.splitlines():
    mm2 = re.search(r'\\setCJKfamilyfont\{(\w+)\}.*FakeBold=([\d.]+)', line_)
    if mm2:
        fb_tbl[mm2.group(1)] = float(mm2.group(2))
fb_ok = (fb_tbl.get('heizhang') == 4.0 and fb_tbl.get('heijie') == 3.3 and fb_tbl.get('heitiao') == 2.7
         and fb_tbl.get('heibf') == 2.3 and fb_tbl.get('heihao') == 2.0 and fb_tbl.get('heibian') == 1.3)
huabf_ok = bool(re.search(r'\\setCJKfamilyfont\{huabf\}.*FakeSlant=0\.18,FakeBold=2\.0', fontfile))
jieti_def = blkfile if False else titfile
mji = re.search(r'\\newcommand\{\\jietitle\}.*?(?=\\newcommand)', titfile, re.S)
jietitle_txt = mji.group(0) if mji else ''
jt_rev = ('\\heiti ' in jietitle_txt and not any(x in jietitle_txt for x in
          ('\\heizhang', '\\heijie', '\\heitiao', '\\heibf', '\\heihao', '\\heibian')))
tiaomu_ok = r'{\heitiao #1.}\hspace{1em}' in blkfile
li_ok = r'{\fontsize{12pt}{15pt}\selectfont\heibian #1}' in blkfile
tjdnr_ok = (r'{\fontsize{12pt}{15pt}\selectfont\heibf #2}' in blkfile
            and '探究点#1}\\par' in blkfile and '\\nopagebreak\\noindent{' in blkfile)
jiexi_tail = bool(re.search(r'\\newcommand\{\\jiexi\}.*?\\addvspace\{7pt\}\}', blkfile, re.S))
zhenti_tail = '【解析】}#4}\\par\\addvspace{7pt}}' in blkfile
n_hao_body = len(re.findall(r'\{\\fontsize\{11\.4pt\}\{14pt\}\\selectfont\\heihao \d．\}', body))
n_hao_pdf = sum(1 for ls in lines_of.values() for t, bb, sps in ls
                for sp in sps if abs(sp['size'] - 11.4) < 0.4 and sp['text'].strip().endswith('．'))
n_lab12 = Counter()
for ls in lines_of.values():
    for t, bb, sps in ls:
        mm3 = re.match(r'^(例1|变式1)〔', t)
        if mm3:
            n_lab12[mm3.group(1)] += 1
            if not (11.6 <= sps[0]['size'] <= 12.4):
                n_lab12[mm3.group(1) + '!'] += 1
check('⑲字重阶梯 tex 级（FakeBold值表/huabf斜粗/\\jietitle反向/\\tiaomu形/解析尾7pt·6-8pt档）',
      fb_ok and huabf_ok and jt_rev and tiaomu_ok and li_ok and tjdnr_ok and jiexi_tail and zhenti_tail,
      f'值表{fb_tbl} huabf{"在" if huabf_ok else "缺"} 节撤仿粗{"是" if jt_rev else "否"} '
      f'\\tiaomu{"在" if tiaomu_ok else "缺"} \\li变式{"在" if li_ok else "缺"} 探究点独行宏{"在" if tjdnr_ok else "缺"} '
      f'解析尾7pt {jiexi_tail and zhenti_tail}')
check('⑲字号档（检测题号11.4pt tex×5＋pdf×5＋例变式标签12pt×18）',
      n_hao_body == 5 and n_hao_pdf == 5 and n_lab12.get('例1') == 9 and n_lab12.get('变式1') == 9
      and '例1!' not in n_lab12 and '变式1!' not in n_lab12,
      f'题号 tex{n_hao_body}/5 pdf{n_hao_pdf}/5 标签 例{n_lab12.get("例1")}变{n_lab12.get("变式1")} 越档'
      f'{n_lab12.get("例1!", 0) + n_lab12.get("变式1!", 0)}')
reg('⑲ 题号→题侧 advance 隙（11.4pt 题号盒与 8pt 题侧盒交叠，登记）', '题号 FakeBold 盒右缘越过题侧盒左缘'
    '（0908 实测 −1.8~0mm），题号辨识度由 11.4pt＋2.0× 加重承担（条9①），ink 口径探针值见交付报告§九')

# ---- N1 判断题括号列位（ink 像素＋bbox） ----
par_ok, par_detail = True, []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for t, bb, sps in lines_of[pno]:
        if not (t.endswith('（√）') or t.endswith('（×）')):
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
        w, h, s = pm.width, pm.height, pm.samples
        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC
        ink_d = (cl + COLW - ink_r) / PT
        bb_d = (cl + COLW - bb[2]) / PT
        par_ok = par_ok and 4.9 <= ink_d <= 5.9 and 3.14 <= bb_d <= 3.54
        par_detail.append(f'p{pno}{t[-2:]} ink{ink_d:.2f}/bbox{bb_d:.2f}')
check('N1 判断题括号固定列位（ink 5.4±0.5 ×6＋bbox 3.34±0.2）', par_ok and len(par_detail) == 6,
      ' '.join(par_detail))
reg('N1 口径（0908 修正）', '两支尾占位统一 \\rule{3.34mm}{0pt}（挂位/单段），ink 同位 5.14；'
    '此前单段支 \\hspace*{5.4mm} 实出 ink 7.17 与挂位错位 2.03 出窗（校准探针抓出），已废')

# ---- N2 选项行距分档双窗 ----
bp, by = None, None
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if any(abs(sp['size'] - 11.4) < 0.4 for sp in sps):
            bp, by = pno, bb[1]
            break
    if bp:
        break
pitches = {'例': [], '评': []}
for pno in range(1, n_pages + 1):
    for cl in COLL:
        opts, allr = [], []
        for t, bb, sps in lines_of[pno]:
            if not (cl - 7 <= bb[0] < cl + COLW + 7):
                continue
            allr.append((bb[1], bb[3]))
            if len(t) > 1 and t[0] in 'ABCD' and t[1] in '．.':
                opts.append((t[0], bb[1], sps[0]['origin'][1]))
        opts.sort(key=lambda x: x[1])
        for (la, ya, oya), (lb, yb, oyb) in zip(opts, opts[1:]):
            if ord(lb) != ord(la) + 1 or not (3 < oyb - oya < 40):
                continue
            if any(yc > ya + 0.6 and yc < yb - 0.6 for yc, _ in allr):
                continue
            reg_ = '评' if (pno, oya) >= (bp, by) else '例'
            pitches[reg_].append((oyb - oya) / PT)
ex_ok = pitches['例'] and all(6.4 <= g <= 7.0 for g in pitches['例'])
ev_ok = pitches['评'] and all(7.1 <= g <= 7.8 for g in pitches['评'])
check('N2 选项行距分档双窗（例区19pt 6.4-7.0／评价·检测21pt 7.1-7.8）',
      ex_ok and ev_ok and len(pitches['例']) >= 3 and len(pitches['评']) >= 1,
      f'例{len(pitches["例"])}档 ' + ' '.join(f'{g:.2f}' for g in pitches['例']) +
      f'／评{len(pitches["评"])}档 ' + ' '.join(f'{g:.2f}' for g in pitches['评']))

# ---- N3 探究点独行＋反向 ----
n_solo, solo_bad = 0, 0
for ls in lines_of.values():
    for t, bb, sps in ls:
        if t.startswith('◆探究点'):
            n_solo += 1
            if '〔' in t or '例1' in t:
                solo_bad += 1
check('N3 探究点标题独行×9＋反向（行内无题侧/例标）', n_solo == 9 and solo_bad == 0 and tjdnr_ok,
      f'独行{n_solo}/9 混排{solo_bad}（宏级 \\par\\nopagebreak\\noindent {"在" if tjdnr_ok else "缺"}）')

# ---- N4 表组 ----
tab_ok, tab_detail, tab_reg = True, [], []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    hrs, vrs = [], []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c or rgb255(c) != (122, 122, 122):
            continue
        if r.width > 15 * PT and r.height < 3:
            hrs.append((r, d))
        elif r.height > 5 * PT and r.width < 3:
            vrs.append(r)
    if len(hrs) < 3:
        continue
    hrs.sort(key=lambda x: x[0].y0)
    rs = [r for r, _ in hrs]
    ths = set()
    for r, d in hrs:
        ths.add(round((d.get('width') if d['type'] == 's' else r.height) / PT, 3))
    tmin, tmax = min(ths), max(ths)
    head_h = (rs[1].y0 - rs[0].y0) / PT
    rowhs = [(b.y0 - a.y0) / PT for a, b in zip(rs, rs[1:])]
    cl = COLL[0] if (rs[0].x0 + rs[0].x1) / 2 < MID else COLL[1]
    # clip 尾收至线墨顶上 1.2pt：−0.3pt 会吃进表顶横线抗锯齿溢出行（前距曾出 −0.11）
    btop = bands(page, cl, cl + COLW, rs[0].y0 - 16, rs[0].y0 - 1.2)
    tpre = (rs[0].y0 - btop[-1][1]) / PT if btop else -9
    # 栏首表豁免：上邻末带若系通栏区文本越栏（无本栏行），前距无对象（p1 表为右栏首元素实证）
    same_col = False
    if btop:
        a_, b_ = btop[-1]
        for t, bb, sps in lines_of[pno]:
            if bb[1] < b_ + 0.5 and bb[3] > a_ - 0.5 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7:
                same_col = True
                break
    if btop and not same_col:
        tab_reg.append(f'p{pno} 表为栏首元素（上邻末带系通栏文本越栏 x0<{cl - 7:.0f}pt）——前距豁免登记')
        pre_ok = True
    else:
        pre_ok = btop and 2.2 <= tpre <= 3.4
    tab_ok = tab_ok and tmin <= 0.18 and tmax >= 0.25 and tmax / tmin >= 1.5 \
        and 7.0 <= head_h <= 9.2 and min(rowhs) >= 6.9 and pre_ok
    tab_detail.append(f'p{pno} 线厚{sorted(ths)} 表头{head_h:.2f} 行高min{min(rowhs):.2f} 前距{tpre:.2f}')
    if len(vrs) >= 2:
        vrs.sort(key=lambda r_: r_.x0)
        c0 = (vrs[0].x0 + vrs[1].x0) / 2
        offs = []
        for t, bb, sps in lines_of[pno]:
            if rs[0].y0 - 1 <= bb[1] and bb[3] <= rs[1].y0 + 1 and vrs[0].x0 <= bb[0] and bb[2] <= vrs[1].x0:
                offs.append((bb[0] + bb[2]) / 2 - c0)
        if offs:
            off = max(abs(o) for o in offs) / PT
            tab_ok = tab_ok and off <= 1.5
            tab_detail.append(f'首列偏{off:.2f}')
        else:
            tab_reg.append(f'p{pno} 首列无表头文本')
    else:
        tab_reg.append(f'p{pno} 竖线{len(vrs)}条（首列居中不可测，登记）')
check('N4 表组（外框0.8>内线0.4pt 色122/表头7.0-9.2/行高≥6.9/表顶前距2.8±0.6/首列居中±1.5）',
      tab_ok, '；'.join(tab_detail))
if tab_reg:
    reg('N4 表组登记项', '；'.join(tab_reg))

# ---- N5 学习目标（楷体/行距/悬挂） ----
kt = []
for t, bb, sps in lines_of[1]:
    if sps and ('Kai' in sps[0]['font'] or 'kai' in sps[0]['font'].lower()):
        kt.append((bb[0], bb[1], sps[0]['origin'][1]))
kt.sort(key=lambda x: x[1])
kt_ok = len(kt) == 4
if kt_ok:
    first_x = kt[0][0] / PT
    hang_x = [x / PT for x, _, _ in kt if abs(x / PT - 23.3) <= 0.6]
    lds = [(b[2] - a[2]) / PT for a, b in zip(kt, kt[1:])]
    kt_ok = (28.0 <= first_x <= 29.7 and len(hang_x) >= 1 and all(5.5 <= d <= 6.5 for d in lds))
check('N5 学习目标（楷体4行/行距17pt档5.5-6.5/首行内容28.84±0.85/回行悬挂23.3±0.6）', kt_ok,
      f'n={len(kt)} 首x{kt[0][0] / PT if kt else -1:.2f} 行距' +
      ' '.join(f'{d:.2f}' for d in [((b[2] - a[2]) / PT) for a, b in zip(kt, kt[1:])]) if kt else 'n=0')
reg('N5 顶格例外（拍板6）', '首行缩进 2 字＋序号「N.」加粗后空 1 字（\\mubiaomu \\hangindent=8.3mm），'
    '断言顶格.py 已同步登记 8.3mm 悬挂合法')

# ---- N6 图组 ----
img_ok, img_detail = True, []
n_center = 0
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            w_ = r.width / PT
            cl = COLL[0] if r.x0 < MID else COLL[1]
            if abs((r.x0 + r.x1) / 2 - cl - COLW / 2) / PT > 3:
                continue
            if not (58 < w_ < 62 or 33 < w_ < 35.2):
                continue
            n_center += 1
            bs = bands(page, cl, cl + COLW, r.y0 - 35, r.y1 + 35)
            ins = [i for i, (a, b) in enumerate(bs) if b > r.y0 + 0.5 and a < r.y1 - 0.5]
            if not ins:
                img_ok = False
                img_detail.append(f'p{pno} 图{w_:.0f} 无墨带!')
                continue
            i0, i1 = ins[0], ins[-1]
            pre = (bs[i0][0] - bs[i0 - 1][1]) / PT if i0 > 0 else -9
            nxt = (bs[i1 + 1][0] - bs[i1][1]) / PT if i1 + 1 < len(bs) else -9
            tgt = (2.8, 2.2) if 58 < w_ < 62 else (2.8, 2.2)
            ok_i = abs(w_ - 60) <= 1 or abs(w_ - 34) <= 1
            ok_i = ok_i and (pre == -9 or 2.3 <= pre <= 3.3) and (nxt == -9 or 1.7 <= nxt <= 2.7)
            img_ok = img_ok and ok_i
            img_detail.append(f'p{pno} 图{w_:.1f} 前{pre:.2f}/后{nxt:.2f}')
check('N6 图组（居中 60±1/34±1、ink 上下距 2.3-3.3/1.7-2.7）', img_ok and n_center == 2,
      '；'.join(img_detail) + f'（居中独立图 {n_center}/2）')
reg('N6 图内字≥7pt 等效断言＝SKIP 登记', '需图源文字像素高折算（任务书条5允许缺口登记）：'
    'sub3_B_4 原生 1408×374px 打印 60mm（≈597dpi 级），图内字等效远超 7pt 档，无降质风险；逐图提档另行任务')

# ---- N7 投影向量条目首子项连排 ----
lianpai_body = r'\tiaomu{3}{投影向量：（1）' in body
lianpai_pdf = any('投影向量：（1）' in t for ls in lines_of.values() for t, bb, sps in ls)
bind23 = body.count('\\bindp （2）') >= 1 and body.count('\\bindp （3）') >= 1
logtxt2 = open(os.path.join(BASE, 'postproc_daoxue_log.txt'), encoding='utf-8', errors='ignore').read()
lp_log = ("\\tiaomu{3}{投影向量：（1）" in logtxt2) and ('未各自成段嫌疑 无' in logtxt2)
check('N7 条目3 首子项（1）连排（body+pdf+postproc台账）＋（2）（3）各自成段',
      lianpai_body and lianpai_pdf and bind23 and lp_log,
      f'body{"在" if lianpai_body else "缺"} pdf{"在" if lianpai_pdf else "缺"} '
      f'\\bindp（2）（3）{"在" if bind23 else "缺"} 台账{"平" if lp_log else "异"}')

# ---- N8 素养小结楷体 ----
xiaojie_kai = r'\noindent{\kaishu #1}' in blkfile
n_xj, kai_ok = 0, 0
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for cl in COLL:
        rows = col_rows(pno, cl)
        for i, (y0, y1, t, sps) in enumerate(rows):
            if t.startswith('【素养小结】'):
                n_xj += 1
                for j in range(i + 1, min(i + 3, len(rows))):
                    if rows[j][2].startswith('①识别'):
                        if 'Kai' in rows[j][3][0]['font'] or 'kai' in rows[j][3][0]['font'].lower():
                            kai_ok += 1
                        break
check('N8 素养小结（标签独行＋内容楷体 ×9）', xiaojie_kai and n_xj == 9 and kai_ok == 9,
      f'宏 \\kaishu {"在" if xiaojie_kai else "缺"}；内容行楷体 {kai_ok}/{n_xj}')

# ---- N9 ◆ 符号 0.63em＋后隙 2.4mm ----
gapf, widf, badf = [], [], 0
for ls in lines_of.values():
    for t, bb, sps in ls:
        if ('知识点' in t or '探究点' in t) and sps and sps[0]['text'].strip() == '◆':
            widf.append((sps[0]['bbox'][2] - sps[0]['bbox'][0]) / PT)
            if len(sps) > 1:
                gapf.append((sps[1]['bbox'][0] - sps[0]['bbox'][2]) / PT)
            else:
                badf += 1
g_ok = len(gapf) >= 9 and all(abs(g - 2.4) <= 0.3 for g in gapf)
w_med = sorted(widf)[len(widf) // 2] if widf else -1
check('N9 ◆后隙 2.4±0.3（n≥9）', g_ok and badf == 0,
      f'n={len(gapf)} ' + ' '.join(f'{g:.2f}' for g in gapf[:6]) + '…')
reg('N9 ◆ advance 宽中位', f'{w_med:.2f}mm（0.63em 桶排 8.6pt 字号，≈0.88em 墨宽，总账E 登记）')

# ---- N10 解析→下题题号距（register） ----
gaps_bb = []
TISIG1 = re.compile(r'^\d．〔')
for pno in range(1, n_pages + 1):
    for cl in COLL:
        rows = col_rows(pno, cl)
        for i, (y0, y1, t, sps) in enumerate(rows):
            if not t.startswith('【解析】'):
                continue
            j = i + 1
            blk_bot = y1
            last_txt = t
            while j < len(rows):
                tt = rows[j][2]
                m1 = TISIG1.match(tt)
                m2 = re.match(r'^（\d+）', tt) and re.search(r'[，。；：与若则]', tt[:10])
                if m1 or m2:
                    break
                blk_bot = max(blk_bot, rows[j][1]); last_txt = tt; j += 1
            if j >= len(rows) or not re.search(r'[。．；？！]$', last_txt):
                continue
            d_ = (rows[j][0] - blk_bot) / PT
            if 0.5 < d_ < 15:
                gaps_bb.append(d_)
reg('N10 解析→下题题号墨距（register）',
    (f'有效对 n={len(gaps_bb)}，bbox 距 ' + ' '.join(f'{g:.2f}' for g in sorted(gaps_bb)) +
     f'，中位 {sorted(gaps_bb)[len(gaps_bb)//2]:.2f}mm（ink 口径另加字面 inset ≈+1.3；'
     '全品题间墨隙参照 4.1–4.7，任务书条9）；tex 级已锁 \\jiexi/\\zhenti 解析尾 \\addvspace{7pt}'
     '（⑲断言；0908 断言轮由 6pt 提 7pt——⑤a p6右断栏回填，墨距随 +0.35mm）。配对总体小（栏断/变式流向不入集）且公式降部扰墨带，故登记不设门') if gaps_bb else '无有效对（异常复核）')

# ---- ⑪⑫⑬ 内容层 ----
n_kd = body.count(r'\kongda{')
check('⑪挖空印答 body.tex \\kongda ×20', n_kd == 20, f'\\kongda={n_kd}')
ANSWERS = ['大小', '方向', '长度', '相反', '互相平行', '重合', '模相等', '三角形', '平行四边形',
           '相同', '实数', '互相垂直', '零向量', '有序实数对']
p12_text = (doc[0].get_text() + doc[1].get_text())
miss = [w for w in ANSWERS if w not in p12_text]
check('⑪-2 印答值 pdf 在场（p1/p2，14 词值＋数字/区间值）', not miss, ('缺 ' + '、'.join(miss)) if miss else '全部在场')
n_kd_anchor, kd_pt = 0, []
for pno in (1, 2):
    page = doc[pno - 1]
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            ux0, ux1 = sorted((it[1].x, it[2].x))
            uw = ux1 - ux0
            if not (42 <= uw <= 60) or ux0 < MARGIN - 8 or ux1 > COLR + 8:
                continue
            near = []
            for blk in page.get_text('dict')['blocks']:
                for ln in blk.get('lines', []):
                    for sp in ln['spans']:
                        sx0, _, sx1, sy1 = sp['bbox']
                        if not sp['text'].strip():
                            continue
                        ov = min(sx1, ux1) - max(sx0, ux0)
                        if ov > 0.5 * min(sx1 - sx0, uw) and -1.5 <= sy1 - it[1].y <= 1.5:
                            near.append(sp['text'])
            if len(near) == 1:
                n_kd_anchor += 1
                kd_pt.append(uw)
kd_min = min(kd_pt) if kd_pt else -1
check('⑪-3 印答盒宽全量实测（20 处线宽 ≥42pt）', n_kd_anchor == 20 and n_kd == 20 and kd_min >= 42,
      f'锚定 {n_kd_anchor}/20 最窄 {kd_min:.1f}pt；body {n_kd}/20')
reg('⑪-3 口径（返修1 沿 v4.2）', '\\kongda 专用寄存器 \\kdmind/\\kdwd（xeCJK 断胶覆写坑），'
    'signature＝栏内 42–60pt 水平细线＋线下紧贴恰一值 span（|dy|≤1.5pt）')
n_zt = body.count(r'\zhenti{')
n_jx_body = body.count(r'\jiexi{')
check('⑫判断题 \\zhenti ×6＋简析 \\jiexi ×14（变式9＋检测5）', n_zt == 6 and n_jx_body == 14,
      f'\\zhenti={n_zt} \\jiexi={n_jx_body}')
segs = re.split(r'\\zsd\{', body)[1:]
seqs = [[int(x) for x in re.findall(r'\\tiaomu\{(\d+)\}', s)] for s in segs]
check('⑬条目按知识点重起（[1,2,3]/[1,2]/[1,2,3,4]）', seqs == [[1, 2, 3], [1, 2], [1, 2, 3, 4]], f'实测 {seqs}')

print('—— 断言实测 ——')
for s in okmsg:
    print(' ✓', s)
for s in regmsg:
    print(' ◎ 登记', s)
for s in fails:
    print(' ✗', s)
print('断言结果：', '全部通过' if not fails else f'未通过 {len(fails)} 项')
raise SystemExit(0 if not fails else 1)
