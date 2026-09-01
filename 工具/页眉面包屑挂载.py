# -*- coding: utf-8 -*-
#
# 沿革：2026-08-30 工具债③新建——页眉右停靠制表位＋STYLEREF"标题 3"面包屑（级B形态，随2026-09-01
#   十项改制拍板退役）；2026-09-01 A'改制轮工具债⑥改版——「同串挂载＋节名锚挂载」（公共规则§7
#   页面条款页脚款/页眉款/节名锚机制现行文本＝A'改制轮口径F/口径G）。旧「右停靠制表位＋
#   STYLEREF "标题 3"」形态与「件标识（共N页）　第X页」旧页脚随本版整体退役。
#
"""页眉面包屑挂载.py — 同串挂载＋节名锚挂载（只处理副本，断言不过不动输出文件）

规格（公共规则§7页眉页脚同串/节名锚机制现行文本；A'改制轮口径F/口径G）：
  1) 节名锚段：每个教材节标题段（挂「标题3」样式段落＝工具/节标题样式挂载.py的挂载对象）之前插入
     一个专用样式「节名锚」段落——样式在 styles.xml 新建（styleId=JieMingMao、name=节名锚）：
     1pt（sz=2半点）、白色#FFFFFF、非隐藏（无w:vanish——域行为实测注记①：隐藏形态STYLEREF不认）、
     行距固定1磅（w:spacing line=20 lineRule=exact）、段前后0、无底纹无边框、jc=left；
     basedOn＝该件styles.xml真实Normal styleId（禁字面量'Normal'悬空——2026-08-31样式挂载定论；
     本册实测='a'）。锚段内容＝「节号 节名」（照节标题原文，剥离节级统计段「（第X—Y题）　本节N题…」）；
     断言：锚段数＝节标题数（每节标题前恰一段，直接前驱）。
  2) 页眉页脚同串重建（两部件整体替换为同一单段）：左对齐单行、9pt（sz=18半点）、中文宋体西文TNR——
     串＝「羿郭工作室·册名 第X章 章名·件型（共N页）　当前节号节名　第X页」：
       · 前段（羿郭工作室·册名 第X章 章名·件型）取自该件既有页眉文本（已在位同串件则截到「（共」前，
         幂等）；旧左串页眉/「件标识（共N页）　第X页」旧页脚随整段重建退役；
       · X＝PAGE复杂域（fldChar begin/separate/end＋w:instrText，禁fldSimple），域缓存＝该件sectPr现start值；
       · 节名段＝STYLEREF复杂域（instrText＝ STYLEREF "节名锚" ），域缓存＝首锚段文本
         （Word/打印/PDF链路必然重算；WPS/静态查看器可能显缓存——公共规则§7备案口径）；
       · 件型段写死；N写'N'占位符（由 工具/册级连续页码.py 盖章阶段填部分总页数实测值）；
       · 件型token参数化：--token 第X章·衔接／第X章·清单／第X章·讲练（同章各卷一致、分卷不加卷次
         ——高中同步总控§5件标识对照；工具以token尾段校验既有页眉前段一致性）。
  3) 版面：sectPr pgMar header=283、footer=850（缺省/杂值即改写）；全文恰1个headerReference＋
     恰1个footerReference（default类型）；无首页不同（剔w:titlePg）、无奇偶页不同
     （settings.xml剔evenAndOddHeaders）；settings.xml确保<w:updateFields w:val="true"/>。
  4) 串宽实测断言：9pt按字符宽估算（CJK/全角/全角空格＝180缇、ASCII半角＝90缇；N/X按3位数字最坏值、
     节名段按该件最长锚段文本），超版心宽（pgSz.w−pgMar.left−pgMar.right）即省略「羿郭工作室·」
     品牌前缀（件型与章名保留）；另以Word COM实测行数断言输出（worst-case串行数=1；带前缀实测>1行
     则自动降级省前缀重测，仍>1行＝断言失败退出码2）。

安全断言（全过才写输出，任一不过退出码2、不产生输出文件）：
  A1 单页眉单页脚——document.xml 恰1个headerReference＋恰1个footerReference且rels可解析到实际部件；
  A2 节标题在位——正文挂「标题3」（name=heading 3/标题 3）样式段落≥1；
  A3 只动五类目标件——输出包除 document.xml/styles.xml/settings.xml/页眉部件/页脚部件 外其余条目
     逐一与输入字节相等；目标件中 document.xml 除锚段插入与sectPr三处版面参数外内容不变；
  A4 结构自检——输出复检：锚段数＝节标题数且逐节标题直接前驱为锚段；锚样式basedOn＝真实Normal
     styleId、sz=2、color=FFFFFF、line=20 exact、无vanish/shd/pBdr；页眉页脚各恰1段、jc=left、
     全部run 18半点＋宋体/TNR、恰两组fldChar begin/separate/end（STYLEREF＋PAGE）、instrText集合
     ＝{ STYLEREF "节名锚" ,  PAGE }、无fldSimple、无NUMPAGES、可见文本＝预期串（N占位）、
     （共N页）占位恰1处；pgMar header=283/footer=850、无titlePg；settings含updateFields；
  A5 串宽——字符宽估算＋COM实测行数＝1（断言输出落盘）。
幂等：锚段已在位且计数相符→跳过插入；同串已在位（页眉含 STYLEREF "节名锚"）→前段截「（共」前推导，
  重建确定性构造，重复挂载输出逐字节不变（zip成员级；N占位重置为'N'——盖章值以盖章为准，管线序＝
  先挂载后盖章）。

用法: python 页眉面包屑挂载.py <in.docx> <out.docx> --token 第2章·衔接 [--no-brand] [--verbose] [--dry-run]
  --no-brand＝强制省略品牌前缀（同部分各卷前缀形态一致性：部分内任一卷实测放不下即各卷都省）
"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
XMLNS = 'http://www.w3.org/XML/1998/namespace'
def q(t): return '{%s}%s' % (W, t)

STYLE_NAME_CANDIDATES = ('heading 3', '标题 3', '标题3')
DEFAULT_STYLE_ID = 'Heading3'
ANCHOR_STYLE_ID = 'JieMingMao'
ANCHOR_STYLE_NAME = '节名锚'
INSTR_STYLEREF = ' STYLEREF "节名锚" '
INSTR_PAGE = ' PAGE '
N_PLACEHOLDER = 'N'
HEADER_TWIPS = '283'   # 页眉距页顶0.5厘米（§7页眉款：页眉距＋单行行高≤上边距850缇）
FOOTER_TWIPS = '850'   # 页脚距页底1.5厘米（与四边边距同值）
RPR_HF = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
          'w:eastAsia="宋体" w:cs="Times New Roman"/>'
          '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>')   # 同串9pt＝18半点（§7）
BRAND = '羿郭工作室·'

class ToolError(Exception):
    pass

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

# ---------------------------------------------------------------- 样式与节标题定位

def find_heading3_style_id(styles_root):
    for cand in (lambda nv: nv.strip().lower() in STYLE_NAME_CANDIDATES,
                 lambda nv: nv.strip() in ('标题 3',)):
        for st in styles_root.findall(q('style')):
            nm = st.find(q('name'))
            nv = (nm.get(q('val')) or '') if nm is not None else ''
            if cand(nv):
                return st.get(q('styleId'))
    for st in styles_root.findall(q('style')):
        if st.get(q('styleId')) == DEFAULT_STYLE_ID:
            return st.get(q('styleId'))
    return None

def find_normal_style_id(styles_root):
    """真实Normal styleId：type=paragraph且default=1（name=normal优先）——禁字面量悬空（经验定论）。"""
    by_name = None
    for st in styles_root.findall(q('style')):
        if st.get(q('type')) != 'paragraph':
            continue
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '').strip().lower() if nm is not None else ''
        if nv == 'normal':
            by_name = st.get(q('styleId'))
            if st.get(q('default')) == '1':
                return st.get(q('styleId'))
    if by_name:
        return by_name
    for st in styles_root.findall(q('style')):
        if st.get(q('type')) == 'paragraph' and st.get(q('default')) == '1':
            return st.get(q('styleId'))
    return None

def section_paras(doc_root, sid3):
    """正文（含表格内）全部挂标题3样式的段落，按文档序。"""
    out = []
    if not sid3:
        return out
    for p in doc_root.find(q('body')).iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None:
            continue
        ps = ppr.find(q('pStyle'))
        if ps is not None and ps.get(q('val')) == sid3:
            out.append(p)
    return out

_STAT_PAT = re.compile(r'（第\d+(?:[—–-]\d+)?题|　?本节\d+题')
def anchor_text_of(title):
    """锚段内容＝「节号 节名」＝节标题原文剥离节级统计段（「（第X—Y题）　本节N题…」）。"""
    m = _STAT_PAT.search(title)
    t = title[:m.start()] if m else title
    return t.rstrip('　 ')

def existing_anchor_paras(doc_root):
    out = []
    for p in doc_root.find(q('body')).iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None:
            continue
        ps = ppr.find(q('pStyle'))
        if ps is not None and ps.get(q('val')) == ANCHOR_STYLE_ID:
            out.append(p)
    return out

# ---------------------------------------------------------------- 串构造与串宽

def make_run_xml(text):
    return ('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'
            % (RPR_HF, text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')))

def field_runs_xml(instr, cache):
    """复杂域五run：begin→instrText→separate→缓存文本→end（禁fldSimple——§7域形态）。"""
    esc = lambda s: str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r>%s<w:instrText xml:space="preserve">%s</w:instrText></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="end"/></w:r>'
            % (RPR_HF, RPR_HF, esc(instr), RPR_HF, RPR_HF, esc(cache), RPR_HF))

def samestring_para_xml(prefix, n_text, styleref_cache, page_cache):
    """同串单段：前段（含件型）＋（共N页）＋全角空格＋STYLEREF节名域＋全角空格＋第X页（PAGE域）。"""
    runs = (make_run_xml(prefix) + make_run_xml('（共%s页）' % n_text)
            + make_run_xml('　') + field_runs_xml(INSTR_STYLEREF, styleref_cache)
            + make_run_xml('　第') + field_runs_xml(INSTR_PAGE, page_cache)
            + make_run_xml('页'))
    # 2026-09-01 E2补丁：补 spacing 288 auto（与工具/字号双档改版.py 页眉页脚冻结形态对齐——
    # 缺失时该段落继承 docDefaults line=410 atLeast，②check-only 判 spacing 偏离）
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="288" w:lineRule="auto"/>'
            '<w:jc w:val="left"/></w:pPr>%s</w:p>' % runs)

def est_twips(s):
    """9pt字符宽估算：CJK/全角＝180缇、ASCII半角＝90缇（保守：·—等按全角计）。"""
    w = 0
    for ch in s:
        if ord(ch) >= 0x2E80 or ch in '·—…－（）　、；：，。？！「」『』':
            w += 180
        else:
            w += 90
    return w

def usable_twips(doc_root):
    sp = doc_root.find(q('body')).findall(q('sectPr'))
    sp = sp[-1] if sp else None
    if sp is None:
        raise ToolError('document.xml 无 body sectPr')
    sz, mar = sp.find(q('pgSz')), sp.find(q('pgMar'))
    if sz is None or mar is None:
        raise ToolError('sectPr 缺 pgSz/pgMar')
    return int(sz.get(q('w'))) - int(mar.get(q('left'))) - int(mar.get(q('right')))

def com_linecount(strings):
    """Word COM实测行数：A4＋1.5cm边距版心、宋体/TNR 9pt单段，返回各串ComputeStatistics(wdStatisticLines)。
    自建实例用完Quit（§1/§4⑧）。"""
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    res = []
    try:
        doc = word.Documents.Add()
        try:
            ps = doc.PageSetup
            ps.PaperSize = 7                     # wdPaperA4（实测本机 CentimetersToPoints 分发不可用，用点值直设）
            cm = lambda c: c * 28.3465           # 1cm = 28.3465pt
            ps.TopMargin = ps.BottomMargin = cm(1.5)
            ps.LeftMargin = ps.RightMargin = cm(1.5)
            for s in strings:
                doc.Content.Delete()
                rng = doc.Range(0, 0)
                rng.InsertAfter(s)
                r2 = doc.Range(0, len(s))
                r2.Font.NameFarEast = '宋体'
                r2.Font.Name = 'Times New Roman'
                r2.Font.Size = 9
                res.append(r2.ComputeStatistics(1))   # 1 = wdStatisticLines
        finally:
            doc.Close(False)
    finally:
        word.Quit()
    return res

# ---------------------------------------------------------------- 部件重建（字符串级手术）

def replace_paras_with(part_xml, para_xml, root_close):
    """删除部件内全部旧段（含自闭合空段与表格——整段退役），在根闭标签前插入新段。保留根元素声明。"""
    pat = re.compile(r'<w:p\b[^>]*/>|<w:p\b[^>]*>.*?</w:p>|<w:tbl\b.*?</w:tbl>', re.S)
    n_removed = len(pat.findall(part_xml))
    xml2 = pat.sub('', part_xml)
    xml2 = re.sub(r'<w:bookmarkStart\b[^>]*/>|<w:bookmarkEnd\b[^>]*/>', '', xml2)
    if root_close not in xml2:
        raise ToolError('部件根闭标签 %s 未找到' % root_close)
    xml2 = xml2.replace(root_close, para_xml + root_close)
    return xml2, n_removed

def visible_text(part_xml):
    return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', part_xml))

def ensure_pgmar_and_notitlepg(doc_xml):
    """sectPr：pgMar header=283/footer=850（缺省即补）；剔titlePg。返回(新xml, 改动标志)。"""
    orig = doc_xml
    def fix_sect(s):
        s = re.sub(r'<w:titlePg/>|<w:titlePg>.*?</w:titlePg>', '', s, flags=re.S)
        for attr, val in (('header', HEADER_TWIPS), ('footer', FOOTER_TWIPS)):
            if re.search(r'w:%s="' % attr, s):
                s = re.sub(r'(<w:pgMar[^>]*?)w:%s="\d+"' % attr, r'\1w:%s="%s"' % (attr, val), s)
            elif '<w:pgMar ' in s:
                s = re.sub(r'(<w:pgMar )', r'\1w:%s="%s" ' % (attr, val), s, count=1)
        return s
    parts = re.split(r'(<w:sectPr.*?</w:sectPr>)', doc_xml, flags=re.S)
    for i in range(1, len(parts), 2):
        parts[i] = fix_sect(parts[i])
    return ''.join(parts), ''.join(parts) != orig

def ensure_settings(settings_xml):
    s = re.sub(r'<w:evenAndOddHeaders[^>]*/>', '', settings_xml)
    if '<w:updateFields' not in s:
        ins = '<w:updateFields w:val="true"/>'
        s = s.replace('<w:compat', ins + '<w:compat', 1) if '<w:compat' in s else s.replace('</w:settings>', ins + '</w:settings>')
    return s

def ensure_anchor_style(styles_xml, normal_sid):
    """styles.xml：节名锚样式在位（幂等＝同串规格重写；basedOn＝真实Normal styleId）。返回(新xml, 新建?)。"""
    style_xml = ('<w:style w:type="paragraph" w:styleId="%s">'
                 '<w:name w:val="%s"/><w:basedOn w:val="%s"/><w:qFormat/>'
                 '<w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
                 '<w:jc w:val="left"/></w:pPr>'
                 '<w:rPr><w:color w:val="FFFFFF"/><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>'
                 '</w:style>') % (ANCHOR_STYLE_ID, ANCHOR_STYLE_NAME, normal_sid)
    pat = re.compile(r'<w:style\b[^>]*w:styleId="%s"[^>]*>.*?</w:style>|<w:style\b[^>]*w:styleId="%s"[^>]*/>'
                     % (re.escape(ANCHOR_STYLE_ID), re.escape(ANCHOR_STYLE_ID)), re.S)
    existed = bool(pat.search(styles_xml))
    styles2 = pat.sub('', styles_xml)
    if '</w:styles>' not in styles2:
        raise ToolError('styles.xml 根闭标签未找到')
    return styles2.replace('</w:styles>', style_xml + '</w:styles>'), not existed

def anchor_para_xml(text):
    """节名锚段：样式＋直接格式双保险（1pt白、line=20 exact、非隐藏、无底纹无边框、无keepX/分页属性）。"""
    esc = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return ('<w:p><w:pPr><w:pStyle w:val="%s"/>'
            '<w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
            '<w:jc w:val="left"/></w:pPr>'
            '<w:r><w:rPr><w:color w:val="FFFFFF"/><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>'
            '<w:t xml:space="preserve">%s</w:t></w:r></w:p>') % (ANCHOR_STYLE_ID, esc)

def build_anchor_element(text):
    p = etree.Element(q('p'))
    ppr = etree.SubElement(p, q('pPr'))
    etree.SubElement(ppr, q('pStyle')).set(q('val'), ANCHOR_STYLE_ID)
    sp = etree.SubElement(ppr, q('spacing'))
    sp.set(q('before'), '0'); sp.set(q('after'), '0'); sp.set(q('line'), '20'); sp.set(q('lineRule'), 'exact')
    etree.SubElement(ppr, q('jc')).set(q('val'), 'left')
    r = etree.SubElement(p, q('r'))
    rpr = etree.SubElement(r, q('rPr'))
    etree.SubElement(rpr, q('color')).set(q('val'), 'FFFFFF')
    etree.SubElement(rpr, q('sz')).set(q('val'), '2')
    etree.SubElement(rpr, q('szCs')).set(q('val'), '2')
    t = etree.SubElement(r, q('t')); t.set('{%s}space' % XMLNS, 'preserve'); t.text = text
    return p

# ---------------------------------------------------------------- 主流程

def main(argv):
    argv = list(argv)
    token = None
    if '--token' in argv:
        i = argv.index('--token')
        if i + 1 < len(argv) and not argv[i + 1].startswith('--'):
            token = argv[i + 1]
            del argv[i:i + 2]
    for a in list(argv):
        if a.startswith('--token='):
            token = a.split('=', 1)[1]
            argv.remove(a)
    args = [a for a in argv if not a.startswith('--')]
    flags = set(a for a in argv if a.startswith('--'))
    verbose = '--verbose' in flags
    dry = '--dry-run' in flags
    no_brand = '--no-brand' in flags   # 同部分一致性：部分内他卷省前缀时本卷强制同形态
    if len(args) != 2 or not token or '·' not in token:
        print(__doc__)
        return 1
    src, dst = args
    token_suffix = token.split('·')[-1]   # 件型尾段（如「衔接」/「讲练」）
    token_head = token.split('·')[0]      # 章段（如「第2章」）
    if os.path.abspath(src) == os.path.abspath(dst):
        print('[中止] 输出路径与输入相同——本工具只处理副本，禁止原地改写。')
        return 2
    if not os.path.exists(src):
        print('[中止] 输入不存在：', src)
        return 2

    zin = zipfile.ZipFile(src)
    try:
        names = [n for n in zin.namelist() if not n.endswith('/')]
        blob = {n: zin.read(n) for n in names}
        doc_root = etree.fromstring(blob['word/document.xml'])
        styles_root = etree.fromstring(blob['word/styles.xml'])

        # ---- A1 单页眉单页脚 ----
        hrefs = [(hr.get(q('type')) or 'default', hr.get('{%s}id' % R)) for hr in doc_root.iter(q('headerReference'))]
        frefs = [(fr.get(q('type')) or 'default', fr.get('{%s}id' % R)) for fr in doc_root.iter(q('footerReference'))]
        if len(hrefs) != 1 or len(frefs) != 1:
            print('[中止] A1 headerReference=%d、footerReference=%d（要求各恰1个）——多定义件需人工裁决。'
                  % (len(hrefs), len(frefs)))
            return 2
        rels_root = etree.fromstring(blob['word/_rels/document.xml.rels'])
        relmap = {rel.get('Id'): rel.get('Target') for rel in rels_root}
        def part_of(rid):
            tgt = relmap.get(rid)
            return ('word/' + tgt.lstrip('/')) if tgt else None
        hname, fname = part_of(hrefs[0][1]), part_of(frefs[0][1])
        if not hname or hname not in blob or not fname or fname not in blob:
            print('[中止] A1 rels解析不到页眉/页脚部件（%s / %s）。' % (hname, fname))
            return 2
        hdr_xml = blob[hname].decode('utf-8')
        ftr_xml = blob[fname].decode('utf-8')

        # ---- A2 节标题在位 ----
        sid3 = find_heading3_style_id(styles_root)
        sec_paras = section_paras(doc_root, sid3)
        if not sid3 or not sec_paras:
            print('[中止] A2 正文无挂「标题3」样式段落（styleId=%s，计数=%d）——先跑 工具/节标题样式挂载.py。'
                  % (sid3, len(sec_paras)))
            return 2
        titles = [para_text(p) for p in sec_paras]
        anchors_txt = [anchor_text_of(t) for t in titles]
        n_sec = len(sec_paras)
        print('A2 节标题：styleId=%s，共%d个；锚段文本（剥统计段）首末=%r / %r'
              % (sid3, n_sec, anchors_txt[0], anchors_txt[-1]))

        # ---- Normal styleId（basedOn真实值）----
        normal_sid = find_normal_style_id(styles_root)
        if not normal_sid:
            print('[中止] styles.xml 解析不到真实 Normal styleId——禁字面量悬空（经验定论），人工裁决。')
            return 2
        print('锚样式 basedOn＝真实 Normal styleId=%r（非字面量）' % normal_sid)

        # ---- 锚段在位检查（幂等）----
        exist_anchors = existing_anchor_paras(doc_root)
        insert_needed = True
        if exist_anchors:
            if len(exist_anchors) == n_sec:
                ok = all(a.getnext() is p for a, p in zip(exist_anchors, sec_paras))
                if ok:
                    insert_needed = False
                    print('幂等：锚段已 %d 个且逐节标题直接前驱——跳过插入。' % n_sec)
            if insert_needed and exist_anchors:
                print('[中止] 既有锚段 %d 个与节标题数 %d 不符或前驱关系破坏——人工裁决。'
                      % (len(exist_anchors), n_sec))
                return 2

        # ---- 前段推导（既有页眉文本；同串件截「（共」前）----
        hdr_text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', hdr_xml))
        prefix_src = hdr_text.split('（共')[0].split('\t')[0]
        had_brand = prefix_src.startswith(BRAND)
        prefix_core = prefix_src[len(BRAND):] if had_brand else prefix_src   # 去既有品牌前缀（防双拼）
        if not prefix_core.endswith(token_suffix) or token_head not in prefix_core:
            print('[中止] 既有页眉前段 %r 与件型token %r 不符（应含章段且以件型尾段收尾）——人工裁决。'
                  % (prefix_core, token))
            return 2
        print('前段（取自既有页眉，整体替换旧串；本位%s品牌前缀）＝%r'
              % ('含' if had_brand else '不含', prefix_core))

        # ---- 串宽估算＋前缀决策（--no-brand＝同部分一致性强制：部分内任一卷省前缀则各卷都省）----
        usable = usable_twips(doc_root)
        longest_anchor = max(anchors_txt, key=est_twips)
        def worst(with_brand):
            return (('羿郭工作室·' if with_brand else '') + prefix_core
                    + '（共999页）　' + longest_anchor + '　第999页')
        est_full, est_nopre = est_twips(worst(True)), est_twips(worst(False))
        keep_brand = (est_full <= usable) and not no_brand
        if no_brand:
            print('--no-brand：同部分一致性强制省略品牌前缀（部分内他卷实测放不下时各卷同形态）。')
        prefix = BRAND if keep_brand else ''
        print('串宽估算：版心=%d缇；worst-case带前缀=%d缇、省前缀=%d缇（最长锚=%r，N/X按3位）→ %s'
              % (usable, est_full, est_nopre, longest_anchor,
                 '保留品牌前缀' if keep_brand else '省略「羿郭工作室·」前缀（§7：同串单行放不下时）'))
        # COM实测行数断言（worst-case）
        try:
            lines = com_linecount([worst(True), worst(False)])
        except Exception as e:
            print('[中止] COM串宽实测失败：', e)
            return 2
        print('A5 COM实测行数（worst-case，宋体/TNR 9pt）：带前缀=%d行、省前缀=%d行（断言＝1）'
              % (lines[0], lines[1]))
        if keep_brand and lines[0] > 1:
            keep_brand = lines[0] == 1
            print('  带前缀COM实测>1行 → 降级省略品牌前缀。')
        prefix = BRAND if keep_brand else ''
        if (lines[0] if keep_brand else lines[1]) > 1:
            print('[中止] A5 省前缀后COM实测仍>1行（%d）——串宽断言失败，人工裁决。'
                  % (lines[0] if keep_brand else lines[1]))
            return 2

        # ---- sectPr现start（PAGE域缓存初值）----
        mstart = re.search(r'<w:pgNumType w:start="(\d+)"/>', blob['word/document.xml'].decode('utf-8'))
        start0 = mstart.group(1) if mstart else '1'

        # ---- 同串重建（页眉＝页脚同内容）----
        para = samestring_para_xml(prefix + prefix_core, N_PLACEHOLDER, anchors_txt[0], start0)
        hdr2, n_h = replace_paras_with(hdr_xml, para, '</w:hdr>')
        ftr2, n_f = replace_paras_with(ftr_xml, para, '</w:ftr>')
        expect_vis = (prefix + prefix_core + '（共%s页）　%s　第%s页'
                      % (N_PLACEHOLDER, anchors_txt[0], start0))
        for tag, xml2, nrem in (('页眉', hdr2, n_h), ('页脚', ftr2, n_f)):
            vis = visible_text(xml2)
            assert vis == expect_vis, '%s可见文本异常: %r（预期 %r）' % (tag, vis, expect_vis)
            assert xml2.count('fldCharType="begin"') == 2 and xml2.count('fldCharType="end"') == 2, tag + '域组数≠2'
            assert 'fldSimple' not in xml2 and 'NUMPAGES' not in xml2, tag + '域形态残留'
            assert INSTR_STYLEREF in xml2 and INSTR_PAGE in xml2, tag + 'instrText缺失'
            print('同串重建（%s部件，退役旧段%d个）：可见文本＝%r' % (tag, nrem, vis))

        # ---- styles / settings / document ----
        styles2, style_new = ensure_anchor_style(blob['word/styles.xml'].decode('utf-8'), normal_sid)
        print('锚样式%s：styleId=%s name=%s basedOn=%s（1pt白、line=20 exact、非隐藏、无底纹无边框）'
              % ('新建' if style_new else '幂等重写', ANCHOR_STYLE_ID, ANCHOR_STYLE_NAME, normal_sid))
        settings2 = ensure_settings(blob['word/settings.xml'].decode('utf-8'))

        doc_changed = insert_needed
        if insert_needed:
            for p, txt in zip(sec_paras, anchors_txt):
                p.addprevious(build_anchor_element(txt))
            doc_xml2 = etree.tostring(doc_root, xml_declaration=True, encoding='UTF-8', standalone=True).decode('utf-8')
        else:
            doc_xml2 = blob['word/document.xml'].decode('utf-8')
        doc_xml2, mar_changed = ensure_pgmar_and_notitlepg(doc_xml2)
        doc_changed = doc_changed or mar_changed
        n_title = blob['word/document.xml'].decode('utf-8').count('<w:titlePg')
        if mar_changed or n_title:
            print('sectPr版面：pgMar header=%s/footer=%s 强制、titlePg剔除%d处%s'
                  % (HEADER_TWIPS, FOOTER_TWIPS, n_title, '（含锚段插入）' if insert_needed else ''))

        if dry:
            print('[dry-run] 不写输出。锚段%d个%s；同串=%r；N占位=%r；PAGE缓存=%s'
                  % (n_sec, '' if insert_needed else '（已在位跳过）', expect_vis, N_PLACEHOLDER, start0))
            return 0

        # ---- A3/A4 输出复检（对将写入的xml串断言，再落盘）----
        out_doc = etree.fromstring(doc_xml2.encode('utf-8'))
        chk_anchors = existing_anchor_paras(out_doc)
        assert len(chk_anchors) == n_sec, '锚段数%d≠节标题数%d' % (len(chk_anchors), n_sec)
        assert all(a.getnext() is p for a, p in zip(chk_anchors, section_paras(out_doc, sid3))), '锚段-节标题前驱关系断裂'
        chk_styles = etree.fromstring(styles2.encode('utf-8'))
        st = None
        for s_ in chk_styles.findall(q('style')):
            if s_.get(q('styleId')) == ANCHOR_STYLE_ID:
                st = s_
        assert st is not None, '锚样式未在位'
        assert st.find(q('basedOn')).get(q('val')) == normal_sid, 'basedOn≠真实Normal'
        assert st.find(q('rPr')).find(q('sz')).get(q('val')) == '2'
        assert st.find(q('rPr')).find(q('color')).get(q('val')) == 'FFFFFF'
        spc = st.find(q('pPr')).find(q('spacing'))
        assert spc.get(q('line')) == '20' and spc.get(q('lineRule')) == 'exact'
        assert st.find(q('rPr')).find(q('vanish')) is None, '锚样式不得隐藏（STYLEREF不认）'
        for a_p in chk_anchors:
            assert a_p.find('.//%s' % q('vanish')) is None, '锚段含隐藏属性'
            assert a_p.find(q('pPr')).find(q('shd')) is None and a_p.find(q('pPr')).find(q('pBdr')) is None, '锚段带底纹/边框'
            assert a_p.find(q('pPr')).find(q('keepNext')) is None and a_p.find(q('pPr')).find(q('keepLines')) is None \
                and a_p.find(q('pPr')).find(q('pageBreakBefore')) is None, '锚段带禁排属性（§7⑥）'
        assert '<w:updateFields' in settings2 and 'evenAndOddHeaders' not in settings2
        for xml2 in (hdr2, ftr2):
            assert re.search(r'<w:jc w:val="left"/>', xml2) and xml2.count('<w:jc') == 1, '页眉/页脚对齐异常'
            szs = re.findall(r'<w:sz w:val="(\d+)"/>', xml2)
            assert szs and set(szs) == {'18'}, '同串run字号≠18半点: %r' % szs
        print('A4 结构自检：PASS（锚段数=%d=节标题数且逐段直接前驱；两部件各2组复杂域、无fldSimple/'
              'NUMPAGES、jc=left、全run 18半点；basedOn=%s；pgMar %s/%s；settings updateFields）'
              % (n_sec, normal_sid, HEADER_TWIPS, FOOTER_TWIPS))

        # ---- 落盘（保持成员原序）----
        tmp = dst + '.tmp'
        replace = {'word/document.xml': doc_xml2.encode('utf-8'),
                   'word/styles.xml': styles2.encode('utf-8'),
                   'word/settings.xml': settings2.encode('utf-8'),
                   hname: hdr2.encode('utf-8'), fname: ftr2.encode('utf-8')}
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for nm in names:
                zout.writestr(nm, replace.get(nm, blob[nm]))
        os.replace(tmp, dst)

        # ---- A3 写盘后复检 ----
        with zipfile.ZipFile(dst) as zchk:
            bad = [n for n in names if n not in replace and zchk.read(n) != blob[n]]
            missing = [n for n in names if n not in zchk.namelist()]
            for nm, data in replace.items():
                assert zchk.read(nm) == data, '写盘后回读不符：%s' % nm
        if bad or missing:
            print('[断言失败 A3] 输出包非预期改动：%s' % (bad + missing))
            os.remove(dst)
            return 2
        print('A3 只动目标件：PASS（其余 %d 个条目与输入字节逐一相等）' % (len(names) - len(replace)))
        print('完成 -> %s（锚段%d；同串页眉页脚；N占位=%r待盖章填值；PAGE缓存=%s）'
              % (dst, n_sec, N_PLACEHOLDER, start0))
        return 0
    finally:
        zin.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
