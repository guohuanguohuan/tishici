# -*- coding: utf-8 -*-
r"""表格重构器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·②-B（十四表重构）

口径（主脑《T8_十四表裁决.md》＋底稿《T8_十五表裁决底稿.md》）：14 张栏内表（7 设计×2 副本）
全部实测为双栏正文区栏内表（tblW 4650dxa=232.5pt≤栏宽 244.5pt），通栏无门、维持无门，一律重构。
内容零增删为硬约束（仅允许形态搬移、类目标签转表题/共用叙述句；裁决授权的合并/拆分复制单独登记）。

七种形态手术（每设计两副本同改，签名识别，非硬编码表序——幂等友好）：
  A 空间向量线性运算(8×4) → 拆两表：A1「空间向量的线性运算」3列(运算|代数表示|几何意义)×5行
     （加法/减法/数乘λ>0/λ<0/λ=0，2图纵并共享随格迁移）＋A2「运算律」2列(运算律|公式)×3行；类目列转两表表题。
  B 方程组解↔位置关系(3×4) → 转置：4行×3列，原首列公式行转表头，按§③重分列宽。
  C 直线与圆位置关系(4×5) → 转置并合列：3列×4行(位置关系|公共点个数|判定方法)，判定格内几何/代数两行公式并存
     （原共享描述行随三关系行复制，裁决授权形态，单独登记）。
  D 圆与圆位置关系(3×6) → 转置：6行×3列(位置关系|图示|d与R、r的关系)，5图转图示列纵放。
  E 双曲线几何性质(9×4) → 收拢类目列：3列(条目|焦点在x轴上|焦点在y轴上)×9行(表头+8)，取消空类目首格与「性质」
     分组列（登记删除），43字「轴」行/对称性/离心率仍跨2格。
  F 抛物线标准方程(5×4) → 合列：3列×5行(图形|标准方程|焦点·准线)，焦点坐标+准线方程并一列格内两行，4图原位。
  G 抛物线几何性质(7×5) → 按开口方向拆两表：G1(条目|y²=2px|y²=-2px)、G2(条目|x²=2py|x²=-2py)各3列；
     首行「p的几何意义」跨格说明提为两表共用叙述句（登记迁移，冗余标签合并）；顶点/离心率(跨4)两表各存一份（登记复制）。

硬要求落地：①内容零增删断言（w:t+m:t 字符多重集、oMath 元素数、drawing 元素数逐项前后对比，
  裁决授权的复制/删除/迁移逐条登记，actual==expected 方过）；②gridSpan/vMerge 正确重映射；
  ③17 张单元格内嵌图随格迁移（deepcopy 原 tc，关系 ID r:embed 原样保留）；④m:oMath 公式原样搬运；
  ⑤tblGrid 重写＋按§③内容感知重分列宽（表宽维持 4650dxa）；⑥G 叙述句、A 两表表题用该件正文常规段落样式落地；
  ⑦幂等（签名匹配＋网格列>3 双闸；重构后列≤3 或签名不再匹配→0 改写）；⑧--dry-run／逐表计数断言／--report 落盘／.bak_ 备份。
模式：默认执行（留 .bak_表格重构，已存在不覆盖）；--dry-run 出逐表命中与形态报告不落盘。
用法:
  python 工具/表格重构器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time, itertools
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from copy import deepcopy
from collections import Counter
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)
def mt(t): return '{%s}%s' % (M, t)
def wpt(t): return '{%s}%s' % (WP, t)

TOTAL_W = 4650
CELL_PAD = 240          # tblCellMar 左右 120*2


# ============ 文本快照与守恒断言 ============
def norm(s):
    return re.sub(r'\s+', '', s)


def wtext(el):
    return ''.join(t.text or '' for t in el.iter(q('t')))


def mtext(el):
    return ''.join(t.text or '' for t in el.iter(mt('t')))


def n_omath(el):
    return len(el.findall('.//' + mt('oMath'))) + len(el.findall('.//' + mt('oMathPara')))


def n_draw(el):
    return len(el.findall('.//' + q('drawing')))


def snap(el):
    return {'w': Counter(norm(wtext(el))), 'm': Counter(norm(mtext(el))),
            'nom': n_omath(el), 'ndr': n_draw(el)}


def snap_add(a, b):
    return {'w': a['w'] + b['w'], 'm': a['m'] + b['m'], 'nom': a['nom'] + b['nom'], 'ndr': a['ndr'] + b['ndr']}


def snap_sub(a, b):
    return {'w': a['w'] - b['w'], 'm': a['m'] - b['m'], 'nom': a['nom'] - b['nom'], 'ndr': a['ndr'] - b['ndr']}


def snap_zero():
    return {'w': Counter(), 'm': Counter(), 'nom': 0, 'ndr': 0}


def snap_eq(a, b):
    return a['w'] == b['w'] and a['m'] == b['m'] and a['nom'] == b['nom'] and a['ndr'] == b['ndr']


def snap_fmt(a):
    return 'w:%d m:%d oMath:%d 图:%d' % (sum(a['w'].values()), sum(a['m'].values()), a['nom'], a['ndr'])


# ============ §③ 列宽内容感知 ============
def char_w(ch):
    o = ord(ch)
    if o >= 0x2E80:
        return 240          # CJK / 全角，按 12pt
    if ch in ' \u3000':
        return 120
    return 130              # 拉丁字母/数字/标点


def text_w(s):
    return sum(char_w(c) for c in s)


def img_w_dxa(tc):
    mw = 0
    for ext in tc.iter(wpt('extent')):
        try:
            mw = max(mw, round(int(ext.get('cx')) / 914400 * 1440))
        except Exception:
            pass
    return mw


def cell_need(tc):
    need = 0
    for p in tc.findall(q('p')):
        t = ''.join(x.text or '' for x in itertools.chain(p.iter(q('t')), p.iter(mt('t'))))
        need = max(need, text_w(t))
    need = max(need, img_w_dxa(tc))
    return need + CELL_PAD


def alloc_widths(needs, total=TOTAL_W, minw=320):
    """§③内容感知：先满足短列（不折行），余量按封顶需求分给长列；全短则余量按占比外扩。"""
    needs = [max(int(n), minw) for n in needs]
    n = len(needs)
    widths = [0] * n
    idxs = set(range(n))
    remaining = total
    while idxs:
        fair = remaining / len(idxs)
        short = [i for i in idxs if needs[i] <= fair * 1.15]
        if not short:
            break
        for i in short:
            widths[i] = needs[i]
            remaining -= needs[i]
            idxs.discard(i)
    if idxs:
        fair = remaining / len(idxs)
        capped = {i: min(needs[i], int(fair * 3)) for i in idxs}
        s = sum(capped.values())
        for i in idxs:
            widths[i] = int(round(remaining * capped[i] / s)) if s > 0 else remaining // len(idxs)
    elif remaining > 0:
        s = sum(needs)
        for i in range(n):
            widths[i] += int(round(remaining * needs[i] / s)) if s > 0 else remaining // n
    diff = total - sum(widths)
    widths[needs.index(max(needs))] += diff
    return widths


def col_need(cells):
    return max([cell_need(tc) for tc in cells] + [minw_default()])


def minw_default():
    return 320


# ============ 构表原语 ============
def rows_cells(tbl):
    return [tr.findall(q('tc')) for tr in tbl.findall(q('tr'))]


def get_vmerge(tc):
    tcpr = tc.find(q('tcPr'))
    if tcpr is None:
        return None
    v = tcpr.find(q('vMerge'))
    if v is None:
        return None
    return v.get(q('val')) or 'continue'


def rebuild_tc(src_tc, width, gridSpan=None, vMerge=None):
    """deepcopy 源 tc（连同 oMath/drawing/段落格式），仅重设 tcW/gridSpan/vMerge。"""
    tc = deepcopy(src_tc)
    tcpr = tc.find(q('tcPr'))
    if tcpr is None:
        tcpr = etree.Element(q('tcPr'))
        tc.insert(0, tcpr)
    for n in ('tcW', 'gridSpan', 'vMerge'):
        e = tcpr.find(q(n))
        if e is not None:
            tcpr.remove(e)
    tcw = etree.Element(q('tcW'))
    tcw.set(q('w'), str(width))
    tcw.set(q('type'), 'dxa')
    tcpr.insert(0, tcw)
    idx = 1
    if gridSpan and gridSpan > 1:
        gs = etree.Element(q('gridSpan'))
        gs.set(q('val'), str(gridSpan))
        tcpr.insert(idx, gs)
        idx += 1
    if vMerge is not None:
        vm = etree.Element(q('vMerge'))
        if vMerge == 'restart':
            vm.set(q('val'), 'restart')
        tcpr.insert(idx, vm)
    return tc


def tc_with_paras(template_tc, paras, width, gridSpan=None, vMerge=None):
    """以 template_tc 的 tcPr 为骨，内容替换为给定段落列表。"""
    tc = rebuild_tc(template_tc, width, gridSpan, vMerge)
    for p in tc.findall(q('p')):
        tc.remove(p)
    for p in paras:
        tc.append(p)
    return tc


def empty_tc(template_tc, width, gridSpan=None):
    """以 template_tc 的 tcPr 为骨，内容清空（留一空段）。"""
    return tc_with_paras(template_tc, [etree.Element(q('p'))], width, gridSpan=gridSpan)


def merged_tc(base_tc, extra_tcs, width, gridSpan=None):
    """base_tc 内容 + extra_tcs 各段依次追加（用于合列，格内多行）。"""
    tc = rebuild_tc(base_tc, width, gridSpan=gridSpan, vMerge=None)
    for etc in extra_tcs:
        for p in etc.findall(q('p')):
            tc.append(deepcopy(p))
    return tc


def concat_para(p_a, p_b):
    """p_a 段内容 + p_b 段非 pPr 子节点（run/oMath）并入同一段。"""
    p = deepcopy(p_a)
    for child in list(p_b):
        if etree.QName(child).localname != 'pPr':
            p.append(deepcopy(child))
    return p


def make_tr(cells):
    tr = etree.Element(q('tr'))
    for tc in cells:
        tr.append(tc)
    return tr


def make_tbl(tblpr_src, widths, trs):
    tbl = etree.Element(q('tbl'))
    tblpr = deepcopy(tblpr_src)
    tw = tblpr.find(q('tblW'))
    if tw is not None:
        tw.set(q('w'), str(sum(widths)))
        tw.set(q('type'), 'dxa')
    tbl.append(tblpr)
    grid = etree.SubElement(tbl, q('tblGrid'))
    for wd in widths:
        gc = etree.SubElement(grid, q('gridCol'))
        gc.set(q('w'), str(wd))
    for tr in trs:
        tbl.append(tr)
    return tbl


def body_pPr():
    ppr = etree.Element(q('pPr'))
    stg = etree.SubElement(ppr, q('snapToGrid')); stg.set(q('val'), '0')
    sp = etree.SubElement(ppr, q('spacing'))
    sp.set(q('line'), '410'); sp.set(q('lineRule'), 'atLeast'); sp.set(q('before'), '0'); sp.set(q('after'), '0')
    jc = etree.SubElement(ppr, q('jc')); jc.set(q('val'), 'left')
    rpr = etree.SubElement(ppr, q('rPr'))
    sz = etree.SubElement(rpr, q('sz')); sz.set(q('val'), '24')
    szcs = etree.SubElement(rpr, q('szCs')); szcs.set(q('val'), '24')
    return ppr


def body_para_from_cell(src_tc):
    """取源 tc 首段（保 run/oMath），换成正文常规段落 pPr，用作表题/叙述句。"""
    p_src = src_tc.find(q('p'))
    if p_src is None:
        p = etree.Element(q('p'))
    else:
        p = deepcopy(p_src)
        old = p.find(q('pPr'))
        if old is not None:
            p.remove(old)
    p.insert(0, body_pPr())
    return p


# ============ 七种形态手术 ============
# 每个 surgery(src_tbl) -> (new_elements, auth_added, auth_removed, note)
#   new_elements: 替换原表的 body 子元素序列（段落+表）
#   auth_added/auth_removed: snap 列表，裁决授权的复制/删除登记（用于守恒断言）

def surgery_A(src):
    rc = rows_cells(src)
    assert len(rc) == 8 and len(rc[0]) == 4 and len(rc[5]) == 3, 'A 结构不符'
    tblpr = src.find(q('tblPr'))
    added, removed = [], []
    title1 = body_para_from_cell(rc[0][0])   # 空间向量的线性运算
    title2 = body_para_from_cell(rc[5][0])   # 运算律
    # A1: 运算 | 代数表示 | 几何意义 ×5行（保留源 vMerge）
    a1_cells = [[rc[i][1], rc[i][2], rc[i][3]] for i in range(5)]
    w_op = col_need([rc[i][1] for i in range(5)])
    w_alg = col_need([rc[i][2] for i in range(5)])
    w_geo = col_need([rc[i][3] for i in range(5)])
    a1w = alloc_widths([w_op, w_alg, w_geo])
    a1_trs = []
    for r in a1_cells:
        row = [rebuild_tc(r[0], a1w[0], vMerge=get_vmerge(r[0])),
               rebuild_tc(r[1], a1w[1]),
               rebuild_tc(r[2], a1w[2], vMerge=get_vmerge(r[2]))]
        a1_trs.append(make_tr(row))
    A1 = make_tbl(tblpr, a1w, a1_trs)
    # A2: 运算律 | 公式 ×3行（清 gridSpan/vMerge）
    a2_cells = [[rc[i][1], rc[i][2]] for i in range(5, 8)]
    w_name = col_need([rc[i][1] for i in range(5, 8)])
    w_form = col_need([rc[i][2] for i in range(5, 8)])
    a2w = alloc_widths([w_name, w_form])
    a2_trs = []
    for r in a2_cells:
        row = [rebuild_tc(r[0], a2w[0]), rebuild_tc(r[1], a2w[1])]
        a2_trs.append(make_tr(row))
    A2 = make_tbl(tblpr, a2w, a2_trs)
    note = '拆两表：A1[空间向量的线性运算]3列×5行(图%d) + A2[运算律]2列×3行；类目列转两表表题' % n_draw(A1)
    return [title1, A1, title2, A2], added, removed, note


def surgery_B(src):
    rc = rows_cells(src)
    assert len(rc) == 3 and len(rc[0]) == 4, 'B 结构不符'
    tblpr = src.find(q('tblPr'))
    # 转置：new[i][j] = old[j][i]，原首列(old col0)转表头行
    new_trs = []
    col_needs = [0, 0, 0]
    for i in range(4):                       # 新表 4 行（原 4 列）
        row_cells = [rc[j][i] for j in range(3)]   # 新行 i = 原列 i 的三个格
        new_trs.append(row_cells)
    # 列宽：新表 3 列，按各列最长内容
    for cj in range(3):
        col_needs[cj] = col_need([new_trs[ri][cj] for ri in range(4)])
    bw = alloc_widths(col_needs)
    trs = []
    for ri in range(4):
        trs.append(make_tr([rebuild_tc(new_trs[ri][cj], bw[cj]) for cj in range(3)]))
    B = make_tbl(tblpr, bw, trs)
    note = '转置→4行×3列(表头=原首列公式行)；零增删'
    return [B], [], [], note


def surgery_C(src):
    rc = rows_cells(src)
    assert len(rc) == 4 and len(rc[0]) == 4 and len(rc[2]) == 5, 'C 结构不符'
    tblpr = src.find(q('tblPr'))
    added, removed = [], []
    # 源：row0=位置关系(跨2)|相交|相切|相离 ; row1=公共点个数(跨2)|2个|1个|0个
    #     row2=判定方法|几何法desc|d<r|d=r|d>r ; row3=(续)|代数法desc|>0|=0|<0
    hdr = [rc[0][0], rc[1][0], rc[2][0]]          # 位置关系|公共点个数|判定方法
    geom_desc = rc[2][1]                          # 几何法：设圆心到直线的距离（含oMath）
    alg_desc = rc[3][1]                           # 代数法：由消元得到一元二次方程的判别式（含oMath）
    # 描述随三关系行复制（1→3），授权复制登记 +2×each
    added.append(snap(geom_desc)); added.append(snap(geom_desc))
    added.append(snap(alg_desc)); added.append(snap(alg_desc))
    # 新表 3 列 × (表头+3关系行)
    # 列宽：判定方法列最长（desc+关系），先估
    tmpl_desc_para = geom_desc.find(q('p'))
    tmpl_alg_para = alg_desc.find(q('p'))
    # 判定方法格内容 = 几何行 + 代数行
    def judge_cell(j):
        geom_p = concat_para(tmpl_desc_para, rc[2][2 + j].find(q('p')))
        alg_p = concat_para(tmpl_alg_para, rc[3][2 + j].find(q('p')))
        return [geom_p, alg_p]
    # 估算判定列 need（取 j=0）
    jc_tmp = tc_with_paras(rc[0][0], judge_cell(0), 1000)
    need_judge = cell_need(jc_tmp)
    need_rel = col_need([rc[0][0], rc[0][1], rc[0][2], rc[0][3]])      # 位置关系(表头)+相交/相切/相离
    need_cnt = col_need([rc[1][0], rc[1][1], rc[1][2], rc[1][3]])      # 公共点个数(表头)+2/1/0个
    cw = alloc_widths([need_rel, need_cnt, need_judge])
    trs = []
    # 表头行
    trs.append(make_tr([rebuild_tc(hdr[0], cw[0]), rebuild_tc(hdr[1], cw[1]), rebuild_tc(hdr[2], cw[2])]))
    for j in range(3):
        c_rel = rebuild_tc(rc[0][1 + j], cw[0])           # 相交/相切/相离
        c_cnt = rebuild_tc(rc[1][1 + j], cw[1])           # 2个/1个/0个
        c_jdg = tc_with_paras(rc[2][0], judge_cell(j), cw[2])
        trs.append(make_tr([c_rel, c_cnt, c_jdg]))
    C = make_tbl(tblpr, cw, trs)
    note = '转置并合列→3列×4行；判定格内几何/代数两行公式；共享描述随三行复制(+2×2 授权登记)'
    return [C], added, removed, note


def surgery_D(src):
    rc = rows_cells(src)
    assert len(rc) == 3 and len(rc[0]) == 6, 'D 结构不符'
    tblpr = src.find(q('tblPr'))
    # 转置：原3行→新3列；原6列→新6行。new[i][j]=old[j][i]
    new_trs = []
    for i in range(6):                       # 新6行（原6列）
        new_trs.append([rc[j][i] for j in range(3)])
    col_needs = [col_need([new_trs[ri][cj] for ri in range(6)]) for cj in range(3)]
    dw = alloc_widths(col_needs)
    trs = []
    for ri in range(6):
        trs.append(make_tr([rebuild_tc(new_trs[ri][cj], dw[cj]) for cj in range(3)]))
    D = make_tbl(tblpr, dw, trs)
    note = '转置→6行×3列(位置关系|图示|d与R、r关系)；5图转图示列纵放；零增删'
    return [D], [], [], note


def surgery_E(src):
    rc = rows_cells(src)
    assert len(rc) == 9, 'E 结构不符'
    tblpr = src.find(q('tblPr'))
    added, removed = [], []
    # 源9行：row0-2 c0=空(跨2) ; row3-8 c0=性质(跨行)/续
    #        row0: (空跨2)|焦点在x轴上|焦点在y轴上
    #        row1: (空跨2)|x²...|y²...
    #        row2: (空跨2)|图|图
    #        row3: 性质|范围|x值|y值        (4格)
    #        row4: (续)|对称性|(跨2)对称轴...  (3格)
    #        row5: (续)|顶点|x值|y值         (4格)
    #        row6: (续)|轴|(跨2)实轴...      (3格)
    #        row7: (续)|离心率|(跨2)e=c/a    (3格)
    #        row8: (续)|渐近线|x值|y值       (4格)
    # 取消「性质」分组列（登记删除）与空类目首格
    removed.append(snap(rc[3][0]))           # 性质
    # 新表 3 列(条目|x轴|y轴) × 9行
    # 条目列：row0-2=空, row3-8=原col1(范围/对称性/顶点/轴/离心率/渐近线)
    new_rows = []
    # row0 表头
    new_rows.append((rc[0][0], rc[0][1], rc[0][2], None))     # (条目=空跨2源, x, y, span标记)
    new_rows.append((rc[1][0], rc[1][1], rc[1][2], None))
    new_rows.append((rc[2][0], rc[2][1], rc[2][2], None))
    # row3 范围（4格：性质|范围|x|y）→ 条目=范围, x=rc[3][2], y=rc[3][3]
    new_rows.append((rc[3][1], rc[3][2], rc[3][3], None))
    # row4 对称性（3格：续|对称性|(跨2)对称轴）→ 条目=对称性, 内容跨2
    new_rows.append((rc[4][1], rc[4][2], None, 2))
    # row5 顶点（4格）→ 条目=顶点, x, y
    new_rows.append((rc[5][1], rc[5][2], rc[5][3], None))
    # row6 轴（3格：续|轴|(跨2)实轴43字）→ 条目=轴, 内容跨2
    new_rows.append((rc[6][1], rc[6][2], None, 2))
    # row7 离心率（3格）→ 条目=离心率, 内容跨2
    new_rows.append((rc[7][1], rc[7][2], None, 2))
    # row8 渐近线（4格）→ 条目=渐近线, x(oMath), y(oMath)
    new_rows.append((rc[8][1], rc[8][2], rc[8][3], None))
    # 列宽
    need_item = col_need([r[0] for r in new_rows if r[0] is not None])
    need_x = col_need([r[1] for r in new_rows if r[1] is not None])
    need_y = col_need([r[2] for r in new_rows if r[2] is not None])
    ew = alloc_widths([need_item, need_x, need_y])
    trs = []
    for item_c, x_c, y_c, span in new_rows:
        row = [rebuild_tc(item_c, ew[0])]
        if span == 2:
            row.append(rebuild_tc(x_c, ew[1] + ew[2], gridSpan=2))
        else:
            row.append(rebuild_tc(x_c, ew[1]))
            row.append(rebuild_tc(y_c, ew[2]))
        trs.append(make_tr(row))
    E = make_tbl(tblpr, ew, trs)
    note = '收拢类目列→3列×9行(表头+8)；取消空类目首格+「性质」分组列(删除登记)；对称性/轴/离心率跨2'
    return [E], added, removed, note


def surgery_F(src):
    rc = rows_cells(src)
    assert len(rc) == 5 and len(rc[0]) == 4, 'F 结构不符'
    tblpr = src.find(q('tblPr'))
    # 合列：焦点坐标(c2)+准线方程(c3) → 一列格内两行；4图原位
    # 新表 3 列(图形|标准方程|焦点·准线) × 5行(表头+4)
    need_img = col_need([rc[i][0] for i in range(5)])
    need_eq = col_need([rc[i][1] for i in range(5)])
    need_fa = col_need([merged_tc(rc[i][2], [rc[i][3]], 1000) for i in range(5)])
    fw = alloc_widths([need_img, need_eq, need_fa])
    trs = []
    for i in range(5):
        c_img = rebuild_tc(rc[i][0], fw[0])
        c_eq = rebuild_tc(rc[i][1], fw[1])
        c_fa = merged_tc(rc[i][2], [rc[i][3]], fw[2])     # 焦点坐标段 + 准线方程段
        trs.append(make_tr([c_img, c_eq, c_fa]))
    F = make_tbl(tblpr, fw, trs)
    note = '合列→3列×5行(图形|标准方程|焦点·准线)；焦点坐标+准线方程格内两行；4图原位；零增删'
    return [F], [], [], note


def surgery_G(src):
    rc = rows_cells(src)
    assert len(rc) == 7 and len(rc[0]) == 5, 'G 结构不符'
    tblpr = src.find(q('tblPr'))
    added, removed = [], []
    # 源：row0=p的几何意义|y²=2px|y²=-2px|x²=2py|x²=-2py
    #     row1=(续)|(跨4)p的几何意义：焦点F到准线l的距离
    #     row2=图象|图|图|图|图 ; row3=范围|4值 ; row4=对称轴|(跨2)x轴|(跨2)y轴
    #     row5=顶点|(跨4)坐标原点 ; row6=离心率|(跨4)e=1
    # 叙述句：取 row1 跨4说明（内容），冗余「p的几何意义」标签(row0 c0)登记删除
    narrative = body_para_from_cell(rc[1][1])
    removed.append(snap(rc[0][0]))           # 冗余「p的几何意义」标签
    # 顶点(跨4)/离心率(跨4) 两表各存一份 → +1×each 登记复制
    added.append(snap(rc[5][1]))             # 坐标原点
    added.append(snap(rc[6][1]))             # e=1
    # 条目列(图象/范围/对称轴/顶点/离心率)拆表后两表各存一份 → +1×each 登记复制
    for rr in range(2, 7):
        added.append(snap(rc[rr][0]))
    # G1: 条目 | y²=2px(rc[0][1]) | y²=-2px(rc[0][2])
    # G2: 条目 | x²=2py(rc[0][3]) | x²=-2py(rc[0][4])
    # 数据行(5)：图象/范围/对称轴/顶点/离心率
    def build_sub(col_a, col_b):
        # col_a,col_b: 原列索引(1,2)->G1 ; (3,4)->G2
        # 表头行：条目(空，因p意义标签移除)|eq_a|eq_b
        hdr_empty_tpl = rc[0][0]
        hdr = [None, rc[0][col_a], rc[0][col_b]]
        # 图象行 row2：图 col_a, col_b
        img = [rc[2][0], rc[2][col_a], rc[2][col_b]]
        # 范围行 row3
        rng = [rc[3][0], rc[3][col_a], rc[3][col_b]]
        # 对称轴行 row4：条目=对称轴, 内容跨2
        axis_val = rc[4][1] if col_a == 1 else rc[4][2]   # x轴/y轴(跨2)
        axis = [rc[4][0], axis_val]
        # 顶点行 row5：条目=顶点, 内容跨2=坐标原点
        vertex = [rc[5][0], rc[5][1]]
        # 离心率行 row6：条目=离心率, 内容跨2=e=1
        ecc = [rc[6][0], rc[6][1]]
        rows_spec = [
            (hdr, None), (img, None), (rng, None),
            (axis, 2), (vertex, 2), (ecc, 2),
        ]
        # 列宽（跨2行不计入单列 need；空条目用模板骨估）
        need_item = col_need([r[0][0] for r in rows_spec if r[0][0] is not None] + [hdr_empty_tpl])
        need_a = col_need([r[0][1] for r in rows_spec if r[1] is None])
        need_b = col_need([r[0][2] for r in rows_spec if r[1] is None])
        gw = alloc_widths([need_item, need_a, need_b])
        trs = []
        for cells, span in rows_spec:
            item_c = empty_tc(hdr_empty_tpl, gw[0]) if cells[0] is None else rebuild_tc(cells[0], gw[0])
            if span == 2:
                val_c = rebuild_tc(cells[1], gw[1] + gw[2], gridSpan=2)
                trs.append(make_tr([item_c, val_c]))
            else:
                a_c = rebuild_tc(cells[1], gw[1])
                b_c = rebuild_tc(cells[2], gw[2])
                trs.append(make_tr([item_c, a_c, b_c]))
        return make_tbl(tblpr, gw, trs)
    G1 = build_sub(1, 2)
    G2 = build_sub(3, 4)
    # G1、G2 之间垫一空正文段，防 Word COM 将相邻两表合并计数（无文本，不破坏守恒断言）
    sep = etree.Element(q('p'))
    sep.insert(0, body_pPr())
    note = '按开口方向拆两表：G1(y²=2px,-2px)+G2(x²=2py,-2py)各3列；p意义提为共用叙述句(冗余标签删除登记)；条目列+顶点值+离心率值两表各存(+7复制登记)；4图随格'
    return [narrative, G1, sep, G2], added, removed, note


# ============ 签名识别（幂等友好） ============
DESIGNS = [
    ('A', ['空间向量的线性运算', '运算律'], surgery_A),
    ('B', ['方程组的解', '无解'], surgery_B),
    ('C', ['判定方法', '相切'], surgery_C),
    ('D', ['外离', '内含'], surgery_D),
    ('E', ['焦点在x轴上', '渐近线'], surgery_E),
    ('F', ['焦点坐标', '准线方程'], surgery_F),
    ('G', ['p的几何意义', '对称轴'], surgery_G),
]


def grid_cols(tbl):
    g = tbl.find(q('tblGrid'))
    return len(g.findall(q('gridCol'))) if g is not None else 0


def match_design(tbl):
    txt = norm(wtext(tbl))
    if grid_cols(tbl) <= 3:
        return None            # 已重构或本就达标 → 跳过（幂等）
    for code, sigs, fn in DESIGNS:
        if all(s in txt for s in sigs):
            return code, fn
    return None


# ============ 主处理 ============
def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    tbls = list(body.iter(q('tbl')))

    lines = []
    lines.append('## 表格重构器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    if not tbls:
        lines.append('无表格。\n')
        return '\n'.join(lines), 0

    hits = []
    for k, tbl in enumerate(tbls):
        m = match_design(tbl)
        if m:
            hits.append((k, tbl, m[0], m[1]))
    if not hits:
        lines.append('表数 %d｜重构命中 0（无 >3 列目标表，幂等跳过）' % len(tbls))
        lines.append('')
        return '\n'.join(lines), 0

    changed = 0
    for k, tbl, code, fn in hits:
        before = snap(tbl)
        new_els, added, removed, note = fn(tbl)
        # 守恒断言：after(新元素) == before + Σadded - Σremoved
        after = snap_zero()
        for el in new_els:
            after = snap_add(after, snap(el))
        agg_add = snap_zero()
        for s in added:
            agg_add = snap_add(agg_add, s)
        agg_rem = snap_zero()
        for s in removed:
            agg_rem = snap_add(agg_rem, s)
        expect = snap_sub(snap_add(before, agg_add), agg_rem)
        ok = snap_eq(after, expect)
        assert ok, '表%d(%s) 内容守恒断言失败\n  before=%s\n  after =%s\n  expect=%s' % (
            k, code, snap_fmt(before), snap_fmt(after), snap_fmt(expect))
        ncol_new = [grid_cols(t) for t in new_els if t.tag == q('tbl')]
        assert all(c <= 3 for c in ncol_new), '表%d(%s) 重构后列数>3: %s' % (k, code, ncol_new)
        ndraw_b, ndraw_a = before['ndr'], after['ndr']
        assert ndraw_a == ndraw_b, '表%d(%s) 图数变化 %d→%d' % (k, code, ndraw_b, ndraw_a)
        lines.append('  表%d [%s] %d列→%s 图%d→%d %s' % (
            k, code, grid_cols(tbl), ncol_new, ndraw_b, ndraw_a, 'OK' if ok else 'FAIL'))
        lines.append('     %s' % note)
        if added:
            lines.append('     授权复制登记 +%d 处快照' % len(added))
        if removed:
            lines.append('     授权删除/迁移登记 -%d 处快照' % len(removed))
        if not dry:
            for el in new_els:
                tbl.addprevious(el)
            body.remove(tbl)
        changed += 1

    lines.insert(1, '表数 %d｜重构命中 %d 张（%s）%s' % (
        len(tbls), changed, '、'.join(c for _, _, c, _ in hits), '（dry-run 预演）' if dry else ''))
    lines.append('')

    if not dry and changed:
        import shutil
        bak = path + '.bak_表格重构'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.tRtmp'
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        for kk in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)
    return '\n'.join(lines), changed


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/表格重构器.py <docx...> [--dry-run] [--report r.md]'
    out = []
    tot = 0
    for path in argv:
        r, n = process(path, dry)
        tot += n
        out.append(r)
        print(r)
    print('=== 合计重构命中 %d 张 ===' % tot)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n=== 合计重构命中 %d 张 ===\n' % tot)


if __name__ == '__main__':
    main()
