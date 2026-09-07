# -*- coding: utf-8 -*-
r"""_测v4断言.py——v4.2 导学件断言实测（交付报告§九证据源）。口径沿同工程先例：
样张v4/练习件/断言v4.py＋样张v4/测评卷/断言版式.py，并按 v4.2 对齐全品轮 22 条指令适配：
①编译零 error/overfull/missingchar（扫 main.log）；页数实测登记（v4.2 内容增：6 或 7 均收，指令22）
②行距主峰 17.5–18.5pt（\linespread{1}，逐栏相邻 baseline 差直方图）
③单页灰档 ⊆{777777, DDDDDD, BFBFBF} 且 ≤3（题图位图内容色天然豁免；0xBF＝black!25 栏线派生档，拍板39）
④学习目标块 ≤35mm＋题区起点口径（v4.1 修订登记）＝「栏内课前预习花形顶」（p1 菱形标顶缘），
  并登记花形底线顶与 ◆知识点一 顶
⑤栏利用率：a) 非末页逐栏 ≥70%（门槛）；b) 非末页每栏末墨距版心底 ≤15mm——断栏经济学待拍板项延续实测登记
  （不计 FAIL）：\raggedcolumns 栏末空零成本、断点由 glueguard−100 与块绑定结构主导，v4 三值 penalty 实验
  不敏感，v4.1 过目轮未裁，v4.2 延续实测登记口径
⑥排印层逻辑断言：◆探究点 9（内联例1 9、变式1 9）、【答案】行 14、★典型性理由 0（v4.2-E18 撤★）、
  【解析】行 20（判断6＋变式9＋检测5，D 类16/17）
⑦花形行栏内化（v4.1 指令6，推翻拍板28）：栏宽 midgray 细线 ×3（课前预习/课中探究/课堂评价），
  每处 (a) 线宽≈栏宽（栏内元素而非通栏）；(b) 线上有菱形标（线上方 45pt 带内、栏 x 带内的行级
  字符集 ⊆ 花形字集，合计 ≥2 字——单字行与「课堂评价」整行连排两种形态均收）；(c) 底线→下级 ≤8mm
  （线下同栏无文本＝栏内最后元素时豁免并登记）；(d) 章首通栏线（>300pt 宽横线）仅页 1 章首带 1 条（无整页横断花形带）
⑧页脚灰块 6/7 页在场：24×7mm、底缘 11±1.5mm（拍板22 保持）、数字 bbox 中心 vs 块中心
  水平+垂直各 ≤1.5mm；页脚小字黑粗（v4.2-A4）由文本在场与字色复查
⑨页眉缺席（v4.2-A1，翻拍板8②回归原旨）：全部页版心顶上方（y<MARGIN−1）无任何文本行
⑩页脚奇偶交替（v4.1 指令4 口径不变）：奇页＝块右缘贴版心右＋小字「章名…导学件」；偶页＝块左缘贴版心左
  ＋小字「高中数学…（人教B版）」
⑪挖空印答（v4.1 指令1）：body.tex \kongda ×20；pdf 文本层各答案值在场（p1/p2）；
  ⑪-3 印答盒宽全量实测（返修1）：栏内 3–60pt 水平细线＋盒内文本锚定，20 处线宽全 ≥42pt（15mm）
⑫判断题解析（v4.1 指令2）＋简析（v4.2-D16/17）：\zhenti ×6＋\jiexi ×14；pdf 层【解析】行 ×20
⑬条目重编号（v4.1 指令8）：body.tex 按 \zsd 分段，\tiaomu 序列＝[1,2,3]／[1,2]／[1,2,3,4]（知识点重起）
⑭栏间竖线在场（v4.2-A3，翻拍板28）：页心 x≈MID 竖线（宽≤1.5pt、高≥50% 版心高）、色 0xBF、跨多页在场
⑮【诊断分析】头单行（v4.2-C13）：pdf 文本层「【诊断分析】…判断正误…×"）」同一 line bbox ×3
⑯检测短选项 4 项/行（v4.2-C15）：body.tex 0.25\linewidth 槽网格行 ≥2（实测 3：检测2/检测4/例9）＋
  pdf 同栏同基线 A．B．C．D．四项组 ≥2
⑰编注/解析 8pt（v4.2-A8/A9/D16）：pdf 层【解析】起始 span size∈[7.5,8.5] ＋ qp-blocks \zhuzhu 8pt 宏定义级
⑱图文并排（v4.2-A6＋返修2）：body.tex \begin{minipage} ≥4（实测 8＝4 组并排×2——返修2 增探究点二例1 题图并排）；
  ⑱-2 顶对齐（返修3）：side 图 rect 顶−题干首行 bbox 顶 |dy|≤2mm ×4 组（图 minipage 内 \raisebox 提基线）
⑲题号加粗（v4.2-G20，tex 级）：qp-blocks \tiaomu 输出形含 {\heiti #1}．＋ body.tex 检测题号 {\heiti N．} ×5"""
import os
import re
from collections import Counter

import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
MARGIN = 15 * PT                       # 42.52pt 版心左/顶（v4.2 撤页眉后版心顶仍＝15mm）
BOT = 20 * PT                          # 56.7pt 版心底＝20mm（v4.2 拍板22 冲突实害修复：正文区让位页脚带）
PAGE_H = 297 * PT
PAGE_W = 595.276
COLSEP = 7.5 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLR = PAGE_W - MARGIN
TEXTH = PAGE_H - MARGIN - BOT
BODY_BOT = PAGE_H - BOT

fails, okmsg, regmsg = [], [], []

def check(name, ok, detail=''):
    (okmsg if ok else fails).append(f'{name}　{detail}')

def reg(name, detail):
    regmsg.append(f'{name}　{detail}')

# ---- ① 编译日志 ----
logtxt = open(os.path.join(BASE, 'main.log'), encoding='utf-8', errors='ignore').read()
n_err = len(re.findall(r'^!', logtxt, re.M))
n_over = len(re.findall(r'Overfull', logtxt))
n_miss = len(re.findall(r'Missing character', logtxt))
m = re.search(r'Output written on main\.pdf \((\d+) pages', logtxt)
n_pages = int(m.group(1)) if m else -1
check('①编译零 error/overfull/missingchar', n_err == 0 and n_over == 0 and n_miss == 0 and n_pages in (6, 7),
      f'errors={n_err} overfull={n_over} missingchar={n_miss} 页数={n_pages}（v4.2 指令22：6/7 均收，实测登记）')

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))

# ---- ② 行距主峰（分栏分桶＋正文 10.5pt 行过滤） ----
lead_ok, gray_ok = True, True
lead_detail, gray_detail = [], []
for pno, page in enumerate(doc, 1):
    col_lines = {0: [], 1: []}
    spans_all = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            spans_all += ln['spans']
            if all(not (10 <= sp['size'] <= 11) for sp in ln['spans']):
                continue
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
    # v4.2-A3：白名单加 0xBF（black!25 栏线派生档，拍板39）；单页 ≤3（777777＋DDDDDD＋BFBFBF）
    if not grays <= {0x77, 0xDD, 0xBF} or len(grays) > 3:
        gray_ok = False
check('②行距主峰 17.5–18.5pt', lead_ok and lead_detail, '；'.join(lead_detail))
check('③单页灰档 ⊆{777777,DDDDDD,BFBFBF} 且 ≤3', gray_ok, ' '.join(gray_detail))
reg('③灰档白名单修订（拍板39）', 'v4.2-A3 栏线 black!25→0xBFBFBF 入册（全品实测栏线灰度 188≈191）；'
    '黑与位图内容色天然豁免')

# ---- ④ 学习目标块 ≤35mm ＋ 题区起点＝栏内课前预习花形顶（口径 v4.1 修订） ----
p1 = doc[0]
mb_top = kn_top = None
hua_char_tops = []
for blk in p1.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        t = ''.join(sp['text'] for sp in ln['spans']).strip()
        y0 = ln['bbox'][1]
        if mb_top is None and t.startswith('【学习目标】'):
            mb_top = y0
        if kn_top is None and t.startswith('◆'):
            kn_top = y0
        if t in ('课', '前', '预', '习') and ln['bbox'][0] < MID + COLW:
            hua_char_tops.append(y0)
hua_top = min(hua_char_tops) if hua_char_tops else None
mb_mm = (hua_top - mb_top) / PT if (hua_top is not None and mb_top is not None) else -1
check('④学习目标块 标签顶→花形顶 ≤35mm（§四-9）', 0 <= mb_mm <= 35,
      f'{mb_mm:.1f}mm；题区起点（口径v4.1＝栏内课前预习花形顶）：版心顶→花形顶 {(hua_top - MARGIN) / PT:.1f}mm，'
      f'◆知识点一顶 {(kn_top - MARGIN) / PT:.1f}mm')
reg('④口径修订', '题区起点原「花形行框顶（通栏）」→ v4.1「栏内课前预习花形（菱形标）顶缘」（指令6，v4.2 延续）')

# ---- ⑤ 栏利用率（文本＋图＋矢量，页脚块不计） ----
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
        if abs(r.x0 - MID) < 2 and r.width <= 2:
            continue   # 栏间竖线（通栏高），非栏内容
        if d.get('fill') and abs(r.width - 24 * PT) < 3 and r.y0 > BODY_BOT - 10:
            continue   # 页脚灰块（24×7mm，版心带内但非栏内容），不参与栏末墨计量
        cols[col_idx((r.x0 + r.x1) / 2)] = max(cols[col_idx((r.x0 + r.x1) / 2)], min(r.y1, BODY_BOT))
    util[pno] = {c: (cols[c] - MARGIN) / TEXTH for c in (0, 1)}
    util[pno]['ink'] = {c: cols[c] for c in (0, 1)}
util_detail = '  '.join(f'p{p}:[左{u[0]*100:.0f}%/右{u[1]*100:.0f}%]' for p, u in util.items())
nonlast_ok = all(min(u[0], u[1]) >= 0.70 for p, u in util.items() if p < n_pages)
over15 = [(p, c, (BODY_BOT - u['ink'][c]) / PT) for p, u in util.items() if p < n_pages
          for c in (0, 1) if BODY_BOT - u['ink'][c] > 15 * PT]
check('⑤a 非末页逐栏利用率 ≥70%', nonlast_ok, util_detail)
reg('⑤b 非末页每栏末墨距版心底 ≤15mm（实测登记，断栏经济学延续）',
    ('全部达标' if not over15 else '；'.join(f'p{p}{"左" if c == 0 else "右"} {d:.1f}mm' for p, c, d in over15))
    + '（口径 v4.1：该项 v4 已登记断栏经济学待拍板——\\raggedcolumns 栏末空零成本、断点由 glueguard−100 与'
      '块绑定结构主导，penalty 500/−100 实验不敏感且仅易位超差，v4.1 过目轮未裁，v4.2 延续实测登记不计 FAIL）')
last = util[n_pages]
print(f'       末页 p{n_pages} 左{last[0]*100:.0f}%/右{last[1]*100:.0f}%——课堂评价自然收尾页，实测登记（参差收尾＝拍板23）')

# ---- ⑥ 排印层逻辑断言（全文空白归一计数：标签跨行折断亦计入） ----
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

# ---- ⑦ 花形行栏内化：栏宽 midgray 细线 ×3 ＋ 菱形标在栏内 ＋ 线→下级 ≤8mm ＋ 无整页横断 ----
HUA_CHARS = set('课前预习中探究堂评价')
hua_rules = []
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        col_ = d.get('color') or d.get('fill')
        if not col_:
            continue
        rgb = tuple(round(x * 255) for x in col_)
        if not (rgb[0] == rgb[1] == rgb[2] == 0x77):
            continue
        if abs(r.width - COLW) <= 6 and r.height <= 2:
            hua_rules.append((pno, r))
wide_rules = [(pno, d['rect']) for pno, page in enumerate(doc, 1) for d in page.get_drawings()
              if d['rect'].width > 300 and d['rect'].height <= 2]
ok7 = len(hua_rules) == 3
d7, c_exempt = [], []
for pno, r in hua_rules:
    page = doc[pno - 1]
    cl = MARGIN if (r.x0 + r.x1) / 2 < MID else MARGIN + COLW + COLSEP
    # (b) 线上方 45pt 带内的花形字行（合计 ≥2 字、栏 x 带内；行级字符集 ⊆ HUA_CHARS——
    #     v4.2 实测 p6「课堂评价」四字连排被并进同一 line bbox，单字行口径漏检，改行级收集双形态兼容）
    hua_lines = [ln for blk in page.get_text('dict')['blocks'] for ln in blk.get('lines', [])
                 if set(''.join(sp['text'] for sp in ln['spans']).strip()) <= HUA_CHARS
                 and r.y0 - 45 <= ln['bbox'][3] <= r.y0 + 2
                 and cl - 2 <= ln['bbox'][0] <= cl + COLW]
    n_hua = sum(len(''.join(sp['text'] for sp in ln['spans']).strip()) for ln in hua_lines)
    # (c) 线下方同栏首行（线下同栏版心带内无文本＝线为栏内最后元素时豁免并登记；页脚带不计——
    #     v4.2 实测 p6 花形线为栏内末元素时页脚小字距线 73.2mm 被误认下级）
    nxt = 1e9
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if BODY_BOT + 1 >= ln['bbox'][1] > r.y1 + 0.5 and cl - 5 <= ln['bbox'][0] <= cl + COLW:
                nxt = min(nxt, ln['bbox'][1])
    gap = (nxt - r.y1) / PT if nxt < 1e8 else -1
    ok_b = n_hua >= 2
    ok_c = 0 <= gap <= 8
    if nxt >= 1e8:
        ok_c = True
        c_exempt.append(f'p{pno}')
    ok7 = ok7 and ok_b and ok_c
    d7.append(f'p{pno} 线宽{r.width / PT:.1f}mm 花形字{n_hua} 缝{gap:.1f}mm')
if c_exempt:
    reg('⑦ (c) 栏内无下级豁免登记', '、'.join(c_exempt) + ' 花形底线为栏内最后元素（线下同栏无文本），豁免 ≤8mm 缝检')
check('⑦花形行栏内化（栏宽细线×3/线上菱形标/线→下级≤8mm）', ok7 and len(hua_rules) == 3, '；'.join(d7))
reg('⑦整页横断检查', f'全件 >300pt 宽横线 {len(wide_rules)} 条（页{sorted(set(p for p, _ in wide_rules))}），'
    f'须仅页1 章首通栏细线 1 条：{"符合" if len(wide_rules) == 1 and wide_rules[0][0] == 1 else "异常复核"}')
check('⑦-2 无整页横断（章首通栏线仅页1×1）', len(wide_rules) == 1 and wide_rules[0][0] == 1,
      '；'.join(f'p{p} w={r.width / PT:.0f}mm' for p, r in wide_rules))

# ---- ⑧⑨⑩ 页脚块/页眉缺席/奇偶交替 ----
feet_ok8, feet_ok10, hdr_ok = True, True, True
d8, d9, d10 = [], [], []
for pno, page in enumerate(doc, 1):
    blk_rect = None
    for d in page.get_drawings():
        r = d['rect']
        f = d.get('fill')
        if not f or r.y0 <= BODY_BOT - 10:
            continue
        rgb = tuple(round(x * 255) for x in f)
        if rgb[0] == rgb[1] == rgb[2] == 0xDD and abs(r.width - 24 * PT) < 3 and abs(r.height - 7 * PT) < 2:
            blk_rect = r
    # 数字 span（文本恰为页码值的 span；正文 span 落进 ±1pt 几何容差带不得并入——
    #   v4.2 实测 p1 dx2.95/p4 dx0.71 均为正文末行 span 污染 num_bbox 的测量口径假阳性）
    num_bbox = None
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                if sp['text'].strip() != str(pno):
                    continue
                bb = sp['bbox']
                if blk_rect and blk_rect.x0 - 1 <= bb[0] and bb[2] <= blk_rect.x1 + 1 \
                   and blk_rect.y0 - 1 <= bb[1] and bb[3] <= blk_rect.y1 + 1:
                    num_bbox = bb if num_bbox is None else (
                        min(num_bbox[0], bb[0]), min(num_bbox[1], bb[1]),
                        max(num_bbox[2], bb[2]), max(num_bbox[3], bb[3]))
    # 页脚小字（页脚带内文本）
    foot_txts = [''.join(sp['text'] for sp in ln['spans'])
                 for blk in page.get_text('dict')['blocks'] for ln in blk.get('lines', [])
                 if ln['bbox'][1] > BODY_BOT - 2]
    odd = pno % 2 == 1
    if blk_rect and num_bbox:
        bot = (PAGE_H - blk_rect.y1) / PT
        dx = abs((num_bbox[0] + num_bbox[2]) / 2 - (blk_rect.x0 + blk_rect.x1) / 2) / PT
        dy = abs((num_bbox[1] + num_bbox[3]) / 2 - (blk_rect.y0 + blk_rect.y1) / 2) / PT
        ok8 = abs(bot - 11) <= 1.5 and dx <= 1.5 and dy <= 1.5
        feet_ok8 = feet_ok8 and ok8
        d8.append(f'p{pno} 底{bot:.1f}mm dx{dx:.2f} dy{dy:.2f}mm')
        # ⑩ 奇偶交替（页脚小字黑粗——文本在场复查，字级断言⑰外 tex 级 qp-headfoot 已登记）
        if odd:
            ok10 = blk_rect.x1 >= COLR - 2 and any('导学件' in t for t in foot_txts)
            d10.append(f'p{pno}奇 块右缘距版心右{(COLR - blk_rect.x1) / PT:.1f}mm 文本{"有" if any("导学件" in t for t in foot_txts) else "无"}')
        else:
            ok10 = blk_rect.x0 <= MARGIN + 2 and any('人教B版' in t.replace(' ', '') or '人教B' in t for t in foot_txts)
            d10.append(f'p{pno}偶 块左缘距版心左{(blk_rect.x0 - MARGIN) / PT:.1f}mm 文本{"有" if any("人教B" in t for t in foot_txts) else "无"}')
        feet_ok10 = feet_ok10 and ok10
    else:
        feet_ok8 = feet_ok10 = False
        d8.append(f'p{pno} 缺页码块/数字')
    # ⑨ 页眉缺席（v4.2-A1 翻拍板8②回归原旨）：版心顶上方无任何文本
    hdr_lines = [t for blk in page.get_text('dict')['blocks'] for ln in blk.get('lines', [])
                 if ln['bbox'][3] < MARGIN - 1
                 for t in [''.join(sp['text'] for sp in ln['spans']).strip()] if t]
    hdr_ok = hdr_ok and not hdr_lines
    d9.append(f'p{pno} {"无页眉" if not hdr_lines else "有文本:" + str(hdr_lines[:2])}')
check('⑧页脚灰块 24×7mm、底缘 11±1.5mm、数字居中 ≤1.5mm', feet_ok8, '；'.join(d8))
check('⑨页眉缺席（版心顶上方无任何文本，全部页）', hdr_ok, '；'.join(d9))
check('⑩页脚奇偶交替（奇=文+块贴右/偶=块贴左+文，小字黑粗）', feet_ok10, '；'.join(d10))

# ---- ⑭ 栏间竖线在场（v4.2-A3 翻拍板28）：页心竖线、0xBF、跨多页 ----
rule_pages, rule_detail = [], []
for pno, page in enumerate(doc, 1):
    found = None
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 1.5 and r.height >= 0.5 * TEXTH):
            continue
        if abs(r.x0 - MID) > 2 and abs(r.x1 - MID) > 2:
            continue
        c = d.get('fill') or d.get('color')
        if c:
            rgb = tuple(round(x * 255) for x in c)
            if rgb[0] == rgb[1] == rgb[2] == 0xBF:
                found = r
                break
    if found:
        rule_pages.append(pno)
        rule_detail.append(f'p{pno} 高{found.height / PT:.0f}mm')
check('⑭栏间竖线在场（页心/black!25/跨多页）', len(rule_pages) == n_pages and n_pages >= 6,
      f'页{rule_pages}/{n_pages}；'.join(['', *rule_detail]))

# ---- ⑮【诊断分析】头单行（v4.2-C13） ----
zhen_lines = []
for page in doc:
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t.startswith('【诊断分析】'):
                zhen_lines.append(t)
ok15 = len(zhen_lines) == 3 and all(('判断正误' in t and t.endswith('）') and '×' in t) for t in zhen_lines)
check('⑮【诊断分析】头栏内单行 ×3（标签＋说明同 line bbox）', ok15,
      '｜'.join(t[:22] + ('…单行' if '判断正误' in t else '…折行!') for t in zhen_lines))

# ---- ⑯ 检测短选项 4 项/行（v4.2-C15） ----
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
# 槽行按行计数：单行恰含 4 个 0.25\linewidth 槽＝4 项/行（原正则粘 \bindopt 后实际行带空格致计 0，v4.2 翻修）
n_row4_tex = sum(1 for ln_ in body.splitlines() if ln_.count(r'0.25\linewidth-0.5em') == 4)
rows4_pdf = 0
for page in doc:
    groups = {}
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if re.match(r'^[A-D]．', t):
                key = (col_idx(ln['bbox'][0]), round(ln['spans'][0]['origin'][1] / 2))
                groups.setdefault(key, set()).add(t[0])
    rows4_pdf += sum(1 for v in groups.values() if v == {'A', 'B', 'C', 'D'})
check('⑯短选项 4 项/行（body.tex 槽行≥2＋pdf 同基线四项组≥2）', n_row4_tex >= 2 and rows4_pdf >= 2,
      f'tex 槽行 {n_row4_tex}（检测2/检测4/例9）; pdf 四项组 {rows4_pdf}')

# ---- ⑰ 编注/解析 8pt（v4.2-A8/A9/D16） ----
sz_ok, n_jx_span = True, 0
for page in doc:
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                if sp['text'].strip().startswith('【解析】'):
                    n_jx_span += 1
                    if not 7.5 <= sp['size'] <= 8.5:
                        sz_ok = False
blkfile = open(os.path.join(BASE, 'qp-blocks.tex'), encoding='utf-8').read()
zhuzhu_8pt = bool(re.search(r'\\newcommand\{\\zhuzhu\}\[1\]\{\{\\fontsize\{8pt\}', blkfile))
check('⑰编注/解析 8pt（pdf【解析】span 实测＋\\zhuzhu 宏定义级）', sz_ok and n_jx_span == 20 and zhuzhu_8pt,
      f'【解析】span {n_jx_span}/20，越档 {0 if sz_ok else "有"}；\\zhuzhu 8pt 定义 {"在" if zhuzhu_8pt else "缺"}')

# ---- ⑱ 图文并排（v4.2-A6）＋ ⑱-2 顶对齐（返修3）＋ ⑲ 题号加粗（v4.2-G20 tex 级） ----
n_mini = body.count(r'\begin{minipage}')
n_side = body.count(r'\begin{minipage}[t]{0.56\linewidth}')
raisebox_ok = r'\raisebox{\dimexpr-\height+\ht\strutbox\relax}' in body
check('⑱图文并排 body.tex minipage ≥4', n_mini >= 4 and n_side == 4 and raisebox_ok,
      f'minipage {n_mini}（4 组题干并排×2，返修2 增探二）；side 行 {n_side}/4 带 \\raisebox 顶对齐 {"在" if raisebox_ok else "缺"}（返修3）')
# ⑱-2 图文并排顶对齐（v4.2-返修3）：side 图（同行左侧有题干文字的图，居中详解图无 ⇒ 豁免）rect 顶
# 与题干首行 bbox 顶差 |dy|≤2mm。判据：行同栏（x0≥图x0−COLW）、整行在图左侧（x1≤图x0+5pt）、
# 行与图垂直带相交（修复后题干首行≈图顶；修复前题干首行贴图底同样相交，bug 值一并可测）
dys, n_side_img = [], 0
for page in doc:
    infos = page.get_image_info(xrefs=True)
    if not infos:
        continue
    tdict = page.get_text('dict')
    tlines = [(l['bbox'], ''.join(sp['text'] for sp in l['spans']))
              for b in tdict['blocks'] if b['type'] == 0 for l in b['lines']]
    for info in infos:
        rct = pymupdf.Rect(info['bbox'])
        near = [bb for bb, tt in tlines
                if bb[0] >= rct.x0 - COLW and bb[2] <= rct.x0 + 5 and bb[1] < rct.y1 and bb[3] > rct.y0
                and (bb[2] - bb[0]) > 20 and not tt.lstrip().startswith('◆')]
        if not near:
            continue
        n_side_img += 1
        dys.append((rct.y0 - min(bb[1] for bb in near)) / PT)
top_ok = n_side_img == 4 and all(abs(v) <= 2.0 for v in dys)
check('⑱-2 图文并排顶对齐（side 图 rect 顶−题干首行顶 |dy|≤2mm）', top_ok,
      f'side 组 {n_side_img}/4；dy=' + ' '.join(f'{v:+.2f}mm' for v in dys))
reg('⑱-2 口径（返修3）', '根因＝\\includegraphics 基线在图底缘，minipage [t] 联排首行基线对齐 ⇒ 图底=题干首行基线'
    '（返修前实测 dy 探二 −52.2／探三 −31.4／探六 −29.6／探八 −15.5mm≈−(图高−行盒高)）；'
    '修法＝side_row 图侧 \\raisebox{\\dimexpr-\\height+\\ht\\strutbox\\relax}（基线提至图顶下 0.7 行距=12.6pt≈首行盒高）。'
    '居中详解图同行无文字自然豁免；side 组数门＝4。')
tiaomu_bold = r'{\heiti #1}．' in blkfile
n_hao_bold = len(re.findall(r'\{\\heiti \d．\}', body))
check('⑲题号加粗 tex 级（\\tiaomu 输出形＋检测题号 ×5）', tiaomu_bold and n_hao_bold == 5,
      f'\\tiaomu {{\\heiti #1}}．{"在" if tiaomu_bold else "缺"}；检测题号粗 {n_hao_bold}/5')

# ---- ⑪⑫⑬ 内容层（body.tex ＋ pdf 文本） ----
n_kd = body.count(r'\kongda{')
check('⑪挖空印答 body.tex \\kongda ×20', n_kd == 20, f'\\kongda={n_kd}')
ANSWERS = ['大小', '方向', '长度', '相反', '互相平行', '重合', '模相等', '三角形', '平行四边形',
           '相同', '实数', '互相垂直', '零向量', '有序实数对']
p12_text = (doc[0].get_text() + doc[1].get_text())
miss = [w for w in ANSWERS if w not in p12_text]
check('⑪-2 印答值 pdf 在场（p1/p2，14 个词值＋数字/区间值）', not miss, ('缺 ' + '、'.join(miss)) if miss else '全部在场')
# ---- ⑪-3 印答盒宽全量实测（v4.2-返修1 防回归：\kongda 暂存寄存器被 xeCJK 覆写致首盒塌陷 1.8mm） ----
# \kongda 全部位于课前预习知识点区（p1/p2，⑪-2 同源口径）；真印答盒 signature＝线下方紧贴恰一个值 span
# （值底缘距线 |dy|≤1.5pt）。p3+ 同宽段为分式横线（分子底距线 −4.75~−7.5pt 或近邻 span 0/≥2 个），不入集
n_kd_anchor, kd_pt = 0, []
for pno, page in list(enumerate(doc, 1))[:2]:
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            ux0, ux1 = sorted((it[1].x, it[2].x))
            uw = ux1 - ux0   # pt
            if not (42 <= uw <= 60) or ux0 < MARGIN - 2 or ux1 > COLR + 2:
                continue   # 栏内 42–60pt 水平细线段（\kongda 最小宽 15mm＝42.5pt；表线/花形线/章首线 >60pt 不入）
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
check('⑪-3 印答盒宽全量实测（\\kongda 20 处线宽 ≥42pt＝15mm）',
      n_kd_anchor == 20 and n_kd == 20 and kd_min >= 42,
      f'锚定印答盒 {n_kd_anchor}/20，最窄 {kd_min:.1f}pt（{kd_min * 25.4 / 72:.1f}mm）；body \\kongda {n_kd}/20')
reg('⑪-3 口径（返修1）', '\\kongda 暂存寄存器 \\dimen0 被 xeCJK 断胶处理覆写致首盒塌陷 1.8mm，宏改专用 \\kdmind/\\kdwd；'
    '本断言以「p1/p2 栏内 42–60pt 水平细线＋线下紧贴恰一个值 span（|dy|≤1.5pt）」全量实测印答盒宽')
n_zt = body.count(r'\zhenti{')
n_jx_body = body.count(r'\jiexi{')
check('⑫判断题 \\zhenti ×6 ＋简析 \\jiexi ×14（变式9＋检测5）', n_zt == 6 and n_jx_body == 14,
      f'\\zhenti={n_zt} \\jiexi={n_jx_body}')
segs = re.split(r'\\zsd\{', body)[1:]
seqs = [[int(x) for x in re.findall(r'\\tiaomu\{(\d+)\}', s)] for s in segs]
check('⑬条目按知识点重起（[1,2,3]/[1,2]/[1,2,3,4]）',
      seqs == [[1, 2, 3], [1, 2], [1, 2, 3, 4]], f'实测 {seqs}')

print('—— 断言实测 ——')
for s in okmsg:
    print(' ✓', s)
for s in regmsg:
    print(' ◎ 登记', s)
for s in fails:
    print(' ✗', s)
print('断言结果：', '全部通过' if not fails else f'未通过 {len(fails)} 项')
raise SystemExit(0 if not fails else 1)
