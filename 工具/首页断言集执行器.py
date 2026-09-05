# -*- coding: utf-8 -*-
r"""首页断言集执行器.py — 2026-09-03 选必1版式复合修复轮·子步0新建（附则《双栏首页断言》前置步0＋④工具门；
断言集执行器＝三族匹配＋①反向校验＋fail-closed；工具债案5d/6）。
2026-09-06 收尾-B v3适配（注记）：①匹配层归一化（nospc）新增剔除 WJ(U+2060)/零宽/软连字＋数学字形
（U+1D400–1D7FF）→ASCII 转写，断言①加块级拼行回退——T7/T9a 插符、OMML 数学斜体、块内拆行三类
终态伪影不再败锚；②--run 新增 --mapping <json>：可直载附则注册锚点映射表（v3，权威源＝
工作区/选必1成书修复-0905/②工具/报告/锚点映射表v3.json——PDF 终态实测定标；docx 侧 gen-mapping
看不见文字层伪影，题名内嵌公式件以其自产表判①不可靠）；③gen-mapping 锚点定族更正为
「文档序第一个条目号/题号块」（前置步0「锚点＝正文首块」；旧「带题件→题号块」预设系②-E 断言①
假阴性 5/10 之根因，讲部补挂后讲练/衔接件首块＝条目号）。

三模式：
  --gen-mapping   逐件读document.xml实测首块特征→锚点映射表v1（机读正则＋实际首块特征）＋黑名单反向校验；
  --make-p1       首页PDF＝全件PDF（主路径产物）第1页裁剪（PrintOut Range被本环境Word忽略，三次复测在案——
                  渲染源同主路径、非ExportAsFixedFormat，合附则⑥）；
  --run           断言①（首页正文成立，首页PDF）＋②（头部要素通栏，首页PDF＋XML侧导航表落区）＋⑤（分卷标题，
                  全件PDF第1页）＋阴性对照（缺陷态PDF须判FAIL）。
fail-closed：首页可抽取块数=0或脚本异常＝不判定＝禁止交付（报告写「不判定」、JSON标blocked=true）。

用法:
  python 首页断言集执行器.py --gen-mapping --out <工作区根> 代号=docx路径...
  python 首页断言集执行器.py --make-p1     --out <工作区根> 代号=docx路径...
  python 首页断言集执行器.py --run         --out <工作区根> 代号=docx路径... [--negative <pdf路径> --neg-code X2]
                                           [--mapping <附则注册锚点映射表json>（v3，2026-09-06收尾-B新增）]
产物: <out>/锚点映射表v1.md / 锚点映射表v1.json / 首页PDF/<代号>_p1.pdf / 首页断言报告.md / 首页断言结果.json
"""
import sys, io, os, re, json, time, zipfile
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

RE_TQH = re.compile(r'^\d+(?:\.\d+){3,}-\d+．')          # 题号块「N-N-N．」式（题型号≥4段）
RE_TMH = re.compile(r'^\d+\.\d+(?:\.\d+)?-\d+．')        # 条目号「N-N．」式（节号2~3段）
RE_STAT = re.compile(r'[ 　]本节\d+题')                  # 节标题统计段
RE_STATS_ROW = re.compile(r'^全件\d+题')                  # 全件统计行
RE_LEGEND = re.compile(r'^〔[基进]〕＝')                  # 图例行
RE_PAGERANGE = re.compile(r'（[^）]*[—–\-上下][^）]*）')  # 范围/卷次括注
RE_COUNT = re.compile(r'（(?:\d+题(?:\d+条)?|\d+条|完成)）')
HF_SIG = '羿郭工作室'                                     # 页眉页脚同串签名

TW2PT = 1.0 / 20.0


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


# 数学字母字形各族基址（拉丁/希腊/数字；U+1D400–1D7FF）→ASCII（2026-09-06 收尾-B v3 适配）
_MATH_FAMILIES = (
    (0x1D400, 52), (0x1D434, 52), (0x1D468, 52), (0x1D49C, 52), (0x1D4D0, 52),
    (0x1D504, 52), (0x1D538, 52), (0x1D56C, 52), (0x1D5A0, 52), (0x1D5D4, 52),
    (0x1D608, 52), (0x1D63C, 52),
    (0x1D670, 10),
    (0x1D6A8, 52), (0x1D6E2, 52), (0x1D71C, 52), (0x1D756, 52), (0x1D790, 52),
    (0x1D7CE, 10), (0x1D7D8, 10), (0x1D7E2, 10), (0x1D7EC, 10), (0x1D7F6, 10),
)


def _math_to_ascii(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x1D400 <= o <= 0x1D7FF:
            for base, n in _MATH_FAMILIES:
                if base <= o < base + n:
                    i = o - base
                    out.append(chr(ord('0') + i) if n == 10 else
                               chr(ord('A') + i) if i < 26 else chr(ord('a') + i - 26))
                    break
            else:
                out.append(ch)      # 字形块内例外/保留位（nabla 等字面）原样保留
        else:
            out.append(ch)
    return ''.join(out)


def nospc(s):
    """断言归一化（2026-09-06 v3适配）：数学字形→ASCII＋去全部空白＋去WJ(U+2060)/零宽/软连字
    （PDF抽取会在数字与CJK间插空格、双栏行折行，T7/T9a 往栏顶芯片插 WJ——断言一律在归一化文本上匹配）。"""
    return re.sub(r'[\s\u2060\u200b\u200c\u200d\ufeff\u00ad]+', '', _math_to_ascii(s))


def tbl_head_cells(tbl):
    tr = tbl.find(q('tr'))
    if tr is None:
        return []
    return [nospc(ptext(tc)) for tc in tr.findall(q('tc'))]


def is_navtbl(tbl):
    """章首导航表签名：表头行含 节名/题量/题型组数（四列固定或五列待四列化形态）。"""
    cells = tbl_head_cells(tbl)
    return ('节名' in cells or any('节名' in c for c in cells)) and any('题量' in c for c in cells) \
        and any('题型组数' in c for c in cells)


def file_stem(filename):
    """文件名主干＝去扩展名、去范围括注、去题量/完成括注。"""
    s = re.sub(r'\.docx$', '', filename)
    s = RE_COUNT.sub('', s)
    s = RE_PAGERANGE.sub('', s)
    return s.strip()


def inspect_docx(path):
    """读document.xml：页面参数、头部要素、正文首块、锚点候选。"""
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body'))
    sects = body.findall(q('sectPr'))
    body_sect = sects[-1]
    pgSz, pgMar = body_sect.find(q('pgSz')), body_sect.find(q('pgMar'))
    page = {'w': int(pgSz.get(q('w'))) * TW2PT, 'h': int(pgSz.get(q('h'))) * TW2PT,
            'ml': int(pgMar.get(q('left'))) * TW2PT, 'mr': int(pgMar.get(q('right'))) * TW2PT,
            'mt': int(pgMar.get(q('top'))) * TW2PT, 'mb': int(pgMar.get(q('bottom'))) * TW2PT}
    kids = list(body)
    brk = None                      # 头部节分节符所在段下标
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brk = i
                break
    header_kids = kids[:brk + 1] if brk is not None else []
    body_kids = kids[brk + 1:] if brk is not None else kids
    title_txt = ptext(header_kids[0]) if header_kids else ''
    stats_row, legends, navtbl = None, [], None
    stats_row_in_header, legends_in_header = False, []
    for el in header_kids:
        ln = etree.QName(el).localname
        if ln == 'p':
            t = ptext(el)
            if RE_STATS_ROW.match(t):
                stats_row = t
                stats_row_in_header = True
            elif RE_LEGEND.match(t):
                legends.append(t)
                legends_in_header.append(True)
    # 导航表识别（签名制，内容表不误判）：头部区与正文区分开找，落区即缺陷签名
    navtbl = None
    if brk is not None:
        for el in header_kids:
            if etree.QName(el).localname == 'tbl' and is_navtbl(el):
                tblpr = el.find(q('tblPr'))
                w = tblpr.find(q('tblW')) if tblpr is not None else None
                navtbl = {'tblW': int(w.get(q('w'))) if w is not None else 0, 'zone': '头部单栏区'}
                break
        if navtbl is None:
            for el in body_kids:
                if etree.QName(el).localname == 'tbl' and is_navtbl(el):
                    tblpr = el.find(q('tblPr'))
                    w = tblpr.find(q('tblW')) if tblpr is not None else None
                    navtbl = {'tblW': int(w.get(q('w'))) if w is not None else 0, 'zone': '双栏正文区(缺陷)'}
                    break
    # 统计行/图例行落区补查（落正文区＝缺陷）
    if brk is not None:
        for el in body_kids:
            if etree.QName(el).localname != 'p':
                continue
            t = ptext(el)
            if stats_row is None and RE_STATS_ROW.match(t):
                stats_row = t
                stats_row_in_header = False
            elif RE_LEGEND.match(t) and t not in legends:
                legends.append(t)
                legends_in_header.append(False)
    # 正文首块特征与锚点候选。
    # 锚点定族（2026-09-06 收尾-B v3 更正）：前置步0「锚点＝正文首块机读特征」——取文档序第一个
    # 条目号/题号块之族；旧「带题件→题号块」预设系②-E 断言①假阴性 5/10 之根因（讲部补挂后
    # 讲练/衔接件首块＝条目号、题号块落第2页）。首块特征栏仍实测登记。
    first_blocks = []
    anchor = None
    first_token = first_tqh = first_tmh = first_secstat = None
    RE_QK = re.compile(r'^（(?:简单|中档|难|衔接必会)')
    for el in body_kids:
        if etree.QName(el).localname != 'p':
            continue
        t = ptext(el).strip()
        if not t:
            continue
        ppr = el.find(q('pPr'))
        fill = style = None
        if ppr is not None:
            shd = ppr.find(q('shd'))
            if shd is not None:
                fill = shd.get(q('fill'))
            ps = ppr.find(q('pStyle'))
            if ps is not None:
                style = ps.get(q('val'))
        if len(first_blocks) < 3:
            first_blocks.append({'text': t, 'fill': fill, 'style': style})
        mstat = re.match(r'^(\d+(?:\.\d+)+)[ 　]+(.+?)[ 　]*本节\d+题', t)
        mtok = re.match(r'^(\d+(?:\.\d+)+-\d+．)', t)
        if first_secstat is None and mstat:
            first_secstat = {'family': '节标题统计行式',
                             'regex': r'^' + re.escape(mstat.group(1)) + re.escape(nospc(mstat.group(2))) + r'本节\d+题',
                             'source': t}
        if mtok:
            tok = mtok.group(1)
            if first_token is None:
                first_token = ({'family': '题号块式', 'regex': r'^' + re.escape(tok), 'source': t}
                               if RE_QK.match(t[len(tok):]) else
                               {'family': '条目号式',
                                'regex': r'^' + re.escape(tok) + re.escape(nospc(t[len(tok):len(tok) + 8])),
                                'source': t})
            if first_tqh is None and RE_QK.match(t[len(tok):]):
                first_tqh = {'family': '题号块式', 'regex': r'^' + re.escape(tok), 'source': t}
            elif first_tmh is None and not RE_QK.match(t[len(tok):]):
                first_tmh = {'family': '条目号式',
                             'regex': r'^' + re.escape(tok) + re.escape(nospc(t[len(tok):len(tok) + 8])),
                             'source': t}
        if first_tqh and first_tmh and first_secstat and len(first_blocks) >= 3:
            break
    anchor = first_token or first_secstat or first_tqh or first_tmh
    blacklist = set()
    if stats_row:
        blacklist.add(stats_row)
    blacklist.update(legends)
    return {'page': page, 'title': title_txt, 'stats_row': stats_row, 'legends': legends,
            'stats_row_in_header': stats_row_in_header, 'legends_in_header': legends_in_header,
            'navtbl': navtbl, 'first_blocks': first_blocks, 'anchor': anchor,
            'blacklist': sorted(blacklist), 'has_break': brk is not None}


def body_blocks(pdf_path, page):
    """首页正文区文本块（剔除页眉页脚带：几何带＋同串签名双判据——品牌前缀可省略的件以
    「本n/共M本…第X页」同串形态补判；页脚带下界放宽18pt且须形态命中，防误剔正文末行）。
    返回 (全部块数, 正文区行列表，行文本已去全部空白)。"""
    import pymupdf
    doc = pymupdf.open(pdf_path)
    pg = doc[0]
    blocks = pg.get_text('blocks')
    n_all = len(blocks)
    lines = []
    hf_pat = re.compile(r'本\d+/共\d+本|第\d+页|羿郭工作室')
    for b in blocks:
        x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
        yc = (y0 + y1) / 2
        if yc <= page['mt']:
            continue
        if yc >= page['h'] - page['mb']:
            continue
        if HF_SIG in text:
            continue
        if yc >= page['h'] - page['mb'] - 18 and hf_pat.search(nospc(text)):
            continue
        lines.append({'bbox': (x0, y0, x1, y1), 'text': text})
    doc.close()
    return n_all, lines


def assert1(pdf_path, page, anchor_re, stem):
    """断言①首页正文成立（去空白归一化行上匹配锚点正则；2026-09-06 v3适配：另试块级拼行——
    锚点串被双栏折行劈开时仍可命中）。返回 (结论, 细节)。"""
    n_all, lines = body_blocks(pdf_path, page)
    if n_all == 0:
        return '不判定', '首页可抽取块数=0（fail-closed）'
    rx = re.compile(anchor_re)
    stem_n = nospc(stem)
    for ln in lines:
        segs = [nospc(seg) for seg in ln['text'].split('\n')]
        segs.append(nospc(ln['text']))              # 块级拼行（拆行容错）
        for seg in segs:
            if rx.match(seg):
                if seg == stem_n:
                    return 'FAIL', '锚点块与文件名主干同串'
                return 'PASS', '锚点命中: %s @y=%.0f' % (seg[:40], ln['bbox'][1])
    return 'FAIL', '首页正文区未见锚点块（块数=%d 正文区行数=%d）' % (n_all, len(lines))


def assert2(pdf_path, info):
    """断言②头部要素通栏（逐要素；缺席逐要素登记不适用原因）。
    段落型要素：PDF侧x0对基准±2pt（左对齐短行宽度随文本、不作判据）＋XML侧落区（头部节分节符之前＝单栏区）；
    章首导航表：XML侧 tblW 对基准±40缇＋落区断言，PDF侧 find_tables 表框宽对基准±2pt（栏宽挤压＝缺陷）。"""
    import pymupdf
    page = info['page']
    x0_ref = page['ml']
    w_ref = page['w'] - page['ml'] - page['mr']
    rows = []
    targets = []
    if info['stats_row']:
        targets.append(('全件统计行', info['stats_row'], info['stats_row_in_header']))
    else:
        rows.append(('全件统计行', '不适用', '本件无全件统计行要素'))
    if info['legends']:
        for lg, hd in zip(info['legends'], info['legends_in_header']):
            targets.append(('图例行', lg, hd))
    else:
        rows.append(('〔基〕/〔进〕图例行', '不适用', '本件无图例行要素'))
    doc = pymupdf.open(pdf_path)
    pg = doc[0]
    blocks = pg.get_text('blocks')
    try:
        tables = pg.find_tables().tables
    except Exception:
        tables = []
    pg_drawings = pg.get_drawings()   # 2026-09-04 子步3：边线法导航表宽测量在 close 前取数
    doc.close()
    for name, txt, in_header in targets:
        key = nospc(txt[:12])
        hit = None
        for b in blocks:
            if HF_SIG in b[4]:
                continue
            if key in nospc(b[4]):
                hit = b
                break
        if hit is None:
            rows.append((name, 'FAIL', '首页PDF未检出要素块: ' + key))
            continue
        x0, wdt = hit[0], hit[2] - hit[0]
        ok = abs(x0 - x0_ref) <= 2 and in_header
        rows.append((name, 'PASS' if ok else 'FAIL',
                     'x0=%.1f(基准%.1f±2) 渲染宽=%.1f XML落区=%s' % (x0, x0_ref, wdt, '头部单栏区' if in_header else '双栏正文区(缺陷)')))
    # 导航表：XML侧 tblW 与落区 ＋ PDF侧表框宽
    if info['navtbl']:
        w_tw = info['navtbl']['tblW']
        ref_tw = int(round(w_ref / TW2PT))
        zone = info['navtbl']['zone']
        xml_ok = abs(w_tw - ref_tw) <= 40 and zone == '头部单栏区'
        pdf_note = ''
        pdf_ok = True
        if tables:
            # 2026-09-04 子步3补丁：内容感知选表——讲部补挂后首页出现条目区表格（对比辨析表等），
            # find_tables 可能把导航表与条目表/底纹行误并为单一大表（B卷首页实测 bbox 37~595×85~782）。
            # 导航表按表头文本（节名＋题量）锁定且宽度须合基准；无合基准候选时改走边线法：
            # 导航表 y 窗（表头「节名…题量」块顶～「合计」块底）内竖直边线对（长>15pt）的最外 x 跨度。
            cand = None
            for t in tables:
                try:
                    grid_txt = ''.join(''.join(cell or '' for cell in row) for row in t.extract())
                except Exception:
                    grid_txt = ''
                # 2026-09-04 子步6补丁：四列化后表头抽层把「题量」拆块（实测块文本「节名题」），
                # 节名＋题量联合锁定失效——放宽为「节名」单锁（首页仅此一处含节名）。
                if '节名' in grid_txt:
                    w_c = t.bbox[2] - t.bbox[0]
                    if abs(w_c - w_ref) <= 2:
                        cand = t
                        break
                    cand = cand or t   # 命中表头但宽度不合基准：留作记录，继续找
            fb_note = ''
            if cand is not None and abs(cand.bbox[2] - cand.bbox[0] - w_ref) <= 2:
                tw = cand.bbox[2] - cand.bbox[0]
            else:
                # —— 边线法 ——
                import re as _re
                y0 = y1 = None
                for b in blocks:
                    tt = _re.sub(r'\s+', '', b[4])
                    if y0 is None and '节名' in tt:   # 子步6：题量拆块，单锁节名
                        y0 = b[1]
                    if '合计' in tt:
                        y1 = b[3]
                tw = None
                if y0 is not None and y1 is not None:
                    vxs = []
                    for d in pg_drawings:
                        r = d['rect']
                        if r.y1 < y0 - 2 or r.y0 > y1 + 2:
                            continue
                        for it in d['items']:
                            if it[0] == 'l':
                                l = it[1]
                                if abs(l.y1 - l.y0) > 15:
                                    vxs += [l.x0, l.x1]
                            elif it[0] == 're':
                                rr = it[1]
                                if rr.height > 15 and rr.width < 6:
                                    vxs += [rr.x0, rr.x1]
                    if vxs:
                        tw = max(vxs) - min(vxs)
                if tw is None:
                    pdf_ok = False
                    pdf_note = ' 首页PDF导航表宽不可测（find_tables误并＋边线法失败）'
                    rows.append(('章首导航表', 'FAIL',
                                 'tblW=%d缇(基准%d缇±40) 落区=%s%s' % (w_tw, ref_tw, zone, pdf_note)))
                    return rows
                fb_note = '（边线法：find_tables误并回退）'
            pdf_ok = abs(tw - w_ref) <= 2
            pdf_note = ' PDF表框宽=%.1f(基准%.1f±2)%s' % (tw, w_ref, fb_note)
        else:
            pdf_note = ' 首页PDF未检出表格块'
        rows.append(('章首导航表', 'PASS' if (xml_ok and pdf_ok) else 'FAIL',
                     'tblW=%d缇(基准%d缇±40) 落区=%s%s' % (w_tw, ref_tw, zone, pdf_note)))
    else:
        rows.append(('章首导航表', '不适用', '本件无章首导航表要素'))
    return rows


def assert5(full_pdf, stem, info, is_first_vol):
    """断言⑤分卷标题（全件PDF第1页）。返回 (结论, 细节)。"""
    import pymupdf
    doc = pymupdf.open(full_pdf)
    pg = doc[0]
    blocks = pg.get_text('blocks')
    doc.close()
    norm = lambda s: re.sub(r'\s+', '', s)
    for b in blocks:
        if norm(b[4]) == norm(stem):
            return 'FAIL', '第1页出现与文件名主干同串标题块: ' + b[4].strip()[:50]
    title_xml = norm(info['title'])
    if not is_first_vol:
        # 后续卷：第1页不得出现任何单位文内标题形态块
        for b in blocks:
            if re.search(r'人教B版.*·(衔接件|知识清单|讲练件)', norm(b[4])):
                return 'FAIL', '后续卷第1页出现文内开头标题: ' + b[4].strip()[:50]
        return 'PASS', '后续卷零文内标题'
    # 首卷/单件：标题块在位且全章口径（题量括注在、无范围/卷次括注）
    found = False
    for b in blocks:
        if title_xml and title_xml in norm(b[4]):
            found = True
            t = norm(b[4])
            if RE_PAGERANGE.search(t):
                return 'FAIL', '首卷标题含范围/卷次括注: ' + b[4].strip()[:50]
            if not RE_COUNT.search(t):
                return 'FAIL', '首卷标题缺全章题量口径: ' + b[4].strip()[:50]
    if not found:
        return 'FAIL', '首卷/单件第1页未检出文内开头标题（XML标题=' + info['title'][:40] + '）'
    return 'PASS', '首卷/单件标题全章口径在位'


def gen_mapping(pairs, out):
    rows, data = [], {}
    for code, path in pairs:
        info = inspect_docx(path)
        a = info['anchor']
        fn = os.path.basename(path)
        stem = file_stem(fn)
        fb = info['first_blocks'][0] if info['first_blocks'] else {'text': '', 'fill': None, 'style': None}
        if a is None:
            rows.append((code, '皆不匹配', '—', '首块纯图或其他: ' + fb['text'][:30]))
            continue
        # 反向校验：锚点源串禁与头部要素全串相同（黑名单全串匹配）
        rev = '通过'
        if a['source'] in info['blacklist']:
            rev = '违规：锚点源串命中头部要素黑名单'
        elif a['source'] == stem:
            rev = '违规：锚点源串＝文件名主干'
        rows.append((code, a['family'], a['regex'], '首块[%s] fill=%s style=%s｜锚源: %s｜反向校验:%s'
                     % (fb['text'][:24], fb['fill'], fb['style'], a['source'][:40], rev)))
        data[code] = {'file': fn, 'stem': stem, 'anchor': a, 'info_page': info['page'],
                      'stats_row': info['stats_row'], 'legends': info['legends'],
                      'stats_row_in_header': info['stats_row_in_header'],
                      'legends_in_header': info['legends_in_header'],
                      'navtbl': info['navtbl'], 'title': info['title'], 'has_break': info['has_break'],
                      'blacklist': info['blacklist']}
    md = ['# 锚点映射表v1（子步0实测生成；主会话据此登记附则《双栏首页断言》前置步0）', '',
          '| 代号 | 锚点族 | 机读正则 | 实际首块特征/锚源/反向校验 |', '|---|---|---|---|']
    for r in rows:
        md.append('| ' + ' | '.join(x.replace('|', '｜') for x in r) + ' |')
    with open(os.path.join(out, '锚点映射表v1.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    with open(os.path.join(out, '锚点映射表v1.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('映射表已生成: %d 行' % len(rows))
    for r in rows:
        print(' ', r[0], r[1], 'rev-check:', r[3][-20:])


def make_p1(pairs, out):
    """首页PDF：裁剪全件PDF（主路径产物）第1页。注：本环境Word→PDFCreator链路实测忽略
    PrintOut Range/From/To/Pages（三种写法2026-09-03各测一次均全件输出），故首页件以同管线
    全件PDF的第1页裁剪获得——渲染源一致、非ExportAsFixedFormat，合附则⑥主路径要求。"""
    import pymupdf
    p1dir = os.path.join(out, '首页PDF')
    os.makedirs(p1dir, exist_ok=True)
    for code, path in pairs:
        dst = os.path.join(p1dir, code + '_p1.pdf')
        if os.path.exists(dst):
            print('[%s] 首页PDF已存在，跳过（幂等）' % code)
            continue
        full = os.path.join(out, 'pdf', code + '.pdf')
        if not os.path.exists(full):
            print('[%s] 全件PDF缺失，无法裁剪首页' % code)
            continue
        d = pymupdf.open(full)
        nd = pymupdf.open()
        nd.insert_pdf(d, from_page=0, to_page=0)
        nd.save(dst)
        nd.close()
        d.close()
        print('[%s] 首页PDF裁剪完成 %dKB' % (code, os.path.getsize(dst) // 1024))


def run_assertions(pairs, out, negative=None, neg_code=None, mapping_path=None):
    # 2026-09-06 收尾-B：--mapping 可直载附则注册锚点映射表（v3，PDF 终态实测定标＝权威源）；
    # 缺省仍用本目录自产 锚点映射表v1.json（docx 实测，题名内嵌公式件文字层不可见）。
    mpath = mapping_path or os.path.join(out, '锚点映射表v1.json')
    mapping = json.load(open(mpath, encoding='utf-8'))
    results = {}
    for code, path in pairs:
        ent = mapping[code]
        info = {'page': ent['info_page'], 'stats_row': ent['stats_row'], 'legends': ent['legends'],
                'stats_row_in_header': ent.get('stats_row_in_header', False),
                'legends_in_header': ent.get('legends_in_header', []),
                'navtbl': ent['navtbl'], 'title': ent['title']}
        p1 = os.path.join(out, '首页PDF', code + '_p1.pdf')
        if not os.path.exists(p1):
            p1 = os.path.join(out, 'pdf', code + '.pdf')   # 断言①②读全件PDF第1页（渲染源一致）
        full = os.path.join(out, 'pdf', code + '.pdf')
        res = {'blocked': False}
        try:
            if not os.path.exists(p1):
                res['a1'] = ('不判定', '首页PDF缺失（fail-closed）')
                res['blocked'] = True
                res['a2'] = [('全部要素', '不判定', '首页PDF缺失')]
            else:
                res['a1'] = assert1(p1, ent['info_page'], ent['anchor']['regex'], ent['stem'])
                res['a2'] = assert2(p1, info)
            is_first = bool(ent['title'])   # 有文内开头标题＝首卷/单件；后续卷无
            if os.path.exists(full):
                res['a5'] = assert5(full, ent['stem'], info, is_first)
            else:
                res['a5'] = ('不判定', '全件PDF缺失')
        except Exception as e:
            res = {'blocked': True, 'error': repr(e)}
        results[code] = res
    if negative and neg_code:
        ent = mapping[neg_code]
        try:
            c, det = assert1(negative, ent['info_page'], ent['anchor']['regex'], ent['stem'])
            results['阴性对照'] = {'a1': (c, det), 'expect': 'FAIL',
                                 'ok': (c == 'FAIL')}
        except Exception as e:
            results['阴性对照'] = {'error': repr(e), 'ok': False}
    # 报告
    md = ['# 首页断言集执行报告（断言①②⑤＋阴性对照；fail-closed）', '',
          '## 断言①（首页正文成立）', '', '| 代号 | 结论 | 细节 |', '|---|---|---|']
    for code, _ in pairs:
        r = results[code]
        if 'error' in r:
            md.append('| %s | 不判定 | 脚本异常 %s |' % (code, r['error'][:60]))
        else:
            md.append('| %s | %s | %s |' % (code, r['a1'][0], r['a1'][1].replace('|', '｜')))
    if '阴性对照' in results:
        nc = results['阴性对照']
        md.append('| 阴性对照(衔接2缺陷态) | %s（期望FAIL） | %s |'
                  % (nc.get('a1', ('?', '?'))[0], nc.get('a1', ('', ''))[1].replace('|', '｜')))
    md += ['', '## 断言②（头部要素通栏）', '', '| 代号 | 要素 | 结论 | 实测 |', '|---|---|---|---|']
    for code, _ in pairs:
        r = results[code]
        for row in r.get('a2', []):
            md.append('| %s | %s | %s | %s |' % (code, row[0], row[1], row[2].replace('|', '｜')))
    md += ['', '## 断言⑤（分卷标题，全件PDF第1页）', '', '| 代号 | 结论 | 细节 |', '|---|---|---|']
    for code, _ in pairs:
        r = results[code]
        a5 = r.get('a5', ('不判定', '脚本异常'))
        md.append('| %s | %s | %s |' % (code, a5[0], a5[1].replace('|', '｜')))
    with open(os.path.join(out, '首页断言报告.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    with open(os.path.join(out, '首页断言结果.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    npass = sum(1 for c, _ in pairs if results[c].get('a1', ('', ''))[0] == 'PASS')
    print('断言① PASS %d/%d；阴性对照: %s' % (npass, len(pairs), results.get('阴性对照', {}).get('a1')))


def main():
    args, opts, i = [], {}, 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a.startswith('--'):
            if '=' in a:
                k, v = a.split('=', 1)
                opts[k] = v
            elif a in ('--out', '--negative', '--neg-code', '--mapping') and i + 1 < len(sys.argv):
                opts[a] = sys.argv[i + 1]
                i += 1
            else:
                opts[a] = True
        else:
            args.append(a)
        i += 1
    out = os.path.abspath(str(opts.get('--out', '.')))
    os.makedirs(out, exist_ok=True)
    pairs = []
    for a in args:
        if '=' in a:
            pairs.append(tuple(a.split('=', 1)))
    if '--gen-mapping' in opts:
        gen_mapping(pairs, out)
    if '--make-p1' in opts:
        make_p1(pairs, out)
    if '--run' in opts:
        run_assertions(pairs, out, opts.get('--negative'), opts.get('--neg-code'),
                       opts.get('--mapping'))


if __name__ == '__main__':
    main()
