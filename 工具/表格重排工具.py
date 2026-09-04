# -*- coding: utf-8 -*-
r"""表格重排工具.py — 工具债案12（附则《表格规范》①-⑤执行工具；2026-09-04 选必1复合修复轮子步4建）。

规范落点：
  ① 通栏表（显示宽＞栏宽）仅允许头部单栏区/单栏件；双栏正文区内容性表一律收窄入栏。
  ② 栏内表 tblW ≤ 栏宽 − 该件 w:tblCellMar 左右之和（逐表现算，禁常数）。
  ③ 列宽内容感知分配（按各列最长内容分布）；表宽不足先调列宽→仍不足缩表内文字（下限10.5pt）
     →再不足报主会话重构（本工具标 MANUAL 且不动该表）。
  ④ 单元格段落照§7：左对齐、段前后0、line=410 atLeast、字号归一12pt（表内下限10.5pt例外）。
  ⑤ 章首导航表为子步6对象，本工具跳过（签名识别＋登记）。

三模式：
  --scan    只读盘点＋处置预案（dry-run，不落盘改动）
  --apply   施工：栏内表收窄入栏＋列宽重排＋字号决策＋单元格段落规则；写回 docx
  --assert  断言：每表x0/表宽对所属区基准±2pt；窄列判据（列宽<最长内容10.5pt估宽）命中且
            单元格文本行数>2 逐个登记（过目清单）；通栏表落双栏区=缺陷；详解分栏表存量扫描=0。
用法:
  python 表格重排工具.py --scan|--apply|--assert --out 前缀 代号=docx路径 ...
产物: 前缀.json（逐表明细）＋前缀.md（汇总表）。--apply 另在 JSON 内附文字流零字符核验与 sha。
"""
import sys, io, os, re, json, zipfile, shutil, hashlib
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)

DEF_CELLMAR = 108          # Word 缺省 tblCellMar 左右（缇）
SLACK = 40                 # 列最小宽附加余量（缇）
SZ_NORMAL = 24             # 12pt（半点）
SZ_MIN = 21                # 10.5pt（半点）——表内文字下限
PT2TW = 20.0
EM_CM_12PT = 0.423         # 12pt 的 1em ≈ 0.423cm（drawing 宽换算用）
TOL_TW = 40                # ±2pt 容差（缇）

RE_NAVHEAD = ('节名', '题量', '题型组数')
RE_QH = re.compile(r'^\d+(?:\.\d+)+-\d+．')           # 题号块/条目号

# OOXML 子元素顺序（按 ECMA-376 序列；插入必须守序，否则 Word 报不可读）
TBLPR_ORDER = ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize',
               'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders',
               'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption', 'tblDescription']
TCPR_ORDER = ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd',
              'noWrap', 'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark']
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
             'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
             'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE',
             'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
             'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
             'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
             'sectPr', 'pPrChange']
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike',
             'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid',
             'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz',
             'szCs', 'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign',
             'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath']


def ordered_insert(parent, el, order):
    """按 order 序列把 el 插入 parent 的正确位置（parent 与 el 均为 W 命名空间）。"""
    tag = etree.QName(el).localname
    try:
        rank = order.index(tag)
    except ValueError:
        parent.append(el)
        return el
    for child in parent:
        ctag = etree.QName(child).localname
        try:
            crank = order.index(ctag)
        except ValueError:
            continue
        if crank > rank:
            child.addprevious(el)
            return el
    parent.append(el)
    return el


def get_or_make(parent, tag, order):
    e = parent.find(q(tag))
    if e is None:
        e = etree.Element(q(tag))
        ordered_insert(parent, e, order)
    return e


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def is_cjk(ch):
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF
            or 0x2018 <= o <= 0x201D or o in (0x2026, 0x2014))


def para_width_em(p):
    """段落内容宽与最长不可断 token（单位 em，12pt 基准）。
    CJK 逐字可断（1em）；半角字母/数字连缀不可断（0.55em/字符）；
    OMML 块整体不可断（0.55em×线性化字符数＋0.3em，下限1em）；段内嵌图按显示宽换算。"""
    total = [0.0]
    max_tok = [0.0]
    cur = [0.0]
    def flush():
        if cur[0] > max_tok[0]:
            max_tok[0] = cur[0]
        cur[0] = 0.0
    def bump(tok):
        total[0] += tok
        if tok > max_tok[0]:
            max_tok[0] = tok
    def bump_breakable(width, min_tok):
        # 可在算符边界折行的内容（OMML）：全宽计入内容宽，最小 token 只按碎片计
        total[0] += width
        if min_tok > max_tok[0]:
            max_tok[0] = min_tok
    def walk(el):
        for ch in el:
            ns = etree.QName(ch).namespace
            tag = etree.QName(ch).localname
            if ns == M and tag in ('oMath', 'oMathPara'):
                flush()
                lin = ''.join(t.text or '' for t in ch.iter(qm('t')))
                bump_breakable(max(1.0, 0.55 * len(lin)) + 0.3, 1.5)
            elif ns == W and tag == 't':
                for c in (ch.text or ''):
                    if is_cjk(c):
                        flush()
                        bump(1.0)
                    elif c in ' \t':
                        flush()
                        total[0] += 0.5
                    elif c in '([{<':
                        flush()                       # 开括号前可断
                        cur[0] += 0.55
                        total[0] += 0.55
                    elif c in ')]}/+-=,:;!?·':
                        cur[0] += 0.55                # 算符/闭标点后可断
                        total[0] += 0.55
                        flush()
                    else:
                        cur[0] += 0.55
                        total[0] += 0.55
            elif ns == W and tag in ('tab',):
                flush(); total[0] += 0.5
            elif ns == W and tag in ('br', 'cr'):
                flush()
            elif ns == W and tag == 'drawing':
                flush()
                ext = ch.find('.//{%s}extent' % WP)
                if ext is not None and ext.get('cx'):
                    # 段内嵌图只计入内容宽、不计最小 token——图可由子步5按单元格分宽缩extent适配
                    total[0] += int(ext.get('cx')) / 360000.0 / EM_CM_12PT
            else:
                walk(ch)
    walk(p)
    flush()
    return total[0], max_tok[0]


def measure_table(tbl, base_sz=SZ_NORMAL):
    """逐列内容宽/最小宽（缇，按 base_sz 半点字号）。返回 (content[], min[], ncols, rows)。"""
    grid = tbl.find(q('tblGrid'))
    ncols = len(grid.findall(q('gridCol'))) if grid is not None else 0
    rows = tbl.findall(q('tr'))
    if ncols == 0 and rows:
        ncols = len(rows[0].findall(q('tc')))
    content = [0.0] * ncols
    mins = [0.0] * ncols
    em_tw = (base_sz / 2.0) * PT2TW
    for tr in rows:
        ci = 0
        for tc in tr.findall(q('tc')):
            tcpr = tc.find(q('tcPr'))
            span = 1
            vmerge_cont = False
            if tcpr is not None:
                gs = tcpr.find(q('gridSpan'))
                if gs is not None and gs.get(q('val')):
                    span = max(1, int(gs.get(q('val'))))
                vm = tcpr.find(q('vMerge'))
                if vm is not None and vm.get(q('val')) != 'restart':
                    vmerge_cont = True
            wmax = 0.0
            tmax = 0.0
            for p in tc.findall(q('p')):
                tw_em, tok_em = para_width_em(p)
                wmax = max(wmax, tw_em * em_tw)
                tmax = max(tmax, tok_em * em_tw)
            if not vmerge_cont and ci < ncols:
                per = wmax / span
                permin = tmax / span
                for j in range(ci, min(ci + span, ncols)):
                    content[j] = max(content[j], per)
                    mins[j] = max(mins[j], permin)
            ci += span
    return content, mins, ncols, rows


def allocate(content, mins, limit):
    """列宽分配：内容比例＋最小宽保底迭代。返回整数缇列表（Σ=limit）或 None（不可行）。"""
    n = len(content)
    if n == 0 or sum(mins) > limit:
        return None
    alloc = [0.0] * n
    fixed = set()
    pool = list(range(n))
    remain = float(limit)
    for _ in range(n + 2):
        csum = sum(content[j] for j in pool)
        for j in pool:
            alloc[j] = remain * (content[j] / csum if csum > 0 else 1.0 / len(pool))
        viol = [j for j in pool if alloc[j] < mins[j]]
        if not viol:
            break
        for j in viol:
            alloc[j] = mins[j]
            fixed.add(j)
        remain = float(limit) - sum(alloc[j] for j in fixed)
        pool = [j for j in range(n) if j not in fixed]
        if not pool:
            break
    if sum(alloc[j] for j in range(n)) <= 0 or remain < 0 and pool:
        return None
    out = [max(1, int(round(a))) for a in alloc]
    out[-1] += limit - sum(out)
    if out[-1] < 1 or sum(out) != limit:
        return None
    return out


def zones_of(body):
    kids = list(body)
    brk = None
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brk = i
                break
    def params(sect):
        pgSz, pgMar = sect.find(q('pgSz')), sect.find(q('pgMar'))
        cols = sect.find(q('cols'))
        num = int(cols.get(q('num')) or 1) if cols is not None else 1
        space = int(cols.get(q('space')) or 425) if cols is not None else 425
        pgw = int(pgSz.get(q('w')))
        ml, mr = int(pgMar.get(q('left'))), int(pgMar.get(q('right')))
        content_w = pgw - ml - mr
        return {'num': num, 'space': space, 'content_w': content_w,
                'col_w': (content_w - space * (num - 1)) / num, 'pgw': pgw, 'ml': ml, 'mr': mr}
    zp = {'body': params(body.find(q('sectPr'))), 'header': None}
    if brk is not None:
        zp['header'] = params(kids[brk].find(q('pPr')).find(q('sectPr')))
    return kids, brk, zp


def cell_margins(tbl):
    tblpr = tbl.find(q('tblPr'))
    l = r = DEF_CELLMAR
    if tblpr is not None:
        cm = tblpr.find(q('tblCellMar'))
        if cm is not None:
            e = cm.find(q('left'))
            if e is not None and e.get(q('w')) is not None:
                l = int(e.get(q('w')))
            e = cm.find(q('right'))
            if e is not None and e.get(q('w')) is not None:
                r = int(e.get(q('w')))
    return l, r


def is_navtbl(tbl):
    tr = tbl.find(q('tr'))
    if tr is None:
        return False
    joined = '|'.join(re.sub(r'[\s　]', '', ''.join(t.text or '' for t in tc.iter(q('t'))))
                      for tc in tr.findall(q('tc')))
    return all(k in joined for k in RE_NAVHEAD)


def tbl_signature(tbl, maxlen=30):
    tr = tbl.find(q('tr'))
    if tr is None:
        return '(空表)'
    return ' | '.join(''.join(t.text or '' for t in tc.iter(q('t')))[:12]
                      for tc in tr.findall(q('tc')))[:maxlen]


def cell_images(tbl):
    """单元格内嵌图清单：{row, col, cx_cm, cy_cm}（栏内可行性含图硬约束；宽图喂子步5缩图清单）。"""
    out = []
    for ri, tr in enumerate(tbl.findall(q('tr')), 1):
        ci = 0
        for tc in tr.findall(q('tc')):
            tcpr = tc.find(q('tcPr'))
            span = 1
            if tcpr is not None:
                gs = tcpr.find(q('gridSpan'))
                if gs is not None and gs.get(q('val')):
                    span = max(1, int(gs.get(q('val'))))
            for d in tc.iter(q('drawing')):
                ext = d.find('.//{%s}extent' % WP)
                if ext is not None and ext.get('cx'):
                    out.append({'row': ri, 'col': ci + 1,
                                'cx_cm': round(int(ext.get('cx')) / 360000.0, 2),
                                'cy_cm': round(int(ext.get('cy') or 0) / 360000.0, 2)})
            ci += span
    return out


def current_tblw(tbl):
    tblpr = tbl.find(q('tblPr'))
    if tblpr is None:
        return None, None
    e = tblpr.find(q('tblW'))
    if e is None:
        return None, None
    return int(e.get(q('w')) or 0), e.get(q('type'))


def current_tblind(tbl):
    tblpr = tbl.find(q('tblPr'))
    if tblpr is None:
        return 0
    e = tblpr.find(q('tblInd'))
    return int(e.get(q('w')) or 0) if e is not None else 0


def text_stream(root):
    out = []
    body = root.find(q('body'))
    for el in body.iter():
        ns = etree.QName(el).namespace
        ln = etree.QName(el).localname
        if (ns == W and ln == 't') or (ns == M and ln == 't'):
            out.append(el.text or '')
    return out


def plan_table(tbl, zone, zp):
    marL, marR = cell_margins(tbl)
    if zone == 'header' or zp[zone]['num'] == 1:
        limit = int(zp[zone]['content_w'])
        kind = '通栏区表'
    else:
        limit = int(round(zp[zone]['col_w'] - marL - marR))
        kind = '栏内表'
    content, mins, ncols, rows = measure_table(tbl, SZ_NORMAL)
    scale = SZ_MIN / SZ_NORMAL
    alloc = allocate(content, [m + marL + marR + SLACK for m in mins], limit)
    sz_choice = SZ_NORMAL
    if alloc is None:
        alloc = allocate([c * scale for c in content],
                         [m * scale + marL + marR + SLACK for m in mins], limit)
        sz_choice = SZ_MIN
    manual = alloc is None
    oldw, oldtype = current_tblw(tbl)
    imgs = cell_images(tbl)
    img_shrink = []
    if alloc is not None:
        for im in imgs:
            j = im['col'] - 1
            cap_tw = alloc[j] - marL - marR - 20 if 0 <= j < len(alloc) else 0
            cx_tw = im['cx_cm'] * 566.93                # cm→缇（1cm≈566.93缇）
            if cap_tw > 200 and cx_tw > cap_tw:
                s = cap_tw / cx_tw
                img_shrink.append({'row': im['row'], 'col': im['col'],
                                   'old_cx_cm': im['cx_cm'], 'old_cy_cm': im['cy_cm'],
                                   'new_cx_cm': round(im['cx_cm'] * s, 2), 'new_cy_cm': round(im['cy_cm'] * s, 2)})
    return {'kind': kind, 'zone': zone, 'marL': marL, 'marR': marR, 'limit': limit,
            'ncols': ncols, 'rows': len(rows), 'sig': tbl_signature(tbl),
            'old_tblW': oldw, 'old_type': oldtype,
            'content': [round(c, 1) for c in content], 'mins': [round(m, 1) for m in mins],
            'alloc': alloc, 'sz': sz_choice, 'manual': manual, 'cell_images': imgs,
            'img_shrink': img_shrink}


def apply_table(tbl, plan):
    chg = {'tblW': 0, 'layout': 0, 'ind': 0, 'grid': 0, 'tcW': 0, 'sz': 0, 'jc': 0, 'spacing': 0, 'ind_p': 0}
    tblpr = tbl.find(q('tblPr'))
    if tblpr is None:
        tblpr = etree.Element(q('tblPr'))
        tbl.insert(0, tblpr)
    tw = get_or_make(tblpr, 'tblW', TBLPR_ORDER)
    if tw.get(q('w')) != str(plan['limit']) or tw.get(q('type')) != 'dxa':
        tw.set(q('w'), str(plan['limit']))
        tw.set(q('type'), 'dxa')
        chg['tblW'] += 1
    lay = get_or_make(tblpr, 'tblLayout', TBLPR_ORDER)
    if lay.get(q('type')) != 'fixed':
        lay.set(q('type'), 'fixed')
        chg['layout'] += 1
    ind = tblpr.find(q('tblInd'))
    if ind is not None:
        tblpr.remove(ind)
        chg['ind'] += 1
    grid = tbl.find(q('tblGrid'))
    if grid is not None:
        gcs = grid.findall(q('gridCol'))
        if len(gcs) == len(plan['alloc']):
            for gc, wv in zip(gcs, plan['alloc']):
                if gc.get(q('w')) != str(wv):
                    gc.set(q('w'), str(wv))
                    chg['grid'] += 1
    for tr in tbl.findall(q('tr')):
        ci = 0
        for tc in tr.findall(q('tc')):
            tcpr = tc.find(q('tcPr'))
            if tcpr is None:
                tcpr = etree.Element(q('tcPr'))
                tc.insert(0, tcpr)
            span = 1
            gs = tcpr.find(q('gridSpan'))
            if gs is not None and gs.get(q('val')):
                span = max(1, int(gs.get(q('val'))))
            wsum = sum(plan['alloc'][ci:ci + span]) if ci < len(plan['alloc']) else plan['alloc'][-1]
            tcw = get_or_make(tcpr, 'tcW', TCPR_ORDER)
            if tcw.get(q('w')) != str(wsum) or tcw.get(q('type')) != 'dxa':
                tcw.set(q('w'), str(wsum))
                tcw.set(q('type'), 'dxa')
                chg['tcW'] += 1
            for p in tc.findall(q('p')):
                ppr = p.find(q('pPr'))
                if ppr is None:
                    ppr = etree.Element(q('pPr'))
                    p.insert(0, ppr)
                jc = ppr.find(q('jc'))
                if jc is not None and jc.get(q('val')) not in (None, 'left'):
                    jc.set(q('val'), 'left')
                    chg['jc'] += 1
                sp = get_or_make(ppr, 'spacing', PPR_ORDER)
                want = {'before': '0', 'after': '0', 'line': '410', 'lineRule': 'atLeast'}
                if {k: sp.get(q(k)) for k in want} != want:
                    for k, v in want.items():
                        sp.set(q(k), v)
                    chg['spacing'] += 1
                indp = ppr.find(q('ind'))
                if indp is not None:
                    ppr.remove(indp)
                    chg['ind_p'] += 1
                for r in p.iter(q('r')):
                    rpr = r.find(q('rPr'))
                    sz = rpr.find(q('sz')) if rpr is not None else None
                    cur = int(sz.get(q('val'))) if sz is not None and sz.get(q('val')) else None
                    if plan['sz'] == SZ_NORMAL and cur in (None, SZ_NORMAL):
                        continue          # 12pt 表：继承/显式24均合规，不动
                    if cur == plan['sz']:
                        continue
                    if rpr is None:
                        rpr = etree.Element(q('rPr'))
                        r.insert(0, rpr)
                    for tag in ('sz', 'szCs'):
                        e = get_or_make(rpr, tag, RPR_ORDER)
                        e.set(q('val'), str(plan['sz']))
                    chg['sz'] += 1
            ci += span
    return chg


def scan_xiangjie_tables(kids):
    in_xj = False
    hits = []
    ctx = ''
    for i, el in enumerate(kids):
        ln = etree.QName(el).localname
        if ln == 'p':
            t = ptext(el).strip()
            if t.startswith('【详解】'):
                in_xj = True
            elif RE_QH.match(t) or t.startswith('【答案】') or t.startswith('【分析】') or t.startswith('【点睛】'):
                in_xj = False
            if t:
                ctx = t[:30]
        elif ln == 'tbl' and in_xj:
            hits.append({'kid_idx': i, 'ctx': ctx, 'sig': tbl_signature(el)})
    return hits


def narrow_col_review(tbl, plan):
    """窄列判据：列宽 < 该列最长内容10.5pt估宽 → 命中；命中列单元格估行数>2 逐个登记。"""
    if plan['manual'] or plan['alloc'] is None:
        return []
    content, mins, ncols, rows = measure_table(tbl, SZ_MIN)
    hits = []
    for j in range(ncols):
        if plan['alloc'][j] < content[j]:
            for ri, tr in enumerate(rows, 1):
                cells = tr.findall(q('tc'))
                ci = 0
                for tc in cells:
                    tcpr = tc.find(q('tcPr'))
                    span = 1
                    if tcpr is not None:
                        gs = tcpr.find(q('gridSpan'))
                        if gs is not None and gs.get(q('val')):
                            span = max(1, int(gs.get(q('val'))))
                    if ci <= j < ci + span:
                        wmax = 0.0
                        for p in tc.findall(q('p')):
                            tw_em, _ = para_width_em(p)
                            wmax = max(wmax, tw_em * (SZ_MIN / 2.0) * PT2TW)
                        import math
                        lines = int(math.ceil(wmax / max(1, plan['alloc'][j]))) if wmax > 0 else 0
                        if lines > 2:
                            hits.append({'col': j + 1, 'row': ri, 'est_lines': lines,
                                         'alloc': plan['alloc'][j], 'content105': round(wmax, 1),
                                         'cell': ptext(tc)[:24]})
                    ci += span
    return hits


def process(path, mode):
    z = zipfile.ZipFile(path)
    raw = z.read('word/document.xml')
    z.close()
    root = etree.fromstring(raw)
    body = root.find(q('body'))
    kids, brk, zp = zones_of(body)
    ts_before = text_stream(root) if mode == 'apply' else None
    tables = []
    nav = []
    for i, el in enumerate(kids):
        if etree.QName(el).localname != 'tbl':
            continue
        zone = 'header' if (brk is not None and i <= brk) else 'body'
        if is_navtbl(el):
            oldw, oldtype = current_tblw(el)
            nav.append({'kid_idx': i, 'zone': zone, 'tblW': oldw, 'type': oldtype,
                        'sig': tbl_signature(el), 'note': '章首导航表——子步6对象，本工具跳过'})
            continue
        plan = plan_table(el, zone, zp)
        plan['kid_idx'] = i
        if mode == 'assert':
            plan['narrow_review'] = narrow_col_review(el, plan)
            plan['x0_ind'] = current_tblind(el)
            plan['x0_ok'] = abs(plan['x0_ind']) <= TOL_TW
            plan['w_ok'] = (plan['old_tblW'] is not None and plan['old_type'] == 'dxa'
                            and abs(plan['old_tblW'] - plan['limit']) <= TOL_TW)
            plan['tonglan_defect'] = (zone == 'body' and zp['body']['num'] > 1
                                      and plan['old_tblW'] is not None and plan['old_tblW'] > plan['limit'] + TOL_TW)
        tables.append(plan)
    xj_hits = scan_xiangjie_tables(kids)
    result = {'file': os.path.basename(path), 'zones': {k: v for k, v in zp.items() if v},
              'has_break': brk is not None, 'tables': tables, 'nav': nav, 'xiangjie_tables': xj_hits}
    if mode == 'apply':
        chg_total = {'tblW': 0, 'layout': 0, 'ind': 0, 'grid': 0, 'tcW': 0, 'sz': 0, 'jc': 0, 'spacing': 0, 'ind_p': 0}
        applied = 0
        for plan in tables:
            if plan['manual']:
                continue
            chg = apply_table(kids[plan['kid_idx']], plan)
            applied += 1
            for k in chg_total:
                chg_total[k] += chg[k]
        result['text_stream_equal'] = (ts_before == text_stream(root))
        result['applied'] = applied
        result['changes'] = chg_total
        result['docx_sha_before'] = hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]
        new_raw = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.tmp_rewrite'
        zin = zipfile.ZipFile(path, 'r')
        zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                data = new_raw
            zout.writestr(item, data)
        zin.close()
        zout.close()
        shutil.move(tmp, path)
        result['docx_sha_after'] = hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]
    return result


def to_md(results, mode):
    title = {'scan': '盘点/dry-run', 'apply': '施工', 'assert': '断言'}[mode]
    md = ['# 表格重排%s报告（案12）' % title, '']
    for code, r in results.items():
        md.append('## %s（%s）' % (code, r['file']))
        zdesc = '；'.join('%s: cols=%d space=%d 内容宽=%d缇 栏宽=%.1f缇' % (zn, p['num'], p['space'], p['content_w'], p['col_w'])
                          for zn, p in r['zones'].items())
        md.append('- 区参数：%s；头部节分节符=%s' % (zdesc, r['has_break']))
        for nv in r['nav']:
            md.append('- 导航表跳过登记：kid=%d zone=%s tblW=%s(%s)｜%s' % (nv['kid_idx'], nv['zone'], nv['tblW'], nv['type'], nv['sig']))
        if not r['tables'] and not r['nav']:
            md.append('- 本件无表格（不适用）')
        if r['tables']:
            md.append('| # | 落区 | 类 | 旧tblW | 上限 | 字号 | 列宽分配(缇) | MANUAL | 签名 |')
            md.append('|---|---|---|---|---|---|---|---|---|')
            for i, t in enumerate(r['tables'], 1):
                md.append('| %d | %s | %s | %s(%s) | %d | %s | %s | %s | %s |' % (
                    i, t['zone'], t['kind'], t['old_tblW'], t['old_type'], t['limit'],
                    '%.1fpt' % (t['sz'] / 2), t['alloc'], '是' if t['manual'] else '',
                    t['sig'].replace('|', '｜')))
        if mode == 'assert':
            n_x0_bad = sum(1 for t in r['tables'] if not t.get('x0_ok', True))
            n_w_bad = sum(1 for t in r['tables'] if not t.get('w_ok', True))
            n_defect = sum(1 for t in r['tables'] if t.get('tonglan_defect'))
            n_narrow = sum(len(t.get('narrow_review', [])) for t in r['tables'])
            md.append('- 断言：x0越限 %d；表宽越限 %d；通栏落双栏缺陷 %d；窄列过目登记 %d 条' % (n_x0_bad, n_w_bad, n_defect, n_narrow))
            for i, t in enumerate(r['tables'], 1):
                for h in t.get('narrow_review', []):
                    md.append('  - 窄列过目 表%d 列%d 行%d：估%d行 alloc=%d缇 content@10.5=%.0f缇｜%s' % (
                        i, h['col'], h['row'], h['est_lines'], h['alloc'], h['content105'], h['cell']))
        if mode == 'apply':
            md.append('- 施工：applied=%d；改动计数=%s；文字流零字符核验=%s；sha %s→%s' % (
                r.get('applied'), r.get('changes'), r.get('text_stream_equal'),
                r.get('docx_sha_before'), r.get('docx_sha_after')))
        md.append('- 详解分栏表存量扫描：命中 %d 处%s' % (
            len(r['xiangjie_tables']),
            ('：' + '；'.join('kid%d《%s》' % (h['kid_idx'], h['ctx']) for h in r['xiangjie_tables'])) if r['xiangjie_tables'] else ''))
        md.append('')
    return '\n'.join(md)


def main():
    args, opts, i = [], {}, 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a.startswith('--'):
            if '=' in a:
                k, v = a.split('=', 1)
                opts[k] = v
            elif a == '--out' and i + 1 < len(sys.argv):
                opts[a] = sys.argv[i + 1]
                i += 1
            else:
                opts[a] = True
        else:
            args.append(a)
        i += 1
    mode = 'scan'
    for m in ('scan', 'apply', 'assert'):
        if '--' + m in opts:
            mode = m
    out = str(opts.get('--out', '表格重排_out'))
    pairs = [tuple(a.split('=', 1)) for a in args if '=' in a]
    results = {}
    for code, path in pairs:
        if not os.path.exists(path):
            print('[%s] 缺失 %s' % (code, path))
            continue
        results[code] = process(path, mode)
        r = results[code]
        print('[%s] 表%d（导航表%d）详解分栏%d %s' % (
            code, len(r['tables']), len(r['nav']), len(r['xiangjie_tables']),
            ('applied=%d 文字流等=%s' % (r.get('applied'), r.get('text_stream_equal'))) if mode == 'apply' else
            ('MANUAL=%d' % sum(1 for t in r['tables'] if t['manual']))))
    odir = os.path.dirname(os.path.abspath(out))
    if odir:
        os.makedirs(odir, exist_ok=True)
    with open(out + '.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    with open(out + '.md', 'w', encoding='utf-8') as f:
        f.write(to_md(results, mode))
    print('落盘: %s.json / .md' % out)


if __name__ == '__main__':
    main()
