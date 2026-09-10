# -*- coding: utf-8 -*-
r"""权威实测.py —— 片G 六图（纯 TikZ 矢量·下置独立行）逐图实测·唯一权威口径（0910 定档）。

自包含、可重复跑、只读：不改 main.pdf／body.tex／postproc_daoxue.py／断言脚本／素材。
用法：python 权威实测.py > run4-权威实测.txt
输出件：六图逐图实测表＋同比核验表＋声明盒余量＋标签清点＋旧口径原样复算（含吞标签逐块定位）
        ＋残差逐条归因＋门值建议。旧口径复算＝直接 import 片G实测.py 调其原函数，不复写近似。

════════════════════════════════════════════════════════════════════════════
【甲】为什么必须有第四套口径（三套旧数互斥的根因）
 A 片G-新断言探针（run3）＝量「声明盒内」的矢量墨 → 漏掉溢出声明盒的图内标签
   （g1 墨高 57.10，实为 58.00；标签在盒外，前距/下距被系统性高估 5mm 级）。
 B 终版实测（run3）＝量「同栏正文行带内」全墨 → 邻行正文墨与图内标签并进同一 bbox，
   且带边界被数学行 bbox 侵入（g1 高 63.71，比素材同比预测矮 5.12mm）。
 C 片G实测·线框列（run3，本口径的前身）＝取「与矢量种子簇*外接矩形*（外扩 1pt）相交的墨连通域」之并
   → 凡蹭到该外接矩形边界的图内标签整块被吞；吞与不吞只由 0.1mm 级的「压线／留缝」决定，随缩放
     系数与标签字体度量翻转 → 件内与素材不可比。铁证见本脚本【五】（原样复跑旧脚本＋逐块定位）：
     · g3 素材侧：旧 seed 外接矩形底 y1＝75.41mm，左下角顶点标签 A 的墨顶 y0＝75.38mm → 压线
       0.03mm → 被吞 → "线框"从纯线网 67.65×67.61 撑到 71.29×72.09（×k=0.9767 → 69.63×70.42）；
       件内侧同一标签距旧 seed 底留缝 +0.13mm → 不吞 → 66.12×66.08 → 伪 Δ −3.51/−4.33。
       即：任务书三处残差之首并非版式差，而是 0.16mm 的判据缝隙差。
     · g2 件内侧旧高 34.71 吞了顶部标签行（本口径 32.09）→ 旧 Δ −0.00/+2.54 全由此来。
     · g4 件内旧 53.76×27.18 吞了盒内标签（本口径 52.79×23.33，虚高 +0.97/+3.85mm），旧 Δ
       +0.09/+0.09 只是两侧同吞而相消——绝对尺寸仍是错的，故旧"线框列"整体作废。
     · g5 旧 Δ +1.29/+0.77 与本 bug 无关：本口径复算仍 +1.29/+0.82 → 属【乙】9(b) 参考系缺陷
       （片段无画布锁定 → \resizebox 缩"含标签自然外框"，而自然外框随标签字体度量变化），见【六】。
 → 结论：判据必须从「笔画外接矩形」换成「笔画本身」；且同比参考系必须取与字体无关的量。

════════════════════════════════════════════════════════════════════════════
【乙】权威口径定义（后续断言门以本节为准）
 0) 版面常数：A4 宽 595.276pt；左右边距 17.2mm；栏宽 84.0mm；栏间 7.6mm；下边距 20mm；
    1mm＝72/25.4pt；渲染 600dpi（1px＝0.04233mm）；真墨阈值 灰度<200。
 1) 笔画集 D＝page.get_drawings() 全部绘图对象（直线 l／贝塞尔 c／矩形 re／四边 qu），
    连同原线宽、原色、原虚线节距、原线端／线拐一并取用。
 2) 种子笔画（只用于"找到图在哪"，不参与量尺寸）：
    · 斜笔＝非轴对齐（dx>1pt 且 dy>1pt）且跨度>2mm；其中跨度≥5mm 计「斜长笔」；
    · 小块＝0.6–4pt 见方的矩形/四边/短曲线（顶点圆点、箭头头、圈号①②③的圆弧）；
      小块计种子但不计斜长笔。
 3) 图簇＝对 2) 的种子集做 8mm 间隙并查集聚簇，再按「同 y 带（y 向隙≤3mm）且 x 向隙≤20mm」
    迭代并行并簇 —— 三联图 g6 三段子图必须并成一簇；「恰成六簇」即并簇参数的硬校验。
    簇门槛：宽≥15mm、高≥10mm、斜长笔≥3（表线/正文/花形/√× 自绘产 0–2 根斜长笔，真图≥5）。
 4) 线框 W（＝权威图墨，量尺寸与定间距的基准）："真压在矢量笔画上的墨"：
    ① 把簇 bbox 内 D 的全部笔画（含轴对齐棱、虚线、填充块）按各自原线宽＋0.8pt、
       按素材原虚线节距之外的**实线**重放到同尺寸空白页 → 600dpi 二值"笔画蒙版"M（再膨胀 1px
       吸收抗锯齿）；∴ M ⊇ 真笔画墨，且 M 的形状由矢量几何唯一决定，与文字无关。
    ② 件内同区真墨掩膜 A ∩ M → 8 邻接连通域（域内≥4px）之并＝W。
    ∴ W ⊆ M ⊆ 笔画并集：图内标签与正文墨在原理上都无法撑大 W；件内与素材走同一函数，
    缩放不变（Δ 只反映真实版式差）。另登记「虚线保真率」＝W 的墨像素在按原虚线节距重放的
    蒙版下的存活率（应≈1.00，防止重放把虚线画歪）。
 5) 图内标签（文本层口径，不用墨连通域）：同栏文本行中，非正文行、与「W ⊕3.5mm」相交、
    自身 ≤22×15mm、且不与任何正文行 bbox 相交者；其"墨"＝该行 bbox 外放 1.2pt 内的真墨。
    正文行判据（本件实测校准）：同栏、跨度最大字号 ∈[9.6,11.2]pt、行宽 ≥4mm。
    —— 六图标签字号 7.80／14.48／14.55／15.14／16.29／17.37／17.58pt 全落正文档外，天然可分；
    换行后不足 15mm 的正文窄末行（如 g1 上邻「b−a−c.」宽 12.54mm）字号 10.25pt，仍正确归正文，
    故不重现旧口径 B/C 的正文污染。
 6) 含标签框 F＝W ∪ 各图内标签真墨＝视觉整图（居中与零侵入核验用）。
 7) 逐图读数（单位 mm，两位小数）：
    页/栏；斜长笔数；线框 W 宽×高；含标签 F 宽×高；
    栏心偏差＝(框心−栏心)，W 基与 F 基并列；
    前距＝图墨顶 − 上邻正文行**真墨底**；下距＝下邻正文行**真墨顶** − 图墨底；
      含标签基与 W 基共用同一对邻行（邻行由 F 定）；一律以墨级为准——文本行 bbox 含升降部
      空档，bbox 基会把缝放大 1mm 级（本脚本并列打印两基供换算）；
    正文相交＝与「F ⊕0.3mm」相交的正文行数，**必须 0**（零侵入硬门；本件六图实测全 0）。
 8) 同比核验（权威性的关键）：素材 standalone（_tmp片G素材/，border=0pt 壳，整页＝片段自然外框）
    走 4)–6) 同一函数（标签认领半径按 1/k 放大，保持与件内同一相对判据）→
    素材线框 W_s ／含标签 F_s ／长宽比 → ×k（k＝声明置宽／素材页宽）→ 预测件内；Δ＝件内−预测。
    · 权威 Δ＝线框基（纯几何，与字体无关），验收线 |Δ|≤0.50mm；
    · 含标签基 Δ 只作参考：素材排数学标签用 CM 家族（CMMI/CMR），件内经 unicode-math 换成
      TeX Gyre Termes Math／泰古，同一锚点下字形墨框不同（g4 素材标签墨宽比件内宽 1.9mm 即此因），
      故不得入闸门；
    · 另给两项与 k（进而与字体）无关的不变量作旁证：各向同性比 rx＝W_w件/W_w素、ry＝W_h件/W_h素
      （|rx−ry| ≤ 0.005 → 证「严格同比、无拉伸畸变」；六图实测 max 0.00265，属墨级线宽端点差）；
      线框/含标形状比之差 件内−素材（≤ 0.005；六图实测 max 0.0036）。
 9) 残差处置：|Δ|>0.50mm 者逐条给因，分三类登记——
    (a) 口径 bug（已修，如【甲】C 的吞标签）；
    (b) 参考系缺陷（本件唯一例＝g5）：figs/g5-fold.tikz 是六片段中唯一无 \path[use as bounding box]
        锁定者 → \resizebox{54.7mm} 的缩放对象＝"含标签自然外框"，而该外框由标签字体度量决定：
        素材（CM 体）页宽 56.56mm，件内（泰古/Termes）同一自然盒实测只有 55.00mm（＝54.7÷rx），
        差 1.57mm＝2.85%，与线框基 Δ +1.29mm（占线框宽 2.77%）同量级同方向 → 属参考系错位，
        不是版式走形（|rx−ry|=0.00024、形状比差 |Δ|≤0.0007 皆在不变量容差内；片段自带注释
        第 4–5 行亦已登记「无 bbox 锁定…会被同比缩 ~3.3%」）。
        收法二选一并已登记在【六】：给该片段补画布锁定（改件动作，本轮不做），或断言对无锁定
        片段改核不变量。
    (c) 真实版式差（须回改件）。
 → 不为收敛而调参数；本文件内所有常数（0.50mm 验收线、0.25mm 门窗安全垫、3.5mm 标签认领半径、
   8mm/20mm/3mm 并簇、0.8pt 线宽外放、1px 膨胀、4px 最小域）一律不动，实测残差全部由口径解释。
════════════════════════════════════════════════════════════════════════════
"""
import re
import sys
import pymupdf

PT = 72 / 25.4
PAGEW = 595.276
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (PAGEW - 2 * MARGIN - COLSEP) / 2          # 84.0mm
MID = MARGIN + COLW + COLSEP / 2
BOT = 20 * PT
DPI = 600
THR = 200
GAP_CLUSTER = 8 / 25.4 * PT
YTOL = 3 * PT
XGAP = 20 * PT
MINLONG = 3
LONG_MM = 5.0
SEED_MM = 2.0
REPLAY_PAD = 0.8
MASK_DIL = 1
BODY_SIZE = (9.6, 11.2)
BODY_MINW = 4.0 * PT
LAB_R = 3.5 * PT
LAB_MAXW, LAB_MAXH = 22 * PT, 15 * PT
LAB_PAD = 1.2
MIN_PIX = 4
DELTA_OK = 0.50                                       # 线框基同比验收线（mm）
ISO_OK = 0.005                                         # 各向同性 |rx−ry| 容差
SHAPE_OK = 0.005                                       # 线框/含标形状比 件内−素材 容差
SRC = 'C:/提示词/工作区/_tmp片G素材/'
FIGDIR = 'C:/提示词/工作区/字替对照-0909/variantF/'
MAIN = FIGDIR + 'main.pdf'
# (标签, 素材 standalone, 声明置宽 mm, 件内片段, 预期落位(页,栏))
MAP = [
    ('g6 三联', 'sub3_投影三联-纯tikz体检.pdf', 84.0, 'g6-triple', (2, 2)),
    ('g1 棱柱', 'img1_tikz.pdf', 41.1, 'g1-prism', (3, 2)),
    ('g2 正方体E', 'image2_重绘.pdf', 42.0, 'g2-cubeE', (4, 1)),
    ('g3 正方体6', 'tikz_tan6.pdf', 84.0, 'g3-cube6', (5, 1)),
    ('g4 二面角', '片G-image4-二面角-standalone.pdf', 66.3, 'g4-dihedral', (6, 1)),
    ('g5 折叠', 'fig-image5-fold.pdf', 54.7, 'g5-fold', (6, 2)),
]
COLC = 72.0 / DPI                                  # pt per px
_bbox_re = re.compile(r'use as bounding box\]?.*?rectangle\s*\(\s*0\s*,\s*0\s*\)\s*rectangle'
                      r'|useasboundingbox\s*\(\s*0\s*,\s*0\s*\)\s*rectangle\s*\('
                      r'|use as bounding box\]?\s*\(\s*0\s*,\s*0\s*\)\s*rectangle\s*\(')


def frag_lock(name):
    """读片段 tex，取声明画布（bbox 锁定）mm；无锁定返回 None。"""
    try:
        s = open(FIGDIR + 'figs/' + name + '.tikz', encoding='utf-8').read()
    except Exception:
        return None
    m = re.search(r'(?:use as bounding box\]?|useasboundingbox)\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)'
                  r'\s*\)\s*rectangle\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)', s)
    if not m:
        return None
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    return (x1 - x0, y1 - y0)


# ------------------------------------------------------------------ 矢量层
def strokes(page):
    out = []
    for o in page.get_drawings():
        col, fill = o.get('color'), o.get('fill')
        if col is None and fill is None:
            continue
        wd = o.get('width') or 1.0
        base = dict(w=wd, col=col, fill=fill, cap=o.get('lineCap') or 0,
                    join=o.get('lineJoin') or 0, dashes=o.get('dashes'))
        for it in o['items']:
            kind = it[0]
            if kind == 'l':
                p1, p2 = it[1], it[2]
                dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                span = max(dx, dy) / PT
                dg = dx > 1.0 and dy > 1.0 and span > SEED_MM
                out.append(dict(base, kind='l', pts=[p1, p2],
                                rect=pymupdf.Rect(min(p1.x, p2.x), min(p1.y, p2.y),
                                                  max(p1.x, p2.x), max(p1.y, p2.y)),
                                seed=dg, long=dg and span >= LONG_MM))
            elif kind == 'c':
                ps = list(it[1:5])
                xs = [q.x for q in ps]
                ys = [q.y for q in ps]
                w, h = max(xs) - min(xs), max(ys) - min(ys)
                span = max(w, h) / PT
                dg = w > 1.0 and h > 1.0 and span > SEED_MM
                blk = (not dg) and 0.6 * PT <= span * PT <= 4 * PT and min(w, h) > 0.5
                out.append(dict(base, kind='c', pts=ps,
                                rect=pymupdf.Rect(min(xs), min(ys), max(xs), max(ys)),
                                seed=dg or blk, long=dg and span >= LONG_MM))
            elif kind in ('re', 'qu'):
                r = pymupdf.Rect(it[1])
                blk = 0.6 * PT <= r.width <= 4 * PT and 0.6 * PT <= r.height <= 4 * PT
                out.append(dict(base, kind=kind, pts=None, rect=r, seed=blk, long=False))
    return out


def clusters(stk):
    idx = [i for i, s in enumerate(stk) if s['seed']]
    rs = [pymupdf.Rect(stk[i]['rect']) for i in idx]
    lg = [1 if stk[i]['long'] else 0 for i in idx]
    par = list(range(len(rs)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            a = pymupdf.Rect(rs[i])
            a.x0 -= GAP_CLUSTER
            a.y0 -= GAP_CLUSTER
            a.x1 += GAP_CLUSTER
            a.y1 += GAP_CLUSTER
            if a.intersects(rs[j]):
                x, y = find(i), find(j)
                if x != y:
                    par[x] = y
    grp = {}
    for i in range(len(rs)):
        grp.setdefault(find(i), []).append(i)
    cs = []
    for g in grp.values():
        r = pymupdf.Rect(rs[g[0]])
        for t in g[1:]:
            r |= rs[t]
        cs.append([r, sum(lg[t] for t in g), [idx[t] for t in g]])
    changed = True
    while changed:
        changed = False
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                a, b = cs[i][0], cs[j][0]
                oy = min(a.y1, b.y1) - max(a.y0, b.y0)
                ox = min(a.x1, b.x1) - max(a.x0, b.x0)
                if (oy > -YTOL and max(a.x0, b.x0) - min(a.x1, b.x1) <= XGAP) or \
                   (ox > -YTOL and max(a.y0, b.y0) - min(a.y1, b.y1) <= XGAP):
                    cs[i] = [a | b, cs[i][1] + cs[j][1], cs[i][2] + cs[j][2]]
                    del cs[j]
                    changed = True
                    break
            if changed:
                break
    return [c for c in cs if c[0].width / PT >= 15 and c[0].height / PT >= 10 and c[1] >= MINLONG]


def _dashstr(d, scale=1.0):
    if not d:
        return None
    arr = d['array'] if isinstance(d, dict) else d
    ph = float(d.get('phase', 0.0)) if isinstance(d, dict) else 0.0
    try:
        arr = [float(v) * scale for v in arr]
    except Exception:
        return None
    if not arr or sum(arr) <= 0:
        return None
    return '[' + ' '.join('%.4f' % v for v in arr) + '] %.4f' % ph


def _replay(page, clip, stk, inidx, dashed, pad=REPLAY_PAD):
    """笔画重放到同尺寸空白页 → 600dpi 二值蒙版。dashed=False 即权威笔画蒙版 M。"""
    import numpy as np
    from scipy import ndimage
    nd = pymupdf.open()
    npg = nd.new_page(width=page.rect.width, height=page.rect.height)
    for i in inidx:
        s = stk[i]
        if s['fill'] is not None and s['col'] is None:
            fc = s['fill']
            if s['kind'] == 'qu':
                npg.draw_quad(pymupdf.Quad(s['rect']), color=None, fill=fc)
            elif s['pts'] and len(s['pts']) >= 3:
                npg.draw_polyline(s['pts'] + [s['pts'][0]], color=None, fill=fc)
            else:
                npg.draw_rect(s['rect'], color=None, fill=fc)
            continue
        sc = s['col'] or (0, 0, 0)
        wdt = s['w'] + pad
        ds = _dashstr(s['dashes']) if dashed else None
        try:
            if s['kind'] == 'l':
                npg.draw_line(s['pts'][0], s['pts'][1], color=sc, width=wdt,
                              lineCap=s['cap'], lineJoin=s['join'], dashes=ds)
            elif s['kind'] == 'c':
                p = s['pts']
                npg.draw_bezier(p[0], p[1], p[2], p[3], color=sc, width=wdt,
                                lineCap=s['cap'], lineJoin=s['join'], dashes=ds)
            else:
                npg.draw_rect(s['rect'], color=sc, width=wdt, dashes=ds)
        except Exception:
            npg.draw_rect(s['rect'], color=sc, width=wdt)
    a = _gray(npg.get_pixmap(dpi=DPI, clip=clip))
    nd.close()
    m = a < 250
    if MASK_DIL:
        m = ndimage.binary_dilation(m, np.ones((3, 3), bool), iterations=MASK_DIL)
    return m


def _gray(pix):
    import numpy as np
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    return np.frombuffer(s, dtype=np.uint8).reshape(h, w, n)[:, :, :3].mean(axis=2)


def ink_mask(page, clip):
    return _gray(page.get_pixmap(dpi=DPI, clip=clip)) < THR


def comps_rect(mask, ox, oy, minpix=MIN_PIX, dilate=0):
    """掩膜 → 8 邻接各连通域真墨 bbox（pt 绝对坐标）。dilate>0 时仅用于并域，bbox 取真墨。"""
    import numpy as np
    from scipy import ndimage
    st = np.ones((3, 3), bool)
    lab, _cnt = ndimage.label(
        ndimage.binary_dilation(mask, st, iterations=dilate) if dilate else mask, structure=st)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        sub = mask[sl] & (lab[sl] == i)
        if sub.sum() < minpix:
            continue
        ys, xs = np.nonzero(sub)
        out.append(pymupdf.Rect(ox + (sl[1].start + xs.min()) * COLC,
                                oy + (sl[0].start + ys.min()) * COLC,
                                ox + (sl[1].start + xs.max() + 1) * COLC,
                                oy + (sl[0].start + ys.max() + 1) * COLC))
    return out


def sub_ink(mask, ox, oy, rect, band):
    """band 掩膜内、rect∩band 部分的真墨 bbox（无墨返回 None）。"""
    import numpy as np
    x0, y0 = max(rect.x0, band.x0), max(rect.y0, band.y0)
    x1, y1 = min(rect.x1, band.x1), min(rect.y1, band.y1)
    if x1 <= x0 or y1 <= y0:
        return None
    c0, r0 = max(int((x0 - ox) / COLC), 0), max(int((y0 - oy) / COLC), 0)
    c1 = min(int((x1 - ox) / COLC) + 1, mask.shape[1])
    r1 = min(int((y1 - oy) / COLC) + 1, mask.shape[0])
    sub = mask[r0:r1, c0:c1]
    if not sub.any():
        return None
    ys, xs = np.nonzero(sub)
    return pymupdf.Rect(ox + (c0 + xs.min()) * COLC, oy + (r0 + ys.min()) * COLC,
                        ox + (c0 + xs.max() + 1) * COLC, oy + (r0 + ys.max() + 1) * COLC)


# ------------------------------------------------------------------ 文本层
def text_lines(page):
    ls = []
    for b in page.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        for ln in b.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not t:
                continue
            ls.append(dict(t=t, r=pymupdf.Rect(ln['bbox']),
                           sz=max(sp['size'] for sp in ln['spans'])))
    return ls


def is_body(L):
    return BODY_SIZE[0] <= L['sz'] <= BODY_SIZE[1] and L['r'].width >= BODY_MINW


# ------------------------------------------------------------------ 单图测量
def measure_fig(page, stk, clus, lines, labr=LAB_R, src=False, box_mm=None):
    """一个图簇 → 权威读数 dict。src=True 用于素材整页（无正文，全部文本行皆图内标签）。"""
    r, nlong, members = clus
    if src:
        col, cl, cw = 1, page.rect.x0, page.rect.width
    else:
        col, cl = (1, MARGIN) if r.x0 < MID else (2, MARGIN + COLW + COLSEP)
        cw = COLW
    H = page.rect.height
    my = [L for L in lines if cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= cl + cw + 2]
    body = [] if src else [L for L in my if is_body(L)]
    if src:
        band = pymupdf.Rect(page.rect.x0 + 0.1, page.rect.y0 + 0.1,
                            page.rect.x1 - 0.1, page.rect.y1 - 0.1)
    else:
        upb = [L['r'] for L in body if L['r'].y1 <= r.y0 + 0.5]
        dnb = [L['r'] for L in body if L['r'].y0 >= r.y1 - 0.5]
        y0 = (min(x.y0 for x in upb) if upb else r.y0 - 6 * PT) - 2 * PT
        y1 = (max(x.y1 for x in dnb) if dnb else r.y1 + 6 * PT) + 2 * PT
        band = pymupdf.Rect(cl + 0.15, max(1.0, y0), cl + cw - 0.15, min(H - 1.0, y1))
    near = pymupdf.Rect(r.x0 - 0.3 * PT, r.y0 - 0.3 * PT, r.x1 + 0.3 * PT, r.y1 + 0.3 * PT)
    inidx = [i for i, s in enumerate(stk)
             if near.intersects(s['rect']) and band.contains(s['rect'])]
    if not inidx:
        return None
    A = ink_mask(page, band)
    M = _replay(page, band, stk, inidx, dashed=False)
    Md = _replay(page, band, stk, inidx, dashed=True)
    WM = A & M
    Wc = comps_rect(WM, band.x0, band.y0)
    if not Wc:
        return None
    W = Wc[0]
    for q in Wc[1:]:
        W |= q
    geo = pymupdf.Rect(stk[inidx[0]]['rect'])
    for i in inidx[1:]:
        geo |= stk[i]['rect']
    claim = pymupdf.Rect(W.x0 - labr, W.y0 - labr, W.x1 + labr, W.y1 + labr)
    labs = []
    for L in my:
        if not src and is_body(L):
            continue
        lr = L['r']
        if lr.width > LAB_MAXW or lr.height > LAB_MAXH or not lr.intersects(claim):
            continue
        if any(B['r'].intersects(lr) for B in body):
            continue
        ib = sub_ink(A, band.x0, band.y0,
                     pymupdf.Rect(lr.x0 - LAB_PAD, lr.y0 - LAB_PAD,
                                  lr.x1 + LAB_PAD, lr.y1 + LAB_PAD), band)
        if ib is None or ib.width > LAB_MAXW or ib.height > LAB_MAXH:
            continue
        labs.append(dict(t=L['t'], bbox=lr, ink=ib, sz=L['sz']))
    F = pymupdf.Rect(W)
    for L in labs:
        F |= L['ink']
    out = dict(col=col, cl=cl, cw=cw, nlong=nlong, nstroke=len(inidx), W=W, F=F,
               labs=labs, nlab=len(labs), band=band, nWpx=int(WM.sum()),
               alive=int((WM & Md).sum()), geo=geo, src=src)
    if not src:
        Fin = pymupdf.Rect(F.x0 - 0.3 * PT, F.y0 - 0.3 * PT, F.x1 + 0.3 * PT, F.y1 + 0.3 * PT)
        rows = []
        for L in body:
            ib = sub_ink(A, band.x0, band.y0, L['r'], band)
            if ib is not None:
                rows.append(dict(t=L['t'], bbox=L['r'], ink=ib))
        out['hits'] = [R for R in rows if R['bbox'].intersects(Fin) or R['ink'].intersects(Fin)]
        out['above'] = [R for R in rows if R['bbox'].y1 <= F.y0 + 0.3 * PT]
        out['below'] = [R for R in rows if R['bbox'].y0 >= F.y1 - 0.3 * PT]
        out['up'] = max(out['above'], key=lambda z: z['bbox'].y1) if out['above'] else None
        out['dn'] = min(out['below'], key=lambda z: z['bbox'].y0) if out['below'] else None
        cc = cl + COLW / 2
        if box_mm:
            out['box'] = (cc - box_mm * PT / 2, cc + box_mm * PT / 2)
        out['cc'] = cc
    return out


def mm(r):
    return r.width / PT, r.height / PT


# ------------------------------------------------------------------ 旧口径复算
LEGACY = '片G实测.py'          # run3「线框列」的出处（＝本口径前身，判据已被【甲】C 证伪）
# run3-六图实测.txt 登记的旧 Δ线框；复算须逐位对上，否则说明复算没照原样跑
HIST_OLD = {'g6 三联': (0.01, -0.02), 'g1 棱柱': (0.00, -0.04), 'g2 正方体E': (0.00, 2.54),
            'g3 正方体6': (-3.51, -4.33), 'g4 二面角': (0.09, 0.09), 'g5 折叠': (1.29, 0.77)}


def legacy_mod():
    """载入 run3 旧脚本（只读，__main__ 门控不触发自跑），用其*原函数*复算旧口径——
       避免"我另写一套近似"导致复算本身不可信。"""
    import os
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), LEGACY)
    spec = importlib.util.spec_from_file_location('_legacy_run3', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def legacy_seed(m, page, target):
    """旧口径种子＝diag_items（只收斜笔/曲线/小块，不含轴对齐棱）→ 8mm 聚簇 → 同带并簇 → 门槛。
       与 target（本口径簇 rect）中心最近者配为该图种子，外扩 1pt 成"外接矩形"。"""
    cs = m.merge_rows(m.cluster(m.diag_items(page.get_drawings()), GAP_CLUSTER))
    cs = [(r, n) for r, n in cs if r.width / PT >= 15 and r.height / PT >= 10 and n >= MINLONG]
    if not cs:
        return None
    cx, cy = (target.x0 + target.x1) / 2, (target.y0 + target.y1) / 2
    r = min(cs, key=lambda z: ((z[0].x0 + z[0].x1) / 2 - cx) ** 2 + ((z[0].y0 + z[0].y1) / 2 - cy) ** 2)[0]
    return pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)


def legacy_wire(lg, page, seed, band):
    """旧「线框列」＝(band 内 600dpi 墨膨胀 2px 并域后) 与 seed 外接矩形相交的连通域之并。"""
    comps = lg.ink_components(page, band)
    keep = [c for c in comps if c.intersects(seed)]
    if not keep:
        return None, [], comps
    U = keep[0]
    for q in keep[1:]:
        U |= q
    return U, keep, comps


def seed_margin(c, S):
    """墨块 c 对旧 seed「外接矩形」的判据余量（mm）：负＝压线（旧法必吞），正＝留缝（旧法不收）。"""
    dx = max(S.x0 - c.x1, c.x0 - S.x1, 0.0)
    dy = max(S.y0 - c.y1, c.y0 - S.y1, 0.0)
    if dx == 0.0 and dy == 0.0:
        pen = [v for v in (c.x1 - S.x0, S.x1 - c.x0, c.y1 - S.y0, S.y1 - c.y0) if v > 0]
        return -min(pen) / PT
    return (dx * dx + dy * dy) ** 0.5 / PT


# ------------------------------------------------------------------ 主流程
def main():
    doc = pymupdf.open(MAIN)
    stks = {p: strokes(doc[p - 1]) for p in range(1, doc.page_count + 1)}
    lns = {p: text_lines(doc[p - 1]) for p in range(1, doc.page_count + 1)}
    cand = []
    for pno in range(1, doc.page_count + 1):
        for c in clusters(stks[pno]):
            cand.append((pno, c))
    cand.sort(key=lambda z: (z[0], z[1][0].y0))
    print('=' * 132)
    print('片G 六图下置·权威实测（口径：矢量笔画重放蒙版 ∩ 600dpi 真墨＝线框；图内标签走文本层）')
    print('件内 %s（%d 页｜md5 f80297ffeeb872438943da5bdc5cebc1）｜素材 %s' % (MAIN, doc.page_count, SRC))
    print('版面常数：A4 595.276pt｜边距 17.2mm｜栏宽 %.2fmm｜栏间 7.6mm｜下边距 20mm｜渲染 %ddpi' % (COLW / PT, DPI))
    print('矢量图簇命中 %d（须 6）' % len(cand))
    print('=' * 132)
    if len(cand) != 6:
        print('!! 簇数≠6 → 并簇/门槛参数失效，整表判废')
        return 2
    rows = []
    for i, (pno, c) in enumerate(cand):
        tag, sn, wbox, frag, at = MAP[i]
        d = measure_fig(doc[pno - 1], stks[pno], c, lns[pno], box_mm=wbox)
        if d is None:
            print('!! %s 无线框墨' % tag)
            return 2
        d.update(tag=tag, frag=frag, page=pno, boxmm=wbox, at=at, clus=c, srcname=sn)
        rows.append(d)
    if [(d['page'], d['col']) for d in rows] != [m[4] for m in MAP]:
        print('!! 落位与预期台账不符：', [(d['page'], d['col']) for d in rows])
        return 2

    print('\n【一】六图逐图实测（mm；线框＝权威图墨，含标签＝线框∪图内标签真墨）')
    print(' 片段       页栏 斜长笔 笔画 标签 │ 线框宽×高        含标签宽×高       '
          '│ 栏心偏 线框/含标   │ 前距 含标/线框   │ 下距 含标/线框  │ 正文相交 落位')
    print(' ' + '─' * 128)
    for d in rows:
        ww, wh = mm(d['W'])
        fw, fh = mm(d['F'])
        d.update(ww=ww, wh=wh, fw=fw, fh=fh,
                 devW=((d['W'].x0 + d['W'].x1) / 2 - d['cc']) / PT,
                 devF=((d['F'].x0 + d['F'].x1) / 2 - d['cc']) / PT,
                 upF=(d['F'].y0 - d['up']['ink'].y1) / PT if d.get('up') else float('nan'),
                 upW=(d['W'].y0 - d['up']['ink'].y1) / PT if d.get('up') else float('nan'),
                 dnF=(d['dn']['ink'].y0 - d['F'].y1) / PT if d.get('dn') else float('nan'),
                 dnW=(d['dn']['ink'].y0 - d['W'].y1) / PT if d.get('dn') else float('nan'))
        print(' %-9s p%dc%d %5d %5d %4d │ %7.2f × %7.2f  %7.2f × %7.2f  │ %+6.2f / %+6.2f  │ '
              '%6.2f / %6.2f  │ %6.2f / %6.2f │ %5d   OK'
              % (d['tag'], d['page'], d['col'], d['nlong'], d['nstroke'], d['nlab'],
                 ww, wh, fw, fh, d['devW'], d['devF'], d['upF'], d['upW'], d['dnF'], d['dnW'],
                 len(d.get('hits') or [])))
    print('  注：前距＝上邻正文行真墨底→图墨顶；下距＝下邻正文行真墨顶→图墨底。含标签基为视觉缝，'
          '线框基为纯线网缝。')
    print('  邻行台账（墨底/墨顶 与 行bbox底/bbox顶，mm）：')
    for d in rows:
        up, dn = d.get('up'), d.get('dn')
        print('   %-9s 上邻 墨%7.2f|bbox%7.2f「%s」｜下邻 墨%7.2f|bbox%7.2f「%s」' % (
            d['tag'], up['ink'].y1 / PT, up['bbox'].y1 / PT, up['t'][:15],
            dn['ink'].y0 / PT, dn['bbox'].y0 / PT, dn['t'][:15]))

    print('\n【二】同比核验（素材 standalone 同函数同算法 ×k → 预测件内；权威＝线框基 Δ）')
    print(' 片段       素材页宽×高            k       锁画布       素材线框→预测      件内线框'
          '     Δ线框        rx/ry        素材含标→预测    件内含标       Δ含标(参考)')
    print(' ' + '─' * 128)
    bad = []
    for d in rows:
        sd = pymupdf.open(SRC + d['srcname'])
        sp = sd[0]
        sstk = strokes(sp)
        slines = text_lines(sp)
        scs = clusters(sstk)
        srect = pymupdf.Rect(scs[0][0])
        for c in scs[1:]:
            srect |= c[0]
        seed = [i for c in scs for i in c[2]]
        nl = sum(c[1] for c in scs)
        pw, ph = sp.rect.width / PT, sp.rect.height / PT
        k = d['boxmm'] / pw
        sm = measure_fig(sp, sstk, (srect, nl, seed), slines, labr=LAB_R / k, src=True)
        swx, shy = mm(sm['W'])
        sfx, sfy = mm(sm['F'])
        lock = frag_lock(d['frag'])
        rx, ry = d['ww'] / swx, d['wh'] / shy
        dWw, dWh = d['ww'] - swx * k, d['wh'] - shy * k
        dFw, dFh = d['fw'] - sfx * k, d['fh'] - sfy * k
        d.update(src=dict(pw=pw, ph=ph, k=k, sw=swx, sh=shy, sfw=sfx, sfh=sfy,
                          dWw=dWw, dWh=dWh, dFw=dFw, dFh=dFh, nclus=len(scs), lock=lock,
                          rx=rx, ry=ry, nlab=len(sm['labs']), sW=sm['W'], sF=sm['F'],
                          sLabs=sm['labs'], srect=srect, sband=sm['band'],
                          alive=sm['alive'] / max(1, sm['nWpx']),
                          geoW=mm(sm['geo'])[0] * k, geoH=mm(sm['geo'])[1] * k))
        print(' %-9s %-26s %.4f×%.4f %6.4f %s  %6.2f×%6.2f→%6.2f×%6.2f %6.2f×%6.2f %+6.2f/%+6.2f '
              '%.4f/%.4f  %6.2f×%6.2f→%6.2f×%6.2f %6.2f×%6.2f %+6.2f/%+6.2f'
              % (d['tag'], d['srcname'], pw, ph, k,
                 ('%5.2f×%5.2f' % lock) if lock else '   无锁定  ',
                 swx, shy, swx * k, shy * k, d['ww'], d['wh'], dWw, dWh, rx, ry,
                 sfx, sfy, sfx * k, sfy * k, d['fw'], d['fh'], dFw, dFh))
        if abs(dWw) > DELTA_OK or abs(dWh) > DELTA_OK:
            bad.append(d)
    print('  自检：素材簇数全 1？ %s｜各向同性 |rx−ry| 最大 %.5f（门 ≤%.3f 即严格同比、无拉伸畸变）｜'
          '虚线保真率最小 %.3f' % (all(d['src']['nclus'] == 1 for d in rows),
                                 max(abs(d['src']['rx'] - d['src']['ry']) for d in rows),
                                 ISO_OK, min(d['src']['alive'] for d in rows)))
    print('  素材标签数 vs 件内：%s' % '  '.join(
        '%s %d/%d' % (d['tag'].split()[0], d['src']['nlab'], d['nlab']) for d in rows))

    print('\n【三】声明盒水平余量（盒＝置宽居中控件盒；负＝图墨溢出声明盒——真实现象，计入图墨）')
    for d in rows:
        bx0, bx1 = d['box']
        print('  %-9s 置宽%5.1f 盒[%7.2f,%7.2f] 线框余 %+5.2f/%+5.2f 含标余 %+5.2f/%+5.2f '
              '（含标越盒 %s mm）'
              % (d['tag'], d['boxmm'], bx0 / PT, bx1 / PT,
                 (d['W'].x0 - bx0) / PT, (bx1 - d['W'].x1) / PT,
                 (d['F'].x0 - bx0) / PT, (bx1 - d['F'].x1) / PT,
                 '%.2f' % max(0, (bx0 - d['F'].x0) / PT, (d['F'].x1 - bx1) / PT)))

    print('\n【四】图内标签清点（文本层：字号档外＋线框外扩 %.1fmm＋不碰正文行）' % (LAB_R / PT))
    for d in rows:
        print('  %-9s 件内 %d 个（素材同法 %d 个）：%s' % (
            d['tag'], d['nlab'], d['src']['nlab'],
            ' '.join('%s' % L['t'][:5].replace('\n', '') for L in d['labs'])))

    print('\n【五】旧口径复算（原样重跑 run3 旧脚本 %s 的 measure_doc/measure_src，一字未改）'
          '＋吞标签逐块定位 —— 伪 Δ 的来源' % LEGACY)
    print('  片段       件内旧线框→权威线框      素材旧线框×k→权威×k    旧Δ线框(复算/历史)      权威Δ线框  复现')
    lg = legacy_mod()
    ldm = lg.measure_doc(lg.MAIN)
    assert len(ldm) == 6, '旧脚本复跑簇数≠6'
    assert [(o['page'], o['col']) for o in ldm] == [(d['page'], d['col']) for d in rows], '旧脚本落位与本表不符'
    srcdoc = {}
    for d, o in zip(rows, ldm):
        m = lg.measure_src(d['srcname'], d['boxmm'])
        k = m['k']
        odW, odH = o['ww'] - m['ww'] * k, o['wh'] - m['wh'] * k
        hdw, hdh = HIST_OLD[d['tag']]
        repro = abs(odW - hdw) <= 0.02 and abs(odH - hdh) <= 0.02
        # —— 逐块定位：旧 seed 外接矩形 ∩ 墨，但落在权威线框 W 之外的连通域＝被当成线的图内标签
        sp = pymupdf.open(SRC + d['srcname'])[0]
        sseed = legacy_seed(lg, sp, d['src']['srect'])
        sdos = legacy_wire(lg, sp, sseed, pymupdf.Rect(sp.rect.x0 + 0.2, sp.rect.y0 + 0.2,
                                                       sp.rect.x1 - 0.2, sp.rect.y1 - 0.2))
        page = doc[d['page'] - 1]
        dseed = legacy_seed(lg, page, d['clus'][0])
        band = pymupdf.Rect(d['cl'] + 0.4, max(MARGIN - 2, dseed.y0 - 14 * PT),
                            d['cl'] + COLW - 0.4, min(page.rect.height - BOT + 2, dseed.y1 + 14 * PT))
        docu = legacy_wire(lg, page, dseed, band)
        srcdoc[d['tag']] = (sseed, dseed, sdos, docu, m)
        print('  %-9s %6.2f×%6.2f →%6.2f×%6.2f  %6.2f×%6.2f →%6.2f×%6.2f  %+5.2f/%+5.2f（%+5.2f/%+5.2f）'
              ' %+5.2f/%+5.2f   %s' % (
                  d['tag'], o['ww'], o['wh'], d['ww'], d['wh'], m['ww'] * k, m['wh'] * k,
                  d['src']['sw'] * k, d['src']['sh'] * k, odW, odH, hdw, hdh,
                  d['src']['dWw'], d['src']['dWh'], 'OK' if repro else '!!不符'))
    print('  注：旧Δ括号内为 run3-六图实测.txt 登记值；逐位相符＝复算忠实于旧脚本（非另写近似）。')

    print('\n  吞标签逐块定位（临界标签：与旧 seed「外接矩形」余量 <1.0mm；负＝压线→旧法必吞，'
          '正＝留缝→旧法不收）')
    for d, o in zip(rows, ldm):
        sseed, dseed, (sU, skep, scomp), (dU, dkeep, dcomp), m = srcdoc[d['tag']]
        k = d['src']['k']
        md = sorted((seed_margin(L['ink'], dseed), L['t'][:5].replace('\n', ''))
                    for L in d['labs'])
        ms = sorted((seed_margin(L['ink'], sseed), L['t'][:5].replace('\n', ''))
                    for L in d['src']['sLabs'])
        nsw_d = sum(1 for v, _t in md if v < 0)
        nsw_s = sum(1 for v, _t in ms if v < 0)
        print('   %-9s 吞标签数 件内 %d／素材 %d ｜ 旧法撑出量 件内 %+5.2f/%+5.2f ｜ 素材(×k) %+5.2f/%+5.2f'
              ' ｜ 旧Δ %+5.2f/%+5.2f → 权威Δ %+5.2f/%+5.2f' % (
                  d['tag'], nsw_d, nsw_s,
                  o['ww'] - d['ww'], o['wh'] - d['wh'],
                  (m['ww'] - d['src']['sw']) * k, (m['wh'] - d['src']['sh']) * k,
                  o['ww'] - m['ww'] * k, o['wh'] - m['wh'] * k,
                  d['src']['dWw'], d['src']['dWh']))
        for side, src in (('件内', md), ('素材', ms)):
            for v, t in src:
                if abs(v) < 1.0:
                    print('      %s %-6s 余量 %+.3fmm → %s' % (
                        side, t, v, '压线（旧法必收其墨）' if v < 0 else '留缝（旧法不收）'))
        def spill(side, keep, W, seed, labs, kk):
            if keep is None:
                return
            WR = pymupdf.Rect(W.x0 - 1, W.y0 - 1, W.x1 + 1, W.y1 + 1)
            sp = [c for c in keep if not WR.contains(c)]
            for c in sorted(sp, key=lambda z: -z.width * z.height)[:3]:
                nm = [L['t'][:5].replace('\n', '') for L in labs if c.intersects(L['ink'])]
                print('      %s 撑出块 %-8s %0.2f×%.2fmm@x[%.2f,%.2f]y[%.2f,%.2f] 越线框 左%+.2f 右%+.2f 上%+.2f 下%+.2f'
                      ' 刀口余量 %+.3fmm' % (
                          side, ('「%s」' % ''.join(nm)) if nm else '未认领',
                          c.width * kk / PT, c.height * kk / PT, c.x0 / PT, c.x1 / PT, c.y0 / PT, c.y1 / PT,
                          (W.x0 - c.x0) * kk / PT, (c.x1 - W.x1) * kk / PT,
                          (W.y0 - c.y0) * kk / PT, (c.y1 - W.y1) * kk / PT,
                          seed_margin(c, seed)))
            pool = dcomp if side == '件内' else scomp
            ms = [c for c in pool if WR.contains(c) and not c.intersects(seed)]
            if ms:
                mU = ms[0]
                for q in ms[1:]:
                    mU |= q
                print('      %s 漏收块 %d 个（真在权威线框内、却整块不与旧 seed 外接矩形相交）合并范围 %0.2f×%.2fmm'
                      ' 自 x[%.2f,%.2f] y[%.2f,%.2f] → 旧线框该向偏小 %+.2f/%+.2fmm' % (
                          side, len(ms), mU.width * kk / PT, mU.height * kk / PT,
                          mU.x0 / PT, mU.x1 / PT, mU.y0 / PT, mU.y1 / PT,
                          (min(c.x0 for c in ms) - W.x0) * kk / PT,
                          (max(c.y1 for c in ms) - W.y1) * kk / PT))
        spill('件内', dkeep, d['W'], dseed, d['labs'], 1.0)
        spill('素材', skep, d['src']['sW'], sseed, d['src']['sLabs'], d['src']['k'])
        exW = (o['ww'] - d['ww']) - (m['ww'] - d['src']['sw']) * k
        exH = (o['wh'] - d['wh']) - (m['wh'] - d['src']['sh']) * k
        mx = max(abs(o['ww'] - d['ww']), abs(o['wh'] - d['wh']),
                 abs(m['ww'] - d['src']['sw']) * k, abs(m['wh'] - d['src']['sh']) * k)
        if max(abs(exW), abs(exH)) > 0.50:
            print('      ⇒ 两侧撑出量不等（差 %+5.2f/%+5.2f mm）→ 件内/素材不可比 → 旧 Δ 是口径伪差；'
                  '本口径标签走文本层、两侧同判据 → 伪差归零' % (exW, exH))
        elif mx < 0.10:
            print('      ⇒ 两侧撑出量皆 <0.10mm（旧法虽收了标签墨，但其墨本在线框界内＝吞而未胀）'
                  '→ 本图旧读数与本口径读数一致，无需豁免')
        elif max(abs(d['src']['dWw']), abs(d['src']['dWh'])) > DELTA_OK:
            print('      ⇒ 两侧撑出量对称（差 %+5.2f/%+5.2f mm）→ 本图旧 Δ 不由吞标签产生，'
                  '另有来源（见【六】参考系判定）' % (exW, exH))
        else:
            print('      ⇒ 两侧同吞（撑出差 %+5.2f/%+5.2f mm，最大撑出 %.2fmm）→ 旧 Δ 侥幸相消，'
                  '但旧「线框列」绝对尺寸已虚大/虚小，不得用作图尺寸·间距门' % (exW, exH, mx))

    print('\n【六】残差判定与逐条解释')
    if not bad:
        print('  六图全部 |Δ线框| ≤ %.2fmm —— 同比核验按页宽基收敛。' % DELTA_OK)
    else:
        print('  按页宽基：五图 |Δ线框| ≤ %.2fmm，超限 %d 图（逐条归因如下，未调任何参数）：'
              % (DELTA_OK, len(bad)))
    for d in bad:
        s = d['src']
        kp = s['k']
        NB_件 = d['boxmm'] / s['rx']
        print('  UNCONVERGED %-9s Δ线框 %+5.2f/%+5.2f｜k(素材页宽基)=%.4f 而实测缩放 rx=%.4f/ry=%.4f'
              '｜片段 bbox 锁定：%s' % (d['tag'], s['dWw'], s['dWh'], kp, s['rx'], s['ry'],
                                        '%.2f×%.2f' % s['lock'] if s['lock'] else '无'))
        if not s['lock']:
            print('    归因（参考系产物，非版式差）：无画布锁定 → \\resizebox 的缩放对象＝"含标签自然外框"，'
                  '而该自然外框由标签字体度量决定。')
            print('    素材页宽 %.2fmm（＝素材自然盒）→ 页宽基 k=%.4f；但件内同锚点用泰古/Termes 排标签，'
                  '其自然盒只有 %.2fmm（＝声明 %.2f ÷ 实测 rx）→ 与素材差 %.2fmm（%.2f%%）。'
                  % (s['pw'], kp, NB_件, d['boxmm'], s['pw'] - NB_件, 100 * (s['pw'] / NB_件 - 1)))
            print('    即件内实际多缩 %.2f%%，恰好等于线框宽向差 %+5.2fmm（占线框宽 %.2f%%）→ '
                  '两方向 Δ 均由参考系错位产生，非图形本身走形：' % (
                      100 * (s['rx'] / kp - 1), s['dWw'], 100 * s['dWw'] / d['ww']))
            print('    各向同性 |rx−ry|=%.5f（≤%.3f 即严格同比无畸变）｜线框/含标形状比之差 件内−素材 '
                  '%+.5f/%+.5f（字体无关不变量）｜含标宽 − 声明置宽 %+.2fmm。' % (
                      abs(s['rx'] - s['ry']), ISO_OK, d['ww'] / d['fw'] - s['sw'] / s['sfw'],
                      d['wh'] / d['fh'] - s['sh'] / s['sfh'], d['fw'] - d['boxmm']))
            print('    旁证：该片段自带注释已登记此效应（figs/g5-fold.tikz 第 4–5 行「本片段无 bbox 锁定，'
                  '自然外框含标签外扩…会被同比缩 ~3.3%%（登记项）」）；本口径实测缩放错位 %.2f%%，'
                  '与登记项同量级 → 口径结论与件内自述相互印证。' % (100 * (s['rx'] / kp - 1)))
            print('    两种收法（本轮不擅自改件）：(a) 给 %s.tikz 补 \\path[use as bounding box] 锁定画布'
                  ' → Δ 可直接收敛；(b) 断言对"无锁定片段"改核不变量：|rx−ry|≤%.3f＋形状比差≤%.3f＋'
                  '含标宽−声明≤±0.30mm。' % (d['frag'], ISO_OK, SHAPE_OK))
    print('\n  逐图余差与不变量（页宽基 k｜Δ线框｜各向同性|rx−ry|｜线框/含标形状比差 件内−素材）：')
    for d in rows:
        s = d['src']
        flag = '' if max(abs(s['dWw']), abs(s['dWh'])) <= DELTA_OK else ' ←超0.50（无锁定，见上）'
        if not flag and max(abs(s['dWw']), abs(s['dWh'])) > 0.05:
            flag = ' （亚 0.1mm 余差：墨级线宽/虚线端点级，不动参数）'
        print('   %-9s k=%.4f Δ%+5.2f/%+5.2f |rx−ry|=%.5f Δ形状=%+.5f/%+.5f%s' % (
            d['tag'], s['k'], s['dWw'], s['dWh'], abs(s['rx'] - s['ry']),
            d['ww'] / d['fw'] - s['sw'] / s['sfw'], d['wh'] / d['fh'] - s['sh'] / s['sfh'], flag))
    print('\n  含标签基 Δ（参考，非门；素材 CM 体 vs 件内泰古/Termes 度量差所致）：' + '  '.join(
        '%s %+5.2f/%+5.2f' % (d['tag'].split()[0], d['src']['dFw'], d['src']['dFh']) for d in rows))
    print('  件内线框 vs 笔画几何并集上界（含线宽外放 %.1fpt＋膨胀 %dpx 的固有正余量）：%s' % (
        REPLAY_PAD, MASK_DIL, '  '.join(
            '%s %+.2f/%+.2f' % (d['tag'].split()[0], d['ww'] - d['src']['geoW'],
                                d['wh'] - d['src']['geoH']) for d in rows)))

    print('\n【七】断言门取值建议（全部由本表实测直读；窗＝实测极值 ± 0.25mm 墨级安全垫，'
          '0.25mm ≈ 600dpi 下 6px，覆盖抗锯齿/虚线端点抖动）')
    PAD = 0.25

    def win(vals, pad=PAD):
        return min(vals) - pad, max(vals) + pad

    ups = [d['upF'] for d in rows]
    dns = [d['dnF'] for d in rows]
    upw = [d['upW'] for d in rows]
    dnw = [d['dnW'] for d in rows]
    devF = [abs(d['devF']) for d in rows]
    devW = [abs(d['devW']) for d in rows]
    lo, hi = win(ups)
    lo2, hi2 = win(upw)
    print('  前距（含标签基·墨级）实测 [%.2f, %.2f] → 建议窗 [%.2f, %.2f]；线框基实测 [%.2f, %.2f] → 窗 [%.2f, %.2f]'
          % (min(ups), max(ups), lo, hi, min(upw), max(upw), lo2, hi2))
    lo, hi = win(dns)
    lo2, hi2 = win(dnw)
    print('  下距（含标签基·墨级）实测 [%.2f, %.2f] → 建议窗 [%.2f, %.2f]；线框基实测 [%.2f, %.2f] → 窗 [%.2f, %.2f]'
          % (min(dns), max(dns), lo, hi, min(dnw), max(dnw), lo2, hi2))
    print('  栏心偏 含标签基 max |%.2f| → 建议窗 ±%.2f；线框基 max |%.2f| → 建议窗 ±%.2f'
          % (max(devF), max(devF) + PAD, max(devW), max(devW) + PAD))
    ok5 = max(max(abs(d['src']['dWw']), abs(d['src']['dWh'])) for d in rows if d['src']['lock'])
    print('  尺寸同比：有 bbox 锁定五图 |Δ线框| 实测 max %.2fmm → 建议门 ≤%.2fmm（DELTA_OK）；'
          '无锁定片段（g5）改核不变量 |rx−ry|≤%.3f＋形状比差≤%.3f＋|含标宽−声明置宽|≤0.30mm'
          % (ok5, DELTA_OK, ISO_OK, SHAPE_OK))
    print('  硬门（与参数无关）：正文相交＝0｜件内簇数＝6｜素材簇数逐图＝1｜标签数件内＝素材（逐图相等）｜'
          '虚线保真率≥0.99（实测 min %.3f）｜含标越声明盒≤0.30mm（实测 max %.2fmm）｜'
          '每图斜长笔≥%d 且簇宽≥15mm 且簇高≥10mm' % (
              min(d['src']['alive'] for d in rows),
              max(d['box'][0] - d['F'].x0 for d in rows) / PT, MINLONG))
    print('  落位门（页,栏）：' + ' '.join('%s=p%dc%d' % (d['tag'].split()[0], d['page'], d['col'])
                                        for d in rows))
    print('  置宽复算（声明置宽 vs 线框宽＋含标签宽）：')
    for d in rows:
        print('   %-9s 置宽 %5.1f｜线框 %5.2f（%.1f%%）｜含标签 %5.2f（%.1f%%）｜'
              '框顶 y %6.2f 框底 y %6.2f' % (
                  d['tag'], d['boxmm'], d['ww'], 100 * d['ww'] / d['boxmm'],
                  d['fw'], 100 * d['fw'] / d['boxmm'], d['F'].y0 / PT, d['F'].y1 / PT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
