# -*- coding: utf-8 -*-
r"""顶格断言（v4.1 指令5 口径，替代断言题号列.py；v4.2 随结构变化复查适配）：
v4.1 撤全部悬挂缩进（\parindent=0pt、hangindent 全撤、题号列恒空制废除），正文一切行、表、图从栏左起。
v4.2 结构变化三点复查：①题干图 minipage 并排行（左 0.56\linewidth 题干／右 0.40\linewidth 图）——
题干行非签名行不进 (c)，图仍在栏带内进 (e)；②选项网格 4 槽行（0.25\linewidth）与 2 槽行同机制，
B．/C．/D．以「同视觉行左侧存在更靠前文本」排除；③【解析】简析行（\jiexi）与②③小结拆行均为顶格
签名行，进 (c) 正常判。检查面：
  (a) body.tex 结构 grep：无 \hangindent / \hspace*{7mm} / \hspace*{2em}（顶格化残留扫描；\kern0.15em
      为 \kongda 印答盒间距 kern，非行首缩进语义，不在禁区）；
  (b) qp-blocks.tex 无 \hspace*{2em}（选项/①链 2em 前缀已撤；\hspace{-2mm} 花形连排、\hspace{0.5em}
      \zhuzhu 前距为非 * 版本且非行首缩进语义，不在禁区；v4.2-C13 \zhenhead 标签后距已撤）；
  (c) pdf 签名行顶格：以〔N．／【答案】／【解析】／【诊断分析】／【素养小结】／【学习目标】／
      A．~D．／①~⑨／◆／（N）〕起行的行首墨迹 ∈ 栏左±3.5pt。坑规（沿 v2/旧脚本登记）：行首
      全角标点【（ 经 xeCJK 半宽压缩，line bbox x0=origin 比墨迹左偏 ~5.2pt——凡 bbox x0<栏左
      的签名行一律 300dpi 墨迹左缘复核。行中元素（选项网格槽位项 B．/C．/D．被 pymupdf 按
      定位跳转拆成独立 line）以「同视觉行左侧存在更靠前文本」排除。
  (d) 竖直表线（宽≤2pt 高≥4pt）全部落在某栏带内（x0≥栏左−1 且 x1≤栏右+1），且每张表的
      左框线在场（页上存在 x0==栏左±1 的表线）＝表盒子顶格；表内部竖线（列分隔/右框）位置
      随内容驱动列宽（表1 16/33/30、表2 10/37/32、表3 起调 10/36/33，v4.2-C14）任意，不判 x0==栏左。
      豁免 multicol 栏线（x0≈栏中缝，v4.2-A3 恢复）、花形行 tcbox 左竖边（高 8~30pt 且距栏左 ≤3pt）。
  (e) 图 6 张全部在栏带内（x0≥栏左−1 且 x1≤栏右+1；并排图位于右 minipage 槽位，仍在栏带内）。
登记豁免：p1 学习目标块（multicols 外通栏区）\mubiaomu 楷体条目 hangindent=1.6em 悬挂保留
（章首块不属正文顶格口径，登记）——条目行不以签名起，不进 (c)；花形右侧灰小字不以签名起；
页眉已撤（v4.2-A1）；页脚块 fill 宽 >2pt 不进 (d)；页码数字不匹配签名。
预期（v4.2 复核）：图 6（3 并排＋2 居中 40mm＋1 三联 45mm）、【答案】行 14。表线总数随分页漂移，不硬编码。"""
import os
import re
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
MARGIN = 15 * PT                              # 42.52pt 版心左＝左栏左
BOT = 20 * PT                                 # 56.7pt 版心底＝20mm（v4.2 拍板22 正文区让位页脚带）
COLSEP = 7.5 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2    # 244.49pt
MID = MARGIN + COLW + COLSEP / 2              # 297.64pt 栏中缝
COLL = (MARGIN, MARGIN + COLW + COLSEP)       # 左/右栏左 42.52 / 308.27
TOL = 3.5                                     # 行首墨迹容差 pt

fail = []

# ---- (a)(b) 结构 grep ----
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
blk = open(os.path.join(BASE, 'qp-blocks.tex'), encoding='utf-8').read()
bad_body = re.findall(r'\\hangindent|\\hspace\*\{7mm\}|\\hspace\*\{2em\}', body)
bad_blk = re.findall(r'\\hspace\*\{2em\}', blk)
print(f'(a) body.tex 顶格残留 {bad_body or "无"}　(b) qp-blocks.tex 2em 前缀 {bad_blk or "无"}')
if bad_body or bad_blk:
    fail.append('(a/b)结构残留')

# ---- (c)(d)(e) pdf ----
SIG = re.compile(
    r'^(\d+．|【答案】|【解析】|【诊断分析】|【素养小结】|【学习目标】|[A-D]．|[①②③④⑤⑥⑦⑧⑨]|◆|（\d+)')

def ink_left(page, y0, y1, cl, dpi=300):
    """竖带 [cl−3, cl+7] × [y0−0.5, y1+0.5] 内最左墨迹像素 x（pt），无墨返回 1e9。"""
    clip = pymupdf.Rect(cl - 3, y0 - 0.5, cl + 7, y1 + 0.5)
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    for x in range(w):
        for y in range(h):
            off = (y * w + x) * n
            if (s[off] + s[off + 1] + s[off + 2]) / 3 < 128:
                return clip.x0 + x / (dpi / 72.0)
    return 1e9

doc = pymupdf.open(BASE + r'\main.pdf')
n_sig = n_viol_c = n_ans = n_rules = n_leftedge = n_viol_d = n_fig = n_viol_e = n_exempt = 0
for pno, page in enumerate(doc, 1):
    H = page.rect.height
    def coll(x0):
        return MARGIN if x0 < MID else MARGIN + COLW + COLSEP

    lines = []
    for blk_ in page.get_text('dict')['blocks']:
        for ln in blk_.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                lines.append((t, pymupdf.Rect(ln['bbox']), ln['spans'][0]['origin'][1]))

    # (c) 签名行行首墨迹（版心 y 带内）
    for t, r, base in lines:
        if not SIG.match(t):
            continue
        if base < MARGIN - 1 or base > H - BOT + 1:      # 页眉/页脚带豁免（v4.2 版心底＝BOT）——
            continue                                      # 返修3 轮改基线判定：栏首数学行（探四变式1【答案】）行内
                                                          # \overrightarrow 箭头字形 bbox 撑高 y0 至版心顶上方，
                                                          # bbox 判定误豁免致【答案】14→13（基线仍在版心内，非版面缺陷）
        cl0 = coll(r.x0)
        if any(o is not r and abs(o[2] - base) < 2.0          # 基线差 <2pt＝同视觉行
               and o[1].x0 >= cl0 - 1.0                        # 同栏起点（排跨栏同 y 行）
               and o[1].x1 <= r.x0 + 1.0 for o in lines):     # 左侧有文本＝行中元素
            continue
        n_sig += 1
        if t.startswith('【答案】'):
            n_ans += 1
        cl = cl0
        ref = r.x0 if cl - 0.5 <= r.x0 else None
        ink = ink_left(page, r.y0, r.y1, cl) if ref is None else cl
        if not (cl - TOL <= ink <= cl + TOL):
            n_viol_c += 1
            print(f'   (c)违规签名行 x0={r.x0:.2f} 墨迹={ink:.2f} 栏左={cl:.2f} p{pno} y={r.y0:.1f} {t[:14]}')

    # (d) 竖直表线
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 2.0 and r.height >= 4.0):
            continue
        if abs(r.x0 - MID) < 1.0:
            continue   # multicol 栏线
        if 8.0 <= r.height <= 30.0 and any(0.5 <= r.x0 - c <= 3.0 for c in COLL):
            n_exempt += 1   # 花形行 tcbox 左竖边
            continue
        n_rules += 1
        cl = coll(r.x0)
        if r.x0 < cl - 1.0 or r.x1 > cl + COLW + 1.0:
            n_viol_d += 1
            print(f'   (d)表线出栏带 x0={r.x0:.2f} x1={r.x1:.2f} 栏带=[{cl:.2f},{cl + COLW:.2f}] p{pno} y={r.y0:.1f}~{r.y1:.1f}')
        if any(abs(r.x0 - c) <= 1.0 for c in COLL):
            n_leftedge += 1   # 表左框线在场（== 栏左）

    # (e) 图
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            n_fig += 1
            cl = coll(r.x0)
            if not (r.x0 >= cl - 1.0 and r.x1 <= cl + COLW + 1.0):
                n_viol_e += 1
                print(f'   (e)违规图 x0={r.x0:.2f} x1={r.x1:.2f} 栏带=[{cl:.2f},{cl + COLW:.2f}] p{pno} y={r.y0:.1f}')

print(f'—— 签名行 {n_sig}（其中【答案】{n_ans}；违规 {n_viol_c}）｜表线 {n_rules}（左框线 {n_leftedge}；'
      f'违规 {n_viol_d}，花形豁免 {n_exempt}）｜图 {n_fig}（违规 {n_viol_e}）')
viol = n_viol_c + n_viol_d + n_viol_e
ok = viol == 0 and not fail and n_fig == 6 and n_ans == 14 and n_leftedge >= 6
if n_sig < 40:
    ok = False
    print(f'!! 签名行计数异常：{n_sig} < 40（签名口径失效嫌疑，人工复核）')
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
