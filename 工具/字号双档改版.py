# -*- coding: utf-8 -*-
#
# 新建：2026-08-31 欠账A版式改版回扫轮·T3（工具债⑨）——公共规则§7段落条款N1/N2落地
#   依据：公共规则§7（字号双档N1：正文24半点/解析18半点；行距分级N2：正文line=410 atLeast/
#   解析line=280 atLeast，行距例外仅页眉一类）、§7排版自检⑧（docDefaults显式、禁主题字体、
#   禁模板默认after=200/line=276）、经验文件（docDefaults双修、docGrid行网格坑——保网格64页vs
#   关网格59页、PUA字符run跳过、oMath不碰）、规格书§1参数速查。
#
r"""字号双档改版.py — N1字号双档＋N2行距分级批量改版（幂等、可整册批量、逐件落盘计数）

分档（run字号，w:sz/w:szCs）:
  解析档=18半点: 凡行内【×】栏目标签行（【答案】【知识点】【分析】【详解】【点睛】【编注】
    【大招指引】【题后反思】【温馨提醒】【定义】【结论】等——开放式匹配）、题内解析块全部
    延续段（块边界=下一题号/标题）、题型通式句与编注说明句（均【编注】起段）、全件/本节统计行
    （^全件N题 / ^本节N题）、〔基〕/〔进〕图例行（^〔基〕＝）、章首导航表全部单元格段落、
    节标题行内统计段（「本节N题：…」起——N11合并后形态，run级切分）。
    讲部（方法讲解｜）区内的【×】标签行只标标签行本身，其后续讲解段＝讲部正文（正文档）。
  正文档=24半点: 其余正文run（题干、选项、知识清单条目题名行与条目正文、讲部/讲部分正文、
    衔接件正文、非导航表单元格段落）。
  标题段run不归本工具（章/讲32、节28、讲部/题型24由T4工具负责）——整段跳过并计数登记
    （段内统计段run除外）；标题段行距仍归本工具（正文档410值——行距例外仅页眉一类）。

行距（段落w:spacing）: 解析档段 line=280 lineRule=atLeast；正文档/标题段 line=410 atLeast；
  一律 before=0 after=0；表格内单元格段落同规；页眉段落一律跳过（无显式spacing的页眉段冻结
  为现继承值 line=288 auto，防 docDefaults 修改的连带抬升——冻结不改现行渲染）；页脚跳过
  不动（M1盖章统一重写）。

docDefaults双修（styles.xml）: rPrDefault 显式 rFonts(ascii/hAnsi=Times New Roman,
  eastAsia=宋体, cs=Times New Roman)+sz/szCs=24，禁主题字体；pPrDefault 显式
  spacing before/after=0 line=410 atLeast，禁模板默认after=200/line=276。

docGrid防线: document.xml 各 sectPr 的 w:docGrid type=lines/linesAndChars（行网格）即归一
  type=default；type缺失/default 等非行网格形态记录不动。

安全边界: m:oMath/m:oMathPara 子树不碰（只取 w:r，m:r 天然不触）；PUA字符(U+E000–U+F8FF)
  run 跳过字号与字体；含 w:drawing 的 run 跳过 rFonts 改写（无文字的纯图run连 sz 一并跳过）；
  w:txbxContent 等图形内部 run 不触；文字零增删（w:t/m:t 流前后恒等断言，不过即退出码2不落盘）。

分类不确定性兜底: 题号门控（^\d+．（ 且 n=期望值才判题号块）编号异常、解析区内疑似题号、
  详解分栏表嫌疑等一律登记「待人工」清单落盘 JSON，不擅自猜。

用法:
  python 字号双档改版.py <in.docx> <out.docx> [--qstart N] [--qcount M] [--json <报告.json>]
  python 字号双档改版.py --batch <outdir> <in1.docx> <in2.docx> ... [--qstart N] [--qcount M]
批量模式逐件落盘: <outdir>/<原名>.docx ＋ <outdir>/<原名>.字号双档.json
幂等: 对已改版件重跑输出语义等价（set-to-value 语义，无累积改写；幂等铁证=zip成员级DIFF=0）。
"""
import sys, io, os, re, json, copy, time, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLNS_SPACE = '{http://www.w3.org/XML/1998/namespace}space'

def q(t):
    return '{%s}%s' % (W, t)

# ---------- OOXML 元素序（插入定位用） ----------
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike',
             'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid',
             'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs',
             'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs',
             'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath']
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
             'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
             'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
             'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing',
             'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
             'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']

SZ_BODY, SZ_ANS = '24', '18'
LINE_BODY, LINE_ANS = '410', '280'

PUA_RE = re.compile(r'[\uE000-\uF8FF]')
RE_LECT = re.compile(r'^\d+(\.\d+)*\s*方法讲解[｜|]')
RE_NUMTITLE = re.compile(r'^\d+(\.\d+)+\s+\S')
RE_QSTART = re.compile(r'^(\d{1,4})．（')
RE_ENTRY = re.compile(r'^\d{1,4}．')
RE_LABEL = re.compile(r'^【[^】]{1,30}】')
RE_STATS = re.compile(r'^(?:本节|全件)\d+题')
RE_LEGEND = re.compile(r'^〔基〕＝')
RE_INSTATS = re.compile(r'本节\d+题')
THEME_MAP = {'asciiTheme': ('ascii', 'Times New Roman'),
             'hAnsiTheme': ('hAnsi', 'Times New Roman'),
             'eastAsiaTheme': ('eastAsia', '宋体'),
             'cstheme': ('cs', 'Times New Roman')}


def local(el):
    try:
        return etree.QName(el).localname
    except ValueError:
        return ''


def ptext(el):
    return ''.join(t.text or '' for t in el.iter(q('t')))


def text_stream(root):
    """w:t/m:t 流（localname 皆为 t），文档序"""
    return [t.text or '' for t in root.iter() if isinstance(t.tag, str) and local(t) == 't']


def ordered_child(parent, tag, order_list):
    """取/建 parent 的 tag 子元素；新建时按 OOXML 序插到正确位置"""
    el = parent.find(q(tag))
    if el is not None:
        return el
    el = etree.Element(q(tag))
    idx = order_list.index(tag)
    for ch in parent:
        name = local(ch)
        if name in order_list and order_list.index(name) > idx:
            ch.addprevious(el)
            return el
    parent.append(el)
    return el


def set_spacing(p, line, rule='atLeast'):
    """段 p 设 pPr/spacing before/after=0 line=<line> lineRule=<rule>（in-place 或有序新建）"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    sp = ordered_child(ppr, 'spacing', PPR_ORDER)
    sp.set(q('before'), '0')
    sp.set(q('after'), '0')
    sp.set(q('line'), line)
    sp.set(q('lineRule'), rule)


def set_run_sz(r, halfpt):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr'))
        r.insert(0, rpr)
    for stag in ('sz', 'szCs'):
        ordered_child(rpr, stag, RPR_ORDER).set(q('val'), halfpt)


def run_kind(r):
    """'skip'（纯图/PUA——sz与rFonts全跳）| 'img'（含drawing但有文字——只跳rFonts）| 'text'"""
    has_t = any(t.text for t in r.findall(q('t')))
    if r.find(q('drawing')) is not None or r.find(q('pict')) is not None \
            or r.find(q('object')) is not None:
        return 'img' if has_t else 'skip'
    for t in r.findall(q('t')):
        if t.text and PUA_RE.search(t.text):
            return 'skip'
    return 'text'


def under_drawing(r):
    a = r.getparent()
    while a is not None:
        n = local(a)
        if n in ('drawing', 'pict', 'txbxContent', 'object'):
            return True
        a = a.getparent()
    return False


def normalize_rfonts(r, rc):
    """run 级主题字体属性 → 显式字体（禁 minorHAnsi/minorEastAsia 隐性继承）"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        return
    rf = rpr.find(q('rFonts'))
    if rf is None:
        return
    hit = False
    for att, (name, val) in THEME_MAP.items():
        if rf.get(q(att)) is not None:
            del rf.attrib[q(att)]
            rf.set(q(name), val)
            hit = True
    if hit:
        rc['主题字体run改写'] += 1


def split_run_at(r, k):
    """把 run r 的 w:t 文本在第 k 字符处切成两个 run（r=前半，返回后半）；零字符增删"""
    t_el = r.find(q('t'))
    txt = t_el.text or ''
    r2 = copy.deepcopy(r)
    t2 = r2.find(q('t'))
    t_el.text = txt[:k]
    t2.text = txt[k:]
    for e in (t_el, t2):
        e.set(XMLNS_SPACE, 'preserve')
    r.addnext(r2)
    return r2


def heading23_styleids(styles_root):
    ids = set()
    for st in styles_root.findall(q('style')):
        nm = st.find(q('name'))
        if nm is not None and nm.get(q('val')) in ('heading 2', '标题2', 'heading 3', '标题3'):
            sid = st.get(q('styleId'))
            if sid:
                ids.add(sid)
    return ids


def classify_title(text, pstyle, h3ids, is_first_content):
    """标题类型 or None（chapter/section/lecture/group；判定同源 extract_structure）"""
    if is_first_content:
        return 'chapter'
    if pstyle in h3ids and RE_NUMTITLE.match(text):
        return 'section'
    if RE_LECT.match(text):
        return 'lecture'
    if RE_NUMTITLE.match(text):
        return 'group' if '：' in text else 'section'
    return None


def process(path_in, path_out, qstart=1, qcount=None, json_path=None):
    t0 = time.time()
    zin = zipfile.ZipFile(path_in)
    members = zin.namelist()
    parts = {n: zin.read(n) for n in members}
    zin.close()

    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)
    stream_before = text_stream(doc)
    para_count_before = len(list(body.iter(q('p'))))
    tbl_count_before = len(list(body.iter(q('tbl'))))

    styles = etree.fromstring(parts['word/styles.xml'])
    h3ids = heading23_styleids(styles)

    log = {
        '输入': os.path.basename(path_in),
        '分类计数': {'标题段跳过': 0, '标题段·章': 0, '标题段·节': 0, '标题段·讲部': 0,
                  '标题段·题型': 0, '正文段': 0, '解析段': 0, '导航表单元格段': 0,
                  '内容表单元格段': 0, '表数': 0, '题号块数': 0, '条目题名行数': 0,
                  '标签行数·题内': 0, '标签行数·独立': 0, '统计行数': 0, '图例行数': 0,
                  '标题行内统计段run切分': 0},
        'run计数': {'sz置24run数': 0, 'sz置18run数': 0, '标题豁免run数(留T4)': 0,
                 '纯图run跳过': 0, 'PUA run跳过': 0, '图形内部run跳过': 0, '主题字体run改写': 0,
                 '段落标记sz置18数': 0, '段落标记主题字体改写数': 0},
        '行距计数': {'line=410段数': 0, 'line=280段数': 0},
        '安全': {'修订标记w:ins/w:del': None},
        '待人工': [],
    }
    exempt_ids = set()   # 标题段豁免sz的run（T4负责）
    exempt_keep = []     # 持活豁免run代理至断言结束：防lxml代理GC后id()地址回收致复核断言随机假失败
                         # （2026-08-31 W-E实测：首跑3/复跑10处假失败；F-工具补丁入库，覆盖全部add位点）

    # ---------- 主遍历：分档分类 + 字号 + 行距 ----------
    zone = 'INIT'          # INIT/LECT/STEM/ANS
    expected = qstart
    first_content_seen = False

    def para_runs(p):
        """段落全部 w:r（文档序，含 hyperlink 内），排除图形/文本框内部"""
        rs = []
        for r in p.iter(q('r')):
            if under_drawing(r):
                log['run计数']['图形内部run跳过'] += 1
            else:
                rs.append(r)
        return rs

    def do_runs(p, cls, stats_from=None):
        """cls='正文'|'解析'（全run置档位sz）；cls='标题'（run豁免留T4；
        stats_from=段内统计段起始偏移，其后run置18、跨界run切分）"""
        rc = log['run计数']
        if cls not in ('正文', '解析', '标题'):
            raise ValueError(cls)
        rs = para_runs(p)
        off = 0
        for i, r in enumerate(rs):
            kind = run_kind(r)
            t_el = r.find(q('t'))
            tlen = len(t_el.text or '') if t_el is not None else 0
            if kind == 'skip':
                if any(t.text and PUA_RE.search(t.text) for t in r.findall(q('t'))):
                    rc['PUA run跳过'] += 1
                else:
                    rc['纯图run跳过'] += 1
                off += tlen
                continue
            if cls == '标题':
                if stats_from is None:
                    rc['标题豁免run数(留T4)'] += 1
                    exempt_ids.add(id(r)); exempt_keep.append(r)
                    normalize_rfonts(r, rc)
                    off += tlen
                    continue
                if off + tlen <= stats_from:
                    rc['标题豁免run数(留T4)'] += 1
                    exempt_ids.add(id(r)); exempt_keep.append(r)
                    normalize_rfonts(r, rc)
                    off += tlen
                    continue
                if off < stats_from and t_el is not None and tlen > 0:
                    r = split_run_at(r, stats_from - off)
                    # 2026-08-31 F-工具补丁审计修：原「rc['标题行内统计段run切分'] += 1」系错挂run计数
                    # （键只在分类计数有初值——首触发即KeyError，本行与下行重复），删错行、保下行唯一计数
                    log['分类计数']['标题行内统计段run切分'] += 1
                    rc['标题豁免run数(留T4)'] += 1
                    exempt_ids.add(id(rs[i])); exempt_keep.append(rs[i])
                    off = stats_from
                    tlen = len(r.find(q('t')).text or '')
                set_run_sz(r, SZ_ANS)
                rc['sz置18run数'] += 1
                normalize_rfonts(r, rc)
                off += tlen
                continue
            base = {'正文': SZ_BODY, '解析': SZ_ANS}[cls]
            set_run_sz(r, base)
            rc['sz置%srun数' % base] += 1
            if kind != 'img':
                normalize_rfonts(r, rc)
            else:
                rc['纯图run跳过'] += 0  # 图run带文字：sz照设、rFonts跳过

    def do_para(p, cls, stats_from=None):
        line = LINE_ANS if cls == '解析' else LINE_BODY
        set_spacing(p, line)
        log['行距计数']['line=%s段数' % line] += 1
        if cls in ('正文', '解析'):
            log['分类计数'][cls + '段'] += 1
        do_runs(p, cls, stats_from)
        # 段落标记（pPr>rPr）：解析段标记显式18（防docDefaults 24隐性抬高末行）；
        # 既有标记rPr的主题字体属性一律显式化（禁主题字体）
        ppr = p.find(q('pPr'))
        if ppr is None and cls == '解析':
            ppr = etree.Element(q('pPr'))
            p.insert(0, ppr)
        if ppr is not None:
            mrpr = ppr.find(q('rPr'))
            if mrpr is None and cls == '解析':
                mrpr = ordered_child(ppr, 'rPr', PPR_ORDER)
            if mrpr is not None:
                if cls == '解析':
                    for stag in ('sz', 'szCs'):
                        ordered_child(mrpr, stag, RPR_ORDER).set(q('val'), SZ_ANS)
                    log['run计数']['段落标记sz置18数'] += 1
                rf3 = mrpr.find(q('rFonts'))
                if rf3 is not None:
                    for att, (name, val) in THEME_MAP.items():
                        if rf3.get(q(att)) is not None:
                            del rf3.attrib[q(att)]
                            rf3.set(q(name), val)
                            log['run计数']['段落标记主题字体改写数'] += 1

    for bi, el in enumerate(els):
        tag = local(el)
        if tag == 'sectPr':
            continue
        if tag == 'tbl':
            log['分类计数']['表数'] += 1
            rows = el.findall(q('tr'))
            frow = ptext(rows[0]) if rows else ''
            is_nav = ('题型组数' in frow) or ('节名' in frow and '题号区间' in frow)
            if not is_nav and zone == 'ANS':
                log['待人工'].append({'元素序': bi, '类型': '详解分栏表嫌疑（解析区内非导航表）',
                                      '首行': frow[:30], '处置': '本件按解析档280处理，人工复核'})
            for p in el.iter(q('p')):
                if is_nav:
                    log['分类计数']['导航表单元格段'] += 1
                    do_para(p, '解析')
                else:
                    log['分类计数']['内容表单元格段'] += 1
                    do_para(p, '解析' if zone == 'ANS' else '正文')
            continue
        if tag != 'p':
            continue
        text = ptext(el)
        ps = el.find(q('pPr'))
        pstyle = ''
        if ps is not None:
            pst = ps.find(q('pStyle'))
            pstyle = pst.get(q('val')) if pst is not None else ''

        if not text.strip():
            do_para(el, '解析' if zone == 'ANS' else '正文')
            continue

        tkind = classify_title(text, pstyle, h3ids, not first_content_seen)
        if tkind:
            first_content_seen = True
            log['分类计数']['标题段跳过'] += 1
            log['分类计数']['标题段·' + {'chapter': '章', 'section': '节',
                                    'lecture': '讲部', 'group': '题型'}[tkind]] += 1
            zone = 'LECT' if tkind == 'lecture' else 'INIT'
            mstat = RE_INSTATS.search(text)
            set_spacing(el, LINE_BODY)
            log['行距计数']['line=410段数'] += 1
            do_runs(el, '标题', stats_from=mstat.start() if mstat else None)
            continue
        first_content_seen = True

        mq = RE_QSTART.match(text)
        if mq:
            n = int(mq.group(1))
            if n == expected:
                expected += 1
                log['分类计数']['题号块数'] += 1
                zone = 'STEM'
                do_para(el, '正文')
                continue
            if zone == 'ANS':
                log['待人工'].append({'元素序': bi, '类型': '解析区内疑似题号（编号≠期望，判解析延续）',
                                      '文本': text[:30], '期望题号': expected, '实际': n})
                do_para(el, '解析')
                continue
            log['待人工'].append({'元素序': bi, '类型': '题号编号异常（仍按题号块处理）',
                                  '文本': text[:30], '期望题号': expected, '实际': n})
            expected = n + 1
            log['分类计数']['题号块数'] += 1
            zone = 'STEM'
            do_para(el, '正文')
            continue

        if RE_STATS.match(text):
            log['分类计数']['统计行数'] += 1
            do_para(el, '解析')
            continue
        if RE_LEGEND.match(text):
            log['分类计数']['图例行数'] += 1
            do_para(el, '解析')
            continue
        if RE_LABEL.match(text):
            if zone in ('STEM', 'ANS'):
                zone = 'ANS'
                log['分类计数']['标签行数·题内'] += 1
            else:
                log['分类计数']['标签行数·独立'] += 1
            do_para(el, '解析')
            continue
        if zone == 'ANS':
            do_para(el, '解析')
            continue
        if RE_ENTRY.match(text):
            log['分类计数']['条目题名行数'] += 1
        do_para(el, '正文')

    log['分类计数']['题号期望终值'] = expected
    if qcount is not None:
        assert log['分类计数']['题号块数'] == qcount, \
            '题号块数=%d ≠ qcount=%d' % (log['分类计数']['题号块数'], qcount)

    # ---------- docGrid 防线（document.xml 各 sectPr） ----------
    grid_log = []
    for dg in doc.iter(q('docGrid')):
        gtype = dg.get(q('type'))
        if gtype in ('lines', 'linesAndChars'):
            dg.set(q('type'), 'default')
            grid_log.append({'动作': '行网格归一default（原type=%s）' % gtype,
                             '其余属性': {local(k): v for k, v in dg.attrib.items() if local(k) != 'type'}})
        else:
            grid_log.append({'动作': '记录不动', '属性': {local(k): v for k, v in dg.attrib.items()}})
    log['docGrid'] = grid_log if grid_log else '无docGrid元素'

    # ---------- 断言：文字零增删 / 结构不变 ----------
    # 2026-08-31 F-工具补丁审计修：原为列表级比对（text_stream(doc) == stream_before）——「标题行内
    # 统计段run级切分」把1个w:t拆成2个时列表必不等而字符零增删，断言假失败；零字符判据改拼接流比对。
    assert ''.join(text_stream(doc)) == ''.join(stream_before), 'w:t/m:t 字符流发生变化——禁止落盘'
    assert len(list(body.iter(q('p')))) == para_count_before, '段落数变化'
    assert len(list(body.iter(q('tbl')))) == tbl_count_before, '表格数变化'

    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                encoding='UTF-8', standalone=True)

    # ---------- docDefaults 双修（styles.xml）＋样式定义主题字体清剿 ----------
    dd = styles.find(q('docDefaults'))
    if dd is None:
        dd = etree.SubElement(styles, q('docDefaults'))
    rprd = dd.find(q('rPrDefault'))
    if rprd is None:
        rprd = etree.SubElement(dd, q('rPrDefault'))
    rpr = rprd.find(q('rPr'))
    if rpr is None:
        rpr = etree.SubElement(rprd, q('rPr'))
    rf = ordered_child(rpr, 'rFonts', RPR_ORDER)
    rf.set(q('ascii'), 'Times New Roman')
    rf.set(q('hAnsi'), 'Times New Roman')
    rf.set(q('eastAsia'), '宋体')
    rf.set(q('cs'), 'Times New Roman')
    for att in THEME_MAP:
        if rf.get(q(att)) is not None:
            del rf.attrib[q(att)]
    ordered_child(rpr, 'sz', RPR_ORDER).set(q('val'), SZ_BODY)
    ordered_child(rpr, 'szCs', RPR_ORDER).set(q('val'), SZ_BODY)
    pprd = dd.find(q('pPrDefault'))
    if pprd is None:
        pprd = etree.SubElement(dd, q('pPrDefault'))
    ppr = pprd.find(q('pPr'))
    if ppr is None:
        ppr = etree.SubElement(pprd, q('pPr'))
    sp = ordered_child(ppr, 'spacing', PPR_ORDER)
    sp.set(q('before'), '0')
    sp.set(q('after'), '0')
    sp.set(q('line'), LINE_BODY)
    sp.set(q('lineRule'), 'atLeast')
    n_style_theme = 0
    for rf2 in styles.iter(q('rFonts')):
        hit = False
        for att, (name, val) in THEME_MAP.items():
            if rf2.get(q(att)) is not None:
                del rf2.attrib[q(att)]
                rf2.set(q(name), val)
                hit = True
        if hit:
            n_style_theme += 1
    log['docDefaults'] = {
        'rPrDefault': {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman', 'eastAsia': '宋体',
                       'cs': 'Times New Roman', 'sz': SZ_BODY, 'szCs': SZ_BODY},
        'pPrDefault': {'before': '0', 'after': '0', 'line': LINE_BODY, 'lineRule': 'atLeast'},
        '样式定义主题字体改写处': n_style_theme,
    }
    parts['word/styles.xml'] = etree.tostring(styles, xml_declaration=True,
                                              encoding='UTF-8', standalone=True)

    # ---------- 页眉冻结（防 docDefaults 连带；页脚跳过不动——M1统一重写） ----------
    header_frozen = 0
    header_parts = []
    for name in members:
        base = os.path.basename(name)
        if name.startswith('word/') and re.match(r'header\d*\.xml$', base):
            header_parts.append(name)
            hroot = etree.fromstring(parts[name])
            touched = False
            for p in hroot.iter(q('p')):
                ppr = p.find(q('pPr'))
                if ppr is None or ppr.find(q('spacing')) is None:
                    set_spacing(p, '288', rule='auto')
                    header_frozen += 1
                    touched = True
            if touched:
                parts[name] = etree.tostring(hroot, xml_declaration=True,
                                             encoding='UTF-8', standalone=True)
    footer_parts = [n for n in members if n.startswith('word/')
                    and re.match(r'footer\d*\.xml$', os.path.basename(n))]
    log['页眉页脚'] = {'页眉部件': header_parts,
                   '页眉段冻结数(补显式288auto防连带)': header_frozen,
                   '页脚部件(跳过不动)': footer_parts}

    # ---------- 复核断言：全部非豁免、非跳过 run 均有显式 sz ----------
    n_missing = 0
    for p in body.iter(q('p')):
        for r in p.iter(q('r')):
            if under_drawing(r) or id(r) in exempt_ids:
                continue
            if run_kind(r) == 'skip':
                continue
            rpr2 = r.find(q('rPr'))
            if rpr2 is None or rpr2.find(q('sz')) is None:
                n_missing += 1
    assert n_missing == 0, '存在%d个非豁免run缺显式sz' % n_missing
    log['安全']['修订标记w:ins/w:del'] = {'w:ins': len(list(doc.iter(q('ins')))),
                                     'w:del': len(list(doc.iter(q('del'))))}
    log['安全']['复核·非豁免run缺显式sz数'] = n_missing

    # ---------- 落盘 ----------
    tmp = path_out + '.tmp'
    for _ in range(12):
        try:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
                for n in members:
                    zo.writestr(n, parts[n])
            os.replace(tmp, path_out)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('输出文件被占用: ' + path_out)

    log['耗时秒'] = round(time.time() - t0, 1)
    log['输出'] = path_out
    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
    print(json.dumps({'文件': log['输入'], '标题段跳过': log['分类计数']['标题段跳过'],
                      '正文段': log['分类计数']['正文段'], '解析段': log['分类计数']['解析段'],
                      '题号块数': log['分类计数']['题号块数'], '待人工': len(log['待人工']),
                      '410段': log['行距计数']['line=410段数'],
                      '280段': log['行距计数']['line=280段数']}, ensure_ascii=False))
    return log


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)

    def argval(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default

    qstart = int(argval('--qstart', '1'))
    qcount = argval('--qcount')
    qcount = int(qcount) if qcount else None

    if '--batch' in argv:
        outdir = os.path.abspath(argval('--batch'))
        os.makedirs(outdir, exist_ok=True)
        files = [a for a in argv if a.endswith('.docx')]
        assert files, '批量模式需在 --batch <outdir> 后列出输入docx'
        for f in files:
            f = os.path.abspath(f)
            out = os.path.join(outdir, os.path.basename(f))
            process(f, out, qstart, qcount,
                    os.path.join(outdir, os.path.basename(f)[:-5] + '.字号双档.json'))
    else:
        src, dst = os.path.abspath(argv[0]), os.path.abspath(argv[1])
        jp = argval('--json', dst + '.字号双档.json')
        process(src, dst, qstart, qcount, jp)


if __name__ == '__main__':
    main()
