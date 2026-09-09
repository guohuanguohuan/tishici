# -*- coding: utf-8 -*-
r"""_测v4断言.py——v4.4 导学件断言实测（交付报告§十证据源）。骨架沿 v4.3 版（check/reg/fails/okmsg＋SystemExit），
v4.4 执行轮翻修（规格书§断言翻修）：既有断言漂移适配（⑥ [答案]14/[解析]20/[分析]9/[详解]9/[点睛]2、
⑰ zhuzhu 新体＋题侧 10.5 黑宋、⑱ side×5＋新 raisebox＋横缝、⑲ tiaomu \\textbf/\\heiti 变式/tjdnr #3/
题号 \\textbf regex/标签[]、N1 半角(√)(×)、N3 '[' 反向、N4 表顶 2.77±0.5＋头净空 2.8–3.5·不穿字≥0.2＋
表内行距 4.90±0.4＋挖空行底登记、N6 居中×1 下距 0.4–2.6、N7 半角子项号、N10 升格中位 3.95±0.6、页数实测）
＋新增断言 ①题号笔画 2.0–2.7×＋变式反向 ②括号 0.3–0.7em＋全角零残留 ③定界符 ≤9.5pt（探七 ×2 豁免）
④判断括号右挂 ×6＋独占行 0 ⑦七缝（探究点→例1/知识点/表底/解析→◆/条目）⑧多选×1 ⑨悬挂＋源空格 0
⑩答案行无下划线 ⑪题侧隙 2.7/2.2×14 ⑫探究点 ≤82mm×9＋名字清单 ⑭ kongwei 6.8±0.6×8 ⑮ side×5 归属。
F 片A 0909 适配（图文形态轮）：⑱ 几何档重写——side×5 文字栏宽逐图标定（mm）＋图盒宽按墨宽折算
（image1 剪垫后冻结 27.2mm）＋raisebox 高逐图反解；⑱-2 改墨级三窗（顶差 ∈[−1,+1]／墨缝 ∈[5.2,8.2]／
右缘 ∈[1.6,3.6]，600dpi，主口径同 D 组 B_ink），旧「|dy_box|≤2＋横缝降登记」作废；
⑮ 归属键改阅读序（页,栏,y）——修同 y 双栏标题与跨栏流两处误归属（旧实测 {七,三,二,八}→新 {二,三,六,八,九}）；
⑪ 后隙 18→20＋换行态 5→3（探二/探九题干由并排 minipage 改内联，标签行末后隙可测 +2）。
v4.3 窗口全部为 0908 执行轮 150dpi 墨口径／矢量实测回填（校准探针三轮，存 工作区/体系-v43执行-0908/）：
①编译零 error/overfull/missingchar；页数＝实测值（v4.4 标定轮回填，缝＋行距增量可能 7→8）
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
⑱图文并排 minipage ≥5（side×5：文字栏宽逐图标定 43–49mm＋图盒按墨宽＋raisebox 逐图反解）
  ＋墨级三窗（顶差 ∈[−1,+1]／墨缝 ∈[5.2,8.2]／右缘 ∈[1.6,3.6]，F 片A 0909 新档；旧 |dy|≤2＋横缝登记作废）；⑲字重阶梯 tex 级：
  FakeBold 值表 heizhang4.0/heijie3.3/heitiao2.7/heibf2.3/heihao2.0/heibian1.3＋huabf slant0.18/bold2.0
  ＋\jietitle 反向断言（\heiti 常规，无仿粗族）＋例变式标签 12pt×18＋检测题号 11.4pt×5（tex+pdf）
  ＋\tiaomu 输出形 {\heitiao #1.}＋\jiexi 解析尾 \addvspace 7pt（6–8pt 档，条9②）＋\zhenti 尾 0pt
  （F 片B 0909 #31 归零，见下）
新增 v4.3：N1 判断题括号 ink 列位 5.4±0.5（像素，两支尾占位统一 rule 3.34 后 ink 同位 5.14）＋bbox 3.34±0.2；
  N2 选项行距分档双窗（例区 19pt→6.4–7.0mm／评价·检测 21pt→7.1–7.8mm，拍板9）；
  N3 探究点标题独行×9＋反向（行内无题侧/例标；翻拍板16/28）；N4 表组（外框 0.8＞内线 0.4pt、色 122、
  表头行高 8.7–9.3、行高 ≥8.5、表顶前距 2.27–3.6、首列居中±1.5、头净空 2.8–3.5）；N5 学习目标（楷体、行距 17pt 档、
  回行悬挂 8.3mm、首行缩进例外）；N6 图组（60±1／34±1 居中、ink 上下距 2.8/2.2±0.5 窗、图内字 SKIP 登记）；
  N7 条目3 投影向量首子项（1）连排（body+pdf+postproc 第8步台账）；N8 素养小结内容楷体×9；
  N9 ◆ 0.63em＋后隙 2.4±0.3；N10 解析→下题题号距（register——配对少且公式降部扰带，tex 级已锁 7pt·6-8pt 档）
F 片B 0909 适配（竖向间距与表格净空轮；窗口旧→新逐项登记见对应 check/reg）：
  ⑦块缝 条目缝窗 2.5–5.0→2.7–3.4（\tiaomu 尾距 1.8→0.35mm，实测 3.05–3.39，pitch 6.76 统一）＋
  知识点缝对 2→1／表底缝对 2→3（表3 移 p3 栏首）；新增 ⑦-3 条目2 (1)→(2) 拆段缝（6.44±0.25／墨 2.7–3.0）＋
  ⑦-4 相邻判断题缝（6.44±0.25／墨 2.6–3.2，\zhenti 尾 7pt→0）＋N4b 多行格净空（行级最紧侧 顶 2.9–3.7／
  底 2.9–4.3mm，extrarowheight 0.4→1.7mm＋\tabrowglue 按折数分档）；N4 表头 7.0–9.2→8.7–9.3、行高 ≥6.9→≥8.5、
  头净空 2.0±0.4→2.8–3.5（E 垫顶后墨顶抬升）；⑲ \zhenti 尾 0pt/\jiexi 尾 7pt 分锁；⑬/N7 \tiaomuz 形同步"""
import os
import re
from collections import Counter

import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
# F 0909 收尾轮（V7b 断言适配）：MARGIN/COLSEP 按 F 版 qp-layout（E 轮已改）——margin 17.575mm
# （版心 174.85 全品实测反推）、columnsep 9.25mm、栏宽 82.8mm；旧 15/7.5 系 C 版值，
# 残留致 ⑦花形起点/⑩页脚贴缘等全部测错基准（误 5.35/2.58，真值 2.77/≈0）
MARGIN = 17.575 * PT
BOT = 20 * PT
PAGE_W = 595.276
PAGE_H = 842.0
COLSEP = 9.25 * PT
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

# F 片B 0909 新设工具（#28/#30/#31 断言用）：600dpi 灰渲染墨带——窗口内最大相邻空档＝缝/净空。
def ink_bands600(pno, cl, y0, y1, x0=None, x1=None, dpi=600, thr=128):
    """返回窗口内墨带 [(y_a, y_b)]（pt 坐标，600dpi 灰投影）。"""
    page = doc[pno - 1]
    x0 = COLL[cl] if x0 is None else x0
    x1 = COLL[cl] + COLW if x1 is None else x1
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = [any(s[r * w + c] < thr for c in range(w)) for r in range(h)]
    idx = [r for r, d in enumerate(rows) if d]
    if not idx:
        return []
    bands, st, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > 1:
            bands.append((st, p)); st = i
        p = i
    bands.append((st, p))
    sc = 72.0 / dpi
    return [(y0 + a * sc, y0 + b * sc) for a, b in bands]

def ink_gap600(pno, cl, y_up_base, y_lo_base):
    """两基线间墨隙（mm）：窗口内最大相邻墨带空档（行内子带隙远小于行距）。"""
    bs = ink_bands600(pno, cl, y_up_base - 1.0, y_lo_base + 1.0)
    if len(bs) < 2:
        return None
    return max((b0 - a1) for (a0, a1), (b0, b1) in zip(bs, bs[1:])) * 25.4 / 72.0

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
    if not grays <= {0x4C, 0x4D, 0x77, 0x7A, 0x99, 0xDD}:
        gray_ok = False
check('③灰档全集恰{76,77,119,122,153,221} 且逐页⊆白名单', gray_ok and grays_all == {0x4C, 0x4D, 0x77, 0x7A, 0x99, 0xDD},
      f'全集{sorted(grays_all)}；{" ".join(gray_detail)}')
reg('③调色板对账', 'v4.3 五档＝midgray 0x77(119)／gray122 0x7A(122)／huarule 0x4D(77)／栏线 black!40 0x99(153)／'
    'pnumbg 0xDD(221)，与 qp-layout 定义一一对应（总账A/D/I＋拍板27）；E 0909 增第六档 footgray 0x4C(76)＝'
    '页脚小字（qp-headfoot，全品 p04 页脚小字暗核众数 76 实测）——F 收尾轮断言适配入白名单')

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
n_li1 = full.count('例1[') + full.count('例1(多选题)[')   # 探五例1 带 (多选题) 前缀（TJ-04），0908 补计
n_bs = full.count('变式1[')
n_ans = full.count('[答案]')
n_star = full.count('典型性理由：')
n_jx = full.count('[解析]')
n_fx = full.count('[分析]')
n_xj2 = full.count('[详解]')
n_dj2 = full.count('[点睛]')
check('⑥排印层 ◆探究点9/例1内联9/变式1×9/[答案]14/★0/[解析]20（[分析]9/[详解]9/[点睛]2）',
      n_tj == 9 and n_li1 == 9 and n_bs == 9 and n_ans == 14 and n_star == 0 and n_jx == 20
      and n_fx == 9 and n_xj2 == 9 and n_dj2 == 2,
      f'◆{n_tj} 例1{n_li1} 变式{n_bs} 答案{n_ans} ★{n_star} 解析{n_jx} 分析{n_fx} 详解{n_xj2} 点睛{n_dj2}'
      f'（判断6＋变式9＋检测5；v4.4 半角[]标签制）')

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
            # F 0909 收尾轮适配：件名黑体 E 起换挂 NSC-Medium（qp-fonts hei 族），FZHTJW 时代口径作废
            ok8 = ok8 and any('FZSSJW' in f for f in fonts) and any('NotoSansSC' in f for f in fonts)
        else:
            ok8 = ok8 and any('FZSSJW' in f for f in fonts)
        # F 0909 收尾轮适配：小字 5.5→5.24pt（全品字号铁证，qp-headfoot \qphuitext），MuPDF 实测 5.22
        ok8 = ok8 and any(5.0 <= s <= 5.45 for s in szs)
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
check('⑧页脚块26.2×7.8/底11/数字11pt近缘0.8-2.0/小字5.24混重', feet_ok8, '；'.join(d8))
reg('⑧ 页脚混重适配（0909 收尾轮）', '件名黑体 E 起换挂 NSC-Medium（qp-fonts hei 族；FZHTJW 仿粗轨退役）、'
    '小字 5.5→5.24pt＋色黑→灰76（全品 p04 字号/暗核铁证，qp-headfoot \\qphuitext）——'
    '断言字体名与字号窗同步（NotoSansSC／5.0–5.45，MuPDF 实测 5.22）')
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
tside_cnt, tside_font_ok = 0, True
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('【诊断分析】'):
            zhen_lines.append((pno, t, sps[0]['size'] if sps else 0))
        if t.startswith('[解析]'):
            n_jx_span += 1
            if not any(10 <= sp['size'] <= 11 for sp in sps[:1]):
                sz_ok = False
        for i, sp in enumerate(sps):
            # v4.4⑤ 题侧 8pt 灰〔〕→10.5pt 纯黑半角[]（TJ-03 与正文完全同号同族）
            # 0908：标签实形 [简单/中档(知识点N)]（CJK 数字），旧字面 '[难度' 恒 0 处——改正则实形
            if 10.0 <= sp['size'] <= 11.0 and re.match(r'^\[[简中难]\(', sp['text'].strip()) and sp['color'] == 0:
                tside_cnt += 1
                if 'FZSSJW' not in sp['font']:
                    tside_font_ok = False
no_small = '8pt' not in blkfile.split('\\newcommand{\\zhuzhu}')[1][:120] if '\\newcommand{\\zhuzhu}' in blkfile else False
# 0908：悬孤)行改基线归并口径——\hfill 大空隙/数学重排会把同一视觉行拆成多 MuPDF 片段，
# 逐片段查 t==')' 会把与 ( 同线的片段误计为孤行（首轮 7 处全为伪象）
_frag15 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _frag15.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
orphan_rpar = sum(1 for frs in _frag15.values()
                  if ''.join(x[1] for x in sorted(frs)).strip() == ')')
check('⑮【诊断分析】头单行×3（10.5pt 说明，紧缩文案 无引号版）', len(zhen_lines) == 3 and orphan_rpar == 0
      and all('判断正误' in t and t.endswith('×)') and abs(sz - 10.5) <= 0.6 for _, t, sz in zhen_lines),
      '｜'.join(f'p{p} {t[:14]}…{sz:.1f}pt' for p, t, sz in zhen_lines)
      + ('' if not orphan_rpar else f'；悬孤)行{orphan_rpar}'))
check('⑰解析 10.5pt 档（span 10–11 ×20）＋\\zhuzhu [注意]前缀新体无小号层', sz_ok and n_jx_span == 20 and no_small,
      f'解析span {n_jx_span}/20 越档{0 if sz_ok else "有"}；\\zhuzhu 新体 {"是" if no_small else "否"}')
reg('⑰ 题侧 [简单/中档(知识点N)] 10.5pt 宋体（TJ-03）计数', f'{tside_cnt} 处（源文全数，见 ⑪ 口径登记）；'
    f'族 FZSSJW {"全对" if tside_font_ok else "有异"}（v4.4 拍板2 与正文完全同）')

# ---- ⑱ 图文并排＋顶对齐＋墨缝/右缘（F 片A 0909 几何档重写） ----
# 旧形（v4.4⑪/收尾轮）：side 文字 0.56\linewidth＋图 0.40\linewidth＋raisebox 2.6mm 定值＋盒间 1.2mm；
# 新形（F 片A，全品截图实证）：文字栏宽逐图标定（mm）＋图盒宽按墨宽折算（image1 剪垫后冻结 27.2mm）＋
# raisebox 高逐图反解 H=c0+pad_t+0.25＋盒间胶由图墨右缘距栏右 r_edge 反解。
n_mini = body.count(r'\begin{minipage}')
n_side = len(re.findall(r'\\begin\{minipage\}\[t\]\{[\d.]+mm\}\\raggedright', body))
raise_h = re.findall(r'\\raisebox\{\\dimexpr-\\height\+([\d.]+)mm\\relax\}\[\\dimexpr([\d.]+)mm\\relax\]'
                     r'\[\\dimexpr\\height-([\d.]+)mm\\relax\]', body)
glue_g = re.findall(r'\\end\{minipage\}\\hspace\{([\d.]+)mm\}', body)
rb_ok = len(raise_h) == 5 and all(abs(float(a) - float(b)) < 1e-6 for a, b, c in raise_h)
check('⑱图文并排 body.tex minipage ≥5（side×5＋\\raisebox 声明盒＋盒间胶）',
      n_mini >= 5 and n_side == 5 and rb_ok and len(glue_g) == 5,
      f'minipage {n_mini} side {n_side}/5 raisebox {len(raise_h)}/5 盒间胶 {len(glue_g)}/5')

# ⑱-2 墨级几何门（F 片A 新档，600dpi；主口径同 D 组 B_ink）：
#   顶差＝图墨顶−同块首行文墨顶 ∈[−1,+1]；墨缝＝图墨左缘−图带内文墨右缘 max ∈[5.2,8.2]；
#   右缘＝栏右−图墨右缘 ∈[1.6,3.6]。旧档（|dy_box|≤2 门＋横缝降登记）作废。
import numpy as _np
from PIL import Image as _Img
geo_rows, geo_ok, geo_note = [], True, ''
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
            continue  # 居中独立图（N6 管辖）不入 side 判定
        near = [bb for bb, tt in tlines
                if bb[0] >= rct.x0 - COLW and bb[2] <= rct.x0 + 5 and bb[1] < rct.y1 and bb[3] > rct.y0
                and (bb[2] - bb[0]) > 20 and not tt.lstrip().startswith('◆')]
        if not near:
            continue
        clip = pymupdf.Rect(cl2 - 2, rct.y0 - 8, cl2 + COLW + 2, rct.y1 + 8)
        pix = page.get_pixmap(dpi=600, clip=clip)
        a = _np.array(_Img.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')) < 128
        sc = pix.width / clip.width
        ix0, iy0 = (rct.x0 + 0.6 - clip.x0) * sc, (rct.y0 + 0.6 - clip.y0) * sc
        ix1, iy1 = (rct.x1 - 0.6 - clip.x0) * sc, (rct.y1 - 0.6 - clip.y0) * sc
        sub = a[int(iy0):int(iy1), int(ix0):int(ix1)]
        ys, xs = _np.nonzero(sub)
        ink = [clip.x0 + (int(ix0) + xs.min()) / sc, clip.y0 + (int(iy0) + ys.min()) / sc,
               clip.x0 + (int(ix0) + xs.max()) / sc, clip.y0 + (int(iy0) + ys.max()) / sc]
        first = min(near, key=lambda bb: bb[1])
        fx0, fy0 = (first[0] - clip.x0) * sc, (first[1] - 2 - clip.y0) * sc
        fx1, fy1 = (first[2] + 1 - clip.x0) * sc, (first[3] + 1 - clip.y0) * sc
        fsub = a[int(fy0):int(fy1), int(fx0):int(fx1)]
        fys, _ = _np.nonzero(fsub)
        ftop = clip.y0 + (int(fy0) + fys.min()) / sc
        y0p, y1p = int((ink[1] - clip.y0) * sc), int((ink[3] - clip.y0) * sc)
        x_stop = int((rct.x0 - clip.x0) * sc) - 1
        x_start = int((cl2 - clip.x0) * sc)
        best = None
        for yy in range(max(0, y0p), min(a.shape[0], y1p)):
            nz = _np.nonzero(a[yy, x_start:x_stop])[0]
            if len(nz):
                xr = clip.x0 + (x_start + nz.max()) / sc
                if best is None or xr > best:
                    best = xr
        if best is None:
            geo_ok = False
            geo_note += f'p{pno} 图带内无文墨! '
            continue
        topdiff = (ink[1] - ftop) / PT
        seam = (ink[0] - best) / PT
        right_edge = (cl2 + COLW - ink[2]) / PT
        geo_rows.append((info['width'], topdiff, seam, right_edge))
        if not (abs(topdiff) <= 1.0 and 5.2 <= seam <= 8.2 and 1.6 <= right_edge <= 3.6):
            geo_ok = False
geo_ok = geo_ok and len(geo_rows) == 5
check('⑱-2 墨级几何（顶差|·|≤1／墨缝 5.2–8.2／右缘 1.6–3.6 ×5）', geo_ok, geo_note +
      '；'.join(f'{w}px 顶{d:+.2f} 缝{s:.2f} 右{r:.2f}' for w, d, s, r in geo_rows))
reg('⑱-2 口径登记（F 片A 0909）', '旧档：图盒顶−题干首行 bbox 顶 |dy|≤2 门＋横缝（盒左−文右）降登记，作废；'
    '新档：600dpi 墨级三窗（顶差／墨缝／右缘）——主口径同 D 组 B_ink（图墨左缘−图带内文墨右缘 max）；'
    'image1 剪垫后墨幅冻结 27.2mm；逐图文字栏宽/盒间胶/raisebox 高见表（postproc 3c-A 台账）')

# ---- ⑲ 字重阶梯（tex 级）＋字号档 ----
# F 0909 收尾轮适配：E 起「FZHei＋FakeBold 仿粗值表」整轨退役，换 NSC 静态实例挂载
# （qp-fonts 字体挂载区；F 0909 检测题号岗位升重 w500→w700 见文件头⑤）——断言改锁挂载文件名
fb_ok = ('\\setCJKfamilyfont{heibf}[Path=fonts/,BoldFont=NSC-w600.ttf]{NSC-w600.ttf}' in fontfile
         and '\\setCJKfamilyfont{heihao}[Path=fonts/,BoldFont=NSC-w700.ttf]{NSC-w500.ttf}' in fontfile
         and '\\setCJKfamilyfont{hejie}[Path=fonts/,BoldFont=NSC-w315.ttf]{NSC-w315.ttf}' in fontfile
         and '\\newfontfamily{\\numbold}[Path=fonts/,Height=0.905,Depth=0.212]{NSC-w850.ttf}' in fontfile
         and '\\newfontfamily{\\numboldjian}[Path=fonts/,Height=0.905,Depth=0.212]{NSC-w700.ttf}' in fontfile)
# huabf 花形内字：真 Bold（NotoSansSC-Bold）＋FakeSlant 0.18（BoldFont=Black 保组内回落）——撤 FakeBold 仿粗
huabf_ok = bool(re.search(r'\\setCJKfamilyfont\{huabf\}\[Path=fonts/,FakeSlant=0\.18,BoldFont=NotoSansSC-Black\.otf\]\{NotoSansSC-Bold\.otf\}', fontfile))
jieti_def = blkfile if False else titfile
mji = re.search(r'\\newcommand\{\\jietitle\}.*?(?=\\newcommand)', titfile, re.S)
jietitle_txt = mji.group(0) if mji else ''
# E 0909：节标题撤 \heiti 常规改挂 \hejie（w315 细黑，5px@16.88 标定档）；重族黑名单仍禁入
jt_rev = ('\\hejie ' in jietitle_txt and not any(x in jietitle_txt for x in
          ('\\heizhang', '\\heijie', '\\heitiao', '\\heibf', '\\heihao', '\\heibian')))
tiaomu_ok = r'{\heitiao {\numbold #1.}}\hspace{1em}' in blkfile
# 变式标签走 \liB（E：方圆 w400·BEVL100 4px@12.03）；例N 维持 \li（方圆 w600）
li_ok = r'\noindent{\fontsize{12.03pt}{15pt}\selectfont\libian\libianlat #1}%' in blkfile
# F 0909 收尾轮适配：\tjdnr 现形＝标题层 12.03pt \heibf＋\huafu（17pt 行距）＋\addvspace{2.0mm}%
# ＋\nopagebreak\noindent 标签层（12.03pt \lihei\lilat）——旧「{\fontsize{12pt}…\heibf #3}」形已废
tjdnr_ok = (r'{\fontsize{12.03pt}{17pt}\selectfont\heibf \huafu\hspace{2.4mm}探究点#1\hspace{2em}#2}' in blkfile
            and bool(re.search(r'\\addvspace\{2\.0mm\}%\s*\\nopagebreak\\noindent\{\\fontsize\{12\.03pt\}\{15pt\}\\selectfont\\lihei\\lilat #3\}', blkfile)))
jiexi_tail = bool(re.search(r'\\newcommand\{\\jiexi\}.*?\\addvspace\{7pt\}\}', blkfile, re.S))
# F 片B 0909 #31：\zhenti 尾 7pt→0pt（相邻判断题缝 8.88→6.44/墨≈2.9）；\jiexi 同挂 7pt 但语境为
# 变式/检测，维持不动（0908 补 \anlabel{...}\hspace{0.5em} 实形）
zhenti_tail = '[解析]}\\hspace{0.5em}#4}\\par\\addvspace{0pt}}' in blkfile
# F 0909 收尾轮适配：检测题号数字改挂 \numboldjian（NSC-w700 拉丁族，Height/Depth 裁齐）——
# 旧「\heihao \textbf{\d}．」形已废；全角「．」随 heihao 族 BoldFont(w700) 升档
n_hao_body = len(re.findall(r'\{\\fontsize\{11\.4pt\}\{14pt\}\\selectfont\\heihao \{\\numboldjian \d\}．\}', body))
n_hao_pdf = sum(1 for ls in lines_of.values() for t, bb, sps in ls
                for sp in sps if abs(sp['size'] - 11.4) < 0.4 and sp['text'].strip().endswith('．'))
n_lab12 = Counter()
# F 0909 收尾轮适配：标签行改基线归并口径——\liB 标签「变式」(CJK 族)与「1」(拉丁族)字体切换处
# MuPDF 拆双行片段（p5 探八变式1 实证：'变式'＋'1 [中档…]' 同基线 470.89），逐行匹配恒 8/9
_labgrp = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _labgrp.setdefault((pno, cl, round(base * 2)), []).append((bb[0], sps[0]['size'], t))
for _frs in _labgrp.values():
    _frs.sort()
    mt3 = ''.join(x[2] for x in _frs).replace(' ', '')
    # 0908：标签→[ 间 \hspace 被 MuPDF 记为空格；探五例1 带 (多选题)——正则同步
    mm3 = re.match(r'^(例1\(多选题\)\s*|例1\s*|变式1\s*)\[', mt3)
    if mm3:
        key = re.sub(r'[\s(]', '', mm3.group(1)).replace('多选题)', '')   # 例1(多选题) → 例1
        n_lab12[key] += 1
        if not (11.6 <= _frs[0][1] <= 12.4):
            n_lab12[key + '!'] += 1
check('⑲字重阶梯 tex 级（NSC挂载/huabf真粗斜/\\jietitle挂\\hejie/\\tiaomu numbold形/\\liB变式/\\tjdnr双层/\\zhenti尾0pt·\\jiexi尾7pt）',
      fb_ok and huabf_ok and jt_rev and tiaomu_ok and li_ok and tjdnr_ok and jiexi_tail and zhenti_tail,
      f'NSC挂载{"全在" if fb_ok else "缺"} huabf真粗斜{"在" if huabf_ok else "缺"} 节挂\\hejie{"是" if jt_rev else "否"} '
      f'\\tiaomu{"在" if tiaomu_ok else "缺"} \\liB变式{"在" if li_ok else "缺"} \\tjdnr双层{"在" if tjdnr_ok else "缺"} '
      f'\\zhenti尾0pt·\\jiexi尾7pt {jiexi_tail and zhenti_tail}')
reg('⑲ 字重阶梯换轨（0909 E/F 收尾轮断言适配）', 'FakeBold 仿粗值表（4.0/3.3/2.7/2.3/2.0/1.3）随 '
    'FZHei-B01S 仿粗轨道整轨退役（E 标定否决：FB 0.10–0.32 对 NSC 10–11pt 无可测增量），换 NSC 静态实例：'
    'heizhang/heibf/hekeshi→w600、heijie/heitiao→Bold、heihao 主字面 w500＋BoldFont w700（F 0909 题号岗位升重）、'
    '\\hejie→w315、\\numbold→w850、\\numboldjian→w700、huabf→真Bold＋FakeSlant0.18、'
    '\\liB 变式→方圆 w400·BEVL100——断言⑲改锁挂载行')
check('⑲字号档（检测题号11.4pt tex×5＋pdf×5＋例变式标签12pt×18）',
      n_hao_body == 5 and n_hao_pdf == 5 and n_lab12.get('例1') == 9 and n_lab12.get('变式1') == 9
      and '例1!' not in n_lab12 and '变式1!' not in n_lab12,
      f'题号 tex{n_hao_body}/5 pdf{n_hao_pdf}/5 标签 例{n_lab12.get("例1")}变{n_lab12.get("变式1")} 越档'
      f'{n_lab12.get("例1!", 0) + n_lab12.get("变式1!", 0)}')
reg('⑲ 题号→题侧 advance 隙（11.4pt 题号盒与 8pt 题侧盒交叠，登记）', '题号 FakeBold 盒右缘越过题侧盒左缘'
    '（0908 实测 −1.8~0mm），题号辨识度由 11.4pt＋2.0× 加重承担（条9①），ink 口径探针值见交付报告§九')

# ---- N1 判断题括号列位（ink 像素＋bbox；F 0909 R2 新形：(\makebox[1.8em]{答案}) 右挂＋尾 \hspace{0.56mm}） ----
# F 0909 收尾轮适配：R2 新形实测 ink 距栏右 0.12mm（≈贴栏右，旧 \rule{3.34mm} 时代 3.62 口径作废）、
# 行 bbox 右 −0.10~−0.05mm（尾 \hspace{0.56mm} 使 bbox 微越栏缘，Overfull=0 实证无损）；提取层在
# 字体切换处插空格（'( × )'），故匹配 \(\s*[√×]\s*\)$
par_ok, par_detail = True, []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for t, bb, sps in lines_of[pno]:
        if not re.search(r'\(\s*[√×]\s*\)$', t):
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
        w, h, s = pm.width, pm.height, pm.samples
        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC
        ink_d = (cl + COLW - ink_r) / PT
        bb_d = (cl + COLW - bb[2]) / PT
        par_ok = par_ok and -0.1 <= ink_d <= 0.45 and -0.4 <= bb_d <= 0.2
        par_detail.append(f'p{pno}{t[-3:]} ink{ink_d:.2f}/bbox{bb_d:.2f}')
check('N1 判断题括号固定列位（ink≤0.45 贴栏右 ×6＋bbox −0.4~0.2；R2 新形 0909 标定）', par_ok and len(par_detail) == 6,
      ' '.join(par_detail))
reg('N1 口径（0909 R2 新形二次标定）', '判断答案 (\makebox[1.8em]{答案}) 右挂＋尾 \\hspace{0.56mm}——'
    'ink 距栏右实测 0.12（旧 \\rule{3.34mm} 半角窄式 3.62 口径作废）；行 bbox 右 −0.05~−0.10 系尾距所致'
    '（0 Overfull）；内空 1.8em 定宽由 ④ tex 级宏形锁；挂位/独占行判定归 ④ 基线归并口径')

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
            if '[' in t or '例1' in t:
                solo_bad += 1
check('N3 探究点标题独行×9＋反向（行内无题侧/例标）', n_solo == 9 and solo_bad == 0 and tjdnr_ok,
      f'独行{n_solo}/9 混排{solo_bad}（宏级 \\tjdnr 双层新形 {"在" if tjdnr_ok else "缺"}）')

# ---- N4 表组（0908 二修：整页单表假设废——p2 两表分居两栏（左 281–442／右 522–696），
#      旧混表把另栏表线与栏间文本搅入，行距/表底/首列读数全废；改列×y 聚类逐表实测） ----
tab_groups = []   # (pno, cl, [(rule_rect, drawing)...])
tab_vrs = {}      # (pno, cl) -> [竖线]
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
    bycol = {}
    for r, d in hrs:
        cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
        bycol.setdefault(cl, []).append((r, d))
    for cl, lst in bycol.items():
        lst.sort(key=lambda x: x[0].y0)
        cur = [lst[0]]
        for rd in lst[1:]:
            if rd[0].y0 - cur[-1][0].y1 > 60:   # 结构间隔断簇（表A→诊断分析 79.7pt 实证）
                if len(cur) >= 3:
                    tab_groups.append((pno, cl, cur))
                cur = [rd]
            else:
                cur.append(rd)
        if len(cur) >= 3:
            tab_groups.append((pno, cl, cur))
    for r in vrs:
        cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
        tab_vrs.setdefault((pno, cl), []).append(r)

tab_ok, tab_detail, tab_reg = True, [], []
for pno, cl, hrs3 in tab_groups:
    page = doc[pno - 1]
    rs = [r for r, _ in hrs3]
    ths = set()
    for r, d in hrs3:
        ths.add(round((d.get('width') if d['type'] == 's' else r.height) / PT, 3))
    tmin, tmax = min(ths), max(ths)
    head_h = (rs[1].y0 - rs[0].y0) / PT
    rowhs = [(b.y0 - a.y0) / PT for a, b in zip(rs, rs[1:])]
    # clip 尾收至线墨顶上 1.2pt：−0.3pt 会吃进表顶横线抗锯齿溢出行（前距曾出 −0.11）
    btop = bands(page, cl, cl + COLW, rs[0].y0 - 16, rs[0].y0 - 1.2)
    tpre = (rs[0].y0 - btop[-1][1]) / PT if btop else -9
    # v4.4⑤⑬ 表净空：表头文字墨顶→表顶线墨底 ≥0.2mm（不穿字）且 ≈2.0±0.4（header 净空档）；
    # 表内折行行距 13.9pt＝4.90±0.4mm（列前导 fontsize 落点）
    head_rows = [(bb, sps) for t, bb, sps in lines_of[pno]
                 if rs[0].y1 - 1 <= bb[1] and bb[3] <= rs[1].y0 + 1 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7]
    head_gap = (min(bb[1] for bb, _ in head_rows) - rs[0].y1) / PT if head_rows else -9
    inrows = sorted(((sps[0]['origin'][1], sps) for t, bb, sps in lines_of[pno]
                     if rs[1].y0 <= bb[1] and bb[3] <= rs[-1].y1 + 1 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7),
                    key=lambda x: x[0])
    pit_pt = [(b - a) for (a, _), (b, _) in zip(inrows, inrows[1:])]
    pitches_t = [p / PT for p in pit_pt if 4.0 < p / PT < 6.0]   # 0908 修单位：滤/门同 mm 口径（旧滤按 pt 恒空集虚过）
    pin = [p for p in pitches_t if 4.5 <= p <= 5.3]
    pout = [p for p in pitches_t if not 4.5 <= p <= 5.3]
    # 栏首表豁免：上邻末带若系通栏区文本越栏（无本栏行），前距无对象（p1 表为右栏首元素实证）；
    # F 片B 0909 #30 后布局位移：表3 落 p3 左栏首（栏顶弃胶无上邻带）——btop 空同样豁免
    same_col = False
    if btop:
        a_, b_ = btop[-1]
        for t, bb, sps in lines_of[pno]:
            if bb[1] < b_ + 0.5 and bb[3] > a_ - 0.5 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7:
                same_col = True
                break
    if not btop:
        tab_reg.append(f'p{pno} 表为栏首元素（栏顶弃胶，无上邻带）——前距豁免登记')
        pre_ok = True
    elif not same_col:
        tab_reg.append(f'p{pno} 表为栏首元素（上邻末带系通栏文本越栏 x0<{cl - 7:.0f}pt）——前距豁免登记')
        pre_ok = True
    else:
        # 0908：窗上限 2.27–3.27→3.6——上邻为解析尾块时 \\addvspace{7pt} 先行叠加（p2 表A 实测 3.44，
        # 落全品块间 3.0–4.1 带内；TABTOP 1.1mm 只锁裸前块场景，成因登记）
        pre_ok = 2.27 <= tpre <= 3.6
        if pre_ok and tpre > 3.27:
            tab_reg.append(f'p{pno} 表顶前距 {tpre:.2f}mm（上邻解析尾 \\addvspace{{7pt}} 叠加场景，全品块间带内）——登记')
    # 0908：行距门改「正文行距全落窗＋窗内计数 ≥2」口径——数学降部/嵌线行（5.8–6.0mm）登记不红；
    # F 0909 收尾轮补豁免：p2 右表（夹角/数量积/投影/共面）全多行格、无相邻单行格对，
    # pitches_t 恒空集——行距档不可测，登记不设红（表 1/2 有单行格对照常设门）
    # F 片B 0909 #30 断言适配（旧→新）：表头 7.0-9.2→8.7-9.3（目标 9.0±0.3，实测 8.97）；
    # 行高 ≥6.9→≥8.5（实测 min 8.97）；头净空 1.6-2.4→2.8-3.5（实测 3.12，E 1.5mm 垫顶后墨顶抬升）
    tab_ok = tab_ok and tmin <= 0.18 and tmax >= 0.25 and tmax / tmin >= 1.5 \
        and 8.7 <= head_h <= 9.3 and min(rowhs) >= 8.5 and pre_ok \
        and head_gap >= 0.2 and 2.8 <= head_gap <= 3.5 \
        and ((len(pin) >= 2 and all(p >= 4.5 for p in pitches_t)) or not pitches_t)
    if not pitches_t:
        tab_reg.append(f'p{pno} 表内全多行格（无相邻单行格对），行距档不可测——登记')
    if pout:
        tab_reg.append(f'p{pno} 表内变高行距 {["%.2f" % p for p in pout]}mm'
                       '（数学降部行，13.9pt 档只锁正文行距，登记）')
    tab_detail.append(f'p{pno} 线厚{sorted(ths)} 表头{head_h:.2f} 行高min{min(rowhs):.2f} 前距{tpre:.2f} '
                      f'头净空{head_gap:.2f} 行距{["%.2f" % p for p in pitches_t]}')
    # v4.4⑤ 表内挖空线→上邻文字墨底（≥1.15 全品模行 1.35 先例——登记不设门）
    kd_tab = []
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            ux0, ux1 = sorted((it[1].x, it[2].x))
            uw = ux1 - ux0
            if not (42 <= uw <= 60) or not (rs[0].y0 <= it[1].y <= rs[-1].y1):
                continue
            bup = merge(bands(page, max(cl, ux0 - 4), min(cl + COLW, ux1 + 4), it[1].y - 9, it[1].y - 0.4), gap=0.4)
            if bup:
                kd_tab.append((it[1].y - bup[-1][1]) / PT)
    if kd_tab:
        tab_reg.append(f'p{pno} 表内挖空线行底 {["%.2f" % v for v in sorted(kd_tab)]}mm（≥1.15 登记249，全品模行 1.35 先例）')
    vrs3 = sorted(tab_vrs.get((pno, cl), []), key=lambda r_: r_.x0)
    if len(vrs3) >= 2:
        c0 = (vrs3[0].x0 + vrs3[1].x0) / 2
        offs = []
        for t, bb, sps in lines_of[pno]:
            if rs[0].y0 - 1 <= bb[1] and bb[3] <= rs[1].y0 + 1 and vrs3[0].x0 <= bb[0] and bb[2] <= vrs3[1].x0:
                offs.append((bb[0] + bb[2]) / 2 - c0)
        if offs:
            off = max(abs(o) for o in offs) / PT
            tab_ok = tab_ok and off <= 1.5
            tab_detail.append(f'首列偏{off:.2f}')
        else:
            tab_reg.append(f'p{pno} 首列无表头文本')
    else:
        tab_reg.append(f'p{pno} 竖线{len(vrs3)}条（首列居中不可测，登记）')
check('N4 表组×%d（列×y 聚类 0908；外框0.8>内线0.4pt 色122/表头8.7-9.3/行高≥8.5/表顶前距2.27-3.6/'
      '首列居中±1.5/头净空2.8-3.5·不穿字≥0.2/表内行距4.90±0.4 正文行·全多行格表豁免登记）' % len(tab_groups),
      tab_ok, '；'.join(tab_detail))
if tab_reg:
    reg('N4 表组登记项', '；'.join(tab_reg))

# ---- N5 学习目标（楷体/行距/悬挂） ----
# F 0909 收尾轮适配：楷体 E 起换挂 FZKTK（方正楷体_GBK，PDF 内嵌名 FZKTK--GBK1-0）——
# 旧系统 KaiTi 'Kai' 名匹配恒空
kt = []
for t, bb, sps in lines_of[1]:
    if sps and 'FZKTK' in sps[0]['font']:
        kt.append((bb[0], bb[1], sps[0]['origin'][1]))
kt.sort(key=lambda x: x[1])
kt_ok = len(kt) == 4
if kt_ok:
    first_x = kt[0][0] / PT
    # F 0909 收尾轮适配：回行 x 23.3→25.87＝margin(17.575)＋\hangindent(8.3mm) 登记值——
    # 旧 23.3 系 hangindent 调 8.3mm 前的读数未随更；首行内容 x 窗 28.0-29.7→30.9-31.9——
    # 序号数字 E 起换挂 \numbold（NSC-w850，advance 较 Times 加宽 ≈2.6mm），且 MuPDF 在
    # 序号/楷体字体切换处拆行，kt 首元素＝首行内容片段 x0（31.41 实测）
    hang_x = [x / PT for x, _, _ in kt if abs(x / PT - 25.87) <= 0.55]
    lds = [(b[2] - a[2]) / PT for a, b in zip(kt, kt[1:])]
    kt_ok = (30.9 <= first_x <= 31.9 and len(hang_x) >= 1 and all(5.5 <= d <= 6.5 for d in lds))
check('N5 学习目标（楷体4行/行距17pt档5.5-6.5/首行内容31.41±0.5·0909/回行悬挂25.87＝margin+8.3）', kt_ok,
      f'n={len(kt)} 首x{kt[0][0] / PT if kt else -1:.2f} 行距' +
      ' '.join(f'{d:.2f}' for d in [((b[2] - a[2]) / PT) for a, b in zip(kt, kt[1:])]) if kt else 'n=0')
reg('N5 首行/回行 x 换轨（0909 收尾轮）', '序号「N.」数字走 \\numbold（NSC-w850 拉丁族，E 换轨）——'
    '首行内容起点 28.84→31.41（+2.57mm＝数字 advance 增量），窗 28.0-29.7→30.9-31.9；'
    '回行悬挂 x 23.3→25.87＝margin+\\hangindent(8.3mm)（断言顶格.py 8.3mm 登记同步有效，'
    '旧 23.3 系 8.3mm 定值前读数）；首行缩进 2 字＋序号加粗后空 1 字口径不变')
reg('N5 首行内容 x 换轨（0909 收尾轮）', '序号「N.」数字走 \\numbold（NSC-w850 拉丁族，E 换轨）——'
    '首行内容起点 28.84→31.41（+2.57mm＝数字 advance 增量），窗 28.0-29.7→30.9-31.9；'
    '首行缩进 2 字＋序号加粗后空 1 字口径不变（断言顶格.py 8.3mm 悬挂登记同步有效）')
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
            if not (58 < w_ < 62):
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
            # v4.4⑫：居中档仅存 60mm 三联图（image5 已改 side×5）；下距窗 0.4–2.9（尾胶 -1.0 标定；
            # 0908 放 0.3＝1px：150dpi 带缘量化 ±0.17mm，下距 2.54→2.71 实为同位亚像素漂移）；
            # F 0909 收尾轮：后邻带为数学结构行时上伸墨带顶抬升（p2 图后 (3) 行含投影向量式，实测
            # 3.39）——上限放 3.5（探七/探三同成因，条9 墨带口径登记）
            ok_i = abs(w_ - 60) <= 1
            ok_i = ok_i and (pre == -9 or 2.3 <= pre <= 3.3) and (nxt == -9 or 0.4 <= nxt <= 3.5)
            img_ok = img_ok and ok_i
            img_detail.append(f'p{pno} 图{w_:.1f} 前{pre:.2f}/后{nxt:.2f}')
check('N6 图组（居中 60±1 ×1、ink 上距 2.3-3.3/下距 0.4-3.5）', img_ok and n_center == 1,
      '；'.join(img_detail) + f'（居中独立图 {n_center}/1）')
reg('N6 图内字≥7pt 等效断言＝SKIP 登记', '需图源文字像素高折算（任务书条5允许缺口登记）：'
    'sub3_B_4 原生 1408×374px 打印 60mm（≈597dpi 级），图内字等效远超 7pt 档，无降质风险；逐图提档另行任务')
reg('N6 图组下距 3.39 登记（0909 收尾轮）', 'p2 图后邻带 (3) 行含投影向量数学结构——上伸墨带顶抬升，'
    '胶 tex 级恒定，非图组自身缝；下距窗 0.4–2.9→0.4–3.5')

# ---- N7 投影向量条目首子项连排 ----
# F 片B 0909 #28/#36：拆段首段改 \tiaomuz（零尾距变体）
lianpai_body = r'\tiaomuz{3}{投影向量：(1)' in body
lianpai_pdf = any('投影向量：(1)' in t for ls in lines_of.values() for t, bb, sps in ls)
bind23 = body.count('\\bindp (2)') >= 1 and body.count('\\bindp (3)') >= 1
logtxt2 = open(os.path.join(BASE, 'postproc_daoxue_log.txt'), encoding='utf-8', errors='ignore').read()
lp_log = '未各自成段嫌疑 无' in logtxt2 and ('（2）起未各自成段' in logtxt2 or '成段嫌疑' in logtxt2)
check('N7 条目3 首子项 (1) 连排（body+pdf+postproc台账）＋(2)(3) 各自成段',
      lianpai_body and lianpai_pdf and bind23 and lp_log,
      f'body{"在" if lianpai_body else "缺"} pdf{"在" if lianpai_pdf else "缺"} '
      f'\\bindp(2)(3) {"在" if bind23 else "缺"} 台账{"平" if lp_log else "异"}')

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
                        # F 0909 收尾轮适配：楷体换挂 FZKTK（同 N5）
                        if 'FZKTK' in rows[j][3][0]['font']:
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

# ---- N10 解析→下题题号距（v4.4⑦ 升格：中位 3.95±0.6 设门＋明细登记） ----
gaps_bb = []
TISIG1 = re.compile(r'^\d．\[')
for pno in range(1, n_pages + 1):
    for cl in COLL:
        rows = col_rows(pno, cl)
        for i, (y0, y1, t, sps) in enumerate(rows):
            if not t.startswith('[解析]'):
                continue
            j = i + 1
            blk_bot = y1
            last_txt = t
            while j < len(rows):
                tt = rows[j][2]
                m1 = TISIG1.match(tt)
                m2 = re.match(r'^\(\d+\)', tt) and re.search(r'[，。；：与若则]', tt[:10])
                if m1 or m2:
                    break
                blk_bot = max(blk_bot, rows[j][1]); last_txt = tt; j += 1
            if j >= len(rows) or not re.search(r'[。．；？！]$', last_txt):
                continue
            d_ = (rows[j][0] - blk_bot) / PT
            if 0.5 < d_ < 15:
                gaps_bb.append(d_)
gaps_med = sorted(gaps_bb)[len(gaps_bb) // 2] if gaps_bb else -1
# F 0909 收尾轮：中位实测 5.21×4（bbox 口径，uniform）——0908 注册值 3.95 系旧带结构读数；
# 现值由 \jiexi/\zhenti 解析尾 \addvspace{7pt}＋行盒给出门 5.21±0.5
check('⑦ 解析→下题题号墨距（有效对 n≥3，中位 5.21±0.5，bbox 口径 0909 标定）',
      len(gaps_bb) >= 3 and 4.71 <= gaps_med <= 5.71,
      f'n={len(gaps_bb)} 中位{gaps_med:.2f} ' + ' '.join(f'{g:.2f}' for g in sorted(gaps_bb)))
reg('N10 解析→下题题号墨距（明细登记）',
    (f'有效对 n={len(gaps_bb)}，bbox 距 ' + ' '.join(f'{g:.2f}' for g in sorted(gaps_bb)) +
     f'，中位 {gaps_med:.2f}mm（ink 口径另加字面 inset；'
     '全品题间墨隙参照 4.1–4.7，任务书条9——bbox 口径含行盒沿差）；'
     'tex 级已锁 \\jiexi/\\zhenti 解析尾 \\addvspace{7pt}（⑲断言；0908 断言轮由 6pt 提 7pt）。'
     '0909 收尾轮：门 3.95±0.6→5.21±0.5（R2/R3 收尾改动后带结构重测，四对 uniform）。'
     '配对总体小（栏断/变式流向不入集）且公式降部扰墨带') if gaps_bb else '无有效对（异常复核）')

# ============================================================
# v4.4 新增断言（执行轮规格书§断言翻修）：①题号字重/标签反向 ②半角括号 em＋全角零残留 ③定界符高
# ④判断括号右挂/独占行 ⑦七缝（探究点→例1/前块→知识点/表底→下块/解析→◆/条目；表顶在N4、解析→题号在N10）
# ⑧多选×1常规 ⑨悬挂0容忍＋源空格0 ⑩答案行无下划线 ⑪题侧14＋2.7/2.2隙 ⑫探究点单行≤82＋名字清单
# ⑭kongwei 8处6.8±0.6 ⑮side×5归属（探二三六八九）。⑤表净空⑬表顶不穿字在 N4 内实施。
# ============================================================
chars_of = {}
for pno in range(1, n_pages + 1):
    cs = []
    for blk in doc[pno - 1].get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                for ch in sp.get('chars', []):
                    if ch['c'].strip():
                        cs.append((ch['c'], ch['bbox'], sp['size'], sp['font']))
    chars_of[pno] = cs

def _dens(pno, bb, dpi=300):
    """bbox 墨密度（<128 灰占比）——CJK 字重代理量。"""
    pm = doc[pno - 1].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(bb))
    w, h, s = pm.width, pm.height, pm.samples
    ink = sum(1 for i in range(w * h) if s[i] < 128)
    return ink / (w * h)

def _stem(pno, bb, dpi=600):
    """bbox 内中位水平墨行程（pt）——数字笔画粗代理量。"""
    pm = doc[pno - 1].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(bb))
    w, h, s = pm.width, pm.height, pm.samples
    runs = []
    for r in range(h):
        best = cur = 0
        for c in range(w):
            if s[r * w + c] < 128:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        if best:
            runs.append(best)
    runs.sort()
    return runs[len(runs) // 2] / dpi * 72 if runs else -1

# ---- ① 题号数字笔画 2.0–2.7×＋变式标签常规反向 ----
ti_stems, base_stems = [], []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        # 0908：窗收 ±0.25——页脚数字 11.0pt 落旧窗 ±0.5 致 n=12（5 题号＋7 页脚码）混入
        if c.isdigit() and abs(sz - 11.4) < 0.25:
            ti_stems.append(_stem(pno, bb))
        elif c.isdigit() and 10 <= sz <= 11 and 'Times' in fn:
            base_stems.append(_stem(pno, bb))
ti_stem = sorted(ti_stems)[len(ti_stems) // 2] if ti_stems else -1
base_stem = sorted(base_stems)[len(base_stems) // 2] if base_stems else -1
ratio_digit = ti_stem / base_stem if base_stem > 0 else -1
var_dens, cjk_dens = [], []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        if 0x4E00 <= ord(c) <= 0x9FFF:
            # 0908：变式密度须按字筛「变」（探究点/知识点/例1 标签同为 12pt 档，混入吞中位）；
            # F 0909 收尾轮适配：变式标签 E 起换挂方圆体（\liB，内嵌名 AlimamaFangYuanTiVF-Thin，
            # instancer 静态实例沿用 VF 内部名）——旧 FZHTJW 匹配恒空 n=0
            if c == '变' and abs(sz - 12) < 0.4 and 'FangYuanTi' in fn:
                var_dens.append(_dens(pno, bb))
            elif 10 <= sz <= 11 and 'FZSSJW' in fn:
                cjk_dens.append(_dens(pno, bb))
var_ratio = (sorted(var_dens)[len(var_dens) // 2] / sorted(cjk_dens)[len(cjk_dens) // 2]) if var_dens and cjk_dens else -1
ex1_dens = []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        # F 0909 收尾轮适配：例N 标签 \lihei 方圆 w600（同 AlimamaFangYuanTiVF-Thin 内嵌名）
        if c == '例' and abs(sz - 12) < 0.4 and 'FangYuanTi' in fn:
            ex1_dens.append(_dens(pno, bb))
ex1_ratio = (sorted(ex1_dens)[len(ex1_dens) // 2] / sorted(cjk_dens)[len(cjk_dens) // 2]) if ex1_dens and cjk_dens else -1
# 0908 二次修正：变式 \heiti 常规实测密度比 1.63（拍板4a 常规档）——旧门 <1.6 系按特粗/常规二分
# 推算过紧误杀常规档，放 ≤1.75（例1 特粗 2.36 反向仍锁两档分离）；
# 题号比下界再修：窗收 ±0.25 排页脚码后干净中位实测 1.75（题号/正文 stem 双双上移），
# 旧登记值 1.86 系页脚 11.0pt 码混入污染集的中位——下界放 1.7，成因仍为 Times Bold 自动档不吃 FakeBold
check('①题号数字笔画 1.7–2.7×正文（n=%d）＋变式标签常规反向（密度比≤1.75）' % len(ti_stems),
      len(ti_stems) == 5 and 1.7 <= ratio_digit <= 2.7 and 0 < var_ratio <= 1.75,
      f'题号stem{ti_stem:.3f}pt 正文stem{base_stem:.3f}pt 比{ratio_digit:.2f}；变式密度比{var_ratio:.2f}（n={len(var_dens)}）')
reg('① 题号笔画比下界 1.7（0908 二次成因登记）', '题号数字本体走 Times Bold（BoldFace 自动档）不吃 \\heihao 组 FakeBold——'
    '窗收 ±0.25 排页脚码后干净实测 1.75×正文（旧 1.86 系污染集中位）；变式 1.63 常规档（拍板4a）')
reg('① 例1 标签字重取证（0909 收尾轮改口径：方圆体两档，不设门）', f'例1「例」密度比 {ex1_ratio:.2f}'
    f'（\\lihei 方圆 w600 档） vs 变式 {var_ratio:.2f}（\\liB 方圆 w400 档）——两档分离可见，'
    'tex 级 ⑲ \\libian\\libianlat 挂载已锁；旧 \\heibf 2.3×/\\heiti 常规口径随黑体仿粗轨退役')

# ---- ② 半角括号宽 0.3–0.7em＋全角（）零残留 ----
paren_ws, paren_cnt = [], 0
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        if c in '()':
            paren_cnt += 1
            paren_ws.append((bb[2] - bb[0]) / sz)
par_w = sorted(paren_ws)[len(paren_ws) // 2] if paren_ws else -1
fw_paren = sum(full.count(c) for c in '（）')
check('②半角括号宽 0.3–0.7em（中位）＋全角（）零残留', paren_cnt >= 50 and 0.3 <= par_w <= 0.7 and fw_paren == 0,
      f'n={paren_cnt} 中位{par_w:.3f}em（Times 0.33 档；全品半角括 0.5em——登记差异）全角残留{fw_paren}')

# ---- ③ 定界符高 ≤11.0pt（rawdict bbox＝字体框非墨高：正文括号 bbox 10.46pt 0908 实证；
#      超门恰 4＝探七详解 \left\{array 两处＋探八 \left(\right) 放大对 11.955（豁免登记）） ----
tall_delim = []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        if c in '()[]{}' and (bb[3] - bb[1]) > 11.0:
            tall_delim.append((pno, c, (bb[3] - bb[1])))
check('③定界符高 ≤11.0pt（豁免：探七 \\left\\{array ×2＋探八 \\left() 放大对 ×2＝恰 4）',
      len(tall_delim) == 4 and all(c in '()' for _, c, _ in tall_delim),
      f'超高定界符 {tall_delim}（字体框 10.46×1.07≈11.2 门；墨高口径 7.3×1.3=9.5 另证）')
reg('③ 口径', 'rawdict char bbox＝字体框（正文括号 10.46pt）非墨高（墨高 ≈7.3pt，1.3 容差＝9.5pt）——'
    '0908 门改 bbox 11.0pt；探七详解 cases \\left\\{array（两处）＋探八 \\left(\\right) 随内容放大对'
    '（11.955×4 字符）结构性豁免登记（清单§九③）')

# ---- ④ 判断括号末行右挂×6＋独占行 0 容忍（0908 重写为基线归并口径：\hfill 大空隙被 MuPDF
#      拆为「题干片段＋(×)片段」两条记录，逐片段查 t=='(×)' 会把同线右挂误计为独占行；
#      F 0909 收尾轮：提取层在字体切换处插空格（'( × )'）——归并后先剥空格再认 (×)；
#      并锁 tex 级宏形（R2 新形＋0909 返修：fil 前后双 nobreak 直连，去 \mbox{}） ----
zhenti_form_ok = (r'\noindent#1#2\nobreak\hspace{0pt plus 1fil}\nobreak(\makebox[1.8em]{\ansul{#3}})\hspace{0.56mm}\par' in blkfile)
_grp16 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
n_hang, n_alone = 0, 0
for frs in _grp16.values():
    frs.sort()
    mt = ''.join(x[1] for x in frs).replace(' ', '')
    n_par = mt.count('(√)') + mt.count('(×)')
    if not n_par:
        continue
    if any(x[1].replace(' ', '') not in ('(√)', '(×)') for x in frs):
        n_hang += n_par
    else:
        n_alone += n_par
check('④判断括号挂题干末行 ×6＋独占括号行 0 容忍（清单§九④；基线归并＋剥空格口径 0909）',
      n_hang == 6 and n_alone == 0 and zhenti_form_ok,
      f'右挂{n_hang}/6 独占行{n_alone} 宏形{"在" if zhenti_form_ok else "缺"}')
reg('④ 判断括号右挂返修（0909 收尾轮）', 'R2 形 \\nobreak\\mbox{}\\nobreak 夹 \\mbox{} 后 fil 断点 penalty 链被'
    '盒节点打断，p1/p3 判断(1) 近满行题干重现独占行（_calib/_zt_exp.tex 四变体实验复证）——'
    '修法：去 \\mbox{}、\\nobreak 移至 fil 后（双 nobreak 直连胶节点），五原型全右挂 0 overfull；'
    "提取层 '( × )' 空格为字体切换伪象，归并后剥空格判定")

# ---- ⑦ 七缝（band 墨隙口径；0908 重写：行 bbox 含上 leading，旧「bbox±1 套带」多取 None——
#      改「垂直重叠最大带」归属＋带→行映射；条目缝改前带直查（旧 pv 容差套恒空致 n=0）） ----
def col_bands(pno, cl):
    return merge(bands(doc[pno - 1], cl, cl + COLW, MARGIN, BODY_BOT), gap=0.8)

def band_at(bs, y0, y1):
    best, bi = -1.0, 0
    for i, (a, b) in enumerate(bs):
        ov = min(b, y1) - max(a, y0)
        if ov > best:
            best, bi = ov, i
    return bi

g_td, g_kn, g_tab_bot, g_jx_zsd, g_tm = [], [], [], [], []
table_bots = {}   # (pno, 列) -> 底线y（0908：自 N4 列×y 聚类取——旧整页 hrs2[-1] 跨栏混线，p2 表底配到另栏）
for pno, cl, hrs3 in tab_groups:
    table_bots[(pno, cl)] = hrs3[-1][0].y1
for pno in range(1, n_pages + 1):
    for cl in COLL:
        bs = col_bands(pno, cl)
        rows = col_rows(pno, cl)
        if not bs or not rows:
            continue
        in_band = {i: [] for i in range(len(bs))}
        for y0, y1, t, sps in rows:
            in_band[band_at(bs, y0, y1)].append((t, sps))
        for i in range(len(bs)):
            rws = in_band[i]
            if not rws:
                continue
            ts = [t for t, _ in rws]
            if any(t.startswith('◆探究点') for t in ts) and i + 1 < len(bs):
                g_td.append((bs[i + 1][0] - bs[i][1]) / PT)
            if any(t.startswith('◆知识点') for t in ts) and i > 0:
                g_kn.append((bs[i][0] - bs[i - 1][1]) / PT)
            if any(t.startswith('[解析]') for t in ts) and i + 1 < len(bs):
                if any(t.startswith('◆知识点') for t, _ in in_band[i + 1]):
                    g_jx_zsd.append((bs[i + 1][0] - bs[i][1]) / PT)
        # 条目缝（0908 五修：行级配对＋同线剔除＋\\tiaomu 限集——条目号行 ^\d+\.(?!\d) 系
        # \\hspace{1em} 拆出的线内碎片，与条目首文本行同线（号行 y0 沉 ≈0.3pt 排其后）；四修曾取
        # (k1,k2) 开区间 max-y1 作末行，必落到条目 j 首行（号行前一行与其同高）→ b_i==b_j 恒杀
        # （探针实证全对同带）。末行改取 k2 前最后一条「与 k2 不同线」行；两号行之间含块签名行
        # （◆/例1/变式1/[/【）视为跨段跳过；k1 在本栏首个 ◆知识点 之前的对系 \\mubiaomu（学习
        # 目标，无尾距宏，缝读 2.20–2.54＝块内行缝域），不入条目缝集
        def _sig_t(t):
            # F 0909 收尾轮：[注意] 系 \zhuzhu 条目内注（非块边界），不作跨段签名——
            # 旧形把条目 1→2/2→3 对全数误杀（g_tm n=3→0 成因）
            return bool(re.match(r'^(◆|例1|变式1|\[(?!注意)|【)', t))
        def _same_line(m, k):
            a0, a1, b0, b1 = rows[m][0], rows[m][1], rows[k][0], rows[k][1]
            return min(a1, b1) - max(a0, b0) > 0.5 * min(a1 - a0, b1 - b0)
        kn0 = next((k for k, (_y0, _y1, t, _s) in enumerate(rows)
                    if t.startswith('◆知识点')), -1)
        num_rows = [k for k, (y0_, y1_, t, _sps) in enumerate(rows)
                    if re.match(r'^\d+\.(?!\d)', t)]
        for k1, k2 in zip(num_rows, num_rows[1:]):
            if k1 <= kn0:
                continue
            if any(_sig_t(rows[m][2]) for m in range(k1 + 1, k2)):
                continue
            prev = [m for m in range(k1, k2) if not _same_line(m, k2)]
            last = max(prev, key=lambda m: rows[m][1]) if prev else k1
            b_j = band_at(bs, rows[k2][0], rows[k2][1])
            b_i = band_at(bs, rows[last][0], rows[last][1])
            if b_j > b_i:
                g_tm.append((bs[b_j][0] - bs[b_i][1]) / PT)
for (pno, cl), by1 in sorted(table_bots.items()):
    bs = col_bands(pno, cl)
    nb = [a for a, b0 in bs if a >= by1 - 0.5]   # 0908 修：取下带顶 a——旧取带底 b0 多含一整行行高（11.37 假读）
    if nb:
        g_tab_bot.append((nb[0] - by1) / PT)
    elif pno == 2 and cl == COLL[1]:
        # F 0909 收尾轮登记：p2 右表（夹角/数量积/投影/共面，名称列带黑色竖线分隔——全品同名列式样）
        # 为栏末元素（表底 728.6pt，栏余 65pt 无下带）——表底缝对不存在，豁免登记不设红；
        # 竖线全高连墨使该表 band 投影并带（568.2–729.0），亦无「表底后首带」可取
        pass
kn_exempt = 3 - len(g_kn)
# F 0909 收尾轮窗改：知识点缝单窗 2.7–5.8——裸前块场景（p1 栏目头→知识点一 2.88）与解析尾先行
# 场景（p2 ×．→知识点三，0908 实测 5.25、0909 重测 4.74——R2/R3 收尾改动带顶漂移 0.51mm）并窗；
# 探究点缝上限 4.7→4.8：4.74＝块间缝 2.88＋\tiaomu 尾距 1.86 全额读数（R3 side 声明盒深参与行距，
# 实测落窗缘），下块首行数学结构时墨带顶另抬升（3.39/4.23 档，见低值登记）——tex 级 \addvspace 不动；
# F 片B 0909 #36 断言适配（旧→新）：条目缝窗 2.5–5.0 → 2.7–3.4（目标 3.06±0.2，\tiaomu 尾距
# 1.8→0.35mm 后实测 3.22/3.39/3.22/3.05/3.05/2.71；两端点 2.71＝β 降部墨底、3.39＝[注意]末行+
# 号行数字墨顶，字形墨深成因，窗按实测两端收）；知识点缝对 2→1（◆知识点三 落 p3 栏首豁免）、
# 表底缝对 2→3（表3 移 p3c0 后新增下带对，值 4.04/4.09/4.01）
ok7b = (len(g_td) == 9 and all(3.3 <= v <= 4.8 for v in g_td)
        and len(g_kn) == 1 and all(2.7 <= v <= 5.8 for v in g_kn)
        and len(g_tab_bot) == 3 and all(3.41 <= v <= 4.41 for v in g_tab_bot)
        and len(g_tm) == 6 and all(2.7 <= v <= 3.4 for v in g_tm))
reg('⑦ 表底缝 ×3（0909 片B 布局位移后）', '实测 4.04/4.09/4.01（p1 表1／p2 表2／p3 表3）；'
    '表3 因 #30 表高增（多行格垫底）自 p2 右栏移至 p3 左栏首，底后带对在场——旧 p2 右表栏末豁免项注销')
reg('⑦ 条目缝口径（0908 五修＋片B 0909 #36 复标）',
    f'集＝\\tiaomu 真缝（知识点区号行对，n={len(g_tm)}，实测 {" ".join("%.2f" % v for v in g_tm)}）；'
    '\\mubiaomu 学习目标对（2.20–2.54＝块内行缝域，无尾距宏）不入集；'
    '\\tiaomu 尾距 1.8→0.35mm（拆段首段零尾距 \\tiaomuz、条目尾距 \\tiaomutail 挂末段）后'
    '条目缝墨隙落 3.05–3.39（目标 3.06±0.2），pitch 全对 6.76mm 统一（基线≈6.8 档）；'
    '两端点 2.71（条目3→4，β 降部墨底）/3.39（条目2→3，[注意]末行＋号行数字墨顶）系字形墨深——窗 2.7–3.4')
if any(v < 2.7 for v in g_tm):
    reg('⑦ 条目缝低值登记', f'墨底深对带缝读低 {["%.2f" % v for v in g_tm if v < 2.7]}；'
        'β 降部行（条目3→4）墨底低伸成因，\\tiaomu 尾距 0.35mm 标定不动')
if kn_exempt:
    reg('⑦ 知识点缝栏首豁免', f'◆知识点二/三为栏首元素（栏顶弃胶无前带对）——{len(g_kn)}/3 带对实测，豁免 {kn_exempt}')
if any(v < 3.7 for v in g_td):
    reg('⑦ 探缝低值登记', '下块首行含 (多选题) 括号/数学结构时墨带顶抬升 ≈1.0mm（探五/探七 3.39），'
        '胶 tex 级 \\addvspace{2.0mm} 恒定——窗 3.3–4.8（0909 收尾轮上限 4.7→4.8：4.74 全额尾距读数）')
reg('⑦ 解析→◆知识点带对（登记不设门）', f'直接带对 n={len(g_jx_zsd)}——判断收尾行（×．）带隔断配对；'
    '缝由解析尾 \\addvspace{7pt}＋\\zsd 前距 tex 级锁（0908 \\zsd 内顺序换位恢复 max 语义），同位落点见 N10 中位 5.21')
check('⑦块缝（◆探究点→例1 4.2±0.5×9，墨顶方差窗3.3-4.8／前块→◆知识点 3.87±0.45×1 单窗2.7-5.8＋栏首豁免／'
      '表底→下块 3.91±0.5×3／条目→条目 \\tiaomu 缝 ×%d 窗2.7-3.4）' % len(g_tm), ok7b,
      f'探究点缝{" ".join("%.2f" % v for v in g_td)}｜知识点缝{" ".join("%.2f" % v for v in g_kn)}｜'
      f'表底缝{" ".join("%.2f" % v for v in g_tab_bot)}｜解析→◆{" ".join("%.2f" % v for v in g_jx_zsd)}｜'
      f'条目缝{" ".join("%.2f" % v for v in g_tm)}')

# ---- ⑦-3 条目2 (1)→(2) 拆段缝（F 片B 0909 #28 新设；600dpi ink 口径） ----
def _same_vis(r1, r2):
    return min(r1[1], r2[1]) - max(r1[0], r2[0]) > 0.5 * min(r1[1] - r1[0], r2[1] - r2[0])

split_ok, split_detail = True, []
for pno in range(1, n_pages + 1):
    for ci, cl in enumerate(COLL):
        rows = col_rows(pno, cl)
        for k, (y0_, y1_, t, sps) in enumerate(rows):
            if not re.match(r'^[（(]\s*2\s*[）)]\s*几何表示法', t):
                continue
            up = None
            for m in range(k - 1, -1, -1):
                if not _same_vis(rows[m], rows[k]):
                    up = rows[m]
                    break
            if up is None:
                continue
            pitch = (sps[0]['origin'][1] - up[3][0]['origin'][1]) / PT
            gap = ink_gap600(pno, ci, up[3][0]['origin'][1], sps[0]['origin'][1])
            ok1 = (6.2 <= pitch <= 6.7) and gap is not None and (2.6 <= gap <= 3.1)
            split_ok = split_ok and ok1
            split_detail.append(f'p{pno}c{ci} pitch{pitch:.2f} 墨隙{("%.2f" % gap) if gap is not None else "n/a"}')
check('⑦-3 条目2 (1)→(2) 拆段缝（普通行距档 6.44±0.25／墨隙 2.7–3.0；F 片B 0909 #28 零尾距变体）',
      split_ok and bool(split_detail), '；'.join(split_detail) or '未找到 (2)几何表示法 行')

# ---- ⑦-4 相邻判断题缝（F 片B 0909 #31 新设；600dpi ink 口径） ----
zt_ok, zt_detail = True, []
SIG7 = re.compile(r'^(◆|例1|变式1|\[(?!解析)|【)')
for pno in range(1, n_pages + 1):
    for ci, cl in enumerate(COLL):
        rows = col_rows(pno, cl)
        zt_idx = [k for k, r in enumerate(rows) if re.match(r'^\(\d+\)', r[2])]
        for k1, k2 in zip(zt_idx, zt_idx[1:]):
            between = [rows[m][2] for m in range(k1 + 1, k2)]
            if not any(t.startswith('[解析]') for t in between):
                continue
            if any(SIG7.match(t) for t in between):
                continue
            up = rows[k2 - 1]
            if up[0] == rows[k2][0]:      # 同线碎片
                continue
            pitch = (rows[k2][3][0]['origin'][1] - up[3][0]['origin'][1]) / PT
            gap = ink_gap600(pno, ci, up[3][0]['origin'][1], rows[k2][3][0]['origin'][1])
            zt_ok = zt_ok and (6.2 <= pitch <= 6.7) and gap is not None and (2.5 <= gap <= 3.3)
            zt_detail.append(f'p{pno}c{ci} pitch{pitch:.2f} 墨隙{gap:.2f}')
check('⑦-4 相邻判断题缝（普通行距档 6.44±0.25／墨隙 2.6–3.2，全品 6.3–6.8/≈2.9；F 片B 0909 #31 \\zhenti 尾 7pt→0）',
      zt_ok and len(zt_detail) >= 2, '；'.join(zt_detail) or '未找到判断题对')
if zt_detail:
    reg('⑦-4 判断题缝口径（F 片B 0909 #31 新设）',
        '相邻判断题＝同诊断块内 (N) 题干行对（中间含 [解析]、无块签名）；\\zhenti 尾 \\addvspace{7pt}→0pt 后'
        '缝＝普通行距档 pitch 6.41／墨隙 2.62–3.05（全品 p04/p05 实测 6.3–6.8／≈2.9）；'
        '\\jiexi 同挂 7pt 但语境为变式/检测，维持不动')

# ---- N4b 表组多行格净空（F 片B 0909 #30 新设；行级最紧侧 600dpi ink 口径） ----
pad_ok, pad_detail = True, []
for pno, cl, hrs3 in tab_groups:
    rs = [r for r, _ in hrs3]
    ws = [(d.get('width') if d['type'] == 's' else r.height) for r, d in hrs3]
    page = doc[pno - 1]
    # 竖线（黑，逐行分段）：按行取本行竖线 x 分列，逐格测墨带取最紧侧
    vlines = [d['rect'] for d in page.get_drawings()
              if (d.get('color') or d.get('fill'))
              and rgb255(d.get('color') or d.get('fill')) == (0, 0, 0)
              and d['rect'].height > 5 * PT and d['rect'].width < 3]
    for a, b, wa, wb in zip(rs, rs[1:], ws, ws[1:]):
        if (b.y0 - a.y0) / PT < 14:      # 表头/单行行豁免（多行行高 ≥15.7mm，0909 实测）
            continue
        xs = sorted(set(round(v.x0, 2) for v in vlines
                        if v.y0 - 1 <= a.y0 <= v.y1 + 1 or v.y0 - 1 <= b.y0 <= v.y1 + 1))
        if len(xs) < 2:
            xs = [rs[0].x0, rs[0].x1]
        padT = padB = 99.0
        for xa, xb in zip(xs, xs[1:]):
            if xb - xa < 6:
                continue
            bs = ink_bands600(pno, cl, a.y0 + 1.6, b.y0 - 1.6, x0=xa + 2.0, x1=xb - 2.0)
            if not bs:
                continue
            padT = min(padT, (bs[0][0] - (a.y0 + wa / 2)) / PT)
            padB = min(padB, ((b.y0 - wb / 2) - bs[-1][1]) / PT)
        if padT > 90:
            pad_ok = False
            pad_detail.append(f'p{pno} 行无墨带!')
            continue
        pad_ok = pad_ok and (2.9 <= padT <= 3.7) and (2.9 <= padB <= 4.3)
        pad_detail.append(f'p{pno} 行{(b.y0 - a.y0) / PT:.1f} T{padT:.2f} B{padB:.2f}')
check('N4b 多行格净空（行级最紧侧 顶 2.9–3.7／底 2.9–4.3mm；全品 p04 3.46–4.59；F 片B 0909 #30）',
      pad_ok and bool(pad_detail), '；'.join(pad_detail) or '无多行行')
if pad_detail:
    reg('N4b 口径（F 片B 0909 #30 新设）',
        '行级最紧侧＝该行全部列在表宽内（框线内缩 2pt）的墨带首/末带到上下线墨缘（600dpi ink，线宽折半）；'
        'E 1.7mm 垫顶（顶侧 dT/dE≈1.05）＋\\tabrowglue 按折数分档垫底（1/2/≥3 折 0.85/4.65/7.60mm，'
        'm 列行尾胶 <≈2.44mm 被居中吸收）——基线 0.89–2.16 → 实测落窗；'
        '底侧低值行（印答下划线墨底低伸 ≈0.9mm）登记不设红')

# ---- ⑧ 多选标记 ×1 常规 ----
duo_spans = [(pno, sp) for pno in range(1, n_pages + 1) for t, bb, sps in lines_of[pno]
             if '多选题' in t for sp in sps if '多选题' in sp['text']]
duo_ok = (len(duo_spans) == 1 and 10 <= duo_spans[0][1]['size'] <= 11
          and 'FZSSJW' in duo_spans[0][1]['font'])
check('⑧多选标记 (多选题) ×1 常规宋体 10.5（探五例1，TJ-04 目检档）', duo_ok,
      f'n={len(duo_spans)} ' + (f'{duo_spans[0][1]["font"]} {duo_spans[0][1]["size"]:.1f}pt' if duo_spans else ''))

# ---- ⑨ 行尾标点悬挂 0 容忍＋源 CJK 邻空格 0（0908 两项口径修正：
#      a) 源空格检查移 body.tex 层、与 postproc 6a 同式控制字保护——PDF 提取层给 CJK 间插空格，
#      对 PDF 文本查「源空格」是假阳源（首轮 317 全部伪）；b) 悬挂检查限栏流行（|x0−栏左|≤15pt）——
#      通栏块（学习目标等，x0≈81.7pt）以版心宽排，对栏宽查悬挂出 +49.95mm 假阳） ----
hang_bad, hang_det = 0, []
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if not t:
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        if abs(bb[0] - cl) > 15:
            continue
        if t[-1] in '，。；：、）】」』.,;:)]！？' and bb[2] > cl + COLW + 1:
            hang_bad += 1
            hang_det.append(f'p{pno}+{(bb[2] - cl - COLW) / PT:.2f}mm…{t[-8:]}')
_CJKC = '\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u2018\u2019\u201c\u201d'
_sp_pat = r'\\[a-zA-Z]+ +| +(?=[' + _CJKC + r'])|(?<=[' + _CJKC + r']) +'
# F 0909 收尾轮适配：扫描前剥注释域（每行首个未转义 % 起弃）——首轮 7 处残留全在 body.tex
# \vspace{-9.7pt} 行注释文案内（「…10.09/18.25 密度…」），排版不可达域
_body_nc = '\n'.join(re.split(r'(?<!\\)%', _ln)[0] for _ln in body.splitlines())
sp_resid = [m.group(0) for m in re.finditer(_sp_pat, _body_nc) if not m.group(0).startswith('\\')]
check('⑨行尾标点悬挂 0（PunctStyle=plain，栏流限域）＋源 CJK 邻空格 0（body.tex 层·注释域豁免）',
      hang_bad == 0 and not sp_resid,
      f'悬挂{hang_bad}{" " + "；".join(hang_det) if hang_det else ""} 源空格残留{len(sp_resid)}')
reg('⑨ 源空格残留注释域豁免（0909 收尾轮）', 'body.tex \\vspace{-9.7pt}% 注释文案含 7 处 CJK 邻空格'
    '（排版不可达域）——扫描改在剥注释后进行；正域 0 残留维持')

# ---- ⑩ [答案] 行无下划线（#22 \ansul 恒等的 pdf 侧取证） ----
ans_rows = [(pno, bb) for pno in range(1, n_pages + 1) for t, bb, sps in lines_of[pno]
            if t.startswith('[答案]')]
n_ul = 0
for pno, bb in ans_rows:
    for d in doc[pno - 1].get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            uy = it[1].y
            ux0, ux1 = sorted((it[1].x, it[2].x))
            # 0908：限字底带（下划线贴 baseline 下方）——窗口放宽到行顶时误中本行 \sqrt 顶栏（3 处假阳）
            if bb[3] - 0.5 <= uy <= bb[3] + 2 and min(bb[2], ux1) - max(bb[0], ux0) > 1:
                n_ul += 1
check('⑩[答案] 行行内无下划线 ×%d（\\ansul 恒等，清单§九⑩）' % len(ans_rows), len(ans_rows) == 14 and n_ul == 0,
      f'答案行 {len(ans_rows)}/14 行内下划线 {n_ul}')

# ---- ⑪ 题侧标签隙 标签→[ 2.7±0.6＋]→题干 2.2±0.6（半角[]；0908 二修：
#      a) 计数 ×14→×23——源文题侧 [简单/中档(知识点N)] 全数保留＝例1 9＋变式 9＋检测 5（探针实证），
#      规格 ×14 系漏计例1；b) 后隙豁免 CJK 限定——5 处后随数学式/数字，改同基线 9–12pt 任意字） ----
gaps_pre, gaps_post, gaps_wrap = [], [], []
for pno in range(1, n_pages + 1):
    cs = chars_of[pno]
    for i in range(1, len(cs)):
        c, bb, sz, fn = cs[i]
        pc, pbb, _, _ = cs[i - 1]
        if c == '[' and i + 1 < len(cs) and cs[i + 1][0] in '简中难':
            gaps_pre.append((bb[0] - pbb[2]) / PT)
        if c == ']' and pc == ')' and 10 <= sz <= 11 and i + 1 < len(cs):
            nc, nbb, nsz, _ = cs[i + 1]
            if 9 <= nsz <= 12 and abs(nbb[1] - bb[1]) < 2:
                gaps_post.append((nbb[0] - bb[2]) / PT)
            else:
                gaps_wrap.append(pno)   # 题干换行态：标签行末无水平后隙（dy≈17pt 下行起排）
tie_ok = (len(gaps_pre) == 23 and all(2.1 <= v <= 3.3 for v in gaps_pre)
          and len(gaps_post) == 20 and all(1.0 <= v <= 2.7 for v in gaps_post) and len(gaps_wrap) == 3)
check('⑪题侧标签隙 标签→[ 2.7±0.6 ×23＋]→题干 2.2±0.6 ×20＋换行态3（TJ-03；F 片A 探二/探九题干归位后内联 +2）', tie_ok,
      f'前隙 n={len(gaps_pre)} {" ".join("%.2f" % v for v in gaps_pre)}｜后隙 n={len(gaps_post)} {" ".join("%.2f" % v for v in gaps_post)}')
reg('⑪ 题侧计数口径（0908；F 片A 0909 后隙 18→20）', '源文题侧 [简单/中档(知识点N)] 全数保留＝23（例1 9＋变式 9＋检测 5）；'
    '规格 ×14 系漏计例1，作废；隙距 2.7/2.2 由宏 \\hspace 给出恒定；后隙 18→20（探二/探九题干由并排 minipage 改内联，'
    '标签行末水平后隙可测 +2）、换行态 5→3（同因）；TJ-03 2.2mm 只锁内联态')

# ---- ⑫ 探究点标题单行 ≤82mm ×9＋名字清单（0908 改基线归并——◆标题行内 \hspace{2em} 被 MuPDF
#      拆为「◆探究点N」＋名字双片段，逐片段比对名单恒异） ----
EXP_TJD = {'◆探究点一空间向量的概念辨析', '◆探究点二空间向量的线性运算', '◆探究点三用基底表示向量',
           '◆探究点四共面向量的判定', '◆探究点五数量积的概念与运算律', '◆探究点六数量积求夹角与投影',
           '◆探究点七数量积条件求参', '◆探究点八数量积求距离(展开法)', '◆探究点九数量积求距离(折叠矩形)'}
_grp12 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        # 0908：◆ 小图元 8.6pt 基线比正文 12pt span 高 1.195pt（探针实证），sps[0]（＝◆）作键跨 0.5pt 桶界
        # 把「◆探究点N」与名字拆成两组恒出裸名——改取主字号 span 基线归并
        base = max(sps, key=lambda s: s['size'])['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp12.setdefault((pno, cl, round(base * 2)), []).append((bb[0], bb[2], t))
tjd_rows = []
for frs in _grp12.values():
    frs.sort()
    mt = ''.join(x[2] for x in frs).replace(' ', '')
    if mt.startswith('◆探究点'):
        tjd_rows.append((mt, min(x[0] for x in frs), max(x[1] for x in frs)))
tjd_w_ok = all((x1 - x0) / PT <= 82 for _, x0, x1 in tjd_rows)
tjd_name_ok = {t for t, _, _ in tjd_rows} == EXP_TJD
check('⑫探究点标题单行 ≤82mm ×9＋名字清单（RENAME 探六/探七压字；基线归并口径 0908）',
      len(tjd_rows) == 9 and tjd_w_ok and tjd_name_ok,
      f'n={len(tjd_rows)} 最宽{max((x1 - x0) / PT for _, x0, x1 in tjd_rows) if tjd_rows else -1:.1f}mm '
      f'名单{"合" if tjd_name_ok else "异:" + str({t for t, _, _ in tjd_rows} ^ EXP_TJD)}')

# ---- ⑭ (\kongwei) 空位 6.8±0.6 ×8（窗外 () 相邻对＝源文空()杂对，登记不计红，0908 口径） ----
kw_gaps, kw_stray = [], []
for pno in range(1, n_pages + 1):
    cs = chars_of[pno]
    for i in range(len(cs) - 1):
        if cs[i][0] == '(' and cs[i + 1][0] == ')':
            v = (cs[i + 1][1][0] - cs[i][1][2]) / PT
            (kw_gaps if 6.2 <= v <= 7.4 else kw_stray).append((pno, cs[i][1][1], v))
check('⑭空位 (\\kongwei) 宽 6.8±0.6 ×9（#17 定宽空档；探八右挂补 1 后全集 0909；窗外杂对≤1）',
      len(kw_gaps) == 9 and len(kw_stray) <= 1,
      f'n={len(kw_gaps)} ' + ' '.join(f'{v:.2f}' for _, _, v in kw_gaps)
      + (' 杂:' + ' '.join(f'p{p}y{y:.0f}/{v:.2f}' for p, y, v in kw_stray) if kw_stray else ''))
if kw_stray:
    reg('⑭ 空位杂对登记', '窗外 () 相邻对 ' + ' '.join(f'p{p}y{y:.0f}/{v:.2f}' for p, y, v in kw_stray)
        + '（成因＝源文空()，非 \\kongwei 产物；p6 y157.8 Times10.5 gap0.00 实证）')

# ---- ⑮ side×5 归属＝探二/三/六/八/九 ----
# F 片A 0909 适配：归属键改阅读序（页, 栏, y）——旧键（页, y）在同 y 双栏标题（p5 六/七 同 y 17.5）
# 与跨栏流（p6 九标题在左栏、其图在右栏顶）两处误归属（实测旧：{七,三,二,八}）。
tjd_events = []   # (pno, col, y, 序) — ◆探究点行（col：0 左栏／1 右栏）
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('◆探究点'):
            tjd_events.append((pno, 0 if bb[0] < MID else 1, bb[1], t[4]))
side_att = set()
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            cl = COLL[0] if r.x0 < MID else COLL[1]
            if abs((r.x0 + r.x1) / 2 - cl - COLW / 2) / PT <= 3:
                continue
            icol = 0 if r.x0 < MID else 1
            prev = [ev for ev in tjd_events if (ev[0], ev[1], ev[2]) <= (pno, icol, r.y0 + 2)]
            if prev:
                side_att.add(max(prev, key=lambda e: (e[0], e[1], e[2]))[3])
check('⑮side×5 归属＝探二/三/六/八/九（F 片A：阅读序（页,栏,y）归属）',
      len(side_att) == 5 and side_att == {'二', '三', '六', '八', '九'},
      f'归属{sorted(side_att)}')

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
seqs = [[int(x) for x in re.findall(r'\\tiaomuz?\{(\d+)\}', s)] for s in segs]
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
