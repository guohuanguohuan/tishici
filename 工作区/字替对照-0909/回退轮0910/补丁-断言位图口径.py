# -*- coding: utf-8 -*-
# 补丁脚本：_测v4断言.py 位图口径改造（回退轮0910）。锚点断言失败即中止不落盘。
import io, sys

P = 'C:/提示词/工作区/字替对照-0909/variantF/_测v4断言.py'
lines = io.open(P, encoding='utf-8').read().split('\n')  # 0-based; 行N = lines[N-1]

def anchor(n, sub):
    if sub not in lines[n - 1]:
        sys.exit(f'锚点失配 行{n}: 期望包含 {sub!r}，实为 {lines[n-1][:60]!r}')

# ---- 锚点校验（行号取自 2418 行版） ----
anchor(205, '实测（600dpi 全墨）另见 ⑱-2')
anchor(283, 'def in_fig(')
anchor(286, 'vec_clusters(pno)')
anchor(289, '片G 0910 六图下置·共用台账')
anchor(305, 'FIGS = [(f, p, c, r, n) for')
anchor(341, 'if not grays <= {0x40,')
anchor(343, "check('③灰档全集恰")
anchor(347, '矢量化后成为页面描边色')
anchor(692, '⑱ 六图下置·tex 形制门')
anchor(728, 'g6 0.22 不动')
anchor(736, '详见权威实测.py【甲】【五】')
anchor(1069, '⑱-2 六图线框几何门')
anchor(1165, '两表任一未同步即 k／Δ 全错')
anchor(1167, '⑱-3 下置独立行·图旁零文字门')
anchor(1196, '无新增常数')
anchor(1542, 'N6 六图台账')
anchor(1556, '本轮复验落位六图')
anchor(2247, '⑮ 五例1图归属')
anchor(2273, '口径加强（旧式可容五图错挂而集合仍等）')
anchor(2295, '矢量图内水平棱')
anchor(69, '三0 计数同基线')

NEW_LEDGER = r'''# ---- 回退轮0910 六图位图回退·共用台账（⑱/⑱-2/⑱-3/N6/⑮ 五门唯一图源；片G 矢量簇台账口径随图源回退作废） ----
# 图源：AI TikZ 矢量重绘→原 Word 位图（media/media/*.png，用户 0910 二次令「禁画三维图——AI 画过的一律不要」）。
# PDF 内图＝raster 对象——pymupdf get_image_info(xrefs=True) 取矩形，并以原生像素尺寸与片段互证（FIG_PX）。
# FIG_W＝body.tex 图行阅读序＋tex 声明置宽（反解三值表取用宽：字母标签像素高→显示 2.65mm 反解、
#   上限 84.0mm∧150dpi 自然尺寸；三值表见 回退轮0910/简报.md）；
# FIG_AT＝实测落位（页,栏）逐图钉——g2 由旧 p4c1 移 p3c2（栏末图，[分析]起文字流 p4c1），余五图未位移。
# 下置图行各自成段，阅读序＝（页,栏,y 顶）排序，与图行序严格一致（此式自片G 起成立，位图回退后仍成立）。
FIG_W = [('g6-triple', '84.0mm'), ('g1-prism', '28.8mm'), ('g2-cubeE', '32.7mm'),
         ('g3-cube6', '54.1mm'), ('g4-dihedral', '47.5mm'), ('g5-fold', '42.5mm')]
BOX_MM = {f: float(w[:-2]) for f, w in FIG_W}
FIG_PX = {'g6-triple': (1408, 374), 'g1-prism': (691, 1159), 'g2-cubeE': (764, 764),
          'g3-cube6': (521, 496), 'g4-dihedral': (788, 424), 'g5-fold': (1798, 1350)}
FIG_PNG = {'g6-triple': 'media/media/sub3_B_4.png', 'g1-prism': 'media/media/image1.png',
           'g2-cubeE': 'media/media/image2.png', 'g3-cube6': 'media/media/image3.png',
           'g4-dihedral': 'media/media/image4.png', 'g5-fold': 'media/media/image5.png'}
FIG_AT = {'g6-triple': (2, 2), 'g1-prism': (3, 2), 'g2-cubeE': (3, 2),
          'g3-cube6': (5, 1), 'g4-dihedral': (6, 1), 'g5-fold': (6, 2)}
FIG_ROWS = []
for _pno in range(1, n_pages + 1):
    for _info in doc[_pno - 1].get_image_info(xrefs=True):
        _r = pymupdf.Rect(_info['bbox'])
        FIG_ROWS.append((_pno, 1 if (_r.x0 + _r.x1) / 2 < MID else 2, _r.y0, _r, _info))
FIG_ROWS.sort(key=lambda z: (z[0], z[1], z[2]))
FIGS, FIG_PXBAD = [], []
for (f, _w), (_p, _c, _y, _r, _info) in zip(FIG_W, FIG_ROWS):
    if FIG_PX[f] != (_info['width'], _info['height']):
        FIG_PXBAD.append(f + '≠' + str(_info['width']) + 'x' + str(_info['height']) + 'px')
    FIGS.append((f, _p, _c, _r, _info))'''

NEW_INFIG = r'''def in_fig(pno, x0, y0, x1, y1, pad=1.0):
    """线段/小框是否落在某位图图矩形内（含 pad pt 容差）——供印答盒线门排除图区墨（防御保留）。
    回退轮0910：图源回位图后矢量层不再有图内棱，判据由矢量簇改锚共用台账 FIG_ROWS（位图矩形）。"""
    return any(p == pno and g.x0 - pad <= x0 and x1 <= g.x1 + pad and g.y0 - pad <= y0 and y1 <= g.y1 + pad
               for p, _c, _y, g, _info in FIG_ROWS)'''

NOTE_VEC = r'''# 【回退轮0910】六图已回位图——本口径（矢量墨聚簇）无图可聚：vec_clusters/_diag_rects 保留停用（备查）；
#   in_fig 改锚位图矩形台账（见下），矢量簇内核 measure_fig 族保留停用见「权威线框口径内核」节注。'''

NEW_GRAY = r'''    if not grays <= {0x4C, 0x4D, 0x77, 0x7A, 0xBD, 0xDD}:'''

NEW_GRAY_CHECK = r'''check('③灰档全集恰{76,77,119,122,189,221}（回退轮位图六档）且逐页⊆白名单', gray_ok and grays_all == {0x4C, 0x4D, 0x77, 0x7A, 0xBD, 0xDD},
      f'全集{sorted(grays_all)}；{" ".join(gray_detail)}')
reg('③ 回退轮0910 灰档回档（7档→6档）',
    '片G 0910 增第七档 cubegray 0x40(64)＝g3-cube6 矢量灰棱上浮为页面描边色；回退轮六图回用原位图后，'
    '灰棱回到像素内、不入矢量色板——白名单回位图时代 6 档 {76,77,119,122,189,221}（0x40 退役）。'
    'qp-blocks.tex 之 \\definecolor{cubegray} 定义保留未动（片段不再 \\input，不入页）。')'''

NEW_18 = r'''# ---- ⑱ 六图下置·tex 形制门（回退轮0910：图源回用原位图，片G 矢量形制口径作废） ----
# 旧形（片G 0910）：`\bindp \par\vspace{1.9mm}\penalty10000\noindent\makebox[\linewidth][c]{\resizebox{置宽}{!}
#      {\input{figs/片段.tikz}}}\par\vspace{-1.0mm}\penalty10000` ×6——用户 0910 二次令「禁画三维图；AI 画过的一律不要」退役。
# 新形（回退轮唯一口径）：下置骨架六行逐字节不变，仅图盒改位图——
#      `\bindp \par\vspace{1.9mm}\penalty10000\noindent\makebox[\linewidth][c]{\includegraphics[width=置宽mm]
#       {media/media/图.png}}\par\vspace{-1.0mm}\penalty10000`
#      置宽逐图钉死（反解三值表取用宽，见共用台账注与 回退轮0910/简报.md）。
FIG_LINE = re.compile(r'\\bindp \\par\\vspace\{1\.9mm\}\\penalty10000\\noindent\\makebox\[\\linewidth\]\[c\]'
                      r'\{\\includegraphics\[width=([^{}]+)mm\]\{(media/media/[A-Za-z0-9_]+\.png)\]\}'
                      r'\\par\\vspace\{-1\.0mm\}\\penalty10000')
PNG2FRAG = {v: k for k, v in FIG_PNG.items()}
fig_row = [(PNG2FRAG.get(m.group(2), m.group(2)), m.group(1) + 'mm') for m in FIG_LINE.finditer(body)]
n_mini = body.count(r'\begin{minipage}')
n_side = len(re.findall(r'\\begin\{minipage\}\[t\]\{[\d.]+mm\}\\raggedright', body))
n_rb = len(re.findall(r'\\raisebox\{', body))
n_rs = len(re.findall(r'\\resizebox\{', body))
n_fin = body.count(r'\input{figs/')
n_gfx = len(re.findall(r'\\includegraphics\[width=', body))
check('⑱ 六图下置 body.tex 形制（位图图行 ×6 同式·置宽与图路径逐图钉·figs入件归零·并排四要素归零）',
      fig_row == FIG_W and n_gfx == 6 and n_fin == 0 and n_rs == 0 and n_mini == 0 and n_side == 0 and n_rb == 0,
      f'图行 {len(fig_row)}/6｜' + ' '.join(f + '=' + w for f, w in fig_row) +
      f'｜位图 {n_gfx}/6 figs入件 {n_fin}/0 resizebox {n_rs}/0 minipage {n_mini}/0 side {n_side}/0 raisebox {n_rb}/0')
reg('⑱ 口径登记（回退轮0910 图源回退·片G→位图）',
    r'片G 0910 旧门值：图行＝\resizebox{宽}{!}{\input{figs/片段.tikz}} ×6（figs 入件 6／位图 0／\resizebox 6）——'
    '本轮六图全数回退原位图，门改核新形制：\includegraphics[width=宽mm]{media/media/图} ×6、'
    '\input{figs/ 归零、\resizebox 归零（位图按声明宽直排）、并排四要素（minipage/side/raisebox/胶）继续归零。'
    '下置骨架（\bindp＋\par\vspace{1.9mm}＋penalty10000＋\noindent\makebox[\linewidth][c]＋\par\vspace{-1.0mm}＋penalty10000）逐字节承片G。')
reg('⑱ 回退轮0910 置宽档改钉（反解三值表·片G 旧→新·逐条）',
    '六图置宽按「位图原生像素中字母标签高→显示标签高 2.65mm(≈7.5pt) 反解；校验上限 84.0mm∧150dpi 自然尺寸」重钉'
    '（量法＝回退轮0910/量标签高.py 连通域主簇中位）：'
    'g6-triple 80.8→84.0mm（反解 133.26 被上限 84.00 截断；标签主簇中位 28px/位图 1408px）；'
    'g1-prism 41.1→28.8mm（反解 28.84；63.5px/691px）；g2-cubeE 42.0→32.7mm（32.65；62px/764px）；'
    'g3-cube6 36.3→54.1mm（54.14；25.5px/521px）；g4-dihedral 30.5→47.5mm（47.46；44px/788px）；'
    'g5-fold 28.2→42.5mm（42.54；112px/1798px）。缩档轮 0910 旧档 80.8/41.1/42.0/36.3/30.5/28.2mm 逐条作废。')'''

NOTE_KERNEL = r'''# 【回退轮0910 停用注】六图已回用原位图——本内核（矢量笔画重放/线框 W/标签认领/measure_fig/fig_lock）
#   判据全部建立在「矢量笔画真墨重放」上，对位图图源原理性不适用：保留代码备查、不再执行
#   （原 ⑱-2 执行块已替换为下方「六图位图几何门」）。其中 text_lines/is_body/ink_mask/sub_ink/_np
#   等基础定义仍被位图 ⑱-2/⑱-3 门沿用。'''

NEW_182 = r'''# ---- ⑱-2 六图位图几何门（回退轮0910 图源回退后按位图口径重建；旧线框门保留停用，见内核节注） ----
# 旧线框门值（片G 0910·缩档轮复标后，逐条作废登记）：前距含标 [1.99,4.44]／下距含标 [2.04,3.85]／
#   栏心偏线框基 ±1.45／Δ线框 ≤0.50（g5 无锁定改不变量 |rx−ry|≤0.005 等三项）／越声明盒 ≤0.30／
#   标签数件内==素材／虚线保真率 ≥0.99／正文相交=0／落位逐图。
# 新门＝位图口径（先实测再定窗，窗＝实测极值±0.25mm 墨级安全垫；实测源＝回退轮0910/实测位图门值.txt）：
#   落位（页,栏）逐图钉 FIG_AT；置宽 |PDF 矩形宽−tex 声明宽|≤0.5mm（任务书规定窗；实测 0.00）；
#   居中＝栏心偏 |·|≤0.25（实测 max 0.005mm，makebox[c] 恒居中）；
#   前距 墨级 ∈[2.04,3.73]（实测 [2.29(g1),3.48(g4)]）；下距 墨级 ∈[2.06,3.89]（实测 [2.31(g1),3.64(g5)]；
#     g2 为栏末图（下无同栏正文行、[分析]流 p4c1）→ 下距免检登记）；
#   零侵入（含标签·墨级）＝正文行 600dpi 真墨 ∩（图矩形外扩 0.5mm）==0（位图标签在像素内，矩形即含标签框）。
# 图真墨矩形 ir＝位图原生墨 bbox（PIL <128）按 PDF 矩形同比映射——前距/下距以 ir 为图基（＝旧「含标基」等价物）。
PAD05 = 0.5 * PT


def line_ink600(page, r):
    """区域 600dpi 真墨 bbox（pt 绝对坐标）；无墨返回 None。"""
    pm = page.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=r)
    a = _np.frombuffer(pm.samples, dtype=_np.uint8).reshape(pm.height, pm.width)
    m = a < 128
    if not m.any():
        return None
    ys, xs = _np.nonzero(m)
    sc = 72.0 / 600
    return pymupdf.Rect(r.x0 + xs.min() * sc, r.y0 + ys.min() * sc,
                        r.x0 + (xs.max() + 1) * sc, r.y0 + (ys.max() + 1) * sc)


from PIL import Image as _PILImage
INK_NAT = {}
for _f, (_px, _py) in FIG_PX.items():
    _im = _PILImage.open(os.path.join(BASE, FIG_PNG[_f]))
    if _im.mode in ('RGBA', 'LA', 'P'):
        _bg = _PILImage.new('RGBA', _im.size, (255, 255, 255, 255))
        _im = _PILImage.alpha_composite(_bg, _im.convert('RGBA'))
    _a = _np.asarray(_im.convert('L')) < 128
    _ys, _xs = _np.nonzero(_a)
    INK_NAT[_f] = (_xs.min() / _px, _ys.min() / _py, (_xs.max() + 1) / _px, (_ys.max() + 1) / _py)

K18, K18P = [], {}
k18_ok, k18_bits = True, []
if len(FIGS) != 6:
    k18_ok = False
    k18_bits.append(f'位图 {len(FIGS)}/6')
if FIG_PXBAD:
    k18_ok = False
    k18_bits.append('图源互证失败 ' + ','.join(FIG_PXBAD))
for frag, pno, col, r, info in FIGS:
    box = BOX_MM[frag]
    cl = COLL[col - 1]
    fx0, fy0, fx1, fy1 = INK_NAT[frag]
    ir = pymupdf.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height,
                      r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)
    pg = doc[pno - 1]
    body_ls = [L for L in text_lines(pg) if is_body(L)
               and cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= cl + COLW + 2]
    for L in body_ls:
        L['ink'] = line_ink600(pg, L['r']) or L['r']
    above = [L for L in body_ls if L['ink'].y1 <= ir.y0 + 0.3]
    below = [L for L in body_ls if L['ink'].y0 >= ir.y1 - 0.3]
    up = max(above, key=lambda z: z['ink'].y1) if above else None
    dn = min(below, key=lambda z: z['ink'].y0) if below else None
    gap_u = (ir.y0 - up['ink'].y1) / PT if up else None
    gap_d = (dn['ink'].y0 - ir.y1) / PT if dn else None
    colend = dn is None and ir.y1 > BODY_BOT - 2 * PT   # 栏末图（下邻流次栏）
    dev = ((r.x0 + r.x1) / 2 - (cl + COLW / 2)) / PT
    wdev = r.width / PT - box
    infl = pymupdf.Rect(r.x0 - PAD05, r.y0 - PAD05, r.x1 + PAD05, r.y1 + PAD05)
    hits = [L for L in body_ls if L['r'].intersects(infl) or L['ink'].intersects(infl)]
    oks = [('落位', (pno, col) == FIG_AT[frag]),
           ('置宽', abs(wdev) <= 0.5),
           ('栏心偏', abs(dev) <= 0.25),
           ('前距', gap_u is not None and 2.04 <= gap_u <= 3.73),
           ('下距', colend or (gap_d is not None and 2.06 <= gap_d <= 3.89)),
           ('零侵入', len(hits) == 0)]
    bad = [n for n, o in oks if not o]
    if bad:
        k18_ok = False
    K18.append(dict(frag=frag, pno=pno, col=col, r=r, ir=ir, up=up, dn=dn, colend=colend,
                    gap_u=gap_u, gap_d=gap_d, dev=dev, wdev=wdev, nhit=len(hits), bad=bad))
    K18P[frag] = K18[-1]
    k18_bits.append('{}@p{}c{} 宽{:+.2f} 偏{:+.2f} 前{} 下{} 侵入{} 墨{:.1f}x{:.1f}'.format(
        frag, pno, col, wdev, dev,
        '—' if gap_u is None else '{:.2f}'.format(gap_u),
        '栏末免' if colend else ('—' if gap_d is None else '{:.2f}'.format(gap_d)),
        len(hits), ir.width / PT, ir.height / PT)
        + ('' if not bad else ' ✗' + ','.join(bad)))
check('⑱-2 六图位图几何（落位钉·置宽±0.5·栏心偏±0.25·前距2.04–3.73·下距2.06–3.89(g2栏末免)·零侵入=0）',
      k18_ok and len(K18) == 6 and not FIG_PXBAD, '；'.join(k18_bits))
reg('⑱-2 口径登记（回退轮0910 线框→位图·旧→新·逐条）',
    '①前距 含标基 [1.99,4.44]→图真墨基 [2.04,3.73]——实测 [2.29(g1),2.99(g6),2.74(g2),3.05(g3),3.48(g4),2.88(g5)]±0.25垫；'
    '②下距 [2.04,3.85]→[2.06,3.89]——实测 [3.19(g6),2.31(g1),3.43(g3),3.30(g4),3.64(g5)]±0.25垫；'
    '③栏心偏 线框基±1.45→矩形基±0.25（实测 max 0.005）；④置宽±0.5mm 新立（实测偏差 0.00）；'
    '⑤Δ线框/越盒/标签数==素材/虚线保真率/正文相交——判据依矢量重放、位图无对象→作废，'
    '零侵入以墨级重建（正文行 600dpi 真墨 ∩ 矩形外扩 0.5mm，实测六图 0）；'
    '⑥落位钉 FIG_AT——g2 旧 p4c1→新 p3c2（置宽 42.0→32.7mm 缩小后 p3 右栏容图至栏末，[分析]起文字流 p4c1；'
    '图墨底距版心下际 3.5pt）＝栏末图，下距/下邻免检、前距/居中/零侵入照常。')'''

NEW_183 = r'''# ---- ⑱-3 下置独立行·图旁零文字门（回退轮0910 按位图矩形口径重建；片G 含标框 F 口径随内核停用） ----
# 门两项（复用 ⑱-2 读数 K18，不重算）：
# ①图旁零文字＝同栏正文行与位图矩形垂直重叠 >1pt 者 ==0（并排残留直接检验；位图标签在像素内，
#   矩形即含标签框——旧「含标框 F」等价物）；②上下邻行在场＝上邻必须有；下邻须有、或为「栏末图」
#   （K18.colend：图墨底贴版心下际 ≤2mm 且下无同栏正文行，文字流次栏——g2 一处，登记）。
k18_3_ok, k18_3_bits = True, []
for _r in K18:
    _pg = doc[_r['pno'] - 1]
    _cl = COLL[_r['col'] - 1]
    _rows = [L for L in text_lines(_pg)
             if _cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= _cl + COLW + 2 and is_body(L)]
    _side = [L for L in _rows
             if min(L['r'].y1, _r['r'].y1) - max(L['r'].y0, _r['r'].y0) > 1 * PT]
    ok1 = not _side
    ok2 = _r['up'] is not None and (_r['dn'] is not None or _r['colend'])
    if not (ok1 and ok2):
        k18_3_ok = False
    k18_3_bits.append('{}：旁文字{}／上邻{}／下邻{}'.format(
        _r['frag'], len(_side), '有' if _r['up'] else '无',
        '栏末免' if _r['colend'] else ('有' if _r['dn'] else '无'))
        + ('' if ok1 and ok2 else ' ✗'))
check('⑱-3 下置独立行·图旁零文字（旁行=0）＋上邻在场＋下邻在场或栏末（×6）', k18_3_ok and len(K18) == 6,
      '；'.join(k18_3_bits))
reg('⑱-3 口径登记（回退轮0910 重建·旧→新）',
    '片G 旧门：①正文行与含标框 F（线框 W＋标签文本层认领）垂直重叠>1pt==0；②up/dn 两邻皆必须有——'
    'F 由矢量内核产出，位图不适用。新门：①同栏正文行与位图矩形垂直重叠>1pt==0（实测六图 0）；'
    '②上邻必须有＋下邻有或栏末（g2@p3c2 一处免检）。零文字与侵入判据同源不同窗：本条管「下置形态」，'
    '⑱-2 零侵入管「墨距外扩」。')'''

NEW_N6 = r'''# ---- N6 六图台账（回退轮0910 位图口径重建；片G 矢量簇台账作废） ----
# 只管「六图在场＋图源互证＋阅读序＋落位（页,栏）逐图钉」；置宽由 ⑱ tex 门核、几何由 ⑱-2 位图门核。
check('N6 六图台账（位图恰6＋原生px尺寸片段互证＋阅读序＋落位逐图钉）',
      len(FIG_ROWS) == 6 and len(FIGS) == 6 and not FIG_PXBAD and
      [(f, p, c) for f, p, c, _r, _i in FIGS] == [(f,) + FIG_AT[f] for f, _w in FIG_W],
      '位图 ' + str(len(FIG_ROWS)) + '/6；' + '；'.join(
          f + '@p' + str(p) + 'c' + str(c) + ' ' + str(i['width']) + 'x' + str(i['height']) + 'px'
          for f, p, c, _r, i in FIGS))
reg('N6 口径登记（回退轮0910 旧→新）',
    '片G 旧门：矢量簇恰 6（斜长笔聚簇）＋落位==FIG_AT（g6@p2c2／g1@p3c2／g2@p4c1／g3@p5c1／g4@p6c1／g5@p6c2）。'
    '新门：PDF raster 对象恰 6、逐图原生像素尺寸（FIG_PX）与片段一对一互证、阅读序（页,栏,y）与 FIG_W 一致、'
    '落位逐图钉——g2 p4c1→p3c2（栏末图，缩图后回流），余五图未位移；'
    '置宽档＝84.0/28.8/32.7/54.1/47.5/42.5mm（片G 旧档 80.8/41.1/42.0/36.3/30.5/28.2mm 作废）。')'''

NEW_15 = r'''# ---- ⑮ 五例1图归属＝探二/三/六/八/九（回退轮0910 位图台账口径；片G 矢量簇台账作废） ----
# F 片A 0909 适配：归属键＝阅读序（页, 栏, y）——旧键（页, y）在同 y 双栏标题（p5 六/七 同 y 17.5）
# 与跨栏流（p6 九标题在左栏、其图在右栏顶）两处误归属（实测旧：{七,三,二,八}）。
# 片G 0910 适配：三联图旧由「居中独立」判据排除，今六图皆居中独立——改由片段名 g6-triple（条目3 投影图，非探究点图）排除。
# 回退轮0910 适配：取图键由矢量簇台账改位图矩形台账（共用台账 FIGS 元组形制不变，归属算法零改动）。
tjd_events = []   # (pno, col, y, 序) — ◆探究点行（col：0 左栏／1 右栏）
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('◆探究点'):
            tjd_events.append((pno, 0 if bb[0] < MID else 1, bb[1], t[4]))
ATT_WANT = [('g1-prism', '二'), ('g2-cubeE', '三'), ('g3-cube6', '六'),
            ('g4-dihedral', '八'), ('g5-fold', '九')]
side_att = {}
for frag, pno, col, r, _info in FIGS:
    if frag == 'g6-triple':
        continue
    prev = [ev for ev in tjd_events if (ev[0], ev[1], ev[2]) <= (pno, col - 1, r.y0 + 2)]
    if prev:
        side_att[frag] = max(prev, key=lambda e: (e[0], e[1], e[2]))[3]
check('⑮ 五例1图归属＝探二/三/六/八/九（回退轮：位图矩形台账逐图一对一归属）',
      len(FIGS) == 6 and [side_att.get(f) for f, _w in ATT_WANT] == [w for _f, w in ATT_WANT],
      '归属 ' + ' '.join(f + '→' + side_att.get(f, '未属') for f, _w in ATT_WANT))
reg('⑮ 口径登记（回退轮0910 位图台账·旧→新）',
    '片G 旧门：共用台账 FIGS（矢量簇）逐片段一对一核 g1→二／g2→三／g3→六／g4→八／g5→九。'
    '新门：FIGS 改位图矩形台账（元组形制同），归属算法与期望映射不变——g2 落位 p4c1→p3c2 后，'
    '其前最近 ◆探究点 仍为「三」（p3c2 y610），五图归属实测 {二,三,六,八,九} 逐图不变；'
    '三联 g6 系条目3 图不入归属（口径承片G）。')'''

NEW_113_NOTE = r'''                continue   # 回退轮0910：图内水平棱随矢量化退场（位图无矢量线）——in_fig 改锚位图矩形，防御保留'''

DOC_NOTE = r'''qp-layout \relpenalty 10000→500、\emergencystretch 2em→1em（#41 断点恢复＋弹性收紧，三0 计数同基线）
  回退轮0910（图源回退轮，用户二次令「禁画三维图——AI 重绘六图全部退役、回用原图位图」）：
  ⑱ tex 形制改核 includegraphics 位图图行 ×6（width=宽mm 直排；figs 入件归零、resizebox 归零，下置骨架逐字节承片G）；
  ⑱-2／⑱-3／N6／⑮ 改位图口径（get_image_info 矩形＋PIL 原生墨映射＋600dpi 墨级前距/下距/零侵入＋落位逐图钉）；
  旧矢量线框内核保留停用（图源回退后不适用）；③ 灰档回位图时代 6 档（0x40 cubegray 退役）；
  置宽反解三值表见 回退轮0910/简报.md（g6 84.0／g1 28.8／g2 32.7／g3 54.1／g4 47.5／g5 42.5mm）。"""'''

# ---- 自底向上替换（行号闭区间，1-based） ----
def splice(a, b, new):
    lines[a - 1:b] = new.split('\n')

splice(2295, 2295, NEW_113_NOTE)
splice(2247, 2273, NEW_15)
splice(1542, 1556, NEW_N6)
splice(1167, 1196, NEW_183)
splice(1069, 1165, NEW_182)
lines.insert(736, NOTE_KERNEL)          # 行736 后插注（insert 在 0-based 736 = 行737 前）
splice(692, 728, NEW_18)
splice(343, 347, NEW_GRAY_CHECK)
splice(341, 341, NEW_GRAY)
splice(289, 305, NEW_LEDGER)
splice(283, 286, NEW_INFIG)
lines.insert(205, NOTE_VEC)             # 行205 后
splice(69, 69, DOC_NOTE)

out = '\n'.join(lines)
io.open(P, 'w', encoding='utf-8').write(out)
print('补丁完成，新行数', out.count('\n') + 1)
