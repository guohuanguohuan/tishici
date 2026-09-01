# -*- coding: utf-8 -*-
#
# 升级：2026-09-01 A'改制轮·T2工具债②——由「字号双档」（欠账A：正文24/解析18＋行距分级
#   410/280、标题字号留T4）改参升级为「归一改版」模式：全件24半点＋line=410 atLeast＋标题
#   梯子自挂（章/讲32、节28、讲部/题型24均加粗）、jc=left显式、w:ind清零、页眉页脚18半点、
#   节名锚段保留登记。旧双档制废止（历史版本git可回查，git log -- 工具/字号双档改版.py）。
#   依据：公共规则§7段落条款＋排版自检⑧、A'规格书§2工具债②/口径A、经验文件（docGrid行网格
#   定论——不关则410收益被网格吞掉；PUA字符run跳过；docDefaults显式化禁主题字体；stdout重包
#   GC坑→改用reconfigure）。
#
r"""字号双档改版.py — 归一改版模式（文件名沿用；幂等、可批量、逐件落盘计数＋归一后自检）

归一参数（全件含表格内全部段落）:
  run 字号 w:sz/w:szCs=24 半点（12pt）；段落 w:spacing before/after=0 line=410
  lineRule=atLeast；w:jc val="left" 显式；w:ind 一律清零（删除元素——含标题段与空段）。
  解析块/标签行/通式句/统计行/图例行/章首导航表与内容表单元格——全部随正文24（双档制废止）。

字号例外挂点（§7标题字号梯子，本工具自挂）:
  章/讲标题与每件文内开头标题（首非空段） run=32 半点＋w:b/bCs；
  节标题 run=28 半点＋加粗——节标题行内统计段（「本节N题」起，跨界run切分）仍24不加粗；
  讲部标题（^\d+(\.\d+)* 方法讲解｜）与题型标题（层级号＋：） 24＋加粗；
  页眉/页脚部件 run=18 半点；段落 spacing 缺失时冻结 288 auto（防docDefaults连带抬升），
    jc=left、w:ind清零同正文；正文行距例外＝页眉段＋节名锚段两类；
  节名锚段（样式名/样式id「节名锚」，A'轮由T5挂载）——按其专用参数整体保留不触碰、仅登记
    （幂等兼容：T5挂载后重跑本工具不误改锚段）。

安全边界（与双档版同源）:
  m:oMath/m:oMathPara 子树不碰（m:r 非命名空间 w:r，天然不触）；PUA字符(U+E000–U+F8FF) run
  跳过字号与字体；纯图run（w:drawing/w:pict/w:object 且无文字）连sz一并跳过；含图带文字run
  只跳rFonts；w:txbxContent 等图形内部 run/段落不触；文字零增删（w:t/m:t字符流前后恒等断言，
  不过即退出码2不落盘）；段落数/表格数前后恒等断言。

docDefaults显式化（styles.xml，禁主题字体继承）:
  rPrDefault = rFonts(ascii/hAnsi/cs=Times New Roman, eastAsia=宋体)＋sz/szCs=24；
  pPrDefault = spacing before/after=0 line=410 lineRule=atLeast（禁模板默认after=200/line=276）；
  styles.xml 内全部 rFonts 主题属性（asciiTheme/hAnsiTheme/eastAsiaTheme/cstheme）改写为显式字体。

docGrid 行网格关闭: 全部 word/*.xml 部件扫描 w:docGrid，type=lines/linesAndChars 一律归一
  type=default（不关则行距收益被网格吞掉——经验定论；type缺失＝Word无网格态，记录不动）。

归一后自检（每次运行内建；write模式偏离非零即退出码2不落盘）:
  全量 run 字号解析值清点（显式sz，缺省按docDefaults=24）——例外外零偏离＋分类计数；
  标题run加粗清点；spacing清点（410/0/0 atLeast；页眉页脚/节名锚例外）；jc=left清点；
  w:ind残留清点；docDefaults核验；docGrid残留lines清点。--check-only 只读审计既有件。

用法:
  python 字号双档改版.py <in.docx> <out.docx> [--json <报告.json>] [--profile 归一]
  python 字号双档改版.py --batch <outdir> <in1.docx> <in2.docx> ...
  python 字号双档改版.py --check-only <docx> [--json <报告.json>]
批量模式逐件落盘: <outdir>/<原名>.docx ＋ <outdir>/<原名>.归一改版.json
幂等: set-to-value 语义，重跑输出语义等价（幂等铁证=zip成员级DIFF=0）。
使用边界: 册目录页（降级节级行18半点）、封面件等配页件不适用本工具（会抹平其专属字号）。

2026-09-01 升级审计注记（既有语句与后继拍板兼容性）:
  - exempt持活列表/id豁免集：双档制「标题run留T4」伴生机制——归一制标题字号本工具自挂，删除；
  - --qstart/--qcount 题号门控与zone分档：双档制解析区识别伴生参数——归一制解析块与正文同值，
    删除（题号/条目号层级制重编归工具债③题号块三段式.py）；
  - 页眉288auto冻结：保留并扩展到页脚（双档轮跳过页脚留M1重写——归一轮18半点例外挂点归本
    工具；T6同串重建照旧整体覆盖，不冲突）；
  - sys.stdout TextIOWrapper重包：GC关buffer坑（经验0831）→ 改用 reconfigure。
"""
import sys, os, re, json, time, copy, zipfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
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

SZ_BODY, SZ_CHAPTER, SZ_SECTION, SZ_HF = '24', '32', '28', '18'
LINE_BODY, LINE_HF = '410', '288'
CLS_SZ = {'正文': SZ_BODY, 'chapter': SZ_CHAPTER, 'section': SZ_SECTION,
          'lecture': SZ_BODY, 'group': SZ_BODY}
CLS_TITLE = {'chapter', 'section', 'lecture', 'group'}
CLS_NAME = {'chapter': '章', 'section': '节', 'lecture': '讲部', 'group': '题型'}

PUA_RE = re.compile(r'[\uE000-\uF8FF]')
RE_LECT = re.compile(r'^\d+(\.\d+)*\s*方法讲解[｜|]')
RE_NUMTITLE = re.compile(r'^\d+(\.\d+)+\s+\S')
RE_INSTATS = re.compile(r'本节\d+题')
NAMES_H2 = {'heading 2', '标题2', '标题 2'}
NAMES_H3 = {'heading 3', '标题3', '标题 3'}
NAMES_ANCHOR = {'节名锚'}
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
    """段 p 设 pPr/spacing before/after=0 line=<line> lineRule=<rule>"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    sp = ordered_child(ppr, 'spacing', PPR_ORDER)
    sp.set(q('before'), '0')
    sp.set(q('after'), '0')
    sp.set(q('line'), line)
    sp.set(q('lineRule'), rule)


def set_jc_left(p):
    ordered_child(p.find(q('pPr')), 'jc', PPR_ORDER).set(q('val'), 'left')


def clear_ind(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    ind = ppr.find(q('ind'))
    if ind is None:
        return False
    ppr.remove(ind)
    return True


def set_run_sz(r, halfpt):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr'))
        r.insert(0, rpr)
    for stag in ('sz', 'szCs'):
        ordered_child(rpr, stag, RPR_ORDER).set(q('val'), halfpt)


def is_on(el):
    return el is not None and el.get(q('val')) in (None, '1', 'on', 'true')


def set_run_bold(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr'))
        r.insert(0, rpr)
    for stag in ('b', 'bCs'):
        el = ordered_child(rpr, stag, RPR_ORDER)
        if el.get(q('val')) not in (None, '1'):
            el.attrib.pop(q('val'), None)


def run_kind(r):
    """'skip'（纯图/PUA/无文字——sz与rFonts全跳）| 'img'（含drawing但有文字——只跳rFonts）| 'text'"""
    has_t = any(t.text for t in r.findall(q('t')))
    if r.find(q('drawing')) is not None or r.find(q('pict')) is not None \
            or r.find(q('object')) is not None:
        return 'img' if has_t else 'skip'
    for t in r.findall(q('t')):
        if t.text and PUA_RE.search(t.text):
            return 'skip'
    return 'text'


def under_drawing(el):
    a = el.getparent()
    while a is not None:
        if local(a) in ('drawing', 'pict', 'txbxContent', 'object'):
            return True
        a = a.getparent()
    return False


def normalize_rfonts(rpr, rc):
    """rPr 级主题字体属性 → 显式字体（禁 minorHAnsi/minorEastAsia 隐性继承）"""
    if rpr is None:
        return
    rf = rpr.find(q('rFonts'))
    if rf is None:
        return
    for att, (name, val) in THEME_MAP.items():
        if rf.get(q(att)) is not None:
            del rf.attrib[q(att)]
            rf.set(q(name), val)
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


def heading_styleids(styles_root, names):
    ids = set()
    for st in styles_root.findall(q('style')):
        nm = st.find(q('name'))
        if nm is not None and nm.get(q('val')) in names:
            sid = st.get(q('styleId'))
            if sid:
                ids.add(sid)
    return ids


def classify_title(text, pstyle, h2ids, h3ids, is_first_content):
    """标题类型 or None（chapter=章/讲/文内开头；section=节；lecture=讲部；group=题型）"""
    if is_first_content:
        return 'chapter'
    if pstyle in h2ids and RE_NUMTITLE.match(text):
        return 'chapter'
    if pstyle in h3ids and RE_NUMTITLE.match(text):
        return 'section'
    if RE_LECT.match(text):
        return 'lecture'
    if RE_NUMTITLE.match(text):
        # 「：」判题型；节标题行内统计段（本节N题）并段形态优先判节
        return 'group' if ('：' in text and not RE_INSTATS.search(text)) else 'section'
    return None


def doc_grid_scan(parts):
    """全部 word/*.xml 部件扫描 docGrid；返回 [(部件名, 状态dict)]（lines型已在调用方归一）"""
    out = []
    for name in sorted(parts):
        base = os.path.basename(name)
        if not (name.startswith('word/') and base.endswith('.xml')):
            continue
        if b'docGrid' not in parts[name]:
            continue
        root = etree.fromstring(parts[name])
        for dg in root.iter(q('docGrid')):
            out.append((name, {local(k): v for k, v in dg.attrib.items()}))
    return out


def doc_grid_normalize(parts):
    """全部部件 docGrid 行网格（lines/linesAndChars）归一 type=default；返回 (动作清单, 改动部件集)"""
    actions, dirty = [], set()
    for name in sorted(parts):
        base = os.path.basename(name)
        if not (name.startswith('word/') and base.endswith('.xml')):
            continue
        if b'docGrid' not in parts[name]:
            continue
        root = etree.fromstring(parts[name])
        touched = False
        for dg in root.iter(q('docGrid')):
            gtype = dg.get(q('type'))
            if gtype in ('lines', 'linesAndChars'):
                dg.set(q('type'), 'default')
                touched = True
                actions.append({'部件': name, '动作': '行网格归一default（原type=%s）' % gtype,
                                '其余属性': {local(k): v for k, v in dg.attrib.items()
                                             if local(k) != 'type'}})
            else:
                actions.append({'部件': name, '动作': '记录不动（type=%s，无网格态）'
                                % ('缺失' if gtype is None else gtype),
                                '属性': {local(k): v for k, v in dg.attrib.items()}})
        if touched:
            parts[name] = etree.tostring(root, xml_declaration=True,
                                          encoding='UTF-8', standalone=True)
            dirty.add(name)
    return actions, dirty


def doc_defaults_apply(styles):
    """styles.xml docDefaults 显式化＋样式定义主题字体清剿；返回描述dict"""
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
    return {'rPrDefault': {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman',
                           'eastAsia': '宋体', 'cs': 'Times New Roman',
                           'sz': SZ_BODY, 'szCs': SZ_BODY},
            'pPrDefault': {'before': '0', 'after': '0', 'line': LINE_BODY,
                           'lineRule': 'atLeast'},
            '样式定义主题字体改写处': n_style_theme}


def doc_defaults_verify(parts):
    st = etree.fromstring(parts['word/styles.xml'])
    dd = st.find(q('docDefaults'))
    got = {'rPrDefault': None, 'pPrDefault': None, '合规': False}
    if dd is not None:
        rprd, pprd = dd.find(q('rPrDefault')), dd.find(q('pPrDefault'))
        if rprd is not None and rprd.find(q('rPr')) is not None:
            rpr = rprd.find(q('rPr'))
            rf = rpr.find(q('rFonts'))
            sz = rpr.find(q('sz'))
            got['rPrDefault'] = ({'ascii': rf.get(q('ascii')), 'hAnsi': rf.get(q('hAnsi')),
                                  'eastAsia': rf.get(q('eastAsia')), 'cs': rf.get(q('cs')),
                                  'sz': sz.get(q('val')) if sz is not None else None}
                                 if rf is not None else None)
        if pprd is not None and pprd.find(q('pPr')) is not None:
            sp = pprd.find(q('pPr')).find(q('spacing'))
            if sp is not None:
                got['pPrDefault'] = {a: sp.get(q(a)) for a in ('before', 'after', 'line', 'lineRule')}
    exp_r = {'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman', 'eastAsia': '宋体',
             'cs': 'Times New Roman', 'sz': SZ_BODY}
    exp_p = {'before': '0', 'after': '0', 'line': LINE_BODY, 'lineRule': 'atLeast'}
    got['合规'] = (got['rPrDefault'] == exp_r and got['pPrDefault'] == exp_p)
    return got


def hf_part_process(parts, name, rc, pc):
    """页眉/页脚部件：run=18半点＋段落spacing缺失冻结288auto＋jc=left＋w:ind清零；返回是否改动"""
    root = etree.fromstring(parts[name])
    dirty = False
    for p in root.iter(q('p')):
        if under_drawing(p):
            pc['页眉页脚图形内部段跳过'] += 1
            continue
        pc['页眉页脚段数'] += 1
        ppr = p.find(q('pPr'))
        if ppr is None or ppr.find(q('spacing')) is None:
            set_spacing(p, LINE_HF, rule='auto')
            pc['页眉页脚spacing冻结数'] += 1
            dirty = True
        # 已有显式spacing的页眉页脚段不触碰（冻结为现值，防docDefaults连带抬升）
        jce = ppr.find(q('jc')) if ppr is not None else None
        if jce is None or jce.get(q('val')) != 'left':
            set_jc_left(p)
            pc['jc置left段数'] += 1
            dirty = True
        if clear_ind(p):
            pc['w:ind清除数'] += 1
            dirty = True
        for r in p.iter(q('r')):
            if under_drawing(r):
                rc['图形内部run跳过'] += 1
                continue
            kind = run_kind(r)
            if kind == 'skip':
                if any(t.text and PUA_RE.search(t.text) for t in r.findall(q('t'))):
                    rc['PUA run跳过'] += 1
                else:
                    rc['纯图run跳过'] += 1
                continue
            rpr = r.find(q('rPr'))
            sz0 = rpr.find(q('sz')) if rpr is not None else None
            if sz0 is None or sz0.get(q('val')) != SZ_HF:
                set_run_sz(r, SZ_HF)
                dirty = True
            rc['页眉页脚sz置18run数'] += 1
            if kind != 'img':
                before = rc['主题字体run改写']
                normalize_rfonts(rpr, rc)
                if rc['主题字体run改写'] > before:
                    dirty = True
        # 段落标记：既有rPr的sz归18＋主题字体显式化
        ppr = p.find(q('pPr'))
        if ppr is not None:
            mrpr = ppr.find(q('rPr'))
            if mrpr is not None:
                if mrpr.find(q('sz')) is not None or mrpr.find(q('szCs')) is not None:
                    before = (mrpr.find(q('sz')).get(q('val')) if mrpr.find(q('sz')) is not None else None)
                    for stag in ('sz', 'szCs'):
                        ordered_child(mrpr, stag, RPR_ORDER).set(q('val'), SZ_HF)
                    if before != SZ_HF:
                        dirty = True
                    rc['段落标记sz归一run数'] += 1
                b0 = rc['主题字体run改写']
                normalize_rfonts(mrpr, rc)
                if rc['主题字体run改写'] > b0:
                    dirty = True
    if dirty:
        parts[name] = etree.tostring(root, xml_declaration=True,
                                     encoding='UTF-8', standalone=True)
    return dirty


def process(path_in, path_out=None, json_path=None, write=True):
    """write=True: 归一改版并落盘（含归一后自检，偏离非零退出码2不落盘）；
    write=False (--check-only): 只读自检既有件，偏离数落盘报告、退出码1"""
    t0 = time.time()
    zin = zipfile.ZipFile(path_in)
    members = zin.namelist()
    parts = {n: zin.read(n) for n in members}
    zin.close()

    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    styles = etree.fromstring(parts['word/styles.xml'])
    h2ids = heading_styleids(styles, NAMES_H2)
    h3ids = heading_styleids(styles, NAMES_H3)
    anchor_ids = heading_styleids(styles, NAMES_ANCHOR) | {'节名锚'}

    log = {
        '输入': os.path.basename(path_in), '模式': '归一' if write else '只读自检',
        '样式识别': {'h2样式id': sorted(h2ids), 'h3样式id': sorted(h3ids),
                 '节名锚样式id': sorted(anchor_ids), '节名锚字面兜底id': ['节名锚']},
        '分类计数': {'标题段·章': 0, '标题段·节': 0, '标题段·讲部': 0, '标题段·题型': 0,
                  '正文段': 0, '空段落': 0, '表数': 0, '表内段落数': 0,
                  '节名锚段跳过': 0, '节标题行内统计段run切分': 0},
        'run计数': {'sz置24run数': 0, 'sz置32run数': 0, 'sz置28run数': 0,
                 '页眉页脚sz置18run数': 0, '标题加粗run数': 0,
                 '纯图run跳过': 0, 'PUA run跳过': 0, '图形内部run跳过': 0,
                 '主题字体run改写': 0, '段落标记sz归一run数': 0},
        '段落计数': {'line=410段数': 0, 'jc置left段数': 0, 'w:ind清除数': 0,
                 '页眉页脚段数': 0, '页眉页脚spacing冻结数': 0,
                 '页眉页脚图形内部段跳过': 0},
        '安全': {},
    }
    rc, pc, cc = log['run计数'], log['段落计数'], log['分类计数']

    if write:
        stream_before = text_stream(doc)
        para_count_before = len(list(body.iter(q('p'))))
        tbl_count_before = len(list(body.iter(q('tbl'))))

        def para_runs(p):
            rs = []
            for r in p.iter(q('r')):
                if under_drawing(r):
                    rc['图形内部run跳过'] += 1
                else:
                    rs.append(r)
            return rs

        def apply_run(r, sz, bold):
            set_run_sz(r, sz)
            rc['sz置%srun数' % sz] += 1
            if bold:
                set_run_bold(r)
                rc['标题加粗run数'] += 1

        def do_para(p, cls, stats_from=None):
            set_spacing(p, LINE_BODY)
            pc['line=410段数'] += 1
            ppr = p.find(q('pPr'))
            jce = ppr.find(q('jc'))
            if jce is None or jce.get(q('val')) != 'left':
                set_jc_left(p)
                pc['jc置left段数'] += 1
            if clear_ind(p):
                pc['w:ind清除数'] += 1
            size, bold = CLS_SZ[cls], cls in CLS_TITLE
            off = 0
            for r in para_runs(p):
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
                r_sz, r_bold = size, bold
                if cls == 'section' and stats_from is not None:
                    if off >= stats_from:
                        r_sz, r_bold = SZ_BODY, False
                    elif off + tlen > stats_from:
                        # 跨界run切分：前半留标题（28加粗），后半归统计段（24不加粗）
                        tail = split_run_at(r, stats_from - off)
                        apply_run(r, SZ_SECTION, True)
                        cc['节标题行内统计段run切分'] += 1
                        r = tail
                        tlen = len(r.find(q('t')).text or '')
                        off = stats_from
                        r_sz, r_bold = SZ_BODY, False
                apply_run(r, r_sz, r_bold)
                if kind != 'img':
                    normalize_rfonts(r.find(q('rPr')), rc)
                off += tlen
            # 段落标记：既有rPr的sz归class值＋主题字体显式化（不新建）
            ppr = p.find(q('pPr'))
            if ppr is not None:
                mrpr = ppr.find(q('rPr'))
                if mrpr is not None:
                    if mrpr.find(q('sz')) is not None or mrpr.find(q('szCs')) is not None:
                        for stag in ('sz', 'szCs'):
                            ordered_child(mrpr, stag, RPR_ORDER).set(q('val'), size)
                        rc['段落标记sz归一run数'] += 1
                    normalize_rfonts(mrpr, rc)
            if cls in CLS_TITLE:
                cc['标题段·' + CLS_NAME[cls]] += 1
            else:
                cc['正文段'] += 1

        # ---------- 主遍历：分类＋归一（全段落 410/0/0＋jc=left＋ind清零＋字号梯子） ----------
        first_content_seen = False
        for el in body:
            tag = local(el)
            if tag == 'sectPr':
                continue
            if tag == 'tbl':
                cc['表数'] += 1
                for p in el.iter(q('p')):
                    if under_drawing(p):
                        rc['图形内部run跳过'] += 0
                        continue
                    cc['表内段落数'] += 1
                    do_para(p, '正文')
                continue
            if tag != 'p':
                continue
            ps = el.find(q('pPr'))
            pstyle = ''
            if ps is not None:
                pst = ps.find(q('pStyle'))
                pstyle = pst.get(q('val')) if pst is not None else ''
            if pstyle in anchor_ids:
                cc['节名锚段跳过'] += 1
                continue
            text = ptext(el)
            if not text.strip():
                cc['空段落'] += 1
                do_para(el, '正文')
                continue
            tkind = classify_title(text, pstyle, h2ids, h3ids, not first_content_seen)
            first_content_seen = True
            mstat = RE_INSTATS.search(text) if tkind == 'section' else None
            do_para(el, tkind or '正文', stats_from=mstat.start() if mstat else None)

        # ---------- 断言：文字零增删 / 结构不变 ----------
        assert ''.join(text_stream(doc)) == ''.join(stream_before), 'w:t/m:t 字符流发生变化——禁止落盘'
        assert len(list(body.iter(q('p')))) == para_count_before, '段落数变化'
        assert len(list(body.iter(q('tbl')))) == tbl_count_before, '表格数变化'

        parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                    encoding='UTF-8', standalone=True)
        log['docDefaults'] = doc_defaults_apply(styles)
        # 序列化必须在 doc_defaults_apply 之后——G件pPrDefault缺before/after首曝此序bug（旧序=旧树写入parts→verify读旧值误报不合规）
        parts['word/styles.xml'] = etree.tostring(
            styles, xml_declaration=True, encoding='UTF-8', standalone=True)

        # ---------- 页眉页脚（18半点例外挂点＋spacing冻结防docDefaults连带） ----------
        hf = {'页眉部件': [], '页脚部件': []}
        for name in members:
            base = os.path.basename(name)
            if name.startswith('word/') and re.match(r'header\d*\.xml$', base):
                hf['页眉部件'].append(name)
                hf_part_process(parts, name, rc, pc)
            elif name.startswith('word/') and re.match(r'footer\d*\.xml$', base):
                hf['页脚部件'].append(name)
                hf_part_process(parts, name, rc, pc)
        log['页眉页脚'] = hf

        # ---------- docGrid 行网格关闭（全部件） ----------
        actions, _dirty = doc_grid_normalize(parts)
        log['docGrid'] = actions if actions else '无docGrid元素'

    # ---------- 归一后自检（write模式对改后树；check-only对既有件） ----------
    dev = verify(parts, h2ids, h3ids, anchor_ids, log)
    log['自检'] = dev
    if not write:
        log['docDefaults'] = dev['docDefaults核验']
        log['docGrid'] = doc_grid_scan(parts) or '无docGrid元素'
    log['安全'].update({'w:ins': len(list(doc.iter(q('ins')))),
                     'w:del': len(list(doc.iter(q('del'))))})

    if write:
        bad = []
        for label, v in (('字号偏离数', dev['run字号清点']['字号偏离数']),
                         ('标题run缺加粗数', dev['标题run缺加粗数']),
                         ('spacing偏离数', dev['spacing清点']['偏离数']),
                         ('jc偏离数', dev['jc清点']['偏离数']),
                         ('w:ind残留数', dev['w:ind残留数']),
                         ('docGrid残留lines数', dev['docGrid残留lines数'])):
            if v:
                bad.append('%s=%d' % (label, v))
        if not dev['docDefaults核验']['合规']:
            bad.append('docDefaults不合规')
        if bad:
            print('[自检失败·不落盘] ' + '; '.join(bad), file=sys.stderr)
            json.dump(log, open((json_path or (path_out or path_in) + '.FAIL.json'),
                                'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            sys.exit(2)

    if write and path_out:
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
        log['输出'] = path_out

    log['耗时秒'] = round(time.time() - t0, 1)
    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
    chk = dev
    print(json.dumps({'文件': log['输入'], '模式': log['模式'],
                      '标题段(章/节/讲部/题型)': [cc['标题段·章'], cc['标题段·节'],
                                            cc['标题段·讲部'], cc['标题段·题型']],
                      '正文段': cc['正文段'], '表内段落数': cc['表内段落数'],
                      'sz置24/32/28': [rc['sz置24run数'], rc['sz置32run数'], rc['sz置28run数']],
                      '页眉页脚sz置18': rc['页眉页脚sz置18run数'],
                      '标题加粗run': rc['标题加粗run数'],
                      '自检偏离': {'字号偏离数': chk['run字号清点']['字号偏离数'],
                                 '标题run缺加粗数': chk['标题run缺加粗数'],
                                 'spacing偏离数': chk['spacing清点']['偏离数'],
                                 'jc偏离数': chk['jc清点']['偏离数'],
                                 'w:ind残留数': chk['w:ind残留数'],
                                 'docGrid残留lines数': chk['docGrid残留lines数']},
                      'docDefaults合规': chk['docDefaults核验']['合规']},
                     ensure_ascii=False))
    return log


def verify(parts, h2ids, h3ids, anchor_ids, log):
    """归一后自检：全量run字号解析值清点（例外外零偏离）＋加粗＋spacing＋jc＋ind＋docGrid＋docDefaults"""
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    dev = {
        'run字号清点': {'24': 0, '28': 0, '32': 0, '18(页眉页脚)': 0, '继承24(无显式)': 0,
                   '跳过run(纯图/PUA/图形内/锚段)': 0, '字号偏离数': 0, '偏离样本': []},
        '标题run缺加粗数': 0, '加粗缺失样本': [],
        'spacing清点': {'410atLeast段数': 0, '页眉页脚例外段数': 0, '节名锚例外段数': 0,
                   '偏离数': 0, '偏离样本': []},
        'jc清点': {'left段数': 0, '偏离数': 0},
        'w:ind残留数': 0,
        'docGrid残留lines数': 0,
        'docDefaults核验': doc_defaults_verify(parts),
    }
    samples = []

    def add_sample(kind, msg):
        if len(samples) < 20:
            samples.append({'类': kind, '说明': msg})
        dev['run字号清点']['字号偏离数'] += 1

    first_content_seen = False
    for el in body:
        tag = local(el)
        if tag == 'sectPr':
            continue
        paras = ()
        if tag == 'tbl':
            paras = [p for p in el.iter(q('p')) if not under_drawing(p)]
            in_tbl = True
        elif tag == 'p':
            paras = [el]
            in_tbl = False
        else:
            continue
        for p in paras:
            ps = p.find(q('pPr'))
            pstyle = ''
            if ps is not None:
                pst = ps.find(q('pStyle'))
                pstyle = pst.get(q('val')) if pst is not None else ''
            if pstyle in anchor_ids:
                dev['spacing清点']['节名锚例外段数'] += 1
                continue
            text = ptext(p)
            if not text.strip():
                cls = '正文'   # 空段落不推进 first_content_seen（与归一遍历一致）
            elif in_tbl:
                cls = '正文'   # 表内段落一律正文24（口径A导航表全表12pt；与写侧 do_para(p,'正文') 对齐——修复：表内节名行列曾被误判节标题）
            else:
                cls = classify_title(text, pstyle, h2ids, h3ids, not first_content_seen) or '正文'
                first_content_seen = True
            mstat = RE_INSTATS.search(text) if cls == 'section' else None
            stats_from = mstat.start() if mstat else None
            # 段落级：spacing/jc/ind
            spc = ps.find(q('spacing')) if ps is not None else None
            ok_spc = spc is not None and spc.get(q('before')) == '0' and spc.get(q('after')) == '0' \
                and spc.get(q('line')) == LINE_BODY and spc.get(q('lineRule')) == 'atLeast'
            if ok_spc:
                dev['spacing清点']['410atLeast段数'] += 1
            else:
                dev['spacing清点']['偏离数'] += 1
                if len(dev['spacing清点']['偏离样本']) < 10:
                    dev['spacing清点']['偏离样本'].append(text[:24])
            jce = ps.find(q('jc')) if ps is not None else None
            if jce is not None and jce.get(q('val')) == 'left':
                dev['jc清点']['left段数'] += 1
            else:
                dev['jc清点']['偏离数'] += 1
            if ps is not None and ps.find(q('ind')) is not None:
                dev['w:ind残留数'] += 1
            # run级：字号解析值＋加粗
            off = 0
            for r in p.iter(q('r')):
                if under_drawing(r):
                    dev['run字号清点']['跳过run(纯图/PUA/图形内/锚段)'] += 1
                    continue
                kind = run_kind(r)
                t_el = r.find(q('t'))
                tlen = len(t_el.text or '') if t_el is not None else 0
                if kind == 'skip':
                    dev['run字号清点']['跳过run(纯图/PUA/图形内/锚段)'] += 1
                    off += tlen
                    continue
                rpr = r.find(q('rPr'))
                sze = rpr.find(q('sz')) if rpr is not None else None
                szv = sze.get(q('val')) if sze is not None else None
                if cls in CLS_TITLE:
                    if cls == 'chapter':
                        exp, exp_b = SZ_CHAPTER, True
                    elif cls == 'section':
                        if stats_from is None or off + tlen <= stats_from:
                            exp, exp_b = SZ_SECTION, True
                        elif off >= stats_from:
                            exp, exp_b = SZ_BODY, False
                        else:
                            add_sample('跨界run', '节标题run跨界统计段边界: %r' % text[:20])
                            off += tlen
                            continue
                    else:
                        exp, exp_b = SZ_BODY, True
                else:
                    exp, exp_b = SZ_BODY, False
                resolved = szv or SZ_BODY  # 无显式→docDefaults 24
                if resolved == exp:
                    dev['run字号清点'][resolved if resolved != SZ_HF else '18(页眉页脚)'] += 1
                else:
                    add_sample('字号', 'sz=%s 期望=%s: %r' % (szv, exp, text[:20]))
                if exp_b and not is_on(rpr.find(q('b')) if rpr is not None else None):
                    dev['标题run缺加粗数'] += 1
                    if len(dev['加粗缺失样本']) < 10:
                        dev['加粗缺失样本'].append(text[:24])
                off += tlen

    # 页眉页脚部件
    for name in sorted(parts):
        base = os.path.basename(name)
        if not (name.startswith('word/') and
                (re.match(r'header\d*\.xml$', base) or re.match(r'footer\d*\.xml$', base))):
            continue
        root = etree.fromstring(parts[name])
        for p in root.iter(q('p')):
            if under_drawing(p):
                continue
            dev['spacing清点']['页眉页脚例外段数'] += 1
            ps = p.find(q('pPr'))
            if ps is None or ps.find(q('spacing')) is None:
                dev['spacing清点']['偏离数'] += 1
            jce = ps.find(q('jc')) if ps is not None else None
            if jce is None or jce.get(q('val')) != 'left':
                dev['jc清点']['偏离数'] += 1
            if ps is not None and ps.find(q('ind')) is not None:
                dev['w:ind残留数'] += 1
            for r in p.iter(q('r')):
                if under_drawing(r) or run_kind(r) == 'skip':
                    dev['run字号清点']['跳过run(纯图/PUA/图形内/锚段)'] += 1
                    continue
                rpr = r.find(q('rPr'))
                szv = (rpr.find(q('sz')).get(q('val'))
                       if rpr is not None and rpr.find(q('sz')) is not None else None)
                if szv == SZ_HF:
                    dev['run字号清点']['18(页眉页脚)'] += 1
                else:
                    add_sample('页眉页脚字号', '%s sz=%s 期望=18: %r'
                               % (name, szv, ptext(p)[:20]))

    for _name, attrs in doc_grid_scan(parts):
        if attrs.get('type') in ('lines', 'linesAndChars'):
            dev['docGrid残留lines数'] += 1
    dev['run字号清点']['偏离样本'] = samples
    return dev


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    for stale in ('--qstart', '--qcount'):
        if stale in argv:
            print('%s 已随双档制废止（归一制无题号门控；层级制重编见 工具/题号块三段式.py）'
                  % stale, file=sys.stderr)
            sys.exit(2)
    if '--profile' in argv:
        prof = argv[argv.index('--profile') + 1]
        if prof != '归一':
            print('仅支持 --profile 归一（双档制已废止，历史版本见 git）', file=sys.stderr)
            sys.exit(2)

    def argval(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default

    if '--check-only' in argv:
        src = os.path.abspath(argval('--check-only'))
        jp = argval('--json', src + '.归一自检.json')
        log = process(src, None, jp, write=False)
        a = log['自检']
        bad = (a['run字号清点']['字号偏离数'] + a['标题run缺加粗数']
               + a['spacing清点']['偏离数'] + a['jc清点']['偏离数']
               + a['w:ind残留数'] + a['docGrid残留lines数'])
        if not log['自检']['docDefaults核验']['合规']:
            bad += 1
        sys.exit(1 if bad else 0)
    if '--batch' in argv:
        outdir = os.path.abspath(argval('--batch'))
        os.makedirs(outdir, exist_ok=True)
        files = [a for a in argv if a.endswith('.docx')]
        assert files, '批量模式需在 --batch <outdir> 后列出输入docx'
        for f in files:
            f = os.path.abspath(f)
            out = os.path.join(outdir, os.path.basename(f))
            process(f, out, None,
                    os.path.join(outdir, os.path.basename(f)[:-5] + '.归一改版.json'))
    else:
        src, dst = os.path.abspath(argv[0]), os.path.abspath(argv[1])
        jp = argval('--json', dst + '.归一改版.json')
        process(src, dst, jp)


if __name__ == '__main__':
    main()
