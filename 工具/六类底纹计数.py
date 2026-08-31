# -*- coding: utf-8 -*-
#
# 沿革：2026-08-28 视觉锚新口径回扫轮收编为「四类底纹计数.py」；
# 2026-08-29 成书形态拍板由四类扩为六类（公共规则§7「六类底纹分开计数」条款），T代理改造更名。
# 旧名 工具/四类底纹计数.py 保留为兼容入口（同一 count，报告口径为六类）。
# 2026-08-30 拍板执行轮（T2代理）：②题号难度块签名同步三段式。
# 2026-08-31 欠账A版式改版回扫轮（T2代理，N4/N5三色板改版）：
#   ①标题整行底纹改段级两色分记：章/节标题段级 w:pPr/w:shd fill=#ADC2DA（PDF灰≈190）、
#     讲部/题型标题段级 fill=#C6D4E3（≈209）；段级直挂与「标题3」样式继承两路解析
#     （节标题样式挂载后底纹在 styles.xml 样式定义内，effective＝直挂＞样式链）；
#     旧 run 级「结构序号」灰块按 N4 废止＝新格式违规残留计数；
#   ②题号块底纹只盖「N．」（N6）：新形＝题号段首连续灰底 run 串接恰为「N．」；
#     过渡期兼容旧形整块「N．（档位·提分线·卡壳看答案）」；退化件裸「N．」按题块起点识别；
#   ③内容标记族 C9C9C9 run 级：题号块/块标签/条目号/条目第一子层/答案值·需背；
#   ④修复历史 bug：报告写进目标件（两参签名误用防护——report 路径＝docx/同文件即拒绝）；
#     「C9C9C9 挂点总数恒差1」——旧公式漏加 chip/marker run 且未扫段级/段落标记挂点，
#     现改为全挂点分桶构造性恒等（Σ桶＝document.xml 原始 w:shd 计数）。
"""六类底纹计数.py — 三色板底纹分色计数与恒等式核验（只读，不改文件）：
  ①标题整行底纹（章/节，段级 #ADC2DA）  ②标题整行底纹（讲部/题型，段级 #C6D4E3）
  ③内容标记族（run级 #C9C9C9）：题号块（新形只盖N．＋过渡旧形）、块标签（含行内小标签
      与并行解法标记——跨run分裂标签按字符级灰底蒙版整chip识别）、条目号、条目第一子层、
      答案值/需背（含 OMML m:r/ctrlPr 挂点）
  恒等式（公共规则§7自检⑦现行口径，2026-08-31 N4/N5）：
      题号块底纹run数＝题量（文件名口径并记）；标题整行底纹段数＝章+节+讲部+题型标题数
      （章标题与文内开头标题一并入计，按色分记 ADC2DA/C6D4E3）；块标签run数＝标签计数；
      条目号run数＝条目计数；第一子层run数＝第一子层计数；内容标记覆盖＝题块数。
  违规：A6A6A6/D9D9D9（document+headers/footers+styles 全包扫描）＝0；w:bdr＝0；
      段级 C9C9C9 误挂＝0；run级 #ADC2DA/#C6D4E3 误挂＝0；新格式旧结构序号run残留＝0；
      加粗类（题号块须加粗；块标签/条目号/子层不加粗；标题整行加粗——effective 解析含样式链）。
  改版前件（未检出段级标题底纹）：标题整行底纹恒等式标「不适用（改版前）」，旧结构序号
  run 计数转登记口径（不阻断）；六类 C9C9C9 族恒等式照常全断言。
  表内非标签灰底（导航表头 run 等）与 tcPr 级底纹、空文本灰底 run 单独登记，不入六类。
  清单件判定：文件名含「知识清单」——题号块与覆盖恒等式不适用，条目号/第一子层照查。
用法: python 六类底纹计数.py <docx> <报告txt>（report 拒绝 .docx 等成品扩展名与同路径，
      防两参签名误用把报告写进目标件；旧名 四类底纹计数.py 同 CLI 兼容入口）"""
import sys, zipfile, re, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lxml import etree
from extract_structure import structure   # 注：该模块导入时会自重包 stdout

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL_CONTENT = 'C9C9C9'      # ③内容标记族（PDF灰≈201）
FILL_TITLE1 = 'ADC2DA'       # ①章/节标题整行底纹（≈190）
FILL_TITLE2 = 'C6D4E3'       # ②讲部/题型标题整行底纹（≈209）
LEGACY_FILLS = ('A6A6A6', 'D9D9D9')
PRODUCT_EXT = ('.docx', '.docm', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.pdf', '.zip')

# —— 与 工具/块标签芯片.py 同源口径（复制常量避免中文名模块导入脆性；改动须两处同步）——
CHIP_RE = re.compile(r'【[^】]{1,16}】')
CHIP_BLACKLIST = ('【易错】', '【了解】')
CHIP_BLACKLIST_RE = re.compile(r'^【典例[^】]*】$')
MARK_RE = re.compile(r'^(?:\(\d{1,2}\)|（\d{1,2}）)?(?:【[^】]{1,12}】)?(?:解：|证明：)?'
                     r'(［?(?:方法|解法)[一二三四五六七八九十]{1,3}］?|另解)[：:]?$')
# 题号块段落前缀（三段式/两段式/过渡旧单段；退化件裸 N．经题块起点识别不靠本式）
QBLOCK_HEAD_RE = re.compile(
    r'^\d+．（(?:(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%))?·卡壳看答案'
    r'|衔接必会·卡壳看答案|(?:简单|中档|难))')
QNUM_LEGACY_RE = re.compile(     # 过渡期旧形：整块「N．（档位[·提分线·卡壳看答案]）」一个run
    r'^\d+．（(?:(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%)·卡壳看答案)?|衔接必会·卡壳看答案)）$')
SECTNUM_RE = re.compile(r'^\d+(?:\.\d+){1,6} ?$')   # 旧结构序号 run（N4 废除形态）
LECTURE_RE = re.compile(r'^\d+(?:\.\d+)*\s*方法讲解[｜|]')
CHAP_RE = re.compile(r'^第\d+章')
MERGED_SEC_RE = re.compile(r'（第\d+[—–-]\d+题）')   # N11 节标题行内合并统计段
ENT_RE = re.compile(r'^\d+．')
SUB_RE = re.compile(r'^（\d+）')
CIRC_RE = re.compile(r'^[①②③④⑤⑥⑦⑧⑨⑩]')
HEAD_RE = re.compile(r'^\d+(?:\.\d+){1,6}(?:\s|方法讲解)')
NUMDOT_RE = re.compile(r'^\d+．$')

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None

def in_tbl(el):
    cur = el.getparent()
    while cur is not None:
        if tag(cur) == 'tbl':
            return True
        cur = cur.getparent()
    return False

def eff_bold(r, styles_bold):
    """run effective 加粗：run rPr 显式＞继承段落样式链（样式挂载后 b 在样式定义）。"""
    rpr = r.find(q('rPr'))
    if rpr is not None:
        b = rpr.find(q('b'))
        if b is not None:
            return b.get(q('val')) not in ('0', 'false', 'off', 'none')
    ps = r.getparent()
    while ps is not None and tag(ps) != 'p':
        ps = ps.getparent()
    if ps is not None:
        ppr = ps.find(q('pPr'))
        pst = ppr.find(q('pStyle')) if ppr is not None else None
        if pst is not None and styles_bold.get(pst.get(q('val'))):
            return True
    return False

def load_styles(z):
    """styles.xml → (styleId→段级fill, styleId→加粗)；basedOn 链解析（防环）。"""
    if 'word/styles.xml' not in z.namelist():
        return {}, {}
    root = etree.fromstring(z.read('word/styles.xml'))
    base, fill, bold = {}, {}, {}
    for st in root.iter(q('style')):
        sid = st.get(q('styleId'))
        if not sid:
            continue
        bo = st.find(q('basedOn'))
        base[sid] = bo.get(q('val')) if bo is not None else None
        ppr = st.find(q('pPr'))
        shd = ppr.find(q('shd')) if ppr is not None else None
        fill[sid] = shd.get(q('fill')) if shd is not None else None
        rpr = st.find(q('rPr'))
        b = rpr.find(q('b')) if rpr is not None else None
        bold[sid] = b is not None and b.get(q('val')) not in ('0', 'false', 'off', 'none')
    def resolve(sid, table):
        seen = set()
        while sid and sid not in seen:
            seen.add(sid)
            if table.get(sid):
                return table[sid]
            sid = base.get(sid)
        return None
    return ({sid: resolve(sid, fill) for sid in fill},
            {sid: resolve(sid, bold) for sid in bold})

def para_shading(p, styles_fill):
    """段级底纹 effective fill：直挂 pPr/shd ＞ 段落样式链；返回 (fill, 直挂?)。"""
    ppr = p.find(q('pPr'))
    if ppr is not None:
        shd = ppr.find(q('shd'))
        if shd is not None:
            return shd.get(q('fill')), True
        pst = ppr.find(q('pStyle'))
        if pst is not None:
            f = styles_fill.get(pst.get(q('val')))
            if f:
                return f, False
    return None, False

def classify_headings(els, ptexts):
    """标题分类（自含口径，不依赖 extract_structure 的 kind 分型）：
    文内开头标题（首个非空段）＝章；正文内 ^第N章＝章；「父号.k 方法讲解｜」＝讲部；
    含（第X—Y题）合并统计段的数码标题＝节（N11——先于题型判定防「本节N题：」冒号误判）；
    数码＋「：」＝题型；其余数码起段＝节。返回 [(idx, kind, text)]。"""
    heads = []
    first = True
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        t = ptexts[i]
        if not t.strip():
            continue
        if first:
            heads.append((i, 'chapter', t)); first = False; continue
        if LECTURE_RE.match(t):
            heads.append((i, 'lecture', t))
        elif MERGED_SEC_RE.search(t) and re.match(r'^\d+(?:\.\d+)*[\s　]', t):
            heads.append((i, 'section', t))
        elif CHAP_RE.match(t):
            heads.append((i, 'chapter', t))
        elif re.match(r'^\d+(\.\d+)*[\s　]+\S', t) and '：' in t:
            heads.append((i, 'group', t))
        elif re.match(r'^\d+(\.\d+)*[\s　]+\S', t):
            heads.append((i, 'section', t))
    return heads

def entry_counts(els, ptexts, qstart_els):
    """条目计数与第一子层计数（状态机同 工具/条目号底纹.py 口径＋题块起点优先复位：
    退化件裸「N．题干」不再误计条目）。返回 (条目数, 第一子层数)。"""
    n_ent = n_sub = 0
    entry_active = False
    deep = False
    last_sub_no = 0
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue                      # 表格＝条目内容，不断语境
        t = ptexts[i]
        if i in qstart_els or QBLOCK_HEAD_RE.match(t):
            entry_active = False; deep = False; last_sub_no = 0
            continue
        if ENT_RE.match(t) and not HEAD_RE.match(t):
            n_ent += 1
            entry_active = True; deep = False; last_sub_no = 0
            continue
        if HEAD_RE.match(t):
            entry_active = False; deep = False; last_sub_no = 0
            continue
        if CIRC_RE.match(t):
            deep = True
            continue
        m = SUB_RE.match(t)
        if m and entry_active:
            no = int(m.group(0)[1:-1])
            if deep and no != last_sub_no + 1:
                continue
            n_sub += 1
            deep = False
            last_sub_no = no
    return n_ent, n_sub

def count(path, report):
    # —— 两参签名误用防护（历史 bug：报告写进目标件）——
    ap = os.path.abspath(path)
    rp = os.path.abspath(report)
    if rp == ap or rp.lower().endswith(PRODUCT_EXT):
        sys.stderr.write('拒绝：报告路径 %s 与目标件相同或为成品扩展名'
                         '（防报告写进目标件）——报告请用 .txt\n' % report)
        sys.exit(2)
    st = structure(path)
    items = st['items']
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    styles_fill, styles_bold = load_styles(z)
    all_parts = [n for n in z.namelist() if n.startswith('word/') and n.endswith('.xml')]
    part_bytes = {n: z.read(n) for n in all_parts}
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    qstart_els = {items[qu['start']]['el'] for qu in st['questions']}
    heads = classify_headings(els, ptexts)
    n_ch = sum(1 for h in heads if h[1] == 'chapter')
    n_sec = sum(1 for h in heads if h[1] == 'section')
    n_lec = sum(1 for h in heads if h[1] == 'lecture')
    n_grp = sum(1 for h in heads if h[1] == 'group')
    head_by_idx = {h[0]: h[1] for h in heads}
    is_qd = '知识清单' in os.path.basename(path)
    m_fn = re.search(r'（(\d+)题）', os.path.basename(path))
    nq_fn = int(m_fn.group(1)) if m_fn else None
    nq = len(st['questions'])
    nent, nsub = entry_counts(els, ptexts, qstart_els)

    # —— 段级标题整行底纹（effective＝直挂＞样式链）——
    t1_direct = t1_style = t2_direct = t2_style = 0
    t1_para_els, t2_para_els = set(), set()
    p3_mis = 0            # 段级 C9C9C9 误挂（内容族无段级合法对象）
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        f, direct = para_shading(el, styles_fill)
        if f == FILL_TITLE1:
            t1_para_els.add(i); t1_direct += direct; t1_style += (not direct)
        elif f == FILL_TITLE2:
            t2_para_els.add(i); t2_direct += direct; t2_style += (not direct)
        elif f == FILL_CONTENT:
            p3_mis += 1
    # 标题漏挂/非标题误挂（按色分记）
    t1_expect = {h[0] for h in heads if h[1] in ('chapter', 'section')}
    t2_expect = {h[0] for h in heads if h[1] in ('lecture', 'group')}
    t1_miss = sorted(t1_expect - t1_para_els)
    t2_miss = sorted(t2_expect - t2_para_els)
    t1_extra = sorted(t1_para_els - t1_expect)
    t2_extra = sorted(t2_para_els - t2_expect)
    new_format = bool(t1_para_els or t2_para_els)

    # —— run 级 C9C9C9 分类 + 字符级灰底蒙版（chip 跨 run 分裂识别）——
    cls = {'内容标记': 0, '题号块新形': 0, '题号块旧形': 0, '条目号': 0, '条目第一子层': 0,
           '表内其他': 0}
    qd_new_bold = qd_old_bold = 0          # 题号块加粗缺失违规（期望 0）
    ent_bold = sub_bold = chip_bold = 0    # 不加粗对象加粗违规（期望 0）
    head_nobold = 0                        # 新格式标题行内非加粗 run（effective，期望 0）
    old_sectnum_residue = 0                # 旧结构序号 run（新格式＝违规残留；改版前＝登记）
    run_t1_t2_mis = 0                      # run 级 #ADC2DA/#C6D4E3 误挂（标题色只许段级）
    empty_shd = 0
    odd = []
    chip_hit = marker_hit = 0
    chip_miss_sample = []
    lb_occ = {}
    # 每段预计算：字符蒙版（shade/run序号）与段首连续灰底 run 串接文本
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        runs = list(el.iter(q('r')))
        # 段首连续灰底 run 串接（题号块/条目号/子层新形判定；空文本 run 跳过不断链）
        lead_txt = ''
        lead_runs = []
        for r in runs:
            rpr = r.find(q('rPr'))
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '':
                continue
            if shd_fill(rpr) == FILL_CONTENT:
                lead_txt += t; lead_runs.append(r)
            else:
                break
        para_t = ptexts[i]
        lead_matched = False
        if lead_runs:
            if i in qstart_els or QBLOCK_HEAD_RE.match(para_t):
                if NUMDOT_RE.fullmatch(lead_txt):
                    cls['题号块新形'] += 1; lead_matched = True
                    if any(not eff_bold(r, styles_bold) for r in lead_runs):
                        qd_new_bold += 1
                elif QNUM_LEGACY_RE.fullmatch(lead_txt):
                    cls['题号块旧形'] += 1; lead_matched = True
                    if any(not eff_bold(r, styles_bold) for r in lead_runs):
                        qd_old_bold += 1
            elif NUMDOT_RE.fullmatch(lead_txt) and not in_tbl(el):
                cls['条目号'] += 1; lead_matched = True
                if any(eff_bold(r, styles_bold) for r in lead_runs):
                    ent_bold += 1
            elif re.fullmatch(r'（\d+）', lead_txt) and not in_tbl(el):
                cls['条目第一子层'] += 1; lead_matched = True
                if any(eff_bold(r, styles_bold) for r in lead_runs):
                    sub_bold += 1
            elif i in head_by_idx and SECTNUM_RE.match(lead_txt):
                old_sectnum_residue += 1; lead_matched = True   # 旧「结构序号」run（新格式违规／改版前登记）
        # 字符级蒙版（chip span 整体灰底识别）＋ run 字符区间
        chars, mask, ridx = [], [], []
        ranges = {}
        for k, r in enumerate(runs):
            rpr = r.find(q('rPr'))
            sh = shd_fill(rpr) == FILL_CONTENT
            bold = eff_bold(r, styles_bold)
            s0 = len(chars)
            for x in r.findall(q('t')):
                s = x.text or ''
                chars.extend(s); mask.extend([sh] * len(s)); ridx.extend([(k, bold)] * len(s))
            ranges[k] = (s0, len(chars))
        fulltext = ''.join(chars)
        # 标签计数（分母）与挂点命中（分子）——chip 按字符级蒙版整 span 灰底识别（跨 run 分裂兼容）；
        # 并行解法标记维持整 run 匹配口径（防正文散文「方法一般…」类假阳性入恒等式）
        chip_spans = []
        for mm in CHIP_RE.finditer(fulltext):
            lb = mm.group(0)
            if lb in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(lb):
                continue
            lb_occ[lb] = lb_occ.get(lb, 0) + 1
            chip_spans.append(mm.span())
        chip_runs = set()
        for (a, bb) in chip_spans:
            if all(mask[a:bb]):
                chip_hit += 1
                if any(ridx[j][1] for j in range(a, bb)):
                    chip_bold += 1          # chip 不加粗（§7）
            elif len(chip_miss_sample) < 8:
                chip_miss_sample.append(fulltext[max(0, a - 6):bb + 6])
            for k, (s0, s1) in ranges.items():
                if s0 >= a and s1 <= bb:
                    chip_runs.add(k)        # run 整体属 chip 域（分类环不重复计入内容标记）
        for r in runs:
            rpr = r.find(q('rPr'))
            if shd_fill(rpr) != FILL_CONTENT:
                continue
            txt = ''.join(x.text or '' for x in r.findall(q('t')))
            if txt and MARK_RE.match(txt):
                marker_hit += 1
                if eff_bold(r, styles_bold):
                    chip_bold += 1
        # 标题行加粗（新格式：标题段全部非空 run effective 加粗）
        if new_format and i in head_by_idx:
            for r in runs:
                t = ''.join(x.text or '' for x in r.findall(q('t')))
                if t.strip() and not eff_bold(r, styles_bold):
                    head_nobold += 1
        # 其余灰底 run 分类（chip 域与并行解法标记 run 不重复计入内容标记）
        for k, r in enumerate(runs):
            rpr = r.find(q('rPr'))
            fill = shd_fill(rpr)
            if fill in (FILL_TITLE1, FILL_TITLE2):
                run_t1_t2_mis += 1
                continue
            if fill != FILL_CONTENT:
                continue
            txt = ''.join(x.text or '' for x in r.findall(q('t')))
            if txt == '':
                empty_shd += 1
                continue
            if k in chip_runs or MARK_RE.match(txt):
                continue
            lead = lead_matched and (r in lead_runs)
            if not lead and i in head_by_idx and SECTNUM_RE.match(txt):
                old_sectnum_residue += 1
            elif not lead and not in_tbl(r) and txt.strip():
                cls['内容标记'] += 1
            elif not lead and in_tbl(r):
                cls['表内其他'] += 1
            elif not lead and not txt.strip():
                empty_shd += 1
            elif not lead:
                odd.append(txt)

    # —— OMML 挂点（m:r / 结构 ctrlPr 的 w:rPr）——
    om_mr = om_ctrl = 0
    for el in doc.iter():
        if etree.QName(el).namespace != M:
            continue
        tg = tag(el)
        if tg in ('r', 'ctrlPr') and shd_fill(el.find(q('rPr'))) == FILL_CONTENT:
            if tg == 'r':
                om_mr += 1
            else:
                om_ctrl += 1

    # —— 全挂点分桶构造性恒等（修「C9C9C9挂点总数恒差1」）——
    buckets = {}
    raw_c9 = 0
    for shd in doc.iter(q('shd')):
        f = shd.get(q('fill')) or ''
        par = shd.getparent()
        gp = par.getparent() if par is not None else None
        gpp = gp.getparent() if gp is not None else None
        if tag(par) == 'rPr':
            if gp is None:
                bk = 'other'
            elif etree.QName(gp).namespace == M:
                bk = 'om_ctrl' if tag(gp) == 'ctrlPr' else 'om_mr'
            elif tag(gp) == 'r':
                bk = 'run'
            elif tag(gp) == 'pPr':
                bk = 'pmark'          # 段落标记 rPr（旧工具盲区——恒差1候选）
            else:
                bk = 'other'
        elif tag(par) == 'pPr':
            bk = 'para'
        elif tag(par) == 'tcPr':
            bk = 'tc'
        elif tag(par) in ('tblPr', 'trPr'):
            bk = 'tbl'
        else:
            bk = 'other'
        buckets[(f, bk)] = buckets.get((f, bk), 0) + 1
        if f == FILL_CONTENT:
            raw_c9 += 1
    b = lambda bk: buckets.get((FILL_CONTENT, bk), 0)
    c9_total = sum(v for (f, _), v in buckets.items() if f == FILL_CONTENT)

    # —— 旧灰残留全包扫描（document+headers/footers+styles 等 word/*.xml）——
    legacy_parts = []
    for name, byt in part_bytes.items():
        for lf in LEGACY_FILLS:
            n = byt.count(('w:fill="%s"' % lf).encode())
            if n:
                legacy_parts.append('%s:%s×%d' % (name, lf, n))
    bdr_total = sum(1 for _ in doc.iter(q('bdr')))
    tc_shd = b('tc')

    # —— ①覆盖恒等：每题块答案行（或跨段续值段）有答案值灰底 ——
    cov = 0
    nocov = []
    for qu in st['questions']:
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        hit = False
        for ci in range(s_el, e_el):
            p = els[ci]
            if tag(p) != 'p':
                continue
            t = ptexts[ci]
            if not t.startswith('【答案】'):
                continue
            for r in p.iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                if txt and not CHIP_RE.fullmatch(txt) and shd_fill(r.find(q('rPr'))) == FILL_CONTENT:
                    hit = True; break
            if not hit:
                for el in p.iter():
                    if etree.QName(el).namespace == M and tag(el) in ('r', 'ctrlPr') \
                            and shd_fill(el.find(q('rPr'))) == FILL_CONTENT:
                        hit = True; break
            if not hit and '【知识点】' not in t:
                cj = ci + 1
                while cj < e_el and tag(els[cj]) == 'p' and not ptexts[cj].strip():
                    cj += 1
                if cj < e_el and tag(els[cj]) == 'p':
                    for r in els[cj].iter(q('r')):
                        txt = ''.join(x.text or '' for x in r.findall(q('t')))
                        if txt and not CHIP_RE.fullmatch(txt) and not NUMDOT_RE.match(txt) \
                                and shd_fill(r.find(q('rPr'))) == FILL_CONTENT:
                            hit = True; break
            break  # 每题只认首个【答案】行
        if hit:
            cov += 1
        else:
            nocov.append(qu['no'])

    nq_block = cls['题号块新形'] + cls['题号块旧形']
    chip_total_occ = sum(lb_occ.values())
    L = []
    L.append('六类底纹计数·三色签名（2026-08-31 N4/N5三色板）：%s' % os.path.basename(path))
    L.append('模式: %s' % ('新三色板（检出段级标题底纹）' if new_format else
                          '改版前（未检出段级标题底纹——标题整行底纹恒等式不适用，待欠账A W波铺开）'))
    L.append('①标题整行底纹 段级#%s %d 段（期望＝章/文内开头 %d＋节 %d＝%d）｜直挂 %d＋样式继承 %d｜'
             '章 %d｜节 %d｜漏挂 %d 段%s｜误挂非标题段 %d 段'
             % (FILL_TITLE1, len(t1_para_els), n_ch, n_sec, n_ch + n_sec,
                t1_direct, t1_style, n_ch, n_sec, len(t1_miss),
                ('（body序号样本 %s）' % t1_miss[:6]) if t1_miss else '', len(t1_extra)))
    L.append('②标题整行底纹 段级#%s %d 段（期望＝讲部 %d＋题型 %d＝%d）｜直挂 %d＋样式继承 %d｜'
             '漏挂 %d 段%s｜误挂非标题段 %d 段'
             % (FILL_TITLE2, len(t2_para_els), n_lec, n_grp, n_lec + n_grp,
                t2_direct, t2_style, len(t2_miss),
                ('（body序号样本 %s）' % t2_miss[:6]) if t2_miss else '', len(t2_extra)))
    L.append('③内容标记族 run级#%s：题号块 %d（新形N．run %d＋过渡旧形整块run %d）＝题量 %d'
             '（文件名口径 %s）%s｜加粗缺失违规 %d（期望 0）'
             % (FILL_CONTENT, nq_block, cls['题号块新形'], cls['题号块旧形'], nq,
                nq_fn if nq_fn is not None else '（文件名无题量）',
                '' if (nq_block == nq and (nq_fn is None or nq == nq_fn)) else ' ←≠',
                qd_new_bold + qd_old_bold))
    L.append('   块标签run（芯片）%d＝标签计数（芯片出现数）%d%s｜并行解法标记run %d（登记）%s'
             % (chip_hit, chip_total_occ, '' if chip_hit == chip_total_occ else ' ←≠',
                marker_hit, ('｜未挂样本 %r' % chip_miss_sample[:3]) if chip_miss_sample else ''))
    top = sorted(lb_occ.items(), key=lambda kv: -kv[1])[:10]
    L.append('   标签分计 TOP：%s' % ('；'.join('%s×%d' % kv for kv in top) if top else '（无）'))
    L.append('   条目号run %d＝条目计数 %d%s｜加粗违规 %d（期望 0）'
             % (cls['条目号'], nent, '' if cls['条目号'] == nent else ' ←≠', ent_bold))
    L.append('   条目第一子层run %d＝第一子层计数 %d%s｜加粗违规 %d（期望 0）'
             % (cls['条目第一子层'], nsub, '' if cls['条目第一子层'] == nsub else ' ←≠', sub_bold))
    L.append('   答案值/需背run %d＋OMML挂点 m:r %d＋ctrlPr %d｜内容标记覆盖＝题块数 %d/%d%s%s'
             % (cls['内容标记'], om_mr, om_ctrl, cov, nq,
                ('（未覆盖题: %s）' % nocov[:12]) if nocov else '',
                '（清单件：题号块/覆盖恒等式不适用）' if is_qd else ''))
    L.append('违规与残留：旧结构序号run %d（%s）｜段级#%s误挂 %d（期望 0）｜run级#%s/#%s误挂 %d（期望 0）｜'
             'chip加粗违规 %d（期望 0）｜标题行非加粗run %d（%s）'
             % (old_sectnum_residue,
                '新格式期望 0' if new_format else '改版前登记口径',
                FILL_CONTENT, p3_mis, FILL_TITLE1, FILL_TITLE2, run_t1_t2_mis,
                chip_bold, head_nobold, '新格式期望 0' if new_format else '改版前不检'))
    L.append('旧灰残留（全包 word/*.xml）：%s｜w:bdr %d（期望 0）'
             % ('；'.join(legacy_parts) if legacy_parts else 'A6A6A6/D9D9D9 全包 0', bdr_total))
    L.append('C9C9C9 全挂点分桶（构造性恒等——修恒差1）：run %d｜run空文本 %d｜段级 %d｜段落标记 %d｜'
             'tcPr %d｜om_mr %d｜om_ctrl %d｜tbl/tr %d｜其他 %d｜Σ %d＝document.xml 原始 %d %s'
             % (b('run'), empty_shd, b('para'), b('pmark'), b('tc'), b('om_mr'), b('om_ctrl'),
                b('tbl'), b('other'), c9_total, raw_c9,
                '✓' if c9_total == raw_c9 else '←≠ 分桶缺口'))
    L.append('登记不入六类：表内非标签灰底run %d｜tcPr底纹（导航表头等） %d｜空文本灰底run %d｜未归类 %d%s'
             % (cls['表内其他'], tc_shd, empty_shd, len(odd),
                ('｜样本 %r' % odd[:6]) if odd else ''))

    base_ok = (cls['条目号'] == nent and ent_bold == 0
               and cls['条目第一子层'] == nsub and sub_bold == 0
               and chip_hit == chip_total_occ and chip_bold == 0
               and p3_mis == 0 and run_t1_t2_mis == 0
               and not legacy_parts and bdr_total == 0 and not odd
               and c9_total == raw_c9)
    if is_qd:
        base_ok = base_ok
    else:
        base_ok = base_ok and nq_block == nq and (nq_fn is None or nq == nq_fn) \
            and cov == nq and qd_new_bold + qd_old_bold == 0
    if new_format:
        ok = (base_ok
              and len(t1_para_els) == n_ch + n_sec and len(t2_para_els) == n_lec + n_grp
              and not t1_miss and not t2_miss and not t1_extra and not t2_extra
              and old_sectnum_residue == 0 and head_nobold == 0)
        L.append('结论: ' + ('PASS 三色板齐＋六类恒等式成立' if ok else 'CHECK 见上'))
    else:
        ok = base_ok
        L.append('结论: ' + ('PASS（改版前口径——六类C9C9C9族恒等式成立；标题整行底纹0段待W波）'
                             if ok else 'CHECK 见上'))
    out = '\n'.join(L)
    d = os.path.dirname(rp)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    open(rp, 'w', encoding='utf-8').write(out + '\n')
    print(out)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python 六类底纹计数.py <docx> <报告txt>')
        sys.exit(1)
    count(sys.argv[1], sys.argv[2])
