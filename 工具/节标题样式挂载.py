# -*- coding: utf-8 -*-
#
# 沿革：2026-08-30 工具债清偿（看板工具债②）新建——公共规则§7「标题真实样式挂载」条款
#   （2026-08-30 拍板新增）落地：教材节标题挂内置样式「标题3」，章/讲标题挂「标题2」由后续
#   扩展承接（本工具只处理节层）。页眉 STYLEREF「标题3」前置工程。
#
"""节标题样式挂载.py — 教材节标题挂内置样式「标题3」（只处理副本，断言不过不动输出文件）

识别规则（节层，只挂教材节）：
  ① 正文直接子段落（表内段落一律不挂——章首导航表节名行不属正文节层）；
  ② 文本前缀匹配 ^\\d+\\.\\d+(\\.\\d+)? 且编号后不得再接「.数字」（四级及以上题型号不匹配）；
  ③ 三级编号（X.Y.Z）必须带题号区间标记「（第X—Y题）」——无标记的三级行是题型组
     （如 2.1.1 坐标法：…，台账 E62 题型组口径），不挂；
  ④ 排除讲部标题（含「方法讲解｜」，§7 讲部形态）与文内开头标题段（首张表格之前的段落＝
     件名行/统计行块；无表件排除首段）。

样式处理：
  · styles.xml 已有「标题3」（name=heading 3/标题3 或 styleId=Heading3）则复用其 styleId，
    并将定义规整到现行参数（rPr＝rFonts 宋体/Times New Roman＋b＋sz 24半点；
    pPr 仅留 outlineLvl=2；剥离既有 Word 默认主题字体/蓝色 color/keepNext/keepLines/
    spacing——否则挂载即变蓝变距，违反视觉零变化。规整前扫描全件，若已有内容引用该
    styleId 即报错中止）；
  · 无该样式则新建：styleId=Heading3、name="heading 3"、basedOn=Normal、qFormat、
    pPr outlineLvl=2、rPr 同上（qFormat/outlineLvl 为真实标题语义件零视觉参数）；
  · stylesWithEffects.xml 存在同 id 定义时同步规整（Word 主读 styles.xml，保持两件一致）。

段落处理：节标题段 pPr 首位插 pStyle（无 pPr 则先建），run 属性一律不动。

安全断言（全过才写输出，任一不过退出码 2、不产生输出文件）：
  A1 挂载段计数 ≥1（空件需 --allow-empty 显式放行）；
  A2 视觉零变化——全件每个 w:r 的 sz/szCs/b/bCs/i/iCs/rFonts(含主题)/color/shd 与每个段落
     的 keepNext/keepLines/pageBreakBefore/widowControl/spacing/ind/jc 解析值
     （docDefaults→样式链→直接格式）挂载前后逐一相等（outlineLvl 非视觉项不计）；
  A3 零字符变化——全件 w:t 拼接文本前后相等；
  A4 幂等——对已挂载件重复运行零改动（样式已规整且段落已挂时输出=输入字节级拷贝）。

用法: python 节标题样式挂载.py <in.docx> <out.docx> [--verbose] [--dry-run] [--allow-empty]
"""
import sys, io, os, re, zipfile, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

SEC_RX    = re.compile(r'^(\d+\.\d+(?:\.\d+)?)(?!\.\d)')
MARKER_RX = re.compile(r'（第\d+[—–\-~～]\d+题）')
LECTURE_RX = re.compile(r'方法讲解｜')

STYLE_NAME_CANDIDATES = ('heading 3', '标题3')
DEFAULT_STYLE_ID = 'Heading3'

OFF_VALS = ('0', 'false', 'none', 'off')

class ToolError(Exception):
    pass

# ---------- 样式表上下文 ----------

def build_styles_ctx(styles_root):
    ctx = {'by_id': {}, 'default_para': None, 'rpr_default': None}
    dd = styles_root.find(q('docDefaults'))
    if dd is not None:
        rprd = dd.find(q('rPrDefault'))
        if rprd is not None:
            ctx['rpr_default'] = rprd.find(q('rPr'))
    for st in styles_root.findall(q('style')):
        sid = st.get(q('styleId'))
        nm = st.find(q('name'))
        based = st.find(q('basedOn'))
        entry = {
            'el': st,
            'name': nm.get(q('val')) if nm is not None else None,
            'basedOn': based.get(q('val')) if based is not None else None,
            'rpr': st.find(q('rPr')),
            'ppr': st.find(q('pPr')),
            'type': st.get(q('type')),
        }
        ctx['by_id'][sid] = entry
        if st.get(q('type')) == 'paragraph' and st.get(q('default')) in ('1', 'true'):
            ctx['default_para'] = sid
    return ctx

def style_chain(ctx, start_id):
    chain, seen, cur = [], set(), start_id
    while cur and cur not in seen:
        seen.add(cur)
        st = ctx['by_id'].get(cur)
        if st is None:
            break
        chain.append(st)
        cur = st['basedOn']
    chain.reverse()
    return chain

# ---------- 解析值收集 ----------

def _toggle(el):
    if el is None:
        return None
    v = el.get(q('val'))
    if v is None:
        return True
    return False if v.strip().lower() in OFF_VALS else True

def collect_rpr_keys(rpr, out):
    if rpr is None:
        return
    for c in rpr:
        t = etree.QName(c).localname
        if t in ('sz', 'szCs'):
            out[t] = c.get(q('val'))
        elif t in ('b', 'bCs', 'i', 'iCs'):
            out[t] = _toggle(c)
        elif t == 'rFonts':
            for a in ('ascii', 'hAnsi', 'eastAsia', 'cs',
                      'asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
                v = c.get(q(a))
                if v is not None:
                    out['rFonts.' + a] = v
        elif t == 'color':
            for a in ('val', 'themeColor', 'themeShade', 'themeTint'):
                v = c.get(q(a))
                if v is not None:
                    out['color.' + a] = v
        elif t == 'shd':
            for a in ('val', 'fill', 'color'):
                v = c.get(q(a))
                if v is not None:
                    out['shd.' + a] = v

def collect_ppr_keys(ppr, out):
    if ppr is None:
        return
    for c in ppr:
        t = etree.QName(c).localname
        if t in ('keepNext', 'keepLines', 'pageBreakBefore', 'widowControl'):
            out[t] = _toggle(c)
        elif t == 'spacing':
            for a in ('before', 'after', 'line', 'lineRule',
                      'beforeAutospacing', 'afterAutospacing'):
                v = c.get(q(a))
                if v is not None:
                    out['spacing.' + a] = v
        elif t == 'ind':
            for a in ('left', 'right', 'leftChars', 'rightChars',
                      'firstLine', 'firstLineChars', 'hanging', 'hangingChars'):
                v = c.get(q(a))
                if v is not None:
                    out['ind.' + a] = v
        elif t == 'jc':
            v = c.get(q('val'))
            if v is not None:
                out['jc'] = v

def resolved_run_keys(run_el, para_chain, ctx):
    out = {}
    collect_rpr_keys(ctx['rpr_default'], out)
    for st in para_chain:
        collect_rpr_keys(st['rpr'], out)
    rpr = run_el.find(q('rPr'))
    if rpr is not None:
        collect_rpr_keys(rpr, out)
    return out

def resolved_para_keys(p, ctx):
    out = {}
    for st in chain_for_para(p, ctx):
        collect_ppr_keys(st['ppr'], out)
    ppr = p.find(q('pPr'))
    if ppr is not None:
        collect_ppr_keys(ppr, out)
    return out

def chain_for_para(p, ctx):
    ppr = p.find(q('pPr'))
    sid = None
    if ppr is not None:
        ps = ppr.find(q('pStyle'))
        if ps is not None:
            sid = ps.get(q('val'))
    if not sid:
        sid = ctx['default_para']
    return style_chain(ctx, sid)

# ---------- 节标题识别 ----------

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def find_section_titles(body):
    """返回 [(段落元素, 文本)]——正文直接子段落的节层标题。"""
    children = list(body)
    first_tbl_idx = next((i for i, c in enumerate(children) if c.tag == q('tbl')), None)
    hits, seen_p = [], 0
    for i, c in enumerate(children):
        if c.tag != q('p'):
            continue
        seen_p += 1
        if first_tbl_idx is not None and i < first_tbl_idx:
            continue  # 文内开头标题块（件名行/统计行，位于章首导航表之前）
        if first_tbl_idx is None and seen_p == 1:
            continue  # 无表件的开头标题段
        t = para_text(c)
        m = SEC_RX.match(t)
        if not m:
            continue
        if LECTURE_RX.search(t):
            continue  # 讲部标题不挂
        num = m.group(1)
        if num.count('.') >= 2 and not MARKER_RX.search(t):
            continue  # 三级无题号区间＝题型组
        hits.append((c, t))
    return hits

# ---------- 挂载 ----------

def mount_paragraph(p, style_id):
    """返回 'added' / 'kept'（幂等跳过）"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    ps = ppr.find(q('pStyle'))
    if ps is None:
        ps = etree.Element(q('pStyle'))
        ps.set(q('val'), style_id)
        ppr.insert(0, ps)
        return 'added'
    if ps.get(q('val')) == style_id:
        return 'kept'
    raise ToolError('段落已有其他 pStyle=%s，拒绝覆盖：%s' % (ps.get(q('val')), para_text(p)[:40]))

# ---------- 样式定义定位 / 规整 / 新建 ----------

def find_heading3(styles_root):
    for st in styles_root.findall(q('style')):
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if nv.strip().lower() in STYLE_NAME_CANDIDATES:
            return st
    for st in styles_root.findall(q('style')):
        if st.get(q('styleId')) == DEFAULT_STYLE_ID:
            return st
    return None

def target_rpr():
    # 任务口径：仅 sz=24半点、b、rFonts 宋体/Times New Roman——不带 bCs/szCs，
    # 使无直接 bCs/szCs 的 run 在挂载前后解析值严格相等（视觉零变化断言 A2 可全过）。
    r = etree.Element(q('rPr'))
    rf = etree.SubElement(r, q('rFonts'))
    rf.set(q('ascii'), 'Times New Roman')
    rf.set(q('hAnsi'), 'Times New Roman')
    rf.set(q('eastAsia'), '宋体')
    rf.set(q('cs'), 'Times New Roman')
    etree.SubElement(r, q('b'))
    sz = etree.SubElement(r, q('sz')); sz.set(q('val'), '24')
    return r

def target_ppr(keep_outline_val):
    p = etree.Element(q('pPr'))
    ol = etree.SubElement(p, q('outlineLvl'))
    ol.set(q('val'), keep_outline_val if keep_outline_val is not None else '2')
    return p

def _sig(el):
    if el is None:
        return None
    return [(etree.QName(c).localname, tuple(sorted((k.split('}')[-1], v) for k, v in c.attrib.items())))
            for c in el]

def style_outline_val(st):
    old_ppr = st.find(q('pPr'))
    if old_ppr is not None:
        ol = old_ppr.find(q('outlineLvl'))
        if ol is not None:
            return ol.get(q('val'))
    return None

def style_needs_norm(st):
    """纯检查：既有定义是否偏离现行参数（不改动）。"""
    return (_sig(st.find(q('pPr'))) != _sig(target_ppr(style_outline_val(st)))) or \
           (_sig(st.find(q('rPr'))) != _sig(target_rpr()))

def apply_norm(st):
    """把既有「标题3」定义规整到现行参数（调用前应过 style_needs_norm）。"""
    old_rpr = st.find(q('rPr'))
    old_ppr = st.find(q('pPr'))
    new_ppr = target_ppr(style_outline_val(st))
    new_rpr = target_rpr()
    if old_ppr is not None:
        st.remove(old_ppr)
    if old_rpr is not None:
        st.remove(old_rpr)
    # 依 schema 序：pPr 在 rPr 之前，且都在 name/basedOn/… 之后（追加到尾部即可）
    st.append(new_ppr)
    st.append(new_rpr)

def create_style(styles_root):
    st = etree.SubElement(styles_root, q('style'))
    st.set(q('type'), 'paragraph')
    st.set(q('styleId'), DEFAULT_STYLE_ID)
    nm = etree.SubElement(st, q('name')); nm.set(q('val'), 'heading 3')
    bo = etree.SubElement(st, q('basedOn')); bo.set(q('val'), 'Normal')
    qf = etree.SubElement(st, q('qFormat'))
    st.append(target_ppr(None))
    st.append(target_rpr())
    return st

def scan_style_references(zin, style_id):
    """内容件（非 styles 件）中对 styleId 的任何样式引用 → 返回引用清单。"""
    refs = []
    for name in zin.namelist():
        if not name.startswith('word/') or not name.endswith('.xml'):
            continue
        base = name.rsplit('/', 1)[-1]
        if base.startswith('styles'):
            continue  # styles.xml / stylesWithEffects.xml 自身定义不算内容引用
        try:
            root = etree.fromstring(zin.read(name))
        except etree.XMLSyntaxError:
            continue
        for el in root.iter(q('pStyle'), q('rStyle')):
            if el.get(q('val')) == style_id:
                refs.append(name)
    return refs

# ---------- 主流程 ----------

def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    flags = set(a for a in argv if a.startswith('--'))
    verbose = '--verbose' in flags
    dry = '--dry-run' in flags
    allow_empty = '--allow-empty' in flags
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
    swe_name = 'word/stylesWithEffects.xml' if 'word/stylesWithEffects.xml' in zin.namelist() else None
    swe_root = etree.fromstring(zin.read(swe_name)) if swe_name else None

    ctx_before = build_styles_ctx(styles_root)

    # ---- 样式定位 ----
    st_el = find_heading3(styles_root)
    if st_el is None:
        action = 'created'
        sid = DEFAULT_STYLE_ID
        create_style(styles_root)   # 2026-08-31 W10 缺陷修复：原版漏调 create_style——
        # docstring 契约为「无该样式则新建」，实测 created 分支只改段落 pStyle 未写样式定义，
        # 致下游 页眉面包屑挂载.py A2 前置依赖（styles.xml 须有标题3）中止。
    else:
        sid = st_el.get(q('styleId'))
        if style_needs_norm(st_el):
            refs = scan_style_references(zin, sid)
            if refs:
                print('[中止] 样式 %s 偏离现行参数且已被内容件引用（%s）——规整会改变其现有视觉，需人工裁决。'
                      % (sid, ', '.join(sorted(set(refs)))))
                return 2
            apply_norm(st_el)
            action = 'normalized'
        else:
            action = 'already-normalized'

    # ---- 段落挂载 ----
    body = doc_root.find(q('body'))
    hits = find_section_titles(body)
    added = kept = 0
    mounted_texts = []
    for p, t in hits:
        r = mount_paragraph(p, sid)
        if r == 'added':
            added += 1
        else:
            kept += 1
        mounted_texts.append(t)

    total_mounted = added + kept
    print('识别节标题（节层候选）：%d 段；本次新挂载 %d 段，幂等已挂 %d 段' % (len(hits), added, kept))
    if verbose:
        for i, t in enumerate(mounted_texts, 1):
            print('  %2d. %s' % (i, t))
    if total_mounted == 0 and not allow_empty:
        print('[中止] 节标题识别数为 0——疑似与该件形态不匹配，按安全纪律不动文件'
              '（确认无误可加 --allow-empty）。')
        return 2

    # ---- stylesWithEffects 同步规整 ----
    swe_changed = False
    if swe_root is not None:
        st2 = find_heading3(swe_root)
        if st2 is not None and st2.get(q('styleId')) == sid and style_needs_norm(st2):
            apply_norm(st2)
            swe_changed = True

    # ---- 断言 A2/A3：视觉零变化 + 零字符 ----
    ctx_after = build_styles_ctx(styles_root)
    runs_before = list(etree.fromstring(zin.read('word/document.xml')).iter(q('r')))
    runs_after = list(doc_root.iter(q('r')))
    paras_before = list(etree.fromstring(zin.read('word/document.xml')).find(q('body')).iter(q('p')))
    paras_after = list(body.iter(q('p')))
    if len(runs_before) != len(runs_after) or len(paras_before) != len(paras_after):
        print('[断言失败] 前后 run/段落数量不一致（%d→%d run, %d→%d p）'
              % (len(runs_before), len(runs_after), len(paras_before), len(paras_after)))
        return 2
    # 逐段处理（run 解析依赖所属段落的样式链）
    bad = []
    body_before = etree.fromstring(zin.read('word/document.xml')).find(q('body'))
    pb_list = list(body_before.iter(q('p')))
    rb_list = list(body_before.iter(q('r')))
    ra_list = list(doc_root.iter(q('r')))
    for pb, pa in zip(pb_list, paras_after):
        cb = chain_for_para(pb, ctx_before)
        ca = chain_for_para(pa, ctx_after)
        rb_runs = list(pb.iter(q('r')))
        ra_runs = list(pa.iter(q('r')))
        if len(rb_runs) != len(ra_runs):
            bad.append(('run数', para_text(pb)[:30], ''))
            continue
        for r0, r1 in zip(rb_runs, ra_runs):
            k0 = dict(resolved_run_keys(r0, cb, ctx_before))
            k1 = resolved_run_keys(r1, ca, ctx_after)
            if k0 != k1:
                diff = {k: (k0.get(k), k1.get(k)) for k in set(k0) | set(k1) if k0.get(k) != k1.get(k)}
                bad.append((para_text(pb)[:30], ''.join(x.text or '' for x in r1.findall(q('t')))[:20], diff))
    for p0, p1 in zip(pb_list, paras_after):
        k0 = resolved_para_keys(p0, ctx_before)
        k1 = resolved_para_keys(p1, ctx_after)
        if k0 != k1:
            diff = {k: (k0.get(k), k1.get(k)) for k in set(k0) | set(k1) if k0.get(k) != k1.get(k)}
            bad.append(('pPr:' + para_text(p0)[:30], '', diff))
    if bad:
        print('[断言失败 A2] 视觉零变化不过：%d 处解析值差异' % len(bad))
        for t, rt, diff in bad[:10]:
            print('   段「%s」 run「%s」差异 %s' % (t, rt, diff))
        return 2
    txt_before = ''.join(t.text or '' for t in etree.fromstring(zin.read('word/document.xml')).iter(q('t')))
    txt_after = ''.join(t.text or '' for t in doc_root.iter(q('t')))
    if txt_before != txt_after:
        print('[断言失败 A3] 字符级文本发生变化')
        return 2
    print('断言 A2 视觉零变化：PASS（%d run × sz/szCs/b/bCs/i/iCs/rFonts/color/shd ＋ %d 段 pPr 解析值逐一相等）'
          % (len(rb_list), len(pb_list)))
    print('断言 A3 零字符变化：PASS')

    # ---- 落盘 ----
    if dry:
        print('[dry-run] 不写输出。样式动作=%s，挂载=%d（新%d/已%d），目标 styleId=%s'
              % (action, total_mounted, added, kept, sid))
        return 0

    doc_changed = added > 0
    chg = {'word/document.xml': etree.tostring(doc_root, xml_declaration=True, encoding='UTF-8', standalone=True) if doc_changed else None,
           'word/styles.xml': etree.tostring(styles_root, xml_declaration=True, encoding='UTF-8', standalone=True) if action in ('created', 'normalized') else None}
    if swe_name and (swe_changed or (action == 'created' and find_heading3(swe_root) is None)):
        pass  # SWE 仅在已存在同 id 定义时规整；新建不向 SWE 播种
    if swe_name and swe_changed:
        chg[swe_name] = etree.tostring(swe_root, xml_declaration=True, encoding='UTF-8', standalone=True)

    if not any(v for v in chg.values()):
        # 幂等零改动：输出＝输入字节级拷贝（断言 A4）
        with open(dst, 'wb') as f:
            f.write(open(src, 'rb').read())
        print('断言 A4 幂等：零改动，输出=输入字节级拷贝 -> %s' % dst)
        print('完成：挂载段合计 %d，styleId=%s（动作=%s）' % (total_mounted, sid, action))
        return 0

    zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    try:
        for item in zin.infolist():
            data = chg.get(item.filename)
            if data is not None:
                zout.writestr(item.filename, data, compress_type=zipfile.ZIP_DEFLATED)
            else:
                zout.writestr(item, zin.read(item.filename))
    finally:
        zout.close()
    print('输出 -> %s（替换 %s）' % (dst, ', '.join(k for k, v in chg.items() if v)))
    print('完成：挂载段合计 %d（新%d/已%d），styleId=%s（动作=%s）' % (total_mounted, added, kept, sid, action))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
