# -*- coding: utf-8 -*-
#
# 沿革：2026-08-30 工具债清偿（看板工具债③）新建——公共规则§7页眉条款（2026-08-30 面包屑拍板）
#   落地：成品件单行页眉右侧追加「当前节名」STYLEREF 复杂域（前置工程＝工具/节标题样式挂载.py
#   已把教材节标题挂内置样式「标题3」）。存量件由页眉面包屑回扫轮统一补挂。
#
"""页眉面包屑挂载.py — 页眉右侧挂「当前节名」STYLEREF 复杂域（只处理副本，断言不过不动输出文件）

规格（公共规则§7页眉条款，2026-08-30拍板）：
  · 在既有单行页眉段落末尾追加：右停靠制表位 ＋ 制表符 run ＋ STYLEREF 复杂域
    （fldChar begin → w:instrText → fldChar separate → 缓存文本 run
    （写该件第一个节标题实测文本）→ fldChar end；instrText 实测定值＝
    「 STYLEREF "标题 3" 」——条款字面「STYLEREF 标题3」实测不解析，差异备案见上）；
    域 run 字号小五与页眉一致
    （直接深拷贝页眉既有文本 run 的 rPr，保证字体字号零偏差）；
  · 段落保持 jc=left 不变；不新增页眉定义（件已有单页眉——断言仅 1 个 headerReference，
    多于 1 个报错退出人工裁决）；不动页脚、不动正文。
  · 制表位位置＝版心右缘，按该件 sectPr 实测动态计算：pgSz.w − pgMar.left − pgMar.right
    （A4 11906 − 2×850 ＝ 10206 缇；拍板任务书拟值≈9026 与「A4减2×850」公式自相矛盾，
    按版心右缘语义取公式实算值——实测见 报告-页眉面包屑.md）；无前导符（拍板：选无）。

前置依赖（不满足报错退出码 2）：文档正文须已有挂「标题3」（name heading 3/标题3）样式的段落——
  先用 工具/节标题样式挂载.py 处理；本工具输入应是已挂样式件。

安全断言（全过才写输出，任一不过退出码 2、不产生输出文件）：
  A1 单页眉——document.xml 恰有 1 个 headerReference 且 rels 可解析到实际部件；
  A2 前置依赖——正文 pStyle＝标题3 styleId 的段落 ≥1（挂载计数落报告）；
  A3 只动页眉部件——输出包除页眉部件外其余条目内容逐一不变（document.xml/页脚/styles 均字节原样）；
  A4 域结构自检——重构后页眉复检：恰 1 组 fldChar begin/separate/end 且顺序正确、
     instrText 含 STYLEREF 与 标题3、无 fldSimple、右停靠制表位在位、jc=left 保持、
     左侧既有文本 run 逐字不变、追加 run 的 rPr 与页眉既有 run 一致（sz 同值）。
幂等：页眉已含 STYLEREF 域（instrText 或 fldSimple 任一形态）则跳过，输出＝输入字节级拷贝、零改动。

缓存风险备案（§7页眉条款口径）：STYLEREF 域缓存文本为挂载时写死的「该件第一个节标题」——
  WPS/静态查看器可能显示缓存旧节名而不重算；Word/打印/PDF 导出链路必然重算，印制实物零风险；
  中招回退预案＝右侧退化为静态件名文字或删右段（其余设计不动）。

用法: python 页眉面包屑挂载.py <in.docx> <out.docx> [--verbose] [--dry-run]
"""
import sys, io, os, re, zipfile, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def q(t): return '{%s}%s' % (W, t)

STYLE_NAME_CANDIDATES = ('heading 3', '标题3')
DEFAULT_STYLE_ID = 'Heading3'
# 域指令实测定值（2026-08-30 选必1第2章讲练件48页实测）：STYLEREF 按样式名解析，
#   styles.xml 内建名 name="heading 3"（中文 Word 界面名「标题 3」）——
#   · 「STYLEREF 标题3」（条款字面，无空格）→ 渲染错误文本「错误!使用…将标题3应用于…」；
#   · 「STYLEREF "heading 3"/"Heading 3"」（内建英文名）→ 同样不解析（中文 Word 实测）；
#   · 「STYLEREF "标题 3"」（本地化名＋半角引号＋名内空格，即中文 Word 插入域的原生写法）→ 正确解析。
#   本工具按实测可用形态落域；与条款字面「STYLEREF 标题3」的差异在 报告-页眉面包屑.md 备案。
INSTR_TEXT = ' STYLEREF "标题 3" '

class ToolError(Exception):
    pass

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def find_heading3_style_id(styles_root):
    """返回「标题3」样式的 styleId（按 name 候选匹配，styleId=Heading3 兜底）。"""
    for st in styles_root.findall(q('style')):
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if nv.strip().lower() in STYLE_NAME_CANDIDATES:
            return st.get(q('styleId'))
    for st in styles_root.findall(q('style')):
        if st.get(q('styleId')) == DEFAULT_STYLE_ID:
            return st.get(q('styleId'))
    return None

def count_heading3_paras(doc_root, sid):
    n = 0
    for p in doc_root.find(q('body')).iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None:
            continue
        ps = ppr.find(q('pStyle'))
        if ps is not None and ps.get(q('val')) == sid:
            n += 1
    return n

def first_heading3_text(doc_root, sid):
    for p in doc_root.find(q('body')).iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None:
            continue
        ps = ppr.find(q('pStyle'))
        if ps is not None and ps.get(q('val')) == sid:
            return para_text(p)
    return None

def header_ref(doc_root):
    """返回 (type, rId) 列表。"""
    out = []
    for hr in doc_root.iter(q('headerReference')):
        rid = hr.get('{%s}id' % R)
        out.append((hr.get(q('type')) or 'default', rid))
    return out

def body_sect_pr(doc_root):
    sp = doc_root.find(q('body')).findall(q('sectPr'))
    return sp[-1] if sp else None

def tab_position(doc_root):
    """版心右缘（缇）＝ pgSz.w − pgMar.left − pgMar.right（取 body sectPr 实测值）。"""
    sp = body_sect_pr(doc_root)
    if sp is None:
        raise ToolError('document.xml 无 body sectPr，无法计算版心右缘')
    sz, mar = sp.find(q('pgSz')), sp.find(q('pgMar'))
    if sz is None or mar is None:
        raise ToolError('sectPr 缺 pgSz/pgMar，无法计算版心右缘')
    w  = int(sz.get(q('w')))
    lf = int(mar.get(q('left'))); rt = int(mar.get(q('right')))
    return w - lf - rt, (w, lf, rt)

def has_styleref_field(hdr_root):
    for it in hdr_root.iter(q('instrText')):
        if 'STYLEREF' in (it.text or '').upper():
            return True
    for fs in hdr_root.iter(q('fldSimple')):
        if 'STYLEREF' in (fs.get(q('instr')) or '').upper():
            return True
    return False

def make_run(rpr, child):
    r = etree.Element(q('r'))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    r.append(child)
    return r

def build_header(hdr_root, sid_tab_pos, cached_text):
    """在页眉第一段末尾追加：右停靠制表位＋制表符run＋STYLEREF复杂域。返回该段。"""
    paras = hdr_root.findall(q('p'))
    if not paras:
        raise ToolError('页眉部件内无段落')
    p = paras[0]
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    # 右停靠制表位（无前导符）——CT_PPr 序中 tabs 在 jc 之前
    tabs = ppr.find(q('tabs'))
    if tabs is None:
        tabs = etree.Element(q('tabs'))
        jc = ppr.find(q('jc'))
        ppr.insert(list(ppr).index(jc) if jc is not None else len(list(ppr)), tabs)
    for old in tabs.findall(q('tab')):
        if old.get(q('val')) == 'right' and old.get(q('pos')) == str(sid_tab_pos):
            break
    else:
        tb = etree.SubElement(tabs, q('tab'))
        tb.set(q('val'), 'right')
        tb.set(q('pos'), str(sid_tab_pos))
    # 域 run 的 rPr＝页眉既有文本 run 的 rPr（深拷贝，保证字号字体零偏差）
    rpr = None
    for r in p.findall(q('r')):
        if r.find(q('t')) is not None:
            rpr = r.find(q('rPr'))
            break
    # 依序追加：制表符 run → begin → instrText → separate → 缓存文本 run → end
    p.append(make_run(rpr, etree.Element(q('tab'))))
    fb = etree.Element(q('fldChar')); fb.set(q('fldCharType'), 'begin')
    p.append(make_run(rpr, fb))
    it = etree.Element(q('instrText')); it.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    it.text = INSTR_TEXT
    p.append(make_run(rpr, it))
    fs = etree.Element(q('fldChar')); fs.set(q('fldCharType'), 'separate')
    p.append(make_run(rpr, fs))
    ct = etree.Element(q('t')); ct.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    ct.text = cached_text
    p.append(make_run(rpr, ct))
    fe = etree.Element(q('fldChar')); fe.set(q('fldCharType'), 'end')
    p.append(make_run(rpr, fe))
    return p

def verify_header(hdr_root, tab_pos, left_texts_before, base_rpr_sig):
    """断言 A4：域结构/制表位/jc/左侧文本零变化/追加run格式一致。返回错误清单。"""
    errs = []
    p = hdr_root.findall(q('p'))[0]
    ppr = p.find(q('pPr'))
    jc = ppr.find(q('jc')) if ppr is not None else None
    if jc is None or jc.get(q('val')) != 'left':
        errs.append('jc=left 保持失败（实测 %s）' % (jc.get(q('val')) if jc is not None else None))
    tabs = ppr.find(q('tabs')) if ppr is not None else None
    hit = tabs is not None and any(
        tb.get(q('val')) == 'right' and tb.get(q('pos')) == str(tab_pos) and tb.get(q('leader')) is None
        for tb in tabs.findall(q('tab')))
    if not hit:
        errs.append('右停靠制表位（pos=%d，无前导符）不在位' % tab_pos)
    ftypes = [fc.get(q('fldCharType')) for fc in p.iter(q('fldChar'))]
    if ftypes != ['begin', 'separate', 'end']:
        errs.append('fldChar 序列≠[begin,separate,end]（实测 %s）' % ftypes)
    instrs = [it.text or '' for it in p.iter(q('instrText'))]
    norm = instrs[0].replace('"', '').replace(' ', '') if instrs else ''
    if len(instrs) != 1 or 'STYLEREF' not in norm.upper() or '标题3' not in norm:
        errs.append('instrText 异常：%r' % instrs)
    if len(list(hdr_root.iter(q('fldSimple')))) != 0:
        errs.append('出现 fldSimple（禁用）')
    # 左侧既有文本 run 逐字不变
    left_now = [t.text or '' for t in p.iter(q('t'))][:-1]  # 末一个是新缓存文本
    if left_now != left_texts_before:
        errs.append('左侧既有文本变化：%r -> %r' % (left_texts_before, left_now))
    # 追加 5 个 run 的 rPr 与基准一致
    runs = p.findall(q('r'))
    for r in runs[-5:]:
        rp = r.find(q('rPr'))
        sig = [(etree.QName(c).localname, tuple(sorted((k.split('}')[-1], v) for k, v in c.attrib.items())))
               for c in rp] if rp is not None else None
        if sig != base_rpr_sig:
            errs.append('追加 run 的 rPr 与页眉基准不一致')
            break
    return errs

def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    flags = set(a for a in argv if a.startswith('--'))
    verbose = '--verbose' in flags
    dry = '--dry-run' in flags
    if len(args) != 2:
        print(__doc__)
        return 1
    src, dst = args
    if os.path.abspath(src) == os.path.abspath(dst):
        print('[中止] 输出路径与输入相同——本工具只处理副本，禁止原地改写。')
        return 2
    if not os.path.exists(src):
        print('[中止] 输入不存在：', src)
        return 2

    zin = zipfile.ZipFile(src)
    doc_root = etree.fromstring(zin.read('word/document.xml'))
    styles_root = etree.fromstring(zin.read('word/styles.xml'))

    # ---- A1 单页眉 ----
    refs = header_ref(doc_root)
    if len(refs) != 1:
        print('[中止] A1 headerReference 数=%d（要求恰 1 个单页眉件）——多页眉件需人工裁决，按安全纪律不动文件。' % len(refs))
        return 2
    htype, rid = refs[0]
    rels_root = etree.fromstring(zin.read('word/_rels/document.xml.rels'))
    hname = None
    for rel in rels_root:
        if rel.get('Id') == rid:
            hname = 'word/' + rel.get('Target').lstrip('/')
            break
    if hname is None or hname not in zin.namelist():
        print('[中止] A1 rels 中解析不到页眉部件（rId=%s）。' % rid)
        return 2

    hdr_root = etree.fromstring(zin.read(hname))

    # ---- 幂等 ----
    if has_styleref_field(hdr_root):
        with open(dst, 'wb') as f:
            f.write(open(src, 'rb').read())
        print('幂等：页眉已含 STYLEREF 域，跳过零改动（输出=输入字节级拷贝）-> %s' % dst)
        return 0

    # ---- A2 前置依赖：正文已有「标题3」样式段 ----
    sid = find_heading3_style_id(styles_root)
    n_h3 = count_heading3_paras(doc_root, sid) if sid else 0
    if not sid or n_h3 == 0:
        print('[中止] A2 前置依赖不满足：正文无挂「标题3」样式的段落（styleId=%s，计数=%d）'
              '——先用 工具/节标题样式挂载.py 处理。' % (sid, n_h3))
        return 2
    first_txt = first_heading3_text(doc_root, sid)
    print('前置依赖：「标题3」styleId=%s，正文挂载段 %d 个；首节标题（域缓存文本）＝%r' % (sid, n_h3, first_txt))

    # ---- 制表位位置 ----
    try:
        tab_pos, geom = tab_position(doc_root)
    except ToolError as e:
        print('[中止]', e)
        return 2
    print('版心右缘＝pgSz.w %d − left %d − right %d ＝ %d 缇（右停靠制表位，无前导符）' % (geom[0], geom[1], geom[2], tab_pos))

    # ---- 改造页眉 ----
    p0 = hdr_root.findall(q('p'))[0]
    left_texts_before = [t.text or '' for t in p0.iter(q('t'))]
    rpr0 = None
    for r in p0.findall(q('r')):
        if r.find(q('t')) is not None:
            rpr0 = r.find(q('rPr'))
            break
    base_rpr_sig = ([(etree.QName(c).localname, tuple(sorted((k.split('}')[-1], v) for k, v in c.attrib.items())))
                     for c in rpr0] if rpr0 is not None else None)
    try:
        build_header(hdr_root, tab_pos, first_txt)
    except ToolError as e:
        print('[中止]', e)
        return 2

    # ---- A4 结构自检 ----
    errs = verify_header(hdr_root, tab_pos, left_texts_before, base_rpr_sig)
    if errs:
        print('[断言失败 A4] 页眉重构自检不过：%d 项' % len(errs))
        for e in errs:
            print('   -', e)
        return 2
    print('断言 A4 域结构自检：PASS（fldChar begin/separate/end 配对、instrText=%r、无 fldSimple、'
          '右停靠制表位 pos=%d、jc=left 保持、左侧文本逐字不变、追加 run rPr 与页眉基准一致）' % (INSTR_TEXT, tab_pos))

    # ---- A3 只动页眉部件（写盘后对成品包逐条目复检）----
    new_hdr = etree.tostring(hdr_root, xml_declaration=True, encoding='UTF-8', standalone=True)
    src_zip_cache = {n: zin.read(n) for n in zin.namelist() if not n.endswith('/')}

    if dry:
        print('[dry-run] 不写输出。页眉部件=%s，制表位 pos=%d，缓存文本=%r' % (hname, tab_pos, first_txt))
        return 0

    # ---- 落盘 ----
    zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    try:
        for item in zin.infolist():
            if item.filename.endswith('/'):
                continue
            data = new_hdr if item.filename == hname else src_zip_cache[item.filename]
            zout.writestr(item.filename, data, compress_type=item.compress_type)
    finally:
        zout.close()

    # ---- A3 写盘后复检：输出包除页眉部件外逐条目与输入字节相等 ----
    zchk = zipfile.ZipFile(dst)
    try:
        bad = [n for n in src_zip_cache
               if n != hname and zchk.read(n) != src_zip_cache[n]]
        missing = [n for n in src_zip_cache if n not in zchk.namelist()]
    finally:
        zchk.close()
    if bad or missing:
        print('[断言失败 A3] 输出包出现非预期改动：%s' % (bad + missing))
        os.remove(dst)
        return 2
    print('断言 A3 只动页眉部件：PASS（其余 %d 个条目与输入字节逐一相等，document.xml/页脚/styles 不触碰）'
          % (len(src_zip_cache) - 1))

    print('输出 -> %s（替换 %s；未新增页眉定义，不动页脚）' % (dst, hname))
    print('完成：页眉右侧 STYLEREF 复杂域挂载，域缓存文本＝%r（WPS/静态查看器可能显示缓存——Word/打印/PDF 链路重算，见 docstring 备案）' % first_txt)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
